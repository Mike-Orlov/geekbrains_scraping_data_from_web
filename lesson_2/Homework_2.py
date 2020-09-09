from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
import pandas as pd
import re

HH_SJ_SAVED_FILE_PATH = 'hh_sj_saved.csv'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/84.0.4147.135 Safari/537.36'}

class NextButtonError(Exception):
    def __init__(self, txt):
        self.txt = txt

def hh_vacancies_parser(target_vacancy): # можно поставить *args и заливать лист с вакансиями
    """
    Функция парсит вакансии с сайта https://hh.ru.

    На вход принимает название вакансии на русском языке. Возвращает список вакансий.
    Каждая отдельная вакансия в списке представлена словарем, в котором такие ключи:
    1. Название сайта
    2. Название вакансии
    3. Ссылка на вакансию
    4. Город, где вакансия размещена
    5. Название работодателя
    6. Ссылка на карточку работодателя
    7. Минимальная зарплата в вакансии
    8. максимальная зарплата в вакансии
    """
    hh_link = 'https://hh.ru'
    gh_session = requests.Session()
    whole_hh_link = hh_link + f'/search/vacancy?clusters=true&area=1&search_field=name&enable_snippets=true&salary=&st=searchVacancy&text={target_vacancy}'

    vacancies = []
    while True:
        response = gh_session.get(whole_hh_link, headers=headers, timeout=2)

        soup = bs(response.text,'html.parser')

        vacancies_list = soup.find_all('div', class_='vacancy-serp-item')
        # print(len(vacancies_list)) # Проверяем, сколько элементов собрали - в данном случае 50 на странице

        for vacancy in vacancies_list:
            vacancy_data = {}
            # vacancy.attrs # Если нужно просто получить все атрибуты
            vacancy_link = vacancy.find('a', class_='bloko-link HH-LinkModifier')['href']
            vacancy_name = vacancy.find('div', class_='vacancy-serp-item__info').getText()

            #vacancy_salary = vacancy.find('div', class_='vacancy-serp-item__sidebar').getText() # оставил для проверки, потом можно убрать
            vacancy_string = vacancy.find('div', class_='vacancy-serp-item__sidebar').getText()
            if '-' in vacancy_string:
                vacancy_min_salary = int(re.sub("[^0-9]", "", vacancy_string.split('-')[0]))
                vacancy_max_salary = int(re.sub("[^0-9]", "", vacancy_string.split('-')[1]))
            elif 'от ' in vacancy_string:
                vacancy_min_salary = int(re.sub("[^0-9]", "", vacancy_string))
                vacancy_max_salary = None
            elif 'до ' in vacancy_string:
                vacancy_max_salary = int(re.sub("[^0-9]", "", vacancy_string))
                vacancy_min_salary = None
            else:
                vacancy_min_salary = None
                vacancy_max_salary = None

            try:
                vacancy_employer = vacancy.find('a', class_='bloko-link bloko-link_secondary').getText()
            except:
                vacancy_employer = None
            try:
                employer_hh_link = hh_link + vacancy.find('a', class_='bloko-link bloko-link_secondary')['href']
            except:
                employer_hh_link = None
            vacancy_city = vacancy.find('span', class_='vacancy-serp-item__meta-info').getText().split(',')[0]

            vacancy_data['site_name'] = 'HeadHunter (hh.ru)'
            vacancy_data['vacancy_name'] = vacancy_name
            vacancy_data['vacancy_link'] = vacancy_link
            #vacancy_data['salary'] = vacancy_salary
            vacancy_data['vacancy_city'] = vacancy_city
            vacancy_data['employer'] = vacancy_employer
            vacancy_data['employer_hh_link'] = employer_hh_link
            vacancy_data['min_salary'] = vacancy_min_salary
            vacancy_data['max_salary'] = vacancy_max_salary

            vacancies.append(vacancy_data)
            
        next_button = soup.find('a', class_='bloko-button HH-Pager-Controls-Next HH-Pager-Control')
        if next_button == None:
            break
        elif next_button.getText() == 'дальше':
            whole_hh_link = hh_link + next_button['href']
        else:
            raise NextButtonError("Неизвестная проблема с обработкой кнопки Дальше")
    return vacancies

def sj_vacancies_parser(target_vacancy): # можно поставить *args и заливать лист с вакансиями
    """
    Функция парсит вакансии с сайта https://www.superjob.ru.

    На вход принимает название вакансии на русском языке. Возвращает список вакансий.
    Каждая отдельная вакансия в списке представлена словарем, в котором такие ключи:
    1. Название сайта
    2. Название вакансии
    3. Ссылка на вакансию
    4. Город, где вакансия размещена
    5. Название работодателя
    6. Ссылка на карточку работодателя
    7. Минимальная зарплата в вакансии
    8. максимальная зарплата в вакансии
    """
    sj_link = 'https://www.superjob.ru'
    gh_session = requests.Session()
    whole_sj_link = sj_link + f'/vacancy/search/?keywords={target_vacancy}&geo%5Bt%5D%5B0%5D=4'

    vacancies = []
    while True:
        response = gh_session.get(whole_sj_link, headers=headers)

        soup = bs(response.text,'html.parser')

        vacancies_list = soup.find_all('div', class_='f-test-vacancy-item') # все классы 'iJCa5 f-test-vacancy-item _1fma_ undefined _2nteL'
        # print(len(vacancies_list)) # Проверяем, сколько элементов собрали - в данном случае 50 на странице

        for vacancy in vacancies_list:
            vacancy_data = {}
            # vacancy.attrs # Если нужно просто получить все атрибуты
            vacancy_link = sj_link + vacancy.find('a', class_='_1UJAN')['href']
            # тут какие-то не уникальные классы 'icMQ_ _6AfZ9 f-test-link-Yuriskonsult _2JivQ _1UJAN', 
            # класс 'f-test-link-Yuriskonsult' завязан на вакансию, т.е. его нельзя будет применить на др. вакансиях
            vacancy_name = vacancy.find('div', class_='_3mfro PlM3e _2JVkc _3LJqf').getText()

            #vacancy_salary = vacancy.find('span', class_='f-test-text-company-item-salary').getText() # оставил для проверки, потом можно убрать
            vacancy_string = vacancy.find('span', class_='f-test-text-company-item-salary').getText()
            if '—' in vacancy_string:
                vacancy_min_salary = int(re.sub("[^0-9]", "", vacancy_string.split('—')[0]))
                vacancy_max_salary = int(re.sub("[^0-9]", "", vacancy_string.split('—')[1]))
            elif 'от ' in vacancy_string:
                vacancy_min_salary = int(re.sub("[^0-9]", "", vacancy_string))
                vacancy_max_salary = None
            elif 'до ' in vacancy_string:
                vacancy_max_salary = int(re.sub("[^0-9]", "", vacancy_string))
                vacancy_min_salary = None
            elif 'месяц' in vacancy_string:
                vacancy_max_salary = int(re.sub("[^0-9]", "", vacancy_string))
                vacancy_min_salary = int(re.sub("[^0-9]", "", vacancy_string))
            else:
                vacancy_min_salary = None
                vacancy_max_salary = None

            try:
                vacancy_employer = vacancy.find('span', class_='f-test-text-vacancy-item-company-name').getText()
            except:
                vacancy_employer = None
            try:
                employer_sj_link = sj_link + vacancy.find('a', class_='icMQ_')['href']
            except:
                employer_sj_link = None
            vacancy_city = vacancy.find('span', class_='f-test-text-company-item-location').findChildren(recursive=False)[2].getText().split(',')[0]

            vacancy_data['site_name'] = 'Superjob'
            vacancy_data['vacancy_name'] = vacancy_name
            vacancy_data['vacancy_link'] = vacancy_link
            #vacancy_data['salary'] = vacancy_salary
            vacancy_data['vacancy_city'] = vacancy_city
            vacancy_data['employer'] = vacancy_employer
            vacancy_data['employer_hh_link'] = employer_sj_link
            vacancy_data['min_salary'] = vacancy_min_salary
            vacancy_data['max_salary'] = vacancy_max_salary

            vacancies.append(vacancy_data)
            
        next_button = soup.find('a', class_='f-test-button-dalshe')
        if next_button == None:
            break
        elif next_button.getText() == 'Дальше':
            whole_sj_link = sj_link + next_button['href']
        else:
            raise NextButtonError("Неизвестная проблема с обработкой кнопки Дальше")
    return vacancies

target_vacancy = 'юрисконсульт'
hh_vacancy_dict = hh_vacancies_parser(target_vacancy)
sj_vacancy_dict = sj_vacancies_parser(target_vacancy)

df = pd.DataFrame(hh_vacancy_dict + sj_vacancy_dict)
print(df.head())
#df.to_csv(HH_SJ_SAVED_FILE_PATH, index=False, encoding='utf-8') # saving DF to CSV