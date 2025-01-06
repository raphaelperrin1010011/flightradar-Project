<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flightradar Project</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <div id="main-content">
        <div id="map"></div>
        <div class="menu" id="menu">
            <div id="welcome" style="display: none">
                <p>Welcome, no data detect in your database, please select a dataset to scrap</p>
                <br>
                <div class="container-datasets">
                    <div class="datasets" id="datasets">
                        <button class="year" id="?year=2017">2017</button>
                        <button class="year" id="?year=2018">2018</button>
                        <button class="year" id="?year=2019">2019</button>
                        <button class="year" id="?year=2020">2020</button>
                        <button class="year" id="?year=2021">2021</button>
                        <button class="year" id="?year=2022">2022</button>
                    </div>
                </div>
                <br>
            </div>
            <p id="progress-bar-text" style="display: none">Scraping in progress...</p>
            <div class='progress-bar' style='display: none' id='progressBar'>
                <div class='progress-bar-inner' id='progressBarInner'>0%</div>
            </div>
            <div id="ready" style='display: none; height: 100%'>
                <p>Please select an action</p>
                <br>
                <div class="button-container" id="playButton"> 
                    <button>
                        <img src="assets/plane.png" alt="Avion" style="width: 60%; height: 60%;">
                    </button>
                </div>
                <div class="button-container" id="streamButton">
                    <button>
                        <svg width="80%" height="80%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M23 7L16 12L23 17V7Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <rect x="1" y="5" width="15" height="14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div id="videoplayer" style="display: none">
                <video id="video" controls>
                    <source src="shared/europe_timelapse.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            <div id="regionModal" class="modal">
                <div class="modal-content">
                    <span class="close">&times;</span>
                    <h2>Choose a region</h2>
                    <button id="asiaButton">Asia</button>
                    <button id="europeButton">Europe</button>
                    <button id="usaButton">USA</button>
                </div>
            </div>
        </div>
        <div id="dateDisplay" style="display: none"></div>
        <div id="controls" style="display: none">
            <label for="speedRange">Speed :</label>
            <input type="range" id="speedRange" min="1" max="10" value="1">
        </div>
        <div id="sidebar" class="sidebar">
            <div id="sidebarContent" class="sidebar-content">
            </div>
        </div>
        <div class="container" id="altitude-container" style="display: none;">
            <!-- Échelle à gauche, en dehors du conteneur mais maintenant à l'intérieur -->
            <div class="scale" id="scaleContainer"></div>
            
            <!-- Conteneur de l'altitude avec la barre -->
            <div class="altitude-container">
                <div class="altitude-bar" id="altitudeBar"></div>
                <div class="altitude-text" id="altitudeText">0 ft</div>
            </div>
        </div>
    </div>
    </div>

    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    <script src="assets/leaflet.rotatedMarker.js"></script>
    <script src="assets/script.js"></script>
</body>
</html>
