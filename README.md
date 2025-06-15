# Asset Manager

## Overview

Asset Manager is a simple web-based asset management system built with Flask.
- User Functions: Register, log in, and submit asset requests.
- Admin Functions: Review, approve, or reject asset submissions.

## Features

- User Authentication: Secure registration and login using Flask-Login.
- Asset Management: Submit asset details and track their status.
- Role-Based Access: Separate interfaces for regular users and administrators.

## Getting Started

### Prerequisites

- Python 3.x
- pip

### Installation

1. Clone the Repository:

   git clone (REPO LINK)
   cd asset_manager

2. Set Up a Virtual Environment:

   python -m venv venv
   # Activate the virtual environment:
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate

3. Install Dependencies:

   pip install -r requirements.txt

## Running the Application

1. Configure the App:
   The default configuration uses a local SQLite database (assets.db).
   Adjust settings in your configuration file or in app/__init__.py if needed.

2. Start the Application:

   flask run

3. Access the Application:
   Open your browser and navigate to http://127.0.0.1:5000

## Running the Tests

1. Ensure Your Virtual Environment is Active.

2. Run Pytest:

   pytest

   This will execute all the tests in the tests/ folder.

## Usage

- User Registration:
  Click "Register" on the login page, fill in your username and password, and submit the form.

- User Login:
  Enter your credentials on the login page to access your dashboard.

- Asset Submission (Regular Users):
  After logging in, navigate to the asset submission page, enter asset details (e.g., asset name, category, purchase date), and submit the form.

- Asset Approval (Admins):
  Log in with admin credentials, navigate to the admin dashboard, and use the provided controls to approve or reject asset submissions.

## Additional Information

- Source Code:
  The complete source code is available on GitHub at: (REPO LINK)

- Deployment:
  This app can be deployed on free public cloud platforms (e.g., Heroku, AWS, or Azure).
