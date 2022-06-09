import ast
import datetime
import hashlib
import json
import mysql.connector
import requests

# SQL 에 연결하여 제품 페이지들을 추출하여 ProductPost array 로 돌려주는 함수입니다
# Ingestion을 대신하는 함수
# Elasticsearch에 들어가는 데이터를 여기서 제공/생성
def getPostings():
    cnx = mysql.connector.connect(user='root',
                                password='my_secret_pw',
                                host='localhost',
                                port=9906,
                                database='flowermall')
    cursor = cnx.cursor()

    # 필요한 데이터 추출
    query = ('SELECT posts.ID AS id, posts.post_content AS content, posts.post_title AS title, posts.guid AS post_url, posts.post_date AS post_date, posts.post_modified AS modified_date, metadata.meta_value AS meta_value, image_data.meta_value AS image FROM wp_posts AS posts JOIN wp_postmeta AS image_metadata ON image_metadata.post_id = posts.ID JOIN wp_postmeta AS image_data ON image_data.post_id = image_metadata.meta_value JOIN wp_postmeta AS metadata ON metadata.post_id = posts.ID WHERE posts.post_status = "publish" AND posts.post_type = "product" AND metadata.meta_key = "_product_attributes" AND image_metadata.meta_key = "_thumbnail_id" AND image_data.meta_key = "_wp_attached_file"')
    cursor.execute(query)

    posting_list = []
    # 받아온 컬럼 데이터를 ProductPost로 매핑
    for (id, content, title, url, post_date, modified_date, meta_value, image) in cursor:
        print("Post {} found. URL: {}".format(id, url))
        product = ProductPost(id, content, title, url,
                             post_date, modified_date, assumeShippingLocation(meta_value), image)
        posting_list.append(product)

    cursor.close()
    cnx.close()
    return posting_list

# 엘라스틱서치에 출력하는 함수입니다.
def postToElasticSearch(products):
    # `/<target>/_doc`: 특정 인덱스에 문서 색인
    ## POST; elasticsearch가 이 doc에 대한 고유 ID를 직접 생성
    ## PUT; 직접 사용자가 id 제공
    ## 이 예제에서는 직접 id를 제공(고유문서에 대한 특정 id를 찾아 중복이 되는것을 막기 위함)
    putUrlPrefix = 'http://localhost:9200/products/_doc/'
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    for product in products:
        # product의 url을 기준으로 고유 id 생성
        id = getUniqueIndexId(product.url)
        print(id)
        # prefix + id 형태
        # json.dumps를 활용하여 product 데이터를 json으로 변경
        r = requests.put(putUrlPrefix + id, data=json.dumps(product.__dict__,
                        indent=4, sort_keys=True, default=json_field_handler), headers=headers)
        # 에러 핸들링
        if r.status_code >= 400:
           print("There is an error writing to elasticsearch")
           print(r.status_code)
           print(r.json()) 

# 아주 naive 한 출고지 extraction subroutine
# 국내/해외 배송 관련
# 관리자 로그인 페이지: localhost:8000/wp-login.php, docker-compose.yml에 있는 id/pw로 로그인 가능
# 관리자 페이지 내에서 각 상품별 '배송지'확인 가능
# 상품 페이지에서는 보이지 않으나, mysql에는 저장된 데이터
# 해당 메타 데이터를 파싱하여 국내/해외 여부 판별
def assumeShippingLocation(raw_php_array):
    if u'국내' in raw_php_array:
        return '국내'
    return '해외'

# Custom handlers for marshalling python object into JSON 
# json에 datetime field가 있으면 isoformat으로 만듦
# json으로 convert할때 에러가 생기지 않도록 함
def json_field_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    raise TypeError("Unable to parse json field")

# 엘라스틱서치에서 사용될 문서의 고유 아이디를 생성합니다.
def getUniqueIndexId(url):
    # sha1 함수 이용
    return hashlib.sha1(url.encode('utf-8')).hexdigest()

# 제품 페이지를 표헌하는 class 입니다.
# elasticsearch에 있는 인덱스 properties를 매핑한 python class, create_index1.py에서 확인 가능
class ProductPost(object):
  """
    Represents semantic data for a single product post
  """
  def __init__(self, id, content, title, url, post_date, modified_date, shipped_from, image_file):
    self.id = id
    self.content = content
    self.title = title
    self.url = url
    self.post_date = post_date
    self.modified_date = modified_date
    self.shipped_from = shipped_from
    self.image_file = image_file

p = getPostings()
postToElasticSearch(p)
