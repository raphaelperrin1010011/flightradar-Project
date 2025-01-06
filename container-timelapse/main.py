from fastapi import FastAPI, Response, Request, HTTPException
from fastapi.responses import StreamingResponse
import os
from io import BytesIO
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import contextily as ctx
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pyproj import CRS, Transformer
from pymongo import MongoClient
import logging
import pytz
from datetime import datetime
import time
import uvicorn
import subprocess
import psutil
import gc
import shutil

# Obtenir le décalage UTC en secondes
utc_offset_sec = time.localtime().tm_gmtoff

# Convertir le décalage en heures
utc_offset_hours = utc_offset_sec / 3600

# Obtenir le fuseau horaire correspondant
local_tz = pytz.timezone(time.tzname[0])
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI()

client = MongoClient('mongodb://mongodb:27017/')
db = client['opensky']
collection = db['flights']
process_vid = db['process_vid']

def log_memory_usage():
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    logging.info(f"Memory usage: RSS={mem_info.rss / 1024 ** 2:.2f} MB, VMS={mem_info.vms / 1024 ** 2:.2f} MB")

def get_batch_data(region, timestamp, skip=0, limit=10000):
    start_time = time.time()
    query = {
        "baroaltitude": {"$gte": 100},  # Filtrer les avions avec baroaltitude >= 100
        "time": timestamp
    }
    if region == "europe":
        query.update({"lon": {"$gte": -10, "$lte": 30}, "lat": {"$gte": 35, "$lte": 70}})
    elif region == "usa":
        query.update({"lon": {"$gte": -130, "$lte": -60}, "lat": {"$gte": 25, "$lte": 50}})
    elif region == "asia":
        query.update({"lon": {"$gte": 60, "$lte": 150}, "lat": {"$gte": 0, "$lte": 60}})
    
    flights = collection.find(query).skip(skip).limit(limit)
    df = pd.DataFrame(list(flights))
    end_time = time.time()
    logging.info(f"get_batch_data: {end_time - start_time:.2f} seconds")
    return df

def get_unique_timestamps(region):
    start_time = time.time()
    query = {"baroaltitude": {"$gte": 100}}  # Filtrer les avions avec baroaltitude >= 100
    if region == "europe":
        query.update({"lon": {"$gte": -10, "$lte": 30}, "lat": {"$gte": 35, "$lte": 70}})
    elif region == "usa":
        query.update({"lon": {"$gte": -130, "$lte": -60}, "lat": {"$gte": 25, "$lte": 50}})
    elif region == "asia":
        query.update({"lon": {"$gte": 60, "$lte": 150}, "lat": {"$gte": 0, "$lte": 60}})
    
    timestamps = collection.distinct("time", query)
    end_time = time.time()
    logging.info(f"get_unique_timestamps: {end_time - start_time:.2f} seconds")
    return sorted(timestamps)

def create_density_map(region, df, title, timestamp, image_path):
    start_time = time.time()
    
    # Définir les proportions de la figure en fonction de la région
    if region == "europe":
        figsize = (12, 8)
        fixed_size = (1200, 800)
    elif region == "usa":
        figsize = (12, 8)
        fixed_size = (1200, 800)
    elif region == "asia":
        figsize = (12, 8)
        fixed_size = (1200, 800)
    
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.Mercator()})
    logging.info(f"create_density_map: plt.subplots took {time.time() - start_time:.2f} seconds")
    
    regions = {
        "europe": {"lon": (-20, 40), "lat": (30, 75)},
        "usa": {"lon": (-140, -50), "lat": (20, 55)},
        "asia": {"lon": (50, 160), "lat": (-10, 70)}
    }

    lon_min, lon_max = regions[region]["lon"]
    lat_min, lat_max = regions[region]["lat"]

    # Ajuster les marges pour maximiser l'espace de la figure
    start_time = time.time()
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    logging.info(f"create_density_map: plt.subplots_adjust took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    in_crs = CRS.from_epsg(4326)
    out_crs = CRS.from_epsg(3857)
    transformer = Transformer.from_crs(in_crs, out_crs, always_xy=True)
    extent = transformer.transform([lon_min, lon_max], [lat_min, lat_max])
    
    logging.info(f"create_density_map: CRS and Transformer setup took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    df = df.copy()
    df.loc[:, 'x'], df.loc[:, 'y'] = transformer.transform(df['lon'].values, df['lat'].values)
    logging.info(f"create_density_map: CRS transformation took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    logging.info(f"create_density_map: ax.add_feature took {time.time() - start_time:.2f} seconds")

    ax.set_extent([extent[0][0], extent[0][1], extent[1][0], extent[1][1]], crs=ccrs.Mercator())

    start_time = time.time()
    sns.kdeplot(x=df['x'], y=df['y'], cmap='plasma', fill=True, bw_adjust=0.3, ax=ax, alpha=0.3, warn_singular=False)
    logging.info(f"create_density_map: sns.kdeplot took {time.time() - start_time:.2f} seconds")
    
    start_time = time.time()
    ctx.add_basemap(ax, crs=ccrs.Mercator(), source=ctx.providers.Esri.WorldImagery, zoom=5)
    logging.info(f"create_density_map: ctx.add_basemap took {time.time() - start_time:.2f} seconds") 
    
    start_time = time.time()
    ax.scatter(df['x'], df['y'], color='white', s=1, alpha=0.6, transform=ccrs.Mercator())
    logging.info(f"create_density_map: ax.scatter took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    readable_timestamp = datetime.fromtimestamp(timestamp, local_tz).strftime('%Y-%m-%d %H:%M:%S')
    plt.title(f"{title}\n{readable_timestamp}")
    logging.info(f"create_density_map: plt.title took {time.time() - start_time:.2f} seconds")

    # Supprimer les bordures et les ticks des axes
    start_time = time.time()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    logging.info(f"create_density_map: ax.set_xticks and ax.spines took {time.time() - start_time:.2f} seconds")

    start_time = time.time()
    plt.savefig(image_path, format='jpeg', dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close()
    logging.info(f"create_density_map: plt.savefig and plt.close took {time.time() - start_time:.2f} seconds")

    # Redimensionner l'image pour qu'elle ait une taille fixe en fonction de la région
    try:
        with Image.open(image_path) as img:
            img = img.resize(fixed_size, Image.Resampling.LANCZOS)
            img.save(image_path)
            logging.info(f"Image resized to fixed size: {fixed_size}")
    except Exception as e:
        logging.error(f"Error resizing image: {e}")

    # Libérer la mémoire
    plt.clf()
    plt.close('all')
    gc.collect()

def update_progress(region, progress):
    process_vid.update_one(
        {"region": region},
        {"$set": {"progress": progress}},
    )
    logging.info(f"Progress updated for region: {region} to {progress}%")

def generate_images(region):
    # Créer le dossier images s'il n'existe pas
    if not os.path.exists('images'):
        os.makedirs('images')
        logging.info("Dossier 'images' créé")

    timestamps = get_unique_timestamps(region)
    total_timestamps = len(timestamps)
    
    logging.info(f"Région: {region}")
    for i, timestamp in enumerate(timestamps):  # Commencer l'indexation à 1
        skip = 0
        while True:
            df = get_batch_data(region, timestamp, skip=skip, limit=10000)
            logging.info(f"Taille de df: {df.shape}")
            log_memory_usage()
            if df.empty:
                break
            image_path = f"images/{region}_{i:08d}.jpg"
            create_density_map(region, df, f"{region.capitalize()} - ", timestamp, image_path)
            skip += 10000
        progress = int((i + 1) / total_timestamps * 99)
        update_progress(region, progress)
    
    # S'assurer que la progression est à 100% à la fin
    logging.info(f"Progress set to 100% for region: {region}")

def create_video_with_ffmpeg(region):
    start_time = time.time()
    generate_images(region)
    video_path = f"shared/{region}_timelapse.mp4"
    ffmpeg_command = [
        'ffmpeg', '-y', '-framerate', '30', '-start_number', '2', '-i', f'images/{region}_%08d.jpg',
        '-c:v', 'libx264', '-r', '30', '-pix_fmt', 'yuv420p', video_path 
    ]
    subprocess.run(ffmpeg_command, check=True)
    end_time = time.time()
    if os.path.exists(video_path):
        update_progress(region, 100)
        process_vid.update_one(
            {"region": region},
            {"$set": {"status": "completed"}}
        )
        logging.info(f"create_video_with_ffmpeg: {end_time - start_time:.2f} seconds")
        return video_path
    else:
        logging.error(f"Video file not found: {video_path}")
        return None

@app.on_event("startup")
async def on_startup():
    logging.info("Application started")
    shared_folder = "/app/shared" 
    
    # Supprimer le contenu du dossier shared
    for filename in os.listdir(shared_folder):
        file_path = os.path.join(shared_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logging.error(f"Failed to delete {file_path}. Reason: {e}")

    logging.info(f"Cleared contents of {shared_folder}")

@app.get("/generate_video")
async def generate_video(region: str, request: Request):
    video_path = f"shared/{region}_timelapse.mp4"  # Remplacez par le chemin correct

    # Vérifier si une vidéo est déjà en cours de génération pour cette région
    if os.path.exists(video_path):
        logging.info(f"Video already exists: {video_path}")
        return Response(content="Vidéo créée et déjà existante", status_code=200)
    else:
        process = process_vid.find_one({"region": region})
        if process and process.get("progress") == 0.1:
            start_time = time.time()
            video_path = create_video_with_ffmpeg(region)
            end_time = time.time()
            logging.info(f"generate_video: {end_time - start_time:.2f} seconds")