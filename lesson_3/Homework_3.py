from pymongo import MongoClient
import pymongo
from pprint import pprint
import pandas as pd
import random

DATA_FILE_PATH = 'hh_sj_saved.csv'

df_full = pd.read_csv(DATA_FILE_PATH) # Полная база
df_initial = df_full.drop(random.sample(range(0, df_full.shape[0]), 500)) # Рандомно выкидываю 500 строк, чтобы проверять дозапись в 3-м задании

client = MongoClient('127.0.0.1', 27017) # ip-адресс и порт
db = client['hot_vacancies'] # указатель на БД, сама БД появляется только когда туда записаны какие-то данные (особенность Mongo)

hh = db.headhunter # создание "коллекции" внутри БД, это как таблица в SQL
sj = db.superjob

def initial_vacancy_to_mongo(df_file):
    """
    Функция производит первичное наполнение базы в 2 коллекции в зависимости от сайта, с которого собраны вакансии.

    На вход принимает файл с результатом парсинга в формате pandas dataframe, который нужно загрузить в базу.
    """
    # Метод insert_many принимает только словари, поэтому преобразую DataFrame методом to_dict()
    sj.insert_many(df_file[df_file['site_name']=='Superjob'].to_dict(orient='records'))
    hh.insert_many(df_file[df_file['site_name']=='HeadHunter (hh.ru)'].to_dict(orient='records'))

initial_vacancy_to_mongo(df_initial)

print(hh.count_documents({})) # Проверка, сколько добавилось
print(sj.count_documents({}))

def find_greater_than(min_sum):
    """
    Функция производит поиск и выводит на экран вакансии с заработной платой больше введенной суммы. 
    Поиск проводится по полям min_salary и max_salary.

    На вход принимает аргумент min_sum (целевую минимальную зарплату).
    На выходе печатает список вакансий на экран.
    """
    # 1-й словарь ищет, 2-й говорит какие выводить столбцы
    for vacancy in hh.find({'$or':[{'min_salary': {'$gte':min_sum}}, {'max_salary': {'$gte':min_sum}}]}, {'employer':1, '_id':0}):
        pprint(vacancy)

#find_greater_than(100000)

def update_if_doesnt_exist(new_df_file):
    """
    Функция добавляет в БД новые вакансии по 2 коллекциям в зависимости от сайта с вакансиями. Дубли вакансий игнорируются.

    На вход принимает файл в формате pandas dataframe/
    """
    for string in new_df_file.to_dict(orient='records'):
        if string['site_name']=='Superjob':
            sj.update_one({'vacancy_link': string['vacancy_link']}, {'$set': string}, upsert=True)
        elif string['site_name']=='HeadHunter (hh.ru)':
            hh.update_one({'vacancy_link': string['vacancy_link']}, {'$set': string}, upsert=True)

update_if_doesnt_exist(df_full)

print(hh.count_documents({})) # Проверка
print(sj.count_documents({}))

hh.create_index([('employer', pymongo.ASCENDING)]) # Сделаем также индексы
sj.create_index([('employer', pymongo.ASCENDING)])

hh.delete_many({})
sj.delete_many({})