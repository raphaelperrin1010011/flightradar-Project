<?php
// Vous pouvez ajouter une logique ici pour arrêter le streaming côté serveur si nécessaire
http_response_code(200);
echo json_encode(["message" => "Streaming stopped"]);