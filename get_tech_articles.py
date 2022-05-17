import json
import time

import pydub
import speech_recognition as sr
from decouple import config
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.add_argument("user-data-dir=cookies")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--enable-javascript")
chrome_options.add_argument(
    '--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"'
)

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)


class NyTimesTechArticlesScraper:
    _URL = "https://www.nytimes.com"

    def __init__(
        self,
        username=config("USERNAME"),
        password=config("PASSWORD"),
    ):
        self.username = username
        self.password = password

    def do_login(self):
        """
        Method to login into the NY Times website
        """
        try:
            # Access the index page
            driver.get(self._URL)
            # Click on the login button
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="app"]/div[2]/div/header/section[1]/div[4]/a[2]',
                    )
                )
            ).click()
            # Enter the username
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="email"]'))
            ).send_keys(self.username)
            # Click on CONTINUE button
            driver.find_element(
                By.XPATH, '//*[@id="myAccountAuth"]/div/div/div/form/div/div[2]/button'
            ).click()
            # Enter the password
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="password"]',
                    )
                )
            ).send_keys(self.password)
            # Click on LOGIN button
            driver.find_element(
                By.XPATH, '//*[@id="myAccountAuth"]/div/div/form/div/div[2]/button'
            ).click()

        except Exception as e:
            print(f"An exception ocurred with login: {e}")
            self.captcha_v3_verificator()
            driver.close()

    def captcha_v3_verificator(self):
        """
        Method to verificate if captcha v3 from Google is present
        """
        if driver.current_url.startswith("https://myaccount.nytimes.com/auth/login"):
            self.captcha_v3_solver()

    def captcha_v3_solver(self):
        """
        Method to solve captcha v3 from Google based on speech to text solution
        """
        try:
            # Click on the 'I am not a robot' button
            WebDriverWait(driver, 20).until(
                EC.visibility_of_element_located(
                    driver.find_element(
                        (
                            By.XPATH,
                            '//*[@id="recaptcha-anchor"]/div[4]',
                        )
                    )
                )
            ).click()

            # focus on iframe and verificate the token request //*[@id="recaptcha-token"]
            # Click on the 'audio' icon
            driver.find_element(By.XPATH, '//*[@id="recaptcha-audio-button"]').click()
            driver.find_element(By.XPATH, '//*[@id=":2"]').click()
            # Click on src link of audio
            audio_link = driver.find_element(
                By.XPATH, '//*[@id="audio-source"]'
            ).get_attribute("src")
            # Download the audio to specific path
            driver.get(audio_link)
            # Access speech recognition API
            sound = pydub.AudioSegment.from_mp3("payload.mp3")
            sound.export("payload.wav", format="wav")
            filename = "payload.wav"
            # initialize the recognizer
            r = sr.Recognizer()
            # open the file
            with sr.AudioFile(filename) as source:
                r.adjust_for_ambient_noise(source)
                # listen for the data (load audio to memory)
                audio_data = r.record(source)
                # recognize (convert from speech to text)
                text = r.recognize_google(audio_data, language="pt-BR")
                # Write and verify if the text is correct
                driver.find_element(By.XPATH, '//*[@id="audio-response"]').send_keys(
                    text
                )
                driver.find_element(
                    By.XPATH, '//*[@id="recaptcha-verify-button"]'
                ).click()

        except Exception as e:
            print(f"An exception ocurred with captcha v3: {e}")
            human_solution = input("Please solve the captcha to save it on cookies and write Y on terminal: ")
            if human_solution.upper == "Y":
                self.do_login()

    def get_tech_articles(self):
        """
        Method to get tech articles from NY times
        """
        try:
            # Click on the tech header item
            tech_header = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//*[@id="app"]/div[2]/div/header/div[4]/ul/li[7]')
                )
            )
            tech_header.click()

            # Scroll down to the bottom/top of the page dealing with lazy loading
            page = driver.find_element(By.TAG_NAME, "html")
            for _ in range(1, 20):
                page.send_keys(Keys.END)
                time.sleep(2)
                page.send_keys(Keys.HOME)
                time.sleep(2)

            # Get the list of all articles
            articles = driver.find_elements(By.CLASS_NAME, "css-ye6x8s")

            # Get each article info: title, summary, author, published date and put inside a list with dictionary format
            articles_info = []
            for iteration, article in enumerate(articles, start=1):
                try:
                    title = article.find_element(
                        By.XPATH,
                        f'//*[@id="stream-panel"]/div[1]/ol/li[{iteration}]/div/div[1]/a/h2',
                    ).text
                    summary = article.find_element(
                        By.XPATH,
                        f'//*[@id="stream-panel"]/div[1]/ol/li[{iteration}]/div/div[1]/a/p',
                    ).text
                    author = article.find_element(
                        By.XPATH,
                        f'//*[@id="stream-panel"]/div[1]/ol/li[{iteration}]/div/div[1]/a/div[2]',
                    ).text
                    published_date = article.find_element(
                        By.XPATH,
                        f'//*[@id="stream-panel"]/div[1]/ol/li[{iteration}]/div/div[2]/span',
                    ).text
                    articles_info.append(
                        {
                            "title": title,
                            "summary": summary,
                            "author": author,
                            "published_date": published_date,
                        }
                    )
                except Exception as e:
                    print(f"An exception ocurred with article {iteration}: {e}")
                    continue
            print(articles_info)
            print(f"{len(articles_info)} articles were found")
            return articles_info

        except Exception as e:
            print(f"An exception ocurred with tech articles: {e}")
            self.do_logout_streampanel()
            driver.close()

    def do_logout_streampanel(self):
        try:
            # click on account menu
            account_menu = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="app"]/div[1]/div/header/section[1]/div[4]/div[1]/button',
                    )
                )
            )
            account_menu.click()
            # click on logout
            logout_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "/html/body/div[4]/div/div/div/div[6]/div[5]/a",
                    )
                )
            )
            logout_button.click()
            time.sleep(1)
        except Exception as e:
            print(f"An exception ocurred with logout: {e}")
            driver.close()


if __name__ == "__main__":
    # Create a new instance of the class
    webscraper = NyTimesTechArticlesScraper()
    # Do login
    webscraper.do_login()
    # Get the list of tech articles
    webscraper.get_tech_articles()
    # Do logout on stream panel
    webscraper.do_logout_streampanel()
    driver.close()
