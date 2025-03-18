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
    git clone https://github.com/imShakil/LogPulse.git
    cd LogPulse
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

1. Using Python directly:

    ```bash
    python report.py
    ```

2. Using PM2 (Recommended for production):

    ```bash
    # Install PM2 if not installed
    npm install pm2 -g

    # Start using ecosystem config
    pm2 start ecosystem.config.js

    # Other useful PM2 commands
    pm2 status                  # Check application status
    pm2 logs logpulse          # View logs
    pm2 restart logpulse       # Restart application
    pm2 stop logpulse          # Stop application
    pm2 delete logpulse        # Remove from PM2

    # For production environment
    pm2 start ecosystem.config.js --env production
    ```

3. Access the application in your web browser at `http://localhost:5000`

Note: The application includes a PM2 ecosystem configuration file [`ecosystem.config.js`](./ecosystem.config.js) that handles:

- Python interpreter settings
- Instance management
- Auto-restart capability
- Memory limits
- Environment-specific configurations

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
└── logpulse.py
```

## Security Considerations

- Use HTTPS in production
- Change default admin credentials
- Set a strong SECRET_KEY
- Properly configure file permissions for log directories
- Use environment variables for sensitive data

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) for details.
