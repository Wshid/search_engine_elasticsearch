import requests

# search를 주어 모든 결과 확인 가능
url = "http://localhost:9200/products/_search"

payload = {}
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
