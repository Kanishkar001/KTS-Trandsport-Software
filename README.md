# 🚛 KTS Transport — Smart Fleet & Expense Management System

## 📌 About This Project

**KTS Transport** is a desktop-based Transport Management System developed using **Python** and **PyQt6**.  
The application helps transport businesses manage vehicles, drivers, trips, and expenses through a modern graphical interface.

This software replaces manual record keeping and spreadsheets with a structured digital system that improves accuracy, tracking, and reporting.

---

## 🎯 Purpose

Transport operations often face challenges such as:

- Manual bookkeeping errors
- Difficulty tracking vehicle expenses
- Poor visibility of trip profits
- Time-consuming report preparation

This project provides a **centralized solution** to manage all transport-related operations efficiently.

---

## ⚙️ Features

### 🚚 Vehicle & Driver Management
- Store vehicle registration details
- Maintain driver information
- Track insurance, permits, tax, and fitness expiry
- Loan and financial tracking

### 🗺️ Trip Management
- Create and manage trip records
- Track routes and broker offices
- Automatic profit & expense calculation
- Paid / Unpaid trip status
- Advanced filtering options

### 💰 Expense Management
- Vehicle maintenance expenses
- Tyre, tax, insurance, and spare work tracking
- Monthly office expense management
- Automatic total calculations

### 📊 Reports & Export
- Export reports to **PDF**
- Export data to **Excel**
- Financial summaries
- Custom date filtering

### 🔐 Security
- Login authentication system
- Password hashing
- OTP-based password reset
- Secure SQLite database

### 🖥️ User Interface
- Built with PyQt6
- Modern dashboard layout
- Easy navigation
- Professional desktop design

---

## 🧱 Tech Stack

| Technology | Usage |
|------------|-------|
| Python 3 | Core Programming |
| PyQt6 | GUI Framework |
| SQLite3 | Database |
| ReportLab | PDF Reports |
| OpenPyXL / Pandas | Excel Export |

---

## 🗄️ Database Modules

- Trips Management
- Vehicle Expenses
- Office Expenses
- Vehicle & Driver Details
- User Authentication

Database tables are automatically created during first run.

---

## 🚀 Installation

```bash
# Clone repository
git clone https://github.com/your-username/kts-transport.git

# Go into project folder
cd kts-transport

# Install dependencies
pip install PyQt6 reportlab pandas openpyxl

# Run application
python homepage.py
