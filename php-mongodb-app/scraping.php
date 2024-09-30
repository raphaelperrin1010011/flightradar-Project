<?php

if (isset($_REQUEST['year'])) {
    $year = addslashes($_REQUEST['year']);
    $url = 'http://python-data:8100/filtered_links/' . $year;
    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30); 

    $response = curl_exec($ch);

	$response = json_decode($response, true);

	foreach ($response['filtered_links'] as $key => $value) {
		print "<button class='date' id='?date=$value' >" . $value . "</button>";
	}
    curl_close($ch);
}

if (isset($_REQUEST['date'])) {
    $date = addslashes($_REQUEST['date']);
    $url = 'http://python-data:8100/filtered_links_2/' . $date;
    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_TIMEOUT, 30); 

    $response = curl_exec($ch);

    $response = json_decode($response, true);

    foreach ($response['filtered_links_2'] as $key => $value) {
        // Générer des checkboxes stylisées comme des boutons
        echo "<label class='checkbox-button'>
                <input type='checkbox' id='$value' value='$value'>
                <span>$value</span>
              </label>";
    }
    echo "<br><div id='start-container'>";
    echo "<button class='start' id='?process_csv=$date' >Start scraping</button>";
    curl_close($ch);
}


if (isset($_REQUEST['process_csv'])) {
    $data = addslashes($_REQUEST['process_csv']);

    $date = explode("[", $data);
    
    $date_part = substr($date[1], 0, -1);

    $link_2 = explode(",", $date_part);
    $date = $date[0];

    $url = 'http://python-data:8100/process_csv/' . $date;
    $postData = json_encode(['link_2' => $link_2]);

    $ch = curl_init();

    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
    curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $response = curl_exec($ch);

    curl_close($ch);
}
