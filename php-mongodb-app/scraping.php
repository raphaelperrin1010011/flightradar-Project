<?php
session_start();

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

if (isset($_REQUEST['year'])) {

    // Lancer l'écoute Redis en arrière-plan
    $redisListener = proc_open('php redis_listener.php', [
        1 => ['pipe', 'w'], // Rediriger stdout
        2 => ['pipe', 'w'], // Rediriger stderr
    ], $pipes);
    
    if (!is_resource($redisListener)) {
        die("Impossible de démarrer le processus Redis listener.<br><br>");
    }
    
    // Appeler l'API Airflow
    $year = addslashes($_REQUEST['year']);
    $response = call_airflow_api('/dags/filtered_links_workflow/dagRuns', 'POST', [
        'conf' => ['year' => $year]
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
    
    // Fermer les ressources après l'arrêt du listener
    fclose($pipes[1]);
    fclose($pipes[2]);
    proc_close($redisListener);
    
    preg_match_all('/\[\d+\] => ([^ ]+)/', $outputBuffer, $matches);
    $output_buffer_tab = $matches[1];

    foreach ($output_buffer_tab as $key => $value) {
        $value = preg_replace('/[^0-9-]+$/', '', $value);
        $value = str_replace('#states/', '', $value);
        $parsed_value = str_replace('.', '', $value);
        echo "<button class='date' id='?date=$value'>" . $parsed_value . "</button>";
    }
}

if (isset($_REQUEST['date'])) {

    if (isset($_REQUEST['date'])) {
        $_SESSION['date'] = $_REQUEST['date'];
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
    $date = addslashes($_REQUEST['date']);
    $response = call_airflow_api('/dags/filtered_links_2_workflow/dagRuns', 'POST', [
        'conf' => ['date' => $date]
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
    
    // Fermer les ressources après l'arrêt du listener
    fclose($pipes[1]);
    fclose($pipes[2]);
    proc_close($redisListener);
    preg_match_all('/\[\d+\] => ([^ ]+)/', $outputBuffer, $matches);
    $output_buffer_tab = $matches[1];
    foreach ($output_buffer_tab as $key => $value) {
        $value = preg_replace('/[^0-9-]+$/', '', $value);
        echo "<label class='checkbox-button'>
                <input type='checkbox' id='$value' value='$value'>
                <span>$value</span>
              </label>";
    }
    echo "<br><div id='start-container'>";
    echo "<button class='start' id='?process_csv=$date'>Start scraping</button>";
    echo "</div>";
}

if (isset($_REQUEST['process_csv'])) {
    $data = addslashes($_REQUEST['process_csv']);
    $date = $_SESSION['date'];

    // Extraire la partie entre crochets
    preg_match('/\[(.*?)\]/', $data, $matches);
    if (isset($matches[1])) {
        $link_2 = explode(",", $matches[1]);
    } else {
        $link_2 = [];
    }

    // Logs pour déboguer
    // error_log("Date: " . $date);
    // error_log("Link_2: " . json_encode($link_2));

    $response = call_airflow_api('/dags/process_csv_workflow/dagRuns', 'POST', [
        'conf' => ['link_1' => $date, 'link_2' => $link_2]
    ]);

    // if ($response) {
    //     $dag_run_id = $response['dag_run_id'];
    //     echo "DAG déclenché avec l'ID de run: $dag_run_id";
    // } else {
    //     echo "Erreur : Échec de la création du DAG run pour le traitement CSV.";
    // }
}

// if (isset($_REQUEST['date'])) {
//     $year = addslashes($_REQUEST['year']);
//     $response = call_airflow_api('/dags/scraping_workflow/dagRuns', 'POST', [
//         'conf' => ['year' => $year]
//     ]);

//     if ($response) {
//         $dag_run_id = $response['dag_run_id'];
//         $_SESSION['dag_run_id'] = $dag_run_id;

//         // Attendre que le DAG soit terminé (vous pouvez ajuster le délai d'attente selon vos besoins)
//         sleep(10);

//         // Récupérer les résultats des XComs pour 'select_year'
//         $filtered_links = get_xcom_value('scraping_workflow', $dag_run_id, 'select_year', 'filtered_links');
//         $filtered_links_value = str_replace("'", '"', $filtered_links['value']);
//         $dates = json_decode($filtered_links_value, true);
//         if ($filtered_links) {
//             foreach ($dates as $value) {
//                 echo "<button class='date' id='?date=$value'>$value</button>";
//             }
//         } else {
//             echo "Erreur : Les données du DAG ne sont pas disponibles.";
//         }
//     } else {
//         echo "Erreur : Échec de la création du DAG run.";
//     }
// }

// // Récupérer les résultats des XComs pour 'select_link_1'
// if (isset($_REQUEST['date'])) {
//     $date = addslashes($_REQUEST['date']);
//     $_SESSION['date'] = $date;

//     $dag_run_id = $_SESSION['dag_run_id'];

//     $filtered_links_2 = get_xcom_value('scraping_workflow', $dag_run_id, 'select_link_1', 'filtered_links_2');

//     if ($filtered_links_2) {
//            foreach ($filtered_links_2['value'] as $value) {
//             echo "<label class='checkbox-button'>
//                     <input type='checkbox' id='$value' value='$value'>
//                     <span>$value</span>
//                   </label>";
//         }
//         echo "<br><div id='start-container'>";
//         echo "<button class='start' id='?process_csv=$date'>Start scraping</button>";
//     } else {
//         echo "Erreur : Les données du DAG ne sont pas disponibles.";
//     }
// }

// // Déclencher le DAG avec la variable 'process_csv'