import requests

url = "http://localhost:9200/products"

payload = ""
headers = {}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

"""
{"products":{"aliases":{},"mappings":{"properties":{"content":{"type":"text"},"id":{"type":"long"},"image_file":{"type":"text"},"modified_date":{"type":"date"},"post_date":{"type":"date"},"shipped_from":{"type":"text"},"title":{"type":"text"},"url":{"type":"text"}}},"settings":{"index":{"routing":{"allocation":{"include":{"_tier_preference":"data_content"}}},"number_of_shards":"1","provided_name":"products","creation_date":"1654698110234","analysis":{"analyzer":{"analyzer-name":{"filter":"lowercase","type":"custom","tokenizer":"keyword"}}},"number_of_replicas":"1","uuid":"M1fWo73WRiOvNPBGhNlsOA","version":{"created":"7130299"}}}}}
"""