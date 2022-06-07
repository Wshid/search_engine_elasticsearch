<?php

# constants
$query = $_GET["s"];
$image_prefix = "http://localhost:8000/wp-content/uploads/";
$es_search_url = "http://elasticsearch:9200/products/_search?q=";

# 검색을 실행합니다
$cURL = curl_init();
$setopt_array = array(CURLOPT_URL => $es_search_url . urlencode($query), CURLOPT_RETURNTRANSFER => true, CURLOPT_HTTPHEADER => array()); 
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