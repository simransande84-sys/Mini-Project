HOSTELSENSE AI
Project Setup and Execution Guide
1. Project Overview
HostelSense AI is an AI-Based Hostel Complaint Prioritization and IoT-Based Water Level Monitoring System.
The application allows users to submit hostel complaints, predicts their base priority using machine learning, supports complaint voting and escalation, and provides an IoT water-monitoring module integrated with Blynk Cloud.
The machine-learning model predicts High, Medium, or Low priority. Critical priority is handled separately by the escalation engine.
2. Technologies Used
•	Frontend: Angular
•	Backend: Python, Django and Django REST Framework
•	Database: PostgreSQL
•	Machine Learning: scikit-learn
•	IoT: ESP32 and Blynk Cloud
3. Project Structure
•	src/backend/ — Django application, APIs, authentication, and business logic
•	src/frontend/ — Angular frontend
•	src/saved_model/ — saved machine-learning model artifacts
•	src/Dataset_duration.csv — machine-learning dataset
•	src/hostel_complaint_prioritization.ipynb — machine-learning training and evaluation notebook
•	db/ — database schema documentation
•	ref/ — research papers and reference materials
•	report/ — project report
•	ppt/ — project presentation
•	readme/ — setup and execution instructions
•	demoVideo/ — project demonstration video
4. Prerequisites
Install the following software:
1.	Python compatible with the supplied backend dependencies
2.	PostgreSQL
3.	Node.js compatible with the Angular project
4.	npm
5.	Visual Studio Code or another code editor
6.	A modern web browser
5. Backend Setup
Step 1: Open the backend folder
Open PowerShell and navigate to the backend directory:
cd src\backend
Step 2: Create a Python virtual environment
python -m venv .venv
Activate it in PowerShell:
.\.venv\Scripts\Activate.ps1
If PowerShell blocks activation, use the virtual environment's Python executable directly instead.
Step 3: Install Python dependencies
python -m pip install -r requirements.txt
Step 4: Configure environment variables
The submission does not include the actual .env file because it contains private credentials.
Create a local .env file using .env.example as the template:
Copy-Item .env.example .env
Edit .env and configure the database name, PostgreSQL username and password, Django secret key, and other settings required for the local installation.
Never publish or share real passwords, secret keys, email app passwords, or Blynk device tokens.
Step 5: Configure PostgreSQL
Start the PostgreSQL service. Create the database specified by DB_NAME in .env, and ensure the configured PostgreSQL user has permission to access it.
The default database name in the project configuration is hostelsense_db.
Step 6: Verify the backend configuration
python manage.py check
Step 7: Create database tables
For a new local database, run:
python manage.py migrate
Step 8: Start the backend server
python manage.py runserver 127.0.0.1:8000
Keep the backend terminal open while using the application.
6. Frontend Setup
Step 1: Open another terminal
Navigate to the Angular frontend folder:
cd src\frontend
Step 2: Install dependencies
npm install
On PowerShell systems where the npm PowerShell script is blocked, use:
npm.cmd install
The project includes package-lock.json to support reproducible dependency installation.
Step 3: Start Angular
npm.cmd start
If the project does not define a start script, use the Angular CLI command configured for the project.
Step 4: Open the application
Open the following URL in a browser:
http://localhost:4200
Keep both the Django backend and Angular frontend running.
7. Machine-Learning Components
The notebook documents the model-training and evaluation workflow. The backend loads the saved model and preprocessing artifacts from src/saved_model/.
The saved artifacts should be preserved and kept compatible with the backend prediction code.
The notebook does not need to be executed merely to start the application.
8. Database and User Accounts
The PostgreSQL database stores application data, including user accounts, student profiles, complaints, and votes.
Existing user accounts and complaint records are not automatically transferred when the source code is copied to another computer.
For a new local database, register a new account through the application. Create an administrative account using Django's createsuperuser command when required.
9. IoT Water-Level Monitoring
The water-monitoring module uses Blynk Cloud to retrieve configured water-level telemetry.
Live readings require valid Blynk configuration and an operational device or telemetry source. Email alerts also require the appropriate email configuration.
These features may remain unavailable until their external services are configured.
10. Troubleshooting
Backend connection refused: Ensure Django is running at 127.0.0.1:8000.
Frontend cannot contact the API: Verify that the API URL in the Angular environment configuration matches the backend address and port.
Database connection failure: Check PostgreSQL, the database name, database permissions, and local .env settings.
Invalid credentials: Confirm that the user account exists in the database used by the running backend and verify the login details.
Missing Python dependency: Install the dependencies listed in requirements.txt in the appropriate Python environment.
Missing frontend dependency: Run npm install from the frontend directory.
Water monitoring unavailable: Verify Blynk credentials, device configuration, and incoming telemetry.
11. Security and Submission Notes
•	The actual .env file must not be included in the submission ZIP.
•	.env.example should contain placeholder values only.
•	The database must be configured locally on the computer where the application runs.
•	Do not delete or replace saved machine-learning artifacts without verifying compatibility.
•	Keep Python and Node.js dependency files with the source code.
12. Execution Summary
1.	Configure PostgreSQL and the local .env file.
2.	Install Python dependencies.
3.	Apply Django migrations to the intended local database.
4.	Start the Django backend.
5.	Install frontend dependencies.
6.	Start the Angular frontend.
7.	Open http://localhost:4200 and test the application.
The availability of authentication, database operations, machine-learning predictions, and live IoT readings depends on correct local configuration and verification.

