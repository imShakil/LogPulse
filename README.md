# LogPulse

A Flask-based web application for real-time log monitoring and management across multiple directories.

## Features

- Real-time log streaming
- Multi-directory log monitoring
- Secure authentication (Local DB and/or API)
- Download logs functionality
- Clean and responsive UI
- Session management
- URL-based navigation

## Prerequisites

- Python 3.8 or higher
- PostgreSQL (for local authentication)
- pip (Python package manager)

## Installation

1. Clone the repository:

    ```bash
    git clone <repository-url>
    cd reporting
    ```

2. Create and activate a virtual environment:

    ```bash
    python -m venv venv
    source venv/bin/activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Configure environment variables:

    ```bash
    cp .env.example .env # Rename to .env and update the value as needed
    ```

## Running the Application

1. Start the Flask application:

    ```bash
    python report.py
    ```

2. Access the application in your web browser at ess the application in your web browser at `http://localhost:5000`

## Authentication Modes

1. Local Database (MODE 0)
   - Uses PostgreSQL for user authentication
   - Default admin credentials: username: admin, password: admin123

2. API Authentication (MODE 1)
   - Uses external API for authentication
   - Requires valid API endpoint configuration

3. Hybrid Mode (MODE 2)
   - Attempts API authentication first
   - Falls back to local database if API fails

## Directory Structure

```plaintext
reporting/
├── auth/
│   └── auth.py
├── services/
│   ├── logger.py
│   ├── log_manager.py
│   ├── log_stream_reader.py
│   └── log_download.py
|   └── log_directory.py
|   └── file_system_log_directory.py
├── static/
│   └── css/
│       └── style.css
├── templates/
│   ├── login.html
│   └── log_viewer.html
├── .env
├── requirements.txt
└── report.py
```

## Security Considerations

- Use HTTPS in production
- Change default admin credentials
- Set a strong SECRET_KEY
- Properly configure file permissions for log directories
- Use environment variables for sensitive data

## Licese
