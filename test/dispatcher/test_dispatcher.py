import requests

url_mock = "http://127.0.0.1:8001/mock_dispatch"
payload_mock = {
    "name": "mock_dispatch_request", 
    "description": "This is a test dispatch", 
    "free_space_gb": 10
    }
print(payload_mock)
response_mock = requests.post(url_mock, json=payload_mock)
print(response_mock.headers)
print(response_mock.status_code)
print(response_mock.json())
print("__________________________________________________________________")

url = "http://127.0.0.1:8001/dispatch"
payload = {
    "name": "test_dispatch_request", 
    "description": "This is a test dispatch", 
    "free_space_gb": 10,
    "node_id": "1"
    }
print(payload)
response = requests.post(url, json=payload)
print(response.headers)
print(response.status_code)
print(response.json())