#!/usr/bin/env python3
"""
ExecEvasion CTF Challenge
A vulnerable web application to practice command obfuscation bypasses.

Made with love by @dr34mhacks
"""

from flask import Flask, request, render_template_string
import subprocess
import re

app = Flask(__name__)

# Blocked patterns - these are common command injection payloads
BLOCKED_PATTERNS = [
    'cat',
    'head',
    'tail',
    'less',
    'more',
    'nl',
    'flag',
    'etc',
    'passwd',
    'shadow',
    'bash',
    'sh',
    'python',
    'perl',
    'ruby',
    'nc',
    'netcat',
    'curl',
    'wget',
    'base64',
    '/bin',
    '/usr',
]

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SecurePing v1.0 - Network Diagnostics</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff41;
            min-height: 100vh;
            padding: 2rem;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 0.5rem;
            font-size: 2rem;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 2rem;
            font-size: 0.9rem;
        }
        .warning {
            background: rgba(255, 0, 0, 0.1);
            border: 1px solid #ff0000;
            padding: 1rem;
            margin-bottom: 2rem;
            border-radius: 8px;
            color: #ff6666;
            font-size: 0.85rem;
        }
        .card {
            background: #111;
            border: 1px solid #333;
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        label {
            display: block;
            margin-bottom: 0.5rem;
            color: #888;
        }
        input[type="text"] {
            width: 100%;
            padding: 1rem;
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 8px;
            color: #00ff41;
            font-family: inherit;
            font-size: 1rem;
            margin-bottom: 1rem;
        }
        input:focus {
            outline: none;
            border-color: #00ff41;
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.2);
        }
        button {
            width: 100%;
            padding: 1rem;
            background: #00ff41;
            border: none;
            border-radius: 8px;
            color: #000;
            font-family: inherit;
            font-size: 1rem;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        button:hover {
            background: #33ff66;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.4);
        }
        .output {
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 8px;
            padding: 1.5rem;
            white-space: pre-wrap;
            font-size: 0.9rem;
            max-height: 400px;
            overflow-y: auto;
        }
        .output.error {
            border-color: #ff0000;
            color: #ff6666;
        }
        .output.success {
            border-color: #00ff41;
        }
        .blocked-list {
            background: #0a0a0a;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
        }
        .blocked-list h3 {
            color: #ff6666;
            margin-bottom: 0.5rem;
            font-size: 0.9rem;
        }
        .blocked-list code {
            display: inline-block;
            background: #1a1a1a;
            padding: 0.2rem 0.5rem;
            margin: 0.2rem;
            border-radius: 4px;
            font-size: 0.8rem;
            color: #888;
        }
        .hint {
            background: rgba(0, 100, 255, 0.1);
            border: 1px solid #0066ff;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 2rem;
            color: #66aaff;
            font-size: 0.85rem;
        }
        .hint a {
            color: #00ff41;
        }
        .flag-box {
            background: rgba(0, 255, 65, 0.1);
            border: 1px solid #00ff41;
            padding: 1rem;
            border-radius: 8px;
            margin-top: 1rem;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SecurePing v1.0</h1>
        <p class="subtitle">Enterprise Network Diagnostics Tool</p>

        <div class="warning">
            <strong>Security Notice:</strong> This system has advanced command injection protection.
            All dangerous commands are blocked by our WAF.
        </div>

        <div class="card">
            <form method="POST">
                <label>Enter hostname or IP to ping:</label>
                <input type="text" name="host" placeholder="example.com" value="{{ host }}" autocomplete="off">
                <button type="submit">Run Diagnostic</button>
            </form>

            <div class="blocked-list">
                <h3>Blocked Keywords (WAF Protection):</h3>
                {% for pattern in blocked %}
                <code>{{ pattern }}</code>
                {% endfor %}
            </div>
        </div>

        {% if output %}
        <div class="card">
            <h3 style="margin-bottom: 1rem;">Output:</h3>
            <div class="output {{ 'error' if error else 'success' }}">{{ output }}</div>
        </div>
        {% endif %}

        <div class="hint">
            <strong>Challenge:</strong> Read the flag from <code>/tmp/flag.txt</code><br><br>
            <strong>Hint:</strong> The filter is checking for exact substrings. Can you obfuscate your commands?<br>
            Try using <a href="https://github.com/dr34mhacks/ExecEvasion" target="_blank">ExecEvasion</a> to generate bypass payloads!
        </div>

        {% if flag_found %}
        <div class="flag-box">
            <strong>Congratulations! You found the flag!</strong>
        </div>
        {% endif %}
    </div>
</body>
</html>
'''

def is_blocked(command):
    """Check if command contains any blocked patterns (case-insensitive)"""
    command_lower = command.lower()
    for pattern in BLOCKED_PATTERNS:
        if pattern.lower() in command_lower:
            return True, pattern
    return False, None

def execute_command(command):
    """Execute the ping command (vulnerable to command injection)"""
    try:
        # Vulnerable: directly concatenating user input
        full_command = f"ping -c 1 {command} 2>&1"
        result = subprocess.run(
            full_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout + result.stderr, False
    except subprocess.TimeoutExpired:
        return "Command timed out", True
    except Exception as e:
        return f"Error: {str(e)}", True

@app.route('/', methods=['GET', 'POST'])
def index():
    output = None
    error = False
    host = ""
    flag_found = False

    if request.method == 'POST':
        host = request.form.get('host', '')

        if not host:
            output = "Please enter a hostname or IP address"
            error = True
        else:
            # Check against blocklist
            blocked, pattern = is_blocked(host)

            if blocked:
                output = f"[WAF BLOCKED] Dangerous pattern detected: '{pattern}'\n\nYour input has been logged and reported."
                error = True
            else:
                output, error = execute_command(host)

                # Check if flag was found in output
                if 'FLAG{' in output or 'flag{' in output:
                    flag_found = True

    return render_template_string(
        HTML_TEMPLATE,
        output=output,
        error=error,
        host=host,
        blocked=BLOCKED_PATTERNS,
        flag_found=flag_found
    )

def setup_flag():
    """Create the flag file"""
    import os
    flag_content = "FLAG{blocked_0_exec_evasion_1}"
    flag_path = "/tmp/flag.txt"
    try:
        with open(flag_path, 'w') as f:
            f.write(flag_content)
        print(f"[+] Flag created at {flag_path}")
    except Exception as e:

        print(f"[-] Could not create flag: {e}")
        print("[*] You may need to manually create /tmp/flag.txt")

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║          ExecEvasion CTF Challenge Server                 ║
    ║                                                           ║
    ║  This is an intentionally vulnerable application for      ║
    ║  practicing command obfuscation techniques.               ║
    ║                                                           ║
    ║  DO NOT expose this to the internet!                      ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    setup_flag()
    print("[*] Starting server on http://127.0.0.1:5000")
    print("[*] Open the URL in your browser to start the challenge")
    print("[*] Use ExecEvasion to generate bypass payloads!\n")

    app.run(host='127.0.0.1', port=5000, debug=False)
