import os
import time
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

# Define multiple log directories
LOG_DIRS = {
    'frontend': '/home/dev/logs/frontend',
    'backend': '/home/dev/logs/backend',
    'admin': '/home/dev/logs/admin',
    'nginx': '/home/dev/logs/nginx',
    'pm2': '/home/dev/.pm2/logs',
    # Add more directories as needed
}

def get_log_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.log')]

# Add helper function to organize logs by application
def get_app_logs(app_name):
    if app_name not in LOG_DIRS:
        return []
    return get_log_files(LOG_DIRS[app_name])

# Add new route for application-specific logs
@app.route('/logs/apps/<app_name>')
def app_logs(app_name):
    if app_name not in LOG_DIRS:
        return jsonify({'error': 'Invalid application'}), 400
    return jsonify(get_app_logs(app_name))

@app.route('/logs')
def index():
    # Group directories by application type
    app_groups = {
        'Applications': ['frontend', 'backend', 'admin'],
        'System': ['nginx', 'pm2']
    }
    
    group_options = ''
    for group, apps in app_groups.items():
        group_options += f'<optgroup label="{group}">'
        group_options += ''.join(f'<option value="{app}">{app}</option>' for app in apps)
        group_options += '</optgroup>'

    initial_dir = list(LOG_DIRS.keys())[0]
    return f'''
    <html>
        <head>
            <title>Multi-Directory Log Stream Viewer</title>
        </head>
        <body>
            <h1>Multi-Directory Log Stream Viewer</h1>
            <div class="container">
                <div class="controls">
                    <label for="dirSelect">Select Application:</label>
                    <select id="dirSelect" onchange="changeDir(this.value)">
                        {group_options}
                    </select>
                    <label for="logSelect">Select Log File:</label>
                    <select id="logSelect" onchange="changeLog(this.value)"></select>
                    <button class="btn" onclick="clearLog()">Clear Log</button>
                </div>
                <pre id="log"></pre>
            </div>
            <script>
                var eventSource;
                var currentDir;

                // Function to update URL with current selections
                function updateURL(dir, log) {{
                    const params = new URLSearchParams();
                    if (dir) params.set('dir', dir);
                    if (log) params.set('log', log);
                    const newURL = `${{window.location.pathname}}?${{params.toString()}}`;
                    history.pushState({{ dir, log }}, '', newURL);
                }}

                // Function to load selections from URL
                function loadFromURL() {{
                    const params = new URLSearchParams(window.location.search);
                    const dir = params.get('dir');
                    const log = params.get('log');
                    
                    if (dir) {{
                        document.getElementById('dirSelect').value = dir;
                        changeDir(dir, log);
                    }} else {{
                        changeDir('{initial_dir}');
                    }}
                }}

                function changeDir(dir, initialLog = null) {{
                    currentDir = dir;
                    updateURL(dir, null);
                    fetch('/logs/get_logs?dir=' + dir)
                        .then(response => response.json())
                        .then(data => {{
                            var logSelect = document.getElementById('logSelect');
                            logSelect.innerHTML = '';
                            data.forEach(log => {{
                                var option = document.createElement('option');
                                option.value = log;
                                option.text = log;
                                logSelect.appendChild(option);
                            }});
                            if (data.length > 0) {{
                                const logToSelect = initialLog || data[0];
                                logSelect.value = logToSelect;
                                changeLog(logToSelect);
                            }} else {{
                                if (eventSource) {{
                                    eventSource.close();
                                }}
                                document.getElementById('log').textContent = 'No log files found in this directory.';
                            }}
                        }});
                }}

                function changeLog(logFile) {{
                    if (eventSource) {{
                        eventSource.close();
                    }}
                    document.getElementById('log').innerHTML = '';
                    if (logFile) {{
                        updateURL(currentDir, logFile);
                        eventSource = new EventSource(`/logs/stream?dir=${{currentDir}}&log=${{logFile}}`);
                        eventSource.onmessage = function(e) {{
                            let data = e.data;
                            let logElement = document.getElementById('log');
                            let lineElement = document.createElement('div');
                            lineElement.textContent = data;
                            logElement.appendChild(lineElement);
                            logElement.scrollTop = logElement.scrollHeight;
                        }};
                    }}
                }}

                function clearLog() {{
                    document.getElementById('log').innerHTML = '';
                }}

                // Handle browser back/forward buttons
                window.onpopstate = function(event) {{
                    if (event.state) {{
                        changeDir(event.state.dir, event.state.log);
                    }} else {{
                        changeDir('{initial_dir}');
                    }}
                }};

                // Initialize from URL parameters
                loadFromURL();
            </script>
        </body>
    </html>
    '''

@app.route('/logs/get_logs')
def get_logs():
    directory = request.args.get('dir')
    if directory not in LOG_DIRS:
        return "Invalid directory", 400
    log_files = get_log_files(LOG_DIRS[directory])
    return jsonify(log_files)

@app.route('/logs/stream')
def stream():
    directory = request.args.get('dir')
    log_file = request.args.get('log')
    if directory not in LOG_DIRS:
        return jsonify({'error': 'Invalid Request, Directory not found'}), 400
    if not log_file or log_file not in get_log_files(LOG_DIRS[directory]):
        return jsonify({'error': 'Invalid Request, Log file not found'}), 400

    full_path = os.path.join(LOG_DIRS[directory], log_file)

    def generate():
        with open(full_path, 'rb') as f:
            # Move to the end of the file
            f.seek(0, os.SEEK_END)
            # Get the last 10 lines
            lines = []
            block_size = 1024
            file_size = f.tell()
            seek_offset = 0

            while len(lines) < 100 and file_size > 0:
                # Calculate the position to seek to
                seek_offset = min(file_size, seek_offset + block_size)
                f.seek(-seek_offset, os.SEEK_END)
                data = f.read(seek_offset)
                lines = data.splitlines()
                file_size -= seek_offset

            # Decode lines and send the last 100
            decoded_lines = [line.decode('utf-8', errors='replace') for line in lines[-100:]]
            for line in decoded_lines:
                yield f'data: {line}\n\n'

            # Continuously read new lines as they are written to the file
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                decoded_line = line.decode('utf-8', errors='replace').rstrip()
                yield f'data: {decoded_line}\n\n'

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
