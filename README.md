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

### Linux / macOS

```bash
git clone https://github.com/silas-vale/BruteForcer.git
cd BruteForcer
pip install -r requirements.txt
```

### Windows

1. Install [Python 3.10+](https://www.python.org/downloads/) — check **"Add Python to PATH"** during setup
2. Open Command Prompt or PowerShell:

```powershell
git clone https://github.com/silas-vale/BruteForcer.git
cd BruteForcer
pip install -r requirements.txt
```

> If `git` isn't installed on Windows, download it from [git-scm.com](https://git-scm.com/download/win)

---

## Wordlist

A `wordlist.txt` is included in this repo with ~1 million common passwords, ready to use out of the box.

```bash
python bruteforce.py http://target.local/login -u admin -w wordlist.txt --fail-string "Login failed"
```

You can also use your own wordlist or the built-in rockyou list on Kali Linux:

```
/usr/share/wordlists/rockyou.txt
```

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

**Basic — single username, included wordlist:**
```bash
python bruteforce.py http://target.local/login \
  -u admin \
  -w wordlist.txt \
  --fail-string "Invalid credentials"
```

**Username list + verbose + 20 threads:**
```bash
python bruteforce.py http://target.local/login \
  -U users.txt \
  -w wordlist.txt \
  -t 20 -v
```

**With CSRF token + Burp proxy:**
```bash
python bruteforce.py http://target.local/login \
  -u admin -w wordlist.txt \
  -x csrf_token=abc123def456 \
  --proxy http://127.0.0.1:8080 \
  -v
```

---

## How it works

1. Builds a Cartesian product of all username × password pairs.
2. Dispatches them across a `ThreadPoolExecutor`.
3. Each thread POSTs the form data and checks the response body for the `--fail-string`.
4. On the first response **not** containing the fail string, all pending futures are cancelled and credentials are printed.

---

## Testing with DVWA

To safely test the tool locally, use [DVWA](https://github.com/digininja/DVWA) (Damn Vulnerable Web Application).

> **Note:** If you run the tool without a target server running, you will get `Connection refused` errors — this is expected. You must start DVWA (or another target) first.

### Start DVWA with Docker

**Linux / macOS:**

First check if Docker is installed and running:
```bash
docker --version
sudo systemctl status docker
```

If not installed:
```bash
sudo apt install docker.io -y
sudo systemctl start docker
```

Then start DVWA (keep this terminal open):
```bash
sudo docker run --rm -p 80:80 vulnerables/web-dvwa
```

**Alternative (if `docker` isn't available):**
```bash
sudo apt install podman-docker -y
docker run --rm -p 80:80 vulnerables/web-dvwa
```

**Windows:**  
Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/), then run:
```powershell
docker run --rm -p 80:80 vulnerables/web-dvwa
```

### Run the test

Once DVWA is running, visit `http://localhost/dvwa/setup.php` to initialise the database, then:

```bash
python bruteforce.py http://localhost/dvwa/login.php \
  -u admin \
  -w wordlist.txt \
  --user-field username \
  --pass-field password \
  --fail-string "Login failed" \
  -t 5 -v
```

The default DVWA password (`password`) is in the included wordlist, so you should get a hit quickly.

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
