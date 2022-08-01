import requests 
import fake_useragent
import json
import re
import csv
import time
from bs4 import BeautifulSoup as BS

def information_anime(url: str, header: dict, link: str) -> None:
    response: requests = requests.get(f'{link}{url}', headers=header).text
    
    # Поиск инфы на странице
    soup: BS = BS(response, 'lxml')
    block: BS = soup.find('div', {'class': 'media mb-3 d-none d-block d-md-flex'})
    anime_info: BS = block.find('dl', {'class': 'row'}) 
    anime_title: BS = block.find('h1').text
    rating: BS = block.find('span', {'class': 'rating-value'}).text
    type: BS = block.find('dd', {'class': 'col-6 col-sm-8 mb-1'}).text
    release: BS = anime_info.find('span').text
    
    # Жанры выдают огромное количество пробелов между собой, из-за чего их приходиться удалить для корректного отображения
    genre: BS = block.find('dd', {'class': 'col-6 col-sm-8 mb-1 overflow-h'}).text
    correct_genre: str = " ".join(genre.split())

    # Запись полученной инфы в csv файлик
    with open('result.csv', 'a', encoding='cp1251', newline='') as file:
        writer: csv = csv.writer(file, delimiter=';')
        writer.writerow(
            ['', anime_title, rating, type, release, correct_genre]
        )
        print("Записал")

    # Задержка, чтобы избежать ошибку страницы 429
    time.sleep(0.5)

# Основная функция по сбору информации
def collect_data(username: str) -> None:
    ua: str = fake_useragent.UserAgent().random
    link: str = "https://animego.org"
    pagination: int = 2

    # Набор данных чтобы избежать защиты ddos-guard.net которая установлена на сайте
    data: dict = {
        'type': 'mylist',
        'page': f'{pagination}'
    }

    headers: dict = {
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': '__ddg1_=U3bS0dfYWT11XpVP8iv6; device_view=full',
        'sec-fetch-site': 'same-origin',
        'user-agent': ua,
        'x-requested-with': 'XMLHttpRequest'
    }

    response: requests = requests.get(f'{link}/user/{username}/mylist/anime', headers=headers).text
    soup: BS = BS(response, 'lxml')
    table_body: str = soup.find('tbody')

    # Проверка на несуществующего пользователя
    try:
    # Перебор полученных данных в таблице, откуда вытаскиваются ссылки на аниме и передаются на дальнейший поиск
        for anime in table_body:
            anime_link: str = anime.find('a').get('href')
            information_anime(anime_link, headers, link)
    except:
        answer: str = input("Пользователя не существует, хотите попробовать ещё раз? (y/n)")
        if answer.lower() == 'y':
            main()
        else:
            exit()
    """
    Тот же самый поиск для данных которые подгружались динамические через ajax в виде закодированного JSON-файла.
    Из-за чего пришлось декодить его, вытаскивать из словаря по ключу 'content', который передавал всю HTML-страничку 
    одним параметром, что вызвало дополнительные сложности которые решались через формирование регулярных строк и поиска 
    ссылок с передачей их в туже функцию для получения информации о самом аниме
    """
    search: bool = True
    while search:
        # Проверка на окончание JSON файла, чтобы остановить перебор
        try:
            paginate: str = requests.get(f'{link}/user/{username}/mylist/anime?type=mylist&page={pagination}', headers=headers, data=data).text 
            jsons: dict = json.loads(paginate)
            parse: str = jsons['content']
            pattern: re = r'href="(.+?)"'
            result: list = re.findall(pattern, parse)
            links: list = result[::3]
            
            for ani in links:
                url: str = ani
                information_anime(url, headers, link)

            pagination += 1
        except json.decoder.JSONDecodeError:
            search = False

    print("Закончил поиск")

def main() -> None:
    username: str = input("Nickname:")
    
    # Создание csv файла с его заголовками
    with open('result.csv', 'a', encoding='cp1251', newline='') as file:
        writer: csv = csv.writer(file, delimiter=';')
        writer.writerow(
            [f'{username}', 'НАЗВАНИЕ', 'РЕЙТИНГ', 'ТИП', 'ДАТА ВЫХОДА', 'ЖАНР']
        )

    collect_data(username)

if __name__ == '__main__':
    main()
    