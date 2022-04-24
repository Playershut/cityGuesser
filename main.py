from settings import *


class MOBotClient(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.settings = DB_SESS.query(Settings).first()

    # используется для отправки карточки со списком команд
    @commands.command(name='help', aliases=['h', 'помощь', 'п'])
    async def help(self, ctx):
        await ctx.channel.send(embed=help_embed)

    # используется для отправки карточки со списком команд l
    @commands.command(name='admin_help', aliases=['ah', 'админ_помощь', 'ап'])
    @commands.has_permissions()
    async def admin_help(self, ctx):
        await ctx.channel.send(embed=admin_help_embed)

    #  используется для начала игры
    @commands.command(name='start_city_guessing', aliases=['scg', 'начать_угадывание_города', 'нуг'])
    async def start_city_guessing(self, ctx):
        if not self.settings.game_in_progress:
            self.settings.chosen_city = choice(DB_SESS.query(Cities.city).all())[0]
            self.settings.game_in_progress = True
            DB_SESS.commit()

            response = requests.get(URL + self.settings.chosen_city).json()
            response = response['response']['GeoObjectCollection']['featureMember'][0]
            response = response['GeoObject']['boundedBy']['Envelope']

            west, south = response['lowerCorner'].split()
            east, north = response['upperCorner'].split()

            start_embed.set_image(
                url=f'{IMG_URL}[{west},{south},{east},{north}]/512x512?access_token={ACCESS_TOKEN}')
            await ctx.channel.send(embed=start_embed)
        else:
            await ctx.channel.send(embed=game_in_progress_embed)

    # используется для угадывания города игроком
    @commands.command(name='city_guess', aliases=['cg', 'угадать_город', 'уг'])
    async def city_guess(self, ctx, *city):
        if not DB_SESS.query(Player).filter(Player.user_id == ctx.author.id).first():
            player = Player()
            player.user_id = ctx.author.id
            player.money = 0
            player.cities_guessed = 0
            player.level = 0
            player.rank = 'Newbie'
            DB_SESS.add(player)
            DB_SESS.commit()

        if not self.settings.game_in_progress:
            await ctx.channel.send(embed=not_game_embed)

        else:
            if city:
                if get_formatted_city_name('+'.join(city)) == get_formatted_city_name(
                        self.settings.chosen_city):
                    await self.player_stats_calc(ctx, ctx.author.id)
                    await ctx.channel.send(embed=win_embed)
                else:
                    await ctx.channel.send(embed=lose_embed)

                self.settings.chosen_city = ''
                self.settings.game_in_progress = False
                DB_SESS.commit()
            else:
                await ctx.channel.send(embed=not_city_get_embed)

    # используется для подсчета и изменения статистики игрока
    async def player_stats_calc(self, ctx, author_id):
        player = DB_SESS.query(Player).filter(Player.user_id == author_id).first()
        player.cities_guessed += 1
        last_player_level = player.level
        if player.level >= 9:
            player.level = round(log(player.cities_guessed - 10, 1.5))
        else:
            player.level = round(log(player.cities_guessed, 1.5))
        player.money += 10 + (player.level - 1)
        player.rank = f'{DB_SESS.query(Ranks.rank).filter(Ranks.id == player.level % RANKS_COUNT).first()[0]}' \
                      f'{"+" * (player.level // RANKS_COUNT)}'
        DB_SESS.commit()
        if last_player_level < player.level:
            player.money += player.cities_guessed
            await ctx.channel.send(embed=level_up_embed)

    # используется для отображения статистики игрока
    @commands.command(name='profile', aliases=['p', 'профиль', 'пр'])
    async def profile(self, ctx):
        if not DB_SESS.query(Player).filter(Player.user_id == ctx.author.id).first():
            player = Player()
            player.user_id = ctx.author.id
            player.money = 0
            player.cities_guessed = 0
            player.level = 0
            player.rank = 'Newbie'
            DB_SESS.add(player)
            DB_SESS.commit()

        player = DB_SESS.query(Player).filter(Player.user_id == ctx.author.id).first()
        profile_embed = Embed(title=f'Профиль игрока {ctx.author.display_name}',
                              description=f'Уровень: {player.level}\n'
                                          f'Ранг: {player.rank}\n'
                                          f'Угадано городов: {player.cities_guessed}\n'
                                          f'Баланс: {player.money}\n'
                                          f'Городов до следующего уровня: '
                                          f'{round(1.5 ** (player.level + 1) - player.cities_guessed)}',
                              color=Color.dark_teal())
        profile_embed.set_thumbnail(url=ctx.author.avatar_url)
        await ctx.channel.send(embed=profile_embed)

    # используется для остановки игры
    @commands.command(name='stop', aliases=['s', 'стоп', 'с'])
    async def stop(self, ctx):
        self.settings.chosen_city = ''
        self.settings.game_in_progress = False
        DB_SESS.commit()
        await ctx.channel.send(embed=game_stopped_embed)

    # используется для добавления роли в магазин
    @commands.command(name='add_role', aliases=['ar', 'добавить_роль', 'др'])
    @commands.has_permissions(manage_roles=True)
    async def add_role(self, ctx, role_id=None, cost=None):
        if ctx.channel.type == ChannelType.private:
            await ctx.send('Данную команду нельзя использовать в личных сообщениях!')
            return

        if not role_id:
            await ctx.send('Не указан ключ роли!')
        elif not cost:
            await ctx.send('Не указана цена роли!')
        else:
            if not DB_SESS.query(Roles).filter(Roles.role_id == role_id).first():
                role = Roles()
                role.role_id = role_id
                role.cost = cost
                role.guild_id = ctx.guild.id
                DB_SESS.add(role)
                DB_SESS.commit()
                await ctx.channel.send(embed=Embed(title='Роль была добавлена',
                                                   description=f'Роль {get(ctx.guild.roles, id=int(role_id)).mention}'
                                                               f' была добавлена',
                                                   color=Color.green()))
            else:
                await ctx.channel.send(embed=Embed(title='Роль не была добавлена',
                                                   description=f'Роль {get(ctx.guild.roles, id=int(role_id)).mention}'
                                                               f' уже есть в магазине',
                                                   color=Color.red()))

    # используется для удаления роли из магазина
    @commands.command(name='delete_role', aliases=['dr', 'удалить_роль', 'ур'])
    @commands.has_permissions(manage_roles=True)
    async def delete_role(self, ctx, role_id=None):
        if ctx.channel.type == ChannelType.private:
            await ctx.send('Данную команду нельзя использовать в личных сообщениях!')
            return

        if not role_id:
            await ctx.send('Не указан ключ роли!')
        else:
            if DB_SESS.query(Roles).filter(Roles.role_id == role_id).first():
                role = DB_SESS.query(Roles).filter(Roles.role_id == role_id).order_by(-Roles.id).first()
                DB_SESS.delete(role)
                DB_SESS.commit()
                await ctx.channel.send(embed=Embed(title='Роль была удалена',
                                                   description=f'Роль {get(ctx.guild.roles, id=int(role_id)).mention}'
                                                               f' была удалена',
                                                   color=Color.green()))
            else:
                await ctx.channel.send(embed=Embed(title='Роль не была удалена',
                                                   description=f'Роли {get(ctx.guild.roles, id=int(role_id)).mention}'
                                                               f' нет в магазине',
                                                   color=Color.red()))

    # используется для отправки ролей, которые могут купить игроки
    @commands.command(name='shop', aliases=['sh', 'магазин', 'м'])
    async def shop(self, ctx):
        if ctx.channel.type == ChannelType.private:
            await ctx.send('Данную команду нельзя использовать в личных сообщениях!')
            return

        shop_desc = ''
        for role_id, cost in DB_SESS.query(Roles.role_id, Roles.cost).order_by(Roles.cost).all():
            shop_desc += f'{get(ctx.guild.roles, id=role_id).mention} - {cost}$' + '\n'
        await ctx.channel.send(embed=Embed(title='Магазин ролей',
                                           description=shop_desc,
                                           color=Color.gold()))

    # используется для покупки роли из магазина
    @commands.command(name='buy', aliases=['b', 'купить', 'к'])
    async def buy(self, ctx, *role):
        if ctx.channel.type == ChannelType.private:
            await ctx.send('Данную команду нельзя использовать в личных сообщениях!')
            return

        if get(ctx.guild.roles, name=' '.join(role)) in ctx.author.roles:
            await ctx.send('У Вас уже есть эта роль!')
            return

        player = DB_SESS.query(Player).filter(Player.user_id == ctx.author.id).first()
        role_cost = DB_SESS.query(Roles.cost).filter(
            Roles.role_id == get(ctx.guild.roles, name=' '.join(role)).id).first()[0]
        if player.money >= role_cost:
            player.money -= role_cost
            DB_SESS.commit()
            await ctx.author.add_roles(get(ctx.guild.roles, name=' '.join(role)))
            await ctx.channel.send(embed=Embed(title='Вы купили роль',
                                               description=f'Вы купили роль '
                                                           f'{get(ctx.guild.roles, name=" ".join(role)).mention}',
                                               color=Color.green()))
        else:
            await ctx.channel.send(embed=Embed(title='Не удалось купить роль',
                                               description=f'Не удалось купить роль '
                                                           f'{get(ctx.guild.roles, name=" ".join(role)).mention}',
                                               color=Color.red()))

    # используется для добавления города в БД
    @commands.command(name='add_city', aliases=['ac', 'добавить_город', 'дг'])
    @commands.has_permissions(administrator=True)
    async def add_city(self, ctx, *city):
        if not DB_SESS.query(Cities).filter(Cities.city == '+'.join(city).lower()).first():
            city_db = Cities()
            city_db.city = '+'.join(city).lower()
            DB_SESS.add(city_db)
            DB_SESS.commit()
            await ctx.channel.send(embed=Embed(title='Город был добавлен',
                                               description=f'Город "{" ".join(city)}" был добавлен в '
                                                           f'базу данных игры',
                                               color=Color.green()))
        else:
            await ctx.channel.send(embed=Embed(title='Город не был добавлен',
                                               description=f'Город "{" ".join(city)}" уже есть в '
                                                           f'базе данных игры',
                                               color=Color.red()))

    # используется для удаления города из БД
    @commands.command(name='delete_city', aliases=['dc', 'удалить_город', 'удг'])
    @commands.has_permissions(administrator=True)
    async def delete_city(self, ctx, *city):
        if DB_SESS.query(Cities).filter(Cities.city == '+'.join(city).lower()).first():
            city_db = DB_SESS.query(Cities).filter(Cities.city == '+'.join(city).lower()).order_by(
                -Cities.id).first()
            DB_SESS.delete(city_db)
            DB_SESS.commit()
            await ctx.channel.send(embed=Embed(title='Город был удален',
                                               description=f'Город "{" ".join(city)}" был удален из '
                                                           f'базы данных игры',
                                               color=Color.green()))
        else:
            await ctx.channel.send(embed=Embed(title='Город не был удален',
                                               description=f'Города "{" ".join(city)}" нет в '
                                                           f'базе данных игры',
                                               color=Color.red()))

    # используется для отображения списка городов из БД
    @commands.command(name='cities_list', aliases=['cl', 'список_городов', 'сг'])
    @commands.has_permissions(administrator=True)
    async def cities_list(self, ctx):
        cities_list = []
        [cities_list.append(city[0]) for city in DB_SESS.query(Cities.city).order_by(Cities.city).all()]
        cities_list = '\n'.join(cities_list)
        await ctx.channel.send(embed=Embed(title='Список городов',
                                           description=cities_list,
                                           color=Color.darker_grey()))

    # используется для отображения изображения города с карты
    @commands.command(name='city_image', aliases=['ci', 'изображение_города', 'иг'])
    @commands.has_permissions(administrator=True)
    async def city_image(self, ctx, *city):
        response = requests.get(URL + '+'.join(city).lower()).json()
        response = response['response']['GeoObjectCollection']['featureMember'][0]
        response = response['GeoObject']['boundedBy']['Envelope']

        west, south = response['lowerCorner'].split()
        east, north = response['upperCorner'].split()

        city_image_embed = Embed(title='Изображение города на карте',
                                 description=f'{" ".join(city)} на карте',
                                 color=Color.dark_magenta())
        city_image_embed.set_image(
            url=f'{IMG_URL}[{west},{south},{east},{north}]/512x512?access_token={ACCESS_TOKEN}')
        await ctx.channel.send(embed=city_image_embed)

    # используется для отображения общего топа 10 игры по угаданным городам
    @commands.command(name='top', aliases=['t','топ','т'])
    async def top(self, ctx):
        players_ids = DB_SESS.query(Player.user_id).order_by(-Player.cities_guessed).all()
        print(players_ids)
        max_top_num = len(players_ids) if len(players_ids) < 10 else 10
        top_desc = ''
        for i in range(0, max_top_num):
            top_desc += f'{i + 1}. {await BOT.fetch_user(players_ids[i][0])}\n'
        await ctx.channel.send(embed=Embed(title='Общий топ по угаданным городам',
                                           description=top_desc,
                                           color=Color.dark_purple()))


if __name__ == '__main__':
    db_session.global_init("db/city_guesser.db")
    DB_SESS = db_session.create_session()
    RANKS_COUNT = DB_SESS.query(Ranks).count()
    BOT = commands.Bot(command_prefix='$', help_command=None)
    BOT.add_cog(MOBotClient(BOT))
    BOT.run(TOKEN)
