from io import BytesIO
from bs4 import BeautifulSoup
import gzip
import requests
import tarfile
import csv
import time
import logging
from pymongo import MongoClient
from typing import List
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
from typing import List

class LinkData(BaseModel):
    link_2: List[str]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client = MongoClient('mongodb://mongodb:27017/')
db = client['opensky']
collection = db['flights']
progress_collection = db['progress']

app = FastAPI()

def update_progress(progress):
    progress_collection.update_one({}, {"$set": {"progress": progress}}, upsert=True)

def convert_types(row):
    # Conversion des types pour chaque champ
    row['time'] = int(row['time']) if row['time'] else None
    row['icao24'] = str(row['icao24']) if row['icao24'] else None
    row['lat'] = float(row['lat']) if row['lat'] else None
    row['lon'] = float(row['lon']) if row['lon'] else None
    row['velocity'] = float(row['velocity']) if row['velocity'] else None
    row['heading'] = float(row['heading']) if row['heading'] else None
    row['vertrate'] = float(row['vertrate']) if row['vertrate'] else None
    row['callsign'] = str(row['callsign']).strip() if row['callsign'] else None
    row['onground'] = row['onground'].lower() in ['true', '1', 'yes'] if row['onground'] else None
    row['alert'] = row['alert'].lower() in ['true', '1', 'yes'] if row['alert'] else None
    row['spi'] = row['spi'].lower() in ['true', '1', 'yes'] if row['spi'] else None
    row['squawk'] = str(row['squawk']) if row['squawk'] else None
    row['baroaltitude'] = float(row['baroaltitude']) if row['baroaltitude'] else None
    row['geoaltitude'] = float(row['geoaltitude']) if row['geoaltitude'] else None
    row['lastposupdate'] = float(row['lastposupdate']) if row['lastposupdate'] else None
    row['lastcontact'] = float(row['lastcontact']) if row['lastcontact'] else None
    return row

@app.get("/filtered_links/{year}")
def get_filtered_links(year: str):
    response = requests.get("https://opensky-network.org/datasets/states")
    time.sleep(1)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")
    filtered_links = [link.get("href")[2:] for i, link in enumerate(links) if i % 4 == 0 and link.get("href")[2:].startswith(year)]
    return {"filtered_links": filtered_links}

@app.get("/filtered_links_2/{link_1}")
def get_filtered_links_2(link_1: str):
    response = requests.get(f"https://opensky-network.org/datasets/states/{link_1}")
    time.sleep(1)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a")
    filtered_links_2 = [link.get("href")[2:] for i, link in enumerate(links) if i % 4 == 0][1:]
    return {"filtered_links_2": filtered_links_2}

@app.post("/process_csv/{link_1}")
def process_csv(link_1: str, link_data: LinkData):
    total_steps = len(link_data.link_2) * 3  # Nombre total d'étapes
    current_step = 0
    update_progress(0.1)
    for link in link_data.link_2:
        try:
            response = requests.get(f"https://opensky-network.org/datasets/states/{link_1}/{link}")
            response.raise_for_status()
            time.sleep(1)
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("a")
            link_3 = [link.get("href")[2:] for i, link in enumerate(links) if i % 4 == 0][2:-1][0]
            time.sleep(1)
            response = requests.get(f"https://opensky-network.org/datasets/states/{link_1}/{link}/{link_3}")
            response.raise_for_status()
            time.sleep(1)
            tar_content = BytesIO(response.content)
            with tarfile.open(fileobj=tar_content, mode="r:*") as tar:
                for member in tar.getmembers():
                    if member.name.endswith(".csv.gz"):
                        f = tar.extractfile(member)
                        if f is not None:
                            with gzip.open(f, mode='rt') as gz:
                                csv_reader = csv.DictReader(gz)
                                rows = []
                                for row in csv_reader:
                                    converted_row = convert_types(row)
                                    if converted_row['lat'] is not None and converted_row['lon'] is not None and converted_row['time'] is not None:
                                        rows.append(converted_row)
                                collection.insert_many(rows)
                                logging.info(f"Inséré {len(rows)} lignes dans la base de données")
            current_step += 3
            update_progress(int((current_step / total_steps) * 100))
        except requests.exceptions.RequestException as e:
            logging.error(f"Erreur de requête: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur de requête: {e}")
        except tarfile.ReadError as e:
            logging.error(f"Erreur de lecture du fichier tar: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur de lecture du fichier tar: {e}")
        except Exception as e:
            logging.error(f"Erreur inattendue: {e}")
            raise HTTPException(status_code=500, detail=f"Erreur inattendue: {e}")
    return {"status": "success", "message": "CSV processed and data inserted into the database"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)

#curl -X GET "http://localhost:8100/filtered_links/2021"
#curl -X GET "http://localhost:8100/filtered_links_2/2021-11-01"
#curl -X POST "http://localhost:8100/process_csv/2021-11-01" -H "Content-Type: application/json" -d '{"link_2": ["00", "01", "02"]}'