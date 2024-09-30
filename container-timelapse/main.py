from fastapi import FastAPI, Response, Request
from fastapi.responses import StreamingResponse
import os
import asyncio
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
progress = db['progress']

stop_streaming_flag = False

def fetch_flight_data(region, skip, limit=100000):
    query = {"baroaltitude": {"$gte": 100}}  # Filtrer les avions avec baroaltitude >= 100
    if region == "europe":
        query.update({"lon": {"$gte": -10, "$lte": 30}, "lat": {"$gte": 35, "$lte": 70}})
    elif region == "usa":
        query.update({"lon": {"$gte": -130, "$lte": -60}, "lat": {"$gte": 25, "$lte": 50}})
    elif region == "asia":
        query.update({"lon": {"$gte": 60, "$lte": 150}, "lat": {"$gte": 0, "$lte": 60}})
    elif region == "world":
        query.update({"lon": {"$gte": -180, "$lte": 180}, "lat": {"$gte": -90, "$lte": 90}})
    flights = collection.find(query).skip(skip).limit(limit)
    return pd.DataFrame(list(flights))

def get_batch_data(region, skip=0, limit=100000):
    return fetch_flight_data(region, skip, limit)

def create_density_map(df, title, timestamp):
    fig, ax = plt.subplots(figsize=(19.2, 10.8), subplot_kw={'projection': ccrs.Mercator()})
    
    # Ajuster les marges pour maximiser l'espace de la figure
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    ax.add_feature(cfeature.LAND)
    ax.add_feature(cfeature.OCEAN)
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')

    in_crs = CRS.from_epsg(4326)
    out_crs = CRS.from_epsg(3857)
    transformer = Transformer.from_crs(in_crs, out_crs, always_xy=True)
    
    df = df.copy()
    df.loc[:, 'x'], df.loc[:, 'y'] = transformer.transform(df['lon'].values, df['lat'].values)

    sns.kdeplot(x=df['x'], y=df['y'], cmap='plasma', fill=True, bw_adjust=0.5, ax=ax, alpha=0.3, warn_singular=False)
    ctx.add_basemap(ax, crs=ccrs.Mercator(), source=ctx.providers.Esri.WorldImagery, zoom=5)
    ax.scatter(df['x'], df['y'], color='white', s=1, alpha=0.6, transform=ccrs.Mercator())

    logging.info(local_tz)
    readable_timestamp = datetime.fromtimestamp(timestamp, local_tz).strftime('%Y-%m-%d %H:%M:%S')
    plt.title(f"{title}\n{readable_timestamp}")

    # Supprimer les bordures et les ticks des axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)

    buf = BytesIO()
    plt.savefig(buf, format='jpeg', dpi=100, bbox_inches='tight', pad_inches=0)
    plt.close()
    buf.seek(0)
    return buf

@app.get("/get_image")
async def get_image(region: str, time: int, request: Request):
    logging.info(region)
    batch_data = get_batch_data(region)
    grouped_data = batch_data.groupby('time')
    logging.info(f"Grouped data by timestamp, found {len(grouped_data.groups)} unique timestamps")
    
    if time in grouped_data.groups:
        logging.info(f"Timestamp {time} found in data")
        group = grouped_data.get_group(time)
        buf = create_density_map(group, f"{region.capitalize()} - ", time)
        img = Image.open(buf)

        jpeg_buffer = BytesIO()
        img.save(jpeg_buffer, format="JPEG")
        jpeg_buffer.seek(0)

        return StreamingResponse(jpeg_buffer, media_type="image/jpeg")
    else:
        logging.error(f"Timestamp {time} not found in data")
        return {"error": "Timestamp not found"}

@app.post("/stop_streaming")
async def stop_streaming():
    global stop_streaming_flag
    stop_streaming_flag = True
    logging.info("Streaming stopped by client request")
    return {"message": "Streaming stopped"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)