import os
import time
import hashlib
import hmac
import base64
import uuid
import requests


def get_env_variable(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"{name} を環境変数でセットしてね")
    return value


def generate_signature(token: str, timestamp: int, nonce: str, secret: str) -> str:
    """
    SwitchBot APIのための署名を生成する。

    Args:
        token (str): アクセストークン。
        timestamp (int): タイムスタンプ。
        nonce (str): ランダム文字列。
        secret (str): シークレットトークン。

    Returns:
        str: 生成された署名。
    """
    message = f'{token}{timestamp}{nonce}'.encode('utf-8')
    signature = hmac.new(secret.encode('utf-8'), msg=message, digestmod=hashlib.sha256).digest()
    return base64.b64encode(signature).decode('utf-8')



def get_device_status(token: str, timestamp: int, sign: str, nonce: str) -> dict:
    """
    SwitchBotデバイスの情報を取得する

    Args:
        token (str): アクセストークン
        timestamp (int): タイムスタンプ
        sign (str): 署名
        nonce (str): ランダム文字列

    Returns:
        dict: デバイスの情報取得
    """

    API_BASE_URL = f"https://api.switch-bot.com/v1.1/devices/{switchbot_device}/status"
    HTTP_OK = 200
    
    api_header = {
        "Authorization": token,
        "Content-Type": "application/json",
        "charset": "utf8",
        "t": str(timestamp),
        "sign": sign,
        "nonce": str(nonce),
    }

    response = requests.get(API_BASE_URL, headers=api_header)
    if response.status_code == HTTP_OK:
        return response.json()
    else:
        raise ValueError(f"Error occurred: {response.status_code}")
        


        
if __name__ == "__main__":
    #set switchbot_token
    switchbot_token = get_env_variable("SWITCHBOT_TOKEN")
    switchbot_secret = get_env_variable("SWITCHBOT_SECRET")
    switchbot_device = get_env_variable("SWITCHBOT_DEVICE")

    #vars
    nonce = str(uuid.uuid4())
    timestamp = int(round(time.time() * 1000))
    signature = generate_signature(switchbot_token, timestamp, nonce, switchbot_secret)
   
    
    #request
    try:
        devices = get_device_status(switchbot_token, timestamp, signature, nonce)
    except ValueError as e:
        print(e)
    else:
        print(devices)

