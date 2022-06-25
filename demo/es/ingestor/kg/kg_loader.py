# 위키미디어의 데이터를 쉽게 parse할 수 있는 라이브러리
import mwparserfromhell
import re
import xml.etree.ElementTree as etree

# 위키미디어의 파일을 읽음
def loadWikimedia(source_file):
    tree = etree.parse(source_file)
    root = tree.getroot()
    namespace = getNamspace(root.tag)
    kg = {}
    # page element를 순회
    for page in root.findall('./' + namespace + 'page'):
        # namespace내 title 태그
        title = page.find(namespace + 'title').text
        # revision 서브 태그
        page_content = page.findall(
            './' + namespace + 'revision/' + namespace + 'text')
        entry = {}
        if len(page_content) > 0:
            # 텍스트 컨텐츠가 parse내로 유입
            wikicode = mwparserfromhell.parse(page_content[0].text)
            templates = wikicode.filter_templates()
            for template in templates:
                #print(template.name)
                for param in template.params:
                    value = stripWikilinksForText(str(param.value)).strip()
                    if len(value) > 0:
                        # 생물 분류 내 이름, 화석_범위, 그림, 그림_설명등의 속성에 따른 결과 값 [[ ... ]] 내용을 한개씩 파싱
                        # 이후 entry라는 key,value dict로 관리
                        entry[str(param.name).strip()] = value
        # 단순히 map에 1차적으로 표현
        # 이를 그래프로 표현하려면 neo4j나 redisGraph등을 사용하여 추출 가능
        # 예제상에서는 간단하게 작업하기 위해 1차원만 사용
        kg[title] = entry
    return kg

# 위키미디아 스타일 링크에서 텍스트만을 추출하는 helper function 입니다.
# [[ ... ]] 형태의 데이터를 파싱
def stripWikilinksForText(wikilink):
    return re.sub(r'\[\[(.+?)\|.+?\]\]', r'\1', wikilink).replace('[[', '').replace(']]', '')

# XML 의 namespace 를 찾아 돌려줍니다.
def getNamspace(tag):
    return '{' + tag.split('}')[0].strip('{') + '}'
