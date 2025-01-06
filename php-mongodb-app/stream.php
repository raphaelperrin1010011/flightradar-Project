<?php


$airflow_url = 'http://airflow-webserver:8080/api/v1';
$username = 'airflow';
$password = 'airflow';

// $redis = new Redis();
// $redis->connect('redis', 6379); // Connectez-vous à Redis (vérifiez le nom du service et le port)

function call_airflow_api($endpoint, $method = 'GET', $data = null) {
    global $username, $password, $airflow_url;

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $airflow_url . $endpoint);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_USERPWD, "$username:$password");
    curl_setopt($ch, CURLOPT_TIMEOUT, 30);

    if ($method === 'POST') {
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
        if ($data) {
            curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
        }
    }

    $response = curl_exec($ch);
    $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);

    if ($http_code !== 200 && $http_code !== 201) {
        echo "Erreur: Impossible d'accéder à l'API Airflow (Code: $http_code). Endpoint: $endpoint";
        return false;
    }

    return json_decode($response, true);
}

if (isset($_GET['region'])) {

    $region = addslashes($_GET['region']);
    $shared_folder = 'shared';
    $video_filename = $region."_timelapse.mp4";
    $shared_video_path = $shared_folder . '/' . $video_filename;
    
    if (file_exists($shared_video_path)) {
        echo("<video id='video' controls><source src='shared/".$region."_timelapse.mp4' type='video/mp4'>Your browser does not support the video tag.</video>");
        die();
    }

    // Lancer l'écoute Redis en arrière-plan
    $redisListener = proc_open('php redis_listener.php', [
        1 => ['pipe', 'w'], // Rediriger stdout
        2 => ['pipe', 'w'], // Rediriger stderr
    ], $pipes);
    
    if (!is_resource($redisListener)) {
        die("Impossible de démarrer le processus Redis listener.<br><br>");
    }
    
    // Appeler l'API Airflow
    $response = call_airflow_api('/dags/python-timelapse-workflow/dagRuns', 'POST', [
        'conf' => ['region' => $region]
    ]);
    
    // Lire les sorties de Redis listener en temps réel
    $outputBuffer = '';
    while ($status = proc_get_status($redisListener)) {
        if (!$status['running']) {
            break;
        }
    
        // Lire stdout et afficher dans le processus principal
        while ($output = fgets($pipes[1])) {
            $outputBuffer .= $output;
        }
    
        // Lire stderr (en cas d'erreurs)
        while ($error = fgets($pipes[2])) {
            echo nl2br("Erreur Redis Listener : $error"); // Utiliser nl2br pour conserver les sauts de ligne
        }
    
        usleep(30000); // Petite pause pour éviter de surcharger la boucle
    }

    fclose($pipes[1]);
    fclose($pipes[2]);
    proc_close($redisListener);

    if ($outputBuffer === "dag_failed") {
        echo("Error: timelapse api failed.<br><br>");
        die();
    } else {
        echo("<video id='video' controls><source src='shared/".$region."_timelapse.mp4' type='video/mp4'>Your browser does not support the video tag.</video>");
        die();
    }
    //A  REVOIR ICIIII
}
?>