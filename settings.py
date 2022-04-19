from random import choice

from discord.ext import commands
from discord import Embed, Color

from data import db_session
from data.players import Player
from data.settings import Settings
from data.ranks import Ranks

import sqlalchemy

import requests

TOKEN = "OTUzNTY1NjM2MTYyOTA4MTgx.YjGbNA.DS0iB3ql2DiWreaJoM1pnuYtFUw"
apikey = "40d1649f-0493-4b70-98ba-98533de7710b"

help_embed = Embed(title='Помощь',
                   description='Используйте \n'
                               '$start_city_guessing, $scg, \n'
                               '$начать_угадывание_города, $нуг - для начала игры  \n'
                               '$city_guess <НазваниеГорода>, \n'
                               '$cg <НазваниеГорода>, \n'
                               '$угадать_город <НазваниеГорода>, \n'
                               '$уг <НазваниеГорода> - для ответа  \n'
                               '$stop, $s, $стоп, $с - для остановки игры \n'
                               '$help, $h, $помощь, $п - для открытия этого списка',
                   color=Color.dark_gold())

start_embed = Embed(title='Угадайте город',
                    description='Используйте \n'
                                '$city_guess <НазваниеГорода>, \n'
                                '$cg <НазваниеГорода>, \n'
                                '$угадать_город <НазваниеГорода>, \n'
                                '$уг <НазваниеГорода> - для ответа  \n'
                                '$stop, $s, $стоп, $с - для остановки игры \n'
                                '$help, $h, $помощь, $п - для открытия списка команд',
                    color=Color.blurple())

game_in_progress_embed = Embed(title='Игра уже начата',
                               description='Используйте \n'
                                           '$city_guess <НазваниеГорода>, \n'
                                           '$cg <НазваниеГорода>, \n'
                                           '$угадать_город <НазваниеГорода>, \n'
                                           '$уг <НазваниеГорода> - для ответа  \n'
                                           '$stop, $s, $стоп, $с - для остановки игры \n'
                                           '$help, $h, $помощь, $п - для открытия списка команд',
                               color=Color.greyple())

not_city_get_embed = Embed(title='Ошибка в написании команды',
                           description='Используйте \n'
                                       '$city_guess <НазваниеГорода>, \n'
                                       '$cg <НазваниеГорода>, \n'
                                       '$угадать_город <НазваниеГорода>, \n'
                                       '$уг <НазваниеГорода> - для ответа  \n'
                                       '$stop, $s, $стоп, $с - для остановки игры \n'
                                       '$help, $h, $помощь, $п - для открытия списка команд',
                           color=Color.greyple())

not_game_embed = Embed(title='Нет игры в процессе',
                       description='Используйте \n'
                                   '$start_city_guessing, $scg, \n'
                                   '$начать_угадывание_города, $нуг - для начала игры  \n'
                                   '$help, $h, $помощь, $п - для открытия списка команд',
                       color=Color.greyple())

win_embed = Embed(title='Вы победили',
                  description='Используйте \n'
                              '$start_city_guessing, $scg, \n'
                              '$начать_угадывание_города, $нуг - для начала новой игры  \n'
                              '$help, $h, $помощь, $п - для открытия списка команд',
                  color=Color.green())

lose_embed = Embed(title='Вы проиграли',
                   description='Используйте \n'
                               '$start_city_guessing, $scg, \n'
                               '$начать_угадывание_города, $нуг - для начала новой игры  \n'
                               '$help, $h, $помощь, $п - для открытия списка команд',
                   color=Color.red())

game_stopped_embed = Embed(title='Игра успешно остановлена',
                           description='Используйте \n'
                                       '$start_city_guessing, $scg, \n'
                                       '$начать_угадывание_города, $нуг - для начала игры  \n'
                                       '$help, $h, $помощь, $п - для открытия списка команд',
                           color=Color.darker_grey())

CITIES = ['Москва', 'Санкт-Петербург', 'Оренбург', 'Улан-Удэ']

def get_formatted_city_name(city):
    response = requests.get(URL + city).json()
    response = response['response']['GeoObjectCollection']['featureMember'][0]
    formatted_city_name = response['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
    return formatted_city_name


URL = f'https://geocode-maps.yandex.ru/1.x/?apikey={apikey}&format=json&geocode='
IMG_URL = 'https://static-maps.yandex.ru/1.x/?'
