# driver imports
import time,pandas
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options

# imports for condition checking
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# exception imports
from selenium.common import NoSuchElementException, TimeoutException

# Extract all links
with open("twitter_links.csv" ,'r') as links:
    link_list =[x[1:-2] for x in links.readlines()]

# driver initialization
service = Service(GeckoDriverManager().install())
fire_options = Options()
fire_options.add_argument("--detach")
driver = webdriver.Firefox(options=fire_options,service=service)

# Temporary Dictionary
data_dict={
    "bio":[],
    "follower":[],
    "following":[],
    "location":[],
    "website":[]
}
# Start from first link
driver.get(url=link_list[0])

for link in range(1,len(link_list)+1):
    # Freeze page after Name loads
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, './/div[@data-testid="UserName"]'))
        )

    # If name not found skip page(page is invalid)
    except TimeoutException:
        print("Account not Found, Skipping")
        time.sleep(2)
        driver.execute_script("window.open(arguments[0]);", link_list[link])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    # Get data when page frozen and skip data that does not exist
    else:
        driver.execute_script("window.stop();")
        try :
            bio = driver.find_element(By.XPATH,value='.//div[@data-testid="UserDescription"]/span').text
        except NoSuchElementException:
            bio = ''
        following = driver.find_element(By.XPATH,value='.//div[@class="css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj"]/div[1]/a/span[1]/span').text
        follower = driver.find_element(By.XPATH,value='.//div[@class="css-175oi2r r-13awgt0 r-18u37iz r-1w6e6rj"]/div[2]/a/span[1]/span').text

        location = driver.find_element(By.XPATH,value='.//span[@data-testid="UserLocation"]/span/span').text
        try:
            website = driver.find_element(By.XPATH,value='.//a[@data-testid="UserUrl"]').get_attribute('href')
        except NoSuchElementException:
            website = ''

        # Insert data into dictionary
        data_dict["bio"].append(bio)
        data_dict["follower"].append(follower)
        data_dict["following"].append(following)
        data_dict["location"].append(location)
        data_dict["website"].append(website)

        # wait for convenience
        time.sleep(3)
        # open the next link and close previous
        try:
            driver.execute_script("window.open(arguments[0]);", link_list[link])
        except IndexError:
            break
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

driver.quit()

df = pandas.DataFrame(data_dict)
df.to_csv("Scrape_data",index=False)
