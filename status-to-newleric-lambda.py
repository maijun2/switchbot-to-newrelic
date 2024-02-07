import os
import time
import hashlib
import hmac
import base64
import uuid
import requests


def lambda_handler(event, context):
    # 環境変数から必要な情報を取得
    switchbot_token = os.getenv("SWITCHBOT_TOKEN")
    switchbot_secret = os.getenv("SWITCHBOT_SECRET")
    switchbot_device = os.getenv("SWITCHBOT_DEVICE")
    newrelic_license_key = os.getenv("NEWRELIC_LICENSEKEY")

    if not (switchbot_token and switchbot_secret and switchbot_device and newrelic_license_key):
        print("Environment variables are missing")
        return {"statusCode": 500, "body": "Environment variables are missing"}

    nonce = str(uuid.uuid4())
    timestamp = int(round(time.time() * 1000))
    signature = generate_signature(switchbot_token, timestamp, nonce, switchbot_secret)

    try:
        devices = get_device_status(switchbot_device, switchbot_token, timestamp, signature, nonce)
        # 温度と湿度を送信
        send_metric("temperature", devices["body"]["temperature"], newrelic_license_key)
        send_metric("humidity", devices["body"]["humidity"], newrelic_license_key)
        return {"statusCode": 200, "body": "Metrics sent successfully"}
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": str(e)}

def generate_signature(token, timestamp, nonce, secret):
    message = f'{token}{timestamp}{nonce}'.encode('utf-8')
    signature = hmac.new(secret.encode('utf-8'), msg=message, digestmod=hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')

def get_device_status(device_id, token, timestamp, sign, nonce):
    API_BASE_URL = f"https://api.switch-bot.com/v1.0/devices/{device_id}/status"
    api_header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "charset": "utf8",
        "t": str(timestamp),
        "sign": sign,
        "nonce": str(nonce),
    }

    response = requests.get(API_BASE_URL, headers=api_header)
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError(f"Error occurred: {response.status_code}")

def send_metric(name, value, license_key):
    headers = {
        "Content-Type": "application/json",
        "Api-Key": license_key,
    }

    data = [{
        "metrics": [{
            "name": name,
            "type": "gauge",
            "value": value,
            "timestamp": time.time(),
            "attributes": {"device.name": "switchbot-sensor"},
        }]
    }]

    response = requests.post(
        "https://metric-api.newrelic.com/metric/v1",
        headers=headers,
        json=data
    )

    if response.status_code not in [200, 202]:
        raise ValueError(f"Failed to send metric: {response.status_code}, {response.text}")

