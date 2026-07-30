<<<<<<< HEAD
# BizFlow AI — Next-Gen Local Business CRM & AI OS

![BizFlow Banner](https://img.shields.io/badge/BizFlow-v2.5-6366F1?style=for-the-badge&logo=sparkles&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.3-000000?style=for-the-badge&logo=flask&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Google Gemini AI](https://img.shields.io/badge/AI-Gemini%202.5-8E44AD?style=for-the-badge&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge)

**BizFlow AI** is a powerful, modern, all-in-one Customer Relationship Management (CRM) and Point of Sale (POS) Operating System built specifically for local businesses, retail stores, service agencies, and freelancers. 

It combines seamless customer tracking, instant POS cart checkout, automated ReportLab PDF invoicing, real-time revenue analytics, and an intelligent **Google Gemini AI Co-Pilot**—wrapped in a high-aesthetic glassmorphism dark-mode UI.

---

##  Key Features

### 1. High-Aesthetic Landing Page (`/`)
- **Vibrant Gradient Mesh Design**: Powered by a multi-layered radial ambient glow system blending Electric Indigo (`#6366F1`), Hot Pink (`#EC4899`), Neon Cyan (`#06B6D4`), and Emerald (`#10B981`).
- **Interactive Live Demo Showcase**: Real-time interactive tab switcher demonstrating the Executive Dashboard, AI Co-Pilot, POS Cart Checkout, and PDF Invoicing.
- **Pricing & FAQ**: Monthly vs. Annual pricing toggle with a 20% discount calculator and expandable FAQ accordions.
- **Responsive Layout**: Designed to look stunning on desktops, tablets, and mobile devices.

### 2. Intelligent AI Business Co-Pilot
- **Natural Language Business Queries**: Ask questions like *"Who is our top spending customer this month?"* or *"Which products have low stock?"*.
- **Automated Performance Summaries**: Instant AI insights on revenue trends, profit margin optimization, and customer re-engagement.
- **Gemini API Integration**: Uses Google's `google-genai` SDK with fallback mock AI capability when offline or without an API key.

### 3. Point of Sale (POS) & Stock Inventory
- **Real-Time Cart Checkout**: Easily select customers, search products, apply custom discounts, and process transactions.
- **Automated Stock Auto-Depletion**: Inventory quantities decrement automatically upon sale completion, preventing overselling.
- **Product Catalog Management**: Organize products by category, price, stock levels, and descriptions.

### 4. One-Click PDF Invoicing Engine
- **ReportLab PDF Generation**: Automatically formats and generates clean, print-ready PDF invoices containing invoice numbers, line items, subtotal, tax, and discount totals.
- **Instant Preview & Download**: Download or open invoices directly in browser with a single click.

### 5. Customer 360 & Relationship Management
- **Detailed Client Profiles**: Manage customer names, phone numbers, email addresses, physical addresses, total spending history, and purchase logs.
- **Data Privacy & Multi-Tenancy**: Isolated per-user data access with password hashing and session encryption.

---

## 🏗️ Project Architecture

```
local_business_crm_bizflow/
├── app.py                   # Main Flask application & route handlers
├── main.py                  # Server launcher script & auto-browser trigger
├── config.py                # System paths, secret keys, and env configuration
├── database.py              # SQLite database connection & table schemas
├── models.py                # Database models & CRUD database operations
├── customer.py              # Customer management business logic
├── product.py               # Inventory & stock management logic
├── sales.py                 # POS sale processing & checkout logic
├── invoice.py               # ReportLab PDF invoice generator
├── reports.py               # Business analytics & revenue reporter
├── ai_assistant.py          # Google Gemini AI Co-Pilot integration
├── requirements.txt         # Dependencies manifest
├── .env                     # Environment variables (API keys & Secrets)
├── static/
│   ├── css/
│   │   ├── style.css        # Main CRM dashboard glassmorphism stylesheet
│   │   └── landing.css      # Modern landing page design system & gradients
│   └── js/
│       ├── app.js           # Main CRM client-side scripts & cart logic
│       └── landing.js       # Landing page tabs, price toggle & animations
└── templates/
    ├── index.html           # Public landing page template
    ├── base.html            # Core CRM dashboard base layout
    ├── auth.html            # Login, Register & Password Reset views
    ├── dashboard.html       # Executive metrics dashboard
    ├── customers.html       # Customer directory management page
    ├── products.html        # Inventory catalog & stock page
    ├── sales.html           # POS cart & sales transaction history
    ├── invoices.html        # PDF invoice list & download page
    └── ai_assistant.html    # Interactive AI Assistant chat interface
```

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Flask 3.1
- **Database**: SQLite3 (Embedded, zero-config)
- **PDF Engine**: ReportLab 4.x
- **AI Integration**: Google Gemini AI (`google-genai`)
- **Frontend**: HTML5, Vanilla CSS3 (Glassmorphism & Gradient Mesh), JavaScript (ES6+)
- **Icons & Fonts**: Lucide Icons, Google Fonts (`Inter` & `Plus Jakarta Sans`)

---

## Quick Setup & Installation Guide

### Prerequisites
Make sure you have **Python 3.10+** installed on your system.

### Step 1: Clone / Navigate to Project Directory
```bash
cd local_business_crm_bizflow
```

### Step 2: Create & Activate Virtual Environment
```bash
# Windows (PowerShell / CMD)
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create or verify a `.env` file in the root directory:
```env
SECRET_KEY=bizflow-ai-crm-secret-key-2026
GEMINI_API_KEY=your_google_gemini_api_key_here
```
*(Note: If no Gemini API key is supplied, BizFlow will operate smoothly using its built-in intelligent fallback engine).*

### Step 5: Launch the Application
Run the launcher script:
```bash
python main.py
```
Or run Flask directly:
```bash
python app.py
```

The application will start on **`http://127.0.0.1:5000`** and automatically launch in your default web browser!

---

## 🔑 Default Administrator Credentials

Upon initial launch, BizFlow automatically seeds a default Store Admin account:

- **Username**: `admin`
- **Password**: `admin123`
- **Email**: `admin@bizflow.ai`

You can also click **"Get Started Free"** on the landing page (`/`) to register new custom store accounts.

---

## 📸 Page Overview & Navigation

| Route | Description | Access |
| :--- | :--- | :--- |
| `/` | **Landing Page** with hero showcase, features, live demo, pricing & FAQ | Public |
| `/login` | **Authentication Page** for signing into existing store accounts | Public |
| `/register` | **Store Registration** for creating a new business account | Public |
| `/dashboard` | **Executive Dashboard** with revenue stats & quick actions | Authenticated |
| `/customers` | **Customer Directory** to add, edit, and view purchase history | Authenticated |
| `/products` | **Stock Catalog** for managing items, prices, and categories | Authenticated |
| `/sales` | **POS Checkout & Sales History** with cart discount processing | Authenticated |
| `/invoices` | **PDF Invoice Generator** & file download manager | Authenticated |
| `/ai-assistant` | **AI Business Co-Pilot** conversational chatbot | Authenticated |

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

Developed with ❤️ for Local Businesses using **BizFlow AI**.
=======
🤖 AI-Powered Local Business Customer Relationship Management (CRM) System
📌 Overview
AI-Powered Local Business CRM System is an intelligent business management application designed to help local businesses efficiently manage customer relationships, sales, inventory, and business operations.

The system provides a centralized platform for managing customer information, tracking leads, monitoring sales activities, generating reports, and using Artificial Intelligence to provide business insights and automate daily tasks.

Built using Python, SQLite, and AI technologies, this CRM system helps businesses improve customer engagement, reduce manual work, and make data-driven decisions.

✨ Key Features
 Secure Authentication
User login and access control system
Secure management of business data
AI-Powered Dashboard
Business performance overview
Customer statistics
Sales insights
Revenue tracking
Customer Management
Add, update, and delete customer records
Store customer details and interaction history
Track customer preferences and activities
Lead Management
Manage potential customers
Track lead status
Follow-up reminders
🛒 Sales Management
Record sales transactions
Monitor sales performance
Generate sales summaries
Inventory Management
Manage products and stock levels
Track available inventory
Prevent stock shortages
Invoice Generation
Generate professional invoices
Store billing history
Export invoices as PDF
AI Business Assistant
Customer behavior analysis
Sales prediction
Personalized recommendations
Automated insights
Reports & Analytics
Sales reports
Customer reports
Inventory reports
Business performance analytics
Technology Stack
Programming Language
Python
Frontend / GUI
CustomTkinter
Tkinter
Database
SQLite
AI & Data Processing
Pandas
NumPy
Scikit-learn
OpenAI/Gemini API
Reporting
ReportLab
Matplotlib
📂 Project Structure
AI-Powered-Local-Business-CRM

│ ├── main.py # Application entry point │ ├── gui/ # User interface screens │ ├── login.py │ ├── dashboard.py │ ├── customer.py │ └── inventory.py │ ├── database/ # Database files │ ├── database.py │ └── schema.sql │ ├── models/ # Data models │ ├── services/ # Business logic │ ├── customer_service.py │ ├── sales_service.py │ └── ai_service.py │ ├── reports/ # Generated reports │ ├── invoices/ # Generated invoices │ ├── assets/ # Images and resources │ ├── tests/ # Testing files │ ├── requirements.txt # Required Python packages │ └── README.md

 Purpose of the Project

The main goal of this project is to provide local businesses with a smart CRM solution that combines customer management, sales tracking, inventory control, and Artificial Intelligence.

The system helps businesses:

Improve customer relationships Automate repetitive tasks Analyze business performance Increase productivity Make better decisions using AI insights 🔮 Future Enhancements Mobile application support Cloud database integration WhatsApp customer notifications AI chatbot for customer support Online payment integration Advanced sales forecasting
>>>>>>> 42a94a8f853da32fd2c2e2072704d552b5bc9a94
