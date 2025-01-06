<?php
require 'vendor/autoload.php'; // Assurez-vous d'avoir installé la bibliothèque MongoDB pour PHP

use MongoDB\Client;

header('Content-Type: application/json');

try {
    // Connexion à MongoDB
    $client = new Client('mongodb://mongodb:27017/');
    $db = $client->opensky; // Remplacez par le nom de votre base de données
    $process_vid_collection = $db->process_vid;

    // Récupérer le paramètre 'region' de la requête
    $region = isset($_GET['region']) ? $_GET['region'] : null;

    if ($region) {
        // Vérifier si le document existe déjà
        $existingDocument = $process_vid_collection->findOne(['region' => $region]);

        if ($existingDocument) {
            echo json_encode(['success' => true, 'message' => 'Document already exists for this region']);
        } else {
            // Créer le document avec 'progress' à 0.1 et 'status' à 'in_progress' pour la région spécifiée
            $result = $process_vid_collection->insertOne(
                ['region' => $region, 'progress' => 0.1, 'status' => 'in_progress']
            );

            echo json_encode(['success' => true, 'message' => 'Document created with progress set to 0.1 and status set to in_progress']);
        }
    } else {
        echo json_encode(['error' => 'Region parameter is missing']);
    }
} catch (Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}