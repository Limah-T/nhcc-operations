# Deployment Guide

This project is deployed using **PythonAnywhere**.

## Prerequisites

- PythonAnywhere account
- Git installed (available by default on PythonAnywhere)
- A GitHub repository containing the project

---

## 1. Clone the Repository

Open a **Bash Console** and run:

```bash
git clone https://github.com/your-username/nhcc-operations.git
cd nhcc-operations
```

---

## 2. Create a Virtual Environment

Replace the placeholders with your Python version and environment name.

```bash
mkvirtualenv --python=/usr/bin/python3.13 nhcc-operations-venv
```

---

## 3. Activate the Virtual Environment

```bash
workon nhcc-operations-venv
```

---

## 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Create a `.env` file (or configure the environment variables through PythonAnywhere) and provide the required settings.

Example:

```text
SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=yourusername.pythonanywhere.com
```

---

## 6. Apply Migrations

```bash
python manage.py check
python manage.py migrate
python manage.py showmigrations
```

---

## 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

---

## 8. Configure the Web App

From the **PythonAnywhere Dashboard**:

- Create a new **Web App**
- Select the correct Python version
- Set the project directory
- Configure the virtual environment
- Configure the WSGI file

### Virtual Environment

```
/home/yourusername/.virtualenvs/nhcc-operations-venv
```

### Project Directory

```
/home/yourusername/nhcc-operations
```

---

## 9. Configure the WSGI File

Import your project and set the Django settings module.

Example:

```python
import os
import sys

path = "/home/yourusername/nhcc-operations"

if path not in sys.path:
    sys.path.append(path)

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "nhcc_operations.config.settings.prod"
)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

---

## 10. Reload the Web Application

Return to the **Web** tab and click **Reload**.

Your application should now be available at:

```
https://yourusername.pythonanywhere.com/
```

## Updating the Web Application
```bash
cd ~/nhcc-operations
git pull
workon nhcc-operations-venv
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```
