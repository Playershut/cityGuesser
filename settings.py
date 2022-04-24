from random import choice

from discord.ext import commands
from discord.utils import get
from discord import Embed, Color, ChannelType

from data.cities import Cities
from data import db_session
from data.players import Player
from data.settings import Settings
from data.ranks import Ranks
from data.roles import Roles

import sqlalchemy

from math import log

import requests

TOKEN = "OTUzNTY1NjM2MTYyOTA4MTgx.YjGbNA.DS0iB3ql2DiWreaJoM1pnuYtFUw"
APIKEY = "40d1649f-0493-4b70-98ba-98533de7710b"
ACCESS_TOKEN = "pk.eyJ1IjoicGxheWVyc2h1dCIsImEiOiJjbDJkMWhnZWIwY3pwM2Rtc3JybTRzbzJ3In0.mqzviFpeYpVedVzTX7NOHg"

help_embed = Embed(title='Помощь',
                   description='Используйте \n'
                               '$start_city_guessing, $scg, \n'
                               '$начать_угадывание_города, $нуг - для начала игры  \n'
                               '\n'
                               '$city_guess <НазваниеГорода>, \n'
                               '$cg <НазваниеГорода>, \n'
                               '$угадать_город <НазваниеГорода>, \n'
                               '$уг <НазваниеГорода> - для ответа  \n'
                               '\n'
                               '$shop, $sh, $магазин, $м - для открытия магазина ролей \n'
                               '\n'
                               '$buy <НазваниеРоли>,\n'
                               '$b <НазваниеРоли>,\n'
                               '$купить <НазваниеРоли>,\n'
                               '$к <НазваниеРоли> - для покупки роли'
                               '\n'
                               '$stop, $s, $стоп, $с - для остановки игры \n'
                               '\n'
                               '$profile, $p, $профиль $пр - для открытия своего профиля \n'
                               '\n'
                               '$help, $h, $помощь, $п - для открытия этого списка \n'
                               '\n'
                               '$admin_help, $ah, $админ_помощь, $ап - для открытия списка команд администраторов',
                   color=Color.dark_gold())

admin_help_embed = Embed(title='Помощь',
                         description='Используйте \n'
                                     '$add_role <IDРоли> <Цена>,\n'
                                     '$ar <IDРоли> <Цена>,\n'
                                     '$добавить_роль <IDРоли> <Цена>,\n'
                                     '$др <IDРоли> <Цена> - для добавления роли в магазин \n'
                                     '\n'
                                     '$delete_role <IDРоли>,\n'
                                     '$dr <IDРоли>,\n'
                                     '$удалить_роль <IDРоли>,\n'
                                     '$ур <IDРоли> - для удаления роли из магазина\n'
                                     '\n'
                                     '$add_city <НазваниеГорода>,\n'
                                     '$ad <НазваниеГорода>,\n'
                                     '$добавить_город <НазваниеГорода>,\n'
                                     '$дг <НазваниеГорода> - для добавления города в базу данных игры\n'
                                     '\n'
                                     '$delete_city <НазваниеГорода>,\n'
                                     '$dc <НазваниеГорода>,\n'
                                     '$удалить_город <НазваниеГорода>,\n'
                                     '$уг <НазваниеГорода> - для удаления города из базы данных игры\n'
                                     '\n'
                                     '$cities_list, $cl,\n'
                                     '$список_городов, $сг - для открытия списка городов в юазе данных игры\n'
                                     '\n'
                                     '$city_image <НазваниеГорода>,\n'
                                     '$ci <НазваниеГорода>,\n'
                                     '$изображение_города <НазваниеГорода>,\n'
                                     '$иг <НазваниеГорода> - показывает изображение города с карты без названий населенных пунктов'
                                     '\n'
                                     '$admin_help, $ah, $админ_помощь, $ап - для открытия этого списка',
                         color=Color.dark_gold())

start_embed = Embed(title='Угадайте город',
                    description='Используйте \n'
                                '$city_guess <НазваниеГорода>, \n'
                                '$cg <НазваниеГорода>, \n'
                                '$угадать_город <НазваниеГорода>, \n'
                                '$уг <НазваниеГорода> - для ответа  \n'
                                '\n'
                                '$stop, $s, $стоп, $с - для остановки игры \n'
                                '\n'
                                '$help, $h, $помощь, $п - для открытия списка команд',
                    color=Color.blurple())

game_in_progress_embed = Embed(title='Игра уже начата',
                               description='Используйте \n'
                                           '$city_guess <НазваниеГорода>, \n'
                                           '$cg <НазваниеГорода>, \n'
                                           '$угадать_город <НазваниеГорода>, \n'
                                           '$уг <НазваниеГорода> - для ответа  \n'
                                           '\n'
                                           '$stop, $s, $стоп, $с - для остановки игры \n'
                                           '\n'
                                           '$help, $h, $помощь, $п - для открытия списка команд',
                               color=Color.greyple())

not_city_get_embed = Embed(title='Ошибка в написании команды',
                           description='Используйте \n'
                                       '$city_guess <НазваниеГорода>, \n'
                                       '$cg <НазваниеГорода>, \n'
                                       '$угадать_город <НазваниеГорода>, \n'
                                       '$уг <НазваниеГорода> - для ответа  \n'
                                       '\n'
                                       '$stop, $s, $стоп, $с - для остановки игры \n'
                                       '\n'
                                       '$help, $h, $помощь, $п - для открытия списка команд',
                           color=Color.greyple())

not_game_embed = Embed(title='Нет игры в процессе',
                       description='Используйте \n'
                                   '$start_city_guessing, $scg, \n'
                                   '$начать_угадывание_города, $нуг - для начала игры  \n'
                                   '\n'
                                   '$help, $h, $помощь, $п - для открытия списка команд',
                       color=Color.greyple())

win_embed = Embed(title='Вы победили',
                  description='Используйте \n'
                              '$start_city_guessing, $scg, \n'
                              '$начать_угадывание_города, $нуг - для начала новой игры  \n'
                              '\n'
                              '$help, $h, $помощь, $п - для открытия списка команд',
                  color=Color.green())

lose_embed = Embed(title='Вы проиграли',
                   description='Используйте \n'
                               '$start_city_guessing, $scg, \n'
                               '$начать_угадывание_города, $нуг - для начала новой игры  \n'
                               '\n'
                               '$help, $h, $помощь, $п - для открытия списка команд',
                   color=Color.red())

game_stopped_embed = Embed(title='Игра успешно остановлена',
                           description='Используйте \n'
                                       '$start_city_guessing, $scg, \n'
                                       '$начать_угадывание_города, $нуг - для начала игры  \n'
                                       '\n'
                                       '$help, $h, $помощь, $п - для открытия списка команд',
                           color=Color.darker_grey())

level_up_embed = Embed(title='Ваш уровень повышен',
                       description='Поздравляем с повышением уровня!',
                       color=Color.green())


def get_formatted_city_name(city):
    response = requests.get(URL + city).json()
    response = response['response']['GeoObjectCollection']['featureMember'][0]
    formatted_city_name = response['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
    return formatted_city_name


URL = f'https://geocode-maps.yandex.ru/1.x/?apikey={APIKEY}&format=json&geocode='
IMG_URL = f'https://api.mapbox.com/styles/v1/playershut/cl2d1jn9y000e14ldtjdkygk3/static/'
