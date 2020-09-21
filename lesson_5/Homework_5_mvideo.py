from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # Ожидание (альтернатива в Selenium библиотеке time)
from selenium.webdriver.support import expected_conditions as EC # Событие производимое по условию
from selenium.webdriver.common.action_chains import ActionChains
from pprint import pprint
import time
from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient
import pymongo

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
chrome_options.add_argument('start-maximized') # Раскрытие браузера сразу на весь экран
#chrome_options.add_argument("--headless")  #Режим без графического интерфейса!

# Скачать драйвер из https://chromedriver.chromium.org/downloads и положить в папку
driver = webdriver.Chrome('./chromedriver.exe', options=chrome_options) # драйвер скачиваем под реально установленный браузер (они есть для всех браузеров)
driver.get('https://www.mvideo.ru/')

goods = driver.find_elements_by_class_name('gallery-layout') # elementS для сбора всех элементов
for good in goods:
    try:
        if 'Хиты продаж' in good.find_element_by_class_name('h2').text:
            actions = ActionChains(driver)
            actions.move_to_element(good)
            actions.perform()
            while True:
                # Закладываем ожидание перед нажатием кнопки, т.к. она исчезает после нажатия на какое-то время
                # time тут будет не удобно, ведь время загрузки может меняться
                # Таймаут 15 сек в данном случае означает максимальное время для ожидания, но может быть и короче
                button = WebDriverWait(good, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME,'sel-hits-button-next'))
                )
                button.click()
                time.sleep(5)
                #print('Click')
                try:
                    good.find_element_by_xpath('.//a[@class="next-btn sel-hits-button-next disabled"]')
                except:
                    continue
                else:
                    break
            all_products = []
            products_list = good.find_elements_by_tag_name('li')
            for product_item in products_list:
                product = {}
                product_name = product_item.find_element_by_tag_name('h4').get_attribute('title')
                product_link = product_item.find_element_by_class_name('sel-product-tile-title').get_attribute("href")

                product['product_name'] = product_name
                product['product_link'] = product_link
                all_products.append(product)
    except:
        continue
#pprint(all_products)

mvideo_df = pd.DataFrame(all_products)

#driver.close() # It closes the the browser window on which the focus is set.
driver.quit() # It basically calls driver.dispose method which in turn closes all the browser windows and ends the WebDriver session gracefully.

client = MongoClient('127.0.0.1', 27017) # ip-адресс и порт
db = client['mvideo_bestsellers'] # указатель на БД, сама БД появляется только когда туда записаны какие-то данные (особенность Mongo)

mvideo = db.mvideo # создание "коллекции" внутри БД, это как таблица в SQL

for string in mvideo_df.to_dict(orient='records'):
    mvideo.update_one({'product_link': string['product_link']}, {'$set': string}, upsert=True)

mvideo.create_index([('product_link', pymongo.ASCENDING)]) # Сделаем также индексы

for news in mvideo.find({}): # Проверка содержания
    pprint(news)

print(mvideo.count_documents({})) # Проверка колличества

mvideo.delete_many({})