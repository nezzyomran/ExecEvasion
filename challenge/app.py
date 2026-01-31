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
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: monospace;
            background: #ffffff;
            color: #000000;
            padding: 1rem;
            margin: 0;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }
        h1 {
            text-align: center;
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }
        .subtitle {
            text-align: center;
            color: #666666;
            margin-bottom: 1rem;
            font-size: 0.8rem;
        }
        .warning {
            background: #fff3f3;
            border: 1px solid #ff0000;
            padding: 0.5rem;
            margin-bottom: 1rem;
            color: #cc0000;
            font-size: 0.8rem;
            word-wrap: break-word;
        }
        .card {
            border: 1px solid #dddddd;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        label {
            display: block;
            margin-bottom: 0.25rem;
            color: #333333;
        }
        input[type="text"] {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #dddddd;
            color: #000000;
            font-family: inherit;
            font-size: 16px;
            margin-bottom: 0.5rem;
            border-radius: 0;
            -webkit-appearance: none;
        }
        input:focus {
            outline: none;
            border-color: #000000;
        }
        button {
            width: 100%;
            padding: 0.75rem;
            background: #f0f0f0;
            border: 1px solid #dddddd;
            color: #000000;
            font-family: inherit;
            font-size: 1rem;
            cursor: pointer;
            -webkit-appearance: none;
            border-radius: 0;
        }
        button:hover, button:active {
            background: #e0e0e0;
        }
        .output {
            border: 1px solid #dddddd;
            padding: 0.75rem;
            white-space: pre-wrap;
            word-wrap: break-word;
            overflow-wrap: break-word;
            font-size: 0.85rem;
            max-height: 300px;
            overflow-y: auto;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        .output.error {
            border-color: #ff0000;
            color: #cc0000;
        }
        .output.success {
            border-color: #000000;
        }
        .blocked-list {
            padding: 0.5rem;
            margin-top: 0.5rem;
        }
        .blocked-list h3 {
            color: #cc0000;
            margin-bottom: 0.25rem;
            font-size: 0.8rem;
        }
        .blocked-list code {
            display: inline-block;
            background: #f0f0f0;
            padding: 0.15rem 0.35rem;
            margin: 0.15rem;
            font-size: 0.75rem;
            color: #666666;
        }
        .hint {
            background: #f0f8ff;
            border: 1px solid #0000ff;
            padding: 0.5rem;
            margin-top: 1rem;
            color: #0000cc;
            font-size: 0.8rem;
            word-wrap: break-word;
        }
        .hint a {
            color: #000000;
            word-break: break-all;
        }
        .hint code {
            background: #e0e8f0;
            padding: 0.1rem 0.25rem;
            word-break: break-all;
        }
        .flag-box {
            background: #f0fff0;
            border: 1px solid #008000;
            padding: 0.75rem;
            margin-top: 0.5rem;
            text-align: center;
        }

        /* Mobile responsive styles */
        @media screen and (max-width: 600px) {
            body {
                padding: 0.5rem;
            }
            h1 {
                font-size: 1.25rem;
            }
            .card {
                padding: 0.75rem;
            }
            input[type="text"] {
                padding: 0.85rem;
                font-size: 16px;
            }
            button {
                padding: 0.85rem;
                font-size: 1rem;
            }
            .blocked-list code {
                font-size: 0.65rem;
                padding: 0.1rem 0.25rem;
                margin: 0.1rem;
            }
            .output {
                font-size: 0.75rem;
                padding: 0.5rem;
                max-height: 250px;
            }
            .warning, .hint {
                font-size: 0.75rem;
                padding: 0.5rem;
            }
        }

        @media screen and (max-width: 380px) {
            h1 {
                font-size: 1.1rem;
            }
            .subtitle {
                font-size: 0.7rem;
            }
            .blocked-list code {
                font-size: 0.6rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SecurePing v1.0</h1>
        <p class="subtitle">Network Diagnostics Tool</p>

        <div class="warning">
            <strong>Security Notice:</strong> This system has command injection protection. Dangerous commands are blocked.
        </div>

        <div class="card">
            <form method="POST">
                <label>Enter hostname or IP to ping:</label>
                <input type="text" name="host" placeholder="example.com" value="{{ host }}" autocomplete="off">
                <button type="submit">Run Diagnostic</button>
            </form>

            <div class="blocked-list">
                <h3>Blocked Keywords:</h3>
                {% for pattern in blocked %}
                <code>{{ pattern }}</code>
                {% endfor %}
            </div>
        </div>

        {% if output %}
        <div class="card">
            <h3 style="margin-bottom: 0.5rem;">Output:</h3>
            <div class="output {{ 'error' if error else 'success' }}">{{ output }}</div>
        </div>
        {% endif %}

        <div class="hint">
            <strong>Challenge:</strong> Read the flag from <code>/tmp/flag.txt</code><br>
            <strong>Hint:</strong> The filter checks for exact substrings. Obfuscate your commands.<br>
            Try using <a href="https://github.com/dr34mhacks/ExecEvasion" target="_blank">ExecEvasion</a> for payloads.
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