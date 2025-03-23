
import requests , random
import threading
import sys
from concurrent.futures import ThreadPoolExecutor
from faker import Faker
import random
import requests
from uuid import uuid4
import random
from faker import Faker

ff = Faker()


class TikTok:
	@staticmethod
	def info(user):
		import requests , datetime
		patre = {
        "Host": "www.tiktok.com",
        "sec-ch-ua": "\" Not A;Brand\";v\u003d\"99\", \"Chromium\";v\u003d\"99\", \"Google Chrome\";v\u003d\"99\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Linux; Android 8.0.0; Plume L2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q\u003d0.9,image/avif,image/webp,image/apng,*/*;q\u003d0.8,application/signed-exchange;v\u003db3;q\u003d0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-language": "en-US,en;q\u003d0.9,ar-DZ;q\u003d0.8,ar;q\u003d0.7,fr;q\u003d0.6,hu;q\u003d0.5,zh-CN;q\u003d0.4,zh;q\u003d0.3"
    }
		tikinfo = requests.get(f'https://www.tiktok.com/@{user}', headers=patre).text
		try:
			getting = str(tikinfo.split('webapp.user-detail"')[1]).split('"RecommendUserList"')[0]
			id = str(getting.split('id":"')[1]).split('",')[0]
			name = str(getting.split('nickname":"')[1]).split('",')[0]
			bio = str(getting.split('signature":"')[1]).split('",')[0]
			country = str(getting.split('region":"')[1]).split('",')[0]
			private = str(getting.split('privateAccount":')[1]).split(',"')[0]
			followers = str(getting.split('followerCount":')[1]).split(',"')[0]
			following = str(getting.split('followingCount":')[1]).split(',"')[0]
			like = str(getting.split('heart":')[1]).split(',"')[0]
			video = str(getting.split('videoCount":')[1]).split(',"')[0]
			B = bin(int(id))[2:]
			L, BS = 0, ""
			while L < 31:
				BS += B[L]
				L += 1
			Date = datetime.datetime.fromtimestamp(int(BS, 2)).strftime('%Y / %m / %d')
			return {
				'Programmer': 'tig3r_coder',
				'id': id,
				'name': name,
				'username': user,
				'followers': followers,
				'following': following,
				'likes': like,
				'videos': video,
				'Bio': bio,
				'country': country,
				'date': Date,
				'private': private		
				}
		except Exception as e:
			return {
				'Programmer': 'tiger_cod3r',
				'info': 'Error',
				'username': user,
				}
class Instagram:
	@staticmethod
	def info(username):
		import requests
		try:
			url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
			headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "X-IG-App-ID": "936619743392459",
                        "Accept": "*/*",
                        "Accept-Language": "en-US,en;q=0.9",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Connection": "keep-alive"
                    }
			response = requests.get(url, headers=headers)
			if response.status_code != 200:
				pass
			data = response.json()
			user = data['data']['user']
			Id=user['id']
			name=user["full_name"]
			fol=user["edge_followed_by"]["count"]
			folg=user["edge_follow"]["count"]
			post=user["edge_owner_to_timeline_media"]["count"]
			bio=user["biography"]
			private=user["is_private"]
			url=user["profile_pic_url"]
			try:		        
			        if int(Id) >1 and int(Id)<1279000:
			            date =  "2010"
			        elif int(Id)>1279001 and int(Id)<17750000:
			            date =  "2011"
			        elif int(Id) > 17750001 and int(Id)<279760000:
			            date =  "2012"
			        elif int(Id)>279760001 and int(Id)<900990000:
			            date =  "2013"
			        elif int(Id)>900990001 and int(Id)< 1629010000:
			            date =  "2014"
			        elif int(Id)>1900000000 and int(Id)<2500000000:
			            date =  "2015"
			        elif int(Id)>2500000000 and int(Id)<3713668786:
			            date =  "2016"
			        elif int(Id)>3713668786 and int(Id)<5699785217:
			            date =  "2017"
			        elif int(Id)>5699785217 and int(Id)<8507940634:
			            date =  "2018"
			        elif int(Id)>8507940634 and int(Id)<21254029834:
			            date =  "2019"	         
			        else:
			            date = "2020-2023"
			except:
				date = None
			return {
			'Programmer': 'tiger_cod3r',
			'name': name,
			'username': username,
			'followers': fol,
			'following': folg,
			'post': post,
			'id': Id,
			'date': date,
			'bio': bio,
			'url': url						
				}		 
		except requests.exceptions.RequestException as e:
			return {
			'Programmer': 'tiger_cod3r',
			'username': username,
			'info': 'Error'			
				}
	@staticmethod
	def CheckEmail(email):
		import requests , user_agent
		import random
		import requests
		import threading
		import sys
		from concurrent.futures import ThreadPoolExecutor
		from faker import Faker
		import random
		fake = Faker()
		tiger_77 = [
			"OnePlus", "Samsung", "Google Pixel", "iPhone", "Huawei", "Xiaomi", "LG", "Nokia", "Sony", "Motorola",
			"Asus", "Realme", "Oppo", "Vivo", "HTC", "Lenovo", "Meizu", "ZTE", "Honor", "Microsoft", "Google Nexus",
			"Sharp", "Acer", "Blackberry", "Essential", "Alcatel", "TCL", "Ptigeronic", "Micromax", "Karbonn", "Lava",
			"Infinix", "Tecno", "Coolpad", "Gionee", "Cherry Mobile", "ZTE", "LeEco", "iQOO", "Doogee", "Blu",
			"Realme", "POCO", "Lenovo Legion", "Xiaomi Mi", "Infinix Zero", "OnePlus Nord", "Vivo iQOO", "Meizu Pro",
			"Redmi Note", "Samsung Galaxy Z", "Oppo F9", "Vivo V15", "Moto E", "Vivo X50", "Samsung Galaxy M",
			"iPhone 11", "iPhone SE", "iPhone 7", "iPhone XR", "iPhone 8", "iPhone 12", "Oppo Reno", "Samsung J7",
			"Google Nexus 6", "Samsung S10", "Huawei P20", "Huawei P30", "Sony Xperia XZ", "Google Pixel 4",
			"Motorola Moto Z", "Samsung Galaxy Fold", "Honor 20", "Samsung Note 9", "Google Pixel 5", "Asus Zenfone",
			"Honor 9X", "Oppo Find X", "Xiaomi Poco F1", "Sony Xperia 1", "Motorola Moto G", "OnePlus 7T", "Redmi K30",
			"Nokia 7.1", "Vivo Y91", "Nokia 8", "Oppo A9", "Samsung Galaxy A52", "Realme 6", "Lenovo Z6 Pro",
			"Blackberry Priv", "Xiaomi Mi 10", "Motorola Edge", "Huawei Mate 30", "Nokia 6", "Xiaomi Mi A3", "Oppo F11",
			"Oppo R17", "Redmi 9", "Samsung Galaxy M31", "Vivo V17", "Vivo V19", "Realme 7", "Infinix S5 Pro",
			"Vivo X21", "Motorola Moto G8", "Oppo Reno 2", "Xiaomi Redmi 8", "Lenovo Legion", "ZTE Blade", "Oppo A5",
			"Realme 5 Pro", "Honor View 20", "Nokia 5.1", "Xiaomi Mi 9 SE", "Oppo A3S", "Google Pixel 2", "LG V30+",
			"Xiaomi Redmi Note 8", "Huawei Nova 5T", "Oppo A7", "Asus Zenfone Max", "Vivo V3", "Realme X2", "Meizu MX6",
			"Xiaomi Mi Mix", "Realme XT", "Oppo K1", "Google Pixel XL", "Honor 10", "Sony Xperia Z3", "LG G5",
			"Samsung Galaxy S9", "Motorola Moto X4", "Nokia 6.2", "OnePlus 6", "Vivo Y93", "Huawei P9", "Oppo A9 2020",
			"iPhone 6S", "Xiaomi Mi 11", "Huawei Mate 20", "Oppo F1", "Sony Xperia XZ1", "Samsung S8", "Vivo X21",
			"Xiaomi Mi Max", "OnePlus 5T", "Motorola Moto Z2", "Vivo Y11", "Honor 8X", "Nokia 3.2", "Oppo F5", "iPhone 6",
			"Asus Zenfone 4", "Huawei P10", "Samsung Galaxy S7", "Motorola Moto E4", "Vivo X60", "Oppo A31", "Meizu Pro 7",
			"Nokia 2.3", "Sony Xperia Z5", "Redmi Note 7", "Xiaomi Mi Mix 3", "Google Nexus 5X", "Samsung Galaxy A51",
			"Oppo R9", "Huawei Mate 10", "OnePlus 8", "Infinix Zero 7", "Realme 3 Pro", "Xiaomi Mi 5X", "Sony Xperia XA1",
			"Lenovo P2", "Huawei Mate 9", "Oppo A1K", "Vivo Y15", "Xiaomi Mi Pad", "Honor 8", "LG G6", "Sony Xperia Z2"
		]

		tiger_os = [
			"28/9", "30/11", "22/10", "25/7", "23/9", "31/12", "20/8", "21/6", "24/10", "29/9", "17/5", "26/1",
			"18/12", "32/3", "33/5", "19/11", "35/4", "36/8", "27/10", "34/2", "30/8", "21/9", "20/11", "29/8",
			"22/5", "26/3", "23/4", "21/7", "20/10", "25/9", "19/6", "23/12", "28/10", "22/4", "24/8", "20/1",
			"31/5", "25/6", "27/3", "30/6", "19/10", "22/9", "23/7", "24/6", "21/5", "22/8", "28/7", "24/5",
			"20/4", "29/5", "30/3", "21/4", "27/6", "25/5", "19/7", "28/12", "24/7", "22/11", "31/8", "26/7",
			"23/3", "27/9", "31/10", "20/2", "28/6", "29/3", "30/9", "21/3", "25/8", "20/5", "23/1", "26/2"
		]

		resolutions = [
			"1080x2147", "1440x2960", "750x1334", "1920x1080", "1280x720", "1080x1920", "2560x1440", "1440x2560",
			"720x1280", "3840x2160", "1366x768", "2160x1440", "1024x768", "1360x768", "800x480", "1280x800", "1600x900",
			"1440x900", "1680x1050", "2560x1600", "1920x1200", "1280x1024", "1600x1200", "1280x768", "1600x1280",
			"1440x1280", "1920x1600", "1600x1600", "1440x1600", "1280x1024", "1280x768", "1280x720", "1024x800",
			"1360x1024", "960x640", "1600x2560", "1920x1080", "960x854", "1280x768", "1920x800", "1600x1024",
			"2560x1600", "1280x600", "1680x1050", "1536x864", "1280x1024", "1920x1440", "1440x2560", "2160x1080",
			"1440x720", "1280x960", "1366x1024", "1680x900", "1280x1152", "1600x900", "1280x854", "1920x1200",
			"1440x960", "1024x576", "2048x1152", "1440x1024", "2048x1536", "1920x1280", "1600x1200", "1920x2560"
		]

		devices = [
			"OnePlus6T", "SM-G950F", "Pixel 3", "iPhone X", "Huawei P30", "Moto G7", "Galaxy S20", "iPhone 12", "iPhone 11",
			"Galaxy Note 10", "Xiaomi Mi 9", "iPhone 7", "Google Pixel 5", "Samsung A71", "iPhone 12 Pro", "Sony Xperia 1",
			"Huawei P40", "Nokia 6.1", "OnePlus 7 Pro", "Samsung Galaxy J7", "Huawei Mate 20 Pro", "Xiaomi Redmi Note 9",
			"iPhone SE", "Oppo Reno 10x", "Vivo V15", "Samsung Galaxy Z", "Sony Xperia XZ", "Google Pixel 4",
			"Motorola Moto Z", "Samsung Galaxy Fold", "Honor 20", "Samsung Note 9", "Google Pixel 5", "Asus Zenfone",
			"Honor 9X", "Oppo Find X", "Xiaomi Poco F1", "Sony Xperia 1", "Motorola Moto G", "OnePlus 7T", "Redmi K30",
			"Nokia 7.1", "Vivo Y91", "Nokia 8", "Oppo A9", "Samsung Galaxy A52", "Realme 6", "Lenovo Z6 Pro",
			"Blackberry Priv", "Xiaomi Mi 10", "Motorola Edge", "Huawei Mate 30", "Nokia 6", "Xiaomi Mi A3", "Oppo F11",
			"Oppo R17", "Redmi 9", "Samsung Galaxy M31", "Vivo V17", "Vivo V19", "Realme 7", "Infinix S5 Pro",
			"Vivo X21", "Motorola Moto G8", "Oppo Reno 2", "Xiaomi Redmi 8", "Lenovo Legion", "ZTE Blade", "Oppo A5",
			"Realme 5 Pro", "Honor View 20", "Nokia 5.1", "Xiaomi Mi 9 SE", "Oppo A3S", "Google Pixel 2", "LG V30+",
			"Xiaomi Redmi Note 8", "Huawei Nova 5T", "Oppo A7", "Asus Zenfone Max", "Vivo V3", "Realme X2", "Meizu MX6",
			"Xiaomi Mi Mix", "Realme XT", "Oppo K1", "Google Pixel XL", "Honor 10", "Sony Xperia Z3", "LG G5",
			"Samsung Galaxy S9", "Motorola Moto X4", "Nokia 6.2", "OnePlus 6", "Vivo Y93", "Huawei P9", "Oppo A9 2020",
			"iPhone 6S", "Xiaomi Mi 11", "Huawei Mate 20", "Oppo F1", "Sony Xperia XZ1", "Samsung S8", "Vivo X21",
			"Xiaomi Mi Max", "OnePlus 5T", "Motorola Moto Z2", "Vivo Y11", "Honor 8X", "Nokia 3.2", "Oppo F5", "iPhone 6",
			"Asus Zenfone 4", "Huawei P10", "Samsung Galaxy S7", "Motorola Moto E4", "Vivo X60", "Oppo A31", "Meizu Pro 7",
			"Nokia 2.3", "Sony Xperia Z5", "Redmi Note 7", "Xiaomi Mi Mix 3", "Google Nexus 5X", "Samsung Galaxy A51",
			"Oppo R9", "Huawei Mate 10", "OnePlus 8", "Infinix Zero 7", "Realme 3 Pro", "Xiaomi Mi 5X", "Sony Xperia XA1",
			"Lenovo P2", "Huawei Mate 9", "Oppo A1K", "Vivo Y15", "Xiaomi Mi Pad", "Honor 8", "LG G6", "Sony Xperia Z2",
			"OnePlus 6", "Samsung Galaxy S6", "iPhone XS", "Xiaomi Mi A2", "Motorola Moto G5", "Sony Xperia XZ Premium",
			"Oppo F3", "Vivo V5 Plus", "Nokia 5", "Realme 2 Pro", "Huawei Honor 8", "Lenovo K8 Plus", "Samsung Galaxy Note 8",
			"Xiaomi Redmi 6", "Vivo Y81", "Infinix Hot 7", "Meizu M6", "Oppo F9 Pro", "Sony Xperia XA", "Nokia 9 PureView",
			"Google Pixel 3 XL", "Samsung Galaxy A7", "Huawei P8", "Xiaomi Redmi 6A", "Oppo F1s", "Nokia 3", "Vivo Y12",
			"Infinix Zero 6", "Asus Zenfone 2", "Lenovo Vibe K5 Plus", "Motorola Moto G3", "Vivo Y55", "Realme 2",
			"Huawei P8 Lite", "Google Nexus 5", "Xiaomi Mi A1", "Sony Xperia M5", "Oppo A37", "Samsung Galaxy J5", "Vivo V11", "OnePlus", "Samsung", "Google Pixel", "iPhone", "Huawei", "Xiaomi", "LG", "Nokia", "Sony", "Motorola",
			"Asus", "Realme", "Oppo", "Vivo", "HTC", "Lenovo", "Meizu", "ZTE", "Honor", "Microsoft", "Google Nexus",
			"Sharp", "Acer", "Blackberry", "Essential", "Alcatel", "TCL", "Ptigeronic", "Micromax", "Karbonn", "Lava",
			"Infinix", "Tecno", "Coolpad", "Gionee", "Cherry Mobile", "ZTE", "LeEco", "iQOO", "Doogee", "Blu",
			"Realme", "POCO", "Lenovo Legion", "Xiaomi Mi", "Infinix Zero", "OnePlus Nord", "Vivo iQOO", "Meizu Pro",
			"Redmi Note", "Samsung Galaxy Z", "Oppo F9", "Vivo V15", "Moto E", "Vivo X50", "Samsung Galaxy M",
			"iPhone 11", "iPhone SE", "iPhone 7", "iPhone XR", "iPhone 8", "iPhone 12", "Oppo Reno", "Samsung J7",
			"Google Nexus 6", "Samsung S10", "Huawei P20", "Huawei P30", "Sony Xperia XZ", "Google Pixel 4",
			"Motorola Moto Z", "Samsung Galaxy Fold", "Honor 20", "Samsung Note 9", "Google Pixel 5", "Asus Zenfone",
			"Honor 9X", "Oppo Find X", "Xiaomi Poco F1", "Sony Xperia 1", "Motorola Moto G", "OnePlus 7T", "Redmi K30",
			"Nokia 7.1", "Vivo Y91", "Nokia 8", "Oppo A9", "Samsung Galaxy A52", "Realme 6", "Lenovo Z6 Pro",
			"Blackberry Priv", "Xiaomi Mi 10", "Motorola Edge", "Huawei Mate 30", "Nokia 6", "Xiaomi Mi A3", "Oppo F11",
			"Oppo R17", "Redmi 9", "Samsung Galaxy M31", "Vivo V17", "Vivo V19", "Realme 7", "Infinix S5 Pro",
			"Vivo X21", "Motorola Moto G8", "Oppo Reno 2", "Xiaomi Redmi 8", "Lenovo Legion", "ZTE Blade", "Oppo A5",
			"Realme 5 Pro", "Honor View 20", "Nokia 5.1", "Xiaomi Mi 9 SE", "Oppo A3S", "Google Pixel 2", "LG V30+",
			"Xiaomi Redmi Note 8", "Huawei Nova 5T", "Oppo A7", "Asus Zenfone Max", "Vivo V3", "Realme X2", "Meizu MX6",
			"Xiaomi Mi Mix", "Realme XT", "Oppo K1", "Google Pixel XL", "Honor 10", "Sony Xperia Z3", "LG G5",
			"Samsung Galaxy S9", "Motorola Moto X4", "Nokia 6.2", "OnePlus 6", "Vivo Y93", "Huawei P9", "Oppo A9 2020",
			"iPhone 6S", "Xiaomi Mi 11", "Huawei Mate 20", "Oppo F1", "Sony Xperia XZ1", "Samsung S8", "Vivo X21",
			"Xiaomi Mi Max", "OnePlus 5T", "Motorola Moto Z2", "Vivo Y11", "Honor 8X", "Nokia 3.2", "Oppo F5", "iPhone 6",
			"Asus Zenfone 4", "Huawei P10", "Samsung Galaxy S7", "Motorola Moto E4", "Vivo X60", "Oppo A31", "Meizu Pro 7",
			"Nokia 2.3", "Sony Xperia Z5", "Redmi Note 7", "Xiaomi Mi Mix 3", "Google Nexus 5X", "Samsung Galaxy A51",
			"Oppo R9", "Huawei Mate 10", "OnePlus 8", "Infinix Zero 7", "Realme 3 Pro", "Xiaomi Mi 5X", "Sony Xperia XA1",
			"Lenovo P2", "Huawei Mate 9", "Oppo A1K", "Vivo Y15", "Xiaomi Mi Pad", "Honor 8", "LG G6", "Sony Xperia Z2"
		]
		def tiger_usrg():
			device = random.choice(devices)
			os_version = random.choice(tiger_os)
			resolution = random.choice(resolutions)
			user_agent = f"Instagram 85.0.0.21.100 Android ({os_version}; 380dpi; {resolution}; {device}; HWEVA; {device}; qcom; en_US; 146536611)"
			return user_agent
		
		url = "https://i.instagram.com/api/v1/accounts/send_recovery_flow_email/"
		
		headers = {
			"Host": "i.instagram.com",
			"user-agent": tiger_usrg(),
			"content-type": "application/x-www-form-urlencoded",
			"accept-encoding": "gzip"
		}

		payload = {
			"email": email
		}
		try:
			response = requests.post(url, headers=headers, data=payload)
			if "sent an" in response.text.lower():
				return {'Programmer : tiger_cod3r \nEmail : email \nAvailable : Yes✅'}
			elif '"spam"' in response.text.lower():
				return {'Programmer': 'tig3r_coder','IP': 'Block'}		     
			else:
				return {'Programmer : tiger_cod3r \nEmail : email \nAvailable : No❌'}	    
		except Exception as e:
			return e




import requests,random
abc = 'azertyuiopmlkjhgfdsqwxcvbn'

class Gmail:
	@staticmethod
	def CheckGmail(email):
		if '@' in email:email=email.split('@')[0]
		s = requests.Session()
		while True:
			try:
				headers = {
					'accept': '*/*',
					'accept-language': 'en',
					'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
					'dnt': '1',
					'origin': 'https://accounts.google.com',
					'referer': 'https://accounts.google.com/',
					'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
					'x-goog-ext-278367001-jspb': '["GlifWebSignIn"]',
					'x-same-domain': '1',
				}
				params = {
				'biz': 'false',
				'continue': 'https://mail.google.com/mail/u/0/',
				'ddm': '1',
				'emr': '1',
				'flowEntry': 'SignUp',
				'flowName': 'GlifWebSignIn',
				'followup': 'https://mail.google.com/mail/u/0/',
				'osid': '1',
				'service': 'mail',
			}
				response = s.get('https://accounts.google.com/lifecycle/flows/signup', params=params, headers=headers)
				TL = response.url.split('TL=')[1]
				at = str(response.text).split('"SNlM0e":"')[1].split('"')[0].replace(':','%3A')
				s1 = str(response.text).split('"Qzxixc":"')[1].split('"')[0]
				headers.update({'x-goog-ext-391502476-jspb':'["{}"]'.format(s1)})
				break
			except:''
		while True:
			try:

				name = ''.join(random.choice(abc) for i in range(random.randrange(5,10)))
				params = {
					'rpcids': 'E815hb',
					'source-path': '/lifecycle/steps/signup/name',
					'hl': 'en-US',
					'TL': TL,
					'rt': 'c',
				}

				data = 'f.req=%5B%5B%5B%22E815hb%22%2C%22%5B%5C%22{}%5C%22%2C%5C%22%5C%22%2Cnull%2Cnull%2Cnull%2C%5B%5D%2Cnull%2C1%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(name,at)

				response = s.post(
					'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
					params=params,
					headers=headers,
					data=data,
				)
				break
			except:''
		while True:
			try:
				params = {
					'rpcids': 'eOY7Bb',
					'source-path': '/lifecycle/steps/signup/birthdaygender',
					'hl': 'en-US',
					'TL': TL,
					'rt': 'c',
				}
				data = 'f.req=%5B%5B%5B%22eOY7Bb%22%2C%22%5B%5B{}%2C5%2C20%5D%2C1%2Cnull%2Cnull%2Cnull%2C%5C%22%3CpGhqaDACAAbe5ec5_uWNRGP8ADzN4FP0ADQBEArZ1Bi3KqRJ2jEufwzhM9DCOkC4py-Spwe8Dm8vIGEUYahQ0cFE1MsIiaW04C_7CxtFzQAAAladAAAAC6cBB7EATZbZc1lblBs3Pyjn18zoKs0dzS4aUpxAwryVbv8iPsaM1XfBJCrUEYx0hOeeUpwbG0Hh59jAFDOul1Q_nXL2xdN3okPfS1tlHQRMBJkUVg39qy9DpG6iLGbC4D3MlzWYexF_GQc5fwWVzu6zeexxryAR74fHHwp0x0VOHm6vsiReDmPuSJw-gea4iEzzhe0QA2CCW_YekjZ0Qu3W544ixt8rdoYcsk8Jx21EFQ2k8f_vdzbtHtdhYJl2In3oIPKXLAuFtsQmkrO0x0myDa_sbuNf8EPswGx_xGrBNciJwrVAVt8jmaK1kncj4VeueZn8pvlElhCpvVkyxFaJdlklKjKbvq4AGdu65_wFWX-nSbvq_EujfCGd1jF2uVxfx9GxGCkETqWFX2TItzMYOygG39N3e0u9zxG2rR9WxO1EKw-wOv_T_Nyc9UuV4oeTCC9s66OE7HyvcZn17B58qzplRRM6xOPKqaAL6blvAlAmsDvujYBUGZmXO4558-0rCrIF6_tyceib3scY62d_lGyGe-qLvMwRJ0a3JOo_r9S2vq15Pt6VATO-nzhs2mpk-K7_A6r9PC9KMxgktD_q7y9lhF_Hd1Hb92Rz2OgzCwuat9LnEIA6rNkoJ5Ev52PFtblk-NNHz3RmX_wLZ86pYeUgMfVTTlOBEQBodV97FHO_QV-4BtwPST0xe9P3zkAEiuFYf4KFwjj131Icb_a8sX_Rd9_ebfpRfvb76EWJyTfnW7WCTzyph22-lFrMnPcGK92FOUod62lZFoEy84QzevvX311QwdDuJWdqPwmvBEHMYpfW5yKlrxOr4f8i2DimNkRq2MiDbsW2ZnnnXhKzBAQgYghjSaAJ3ofdFhfE5yBWynv3IVxW_rEgpE7CYAPopkWqZUVsBtH0FA8o08ZSvmlt0p-thgwYQgJHmiWtTyMek5c_cSdoN5cqLk-JxOL2XBE68aPGC1JKyFCACcDCNnJR3DzncD1ZS4lchyFPsKyyalMzWp53CNH2aeoKLAdHyVz8TgpM56GcO1PpWKYzu0882T-AWvCaZEKqi9Qyb8fvCLFaxlzMGVEvCn2dU2q5LBNxJ0VsjljtR_aqLSEQ4tx5EITA5cyYA1-S_rQtDuCvCGC1-fDf8bsAckU7RNMh5pKZlXvzhlnHTnex6r6CaI7EnqUkw-NcuZpqq65s2o_4CnS23t5EAY7hTcBseN9h1eFkse2KnNDou38FjETsJpb6Fy1mLu-yzQ0tD152f39v9RVEUP4oMFLJO76O899vkgxxL3rQLk8EGXQDqaFjN5busj4VOhI6NIjqf1i9K0gKaBoHGSHG3gBqkXYXygJeiy_f8J2-VeG44bwNZl_m5P6L-Ce8c91zzZswM1MhPZqnz8_JUW-2LcBw5fNFDnQQ-fynszm4WY8F3PXxhdEoaun9xLOtqIeR8GPXPadPdE13RsBQdSibk6pw7ixPqieKkUbFD5wIKTD_UZf8tO0vc2QWH_5gHSSX-WjIoOEXHYWgUQt99fCXNTx1P8XL27N4CDgYR82-9QENXeP7qPAYBfcnWrtkvlRC8aRyxoMA_xS8BpYtsb5nKu1H6n4Mk4wgf0MZLIgC5E__IJy4ojRBCbBwams04rUlXWyB2llJ0Lo4SunQffsLiQqGxhMzhkwStuPgv7BHXY-kDPLyZXx-cewDw9ZjhvtJPpK6nW873_WkIO542o7kF_oNZRlE3pyLbdOabPG11KCjMIZgBEVpdzPssPPu6TXvh6F6_klPozrjf35DsktV7c-c3a2OVPKoYJtcQnwCA4UnHqR_i1-N1wxlooGJ6GUBI7H8wZmj_B2jjvqFWOfdLB8_bDmEysG_brczvsnyl-mGwipdMHPRZ70HpyGOign0Rg8JAQrVOnKH_oXkFjPmzGM3vXNOJ2tndrE9Z2isXvs_RPGpgUDiNbNYyJjLCmHJWz4mvyo5DrtANi-5qifEMEdrM9kxWKolh6meQd8Vx8Z61zQR5oQSu_V6lafpELV_fK7tZSHfRwlBAxx26rZaTXDI1yxSPk9Pmt_lfPiecmlRa43bCZQVPmj3rf0nQJf3_I8rUmFv4IemINkUEZBtVVBHIjJusuRI49-zoQMp1UsmbMiL17F1_sTwibBEvk2LjbF9Jo7HbGTqtLzZ0oLButszorJ4Hp0fq9GL4tJoMT2wbACAycYSvl-9LGX8JtYoMOkKnqLg3oRCRbeitDMAaQCSuGxSUCjTxkfAD_UCs3pBPvC3jYk5sK-SuKKIO48qJ_p8AYQkFutKtclzf2-P-SQozeuQYLpf5Ch2WtFpmm40DQ58SZ8OTxzMubG_q5K1t2ZsknjqnOMfzegagfp2_Lbm2ReTba9jJdH2EZ1zSoDyMV73O1NeSG8MCfBqqtjvevUtXq1T21l-f2Pcj_KYZ09uk50rTdkbDKXJ65Rr8EaLUVYveJ6Mcc7n740N7x-v8P3VUUYjNHDlbJbrWZ7J7PvfreGCZw7_jZDHd2_Fw5NvuJH7UXnrqEVzT3xvT8Wavpj1OCTyA0ItJPrSFo3JsvBWNsKaP0F34uSxlwpteTqzORTNjxN4QaGWFpzapvX3IYCkADk8iv3Oqm3OYtwtBW6Wm8ezJoySogZME2BHlcOLIajHAPR0isdLwXXSD9dzPO_zsfKB8Q7zM9DN-xwM9mQsQrsRCTq_cUjWxiqfonxFDIZx-UT5ez-U1az-JcfIwhlCtgiRt3s88omlG7znGNZSzu9V6P3szV5oT4ydTH1wQILd50eteZxhj4z7n0QbN5NUBd9nxK5NVYMs96NuwS7ZTOJB-fd_kr85giz0Om6_CY7CGhRwAM14oPpwNeyFQWsKpXOWR3huLTGQX3iFaspc_-F-UcYbA01_gafjo9sQqjn5oYrRVRIMu1pSzlYhfFWny0RoDWIEA-2eC3xjxrYWQASloqsyDUBetIuECA3Cr5BfQj-vcBa8GmQqjUGRJ1UxreLUrtoE9K7-BUkTSqfC6_ItIp8w7SXKnD4HImqa3NMvy6tqzHhNcrdhyAsNqnQG-by00SLuBMz2eHe49gTNyBiDrIjDzUYjieEn7X8DW8Z-QKdkJ3up_h5Q4XO9MkQ0pSi-YLVpkq7BBg_tUpwzOsQyhmVqm6gIZ6zDWIsc9iEkXzROe-aHxVwPsVSOUFXuDgCHQC7PqXl_ZkfA6XoOANg6mnqDJwKmE48pDHHq11tln2yGy0sDoN7et3FGFUV5nKEhUvkDq-FX-h1vBUKFpb5wdpiENT5Bz77GyiKHK8TwvFHZTUl6jgjIhYPYscylYG1U-_38hDBDxcNeCToG1ytkEqJMBLvBj0Q0iVeehPzzxFEYYZDhupE2wjgdp_RfOhqp30fRWBNSRk-XuAb-Ruasj7q6GHSm5ih2ukiloyRWBbr9QtTuOL_6LCvP_2-0yo18mMM1Az3jsmgDZHJGYPnE8LArBa2icMHRWdI1I5W_g45CaPogPMNMbRQZCvsGJJb6vwHa_4V69uB-FIjZxEoJwS8n10nRyAzxhedAp0udy3hYy43vNGg5CYgwNq8hFBqirHq3gRnh_fwzuAl56QHlvSD9clH6mgZbGLyz3-RlbLDRUGE7ev8GR-OQ0gxA2pBhRIQOl_DuHvWS_fshRRtTGXRkxZCv2X3lz6y7hMtztBPQ06LdIb0WaIkQgjJvwEthghzRWLUlkNd5wiC6tpRHQ9yWcnyQMgX13KFDWVa8sGoVyil_Wyxn1jfqbuCnuJdkdQhg72zZ5uFxtw8eH1Mgf8ab-n6LMLUbNCsbS7cz26IV-qmsIJA-m4b9AVZMPTgprpJwWUY3JYPqesT1zeoi4ZnDCYFCXlANT4NYI3a9hX--e7SsHcYGsddaq6HrP894ffqXbfyJ5J3n5fX8UHMu4aMe9Qa43Sw8eNfXPgewGtz34AIesPXDBPcVnS3-xdoK3K6gxqu8xc-hHt6Fo8Swb7cgV7HwQ9V2qpWc3P9XsGwGjVBpM6K-x30vqW9Kw89tLPAWEOlctJ8YGMFG_fujAVNN61GpvjfTcOzIaIIxLQjMkF89TQd3XE4ncgabEhbzjIS5SUVqSi3aG5wGdQ-vB_PYGDS3xonKccgoLg_UPeDnKuFHhoPDWq9P6IJQVagPLfuzzI76f8Rj3dJH3LnDlIVPcNwlHpX-YmYCniKytU5dQnX0AWLlQy_1z77IHhWU63yrQyoMU9iky4FUaeeJsLgx3XpVpR9PjhAGCFqUrr0ykCTpgADyyrNLs62wxVw-3bA0QsBca6LfD6eKCsWUHKRuhIKzy5I9S5XQ66WhHfNcPB7XbtdsQOBMBlB0v8gM5EKjNAic56B5Jb39ILbd_WT7xywRe9If-rXg9fHnGTApfNJKKMFsRr18Twkp11HFqV5M3Eg4oClga9aVvnwd751J4hLAWdo9bep0GS8pyX_SLQOM0dqpg6kANBYlpEczBWa_gCVdfpVOvOsp5GyoQHiHZVcu8p4fmXUd60LkmjyO4fMhqHtjnQjKXJorpNcCQK8w-RjcBw8Z7liV4zZts52-J5jfrXrDd2236i6OhNDlMqb6evHStjjJcc7jKqxnQ17A1wklO68gB8st3OuFPPiJXlnczSKJOyji0BVGPQUKztyJSlz-hcKWUgHLDoyYm34SrhDurlt-pcKA5MyHHRIH5nC6wFm6orlLD5OwoKyXfB48ylnPm2gDmDvdtctEDpXy3Qa-ZILfv7rCQkTFvef2qbdvxFwpGMoP_AyX5Ah8muwu8TYVlf63HWqIzev6tM1fOUAmadvdcjqhp5GTMbm5ewqWBzQNdjU5GjQLBkvQv2yRxFmkyvwr77rvCbgcaP6FLNFG1kI8RKh1E6HoCZnsCB7MVQptShtbtuSljBcxZ50%5C%22%2C%5Bnull%2Cnull%2C%5C%22https%3A%2F%2Fmail.google.com%2Fmail%2Fu%2F0%2F%5C%22%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5C%22mail%5C%22%5D%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(random.randrange(1990,2007),at)

				response = s.post(
					'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
					params=params,
					headers=headers,
					data=data,
				)
				break
			except:''
		while True:
			try:

				params = {
					'rpcids': 'NHJMOd',
					'source-path': '/lifecycle/steps/signup/username',
					'hl': 'en-US',
					'TL': TL,
					'rt': 'c',
				}

				data = 'f.req=%5B%5B%5B%22NHJMOd%22%2C%22%5B%5C%22{}%5C%22%2C1%2C0%2Cnull%2C%5Bnull%2Cnull%2Cnull%2Cnull%2C0%2C236841%5D%2C0%2C40%5D%22%2Cnull%2C%22generic%22%5D%5D%5D&at={}&'.format(email,at)

				response = s.post(
					'https://accounts.google.com/lifecycle/_/AccountLifecyclePlatformSignupUi/data/batchexecute',
					params=params,
					headers=headers,
					data=data,
				).text

				if 'password' in response:
					return {'Programmer : tiger_cod3r \nEmail : email \nAvailable : Yes✅'}
				else:
					return {'Programmer : tiger_cod3r \nEmail : email \nAvailable : No❌'}
			except Exception as e:
				return e

class Hotmail:
	@staticmethod
	def CheckEmail(email):
	    import requests , random , re
	    version = random.choice(["13.1.2", "13.1.1", "13.0.5", "12.1.2", "12.0.3"])
	    platform = random.choice(["Macintosh; Intel Mac OS X 10_15_7","Macintosh; Intel Mac OS X 10_14_6","iPhone; CPU iPhone OS 14_0 like Mac OS X","iPhone; CPU iPhone OS 13_6 like Mac OS X"])
	    user_agent = f"Mozilla/5.0 ({platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15 Edg/122.0.0.0"
	    response = requests.post('https://signup.live.com',headers={'user-agent': user_agent})
	    try:
	        amsc = response.cookies.get_dict()['amsc']
	        match = re.search(r'"apiCanary":"(.*?)"', response.text)      
	        if match:
	            api_canary= match.group(1)
	            canary = api_canary.encode().decode('unicode_escape')
	            response = requests.post(
      'https://signup.live.com/API/CheckAvailableSigninNames',cookies={'amsc':amsc},headers={'authority': 'signup.live.com','accept': 'application/json','accept-language': 'en-US,en;q=0.9','canary': canary,'user-agent': user_agent},json={'signInName': email})
	            if '"isAvailable":true' in response.text:
	            	return {'Programmer : tiger_cod3r \nEmail : email \nAvailable : Yes✅'}
	            else:
	            	return {'Programmer : tiger_cod3r \nEmail : email \nAvailable : No❌'}
	    except Exception as e:
	    	return e

#--------------------------------------#
class Agent:
    @staticmethod
    def user():
        aa = {
            "28/9": ["720dpi", "1080dpi", "1440dpi"],
            "29/10": ["720dpi", "1080dpi", "1440dpi", "2160dpi"],
            "30/11": ["1080dpi", "1440dpi", "2160dpi"],
            "31/12": ["1440dpi", "2160dpi"]
        }
        ss = {
            "720dpi": ["1280x720", "1920x1080"],
            "1080dpi": ["1920x1080", "2560x1440", "3840x2160"],
            "1440dpi": ["2560x1440", "3840x2160"],
            "2160dpi": ["3840x2160", "7680x4320"]
        }
        dd = {
            "samsung": ["SM-T292", "SM-G973F", "SM-A515F"],
            "google": ["Pixel 4", "Pixel 5"],
            "huawei": ["P30 Pro", "Mate 40 Pro"],
            "xiaomi": ["Mi 10", "Redmi Note 10"],
            "oneplus": ["8T", "9 Pro"],
            "sony": ["XZ2", "Xperia 1"]
        }
        cc = ["qcom", "exynos", "kirin", "mediatek", "apple"]
        lan = ["en_US", "es_ES", "fr_FR", "de_DE", "zh_CN", "ja_JP", "ko_KR"]
        dp = ["phone", "tablet", "watch", "tv", "car"]
        arm = ["arm64_v8a", "armeabi-v7a", "x86", "x86_64"]
        comb = ["samsung", "google", "huawei", "xiaomi", "oneplus", "sony"]

        sos = random.choice(list(aa.keys()))
        vlo = random.choice(aa[sos])
        lop = random.choice(ss[vlo])
        ki = random.choice(comb)
        mo = random.choice(dd.get(ki, ["Unknown"]))

        user_agent = (
            f"Instagram 368.0.0.45.96 Android "
            f"({sos}; {vlo}; {lop}; {ki}; {mo}; "
            f"{random.choice(arm)}; {random.choice(dp)}; "
            f"{random.choice(lan)}; {random.choice(cc)})"
        )

        return user_agent
        
        

    
    
    

class Agent2:
    @staticmethod
    def user():
        aa = {
            "28/9": ["720dpi", "1080dpi", "1440dpi"],
            "29/10": ["720dpi", "1080dpi", "1440dpi", "2160dpi"],
            "30/11": ["1080dpi", "1440dpi", "2160dpi"],
            "31/12": ["1440dpi", "2160dpi"]
        }
        ss = {
            "720dpi": ["1280x720", "1920x1080"],
            "1080dpi": ["1920x1080", "2560x1440", "3840x2160"],
            "1440dpi": ["2560x1440", "3840x2160"],
            "2160dpi": ["3840x2160", "7680x4320"]
        }
        dd = {
            "samsung": ["SM-T292", "SM-G973F", "SM-A515F"],
            "google": ["Pixel 4", "Pixel 5"],
            "huawei": ["P30 Pro", "Mate 40 Pro"],
            "xiaomi": ["Mi 10", "Redmi Note 10"],
            "oneplus": ["8T", "9 Pro"],
            "sony": ["XZ2", "Xperia 1"]
        }
        cc = ["qcom", "exynos", "kirin", "mediatek", "apple"]
        lan = ["en_US", "es_ES", "fr_FR", "de_DE", "zh_CN", "ja_JP", "ko_KR"]
        dp = ["phone", "tablet", "watch", "tv", "car"]
        arm = ["arm64_v8a", "armeabi-v7a", "x86", "x86_64"]
        comb = ["samsung", "google", "huawei", "xiaomi", "oneplus", "sony"]

        sos = random.choice(list(aa.keys()))
        vlo = random.choice(aa[sos])
        lop = random.choice(ss[vlo])
        ki = random.choice(comb)
        mo = random.choice(dd.get(ki, ["Unknown"]))

        user_agent = (
            f"Instagram 237.0.0.14.102 Android "
            f"({sos}; {vlo}; {lop}; {ki}; {mo}; "
            f"{random.choice(arm)}; {random.choice(dp)}; "
            f"{random.choice(lan)}; {random.choice(cc)})"
        )

        return user_agent

#---------------[MAIN_URL]-------------------#
url = "https://graph.facebook.com/graphql"
#---------------[MAIN_URL]-------------------#

class UserAgent:
    @staticmethod
    def generate():
        Br = {
            "Xiaomi": ["Mi 11 Lite", "Mi 10T", "Redmi Note 10", "Redmi 9", "POCO X3 Pro"],
            "Huawei": ["P30", "Mate 40 Pro", "Nova 9", "Y9 Prime", "P50 Pocket"],
            "Samsung": ["Galaxy S21", "Galaxy A72", "Galaxy Note 20", "Galaxy Z Fold 3", "Galaxy M32"],
            "Google": ["Pixel 6", "Pixel 5a", "Pixel 4 XL", "Pixel 3", "Pixel 7 Pro"],
            "Oppo": ["Reno 6", "Find X3", "A74", "F19 Pro", "K10"]
        }

        Mod = {
            "Mi 11 Lite": "2109119DG",
            "Mi 10T": "M2007J3SY",
            "Redmi Note 10": "M2101K7AG",
            "Redmi 9": "M2004J19AG",
            "POCO X3 Pro": "M2012J20SG",
            "P30": "ELE-L29",
            "Mate 40 Pro": "NOH-NX9",
            "Nova 9": "NAM-LX9",
            "Y9 Prime": "STK-L21",
            "P50 Pocket": "BAL-AL00",
            "Galaxy S21": "SM-G991B",
            "Galaxy A72": "SM-A725F",
            "Galaxy Note 20": "SM-N980F",
            "Galaxy Z Fold 3": "SM-F926B",
            "Galaxy M32": "SM-M325F",
            "Pixel 6": "GR1YH",
            "Pixel 5a": "G1F8F",
            "Pixel 4 XL": "G020J",
            "Pixel 3": "G013A",
            "Pixel 7 Pro": "GFE4J",
            "Reno 6": "CPH2235",
            "Find X3": "CPH2173",
            "A74": "CPH2219",
            "F19 Pro": "CPH2285",
            "K10": "CPH2373"
        }

        ComP = random.choice(list(Br.keys()))
        Dev = random.choice(Br[ComP])
        SerL = Mod.get(Dev, f"{random.randint(20000, 25000)}PN0CC")
        
        user_agent = (
            f"[FBAN/FB4A;FBAV/504.0.0.69.64;FBBV/{random.randint(700000000, 800000000)};"
            f"FBDM/{{density={random.uniform(2.0, 4.0):.2f},width={random.choice([1080, 1440, 2160])},"
            f"height={random.choice([1920, 2220, 2400])}}};FBLC/en_EN;FBRV/{random.randint(700000000, 800000000)};"
            f"FBCR/Unknown;FBMF/{ComP};FBBD/{Dev};FBPN/com.facebook.katana;FBDV/{SerL};"
            f"FBSV/{random.randint(9, 15)};FBOP/1;FBCA/{random.choice(['arm64-v8a', 'armeabi-v7a', 'x86', 'x86_64'])};]"
        )

        return user_agent
class Facebook:
	@staticmethod
	def CheckV2(email):
		try:
			payload = {
	'method': "post",
	'pretty': "false",
	'format': "json",
	'server_timestamps': "true",
	'locale': "en_EN",
	'purpose': "fetch",
	'fb_api_req_friendly_name': "FbBloksActionRootQuery-com.bloks.www.bloks.caa.reg.async.contactpoint_email.async",
	'fb_api_caller_class': "graphservice",
	'client_doc_id': "119940804216386667488826941930",
	'fb_api_client_context': "{\"is_background\":false}",
	'variables': "{\"params\":{\"params\":\"{\\\"params\\\":\\\"{\\\\\\\"client_input_params\\\\\\\":{\\\\\\\"accounts_list\\\\\\\":[],\\\\\\\"email_prefilled\\\\\\\":0,\\\\\\\"confirmed_cp_and_code\\\\\\\":{},\\\\\\\"family_device_id\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"fb_ig_device_id\\\\\\\":[],\\\\\\\"device_id\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"lois_settings\\\\\\\":{\\\\\\\"lois_token\\\\\\\":\\\\\\\"\\\\\\\"},\\\\\\\"msg_previous_cp\\\\\\\":\\\\\\\"\\\\\\\",\\\\\\\"is_from_device_emails\\\\\\\":1,\\\\\\\"switch_cp_first_time_loading\\\\\\\":1,\\\\\\\"email\\\\\\\":\\\\\\\""+email+"\\\\\\\",\\\\\\\"switch_cp_have_seen_suma\\\\\\\":0},\\\\\\\"server_params\\\\\\\":{\\\\\\\"event_request_id\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"is_from_logged_out\\\\\\\":0,\\\\\\\"text_input_id\\\\\\\":130583423800076,\\\\\\\"layered_homepage_experiment_group\\\\\\\":null,\\\\\\\"device_id\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"waterfall_id\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"INTERNAL__latency_qpl_instance_id\\\\\\\":1.30583423800112E14,\\\\\\\"flow_info\\\\\\\":\\\\\\\"{\\\\\\\\\\\\\\\"flow_name\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\"new_to_family_fb_default\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"flow_type\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\"ntf\\\\\\\\\\\\\\\"}\\\\\\\",\\\\\\\"is_platform_login\\\\\\\":0,\\\\\\\"INTERNAL__latency_qpl_marker_id\\\\\\\":36707139,\\\\\\\"reg_info\\\\\\\":\\\\\\\"{\\\\\\\\\\\\\\\"first_name\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\""+ff.first_name()+"\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"last_name\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\""+ff.last_name()+" \\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"full_name\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"contactpoint\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"ar_contactpoint\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"contactpoint_type\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"is_using_unified_cp\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"unified_cp_screen_variant\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"is_cp_auto_confirmed\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"is_cp_auto_confirmable\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"confirmation_code\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"birthday\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\"18-03-1999\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"did_use_age\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"gender\\\\\\\\\\\\\\\":2,\\\\\\\\\\\\\\\"use_custom_gender\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"custom_gender\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"encrypted_password\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"username\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"username_prefill\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"fb_conf_source\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"device_id\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\"34a69770-6dc3-4a9e-9942-45852bc49563\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"ig4a_qe_device_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"family_device_id\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\"0c607121-83ea-4f8f-a21d-58cda3df7b6e\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"nta_eligibility_reason\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"ig_nta_test_group\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"user_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"safetynet_token\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"safetynet_response\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"machine_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"profile_photo\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"profile_photo_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"profile_photo_upload_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"avatar\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"email_oauth_token_no_contact_perm\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"email_oauth_token\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"email_oauth_tokens\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"should_skip_two_step_conf\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"openid_tokens_for_testing\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"encrypted_msisdn\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"encrypted_msisdn_for_safetynet\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"cached_headers_safetynet_info\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"should_skip_headers_safetynet\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"headers_last_infra_flow_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"headers_last_infra_flow_id_safetynet\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"headers_flow_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"was_headers_prefill_available\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"sso_enabled\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"existing_accounts\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"used_ig_birthday\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"sync_info\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"create_new_to_app_account\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"skip_session_info\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"ck_error\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"ck_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"ck_nonce\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"should_save_password\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"horizon_synced_username\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"fb_access_token\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"horizon_synced_profile_pic\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"is_identity_synced\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"is_msplit_reg\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"user_id_of_msplit_creator\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"msplit_creator_nonce\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"dma_data_combination_consent_given\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"xapp_accounts\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"fb_device_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"fb_machine_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"ig_device_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"ig_machine_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"should_skip_nta_upsell\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"big_blue_token\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"skip_sync_step_nta\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"caa_reg_flow_source\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\"login_home_native_integration_point\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"ig_authorization_token\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"full_sheet_flow\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"crypted_user_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"is_caa_perf_enabled\\\\\\\\\\\\\\\":true,\\\\\\\\\\\\\\\"is_preform\\\\\\\\\\\\\\\":true,\\\\\\\\\\\\\\\"ignore_suma_check\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"ignore_existing_login\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"ignore_existing_login_from_suma\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"ignore_existing_login_after_errors\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"suggested_first_name\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"suggested_last_name\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"suggested_full_name\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"replace_id_sync_variant\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"is_redirect_from_nta_replace_id_sync_variant\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"frl_authorization_token\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"post_form_errors\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"skip_step_without_errors\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"existing_account_exact_match_checked\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"existing_account_fuzzy_match_checked\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"email_oauth_exists\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"confirmation_code_send_error\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"is_too_young\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"source_account_type\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"whatsapp_installed_on_client\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"confirmation_medium\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"source_credentials_type\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"source_cuid\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"source_account_reg_info\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"soap_creation_source\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"source_account_type_to_reg_info\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"registration_flow_id\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\""+str(uuid4())+"\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"should_skip_youth_tos\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"is_youth_regulation_flow_complete\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"is_on_cold_start\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"email_prefilled\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"cp_confirmed_by_auto_conf\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"auto_conf_info\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"in_sowa_experiment\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"youth_regulation_config\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"conf_allow_back_nav_after_change_cp\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"conf_bouncing_cliff_screen_type\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"conf_show_bouncing_cliff\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"eligible_to_flash_call_in_ig4a\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"flash_call_permissions_status\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"attestation_result\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"request_data_and_challenge_nonce_string\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"confirmed_cp_and_code\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"notification_callback_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"reg_suma_state\\\\\\\\\\\\\\\":0,\\\\\\\\\\\\\\\"is_msplit_neutral_choice\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"msg_previous_cp\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"ntp_import_source_info\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"youth_consent_decision_time\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"should_show_spi_before_conf\\\\\\\\\\\\\\\":true,\\\\\\\\\\\\\\\"google_oauth_account\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"is_reg_request_from_ig_suma\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"device_emails\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"is_toa_reg\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"is_threads_public\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"spc_import_flow\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"caa_play_integrity_attestation_result\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"flash_call_provider\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"spc_birthday_input\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"failed_birthday_year_count\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"user_presented_medium_source\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"user_opted_out_of_ntp\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"is_from_registration_reminder\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"show_youth_reg_in_ig_spc\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"fb_suma_combined_landing_candidate_variant\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\"control\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"fb_suma_is_high_confidence\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"screen_visited\\\\\\\\\\\\\\\":[\\\\\\\\\\\\\\\"CAA_REG_WELCOME_SCREEN\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"bloks.caa.reg.birthday\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"CAA_REG_CONTACT_POINT_PHONE\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"CAA_REG_CONTACT_POINT_EMAIL\\\\\\\\\\\\\\\"],\\\\\\\\\\\\\\\"fb_email_login_upsell_skip_suma_post_tos\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"fb_suma_is_from_email_login_upsell\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"fb_suma_login_upsell_skipped_warmup\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"fb_suma_login_upsell_show_list_cell_link\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"reg_shortening_test_variant\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\"control\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"reg_shortening_boundary_test_variant\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\"control\\\\\\\\\\\\\\\",\\\\\\\\\\\\\\\"should_prefill_cp_in_ar\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"ig_partially_created_account_user_id\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"ig_partially_created_account_nonce\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"ig_partially_created_account_nonce_expiry\\\\\\\\\\\\\\\":null,\\\\\\\\\\\\\\\"has_seen_suma_landing_page_pre_conf\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"has_seen_suma_candidate_page_pre_conf\\\\\\\\\\\\\\\":false,\\\\\\\\\\\\\\\"nta_login_footer_variant\\\\\\\\\\\\\\\":\\\\\\\\\\\\\\\"control\\\\\\\\\\\\\\\"}\\\\\\\",\\\\\\\"family_device_id\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"offline_experiment_group\\\\\\\":null,\\\\\\\"cp_funnel\\\\\\\":0,\\\\\\\"cp_source\\\\\\\":0,\\\\\\\"access_flow_version\\\\\\\":\\\\\\\"F2_FLOW\\\\\\\",\\\\\\\"is_from_logged_in_switcher\\\\\\\":0,\\\\\\\"current_step\\\\\\\":4}}\\\"}\",\"bloks_versioning_id\":\"24ee0ea0cc798aaa4d3e3c8a9055885112fb3d4213c4175bb6e9c76972ec34d1\",\"app_id\":\"com.bloks.www.bloks.caa.reg.async.contactpoint_email.async\"},\"scale\":\"3\",\"nt_context\":{\"using_white_navbar\":true,\"styles_id\":\"2def2bac2d4f2b16ef7cbebba00a42f6\",\"pixel_ratio\":3,\"is_push_on\":true,\"debug_tooling_metadata_token\":null,\"is_flipper_enabled\":false,\"theme_params\":[{\"value\":[\"BLUEPRINT_TEST_ROUNDED_CORNERS_NO_GUTTERS\",\"BLUEPRINT_TEST_GUTTER\"],\"design_system_name\":\"FDS\"}],\"bloks_version\":\"24ee0ea0cc798aaa4d3e3c8a9055885112fb3d4213c4175bb6e9c76972ec34d1\"}}",
	'fb_api_analytics_tags': "[\"GraphServices\"]",
	'client_trace_id': str(uuid4())
	}

			headers = {
	'User-Agent': UserAgent.generate(),
	'x-fb-friendly-name': "FbBloksActionRootQuery-com.bloks.www.bloks.caa.reg.async.contactpoint_email.async", 
	'authorization': "OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32",
	'x-fb-conn-uuid-client': str(uuid4()).replace("-","")
	}


			response = requests.post(url, data=payload, headers=headers).json()
			op = str(response).encode("utf-8").decode("unicode-escape", errors="ignore").replace("\\","").replace("/","")
			if "CAA_REG_EMAIL_LOGIN_UPSELL:has_showed_upsell" in op:
				return {'Programmer : tiger_cod3r \nEmail : email \nAvailable : Yes✅'}
			else:
				return {'Programmer : tiger_cod3r \nEmail : email \nAvailable : No❌'}

		except Exception as e:
			print(e)

	def CheckV1(email):
		try:
			payload = {
	'method': "post",
	'pretty': "false",
	'format': "json",
	'server_timestamps': "true",
	'locale': "en_EN",
	'purpose': "fetch",
	'fb_api_req_friendly_name': "FbBloksActionRootQuery-com.bloks.www.caa.ar.search.async",
	'fb_api_caller_class': "graphservice",
	'client_doc_id': "119940804216386667488826941930",
	'fb_api_client_context': "{\"is_background\":false}",
	'variables': "{\"params\":{\"params\":\"{\\\"params\\\":\\\"{\\\\\\\"client_input_params\\\\\\\":{\\\\\\\"text_input_id\\\\\\\":\\\\\\\"lh37sk:580\\\\\\\",\\\\\\\"flash_call_permissions_status\\\\\\\":{\\\\\\\"READ_PHONE_STATE\\\\\\\":\\\\\\\"DENIED\\\\\\\",\\\\\\\"READ_CALL_LOG\\\\\\\":\\\\\\\"DENIED\\\\\\\",\\\\\\\"ANSWER_PHONE_CALLS\\\\\\\":\\\\\\\"DENIED\\\\\\\"},\\\\\\\"was_headers_prefill_available\\\\\\\":0,\\\\\\\"sfdid\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"attestation_result\\\\\\\":{\\\\\\\"data\\\\\\\":\\\\\\\"\\\\\\\",\\\\\\\"signature\\\\\\\":\\\\\\\"MEUCIQCBSrzyU6wUrgZaV38L30a31rPMeiQcj2YCWvuL9zZZTwIgelOJPF+yzdSqoF0B8bsEZ04x1WMAE91\\\\/p13tLvAPqmc=\\\\\\\",\\\\\\\"keyHash\\\\\\\":\\\\\\\"e93b8ab100a56f1ea430311c3c4dfb11d07b1b89eb65514bf45b08e1be98bec5\\\\\\\"},\\\\\\\"fetched_email_token_list\\\\\\\":{},\\\\\\\"search_query\\\\\\\":\\\\\\\""+email+"\\\\\\\",\\\\\\\"android_build_type\\\\\\\":\\\\\\\"\\\\\\\",\\\\\\\"sim_state\\\\\\\":5,\\\\\\\"accounts_list\\\\\\\":[],\\\\\\\"is_oauth_without_permission\\\\\\\":0,\\\\\\\"ig_oauth_token\\\\\\\":[],\\\\\\\"search_screen_type\\\\\\\":\\\\\\\"email\\\\\\\",\\\\\\\"is_whatsapp_installed\\\\\\\":1,\\\\\\\"lois_settings\\\\\\\":{\\\\\\\"lois_token\\\\\\\":\\\\\\\"\\\\\\\"},\\\\\\\"was_headers_prefill_used\\\\\\\":0,\\\\\\\"headers_infra_flow_id\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"fetched_email_list\\\\\\\":[\\\\\\\"\\\\\\\"],\\\\\\\"sso_accounts_auth_data\\\\\\\":[],\\\\\\\"encrypted_msisdn\\\\\\\":\\\\\\\"\\\\\\\"},\\\\\\\"server_params\\\\\\\":{\\\\\\\"event_request_id\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"is_from_logged_out\\\\\\\":0,\\\\\\\"layered_homepage_experiment_group\\\\\\\":null,\\\\\\\"device_id\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"waterfall_id\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"INTERNAL__latency_qpl_instance_id\\\\\\\":1.29849323600707E14,\\\\\\\"is_platform_login\\\\\\\":0,\\\\\\\"context_data\\\\\\\":\\\\\\\"\\\\\\\",\\\\\\\"INTERNAL__latency_qpl_marker_id\\\\\\\":36707139,\\\\\\\"family_device_id\\\\\\\":\\\\\\\""+str(uuid4())+"\\\\\\\",\\\\\\\"offline_experiment_group\\\\\\\":null,\\\\\\\"access_flow_version\\\\\\\":\\\\\\\"F2_FLOW\\\\\\\",\\\\\\\"is_from_logged_in_switcher\\\\\\\":0}}\\\"}\",\"bloks_versioning_id\":\"24ee0ea0cc798aaa4d3e3c8a9055885112fb3d4213c4175bb6e9c76972ec34d1\",\"app_id\":\"com.bloks.www.caa.ar.search.async\"},\"scale\":\"3\",\"nt_context\":{\"using_white_navbar\":true,\"styles_id\":\"2def2bac2d4f2b16ef7cbebba00a42f6\",\"pixel_ratio\":3,\"is_push_on\":true,\"debug_tooling_metadata_token\":null,\"is_flipper_enabled\":false,\"theme_params\":[{\"value\":[\"BLUEPRINT_TEST_ROUNDED_CORNERS_NO_GUTTERS\",\"BLUEPRINT_TEST_GUTTER\"],\"design_system_name\":\"FDS\"}],\"bloks_version\":\"24ee0ea0cc798aaa4d3e3c8a9055885112fb3d4213c4175bb6e9c76972ec34d1\"}}",
	'fb_api_analytics_tags': "[\"GraphServices\"]",
	'client_trace_id': str(uuid4())
	}

			headers = {
	'User-Agent': UserAgent.generate(),
	'x-fb-friendly-name': "FbBloksActionRootQuery-com.bloks.www.caa.ar.search.async", 
	'authorization': "OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32",
	'x-fb-conn-uuid-client': str(uuid4()).replace("-","")
	}
			response = requests.post(url, data=payload, headers=headers).json()
			op = str(response).replace("\\","").replace("/","").replace("u", "\\u").encode("utf-8").decode("unicode-escape", errors="ignore")

			if f"It looks like {email} isn’t connected to an accont. Yo can create a new accont with this email or try again." in op or "We coldn't find yor accont. Create a new accont?" in op:
				return {'Programmer : tiger_cod3r \nEmail : email \nAvailable : Yes✅'}
			elif "obfscated_id" in op:
				return {'Programmer : tiger_cod3r \nEmail : email \nAvailable : No❌'}
			else:
				Facebook.CheckV2(email)
		
		except Exception as e:
			print(e)