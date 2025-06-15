# Asset Manager

## Overview

Asset Manager is a simple web-based asset management system built with Flask.  
- **User Functions:** Register, log in, and submit asset requests.  
- **Admin Functions:** Review, approve, or reject asset submissions.

## Features

- **User Authentication:** Secure registration and login using Flask-Login.
- **Asset Management:** Submit asset details and track their status.
- **Role-Based Access:** Separate interfaces for regular users and administrators.

## Getting Started

### Prerequisites

- Python 3.x  
- pip

### Installation

1. **Clone the Repository:**

   ```bash
   git clone (REPO LINK)
   cd asset_manager

Set Up a Virtual Environment:

bash
python -m venv venv
# Activate the virtual environment:
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
Install Dependencies:

bash
pip install -r requirements.txt
Running the Application
Configure the App: The default configuration uses a local SQLite database (assets.db). Adjust settings in your configuration file or in app/__init__.py if needed.

Start the Application:

bash
flask run
Access the Application: Open your browser and navigate to http://127.0.0.1:5000.

Running the Tests
Ensure Your Virtual Environment is Active.

Run Pytest:

bash
pytest
This will execute all the tests in the tests/ folder.

Usage
User Registration: Click "Register" on the login page, fill in your username and password, and submit the form.

User Login: Enter your credentials on the login page to access your dashboard.

Asset Submission (Regular Users): After logging in, navigate to the asset submission page, enter asset details (e.g., name, category, purchase date), and submit.

Asset Approval (Admins): Log in with admin credentials, navigate to the admin dashboard, and use the controls to approve or reject asset submissions.