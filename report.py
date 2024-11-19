import os
import time
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

# Define multiple log directories
LOG_DIRS = {
    'nginx': '/var/log/nginx',
    'pm2': '/home/dev/.pm2/logs',
    # Add more directories as needed
}

def get_log_files(directory):
    return [f for f in os.listdir(directory) if f.endswith('.log')]

@app.route('/logs')
def index():
    dir_options = ''.join(f'<option value="{dir}">{dir}</option>' for dir in LOG_DIRS.keys())
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
                    <label for="dirSelect">Select Directory:</label>
                    <select id="dirSelect" onchange="changeDir(this.value)">
                        {dir_options}
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
                function changeDir(dir) {{
                    currentDir = dir;
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
                                changeLog(data[0]);
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
                // Initialize with the first directory
                changeDir('{initial_dir}');
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
        return jsonify({'error': 'Invalid Request'}), 400
    if not log_file or log_file not in get_log_files(LOG_DIRS[directory]):
        return jsonify({'error': 'Invalid Log File'}), 400

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
