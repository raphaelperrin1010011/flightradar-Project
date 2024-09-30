<?php
require 'vendor/autoload.php'; // Inclure l'autoloader de Composer

use MongoDB\Client;

// Se connecter à MongoDB
$client = new Client("mongodb://mongodb:27017/");

// Sélectionner la base de données et la collection
$database = $client->selectDatabase('opensky');
$flightsCollection = $database->selectCollection('flights');

$data = [];

// Définir les paramètres de pagination
$limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 100;
$lastTime = isset($_GET['lastTime']) ? (int)$_GET['lastTime'] : 0;

// Si lastTime est 0, récupérer le premier time le plus bas
if ($lastTime === 0) {
    $firstFlight = $flightsCollection->findOne([], ['sort' => ['time' => 1]]);
    // error_log("Premier vol trouvé : " . json_encode($firstFlight));
    if ($firstFlight && isset($firstFlight['time'])) {
        $lastTime = (int)$firstFlight['time'];
    } else {
        echo json_encode(['error' => "Aucun vol trouvé avec un time."]);
        exit;
    }
} else {
    // Trouver le suivant plus gros timestamp après le dernier time
    $nextFlight = $flightsCollection->findOne(['time' => ['$gt' => $lastTime]], ['sort' => ['time' => 1]]);
    if ($nextFlight && isset($nextFlight['time'])) {
        $lastTime = (int)$nextFlight['time'];
    } else {
        echo json_encode(['error' => "Aucun vol trouvé avec un time supérieur à $lastTime."]);
        exit;
    }
}

$query = ['time' => (int)$lastTime];
$flights = $flightsCollection->find($query);

$flightCount = $flightsCollection->countDocuments($query);

if ($flightCount === 0) {
    // error_log("Aucun vol trouvé avec le time");
}
foreach ($flights as $flight) {
    // error_log("Vol trouvé : " . json_encode($flight)); 
    if (!empty($flight['icao24']) && !empty($flight['lat']) && !empty($flight['lon']) && !empty($flight['time']) && !empty($flight['callsign'])) {
        $data[] = [
            'icao24' => $flight['icao24'],
            'lat' => (float)$flight['lat'],
            'lon' => (float)$flight['lon'],
            'time' => (int)$flight['time'],
            'callsign' => $flight['callsign'],
            'velocity' => isset($flight['velocity']) ? (float)$flight['velocity'] : null,
            'heading' => isset($flight['heading']) ? (float)$flight['heading'] : null,
            'vertrate' => isset($flight['vertrate']) ? (float)$flight['vertrate'] : null,
            'baroaltitude' => isset($flight['baroaltitude']) ? (float)$flight['baroaltitude'] : null,
            'geoaltitude' => isset($flight['geoaltitude']) ? (float)$flight['geoaltitude'] : null,
            'lastposupdate' => isset($flight['lastposupdate']) ? (float)$flight['lastposupdate'] : null,
            'lastcontact' => isset($flight['lastcontact']) ? (float)$flight['lastcontact'] : null
        ];
    }
}

if (empty($data)) {
    echo json_encode(['error' => "Aucun vol trouvé avec le time $lastTime."]);
    exit;
}

// Obtenir le dernier timestamp des données récupérées
$lastTime = end($data)['time'];

// Retourner les données en JSON avec le dernier timestamp
header('Content-Type: application/json');
echo json_encode(['data' => $data, 'lastTime' => $lastTime]);