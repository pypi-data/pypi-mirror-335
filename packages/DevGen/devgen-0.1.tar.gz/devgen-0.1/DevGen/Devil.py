import requests
import json
class DevGen:
    @staticmethod
    def Gen(message: str):
        url = "https://www.blackbox.ai/api/chat"
        
        payload = {
            "messages": [
                {
                    "id": "tYD3wrF",
                    "content": message,
                    "role": "user"
                }
            ],
            "agentMode": {},
            "id": "tYD3wrF",
            "previewToken": None,
            "userId": None,
            "codeModelMode": True,
            "trendingAgentMode": {},
            "isMicMode": False,
            "userSystemPrompt": None,
            "maxTokens": 1024,
            "playgroundTopP": None,
            "playgroundTemperature": None,
            "isChromeExt": False,
            "githubToken": "",
            "clickedAnswer2": False,
            "clickedAnswer3": False,
            "clickedForceWebSearch": False,
            "visitFromDelta": False,
            "isMemoryEnabled": False,
            "mobileClient": False,
            "userSelectedModel": None,
            "validated": "00f37b34-a166-4efb-bce5-1312d87f2f94",
            "imageGenerationMode": False,
            "webSearchModePrompt": False,
            "deepSearchMode": False,
            "domains": None,
            "vscodeClient": False,
            "codeInterpreterMode": False,
            "customProfile": {
                "name": "",
                "occupation": "",
                "traits": [],
                "additionalInfo": "",
                "enableNewChats": False
            },
            "session": {
                "user": {
                    "name": "AtTet",
                    "email": "nasr2python@gmail.com",
                    "image": "https://lh3.googleusercontent.com/a/ACg8ocJ4CzXb4sBKosKJ8u3ZE3wmw6KnMBl7p-TC0hSkWY3EBJZGyicZ=s96-c"
                },
                "expires": "2025-04-18T04:47:20.249Z"
            },
            "isPremium": False,
            "subscriptionCache": {
                "status": "FREE",
                "expiryTimestamp": None,
                "lastChecked": 1742359620127,
                "isTrialSubscription": False
            },
            "beastMode": False
        }

        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
            'Content-Type': "application/json",
            'sec-ch-ua-platform': "\"Linux\"",
            'sec-ch-ua': "\"Chromium\";v=\"134\", \"Not:A-Brand\";v=\"24\", \"Google Chrome\";v=\"134\"",
            'sec-ch-ua-mobile': "?0",
            'origin': "https://www.blackbox.ai",
            'sec-fetch-site': "same-origin",
            'sec-fetch-mode': "cors",
            'sec-fetch-dest': "empty",
            'referer': "https://www.blackbox.ai/",
            'accept-language': "en-US,en;q=0.9,ar-AE;q=0.8,ar;q=0.7",
            'priority': "u=1, i",
            'Cookie': "sessionId=dc345ae3-deca-4ae7-b782-fef560736c03; intercom-id-jlmqxicb=91822be1-d6ea-4b8b-bce7-3b160b53c1fa; intercom-device-id-jlmqxicb=3bc6e34c-f51f-4f0a-a96b-efe3e68bd1a4; intercom-id-x55eda6t=05dd1e01-81cf-46ea-a733-5b8bc7eabc5b; intercom-device-id-x55eda6t=97a59499-b0f5-44e7-83bc-2b9b5a47bdce; render_app_version_affinity=dep-cvd3kdin91rc73dcilgg; __Host-authjs.csrf-token=500386bca4d638c8686625a06b0c62db09939deba315136933326f1171aa6efa%7C6d0026b6fb5631695794c885527c6bf1df415579ac7f2311f68f8d5e28ff0d2b; __Secure-authjs.callback-url=https%3A%2F%2Fwww.blackbox.ai; intercom-session-x55eda6t=ekY2c0NEQTBnS2pFZ3JNRk1ScHBJQ3RUK1ErM1VUWUs1Um5NMW8yU1ozVDJBWjBuMU5za2FkVVRmYURyOExhb3Y3NmlBcWRmQUxadUQ4WWlZSVd5aGRJRWdiWHhKOVl6bEVqVktjdFhabmM9LS0zTlpMZFdkTnFMQk9Sd09DMVUzUGJnPT0=--428c2a69bc27928d525ecc05349b1740456ac6d6; __Secure-authjs.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..7oED-J-77zHzrT7u.EL8cXcavn9q8-g7Qpnx6a9OU3-QFiMou3jUDa3oagnW9_vXl5FwPb29b4OznYfPM02shZD4pDqKwUeQz7qVQ0KhAF69kgti7mrVMt9NwlbiPMFqeCnokbCrR8oqEsNcBrBySAGBR_FkGqq-epNLem7LHJNVccs1dH1jEWGJCnsGUbRxkhuvAxalpFq_hkVfo7Sevd2CvuEwCgPpWzQFiYwgSWr-nFuooo0hBgWGAipSuiqStFGWQS1uqWkcfMKByxrRTxFN2Te36Dhb_40l6aTcPOYc0f7kLcbjH-HNpd4bzWLCk12ykf6yUeAM1uRzEXjbI1asEzVvbSDOIScbxHivG7FA0hpx25Gz-9tyFZbeXPTOFBix_yDyGeFecXDOtg-cbB7y-CBFEn_qWTdqyNo5kIwfD6azhYIzvpcM5-86NIkxu0S-F4ncV_PKY6WOfQSrZ_QAqtgFjpXeZsETQTAP2FXJDyUoS6YvHxLXnY-gYw6ZK6r0ZXinfhBscwtL3DJnr.LBdzqwgC-EMyqo8AIBs-jA"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return "حدث خطأ أثناء الاتصال بالخدمة"