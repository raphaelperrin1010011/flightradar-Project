<?php
// Vérifier si le paramètre ICAO est présent dans la requête GET
if (isset($_GET['icao'])) {
    $icao = $_GET['icao'];
} else {
    echo 'Erreur: Aucun code ICAO fourni.';
    exit;
}

// URL de l'API FastAPI
$api_url = 'http://python-image-api:8200/get-aircraft-image/';

// Créer les données JSON pour la requête POST
$data = json_encode(array('icao' => $icao));

// Initialiser cURL
$ch = curl_init($api_url);

// Configurer les options cURL
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $data);

// Exécuter la requête cURL
$response = curl_exec($ch);

// Vérifier les erreurs cURL
if (curl_errno($ch)) {
    echo 'Erreur cURL: ' . curl_error($ch);
} else {
    // Décoder la réponse JSON
    $response_data = json_decode($response, true);

    // Vérifier si l'image URL est présente dans la réponse
    if (isset($response_data['image_url'])) {
        $image_url = $response_data['image_url'];
        echo '<img src="' . $image_url . '" alt="Aircraft Image">';
    } else {
		echo 'No image found for ICAO code ' . $icao;
    }
}


// Fermer la session cURL
curl_close($ch);


// Vérifier si le paramètre ICAO est présent dans la requête GET
// if (isset($_GET['icao'])) {

//     // URL de l'API Airflow pour déclencher le DAG
//     $api_url = 'http://airflow-webserver:8080/api/v1/dags/get_aircraft_image_workflow/dagRuns';

//     // Créer les données JSON pour la requête POST
//     $data = json_encode(array('conf' => array('icao' => $icao)));

//     // Initialiser cURL
//     $ch = curl_init($api_url);

//     // Configurer les options cURL
//     curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
//     curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json', 'Authorization: Basic ' . base64_encode('username:password')));
//     curl_setopt($ch, CURLOPT_POST, true);
//     curl_setopt($ch, CURLOPT_POSTFIELDS, $data);

//     // Exécuter la requête cURL
//     $response = curl_exec($ch);

//     // Vérifier les erreurs cURL
//     if (curl_errno($ch)) {
//         echo 'Erreur cURL: ' . curl_error($ch);
//     } else {
//         // Décoder la réponse JSON
//         $response_data = json_decode($response, true);

//         // Vérifier si le DAG a été déclenché avec succès
//         if (isset($response_data['dag_run_id'])) {
//             echo 'DAG déclenché avec succès. ID de l\'exécution du DAG: ' . $response_data['dag_run_id'];
//         } else {
//             echo 'Erreur lors du déclenchement du DAG.';
//         }
//     }

//     // Fermer la session cURL
//     curl_close($ch);
// }