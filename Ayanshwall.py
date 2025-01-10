import requests
import os
import re
import time
import random
from requests.exceptions import RequestException

# Define constants for ANSI colors
GREEN = "\033[1;37;m"
RED = "\033[1;37;m"
CYAN = "\033[1;37;m"
YELLOW = "\033[1;37;m"
BLUE = "\033[1;37;m"
MAGENTA = "\033[1;37;m"
RESET = "\033[0m"

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def lines():
    print('\u001b[37m' + ' WELCOME TO AYANSH TRICKER WALL TOOL')

def lines2():
    print('\u001b[37m' + '[[✓]] <<===========AYANSH-XD ONFIRE=========>>')
def new_logo():
    logo_text = r"""


    """
    

def read_cookie():
    try:
        lines()
        cookies_file = input("\033[1;36m[•]Enter cookies file path  : ")
        lines()
        with open(cookies_file, 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        print("\033[1;31m[!] FILE NOT FOUND. Please provide the correct file path.")
        return None

def make_request(url, headers, cookie):
    try:
        response = requests.get(url, headers=headers, cookies={'Cookie': cookie})
        return response.text
    except RequestException as e:
        print(f"\033[1;31m[!] Error making request: {e}")
        return None

def extract_target_id(url):
    if url.startswith("pfbid"):
        return url.split('/')[0]
    match = re.search(r'pfbid\w+|\d+', url)
    return match.group(0) if match else None

def get_profile_info(token_eaag):
    try:
        response = requests.get(f"https://graph.facebook.com/me?fields=id,name&access_token={token_eaag}")
        profile_info = response.json()
        return profile_info.get("name"), profile_info.get("id")
    except RequestException:
        print("\033[1;31m[!] Error fetching profile information.")
        return None, None

def main():
    cls()
    new_logo()
    

    while True:
        cookies_data = read_cookie()
        if cookies_data is None:
            break

        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; RMX2144 Build/RKQ1.201217.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.71 Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/375.1.0.28.111;]'
        }

        valid_cookies = []
        for cookie in cookies_data:
            response = make_request('https://business.facebook.com/business_locations', headers, cookie)
            if response:
                token_eaag_match = re.search(r'(EAAG\w+)', response)
                if token_eaag_match:
                    valid_cookies.append((cookie, token_eaag_match.group(1)))
                else:
                    print("\033[1;31m[!] EAAG token not found in the response for cookie:", cookie)
            else:
                print("\033[1;31m[!] No response for cookie:", cookie)

        if not valid_cookies:
            print("\033[1;31m[!] No valid cookie found. Exiting...")
            break

        post_url = input("\033[1;34m[[=>]] FB post  link :")
        target_id = extract_target_id(post_url)
        if not target_id:
            print("\033[1;31m[!] Invalid URL. Exiting...")
            break

        commenter_name = input("\033[1;36m[[=>]] Add Hater's Name : ")
        delay = int(input("\033[1;32m[[=>]] Comments sending time (seconds) : "))
        comment_file_path = input("\033[1;36m[[=>]] Add comment file path : ")

        try:
            with open(comment_file_path, 'r') as file:
                comments = file.readlines()
        except FileNotFoundError:
            print("\033[1;31m[!] Comments file not found.")
            break

        x, cookie_index = 0, 0
        while True:
            try:
                teks = comments[x].strip()
                comment_with_name = f"{commenter_name}: {teks}"
                current_cookie, token_eaag = valid_cookies[cookie_index]

                # Fetch profile name and ID
                profile_name, profile_id = get_profile_info(token_eaag)
                if profile_name and profile_id:
                    print(f"\033[1;32mLogged in as: {profile_name} (ID: {profile_id})")

                data = {
                    'message': comment_with_name,
                    'access_token': token_eaag
                }

                response2 = requests.post(f'https://graph.facebook.com/{target_id}/comments/', data=data, cookies={'Cookie': current_cookie})
                response_json = response2.json()

                if 'id' in response_json:
                    print(f"\033[1;32mComment sent successfully at {time.strftime('%Y-%m-%d %H:%M:%S')}: {comment_with_name}")
                    lines2()
                else:
                    print("\033[1;31m[!] Comment failed:", response_json)

                x = (x + 1) % len(comments)
                cookie_index = (cookie_index + 1) % len(valid_cookies)
                time.sleep(delay)

            except RequestException as e:
                print(f"\033[1;31m[!] Error making request: {e}")
                time.sleep(5)
                continue
            except Exception as e:
                print(f"\033[1;31m[!] An unexpected error occurred: {e}")
                break

if __name__ == "__main__":
    main()
