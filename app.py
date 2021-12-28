from flask import Flask
from flask_cors import CORS
from flask import request
from flask import jsonify
import requests
import time
import base64
from requests.auth import HTTPBasicAuth
import os

app= Flask(__name__)
CORS(app)

APPID = os.environ.get("APPID")
ACCESS_KEY = os.environ.get("ACCESS_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
VENDOR = 1
REGION = int(os.environ.get("REGION"))
BUCKET = os.environ.get("BUCKET")
API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
TOKEN_APP_NAME = os.environ.get("TOKEN_APP_NAME")

timeout=30

url="https://api.agora.io/v1/apps/"+ APPID +"/cloud_recording/"


def cloud_post(url, data=None):
	headers = {'Content-type': "application/json;charset=utf-8"}

	try:
		response = requests.post(url, auth=HTTPBasicAuth(API_KEY,API_SECRET), json=data, headers=headers, timeout=timeout, verify=False)
		print("url: %s, request body:%s response: %s" %(url, response.request.body,response.json()))
		return response.json()
	except requests.exceptions.ConnectTimeout:
		raise Exception("CONNECTION_TIMEOUT")
	except requests.exceptions.ConnectionError:
		raise Exception("CONNECTION_ERROR")

def cloud_get(url):
	headers = {'Content-type': "application/json;charset=utf-8"}

	try:
		response = requests.get(url, auth=HTTPBasicAuth(API_KEY,API_SECRET), headers=headers, timeout=timeout, verify=False)
		print("url: %s, request body:%s response: %s" %(url, response.request.body,response.json()))
		return response.json()
	except requests.exceptions.ConnectTimeout:
		raise Exception("CONNECTION_TIMEOUT")
	except requests.exceptions.ConnectionError:
		raise Exception("CONNECTION_ERROR")


@app.route('/',methods=['POST'])
def index():
	print(request.get_data(),flush=True)

	return jsonify(success=True)

@app.route('/acquire',methods=['POST'])
def acquire():
	acquire_url = url+"acquire"
	#r_acquire = cloud_post(acquire_url, acquire_body)
	acquire_body={
		"uid": "99",#request.json['uid'],
		"cname": request.json['cName'],
		"clientRequest": {
			"resourceExpiredHour": 24
		}
	}

	response = cloud_post(acquire_url,acquire_body)

	return response


@app.route('/start',methods=['POST'])
def start():
	start_url = url+ "resourceid/%s/mode/mix/start" % request.json['resourceId']

	response = requests.get('https://'+TOKEN_APP_NAME+'.herokuapp.com/access_token?channel='+request.json['cName']+'&uid=99')

	token = response.json()['token']
	print(token)
	print('token printed: ' + TOKEN_APP_NAME)
	layoutConfig = [{"x_axis": 0.0, "y_axis": 0.0, "width": 0.3, "height": 0.3, "alpha": 0.9, "render_mode": 1},
					{"x_axis": 0.3, "y_axis": 0.0, "width": 0.3,"height": 0.3, "alpha": 0.77, "render_mode": 0}]
	start_body={
			"uid": "99",#request.json['uid'],
			"cname": request.json['cName'],
			"clientRequest": {
				"token": token,
				"storageConfig": {
					"secretKey": SECRET_KEY,
					"region": REGION,
					"accessKey": ACCESS_KEY, 
					"bucket": BUCKET,
					"vendor": VENDOR,
					"fileNamePrefix": [request.json['cName'][2:]]
					},
				"recordingConfig": {
					"audioProfile": 2,
					"channelType": 0,
					"maxIdleTime": 30,
					"transcodingConfig": {
						"width": 640,
						"height": 360,
						"fps": 15,
						"bitrate": 600,
						"mixedVideoLayout": 1,
						"backgroundColor": "#ffffff"
						}
					},
				"recordingFileConfig": {
					"avFileType": ["hls","mp4"]
					}
				}
			}

	response = cloud_post(start_url,start_body)

	return response

@app.route('/stop',methods=['POST'])
def stop():
	stop_url = url+"resourceid/%s/sid/%s/mode/mix/stop" % (request.json['resourceId'], request.json['sid'])
	stop_body = {
		'uid':"99",
		'cname':request.json['cName'],
		'clientRequest':{}
	}

	response = cloud_post(stop_url,stop_body)

	return response

@app.route('/query',methods=['POST'])
def query():
	query_url = url+"resourceid/%s/sid/%s/mode/mix/query" % (request.json['resourceId'], request.json['sid'])

	response = cloud_get(query_url)

	return response



if __name__ == "__main__":
	app.run()
