from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions
import time
import os

app = FastAPI()

# Ajouter le middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permettre toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Permettre toutes les méthodes
    allow_headers=["*"],  # Permettre tous les headers
)

class ICAORequest(BaseModel):
    icao: str

class FlightRadarScraper:
    def __init__(self, driver_path: str):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        self.driver = webdriver.Chrome(service=Service(driver_path), options=chrome_options)
        self.url = 'https://www.flightradar24.com/data'
        self.driver.get(self.url)
        self.reject_cookies()

    def reject_cookies(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="onetrust-reject-all-handler"]')))
            cookies = self.driver.find_element(By.XPATH, '//*[@id="onetrust-reject-all-handler"]')
            self.driver.execute_script("arguments[0].click();", cookies)
            time.sleep(1)
        except selenium.common.exceptions.NoSuchElementException as e:
            print(f'Erreur: Element non trouvé {e}')
        except selenium.common.exceptions.ElementClickInterceptedException as e:
            print(f'Erreur: Element click intercepté {e}')
        except Exception as e:
            print(f'Erreur: {e}')

    def search_aircraft(self, icao: str) -> str:
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="searchAircraft"]')))
            recherche = self.driver.find_element(By.XPATH, '//*[@id="searchAircraft"]')
            time.sleep(1)
            recherche.send_keys(icao)
            time.sleep(1)
            self.driver.execute_script("""
            var rect = arguments[0].getBoundingClientRect();
            var x = rect.left + (rect.width / 2);
            var y = rect.bottom + 10;  // 10 pixels en dessous
            var evt = new MouseEvent('click', {
                bubbles: true,
                cancelable: true,
                view: window,
                clientX: x,
                clientY: y
            });
            arguments[0].dispatchEvent(evt);
            """, recherche)
            time.sleep(1)
            recherche.send_keys(u'\ue007')  # Deuxième fois
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="cnt-data-content"]/div[1]/div[2]/div/div[1]/a/img')))
            img = self.driver.find_element(By.XPATH, '//*[@id="cnt-data-content"]/div[1]/div[2]/div/div[1]/a/img')
            time.sleep(1)
            return img.get_attribute('src')
        except (selenium.common.exceptions.NoSuchElementException, selenium.common.exceptions.ElementClickInterceptedException) as e:
            print(f'Erreur: {e}')
        except Exception as e:
            print(f'Erreur: {e}')
            raise

    def close(self):
        self.driver.quit()

    def __del__(self):
        self.close()

@app.post("/get-aircraft-image/")
def get_aircraft_image_endpoint(request: ICAORequest):
    try:
        scraper = FlightRadarScraper(driver_path='/usr/local/bin/chromedriver')
        img_src = scraper.search_aircraft(request.icao)
        scraper.close()
        if img_src is None:
            raise HTTPException(status_code=404, detail="Image not found")
        return {"image_url": img_src}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)