<?php

# constants
$query = $_GET["s"];
$image_prefix = "http://localhost:8000/wp-content/uploads/";
$es_search_url = "http://elasticsearch:9200/products/_search";

function getClientCountryCode() {
    $ip = $_SERVER['HTTP_CF_CONNECTING_IP'];
    $rev_geo_lookup_url = "http://www.geoplugin.net/json.gp?ip=";
    $cURL = curl_init();
    $setopt_array = array(CURLOPT_URL => $rev_geo_lookup_url . urlencode($ip), CURLOPT_RETURNTRANSFER => true, CURLOPT_HTTPHEADER => array()); 
    curl_setopt_array($cURL, $setopt_array);
    $json_resp = curl_exec($cURL);
    curl_close($cURL);
    $rev_geo_resp = json_decode($json_resp);
    if (isset($rev_geo_resp)) {
        return $rev_geo_resp->geoplugin_countryCode;
    }
    return "";
}

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
$setopt_array = array(CURLOPT_URL => $es_search_url , CURLOPT_RETURNTRANSFER => true, CURLOPT_HTTPHEADER => array('Content-Type: application/json')); 
$es_json_body = (object) [];
$es_json_body->query->bool->must = array(array('query_string' => array('query' => str_replace($color_from_query, "",$query))));
if ($color_from_query != '') {
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