#!/usr/bin/env python3

import os
from flask import Flask, Response, request, jsonify, render_template, send_file
from flask_login import login_required
from dotenv import load_dotenv
from services.log_manager import LogManager
from services.log_stream_reader import LogStreamReader
from services.log_download import LogDownloader
from services.logger import setup_logger
from auth.auth import auth_bp, init_auth

load_dotenv()

app = Flask(__name__)
logger = setup_logger('flask_app')
log_manager = LogManager()

# Register authentication blueprint and initialize
app.register_blueprint(auth_bp)
init_auth(app)

@app.route('/logs')
@login_required
def index():
    logger.info("Accessing main log viewer page")
    initial_dir = list(log_manager.directories.keys())[0]
    return render_template('log_viewer.html',
                         app_groups=log_manager.get_app_groups(),
                         initial_dir=initial_dir)

@app.route('/logs/get_logs')
@login_required
def get_logs():
    directory = request.args.get('dir')
    logger.info(f"Getting logs for directory: {directory}")
    
    log_dir = log_manager.get_directory(directory) if directory else None
    if not log_dir:
        logger.warning(f"Invalid directory requested: {directory}")
        return "Invalid directory", 400
    return jsonify(log_dir.get_logs())

@app.route('/logs/stream')
@login_required
def stream():
    directory = request.args.get('dir')
    log_file = request.args.get('log')
    
    logger.info(f"Streaming request for {log_file} in {directory}")
    
    log_dir = log_manager.get_directory(directory) if directory else None
    if not log_dir:
        logger.warning(f"Invalid directory requested: {directory}")
        return jsonify({'error': 'Invalid Request, Directory not found'}), 400
    
    if not log_file or log_file not in log_dir.get_logs():
        logger.warning(f"Invalid log file requested: {log_file}")
        return jsonify({'error': 'Invalid Request, Log file not found'}), 400

    log_path = log_dir.get_log_path(log_file)
    stream_reader = LogStreamReader(log_path)
    return Response(stream_reader.generate_stream(), mimetype='text/event-stream')

@app.route('/logs/download')
@login_required
def download_log():
    directory = request.args.get('dir')
    log_file = request.args.get('log')
    
    logger.info(f"Download request for {log_file} in {directory}")
    
    log_dir = log_manager.get_directory(directory) if directory else None
    if not log_dir:
        logger.warning(f"Invalid directory requested: {directory}")
        return jsonify({'error': 'Invalid Request, Directory not found'}), 400
    
    if not log_file or log_file not in log_dir.get_logs():
        logger.warning(f"Invalid log file requested: {log_file}")
        return jsonify({'error': 'Invalid Request, Log file not found'}), 400

    log_path = log_dir.get_log_path(log_file)
    downloader = LogDownloader(log_path)
    
    return send_file(
        log_path,
        mimetype='text/plain',
        as_attachment=True,
        download_name=log_file
    )

# Create an initial admin user
def create_admin_user():
    from auth.auth import User, db
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            logger.info("Creating initial admin user")
            admin = User(username='admin')
            admin.set_password(str(os.getenv('ADMIN_PASS', 'admin123')))  # Change this password
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    auth_mode = int(os.getenv('AUTH_MODE', '0'))
    logger.info(f"Authentication mode: {auth_mode}")
    if auth_mode in [0, 2]:
        logger.info("Initializing authentication")
        create_admin_user()  # Create initial admin user
    logger.info("Starting Flask application")
    app.run(debug=True, port=int(os.getenv('PORT', 5000)))
