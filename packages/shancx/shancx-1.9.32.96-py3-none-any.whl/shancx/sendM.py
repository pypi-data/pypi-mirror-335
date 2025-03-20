import requests
import datetime 
def sendMES(message,key='0f313-17b2-4e3d-84b8-3f9c290fa596',NN = None):
    webHookUrl = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={NN}{key}'
    response=None
    try:
        url=webHookUrl
        headers = {"Content-Type":"application/json"}
        data = {'msgtype':'text','text':{"content":message}}
        res = requests.post(url,json=data,headers=headers)
    except Exception as e:
        print(e)
 