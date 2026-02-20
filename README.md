# Patient Risk Monitoring System

A structured healthcare web application for monitoring patient risk based on vitals, clinical history, and demographics. Built with Django and MySQL.

## 🚀 Features

- **Automated Risk Calculation**: Real-time scoring using specific clinical rules (Demographics, Vitals, Labs).
- **Risk Classification**: Auto-assigns LOW, MEDIUM, or HIGH risk levels.
- **Critical Escalation**: Immediate HIGH risk triggers for critical vital signs.
- **Audit Logging**: Tracks every change to patient records with "Before & After" risk states.
- **PDF Extraction**: Autofills patient forms by parsing uploaded medical PDF reports.
- **Interactive Dashboard**: Visual analytics for risk distribution and recent admissions.
- **Responsive UI**: Clean interface built with Bootstrap 5.

## 🛠 Technology Stack

- **Backend**: Django 5.x, Python 3.x
- **Database**: MySQL
- **Frontend**: HTML5, CSS3, Bootstrap 5, Chart.js
- **PDF Processing**: PyPDF2
- **Utilities**: Regex key-value extraction

## ⚙️ Architecture

The project follows a Service-Oriented Architecture (SOA) within Django:

- `risk_monitor/services/risk_engine.py`: Pure logic module for calculating risk scores. Decoupled from models.
- `risk_monitor/services/audit_service.py`: Handles business logic for updates, risk recalculation, and audit trail creation.
- `risk_monitor/utils/pdf_parser.py`: Utility to parse unstructured text from PDFs.
- `risk_monitor/views.py`: Thin view layer handling HTTP requests and delegating to services.

## 📦 Setup & Installation

### Prerequisites
- Python 3.9+
- MySQL Server

### 1. Clone & Environment
```bash
git clone <repo_url>
cd patient-risk-monitoring-system
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Database Configuration
The project is configured to use **SQLite** by default for immediate testing without setup.

**To use MySQL (Optional):**
1. Create a MySQL database (e.g., `patient_monitor`).
2. Rename `.env.example` to `.env` (if applicable) and update credentials:
   ```ini
   DB_NAME=patient_monitor
   DB_USER=root
   DB_PASSWORD=your_password
   DB_HOST=localhost
   ```
3. Uncomment the MySQL configuration in `config/settings.py` and comment out the SQLite section.

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run Server
```bash
python manage.py runserver
```

## ✅ Feature Checklist

- [x] Risk Calculation Engine (Rules implemented exactly)
- [x] Patient & AuditLog Models
- [x] Automated Audit Logging
- [x] PDF Vitals Extraction (Auto-fill)
- [x] Dashboard with Charts
- [x] CSV Export for Audit Logs

## 🧪 Testing

Run the logic verification script:
```bash
python verify_logic.py
```

Run Django tests:
```bash
python manage.py test risk_monitor
```

## 📝 Assumptions & Limitations
- **PDF Format**: Assumes a standard text-based PDF report format (not OCR).
- **Authentication**: Usage assumes an internal network; login/auth system logic is standard Django admin (not customized for this scope).
- **Risk Override**: As per requirements, risk level cannot be manually edited; it is always derived from data.

## 🔮 Future Enhancements
- [ ] HL7 / FHIR integration for real-time EMR data.
- [ ] Email alerts for HIGH risk escalations.
- [ ] User role management (Doctor vs Nurse views).
