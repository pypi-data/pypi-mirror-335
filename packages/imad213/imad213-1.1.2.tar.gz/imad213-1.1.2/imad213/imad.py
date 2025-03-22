import os
import requests
import time
from bs4 import BeautifulSoup


def main():
    os.system("clear" if os.name == "posix" else "cls")

    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    ascii_art = f"""{GREEN}
 ___ __  __    _    ____       ____  _ _____ 
|_ _|  \/  |  / \  |  _ \     |___ \/ |___ / 
 | || |\/| | / _ \ | | | |_____ __) | | |_ \ 
 | || |  | |/ ___ \| |_| |_____/ __/| |___) |
|___|_|  |_/_/   \_\____/     |_____|_|____/ {RESET}

    {RED}----IMAD-213>INSTA-FOLLOWERS----{RESET}
    {RED}
    1 - followers-login
    2 - likes-reels
    3 - view-reels
    4 - comment-reels
    5 - exit{RESET}
    """

    print(ascii_art)

    choice = input(f"{GREEN}Select number: {RESET}")

    if choice == "1":
        session = requests.Session()

        username = input("Enter username: ")
        password = input("Enter password: ")
        target_username = input("Enter target username to send followers: ")

        sites = [
            "takipcimx.net", "takipcizen.com", "www.bigtakip.net",
            "takip88.com", "www.takipciking.net", "www.takipcigen.com",
            "takipcikrali.com", "takipcitime.net", "takipcimx.net",
            "takipciking.net"
        ]

        for site in sites:
            print(f"{RED}START NEW FOLLOWERS{RESET}")

            try:
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

                response = session.post(login_url, headers=headers, data=login_data, allow_redirects=False)

                if response.status_code == 200 and "success" in response.text:
                    print(f"{GREEN}LOGIN SUCCESS{RESET}")

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
                            send_followers_data = {"adet": "150", "userID": user_id, "userName": target_username}

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
            except requests.exceptions.TooManyRedirects:
                print(f"{RED}ERROR: Too many redirects on {site}{RESET}")
            except Exception as e:
                print(f"{RED}Unexpected error: {e}{RESET}")

            print("Waiting 60 seconds ...")
            time.sleep(60)

        print(f"{RED}COMPLET SENT FOLLOWERS{RESET}")

    elif choice == "2":
        session = requests.Session()

        username = input("Enter username: ")
        password = input("Enter password: ")
        video_url = input("Enter video URL: ")

        sites = [
            "instamoda.org", "takipcimx.net", "takipcizen.com", "www.bigtakip.net",
            "takip88.com", "www.takipciking.net", "www.takipcigen.com",
            "takipcikrali.com", "takipcitime.net", "takipcimx.net", "takipciking.net"
        ]

        for site in sites:
            print(f"{RED}START NEW COMMENT{RESET}")

            try:
                login_url = f"https://{site}/login?"
                headers = {
                    "Host": site,
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
                }

                login_data = {
                    "username": username,
                    "password": password
                }

                response = session.post(login_url, headers=headers, data=login_data)

                if response.status_code == 200:
                    print(f"{GREEN}LOGIN SUCCESS{RESET}")

                    media_data = {"mediaUrl": video_url}
                    find_media_url = f"https://{site}/tools/send-like?formType=findMediaID"

                    media_response = session.post(find_media_url, headers=headers, data=media_data)

                    if media_response.status_code == 200:
                        soup = BeautifulSoup(media_response.text, 'html.parser')
                        media_id_input = soup.find("input", {"name": "mediaID"})

                        if media_id_input:
                            media_id = media_id_input["value"]
                            print(f"Media ID extracted: {media_id}")

                            send_like_url = f"https://{site}/tools/send-like/{media_id}?formType=send"
                            send_like_data = {
                                "adet": "10",
                                "mediaID": media_id
                            }

                            for i in range(10, 110, 10):
                                send_response = session.post(send_like_url, headers=headers, data=send_like_data)

                                if send_response.status_code == 200:
                                    print(f"{GREEN}COMMENT SUCCESS {i}%{RESET}")
                                    time.sleep(2)
                                else:
                                    print(f"{RED}ERROR IN COMMENTING !{RESET}")
                                    break

                        else:
                            print(f"{RED}MEDIA ID NOT FOUND!{RESET}")
                    else:
                        print(f"{RED}ERROR IN FINDING MEDIA ID!{RESET}")
                else:
                    print(f"{RED}LOGIN ERROR!{RESET}")
            except Exception as e:
                print(f"{RED}Error! {e}{RESET}")

            print("Waiting 60 seconds ...")
            time.sleep(60)

        print(f"{RED}COMPLET COMMENT SENT{RESET}")

    elif choice == "3":
        session = requests.Session()

        username = input("Enter username: ")
        password = input("Enter password: ")
        video_url = input("Enter video URL: ")

        sites = [
            "instamoda.org", "takipcimx.net", "takipcizen.com", "www.bigtakip.net",
            "takip88.com", "www.takipciking.net", "www.takipcigen.com",
            "takipcikrali.com", "takipcitime.net", "takipcimx.net", "takipciking.net"
        ]

        for site in sites:
            print(f"{RED}START NEW VIEW{RESET}")

            try:
                login_url = f"https://{site}/login?"
                headers = {
                    "Host": site,
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
                }

                login_data = {
                    "username": username,
                    "password": password
                }

                response = session.post(login_url, headers=headers, data=login_data)

                if response.status_code == 200:
                    print(f"{GREEN}LOGIN SUCCESS on {site}{RESET}")

                    media_data = {"mediaUrl": video_url}
                    find_media_url = f"https://{site}/tools/send-like?formType=findMediaID"

                    media_response = session.post(find_media_url, headers=headers, data=media_data)

                    if media_response.status_code == 200:
                        soup = BeautifulSoup(media_response.text, 'html.parser')
                        media_id_input = soup.find("input", {"name": "mediaID"})

                        if media_id_input:
                            media_id = media_id_input["value"]
                            print(f"Media ID extracted: {media_id}")

                            send_like_url = f"https://{site}/tools/send-like/{media_id}?formType=send"
                            send_like_data = {
                                "adet": "10",
                                "mediaID": media_id
                            }

                            for i in range(10, 110, 10):
                                send_response = session.post(send_like_url, headers=headers, data=send_like_data)

                                if send_response.status_code == 200:
                                    print(f"{GREEN}VIEW SUCCESS {i}%{RESET}")
                                    time.sleep(2)
                                else:
                                    print(f"{RED}ERROR IN VIEWING!{RESET}")
                                    break

                        else:
                            print(f"{RED}MEDIA ID NOT FOUND!{RESET}")
                    else:
                        print(f"{RED}ERROR IN FINDING MEDIA ID!{RESET}")
                else:
                    print(f"{RED}LOGIN ERROR!{RESET}")
            except Exception as e:
                print(f"{RED}Error! {e}{RESET}")

            print("Waiting 60 seconds ...")
            time.sleep(60)

        print(f"{RED}COMPLET VIEWS SENT{RESET}")

    elif choice == "4":
        session = requests.Session()

        username = input("Enter username: ")
        password = input("Enter password: ")
        video_url = input("Enter video URL: ")
        comment_message = input("Enter your comment message: ")

        sites = [
            "instamoda.org", "takipcimx.net", "takipcizen.com", "www.bigtakip.net",
            "takip88.com", "www.takipciking.net", "www.takipcigen.com",
            "takipcikrali.com", "takipcitime.net", "takipcimx.net", "takipciking.net"
        ]

        for site in sites:
            print(f"{RED}START NEW COMMENT{RESET}")

            try:
                login_url = f"https://{site}/login?"
                headers = {
                    "Host": site,
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
                }

                login_data = {
                    "username": username,
                    "password": password
                }

                response = session.post(login_url, headers=headers, data=login_data)

                if response.status_code == 200:
                    print(f"{GREEN}LOGIN SUCCESS on {site}{RESET}")

                    media_data = {"mediaUrl": video_url}
                    find_media_url = f"https://{site}/tools/send-comment?formType=findMediaID"

                    media_response = session.post(find_media_url, headers=headers, data=media_data)

                    if media_response.status_code == 200:
                        soup = BeautifulSoup(media_response.text, 'html.parser')
                        media_id_input = soup.find("input", {"name": "mediaID"})

                        if media_id_input:
                            media_id = media_id_input["value"]
                            print(f"Media ID extracted: {media_id}")

                            send_comment_url = f"https://{site}/tools/send-comment/{media_id}?formType=send"
                            send_comment_data = {
                                "yorum[]": comment_message,
                                "mediaID": media_id
                            }

                            send_response = session.post(send_comment_url, headers=headers, data=send_comment_data)

                            if send_response.status_code == 200:
                                print(f"{GREEN}COMMENT SUCCESS{RESET}")
                            else:
                                print(f"{RED}ERROR IN COMMENTING{RESET}")

                        else:
                            print(f"{RED}MEDIA ID NOT FOUND!{RESET}")
                    else:
                        print(f"{RED}ERROR IN FINDING MEDIA ID!{RESET}")
                else:
                    print(f"{RED}LOGIN ERROR!{RESET}")
            except Exception as e:
                print(f"{RED}Error!{e}{RESET}")

            print("Waiting 60 seconds ...")
            time.sleep(60)

        print(f"{RED}COMPLET COMMENT SENT{RESET}")

    elif choice == "5":
        print(f"{RED}Exiting...{RESET}")
        exit()

if __name__ == "__main__":
    main()
