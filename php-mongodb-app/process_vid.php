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
    $shared_folder = 'shared';
    $video_filename = $region."_timelapse.mp4";
    $shared_video_path = $shared_folder . '/' . $video_filename;
    
    if ($region) {
        if (file_exists($shared_video_path)) {
            echo json_encode(['region' => $region, 'progress' => 100]);
            die();
        }
        // Rechercher le document correspondant à la région
        $process_vid = $process_vid_collection->findOne(['region' => $region]);
        if ($process_vid) {
            $progress = $process_vid['progress'];
            echo json_encode(['region' => $region, 'progress' => $progress]);
        } else {
            echo json_encode(['error' => 'Region not found']);
        }
    } else {
        // Rechercher une région dont le statut est 'in_progress'
        $process_vid = $process_vid_collection->findOne(['status' => 'in_progress']);
        if ($process_vid) {
            echo json_encode(['region' => $process_vid['region'], 'progress' => $process_vid['progress'], 'status' => $process_vid['status']]);
        } else {
            echo json_encode(['error' => 'No region with status in_progress found']);
        }
    }
} catch (Exception $e) {
    echo json_encode(['error' => $e->getMessage()]);
}