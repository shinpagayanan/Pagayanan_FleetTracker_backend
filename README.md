# 🚗 Fleet Maintenance Tracker — Backend

A web-based system for managing university assets, vehicles, maintenance requests, and work orders. Built with Django and Django REST Framework, it provides a centralized RESTful API with role-based access control, audit logging, and automated work order management.

---

## 📋 Table of Contents

- [User Roles](#user-roles)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
- [Running the Development Server](#running-the-development-server)
- [API Endpoints](#api-endpoints)
- [Security](#security)
- [Deployment](#deployment)

---

## 👥 User Roles

| Role | Permissions |
|------|------------|
| **Manager** | Manage users, assets, and vehicles · Assign assets to staff · Approve/reject maintenance requests · Create and complete work orders · View system-wide reports and dashboard |
| **Auditor** | View assets · View reports and audit logs · View dashboard statistics |
| **Staff** | View assigned assets · Submit and view maintenance requests · View work orders for their assets · Submit and view mileage logs |

---

## ✨ Features

- **User Management** — JWT-based authentication with role-based authorization (Manager, Auditor, Staff)
- **Asset Management** — Create, update, delete, and track assets; assign to staff members
- **Vehicle Management** — Manage vehicle records, monitor status, and track maintenance history
- **Maintenance Requests** — Staff can submit requests; Managers can approve or reject them
- **Work Orders** — Automatically created upon request approval; Managers can mark as complete
- **Mileage Logs** — Staff can record and view vehicle mileage history
- **Reporting** — Asset, maintenance, work order, and mileage reports (Manager & Auditor)
- **Audit Logging** — Full audit trail of all system actions
- **Alerts** — Notifications when assets are due for maintenance

---

## 🛠 Technology Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12+ |
| Framework | Django, Django REST Framework |
| Authentication | JWT (Simple JWT) |
| Database | PostgreSQL |
| File Storage | Cloudinary |
| Deployment | Render |

---

## 🏗 System Architecture

```
Frontend Application
        │
        ▼
Django REST Framework API
        │
        ▼
Business Logic Layer
        │
        ▼
PostgreSQL Database
```

---

## ✅ Prerequisites

Ensure the following are installed before setup:

- Python 3.12 or higher
- PostgreSQL
- Git

Verify your installation:

```bash
python --version
pip --version
```

---

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <backend-repository-url>
cd fleettracker-backend
```

### 2. Create a Virtual Environment

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=False
DATABASE_URL=postgresql://<user>:<password>@<host>/<database>

CLOUDINARY_CLOUD_NAME=your-cloudinary-cloud-name
CLOUDINARY_API_KEY=your-cloudinary-api-key
CLOUDINARY_API_SECRET=your-cloudinary-api-secret
```

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | Enable or disable debug mode |
| `DATABASE_URL` | Full PostgreSQL connection URL (provided by Render) |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name for media storage |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |

> The database is hosted on Render's managed PostgreSQL service. `DATABASE_URL` is automatically provided when you attach a Render PostgreSQL instance to your web service.

---

## 🗄 Database Setup

Create the database:

```sql
CREATE DATABASE fleettracker;
```

Apply migrations:

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

> **Grading account:** Username: `admin` · Password: `123`

---

## ▶️ Running the Development Server

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`

---

## 📡 API Endpoints

**Base URL:** `https://pagayanan-fleettracker-backend.onrender.com`

All endpoints except `/api/token/` require a JWT Bearer token in the `Authorization` header:

```
Authorization: Bearer <access_token>
```

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/token/` | Login — returns JWT access & refresh tokens |
| `GET` | `/api/current-user/` | Get currently authenticated user |

### Users *(Manager only)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/` | List all users |
| `POST` | `/api/users/` | Create new user |
| `GET` | `/api/users/{id}/` | Get single user |
| `PUT` | `/api/users/{id}/` | Update user |
| `DELETE` | `/api/users/{id}/` | Delete user |

### Assets

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/assets/` | List assets | Manager/Auditor = all · Staff = assigned only |
| `POST` | `/api/assets/` | Create asset | Manager |
| `GET` | `/api/assets/{id}/` | Get single asset | All |
| `PUT` | `/api/assets/{id}/` | Update asset | Manager |
| `DELETE` | `/api/assets/{id}/` | Delete asset | Manager |

### Maintenance Requests

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/requests/` | List all requests | All |
| `POST` | `/api/requests/` | Submit maintenance request | Staff |
| `GET` | `/api/requests/{id}/` | Get single request | All |
| `POST` | `/api/requests/{id}/approve/` | Approve request | Manager |
| `POST` | `/api/requests/{id}/reject/` | Reject request | Manager |

### Work Orders

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/workorders/` | List all work orders | All |
| `GET` | `/api/workorders/{id}/` | Get single work order | All |
| `PUT` | `/api/workorders/{id}/` | Mark as complete | Manager |

### Mileage

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/mileage/` | Get mileage logs | All |
| `POST` | `/api/mileage/` | Submit mileage entry | Staff |

### Dashboard

| Method | Endpoint | Description | Access |
|--------|----------|-------------|--------|
| `GET` | `/api/dashboard/` | Role-based dashboard summary | All roles |

### Reports *(Manager & Auditor)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/reports/assets/` | Asset summary report |
| `GET` | `/api/reports/maintenance/` | Maintenance request report |
| `GET` | `/api/reports/workorders/` | Work order report |
| `GET` | `/api/reports/mileage/` | Mileage report |

### Audit Logs *(Manager & Auditor)*

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/audit-logs/` | Full audit trail of all system actions |

### Alerts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/alerts/` | Assets due for maintenance |

---

## 🔒 Security

- JWT-based authentication
- Role-based authorization
- CSRF protection
- Environment-based secret management
- Secure deployment settings
- Full audit logging

**Security validation commands:**

```bash
# Django deployment checks
python manage.py check --deploy

# Dependency vulnerability scan
pip-audit

# Static security analysis
bandit -r . -x .venv
```

---

## ☁️ Deployment

The application is deployed on **Render**.

### Steps

1. Push repository to GitHub
2. Create a Render Web Service
3. Configure environment variables
4. Attach a PostgreSQL database
5. Run migrations
6. Deploy the application

Collect static files:

```bash
python manage.py collectstatic --noinput
```
