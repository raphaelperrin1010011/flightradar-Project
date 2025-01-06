click = 0;
var region_global = null;
i = 0;

let stopChecking = false;

async function checkVideo(region) {
    while (!stopChecking) {
        console.log('En attente de la vidéo...');
        await $.get('stream.php?region=' + region, function(response, status, xhr) {
            console.log(status);
            console.log(response);
            if (status === "success") {
                jQuery('#videoplayer').empty().html(response);
                video = document.getElementById('video');
                video.addEventListener('canplaythrough', function() {
                    stopChecking = true;
                    console.log('La vidéo est prête à être visionnée.');
                });
            }
        });
        await new Promise(resolve => setTimeout(resolve, 1000)); // Attendre 100 ms
    }
}

function updateProgressBar(region = region_global) {
    if (region){
        fetch(`process_vid.php?region=${region}`)
        .then(response => response.json())
        .then(data => {
            const progressBarInner = document.getElementById('progressBarInner');
            progressBarInner.style.width = data.progress + '%';
            progressBarInner.textContent = Math.round(data.progress) + '%';
            if (data.progress >= 100) {
                progressBarInner.style.width = '100%';
                progressBarInner.textContent = '100%';
                jQuery('#progressBar').hide();
                jQuery('#progress-bar-text').hide();
                video = document.getElementById('video');
                canPlayThroughTriggered = false;
                video.addEventListener('canplaythrough', function() {
                    canPlayThroughTriggered = true;
                    console.log('La vidéo est prête à être visionnée.');
                });
                if (!canPlayThroughTriggered) {
                    checkVideo(region);
                }
                jQuery('#videoplayer').show('slow');
                console.log(`Chargement de la vidéo pour la région: ${region}`);
                modal.style.display = 'none';
                region_global = null;
                i = 0;
            } else {
                if (i == 0){
                    jQuery('#progressBar').show('slow');
                    jQuery('#progress-bar-text').text(`Processing video of ${region_global}`).show('slow');
                    i = 1;
                }
                setTimeout(updateProgressBar, 100);
            }
        })
        .catch(error => console.error('Error fetching progress:', error));
    } else {
        fetch('progress.php')
        .then(response => response.json())
        .then(data => {
            const progressBarInner = document.getElementById('progressBarInner');
            progressBarInner.style.width = data.progress + '%';
            progressBarInner.textContent = Math.round(data.progress) + '%';
            if (data.progress >= 100) {
                progressBarInner.style.width = '100%';
                progressBarInner.textContent = '100%';
                jQuery('#progressBar').hide();
                jQuery('#progress-bar-text').hide();
                jQuery('#ready').show('slow');
            } else {
                setTimeout(updateProgressBar, 1000);
            }
        })
        .catch(error => console.error('Error fetching progress:', error));
    }
}

function check(region) {
    if (region){
        console.log(region);
        fetch(`process_vid.php?region=${region}`)
        .then(response => response.json())
        .then(data => {
            if (data.progress < 100 && data.progress >= 0) {
                jQuery('#ready').hide();
                jQuery('#progressBar').show('slow');
                jQuery('#progress-bar-text').text(`Processing video of ${region}`).show('slow');
                updateProgressBar();
            } else {
                region_global = null;
                jQuery('#progressBar').hide();
                jQuery('#progress-bar-text').hide();
                jQuery('#ready').show();
            }
        })
    } else {
        fetch('progress.php')
            .then(response => response.json())
            .then(data => {
                if (data.progress < 100 && data.progress > 0) {
                    jQuery('#progressBar').show('slow');
                    jQuery('#progress-bar-text').show('slow');
                    updateProgressBar();
                } else if (data.progress >= 100) {
                    jQuery('#ready').show();
                    
                } else {
                    jQuery('#welcome').show();
                }
            })
    }
}

function fetch_region() {
    return fetch(`process_vid.php`)
    .then(response => response.json())
    .then(data => {
        if (data.region) {
            return data.region;
        } else {
            return null;
        }
    });
}

$(document).ready(function() {
    fetch_region().then(region => {
        console.log(region);
        region_global = region;
        check(region);
    });

    $(document).on('click', '.year', function() {
        console.log('click');
        $('.year').hide();
        $(document).off('click', '.year');
        
        var route = $(this).attr('id');
        
        jQuery('#datasets').load('scraping.php' + route);
    });
    
    $(document).on('click', '.date', function() {
        $(document).off('click', '.date');
        var route = $(this).attr('id');

        url = 'scraping.php' + route;
        $.get(url, function(response, status, xhr) {
            console.log(status);
            if (status === "success") {
               console.log(response);
                
               jQuery('#datasets').html(response.split('<br>')[0]);
               jQuery('#menu').append(response.split('<br>')[1]);
            } else if (status === "error") {
                console.error("Erreur lors du chargement du contenu : " + xhr.status + " " + xhr.statusText);
            }
        });
    });
    
    $(document).on('click', '.start', function() {
        $(document).off('click', '.start');
        var route = $(this).attr('id');
        var checked = [];
        
        $('#datasets input:checked').each(function() {
            checked.push($(this).attr('id'));
        });
        
        route = route + "[" + checked + "]";
        
        jQuery('#start-container').hide();
        jQuery('#datasets').load('scraping.php' + route);
        jQuery('#welcome').hide()
        jQuery('#progressBar').show('slow');
        jQuery('#progress-bar-text').show('slow');
        updateProgressBar();
    });

    $(document).on('click', '.checkbox-button input[type="checkbox"]', function() {
        let checked = [];
        
        // Récupérer tous les IDs des cases à cocher sélectionnées
        $('.checkbox-button input[type="checkbox"]:checked').each(function() {
            checked.push(parseInt($(this).attr('id')));
        });

        // Trier les IDs pour vérifier la séquence
        checked.sort((a, b) => a - b);

        // Vérifier si les IDs sont consécutifs à refaire
        // Vérifier si les IDs sont consécutifs
        // Vérifier si les IDs sont consécutifs
        // Vérifier si les IDs sont consécutifs
        for (let i = 1; i < checked.length; i++) {
            if (checked[i] !== checked[i - 1] + 1) {
                alert('Les cases à cocher doivent être consécutives.');
                $(this).prop('checked', false);
                return;
            }
        }
    }); 
});

let map = L.map('map', {
    center: [48.8566, 2.3522],
    zoom: 6,
    zoomControl: false, // Désactiver le contrôle de zoom
    scrollWheelZoom: false, // Désactiver le zoom avec la molette de la souris
    doubleClickZoom: false, // Désactiver le zoom avec le double-clic
    boxZoom: false, // Désactiver le zoom avec la boîte de sélection
    keyboard: false, // Désactiver le zoom avec le clavier
    // dragging: false, // Désactiver le déplacement de la carte
    maxBounds: [
        [-90, -180], // Sud-Ouest
        [90, 180]    // Nord-Est
    ],
    maxBoundsViscosity: 1.0 // Rendre les limites strictes
});

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

let planeIcon = L.icon({
    iconUrl: 'assets/plane.png',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
    popupAnchor: [0, -10]
});

let markers = {};
let selectedIcao24 = null; // Variable pour stocker l'ICAO24 de l'avion sélectionné
const playButton = document.getElementById('playButton');
const airplane = document.getElementById('airplane');
const speedRange = document.getElementById('speedRange');

let baseIntervalTime = 10000; // Intervalle de base de 10 secondes
let intervalTime = baseIntervalTime; // Intervalle initial

speedRange.addEventListener('input', () => {
    let speedFactor = speedRange.value;
    intervalTime = baseIntervalTime / speedFactor;
    updateDateDisplaySpeed(speedFactor);
});

function updateDateDisplaySpeed(speedFactor) {
    let dateDisplay = document.getElementById('dateDisplay');
    let currentText = dateDisplay.textContent.split(' | ')[0]; // Garder seulement la date
    dateDisplay.textContent = `${currentText} | Speed: x${speedFactor}`;
}

const streamButton = document.getElementById('streamButton');
const modal = document.getElementById('regionModal');
const closeModal = document.getElementsByClassName('close')[0];
const asiaButton = document.getElementById('asiaButton');
const europeButton = document.getElementById('europeButton');
const usaButton = document.getElementById('usaButton');

streamButton.addEventListener('click', () => {
    modal.style.display = 'block';
});

closeModal.addEventListener('click', () => {
    modal.style.display = 'none';
});

window.addEventListener('click', (event) => {
    if (event.target == modal) {
        modal.style.display = 'none';
    }
});

function updateProgress(region) {
    fetch(`set_0.php?region=${region}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log(data.message);
            } else {
                console.error(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
}

function loadVideo(region) {
    region_global = region;
    updateProgress(region);
    jQuery('#ready').hide();
    $.get('stream.php?region=' + region, function(response, status, xhr) {
        console.log(status);
        if (status === "success") {
            jQuery('#videoplayer').empty().html(response);
        }
    });
    updateProgressBar();
    console.log(`Chargement de la vidéo pour la région: ${region_global}`);
    modal.style.display = 'none';
}

asiaButton.addEventListener('click', () => loadVideo('asia'));
europeButton.addEventListener('click', () => loadVideo('europe'));
usaButton.addEventListener('click', () => loadVideo('usa'));

playButton.addEventListener('click', () => {
    let clickEnabled = true; // Variable pour suivre l'état de clic
    jQuery('#menu').hide('slow');
    jQuery('#dateDisplay').show();
    jQuery('#controls').show();
    let limit = 100; // Nombre de documents à récupérer par requête
    let lastTime = 0; // Time initial

    function fetchAndDisplayData() {
        fetch(`data.php?limit=${limit}&lastTime=${lastTime}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    console.error('Error from server:', data.error);
                    if (data.error.includes('Aucun vol trouvé')) {
                        console.log('Dataset is empty, restarting from the beginning...');
                        lastTime = 0; // Réinitialiser le dernier time à zéro
                        fetchAndDisplayData();
                        return;
                    }
                }

                // Vérifier si les données sont vides
                if (!data.data || data.data.length === 0) {
                    console.log('No more data available, restarting from the beginning...');
                    lastTime = 0; // Réinitialiser le dernier time à zéro
                    fetchAndDisplayData(); 
                    return;
                }

                // Grouper les données par time
                let groupedData = data.data.reduce((acc, flight) => {
                    let time = flight.time;
                    if (!acc[time]) {
                        acc[time] = [];
                    }
                    acc[time].push(flight);
                    return acc;
                }, {});

                let times = Object.keys(groupedData).sort((a, b) => a - b);
                let index = 0;

                function displayNextBatch() {
                    if (index >= times.length) {
                        lastTime = data.lastTime; // Mettre à jour le dernier time
                        fetchAndDisplayData(); // Récupérer et afficher le lot suivant
                        return;
                    }

                    let currentTime = times[index];
                    let flights = groupedData[currentTime];

                    // Mettre à jour l'affichage de la date
                    let dateDisplay = document.getElementById('dateDisplay');
                    let date = new Date(currentTime * 1000); // Convertir le timestamp en millisecondes
                    let speedFactor = speedRange.value;
                    dateDisplay.textContent = `${date.toLocaleString()} | Speed: x${speedFactor}`; // Afficher la date et l'accélération

                    flights.forEach(flight => {
                        if (markers[flight.icao24]) {
                            // Déplacer et orienter le marqueur existant
                            markers[flight.icao24].setLatLng([flight.lat, flight.lon]);
                            if (flight.heading !== null) {
                                markers[flight.icao24].setRotationAngle((flight.heading - 45 + 360) % 360); // Appliquer la correction de -45 degrés
                            }
                        } else {
                            // Créer un nouveau marqueur avec orientation
                            let marker = L.marker([flight.lat, flight.lon], {
                                icon: planeIcon,
                                rotationAngle: flight.heading !== null ? (flight.heading - 45 + 360) % 360 : 0 // Utiliser la valeur de heading avec correction si disponible
                            }).addTo(map);
                    
                            markers[flight.icao24] = marker;

                            // Ajouter un événement de clic pour afficher le parcours
                            marker.on('click', () => {
                                if (clickEnabled) {
                                    clickEnabled = false; // Désactiver les clics
                                    fetchFlightPath(flight.icao24, currentTime);
                                    showSidebar(flight);
                                    selectedIcao24 = flight.icao24; // Mettre à jour l'ICAO24 de l'avion sélectionné
                                    setTimeout(() => {
                                        clickEnabled = true; // Réactiver les clics après 3 secondes
                                    }, 10000);
                                }
                            });
                        }

                        // Mettre à jour les informations de l'avion sélectionné dans le menu latéral
                        if (flight.icao24 === selectedIcao24) {
                            updateSidebar(flight);
                        }
                    });

                    index++;
                    setTimeout(displayNextBatch, intervalTime); // Utiliser l'intervalle dynamique
                }

                displayNextBatch(); // Appeler immédiatement pour afficher les données
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                // Réinitialiser les variables et recommencer depuis le début en cas d'erreur
                lastTime = 0;
                fetchAndDisplayData();
            });
    }

    fetchAndDisplayData(); // Initial call to fetch and display data
});

let currentPolyline = null;
let animatedMarkers = [];

function fetchFlightPath(icao24, currentTime) {
    fetch(`flight_path.php?icao24=${icao24}&currentTime=${currentTime}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error('Error from server:', data.error);
                return;
            }

            if (!Array.isArray(data.path) || data.path.length < 2) {
                console.log('Not enough path data available to draw a polyline');
                console.log('Logs:', data.logs); // Journaliser les logs d'erreur
                return; // Arrêter si moins de deux points sont retournés
            }

            // Supprimer la polyline actuelle si elle existe
            if (currentPolyline) {
                map.removeLayer(currentPolyline);
            }

            // Supprimer les marqueurs animés actuels s'ils existent
            animatedMarkers.forEach(marker => map.removeLayer(marker));
            animatedMarkers = [];

            // Tracer le parcours de l'avion
            let latlngs = data.path.map(point => [point.lat, point.lon]);
            currentPolyline = L.polyline(latlngs, { color: 'rgba(255, 0, 0, 0.4)', className: 'glowing-polyline' }).addTo(map);

        })
        .catch(error => console.error('Error fetching flight path:', error));
}

function showSidebar(flight) {
    click = 1;
    const sidebar = document.getElementById('sidebar');
    const sidebarContent = document.getElementById('sidebarContent');
    jQuery('#altitude-container').show('slow');
    // Remplir le contenu du menu latéral avec les informations de l'avion
    sidebarContent.innerHTML = `
        <h2>Aircraft data:</h2><br>
        <div id="loading">
            <div class="spinner"></div>
        </div>
        <div id="aircraftImage" style="text-align: center;"></div>
        <br>
        <p><strong>CallSign:</strong><br> ${flight.callsign}</p><br>
        <p><strong>ICAO24:</strong><br> ${flight.icao24}</p><br>
        <p><strong>Latitude:</strong><br> ${flight.lat}</p><br>
        <p><strong>Longitude:</strong><br> ${flight.lon}</p><br>
        <p><strong>Time:</strong><br> ${new Date(flight.time * 1000).toLocaleString()}</p><br>
        <p><strong>Velocity:</strong><br> ${flight.velocity !== null ? flight.velocity : 'N/A'}</p><br>
        <p><strong>Heading:</strong><br> ${flight.heading !== null ? flight.heading : 'N/A'}</p><br>
        <p><strong>Vertical Rate:</strong><br> ${flight.vertrate !== null ? flight.vertrate : 'N/A'}</p><br>
        <p><strong>Barometric Altitude:</strong><br> ${flight.baroaltitude !== null ? flight.baroaltitude : 'N/A'}</p><br>
        <p><strong>Geometric Altitude:</strong><br> ${flight.geoaltitude !== null ? flight.geoaltitude : 'N/A'}</p><br>
        <p><strong>Last Position Update:</strong><br> ${flight.lastposupdate !== null ? new Date(flight.lastposupdate * 1000).toLocaleString() : 'N/A'}</p><br>
        <p><strong>Last Contact:</strong><br> ${flight.lastcontact !== null ? new Date(flight.lastcontact * 1000).toLocaleString() : 'N/A'}</p><br>
        <a href="javascript:void(0)" class="closebtn" onclick="closeSidebar()">&times;</a>
    `;

    if (flight.baroaltitude !== null) {
        updateAltitude(flight.baroaltitude);
    }

    // Afficher le menu latéral
    sidebar.style.width = '250px';

    // Charger l'image de l'avion
    loadAircraftImage(flight.icao24);
}

// Créer un objet de cache pour stocker les images récupérées
const aircraftImageCache = {};

function updateSidebar(flight) {
    const sidebarContent = document.getElementById('sidebarContent');

    // Mettre à jour le contenu du menu latéral avec les informations de l'avion
    sidebarContent.innerHTML = `
        <h2>Aircraft data:</h2><br>
        <div id="loading">
            <div class="spinner"></div>
        </div>
        <div id="aircraftImage" style="text-align: center;"></div>
        <br>
        <p><strong>CallSign:</strong><br> ${flight.callsign}</p><br>
        <p><strong>ICAO24:</strong><br> ${flight.icao24}</p><br>
        <p><strong>Latitude:</strong><br> ${flight.lat}</p><br>
        <p><strong>Longitude:</strong><br> ${flight.lon}</p><br>
        <p><strong>Time:</strong><br> ${new Date(flight.time * 1000).toLocaleString()}</p><br>
        <p><strong>Velocity:</strong><br> ${flight.velocity !== null ? flight.velocity : 'N/A'}</p><br>
        <p><strong>Heading:</strong><br> ${flight.heading !== null ? flight.heading : 'N/A'}</p><br>
        <p><strong>Vertical Rate:</strong><br> ${flight.vertrate !== null ? flight.vertrate : 'N/A'}</p><br>
        <p><strong>Barometric Altitude:</strong><br> ${flight.baroaltitude !== null ? flight.baroaltitude : 'N/A'}</p><br>
        <p><strong>Geometric Altitude:</strong><br> ${flight.geoaltitude !== null ? flight.geoaltitude : 'N/A'}</p><br>
        <p><strong>Last Position Update:</strong><br> ${flight.lastposupdate !== null ? new Date(flight.lastposupdate * 1000).toLocaleString() : 'N/A'}</p><br>
        <p><strong>Last Contact:</strong><br> ${flight.lastcontact !== null ? new Date(flight.lastcontact * 1000).toLocaleString() : 'N/A'}</p><br>
        <a href="javascript:void(0)" class="closebtn" onclick="closeSidebar()">&times;</a>
    `;
    if (flight.baroaltitude !== null) {
        updateAltitude(flight.baroaltitude);
    }
        // Charger l'image de l'avion
    loadAircraftImage(flight.icao24);
}

let isRequestInProgress = false; // Variable d'état pour suivre si une requête est en cours

function loadAircraftImage(icao24) {
    const imageContainer = document.getElementById('aircraftImage');
    const loadingIndicator = document.getElementById('loading');

    // Vérifier si une requête est déjà en cours
    if (isRequestInProgress) {
        console.log('Une requête est déjà en cours, veuillez patienter.');
        return;
    }

    // Vérifier si l'image est déjà dans le cache
    if (aircraftImageCache[icao24]) {
        // Masquer l'indicateur de chargement
        loadingIndicator.style.display = 'none';

        // Utiliser l'image depuis le cache
        imageContainer.innerHTML = aircraftImageCache[icao24];
    } else {
        // Afficher l'indicateur de chargement
        loadingIndicator.style.display = 'block';

        // Marquer qu'une requête est en cours
        isRequestInProgress = true;

        // Envoyer une requête AJAX pour obtenir l'image de l'avion
        fetch(`image.php?icao=${icao24}`)
            .then(response => response.text())
            .then(data => {
                // Masquer l'indicateur de chargement
                loadingIndicator.style.display = 'none';

                // Stocker l'image dans le cache
                aircraftImageCache[icao24] = data;

                // Afficher l'image de l'avion
                imageContainer.innerHTML = data;
            })
            .catch(error => {
                console.error('Error fetching aircraft image:', error);
                loadingIndicator.style.display = 'none';
                imageContainer.innerHTML = '<p>Erreur lors du chargement de l\'image.</p>';
            })
            .finally(() => {
                // Marquer que la requête est terminée
                isRequestInProgress = false;
            });
    }
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.style.width = '0';
    selectedIcao24 = null; // Réinitialiser l'ICAO24 de l'avion sélectionné
    jQuery('#altitude-container').hide('slow');
    click = 0;
}






//altitude et vitesse

const altitudeBar = document.getElementById('altitudeBar');
const altitudeText = document.getElementById('altitudeText');
const scaleContainer = document.getElementById('scaleContainer');

const maxAltitude = 15000; // Altitude max visible sur l'échelle (pieds)
let altitude = 0; // Altitude de départ

// Fonction pour ajuster la hauteur de la barre et le texte
function updateAltitude(altitude) {
    const barHeight = (altitude / maxAltitude) * 100; // Calcul de la hauteur en %
    altitudeBar.style.height = barHeight + '%';
    altitudeText.textContent = altitude.toFixed(0) + ' ft';
    // Ajuster la position du texte
    altitudeText.style.bottom = (barHeight - 15) + '%'; // Place le texte un peu plus bas
}

function generateScale(maxAltitude) {
    for (let i = maxAltitude; i >= 0; i -= 1500) {
        const tick = document.createElement('div');
        tick.classList.add('tick');
        tick.textContent = i + ' ft';
        scaleContainer.appendChild(tick);
    }
}

generateScale(maxAltitude);