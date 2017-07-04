# -*- coding:utf-8 -*-
import requests
def send_by_yunpian(phone, code):
    url = "https://sms.yunpian.com/v2/sms/single_send.json"
    data = {
        'apikey': '0c263e35ca1dd0996a84568187abbc3a',
        'mobile': '18408256349',
        'text': '【创客英雄】验证码：1234，欢迎成为创客英雄会员。',
    }

    r = requests.post(url, data)
    print r.content

send_by_yunpian('123',12313)
