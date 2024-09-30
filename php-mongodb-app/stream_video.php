<?php
require 'vendor/autoload.php';
use MongoDB\Client;

// Connexion à la base de données MongoDB
$client = new Client('mongodb://mongodb:27017/');
$db = $client->opensky;
$collection = $db->flights;

// Récupérer les paramètres 'time' et 'region' depuis l'URL
$timestamp = isset($_GET['time']) ? $_GET['time'] : null;
$region = isset($_GET['region']) ? $_GET['region'] : 'world';

if ($timestamp === null) {
    // Récupérer toutes les valeurs 'time' dans l'ordre
    $times = $collection->distinct('time', [], ['sort' => ['time' => 1]]);
    header('Content-Type: application/json');
    echo json_encode($times);
    exit;
}

$api_url = 'http://python-timelapse:5000/get_image?region=' . $region . '&time=' . $timestamp;

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $api_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HEADER, false);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);

$image_data = curl_exec($ch);

if (curl_errno($ch)) {
    echo "Error: " . curl_error($ch);
} else {
    header('Content-Type: image/jpeg');
    header('Cache-Control: no-cache');
    echo $image_data;
}

curl_close($ch);