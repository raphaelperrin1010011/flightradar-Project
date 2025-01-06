from playwright.async_api import async_playwright
import asyncio
import time
import re
import requests
import csv
import gzip
import tarfile
from io import BytesIO
import logging
from pymongo import MongoClient
from typing import List
from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

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

dates_save = None

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

async def get_all_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://opensky-network.org/datasets/#states/")
        await asyncio.sleep(0.1)

        all_hrefs = []

        while True:
            links = await page.query_selector_all('a.button.is-text.is-rounded')
            hrefs = [await link.get_attribute('href') for link in links]
            all_hrefs.extend(hrefs)
            print(all_hrefs)
            next_button = await page.query_selector('button.button.is-primary.is-rounded:has(i.fas.fa-angle-right)')
            if next_button:
                try:
                    if await next_button.is_visible() and await next_button.is_enabled():
                        await next_button.click(timeout=60000)
                        await asyncio.sleep(0.1)
                    else:
                        logging.info("Le bouton 'Suivant' n'est pas visible ou activé. fin du scraping.")
                        break
                except TimeoutError:
                    logging.error("Le bouton 'Suivant' n'est pas cliquable après 60 secondes. fin du scraping.")
                    break
            else:
                break

        await browser.close()
        return all_hrefs

@app.on_event("startup")
async def startup_event():
    global links
    links = await get_all_links()

@app.get("/filtered_links/{year}")
def get_filtered_links(year: str):
    global links
    dates = [link for link in links if re.search(year, link)]
    return {"filtered_links": dates}

@app.get("/filtered_links_2/{cible}")
async def get_filtered_links_2(cible: str):
   return {"filtered_links_2": [f"{str(i).zfill(2)}" for i in range(24)]}

@app.post("/process_csv/{cible}")
def download_parts(cible: str, parts_cible: LinkData):
    update_progress(0.1)
    total_steps = len(parts_cible.link_2) * 3
    current_step = 0
    if cible[0] == ".":
        date_parsed = cible[1:]
    else:
        date_parsed = cible
    for part in parts_cible.link_2:
        dl_link = f"https://s3.opensky-network.org/data-samples/states/{cible}/{part}/states_{date_parsed}-{part}.csv.tar"
        logging.info(f"Téléchargement de\n{dl_link}\n")
        response = requests.get(dl_link)
        if response.status_code == 200:
            response.raise_for_status()
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
        else:
            logging.error(f"Erreur lors du téléchargement de {dl_link}: {response.status_code}\n\n====================================================================================================================================\n")
            return {"status": "failed", "message": "can't find the date in the list"}
    return {"status": "success", "message": "CSV processed and data inserted into the database"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)

#curl -X GET "http://localhost:8100/filtered_links/2021"
#curl -X GET "http://localhost:8100/filtered_links_2/2021-11-01"
#curl -X POST "http://localhost:8100/process_csv/2021-11-01" -H "Content-Type: application/json" -d '{"link_2": ["00", "01", "02"]}'