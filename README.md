<div align="center">

# ⚡ BizFlow AI — Next-Gen Local Business CRM & AI OS

[![Version](https://img.shields.io/badge/BizFlow-v2.5-6366F1?style=for-the-badge&logo=sparkles&logoColor=white)](https://github.com/Mrrwuday45/bizflow)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Google Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-8E44AD?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![ReportLab](https://img.shields.io/badge/PDF-ReportLab%204.x-DA291C?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](https://www.reportlab.com/)
[![License](https://img.shields.io/badge/License-MIT-10B981?style=for-the-badge)](LICENSE)

<p align="center">
  <b>The modern, high-aesthetic Customer Relationship Management (CRM), Point of Sale (POS), and Intelligent Business Operating System designed for local businesses, retail stores, service agencies, and freelancers.</b>
</p>

---

[Key Features](#-key-features) • [Architecture](#-project-architecture) • [Tech Stack](#-technology-stack) • [Installation](#-quick-setup--installation-guide) • [Routes](#-page-overview--navigation) • [API & AI Engine](#-intelligent-ai-business-co-pilot) • [License](#-license)

</div>

---

## 🌟 Overview

**BizFlow AI** reimagines how local store owners, service agencies, and freelancers run their business. Built from the ground up with Python, Flask, and an embedded zero-config SQLite architecture, BizFlow AI integrates customer management, instant Point of Sale (POS) checkout, automated inventory depletion, ReportLab PDF invoicing, and real-time revenue analytics—all powered by an interactive **Google Gemini AI Business Co-Pilot** and wrapped in a stunning dark-mode glassmorphism UI.

```
                  ┌──────────────────────────────────────────────┐
                  │                BizFlow AI OS                 │
                  └──────────────────────┬───────────────────────┘
                                         │
       ┌──────────────────┬──────────────┼──────────────┬──────────────────┐
       ▼                  ▼              ▼              ▼                  ▼
┌──────────────┐   ┌──────────────┐ ┌──────────┐ ┌──────────────┐   ┌──────────────┐
│ Landing Page │   │ Executive    │ │ POS Cart │ │ ReportLab    │   │ Gemini AI    │
│ & Pricing    │   │ Analytics    │ │ Checkout │ │ PDF Invoices │   │ Co-Pilot     │
└──────────────┘   └──────────────┘ └──────────┘ └──────────────┘   └──────────────┘
```

---

## ✨ Key Features

### 🎨 1. High-Aesthetic Glassmorphism UI & Ambient Mesh Design
- **Radial Ambient Glow System**: Vibrant color gradient mesh layering Electric Indigo (`#6366F1`), Hot Pink (`#EC4899`), Neon Cyan (`#06B6D4`), and Emerald (`#10B981`).
- **Interactive Landing Showcase (`/`)**: Live interactive tab switcher displaying live demos of the Executive Dashboard, AI Co-Pilot, POS Cart Checkout, and PDF Invoices.
- **Pricing & FAQ Calculator**: Dynamic monthly/annual pricing toggle with automated 20% annual discount calculations and collapsible FAQ accordions.
- **Fully Responsive**: Smooth experience across mobile, tablet, and ultra-wide displays with modern typography (`Inter` & `Plus Jakarta Sans`).

### 🤖 2. Intelligent Google Gemini AI Business Co-Pilot (`/ai-assistant`)
- **Natural Language Business Queries**: Ask questions directly like *"Who is our top spending customer this month?"*, *"Which products have low stock?"*, or *"Generate a strategy to boost weekend sales"*.
- **Automated Insights**: AI auto-scans store data to deliver actionable advice on revenue trends, inventory reordering, and customer retention.
- **Resilient Fallback Engine**: Uses the official `google-genai` SDK with an intelligent offline mock AI fallback if no API key is set or network is offline.
- **Chat Management**: Persistent conversation context, with one-click capabilities to clear chat history or delete individual message logs.

### 🛒 3. Point of Sale (POS) & Stock Inventory (`/sales`, `/products`)
- **Instant Cart Checkout**: Select customers, search product catalogs dynamically, apply line-item or global cart discounts, and finalize transactions instantly.
- **Auto Stock Depletion**: Inventory balances automatically decrement upon sale completion, preventing accidental overselling.
- **Inventory Catalog Management**: Add, update, and manage products categorized by price, stock levels, SKU categories, and descriptions.

### 📄 4. One-Click ReportLab PDF Invoicing Engine (`/invoices`)
- **Automated PDF Generation**: Automatically formats and builds crisp, vector-rendered PDF invoices complete with store branding, itemized order tables, subtotals, applied taxes, and discount totals.
- **Instant Preview & Direct Download**: Stream invoices directly in-browser or download print-ready PDFs with a single click.

### 👥 5. Customer 360 & Relationship Management (`/customers`)
- **Comprehensive Profiles**: Track client phone numbers, emails, physical addresses, lifetime spend totals, and granular purchase history logs.
- **Multi-Tenant Data Isolation**: Multi-user account security with hashed passwords, session encryption, and isolated per-store datasets.

---

## 🏗️ Project Architecture

```
local_business_crm_bizflow/
├── app.py                   # Main Flask web application & HTTP route controllers
├── main.py                  # Server entry launcher (starts app & opens web browser)
├── config.py                # System paths, environment keys, and directory configs
├── database.py              # SQLite database connection manager & table schema setup
├── models.py                # Data access layer & multi-tenant CRUD operations
├── customer.py              # Customer management business logic module
├── product.py               # Inventory management & stock control logic module
├── sales.py                 # POS cart processing & sales transaction logic module
├── invoice.py               # ReportLab PDF invoice generation engine
├── reports.py               # Revenue analytics, metrics aggregator & business reporter
├── ai_assistant.py          # Google Gemini AI Co-Pilot integration & offline fallback
├── requirements.txt         # Python project dependencies manifest
├── .env                     # Local environment variables & API key configuration
├── static/
│   ├── css/
│   │   ├── style.css        # Core CRM dark-mode glassmorphism design system
│   │   └── landing.css      # Landing page ambient gradient mesh styles
│   └── js/
│       ├── app.js           # Client-side CRM logic, cart processing & notifications
│       └── landing.js       # Interactive demo tabs, pricing toggles & smooth scroll
└── templates/
    ├── index.html           # Public landing page template
    ├── base.html            # Main CRM dashboard layout wrapper & sidebar
    ├── auth.html            # Sign In, Store Registration & Password Reset view
    ├── dashboard.html       # Executive revenue metrics & business analytics dashboard
    ├── customers.html       # Customer directory & client profile management
    ├── products.html        # Stock catalog & inventory management
    ├── sales.html           # POS checkout cart & sales history log
    ├── invoices.html        # ReportLab PDF invoice manager & download center
    └── ai_assistant.html    # Conversational AI Co-Pilot interface
```

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend Framework** | Python 3.10+, Flask 3.1, Gunicorn (Production) |
| **Database** | SQLite3 (Embedded, Zero-Config, Transactional) |
| **AI Integration** | Google Gemini AI (`google-genai` SDK) with fallback engine |
| **PDF Invoice Engine** | ReportLab 4.x Vector PDF Builder |
| **Frontend Layout** | HTML5, Vanilla CSS3 (Glassmorphism & Radial Mesh), JavaScript (ES6+) |
| **Typography & Icons** | Google Fonts (`Inter`, `Plus Jakarta Sans`), Lucide Icons |
| **Environment & Config** | `python-dotenv`, standard system environment management |

---

## ⚡ Quick Setup & Installation Guide

### Prerequisites
Ensure you have **Python 3.10** or higher installed on your operating system.

### Step 1: Clone the Repository & Navigate to Directory
```bash
git clone https://github.com/Mrrwuday45/bizflow.git
cd bizflow
```

### Step 2: Create & Activate Virtual Environment
```bash
# Windows (PowerShell)
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
Create a `.env` file in the project root directory (or update existing):
```env
SECRET_KEY=bizflow-ai-crm-secret-key-2026
GEMINI_API_KEY=your_google_gemini_api_key_here
```
> 💡 *Note: If no `GEMINI_API_KEY` is provided, BizFlow AI will seamlessly operate using its built-in intelligent offline fallback engine.*

### Step 5: Launch the Application
Run the main launcher script:
```bash
python main.py
```
*Or launch Flask directly:*
```bash
python app.py
```

The application will start at **`http://127.0.0.1:5000`** and automatically open in your default browser!

---

## 🔑 Default Administrator Credentials

When initialized for the first time, BizFlow automatically seeds default store admin accounts:

| Username | Email | Default Password | Role |
| :--- | :--- | :--- | :--- |
| `admin` | `admin@store.com` | `admin123` | Store Admin |
| `uday734` | `uday734@store.com` | `uday734` | Store Admin |

> 🔒 *Security Tip: You can register new custom store accounts directly via the `/register` route or change passwords inside the app.*

---

## 📸 Page Overview & Navigation

| Route | Page Title | Access Level | Purpose / Description |
| :--- | :--- | :--- | :--- |
| `/` | **Landing Page** | Public | Interactive product showcase, feature breakdown, live tab demo, pricing & FAQ |
| `/login` | **Sign In** | Public | Secure authentication portal for existing store accounts |
| `/register` | **Store Registration** | Public | Register a new business workspace with isolated store data |
| `/reset-password` | **Password Reset** | Public | Security question recovery interface to update forgotten passwords |
| `/dashboard` | **Executive Dashboard** | Authenticated | High-level KPI metrics, revenue charts, top items, and recent sales feed |
| `/customers` | **Customer Directory** | Authenticated | Client management table, search filtering, add/edit/delete customer records |
| `/products` | **Stock Inventory** | Authenticated | Product catalog, stock tracking, price adjustments & low-stock alerts |
| `/sales` | **POS Cart Checkout** | Authenticated | Live checkout cart, discount configuration, and complete sales transaction log |
| `/invoices` | **PDF Invoices** | Authenticated | ReportLab invoice list, single-click PDF generation & direct download links |
| `/ai-assistant` | **AI Co-Pilot** | Authenticated | Conversational business assistant with live query handling & chat history controls |

---

## ⚙️ REST & System API Reference

BizFlow AI exposes several internal API endpoints for smooth client-side interaction:

- `POST /api/ai-chat` — Send natural language query to Gemini AI / Fallback engine and retrieve structured response.
- `POST /api/ai-chat/clear` — Clear current store user's AI chat history.
- `POST /sales/checkout` — Submit POS cart payload, create transaction record, and decrement product quantities.
- `GET /invoices/generate/<sale_id>` — Trigger ReportLab to build PDF invoice for specified sale ID.
- `GET /invoices/download/<filename>` — Serve generated PDF invoice file directly to browser.
- `POST /api/purge-database` — Reset local store database tables back to default state (Admin only).

---

## 🗄️ Database Schema Overview

BizFlow AI operates on a relational SQLite schema enforcing store-level multi-tenancy via `user_id`:

```
┌────────────────┐        ┌────────────────┐        ┌────────────────┐
│     users      │1      *│   customers    │1      *│     sales      │
├────────────────┤────────├────────────────┤────────├────────────────┤
│ user_id (PK)   │        │ customer_id(PK)│        │ sale_id (PK)   │
│ username       │        │ user_id (FK)   │        │ user_id (FK)   │
│ email          │        │ name, phone    │        │ customer_id(FK)│
│ password_hash  │        └────────────────┘        │ total_amount   │
└────────────────┘                                  └───────┬────────┘
        │                                                   │1
        │1                                                  │
        │*                                                  │*
┌───────┴────────┐                                  ┌───────┴────────┐
│    products    │                                  │   sale_items   │
├────────────────┤                                  ├────────────────┤
│ product_id (PK)│                                  │ item_id (PK)   │
│ user_id (FK)   │                                  │ sale_id (FK)   │
│ product_name   │                                  │ product_id (FK)│
│ price, quantity│                                  │ price, quantity│
└────────────────┘                                  └────────────────┘
```

---

## 🤝 Contributing

Contributions, feature requests, and bug reports are welcome!
1. Fork the project repository.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more details.

<div align="center">
  <br />
  Made with for Local Businesses & Store Owners by <b>BizFlow AI</b>.
</div>
