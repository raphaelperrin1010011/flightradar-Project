<?php
require 'vendor/autoload.php'; // Inclure l'autoloader de Composer

use MongoDB\Client;

// Se connecter à MongoDB
$client = new Client("mongodb://mongodb:27017/");

// Sélectionner la base de données et les collections
$database = $client->selectDatabase('opensky');
$flightsCollection = $database->selectCollection('flights');

// Récupérer les paramètres de la requête
$icao24 = isset($_GET['icao24']) ? $_GET['icao24'] : null;
$currentTime = isset($_GET['currentTime']) ? (int)$_GET['currentTime'] : 0;

$logs = [];

if (!$icao24 || $currentTime === 0) {
    $logs[] = "Paramètres manquants ou invalides.";
    echo json_encode(['error' => "Paramètres manquants ou invalides.", 'logs' => $logs]);
    exit;
}

// Journaliser les paramètres reçus
$logs[] = "Received parameters: icao24=$icao24, currentTime=$currentTime";

// Récupérer les documents de la collection 'flights' pour l'avion spécifié depuis le temps actuel
$query = [
    'icao24' => $icao24,
    'time' => ['$gte' => $currentTime] // Récupérer les documents à partir du timestamp fourni
];
$options = [
    'sort' => ['time' => 1] // Trier par time croissant
];

// Journaliser la requête MongoDB
$logs[] = "MongoDB query: " . json_encode($query);

$flights = $flightsCollection->find($query, $options);

$data = [];
foreach ($flights as $flight) {
    if (!empty($flight['lat']) && !empty($flight['lon']) && !empty($flight['time'])) {
        $data[] = [
            'lat' => (float)$flight['lat'],
            'lon' => (float)$flight['lon'],
            'time' => (int)$flight['time']
        ];
    }
}

// Journaliser le nombre de documents trouvés
$logs[] = "Number of documents found: " . count($data);

// Journaliser les documents trouvés
foreach ($data as $index => $flight) {
    $logs[] = "Document $index: " . json_encode($flight);
}

if (empty($data)) {
    echo json_encode(['error' => "Aucun parcours trouvé pour l'avion $icao24 depuis le temps $currentTime.", 'logs' => $logs]);
    exit;
}

// Retourner les données en JSON
header('Content-Type: application/json');
echo json_encode(['path' => $data, 'logs' => $logs]);