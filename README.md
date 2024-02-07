# これは何？
Switchbot の温度計で管理している各種情報を NewRelic で管理すべくサクッと書いたPythonコード類です

## 構成
getdevice-switchbot.py
- Switchbot へ登録しているデバイスの情報を一覧で取得します

getstatus-switchbot.py
- 上記で取得したデバイス情報を指定し、デバイスで管理している各種情報を取得します
- Switchbot 温度計で管理している温度・湿度を取得するのが目的です

status-to-newleric
- Switchbot 温度計で管理している温度・湿度の情報をNewRelic へ送信します。

status-to-newleric-lambda.py
- 最終的にLambdaで動作させるコードになります。