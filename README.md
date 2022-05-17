# NY TIMES WEB SCRAPER
1. Create a virtual environment
2. Install dependencies with: 
```
pip install -r requirements.txt
```

3. Run the tech articles scraper with:
```
python get_tech_articles.py
```

4. Run the get account info script with:
```
python get_account_info.py
```

## Considerations
1. The scraper saves all cookies infos incuding the session id like solved captcha. I created a captcha solver script to solve the captcha but thinking about it, I think it's better to solve it manually and just save on cookies. On the first execution you can set chrome_options.add_argument("--headless") as commented to see the flow of the scraper and on second execution you can set chrome_options.add_argument("--headless") as uncommented to see the flow without screen executions and no risk with captchas.
2. I created a django app to store the articles and the account info. I think it's better to store the articles in a database and the account info in a json file but i couldn't finalize the app because my demand in DMCARD is very high, including war rooms on the weekend. I can do it in the future in a v2 of the scraper if needs.
3. I couldnt create tests because of the time limitation. I think it's better to create tests in the future.
4. Please contact me if you have any questions.
