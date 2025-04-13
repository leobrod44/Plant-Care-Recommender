from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
import random
import time
import json
import os
import urllib.request
from selenium.webdriver.common.by import By
import types
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys # Added for escape key.


def create_stealth_browser():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    options = webdriver.ChromeOptions()
    options.add_argument(f'--user-agent={random.choice(user_agents)}')
    options.add_argument('--user-data-dir=./chrome_profile')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    
    def random_human_behavior(self):
        time.sleep(random.uniform(1, 3))
        scroll_amount = random.randint(300, 700)
        self.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 2))
        if random.random() > 0.7:
            self.execute_script(f"window.scrollBy(0, -{random.randint(100, 300)});")
            time.sleep(random.uniform(0.5, 1.5))
    
    driver.random_human_behavior = types.MethodType(random_human_behavior, driver)
    
    return driver

def download_images(plant_name, num_images):
    driver = create_stealth_browser()
    
    folder_path = f'/home/singouini/Projects/Victorin/ml/dataset4/{plant_name.replace(" ", "_")}/'
    create_directory(folder_path)
    
    json_file = os.path.join(folder_path, 'image_urls.json')
    image_urls_dict = load_image_urls(json_file)

    skip_val = len(os.listdir(folder_path))

 
    search_url = f'https://www.google.com/search?q={plant_name.replace(" ", "+")}&tbm=isch&tbs=isz:l'
    driver.get(search_url)
    
    time.sleep(random.uniform(3, 5))

    for i in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(1, 2))

    driver.random_human_behavior()
    
    downloaded_count = 0
    scroll_count = 0

    while downloaded_count < num_images:
        thumbnails = driver.find_elements(By.XPATH, "//img[contains(@class, 'YQ4gaf') and not(contains(@class, ' '))]")[(skip_val+30):]
        print(f"Loaded {len(thumbnails)} thumbnails.")
        
        for index, thumbnail in enumerate(thumbnails[:]):
            if downloaded_count >= num_images:
                break
                
            try:
                time.sleep(random.uniform(0.5, 1.5))
                driver.execute_script("arguments[0].scrollIntoView(true);", thumbnail)
                # Wait for the thumbnail to be clickable
                #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "(//img[contains(@class, 'YQ4gaf') and not(contains(@class, ' '))])[" + str(index + 1) + "]")))
                
                # Try clicking with JavaScript
                driver.execute_script("arguments[0].click();", thumbnail)
                time.sleep(random.uniform(2, 4))
                
                try:
                    large_img = driver.find_element(By.XPATH, "//img[@jsname='kn3ccd']")
                    img_url = large_img.get_attribute('src')
                    
                    if img_url and img_url not in image_urls_dict.get(plant_name, []):
                        try:
                            time.sleep(random.uniform(0.5, 1.5))
                            filename = img_url.split('/')[-1]
                            urllib.request.urlretrieve(img_url, os.path.join(folder_path, f"{index}.jpg"))
                            
                            if plant_name not in image_urls_dict:
                                image_urls_dict[plant_name] = []
                            image_urls_dict[plant_name].append(img_url)
                            save_image_urls(image_urls_dict, json_file)
                            
                            downloaded_count += 1
                            print(f"Downloaded {downloaded_count}/{num_images} for {plant_name}")
                            
                            time.sleep(random.uniform(1, 3))
                        except Exception as download_error:
                            print(f"Download error for {img_url}: {download_error}")
                    else:
                        print(f"Image already downloaded or URL not found for thumbnail {index}")
                except Exception as e:
                    print(f"Error accessing full image for thumbnail {index}: {e}")
                
                if random.random() > 0.7:
                    driver.random_human_behavior()
                    
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(random.uniform(0.5, 1.5))
                
            except Exception as e:
                print(f"Error with thumbnail {index} {e}")
                continue
        
        if downloaded_count < num_images and len(thumbnails) > 0 and scroll_count < 3: 

            for i in range(1):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(random.uniform(1, 2))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 5))
            scroll_count += 1
        else:
            break

    driver.quit()
    print(f"Completed downloading {downloaded_count} images for {plant_name}")

def create_directory(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def load_image_urls(json_file):
    try:
        with open(json_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_image_urls(image_urls, json_file):
    with open(json_file, 'w') as f:
        json.dump(image_urls, f, indent=4)

def main():
   
    #plants = [ 'Jade plant (Crassula ovata)','Pothos (Ivy arum)', 'Polka Dot Plant (Hypoestes phyllostachya)', 'Yucca', 'Dumb Cane (Dieffenbachia spp.)', 'Daffodils (Narcissus spp.)', 'Elephant Ear (Alocasia spp.)', 'Poinsettia (Euphorbia pulcherrima)', 'Calathea', 'Monstera Deliciosa (Monstera deliciosa)', 'Hyacinth (Hyacinthus orientalis)', 'Sago Palm (Cycas revoluta)', 'Chrysanthemum', 'Ponytail Palm (Beaucarnea recurvata)', 'Anthurium (Anthurium andraeanum)', 'Tradescantia', 'Chinese Money Plant (Pilea peperomioides)', 'Chinese evergreen (Aglaonema)', 'Tulip', 'Parlor Palm (Chamaedorea elegans)', 'Peace lily', 'ZZ Plant (Zamioculcas zamiifolia)', 'Venus Flytrap', 'Christmas Cactus (Schlumbergera bridgesii)', 'Rattlesnake Plant (Calathea lancifolia)', 'Money Tree (Pachira aquatica)', 'Boston Fern (Nephrolepis exaltata)', 'Cast Iron Plant (Aspidistra elatior)', 'Orchid', 'African Violet (Saintpaulia ionantha)', 'Ctenanthe', 'Snake plant (Sanseviera)', 'Bird of Paradise (Strelitzia reginae)', 'English Ivy (Hedera helix)', 'Birds Nest Fern (Asplenium nidus)']
    plants = [
    "Elaeagnus (Elaeagnus spp.)",
    "Embothrium (Embothrium spp.)",
    "Enkianthus (Enkianthus spp.)",
    "Epacris (Epacris spp.)",
    "Erica (Erica spp.)",
    "Eriostemon (Eriostemon spp.)",
    "Eryngium (Eryngium spp.)",
    "Erythrina (Erythrina spp.)",
    "Escallonia (Escallonia spp.)",
    "Eucalyptus (Eucalyptus spp.)",
    "Eucryphia (Eucryphia spp.)",
    "Euonymus (Euonymus spp.)",
    "Eupatorium (Eupatorium spp.)",
    "Euryops (Euryops spp.)",
    "Exochorda (Exochorda spp.)",
    "Fatshedera (Fatshedera spp.)",
    "Felicia (Felicia spp.)",
    "Forsythia (Forsythia spp.)",
    "Fothergilla (Fothergilla spp.)",
    "Freesia (Freesia spp.)",
    "Fuchsia (Fuchsia spp.)",
    "Gaillardia (Gaillardia spp.)",
    "Garrya (Garrya spp.)",
    "Gaura (Gaura spp.)",
    "Genista (Genista spp.)",
    "Geranium (Geranium spp.)",
    "Gerbera (Gerbera spp.)",
    "Geum (Geum spp.)",
    "Gillenia (Gillenia spp.)",
    "Gladiolus (Gladiolus spp.)",
    "Gomphrena (Gomphrena spp.)",
    "Grevillea (Grevillea spp.)",
    "Grewia (Grewia spp.)",
    "Griselinia (Griselinia spp.)",
    "Gunnera (Gunnera spp.)",
    "Gymnocalycium (Gymnocalycium spp.)",
    "Haemanthus (Haemanthus spp.)",
    "Halimium (Halimium spp.)",
    "Hamamelis (Hamamelis spp.)",
    "Hebe (Hebe spp.)",
    "Hedychium (Hedychium spp.)",
    "Helenium (Helenium spp.)",
    "Helianthemum (Helianthemum spp.)",
    "Helianthus (Helianthus spp.)",
    "Helichrysum (Helichrysum spp.)",
    "Heliopsis (Heliopsis spp.)",
    "Helleborus (Helleborus spp.)",
    "Heloniopsis (Heloniopsis spp.)",
    "Hemigraphis (Hemigraphis spp.)",
    "Heptacodium (Heptacodium spp.)",
    "Heracleum (Heracleum spp.)",
    "Hesperantha (Hesperantha spp.)",
    "Heuchera (Heuchera spp.)",
    "Hibbertia (Hibbertia spp.)",
    "Hibiscus (Hibiscus spp.)",
    "Hieracium (Hieracium spp.)",
    "Hippophae (Hippophae spp.)",
    "Holboellia (Holboellia spp.)",
    "Hosta (Hosta spp.)",
    "Houttuynia (Houttuynia spp.)"
    ]   

    
    plant_names = [name + " in pot" for name in plants]
    num_images = 200

    for plant in plant_names:
        print(f"Starting image download for {plant}...")
        download_images(plant, num_images)
        print(f"Images for {plant} have been downloaded.")

if __name__ == "__main__":
    main()