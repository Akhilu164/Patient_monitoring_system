# Patient Risk Monitoring System

> **A comprehensive healthcare web application for real-time patient risk assessment and monitoring.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Django 5.x](https://img.shields.io/badge/django-5.x-green.svg)](https://www.djangoproject.com/)
[![MySQL](https://img.shields.io/badge/mysql-8.0+-orange.svg)](https://www.mysql.com/)

---

## About The Project

The **Patient Risk Monitoring System** is a robust, service-oriented web application designed to assist healthcare professionals in monitoring patient health status efficiently. By analyzing vitals, demographics, and clinical history, the system automatically calculates risk scores, assigns risk levels (LOW, MEDIUM, HIGH), and maintains a detailed audit trail of all changes.

Key capabilities include automated PDF report parsing for quick data entry and a dynamic dashboard for visual analytics.

## Key Features

*   **Automated Risk Engine**: Real-time risk calculation based on configurable clinical rules (Demographics, Vitals, Labs).
*   **Intelligent Classification**: Auto-assigns risk levels:
    *   **LOW**: Routine monitoring.
    *   **MEDIUM**: Requires attention.
    *   **HIGH**: Critical escalation needed.
*   **Critical Alerts**: Immediate high-risk triggers for abnormal vital signs (e.g., severe hypertension).
*   **Automated Audit Logging**: Complete history tracking with "Before & After" snapshots for every patient record update.
*   **Smart PDF Extraction**: Drag-and-drop medical PDF reports to auto-fill patient forms using advanced text parsing.
*   **Interactive Dashboard**: Visual insights into risk distribution, recent admissions, and system usage.
*   **Responsive Design**: Fully responsive UI built with Bootstrap 5 for seamless access on any device.

## Technology Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Backend** | Django 5.x, Python 3.x | Core application logic and API handling. |
| **Database** | MySQL | Robust relational database for patient records. |
| **Frontend** | HTML5, CSS3, Bootstrap 5 | Responsive and accessible user interface. |
| **Visualization** | Chart.js | Dynamic charts for the dashboard. |
| **Processing** | PyPDF2, Regex | Text extraction and data parsing from PDF reports. |

## Architecture

The project adopts a **Service-Oriented Architecture (SOA)** within the Django framework to ensure scalability and maintainability:

*   **`risk_monitor/services/risk_engine.py`**: A pure logic module dedicated to calculating risk scores, completely decoupled from database models.
*   **`risk_monitor/services/audit_service.py`**: Manages business logic for patient updates, risk recalculation, and audit trail generation.
*   **`risk_monitor/utils/pdf_parser.py`**: A specialized utility for extracting structured data from unstructured medical PDF reports.
*   **`risk_monitor/views.py`**: A thin view layer that strictly handles HTTP requests/responses and delegates complex logic to the services.

## Getting Started

Follow these steps to set up the project locally.

### Prerequisites

*   Python 3.9 or higher
*   MySQL Server (optional, SQLite is default)
*   Git

### Installation

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/Akhilu164/Patient_monitoring_system.git
    cd Patient_monitoring_system
    ```

2.  **Create Virtual Environment**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Linux/macOS
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

#### Database Setup
By default, the project uses **SQLite**. To use **MySQL**:

1.  Create a MySQL database (e.g., `patient_monitor`).
2.  Create a `.env` file in the root directory and add your credentials:
    ```ini
    DB_NAME=patient_monitor
    DB_USER=root
    DB_PASSWORD=your_password
    DB_HOST=localhost
    ```
3.  Update `config/settings.py` to use the MySQL configuration.

#### Run Migrations
Initialize the database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Running the Application

Start the development server:

```bash
python manage.py runserver
```

Access the application at: `http://127.0.0.1:8000/`

## Testing & Verification

Ensure the system logic is solid by running the included tests.

**Run Logic Verification Script:**
```bash
python verify_logic.py
```

**Run Django Unit Tests:**
```bash
python manage.py test risk_monitor
```

## Feature Checklist

- [x] Risk Calculation Engine
- [x] Patient & AuditLog Database Models
- [x] Automated Audit History
- [x] PDF Data Extraction
- [x] Analytics Dashboard
- [x] CSV Export Functionality

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.
