# NHCC Operations

NHCC Operations
Internal financial and operations management system for the Nigerian-Hungarian Chamber of Commerce (NHCC). It replaces manual spreadsheets and document preparation with an integrated workflow by providing expense tracking, salary management, reporting, and operational workflows.


## Features

### Available Features

- ✅ Staff Management
- ✅ Salary Management
- ✅ Diesel Management
- ✅ Electricity (EKEDC) Tracking
- ✅ Office Expenses
- ✅ Reports
- ✅ PDF Report Export
- ✅ Authentication & Authorization

### Planned Features

- 🚧 Members Management
- 🚧 Directors Management
- 🚧 Activities Management
- 🚧 Document Templates


## Tech Stack

- Python
- Django
- HTML
- JavaScript
- Bootstrap 5
- SQLite
- WeasyPrint

## Screenshots

### Dashboard

![Dashboard](docs/images/dashboard.png)

## Demo

🎥 Watch the application in action:

https://youtube/video-link


## Local Setup
### 1. Clone the repository

```bash
git clone https://github.com/your-username/nhcc-operations.git
cd nhcc-operations
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Run the development server

```bash
python manage.py runserver
```

Visit

```
http://127.0.0.1:8000/
```


## Project Structure

```text
nhcc-operations/
│
├── account/              # Authentication & user accounts
├── dashboard/            # Dashboard UI
├── finance/              # Expenses, diesel & electricity
├── staff/                # Staff management
├── members/              # Members management
├── directors/            # Directors management
├── activities/           # Activities management
├── reports/              # Reports & exports
├── templating/           # Document templates
├── documentations/       # Project documentation
├── requirements.txt
└── manage.py
```

## Architecture

The project follows a service-layer architecture.

Each application contains a `services/` package responsible for business logic while Django views remain focused on handling HTTP requests and responses.

Example:

```text
staff/
├── views/
├── services/
├── models.py
├── forms.py
└── urls.py
```

## UI Development

The user interface was initially scaffolded with AI assistance and then extensively reviewed, customized, and integrated into the Django application. The layout, user flow, responsiveness, component behavior, and overall user experience were refined to meet the application's functional and usability requirements.

## Backend Development

The system architecture, database design, backend implementation, business logic, integrations, security, and application workflows were designed and implemented by the project author.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Django](https://img.shields.io/badge/Django-6.x-green)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)