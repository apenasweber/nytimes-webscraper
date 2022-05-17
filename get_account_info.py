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
# chrome_options.add_argument("--headless")
chrome_options.add_argument("user-data-dir=cookies")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--enable-javascript")
chrome_options.add_argument(
    '--user-agent="Mozilla/5.0 (Windows Phone 10.0; Android 4.2.1; Microsoft; Lumia 640 XL LTE) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Mobile Safari/537.36 Edge/12.10166"'
)

driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)


class NyTimesAccountInfoScraper:
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

    def get_account_info(self):
        """
        Method to get logged user infos
        """
        try:
            # Click on account drop-down
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="app"]/div[2]/div/header/section[1]/div[4]/div[1]/button',
                    )
                )
            ).click()

            # Click on account hyperlink
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//html/body/div[5]/div/div/div/div[4]/div[2]/a")
                )
            ).click()
            time.sleep(1)
            # switch to modal
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(2)
            account_number = driver.find_element(
                By.XPATH,
                '//*[@id="root"]/div[1]/div[2]/div[3]/div[2]/div/div/section[1]/div[3]/div/div[2]/div/span[2]',
            ).text
            email_address = driver.find_element(
                By.XPATH,
                "//*[@id='root']/div[1]/div[2]/div[3]/div[2]/div/div/section[1]/div[4]/div/div[2]/div[1]/span[2]",
            ).text
            driver.switch_to.window(driver.window_handles[0])
            driver.close()
            print(f"Account number: {account_number} | Email address: {email_address}")
            return [{"account_number": account_number, "email_address": email_address}]

        except Exception as e:
            print(f"An exception ocurred with account info: {e}")
            self.do_logout_account()
            driver.close()

    def do_logout_account(self):
        try:
            driver.switch_to.window(driver.window_handles[0])
            # click on account menu
            account_menu = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="root"]/div[1]/div[1]/div/div[1]/div[2]/button',
                    )
                )
            )
            account_menu.click()
            # click on logout
            logout_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="root"]/div[1]/div[2]/div/div[5]/a',
                    )
                )
            )
            time.sleep(1)
            logout_button.click()
            
        except Exception as e:
            print(f"An exception ocurred with logout in stream panel: {e}")
            driver.close()


if __name__ == "__main__":
    webscraper = NyTimesAccountInfoScraper()
    # Do login
    webscraper.do_login()
    # Get the acccount info
    webscraper.get_account_info()
    # Do logout
    webscraper.do_logout_account()
    driver.close()
