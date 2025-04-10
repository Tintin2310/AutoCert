from flask import Flask, request, render_template, jsonify, redirect, url_for, session
import json
import google.generativeai as genai
import os
from werkzeug.utils import secure_filename
import pytesseract
from PIL import Image
from flask_sqlalchemy import SQLAlchemy
from models import db, init_db, register_user, authenticate_user, register_admin, authenticate_admin, store_certificate, get_all_certificates
import requests


# ImgBB API Key 
IMGBB_API_KEY = "IMGBB_API"

app = Flask(__name__)
app.secret_key = "SECRET_KEY"

# Google Gemini API Key
genai.configure(api_key="GEMINI_API")

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"TESSERACT_PATH"

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dummy User Database
users = {
    "12345": {"name": "John Doe", "password": "password123", "email": "john@example.com"}
}

# Admin user storage
admins = {
    "admin": {"name": "Admin", "password": "admin123"}
}

# Store extracted certificate details globally
certificates = []

def upload_to_imgbb(image_path):
    """Uploads image to Imgbb and returns the hosted image URL"""
    with open(image_path, "rb") as file:
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY},
            files={"image": file},
        )

    if response.status_code == 200:
        return response.json()["data"]["url"]
    return None

def extract_text_from_image(image_path):
    """Extract text from an uploaded certificate image using OCR"""
    try:
        text = pytesseract.image_to_string(Image.open(image_path))
        return text.strip()
    except Exception as e:
        print("OCR Error:", e)
        return None

def analyze_text_with_ai(ocr_text):
    """Google Gemini AI to extract structured details in JSON format"""
    
    prompt = f"""
    Extract key details from the following certificate text and return them **strictly** as a JSON object.
    
    Example format:
    ```json
    {{
      "Name": "<Recipient's Name>",
      "Event": "<Event Name>",
      "Rank/Position": "<Rank or Position (or 'Not Found')>",
      "Type": "<Certificate Type: Participation/Appreciation/Achievement>"
    }}
    ```
    
    Here is the certificate text:
    ```
    {ocr_text}
    ```
    
    **Only return valid JSON output. Do not include any explanations or extra text.**
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)

    try:
        extracted_json = response.text.strip().replace("```json", "").replace("```", "")
        structured_data = json.loads(extracted_json)
    except json.JSONDecodeError:
        structured_data = {
            "Name": "Not Found",
            "Event": "Not Found",
            "Rank/Position": "Not Found",
            "Type": "Not Found"
        }

    return structured_data

@app.route("/")
def index():
    if "user" in session:
        return render_template("index.html", name=session["user"]["name"])
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        roll_number = request.form["roll_number"]
        password = request.form["password"]

        user = authenticate_user(roll_number, password)
        if user:
            session["user"] = user
            return redirect(url_for("index"))
        return "Invalid credentials. Try again."

    return render_template("login.html")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

# -------------------- ADMIN AUTHENTICATION --------------------

@app.route("/admin/register", methods=["GET", "POST"])
def admin_register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if register_admin(username, password):
            return redirect(url_for("admin_login"))
        return "Admin already exists!"

    return render_template("admin_register.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if authenticate_admin(username, password):
            session["admin"] = {"username": username}  
            return redirect(url_for("admin_dashboard"))

        return "Invalid credentials. Try again."

    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    """Logout admin"""
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

@app.route("/admin")
def admin_dashboard():
    """Admin Dashboard"""
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    certificates = get_all_certificates()  # Fetch from database
    return render_template("admin_dashboard.html", certificates=certificates)



# -------------------- USER REGISTRATION --------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        roll_number = request.form["roll_number"]
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]

        if register_user(roll_number, name, email, password):
            return redirect(url_for("login"))
        return "User already exists!"

    return render_template("register.html")


# -------------------- CERTIFICATE UPLOAD & PROCESSING --------------------

@app.route("/upload", methods=["GET", "POST"])
def upload_certificate():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"})

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No selected file"})

        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            # Upload to Imgbb and get image URL
            image_url = upload_to_imgbb(file_path)
            if not image_url:
                return jsonify({"error": "Image upload failed"})

            ocr_text = extract_text_from_image(file_path)

            if not ocr_text:
                return jsonify({"error": "Could not extract text from the image"})

            structured_data = analyze_text_with_ai(ocr_text)

            # Always override Name with logged-in user's name
            user_name = session["user"]["name"]
            structured_data["Name"] = user_name
            structured_data["Image_URL"] = image_url
            session["certificate_data"] = structured_data

            # Store the corrected data in the database
            store_certificate(  
                user_name,
                structured_data["Event"],
                structured_data["Rank/Position"],
                structured_data["Type"],
                image_url
            )

            return redirect(url_for("result_page"))

    return render_template("upload.html")


@app.route("/result", methods=["GET", "POST"])
def result_page():
    if "user" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        session["certificate_data"]["Name"] = request.form["name"]
        return redirect(url_for("confirm_page"))

    certificate_data = session.get("certificate_data", {})
    if not certificate_data:
        return redirect(url_for("index"))

    return render_template("result.html", data=certificate_data)

@app.route("/admin/certificates")
def view_certificates():
    """View all uploaded certificates (Admin)"""
    if "admin" not in session:
        return redirect(url_for("admin_login"))  # Ensure only admins can access

    # Fetch certificates from the database
    certificates = get_all_certificates()  

    return render_template("view_certificates.html", certificates=certificates)


@app.route("/confirm", methods=["POST"])
def confirm_page():
    if "certificate_data" not in session:
        return redirect(url_for("upload_certificate"))

    certificate_data = session["certificate_data"]

    # Get the updated name from the form
    corrected_name = request.form["name"]
    certificate_data["Name"] = corrected_name

    return render_template("confirm.html", data=certificate_data)


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///certificates.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize Database
init_db(app)


if __name__ == "__main__":
    app.run(debug=True)
