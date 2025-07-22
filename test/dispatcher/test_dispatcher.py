import requests

url = "http://127.0.0.1:8000/mock_dispatch"
payload = {
    "name": "mock_dispatch_request", 
    "description": "This is a test dispatch", 
    "value": 10737418240
    }
print(payload)
response = requests.post(url, json=payload)
print(response.headers)
print(response.status_code)
print(response.json())