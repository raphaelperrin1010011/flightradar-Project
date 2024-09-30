<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flight Density Map Stream</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 100vh;
            background-color: #f0f0f0;
        }
        #canvasElement {
            max-width: 100%;
            max-height: 100%;
            width: auto;
            height: auto;
            z-index: 1000;
            background-color: black;
        }
    </style>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    <canvas id="canvasElement"></canvas>
    <?php
    // Récupérer le paramètre 'region' de l'URL
    $region = isset($_GET['region']) ? $_GET['region'] : 'world';
    // Envoyer au JS
    echo "<script>const region = '$region';</script>";
    ?>
    <script>
        const canvas = document.getElementById('canvasElement');
        const ctx = canvas.getContext('2d');
        console.log(region);

        // URL de base pour récupérer les timestamps et les images
        const baseUrl = 'stream_video.php';

        // Fonction pour récupérer les timestamps
        function fetchTimestamps() {
            $.get(`${baseUrl}`, { region: region }, function(data) {
                const timestamps = data;
                displayImagesSequentially(timestamps);
            });
        }

        // Fonction pour afficher les images en séquence
        function displayImagesSequentially(timestamps) {
            let index = 0;
            let skipFirstImage = 1;

            function displayNextImage() {
                if (index < timestamps.length) {
                    const timestamp = timestamps[index];
                    const imageUrl = `${baseUrl}?region=${region}&time=${timestamp}`;
                    const img = new Image();
                    img.onload = function() {
                        if (skipFirstImage) {
                            skipFirstImage = false; // Ignorer la première image
                            index++;
                            displayNextImage();
                        } else {
                            canvas.width = 1920;
                            canvas.height = 1080;
                            ctx.drawImage(img, 0, 0);
                            console.log('Image affichée pour timestamp:', timestamp);
                            index++;
                            setTimeout(displayNextImage, 1000); // Délai de 1 seconde entre chaque image
                        }
                    }
                    img.onerror = function() {
                        console.log('Erreur de chargement de l\'image pour timestamp:', timestamp);
                        index++;
                        displayNextImage(); // Passer à l'image suivante en cas d'erreur
                    }
                    img.src = imageUrl;
                    console.log('Chargement de l\'image:', img.src);
                }
            }

            displayNextImage();
        }

        fetchTimestamps();
    </script>
</body>
</html>