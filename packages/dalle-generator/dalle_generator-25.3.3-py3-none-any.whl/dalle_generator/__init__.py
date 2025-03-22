import os
import uuid
import json
import base64
import requests
import tempfile
from PIL import Image
from io import BytesIO
from datetime import datetime
from selenium import webdriver
from importlib import resources
from colorpaws import ColorPaws
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class DalleGenerator():
    """Copyright (C) 2025 Ikmal Said. All rights reserved."""
    def __init__(self, mode="default", log_on=True, log_to=None, save_to="outputs", save_as="webp"):
        """
        Initialize Dalle Generator module.

        Parameters:
        - mode    (str): Startup mode ('default', 'webui', 'api').
        - log_on (bool): Enable logging.
        - log_to  (str): Directory to save logs.
        - save_to (str): Directory to save outputs.
        - save_as (str): Output format ('webp', 'jpg', 'pil').
        """
        self.logger = ColorPaws(
            name=self.__class__.__name__, 
            log_on=log_on, 
            log_to=log_to
        )

        self.__online_check()
        self.__load_preset()
        
        self.__init_checks(save_to, save_as)
        self.__driver = self.__get_webdriver()
        self.__authenticate()
        
        self.logger.info(f"{self.__class__.__name__} is now ready!")
        
        if mode != "default":
            self.__startup_mode(mode)

    def __init_checks(self, save_to: str, save_as: str):
        """
        Initialize essential checks.
        """
        try:
            self.save_to = save_to if save_to else tempfile.gettempdir()
            self.save_to = os.path.join(self.save_to, "dalle")
            
            if save_as.lower() in ['webp', 'jpg', 'pil']:
                self.save_as = save_as.lower()
            else:
                self.logger.warning(f"Invalid save format '{save_as}', defaulting to WEBP")
                self.save_as = 'webp'
        
        except Exception as e:
            self.logger.error(f"Error in init_checks: {str(e)}")
            raise
  
    def __startup_mode(self, mode: str):
        """
        Startup mode for api or webui with default values.
        """
        try:
            if mode == "webui":
                self.start_webui()
            
            elif mode == "api":
                self.start_api()
            
            else:
                raise ValueError(f"Invalid startup mode: {mode}")
        
        except Exception as e:
            self.logger.error(f"Error in startup_mode: {str(e)}")
            raise
           
    def __online_check(self, url: str = 'https://www.google.com', timeout: int = 10):
        """
        Check if there is an active internet connection.
        """
        try:
            requests.get(url, timeout=timeout)
        
        except Exception as e:
            self.logger.error("No internet connection available! Please check your network connection.")
            raise
    
    def __load_preset(self, preset_path='data.py'):
        try: 
            with open(resources.path(__name__, preset_path), 'r', encoding="utf-8") as f:
                __preset = json.load(f)
            
            self.__se = base64.b64decode(__preset["locale"][0]).decode('utf-8')
            self.__au = base64.b64decode(__preset["locale"][1]).decode('utf-8')
            self.__us = base64.b64decode(__preset["locale"][2]).decode('utf-8')
            self.__pa = base64.b64decode(__preset["locale"][3]).decode('utf-8')
        
        except Exception as e:
            self.logger.error(f"Error in load_preset: {str(e)}")
            raise
    
    def __get_webdriver(self):
        try:            
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            options.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
            
            try:
                self.logger.info('Attempting to use system webdriver!')
                return webdriver.Chrome(options=options)
            
            except WebDriverException:
                self.logger.info('System webdriver not found or incompatible, downloading webdriver...')
                service = Service(ChromeDriverManager().install())
                return webdriver.Chrome(service=service, options=options)
            
            finally:
                self.logger.info('Webdriver is ready!')
        
        except Exception as e:
            self.logger.error(f"Error in get_webdriver: {str(e)}")
            raise

    def __authenticate(self):
        try:
            self.__driver.minimize_window()
            self.__driver.set_window_position(0, -10000)
            
            self.__driver.get(self.__au)

            step_a = WebDriverWait(self.__driver, 15).until(EC.visibility_of_element_located((By.ID, "i0116")))
            step_a.send_keys(self.__us)
            
            step_b = WebDriverWait(self.__driver, 15).until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            step_b.click()
            
            step_c = WebDriverWait(self.__driver, 15).until(EC.visibility_of_element_located((By.ID, "i0118")))
            step_c.send_keys(self.__pa)
            
            step_d = WebDriverWait(self.__driver, 15).until(EC.element_to_be_clickable((By.ID, "idSIButton9")))
            step_d.click()
            
            step_e = WebDriverWait(self.__driver, 15).until(EC.element_to_be_clickable((By.ID, "acceptButton")))
            step_e.click()
        
        except Exception as e:
            self.logger.error(f"Error in authenticate: {str(e)}")
            raise
    
    def __get_task_id(self):
        """
        Generate a unique task ID for request tracking.
        Returns a truncated UUID (8 characters).
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            uuid_part = str(uuid.uuid4())[:8]
            task_id = f"{timestamp}_{uuid_part}"
            
            self.logger.info(f"[{task_id}] Created task id from request!")
            return task_id
        
        except Exception as e:
            self.logger.error(f"Error in get_task_id: {str(e)}")
            raise
                 
    def __save_image(self, url: str, task_id, index: int = 1) -> str:
        """Helper function to save an image from a URL to a temporary file."""
        try:
            # Only create directories when actually saving
            if self.save_as != 'pil':
                date_part = task_id.split('_')[0]
                formatted_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                output_dir = os.path.join(self.save_to, formatted_date)
                os.makedirs(output_dir, exist_ok=True)
            
            response = requests.get(url)
            
            if self.save_as == 'webp':
                try:                
                    img = Image.open(BytesIO(response.content))
                    
                    webp_buffer = BytesIO()
                    img.save(webp_buffer, format='WebP', quality=90)
                    content = webp_buffer.getvalue()
                    suffix = '.webp'
                    
                except Exception as e:
                    self.logger.warning(f"[{task_id}] Failed to convert to WebP, falling back to JPG!")
                    content = response.content
                    suffix = '.jpg'
                    
            elif self.save_as == 'pil':
                img = Image.open(BytesIO(response.content))
                return img

            else:
                content = response.content
                suffix = '.jpg'

            filename = f"{task_id}_{index}{suffix}"
            file_path = os.path.join(output_dir, filename)
            
            with open(file_path, 'wb') as output:
                output.write(content)
                
            self.logger.info(f"[{task_id}] Saved output: {file_path}")
            return file_path
                
        except Exception as e:
            self.logger.error(f"[{task_id}] Error in save_image: {str(e)}")
            raise

    def __v1(self, prompt, task_id) -> list:
        try:
            self.__driver.get(self.__se)
            self.__driver.refresh()
            
            self.__driver.find_element(By.ID, "sb_form_q").send_keys(prompt)
            self.__driver.find_element(By.ID, "create_btn_c").click()

            try:
                WebDriverWait(self.__driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "gil_err_tc")))
                raise Exception(f'[{task_id}] Request blocked (likely explicit content)')
            
            except TimeoutException:
                pass

            saved_images = []
            while True:
                self.logger.info(f"[{task_id}] Refreshing request!")
                self.__driver.refresh()

                try:
                    WebDriverWait(self.__driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "img_cont")))
                    divs = self.__driver.find_elements(By.CLASS_NAME, "img_cont")
                    urls = [div.find_element(By.TAG_NAME, "img").get_attribute("src").split("?")[0] for div in divs]
                    self.logger.info(f'[{task_id}] Found {len(urls)} images!')
                    
                    for idx, url in enumerate(urls, 1):
                        if filename := self.__save_image(url, task_id, idx):
                            saved_images.append(filename)
                    return saved_images
                
                except TimeoutException:
                    try:
                        img = self.__driver.find_element(By.CLASS_NAME, "gir_mmimg")
                        src = img.get_attribute("src").split("?")[0]
                        self.logger.info(f'[{task_id}] Found 1 image!')
                        
                        if filename := self.__save_image(src, task_id):
                            saved_images.append(filename)
                        return saved_images
                    
                    except NoSuchElementException:
                        raise Exception(f'[{task_id}] Unable to find images!')
        
        except Exception as e:
            self.logger.error(f"{str(e)}")
            raise

    def __v2(self, prompt, task_id) -> list:
        try:
            self.__driver.get(self.__se)
            self.__driver.refresh()
            
            self.__driver.find_element(By.ID, "sb_form_q").send_keys(prompt)
            self.__driver.find_element(By.ID, "create_btn_c").click()
            
            try:
                WebDriverWait(self.__driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "gil_err_tc")))
                self.logger.error(f'[{task_id}] Request blocked (likely explicit content)')
                return []
            
            except TimeoutException:
                pass

            while True:
                self.logger.info(f"[{task_id}] Refreshing request!")
                self.__driver.refresh()

                try:
                    grid = WebDriverWait(self.__driver, 15).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "girrgrid.light.seled"))
                    )
                    
                    saved_images = []
                    try:
                        images = grid.find_elements(By.CLASS_NAME, "_4-images")
                        
                        if images:
                            urls = [img.get_attribute("src").split("?")[0] for img in images]
                            self.logger.info(f'[{task_id}] Found {len(urls)} images!')
                        
                        else:
                            img = grid.find_element(By.CLASS_NAME, "_1-images")
                            urls = [img.get_attribute("src").split("?")[0]]
                            self.logger.info(f'[{task_id}] Found 1 image!')
                        
                        for idx, url in enumerate(urls, 1):
                            if filename := self.__save_image(url, task_id, idx):
                                saved_images.append(filename)
                        
                        return saved_images
                    
                    except NoSuchElementException:
                        raise Exception(f'[{task_id}] Unable to find images!')
                        
                except TimeoutException:
                    raise Exception(f'[{task_id}] Unable to find target element in time!')
        
        except Exception as e:
            self.logger.error(f"{str(e)}")
            return []

    def image_generate(self, prompt):
        try:
            self.__driver.get(self.__se)
            self.__driver.refresh()
            
            task_id = self.__get_task_id()
            
            try:
                self.__driver.find_element(By.CLASS_NAME, "gih_pink")
                self.logger.info(f"[{task_id}] Processing request in legacy mode!")
                return self.__v1(prompt, task_id)
            
            except NoSuchElementException:
                self.logger.info(f"[{task_id}] Processing request in latest mode!")
                return self.__v2(prompt, task_id)
        
        except Exception as e:
            self.logger.error(f"[{task_id}] Error in image_generate: {str(e)}")
            raise

    def start_api(self, host: str = "0.0.0.0", port: int = 5734, debug: bool = False):
        """
        Start the API server with all endpoints.

        Parameters:
        - host (str): Host to run the server on (default: "0.0.0.0")
        - port (int): Port to run the server on (default: 5734)
        - debug (bool): Enable Flask debug mode (default: False)
        """
        try:
            from .api import DalleWebAPI
            self.save_to = None
            self.save_as = 'pil'
            
            DalleWebAPI(self, host=host, port=port, debug=debug)
        
        except Exception as e:
            self.logger.error(f"WebAPI error: {str(e)}")
            raise

    def start_webui(self, host: str = "0.0.0.0", port: int = 7680, browser: bool = False, upload_size: str = "4MB",
                    public: bool = False, limit: int = 10, quiet: bool = False):
        """
        Start Atelier WebUI with all features.
        
        Parameters:
        - host (str): Server host (default: "0.0.0.0")
        - port (int): Server port (default: 7680) 
        - browser (bool): Launch browser automatically (default: False)
        - upload_size (str): Maximum file size for uploads (default: "4MB")
        - public (bool): Enable public URL mode (default: False)
        - limit (int): Maximum number of concurrent requests (default: 10)
        - quiet (bool): Enable quiet mode (default: False)
        """
        try:
            from .webui import DalleWebUI
            
            DalleWebUI(self, host=host, port=port, browser=browser, upload_size=upload_size,
                       public=public, limit=limit, quiet=quiet)
        
        except Exception as e:
            self.logger.error(f"Error in start_wui: {str(e)}")
            raise
