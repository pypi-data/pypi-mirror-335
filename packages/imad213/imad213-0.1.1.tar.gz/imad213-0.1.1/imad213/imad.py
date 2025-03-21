import os
import requests
import time
from bs4 import BeautifulSoup

# مسح الشاشة قبل العرض
os.system("clear" if os.name == "posix" else "cls")

GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

def main():
    ascii_art = f"""{GREEN}
+--- IMAD-213 ---+

{RED}----IMAD-213>INSTA-FOLLOWERS----{RESET}
{RED}
1 - followers-login
2 - exit{RESET}
"""
    print(ascii_art)

    choice = input(f"{GREEN}Select number: {RESET}")

    if choice == "1":
        session = requests.Session()

        username = input("Enter username: ")
        password = input("Enter password: ")
        target_username = input("Enter target username to send followers: ")

        sites = [
            "takipcimx.net",
            "takipcizen.com",
            "takipcibase.com",
            "takip88.com",
            "www.takipciking.net",
            "www.bigtakip.net",
            "www.takipcigen.com",
            "takipcikrali.com",
            "instamoda.org",
            "takipcimx.net"
        ]

        for site in sites:
            print(f"{RED}START NEW FOLLOWERS{RESET}")

            login_url = f"https://{site}/login?"
            headers = {
                "Host": site,
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
                "Referer": f"https://{site}/login"
            }
            login_data = {
                "username": username,
                "password": password,
                "userid": "",
                "antiForgeryToken": "5e65770c2420a986097445ab74b0e24b"
            }

            response = session.post(login_url, headers=headers, data=login_data)

            if response.status_code == 200 and "success" in response.text:
                print(f"{GREEN}تم تسجيل الدخول بنجاح!{RESET}")

                find_user_url = f"https://{site}/tools/send-follower?formType=findUserID"
                followers_data = {"username": target_username}

                followers_response = session.post(find_user_url, headers=headers, data=followers_data)

                if followers_response.status_code == 200:
                    soup = BeautifulSoup(followers_response.text, 'html.parser')
                    user_id_input = soup.find("input", {"name": "userID"})

                    if user_id_input:
                        user_id = user_id_input["value"]
                        print(f"{RED}START{RESET}")

                        send_followers_url = f"https://{site}/tools/send-follower/{user_id}?formType=send"
                        send_followers_data = {"adet": "100", "userID": user_id, "userName": target_username}

                        send_response = session.post(send_followers_url, headers=headers, data=send_followers_data)

                        if send_response.status_code == 200:
                            print(f"{RED}FOLLOWERS SENT SUCCESS{RESET}")

                            for i in range(10, 110, 10):
                                print(f"{GREEN}FOLLOWERS SUCCESS {i}%{RESET}")
                                time.sleep(4)
                        else:
                            print(f"{RED}ERROR!{RESET}")
                    else:
                        print(f"{RED}COMPTE PRIVATE{RESET}")
                else:
                    print(f"{RED}ERROR!{RESET}")
            else:
                print(f"{RED}COMPTE BANEE{RESET}")

        print("COMPLET SENT FOLLOWERS")

    elif choice == "2":
        print("EXIT...")
    else:
        print(f"{RED}ERROR!{RESET}")

# جعل `main()` تعمل تلقائيًا عند تشغيل السكربت
if __name__ == "__main__":
    main()

