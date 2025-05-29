# Smart Complaint Redressal System

A web-based complaint management platform developed as part of a semester project for Database Management Systems (DBMS). The system allows students to submit complaints and administrators to manage and escalate them efficiently.

## Project Description

This project aims to streamline complaint submission and redressal in an institutional setting through a secure, scalable, and user-friendly web application. It supports role-based access for both **students** and **admins**, ensuring appropriate privileges across the platform.

## Tech Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML, Bootstrap 5, JavaScript
- **Database:** SQL Server
- **Database Connection:** pyodbc

## Key Features

- Role-based access control (Admin / Student)
- Department-specific complaint title dropdown
- Dynamic form submission using AJAX
- Real-time password and field validation
- CRUD operations for complaints and users
- Profile management (update, delete account)
- Flash message notifications and Bootstrap toasts

## Project Structure

```
project/
│
├── templates/             # HTML templates
│   ├── dashboard_student.html
│   ├── dashboard_admin.html
│   ├── login.html
│   ├── signup.html
|   ├── manage_users.html
|   ├── submit_complaint.html
|   ├── view_complaint.html
│   └── profile.html
│
├── static/                # (Optional) CSS, JS, assets
├── db_config.py           # Database connection config
├── app.py                 # Main Flask application
├── requirements.txt
└── README.md              # Project readme
```

## Database Schema Overview

- **User**: Stores student/admin info (with role field)
- **Complaint**: Records complaints submitted by users
- **Department**: List of institutional departments
- **Status**: Tracks status (Pending, In Progress, Resolved)
- **IssueTitle**: Titles per department for dropdown logic

## Access Control

- Students can: Submit, view, and delete their own complaints  
- Admins can: View all complaints, delete any, manage user roles

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/Gushtasp47/SmartComplaintSystem.git
   cd SmartComplaintSystem
   ```
2. Set up a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure `db_config.py` with your SQL Server credentials.
5. Create database and run schema script (included separately).
6. Run the app:
   ```bash
   python app.py
   ```
7. Visit `http://127.0.0.1:5000/` in your browser.

## Demo Video

*Available upon request or in [LinkedIn](https://www.linkedin.com/posts/shehzada-gushtasp-khan-1a6a6a292_flask-sqlserver-dbms-activity-7333842967880740866-oSbe?utm_source=share&utm_medium=member_desktop&rcm=ACoAAEb-Ao4BtgKleakDaNvfCRGMbUfXnZXdYS4) post.*

---

Feel free to fork, contribute, or raise issues. This project was created with learning, collaboration, and real-world relevance in mind.

---

**Author:** Shehzada Gushtasp Khan & Muhammad Dayyan Qazi  
**Course:** Database Management Systems  
**Institution:** Bahria University

