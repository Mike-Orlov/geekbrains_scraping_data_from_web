from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from pprint import pprint
import time
from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
import pymongo

chrome_options = Options()
chrome_options.add_argument('start-maximized') # Раскрытие браузера сразу на весь экран
#chrome_options.add_argument("--headless")  #Режим без графического интерфейса!

# Скачать драйвер из https://chromedriver.chromium.org/downloads и положить в папку
driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options) # драйвер скачиваем под реально установленный браузер (они есть для всех браузеров)
driver.get('https://mail.ru/')

login = driver.find_element_by_id('mailbox:login-input')
login.send_keys('study.ai_172@mail.ru')
# login.clear() # Прижелании можно было бы и очистить

login.send_keys(Keys.RETURN)
time.sleep(2)

passw = driver.find_element_by_id('mailbox:password-input')
passw.send_keys('NextPassword172')

passw.send_keys(Keys.RETURN)
time.sleep(2)

assert "Почта Mail.ru" in driver.title # Проверка, что мы именно попали на нужную страницу
# assert "No results found." not in driver.page_source # Т.е. можно было бы и отрицание использовать

all_letters = []

while True:
    count = 0
    letters_list = driver.find_elements_by_class_name('js-letter-list-item')

    for letter_item in letters_list:
        letter = {}
        subject = letter_item.find_element_by_class_name('llc__subject').text
        sender_mailbox = letter_item.find_element_by_xpath('.//div[contains(@class, "llc__item_correspondent")]/span').get_attribute("title")
        sender_name = letter_item.find_element_by_class_name('llc__item_correspondent').text
        letter_date = letter_item.find_element_by_class_name('llc__item_date').get_attribute("title")
        if 'Вчера' in letter_date:
            letter_date = letter_date.replace('Вчера', str(datetime.now().date() - timedelta(days=1)))
        elif 'Сегодня' in letter_date:
            letter_date = letter_date.replace('Сегодня', str(datetime.now().date()))
        letter_link = letter_item.get_attribute("href")

        letter['subject'] = subject
        letter['sender_mailbox'] = sender_mailbox
        letter['sender_name'] = sender_name
        letter['letter_date'] = letter_date
        letter['letter_link'] = letter_link
        
        if letter not in all_letters:
            all_letters.append(letter)
        else:
            count += 1
    if count == len(letters_list):
        break

    actions = ActionChains(driver)
    actions.move_to_element(letters_list[-1])
    actions.perform()
    

#pprint(all_letters)
#print(len(all_letters))

mailru_box_df = pd.DataFrame(all_letters)

#driver.close() # It closes the the browser window on which the focus is set.
driver.quit() # It basically calls driver.dispose method which in turn closes all the browser windows and ends the WebDriver session gracefully.



client = MongoClient('127.0.0.1', 27017) # ip-адресс и порт
db = client['emails'] # указатель на БД, сама БД появляется только когда туда записаны какие-то данные (особенность Mongo)

mailru_box = db.mailru_box # создание "коллекции" внутри БД, это как таблица в SQL

for string in mailru_box_df.to_dict(orient='records'):
    mailru_box.update_one({'letter_link': string['letter_link']}, {'$set': string}, upsert=True)

mailru_box.create_index([('letter_link', pymongo.ASCENDING)]) # Сделаем также индексы

for news in mailru_box.find({}): # Проверка содержания
    pprint(news)

print(mailru_box.count_documents({})) # Проверка колличества

mailru_box.delete_many({})