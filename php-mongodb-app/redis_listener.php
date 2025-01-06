<?php
// Connexion à Redis
$redis = new Redis();
$connected = $redis->connect('redis', 6379);
$redis->select(0);

if (!$connected) {
    echo "Erreur : impossible de se connecter à Redis.\n";
    exit(1);
}


// Canal Redis pour écouter les notifications
$channel = 'dag_notifications';

$redis->subscribe([$channel], function ($redis, $chan, $msg) {
    // Créer une nouvelle connexion Redis dans la fonction de rappel
    $redis_callback = new Redis();
    $redis_callback->connect('redis', 6379);
    $redis_callback->select(0);

    // print_r($msg);
    
    if ($msg === 'year') {
        // Vérifier si la clé existe
        if ($redis_callback->exists('year')) {
            $results = $redis_callback->get('year');
            if ($results !== false) {
                $decoded_results = json_decode($results, true); // Désérialisation des données JSON
                if (json_last_error() === JSON_ERROR_NONE) {
                    print_r($decoded_results);
                }
            }
        }
    }
    if ($msg === 'filtered_links_2') {
        if ($redis_callback->exists('filtered_links_2')) {
            $results = $redis_callback->get('filtered_links_2');
            if ($results !== false) {
                $decoded_results = json_decode($results, true); // Désérialisation des données JSON
                if (json_last_error() === JSON_ERROR_NONE) {
                    print_r($decoded_results);
                }
            }
        }
    }
    if ($msg === 'image') {
        if ($redis_callback->exists('image')) {
            $results = $redis_callback->get('image');
            if ($results !== false) {
                $decoded_results = json_decode($results, true); // Désérialisation des données JSON
                if (json_last_error() === JSON_ERROR_NONE) {
                    print_r($decoded_results);
                }
            }
        }
    }
    $redis->unsubscribe([$chan]); // Désabonnement après réception
    $redis_callback->close();
    $redis->close();
});
