from random import choice

from discord.ext import commands
from discord import Embed

import requests

TOKEN = "OTUzNTY1NjM2MTYyOTA4MTgx.YjGbNA.JZOllvsvXK7eFbjAcONnt0O38ZU"
apikey = "40d1649f-0493-4b70-98ba-98533de7710b"

start_embed = Embed(title='Угадайте город',
                    description='Используйте \n'
                                '$city_guess <НазваниеГорода> - для ответа  \n'
                                '$stop - для остановки игры \n'
                                '$help - для открытия списка команд')

not_game_embed = Embed(title='Нет игры в процессе',
                       description='Используйте \n'
                                   '$start_city_guessing - для начала игры  \n'
                                   '$help - для открытия списка команд')

win_embed = Embed(title='Вы победили',
                  description='Используйте \n'
                              '$start_city_guessing - для начала новой игры  \n'
                              '$help - для открытия списка команд')

lose_embed = Embed(title='Вы проиграли',
                   description='Используйте \n'
                               '$start_city_guessing - для начала новой игры  \n'
                               '$help - для открытия списка команд')

cities = ['Москва', 'Санкт-Петербург', 'Оренбург']

url = f'https://geocode-maps.yandex.ru/1.x/?apikey={apikey}&format=json&geocode='
img_url = 'https://static-maps.yandex.ru/1.x/?'
