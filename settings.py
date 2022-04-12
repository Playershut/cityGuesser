from random import choice

from discord.ext import commands
from discord import Embed

from data import db_session
from data.players import Player

import sqlalchemy

import requests

TOKEN = "OTUzNTY1NjM2MTYyOTA4MTgx.YjGbNA.MQf4IdIfQwn9unK1kk__yrW_N7c"
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
                               '$help, $h, $помощь, $п - для открытия этого списка')

start_embed = Embed(title='Угадайте город',
                    description='Используйте \n'
                                '$city_guess <НазваниеГорода>, \n'
                                '$cg <НазваниеГорода>, \n'
                                '$угадать_город <НазваниеГорода>, \n'
                                '$уг <НазваниеГорода> - для ответа  \n'
                                '$stop, $s, $стоп, $с - для остановки игры \n'
                                '$help, $h, $помощь, $п - для открытия списка команд')

game_in_progress_embed = Embed(title='Игра уже начата',
                               description='Используйте \n'
                                           '$city_guess <НазваниеГорода>, \n'
                                           '$cg <НазваниеГорода>, \n'
                                           '$угадать_город <НазваниеГорода>, \n'
                                           '$уг <НазваниеГорода> - для ответа  \n'
                                           '$stop, $s, $стоп, $с - для остановки игры \n'
                                           '$help, $h, $помощь, $п - для открытия списка команд')

not_city_get_embed = Embed(title='Ошибка в написании команды',
                           description='Используйте \n'
                                       '$city_guess <НазваниеГорода>, \n'
                                       '$cg <НазваниеГорода>, \n'
                                       '$угадать_город <НазваниеГорода>, \n'
                                       '$уг <НазваниеГорода> - для ответа  \n'
                                       '$stop, $s, $стоп, $с - для остановки игры \n'
                                       '$help, $h, $помощь, $п - для открытия списка команд')

not_game_embed = Embed(title='Нет игры в процессе',
                       description='Используйте \n'
                                   '$start_city_guessing, $scg, \n'
                                   '$начать_угадывание_города, $нуг - для начала игры  \n'
                                   '$help, $h, $помощь, $п - для открытия списка команд')

win_embed = Embed(title='Вы победили',
                  description='Используйте \n'
                              '$start_city_guessing, $scg, \n'
                              '$начать_угадывание_города, $нуг - для начала новой игры  \n'
                              '$help, $h, $помощь, $п - для открытия списка команд')

lose_embed = Embed(title='Вы проиграли',
                   description='Используйте \n'
                               '$start_city_guessing, $scg, \n'
                               '$начать_угадывание_города, $нуг - для начала новой игры  \n'
                               '$help, $h, $помощь, $п - для открытия списка команд')

game_stopped_embed = Embed(title='Игра успешно остановлена',
                           description='Используйте \n'
                                       '$start_city_guessing, $scg, \n'
                                       '$начать_угадывание_города, $нуг - для начала игры  \n'
                                       '$help, $h, $помощь, $п - для открытия списка команд')

CITIES = ['Москва', 'Санкт-Петербург', 'Оренбург']

URL = f'https://geocode-maps.yandex.ru/1.x/?apikey={apikey}&format=json&geocode='
IMG_URL = 'https://static-maps.yandex.ru/1.x/?'
