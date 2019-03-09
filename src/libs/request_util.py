#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  9 10:55:36 2019

@author: chengyu
"""
import requests
import json

def get_intent(message_data, url = 'http://13.124.42.223:9999/api/chat/',
               access_token=None):
    """ Makes use of Send API:
        https://developers.facebook.com/docs/messenger-platform/send-api-reference
    """
    headers = {
        'Content-Type': 'application/json',
    }
#    params = {
#        'access_token': access_token,
#    }
    
    payload= {
      "fromUser": {
        "id": "string",
        "name": "string"
      },
      "toUser": {
        "id": "string",
        "name": "string"
      },
      "conversation": {
        "history": [
          {
            "text": {
              "data": "string",
              "isUser": True,
              "timestamp": "string"
            }
          }
        ]
      },
      "current": message_data,
      "mode": "string",
      "sessionId": "string",
      "messageType": "string",
      "event": "string"
    }
    
    
    url = url
    response = requests.post(url, headers=headers, params=None,
                             data=json.dumps(payload))
    response.raise_for_status()
    return response.json() 

#%%

if __name__ == '__main__':
    print(get_intent("你是笨蛋么"))