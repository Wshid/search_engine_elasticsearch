<?php

# constants
$query = $_GET["s"];
$image_prefix = "http://localhost:8000/wp-content/uploads/";
# search를 이용해 query_string을 사용하여 조회 가능
# must, should, ...
# rank_features를 변경할때도 사용함(boost를 통해 score boost 가능, 기본 socre * boost로 정의됨)
$es_search_url = "http://elasticsearch:9200/products/_search";


function getClientCountryCode() {
    # php 7.0부터 지원, ip를 가져올 수 있음
    $ip = $_SERVER['HTTP_CF_CONNECTING_IP'];
    # reverse IP lookup, geoplugin 서비스 사용, ip를 입력하면 해당 위치를 알려줌
    # json.gp를 입력하면 관련 내용을 json 형태로 받아볼 수 있음 
    $rev_geo_lookup_url = "http://www.geoplugin.net/json.gp?ip=";
    $cURL = curl_init();
    $setopt_array = array(CURLOPT_URL => $rev_geo_lookup_url . urlencode($ip), CURLOPT_RETURNTRANSFER => true, CURLOPT_HTTPHEADER => array()); 
    curl_setopt_array($cURL, $setopt_array);
    $json_resp = curl_exec($cURL);
    curl_close($cURL);
    $rev_geo_resp = json_decode($json_resp);
    # json 데이터가 올바르다면, 관련 값 리턴, 아닐경우 ""
    if (isset($rev_geo_resp)) {
        return $rev_geo_resp->geoplugin_countryCode;
    }
    return "";
}

# query가 string이고, string 내에 색깔(e.g. red)가 들어있다면 해당 색상 리턴
function getColorFromQuery($query) {
    if (strpos($query, 'red') !== false) {
        return 'red';
    } else if (strpos($query, 'blue') !== false) {
        return 'blue';
    } else if (strpos($query, 'green') !== false) {
        return 'green';
    }
    return '';
}

# 검색을 실행합니다
$cURL = curl_init();
$country_code = getClientCountryCode();
$color_from_query = getColorFromQuery($query);
# json type 추가에 따라 header내에 content-type 추가
$setopt_array = array(CURLOPT_URL => $es_search_url , CURLOPT_RETURNTRANSFER => true, CURLOPT_HTTPHEADER => array('Content-Type: application/json')); 
$es_json_body = (object) [];
# json attribute를 정의하는 부분. es search_query body를 생성하는 작업
# 특정 색상 정보 (e.g. red)가 쿼리 자체에 존재한다면, 해당 내용을 ""로 치환(제거)
## e.g. `red 장미` 검색 -> `장미` 검색 결과로
$es_json_body->query->bool->must = array(array('query_string' => array('query' => str_replace($color_from_query, "",$query))));
# color_from_query가 있다면, 관련 내용을 `color_ranks`에 추가함
if ($color_from_query != '') {
    # es 내부의 값들은 json 형태로 `.`을 통해 접근 가능(e.g. color_ranks.red)
    array_push($es_json_body->query->bool->must,
        array('rank_feature' => array('field' => 'color_ranks.' . $color_from_query, 'saturation' => array('pivot' => 35))));
}
if (strcasecmp($country_code, 'KR') == 0) {
    array_push($es_json_body->query->bool->must,
        array('rank_feature' => array('field' => 'local_confidence.KR', 'boost' => 1.0)));
}
curl_setopt( $cURL, CURLOPT_POSTFIELDS, json_encode($es_json_body));
curl_setopt_array($cURL, $setopt_array);
$json_response_data = curl_exec($cURL);
curl_close($cURL);
$search_result = json_decode($json_response_data);
?>
<html>
    <head>
        <title>검색결과 - <?php print($query) ?></title>
    </head>
    <body>
        <div><?php print($search_result->took) ?>ms 안에 <?php print($search_result->hits->total->value) ?>개의 검색결과를 찾았습니다.</div>
        <br>
        <?php
            foreach ($search_result->hits->hits as $row) {
                print("<div><img src='" . $image_prefix . $row->_source->image_file . "' height='100'></div>");
                print("<div><a href='" .  $row->_source->url . "'>" . $row->_source->title . " (score:" . $row->_score . ")</a></div>");
                print("<div>" . $row->_source->content . "</div>");
                print('<hr>');
            }
        ?>
        <br>
        <!-- 재검색 기능 -->
        <form action="search.php" method="get">
            <input type="text" placeholder="재검색 하기" name="s">
            <button type="submit">검색</button>
        </form>
    </body>
</html>