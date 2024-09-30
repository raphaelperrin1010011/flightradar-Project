<?php
require 'vendor/autoload.php'; // Assurez-vous d'avoir installé la bibliothèque MongoDB pour PHP

use MongoDB\Client;

header('Content-Type: application/json');

try {
    // Connexion à MongoDB
    $client = new Client('mongodb://mongodb:27017/');
    $db = $client->opensky; // Remplacez par le nom de votre base de données
    $progressCollection = $db->progress;

    // Récupérer la progression
    $progressDocument = $progressCollection->findOne([]);

    if ($progressDocument) {
        $progress = $progressDocument['progress'];
    } else {
        $progress = 0;
    }

    // Retourner la progression au format JSON
    echo json_encode(['progress' => $progress]);
} catch (Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}