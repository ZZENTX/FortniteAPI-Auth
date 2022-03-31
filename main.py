# -*- coding: utf-8 -*-

import os
import time
import requests
import datetime
import webbrowser

class endpoints:
	token = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
	redirect = "https://www.epicgames.com/id/logout?redirectUrl=https%3A//www.epicgames.com/id/login%3FredirectUrl%3Dhttps%253A%252F%252Fwww.epicgames.com%252Fid%252Fapi%252Fredirect%253FclientId%253Dec684b8c687f479fadea3cb2ad83f5c6%2526responseType%253Dcode"
	pc_client = "ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ"
	ios_client = "MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE"
	exchange = "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/exchange"

def authorization(code):
	h = {
			"Content-Type": "application/x-www-form-urlencoded",
			"Authorization": f"basic {endpoints.pc_client}"
	}

	data = {
			"grant_type": "authorization_code",
			"code": code
	}
	
	r = requests.post(endpoints.token, headers=h, data=data)
	r = json.loads(r.text)

	if "access_token" in r:
		access_token = r["access_token"]
		account_id= r["account_id"]
		displayName= r["displayName"]
		print("Token received successfully!")
		return access_token, account_id, displayName
	else:
		if "errorCode" in r:
			print(f"[ERROR] {r['errorCode']}")
		else:
			print("[ERROR] Unknown error!")
		return False

def get_exchange(access_token):
	h = {
            "Authorization": f"bearer {access_token}",
            "Content-Type": "application/json"
    }
	
	r = requests.get(endpoints.exchange, headers=h, data="{}")
	r = json.loads(r.text)

	if "code" in r:
		exchange_code = r["code"]
		print(f"Exchange code received successfully!")
		return exchange_code
	else:
		if "errorCode" in r:
			print(f"[ERROR] {r['errorCode']}")
		else:
			print("[ERROR] Unknown error!")
		return False

def exchange_auth(code):
	h = {
			"Content-Type": "application/x-www-form-urlencoded",
			"Authorization": f"basic {endpoints.ios_client}"
	}

	data = {
			"grant_type": "exchange_code",
			"exchange_code": code
	}
	
	r = requests.post(endpoints.token, headers=h, data=data)
	r = json.loads(r.text)

	if "access_token" in r:
		access_token = r["access_token"]
		device_id = r["device_id"]
		print(f"Authorization through Exchange code was successful!")
		return device_id, access_token
	else:
		if "errorCode" in r:
			print(f"[ERROR] {r['errorCode']}")
		else:
			print("[ERROR] Unknown error!")
		return False

def device_auth(account_id, device_id, secret):
	h = {
			"Authorization": "basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE"
	}

	data = {
			"grant_type": "device_auth",
			"account_id": f"{account_id}",
			"device_id":  f"{device_id}",
			"secret": f"{secret}"
	}

	r = requests.post(endpoints.token, headers=h, data=data)
	r = json.loads(r.text)

	if "access_token" in r:
		print("Authorization through the device was successful!\n")
		return True
	else:
		if "errorCode" in r:
			print(f"[ERROR] {r['errorCode']}")
			return False
		else:
			print("[ERROR] Unknown error!")
		return False

def create_device(account_id, access_token):
	h = {
			"Authorization": f"bearer {access_token}",
			"Content-Type": "application/json"
	}
	
	r = requests.post(f"https://account-public-service-prod.ol.epicgames.com/account/api/public/account/{account_id}/deviceAuth", headers=h, data="{}")
	r = json.loads(r.text)

	if "secret" in r:
		secret = r["secret"]
		device_id = r["deviceId"]
		print("The creation of the device was successful!")
		return secret, device_id
	else:
		if "errorCode" in r:
			print(f"[ERROR] {r['errorCode']}")
		else:
			print("[ERROR] Unknown error!")
		return False

# Device creation and authorization
def main(code):
	try:
		# Basic Authorization
		auth = authorization(code)

		access_token = auth[0]
		account_id = auth[1]
		name = auth[2]

		# Getting an Exchange Code
		exchange = get_exchange(access_token)

		# Authorization via exchange code
		data = exchange_auth(exchange)
		access_token = data[1]

		# Creating a device for authorization
		all_data = create_device(account_id, access_token)
		secret = all_data[0]
		device_id = all_data[1]

		# Authorization attempt through the created device
		result = device_auth(account_id, device_id, secret)

		if result:
			return name, account_id, secret, device_id
		else:
			return False
	except Exception as e:
		return False

# Extracting code from a string
def line_processing(line):
	line = line.split('"')
	if len(line[7]) == 32:
		print(f"Code: {line[7]}\n")
		return line[7]
	else:
		return False

if __name__ == '__main__':
	print("Now the site will open in your browser, after authorization, paste the entire line.")
	time.sleep(3)
	webbrowser.open(endpoints.redirect, new=2)

	line = input("Line: ")
	code = line_processing(line)

	if code != False:
		authorization = main(code)
		if authorization != False:
			print("Information:\n\nAccount name: %s\nAccount id: %s\nSecret: %s\nDevice id: %s" % (authorization[0], authorization[1], authorization[2], authorization[3]))
		else:
			print("An error occurred while creating the device!")
	else:
		print("The line from the website was inserted incorrectly! Try again!")

	input('Press any key...')
