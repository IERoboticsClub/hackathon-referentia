from bs4 import BeautifulSoup
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Airbnb_scraper:

    def __init__(self, driver):
        self.html = None
        self.soup = None
        self.driver = driver
        self.href = None
        self.reviews = None
        self.distribution = None
    
    def chrome_options():
        chrome_options = Options()
        chrome_options.page_load_strategy = 'normal'
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        return chrome_options


    # Example link: https://www.airbnb.es/rooms/plus/23840102?adults=1&category_tag=Tag%3A7769&children=0&enable_m3_private_room=true&infants=0&pets=0&search_mode=flex_destinations_search&check_in=2023-10-16&check_out=2023-10-21&federated_search_id=42f775af-840a-450e-907c-f0fc91b059f6&source_impression_id=p3_1685434270_ulStyYBL9a3RL5Ax
    
    def get_reviews(self, airbnb_url):
            reviews = {}
            self.driver.get(airbnb_url)
            scroll_attempts = 0
            flag = False
            time.sleep(1)
            
            try:
                time.sleep(3)
                close_button = self.driver.find_element(By.CSS_SELECTOR, "[aria-label='Close']")
                close_button.click()
            except:
                print('No pop-up for traduction niceeee!')

            # Scroll to the review expand button
            while scroll_attempts < 7:
                try:
                    button = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='pdp-show-all-reviews-button']")
                    self.driver.execute_script("window.scrollBy(0, 5);")
                    if button.is_displayed() and button.is_enabled():
                        button.click()
                        print("Review button clicked succesfully!")
                        flag = True
                        break
                except Exception as e:
                    print("Scrolling... can't find review button")
                    self.driver.execute_script("window.scrollBy(0, 5);")
                    scroll_attempts += 1
                    time.sleep(1)
            
            if flag:
                scrollable_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(((By.CSS_SELECTOR, '[class="_17itzz4"]'))))
                while True:
                    initial_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
                    ActionChains(self.driver).move_to_element(scrollable_element).click_and_hold().perform()
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_element)
                    ActionChains(self.driver).release().perform()
                    time.sleep(1)
                    new_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
                    print("Scrolling... through reviews")
                    if new_height == initial_height:
                        print("Reached end!")
                        break
                
                html = self.driver.page_source
                self.soup = BeautifulSoup(html, 'html.parser')

                """file_path = './tempDir/output.txt'
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(self.soup.prettify())
                print(f'Prettified output has been written to {file_path}')"""

                # Get General review of the Airbnb
                try:
                    generalpivot = self.soup.find('span', {'class':'t1xdm4l6 dir dir-ltr'})
                    generalreview = generalpivot.find('span', {'class':'a8jt5op dir dir-ltr'}).text
                    generalreview = generalreview.replace(",", ".")
                    generalreview = float(generalreview.split(" estrellas")[0])
                except Exception:
                    generalreview = None 

                reviews['General_Rating'] = generalreview


                # Get Review distribution
                reviews['Categories'] = {}
                distr_pivot = self.soup.find('div', {'class':'_13qdk1f'})
                distr_bar = distr_pivot.find('div', {'class':'c6req26 dir dir-ltr'})
                distrs = distr_bar.findAll('div', {'class':'_yorrb7h'})

                for distr in distrs:
                    try:
                        category = distr.find('div', {'class':'_y1ba89'}).text
                    except Exception:
                        category = 'NotFound'
                    try:
                        rating = distr.find('span', {'class':'_4oybiu'}).text
                        rating = rating.replace(",", ".")
                        rating = float(rating)
                    except Exception:
                        rating = None
                    
                    reviews['Categories'][category] = rating

                # Get the reviews from page
                review_bar = self.soup.find('div', {'data-testid':'pdp-reviews-modal-scrollable-panel'})
                reviews_list = review_bar.findAll('div', {'class':'r1are2x1 dir dir-ltr'})
                reviews['Reviews'] = []
                for review in reviews_list:
                    try:
                        review = review.find('span', {'class':'ll4r2nl dir dir-ltr'}).text
                    except Exception:
                        review = None
                    reviews['Reviews'].append(review)
                print('General Rating: ', reviews['General_Rating'])
                print('Categories Rating: ', reviews['Categories'])
                print('Length text reviews: ', len(reviews['Reviews']))
                return reviews
            else:
                print('Little reviews, no button available')
                return None


### Code for streamlit app ###
# from streamlit-scrapper import Airbnb_scraper

"""retrieved_url = 'Insert-Link'
# Make sure to have driver 'chromedriver.exe' in folder 'driver'
driver = webdriver.Chrome(executable_path=r'driver\chromedriver.exe', chrome_options=Airbnb_scraper.chrome_options())
scrapper = Airbnb_scraper(driver)
reviews = scrapper.get_reviews(retrieved_url)
print(reviews)"""