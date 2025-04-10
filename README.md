# AutoCert

**AutoCert** is an AI-powered certificate management system designed to streamline the process of uploading, extracting, and verifying certificate information. Using advanced OCR technology and Google Gemini AI, AutoCert reads and interprets certificate images, making data handling faster and more efficient for both users and administrators.

---

## 🚀 Features

- **AI-Driven Certificate Extraction**: Automatically extracts certificate details like name, event, and date using OCR + Gemini.
- **User Authentication**: Separate login portals for users and administrators.
- **Certificate Upload**: Simple interface for users to upload certificate images.
- **Admin Panel**: View and manage all uploaded certificates and extracted details.
- **ImgBB Integration**: Uploads images to ImgBB and stores secure URLs.
- **Gemini AI Integration**: Uses LLM to improve accuracy and understand OCR results intelligently.

---

## 🛠 Tech Stack

- **Frontend**: HTML, CSS, Bootstrap
- **Backend**: Python (Flask), SQLAlchemy
- **OCR**: Tesseract OCR
- **AI/ML**: Google Gemini API (via Google Generative AI Python SDK)
- **Cloud Image Hosting**: ImgBB API

---

## 💻 Installation

To set up AutoCert on your local machine:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/username/autocert.git
   cd autocert
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

3. **Run the Application**:
   ```bash
   flask run

4.**Access the application**
  Open your browser and go to [http://127.0.0.1:5000]

---

## 🧑‍💼 Usage

- **Users**: Register and log in to upload certificates. The app will extract and display certificate data automatically.
- **Admins**: Log in to the admin dashboard to review all submitted certificates with extracted details.
- **Gemini AI**: Helps improve data extraction accuracy using natural language understanding.

---

## ⚙️ Scalability and Novelty

- **Modular Codebase**: Built with separation of concerns using models, routes, and templates.
- **AI-Powered Intelligence**: Combines OCR with LLMs for better document understanding.
- **Easy Integration**: Plug-and-play architecture makes it ideal for educational or HR certificate verification systems.
- **Secure File Handling**: All uploads are sanitized and securely stored.

---

## 📜 License

This project is developed as a submission for a University and is licensed under the **MIT License**.
