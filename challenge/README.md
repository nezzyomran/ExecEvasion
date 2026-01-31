# ExecEvasion CTF Challenge

A practice vulnerable web application to demonstrate command obfuscation bypass techniques.

## Overview

This challenge simulates a "secure" ping utility with WAF-like protection that blocks common dangerous commands. Your goal is to bypass the filter and read the flag.

## Setup

1. Install dependencies:
```bash
pip install flask
```

2. Run the challenge server:
```bash
python app.py
```

3. Open http://127.0.0.1:5000 in your browser

## Challenge

**Objective:** Read the contents of `/tmp/flag.txt`

**Difficulty:** Easy-Medium

The application:
- Takes user input for a "hostname" to ping
- Has a blocklist filter checking for dangerous keywords
- Is vulnerable to command injection via the ping parameter

## Blocked Keywords

The filter blocks these patterns:
- `cat`, `head`, `tail`, `less`, `more`, `nl`
- `flag`, `etc`, `passwd`, `shadow`
- `bash`, `sh`, `python`, `perl`, `ruby`
- `nc`, `netcat`, `curl`, `wget`, `base64`
- `/bin`, `/usr`

## Hints

<details>
<summary>Hint 1 (Mild)</summary>
The filter only checks for exact substring matches. What if you could break up the blocked words?
</details>

<details>
<summary>Hint 2 (Medium)</summary>
Try using ExecEvasion to generate obfuscated payloads. Techniques like quotes, backslashes, or glob patterns can help.
</details>


## Warning

This application is **intentionally vulnerable** and should only be run locally for educational purposes. Never expose it to the internet or use it in production.


---
Part of the ExecEvasion project by [Sid Joshi](https://github.com/dr34mhacks)
