import requests
import json

# elasticsearch의 주소 지정, products 라는 인덱스명
url = "http://localhost:9200/products"

payload = json.dumps({
    "settings": {
        "index": {
            # shards: 인덱스를 나누는 분산 값, 여기서는 단일 인덱스로 활용, 
            ## performance와 연관(더 빨리 병행 처리가 가능하도록 load balance)
            "number_of_shards": 1,
            # replica: shard마다 지정할 복제수
            ## availability
            "number_of_replicas": 1
        },
        "analysis": {
            "analyzer": {
                "analyzer-name": {
                    "type": "custom",
                    # token을 keyword로 맞추고, 들어오는 keyword를 lowercase 방식으로 처리
                    "tokenizer": "keyword",
                    "filter": "lowercase"
                } 
            }
        }
    },
    "mappings": {
        # 검색을 위해 필요한 properties, 인덱싱을 하고 싶은 인자들
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
            # post가 언제 업로드 되었는지
            "post_date": {
                "type": "date"
            },
            "modified_date": {
                "type": "date"
            },
            # 국내/해외 배송 여부
            "shipped_from": {
                "type": "text"
            }
        }
    }
})
headers = {
    'Content-Type': 'application/json'
}

response = requests.request("PUT", url, headers=headers, data=payload)

print(response.text)
