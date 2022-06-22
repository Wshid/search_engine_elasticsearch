import requests
import json

url = "http://localhost:9200/products"

payload = json.dumps({
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "analysis": {
            "analyzer": {
                "analyzer-name": {
                    "type": "custom",
                    "tokenizer": "keyword",
                    "filter": "lowercase"
                }
            }
        }
    },
    # properties가 `create_index1.py`에 비해 늘어남
    "mappings": {
        "properties": {
            "id": {
                "type": "long"
            },
            "content": {
                "type": "text"
            },
            "title": {
                "type": "text"
            },
            "url": {
                "type": "text"
            },
            "image_file": {
                "type": "text"
            },
            "post_date": {
                "type": "date"
            },
            "modified_date": {
                "type": "date"
            },
            "shipped_from": {
                "type": "text"
            },
            # keywords, meta_data 추가
            "keywords": {
                "type": "text"
            },
            "meta_data": {
                # 여러가지 요소를 넣을 수 있는 타입
                "type": "object"
            }
        }
    }
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("PUT", url, headers=headers, data=payload)

print(response.text)
