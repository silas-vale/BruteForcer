# BruteForcer

A fast, threaded HTTP login brute-forcer written in Python 3.10+.  
Built for penetration testers and CTF players.

> **LEGAL DISCLAIMER**  
> This tool is intended **solely for authorized penetration testing, security research, and CTF challenges**.  
> Using it against systems you do not own or have **explicit written permission** to test is illegal under the Computer Fraud and Abuse Act (CFAA), the UK Computer Misuse Act, and equivalent laws worldwide.  
> The author assumes no liability for misuse.

---

## Features

- Single username or username list support
- Threaded — configurable concurrency
- Per-thread request delay for rate-limit evasion
- Configurable form field names (works with any HTML login form)
- Failure-string detection (stops on first hit)
- Extra POST field injection (CSRF tokens, hidden inputs)
- Proxy support (works with Burp Suite, OWASP ZAP)
- Verbose mode shows every attempt in real time

---

## Installation

**Clone the repo:**
```bash
git clone https://github.com/silas-vale/BruteForcer.git
cd BruteForcer
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

Requires Python 3.10+.

---

## Usage

```
python bruteforce.py <url> -u <user> -w <wordlist> [options]
```

### Arguments

| Flag | Description | Default |
|------|-------------|---------|
| `url` | Login endpoint | *(required)* |
| `-u / --username` | Single username | |
| `-U / --userlist` | File with usernames | |
| `-w / --wordlist` | Password wordlist | *(required)* |
| `--user-field` | HTML name of username field | `username` |
| `--pass-field` | HTML name of password field | `password` |
| `--fail-string` | String in response body on failure | `Invalid` |
| `-x KEY=VALUE` | Extra POST fields (repeatable) | |
| `-t / --threads` | Concurrent threads | `10` |
| `-d / --delay` | Per-thread delay (seconds) | `0.0` |
| `--timeout` | Request timeout (seconds) | `10` |
| `--proxy` | HTTP(S) proxy URL | |
| `-v / --verbose` | Print every attempt | |

---

## Examples

**Basic — single username, rockyou wordlist:**
```bash
python bruteforce.py http://target.local/login \
  -u admin \
  -w /usr/share/wordlists/rockyou.txt \
  --fail-string "Invalid credentials"
```

**Username list + verbose + 20 threads:**
```bash
python bruteforce.py http://target.local/login \
  -U users.txt \
  -w passwords.txt \
  -t 20 -v
```

**With CSRF token + Burp proxy:**
```bash
python bruteforce.py http://target.local/login \
  -u admin -w passwords.txt \
  -x csrf_token=abc123def456 \
  --proxy http://127.0.0.1:8080 \
  -v
```

**Custom form fields (e.g. DVWA):**
```bash
python bruteforce.py "http://dvwa.local/login.php" \
  -u admin -w passwords.txt \
  --user-field username \
  --pass-field password \
  --fail-string "Login failed"
```

---

## How it works

1. Builds a Cartesian product of all username × password pairs.
2. Dispatches them across a `ThreadPoolExecutor`.
3. Each thread POSTs the form data and checks the response body for the `--fail-string`.
4. On the first response **not** containing the fail string, all pending futures are cancelled and credentials are printed.

---

## Good test targets

Practice on deliberately vulnerable apps — never on live systems without permission:

- [DVWA](https://github.com/digininja/DVWA) (Damn Vulnerable Web Application)
- [HackTheBox](https://www.hackthebox.com/)
- [TryHackMe](https://tryhackme.com/)
- [OWASP WebGoat](https://github.com/WebGoat/WebGoat)

---

## License

MIT
