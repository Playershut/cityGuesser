import discord

from settings import *


class MOBotClient(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.settings = DB_SESS.query(Settings).first()

    # используется для отправки карточки со списком команд
    @commands.command(name='help', aliases=['h', 'помощь', 'п'])
    async def help(self, ctx):
        await ctx.channel.send(embed=help_embed)

    #  используется для начала игры
    @commands.command(name='start_city_guessing', aliases=['scg', 'начать_угадывание_города', 'нуг'])
    async def start_city_guessing(self, ctx):
        if not self.settings.game_in_progress:
            self.settings.chosen_city = choice(CITIES)
            self.settings.game_in_progress = True
            DB_SESS.commit()
            response = requests.get(URL + self.settings.chosen_city).json()
            response = response['response']['GeoObjectCollection']['featureMember'][0]
            response = response['GeoObject']['boundedBy']['Envelope']
            lll_param = ','.join(response['lowerCorner'].split())
            ull_param = ','.join(response['upperCorner'].split())
            l_param = choice(['map', 'sat,skl'])
            start_embed.set_image(url=f'{IMG_URL}bbox={lll_param}~{ull_param}&l={l_param}')
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
                if get_formatted_city_name('+'.join(city)) == \
                        get_formatted_city_name(self.settings.chosen_city):
                    await self.player_stats_calc(ctx.author.id)
                    await ctx.channel.send(embed=win_embed)
                else:
                    await ctx.channel.send(embed=lose_embed)

                self.settings.chosen_city = ''
                self.settings.game_in_progress = False
                DB_SESS.commit()
            else:
                await ctx.channel.send(embed=not_city_get_embed)

    # используется для подсчета и изменения статистики игрока
    async def player_stats_calc(self, author_id):
        player = DB_SESS.query(Player).filter(Player.user_id == author_id).first()
        player.money += 10
        player.cities_guessed += 1
        player.level = len(format(player.cities_guessed, 'b'))
        player.rank = f'{DB_SESS.query(Ranks.rank).filter(Ranks.id == player.level % RANKS_COUNT).first()[0]}' \
                      f'{"+" * (player.level // RANKS_COUNT)}'
        DB_SESS.commit()

    # используется для отображения статистики игрока
    @commands.command(name='profile', aliases=['p', 'профиль', 'пр'])
    async def profile(self, ctx):
        player = DB_SESS.query(Player).filter(Player.user_id == ctx.author.id).first()
        await ctx.channel.send(embed=Embed(title=f'Профиль игрока {ctx.author.display_name}',
                                           description=f'Уровень: {player.level}\n'
                                                       f'Ранг: {player.rank}\n'
                                                       f'Угадано городов: {player.cities_guessed}\n'
                                                       f'Баланс: {player.money}',
                                           color=Color.dark_teal()))

    # используется для остановки игры
    @commands.command(name='stop', aliases=['s', 'стоп', 'с'])
    async def stop(self, ctx):
        self.settings.chosen_city = ''
        self.settings.game_in_progress = False
        DB_SESS.commit()
        await ctx.channel.send(embed=game_stopped_embed)

    @commands.command(name='add_role', aliases=['ar', 'добавить_роль', 'др'])
    async def add_role(self, ctx, role_id, cost):
        role = Roles()
        role.role_id = role_id
        role.cost = cost
        DB_SESS.add(role)
        DB_SESS.commit()
        role = get(ctx.guild.roles, id=role_id)
        await ctx.channel.send(embed=Embed(title='Роль была добавлена',
                                           description=f'Роль {role.mention} была добавлена'))

    @commands.command(name='shop', aliases=['sh', 'магазин', 'м'])
    async def shop(self, ctx):
        shop_desc = ''
        for role_id, cost in DB_SESS.query(Roles.role_id, Roles.cost).all():
            shop_desc += f'{get(ctx.guild.roles, id=role_id).mention} - {cost}$' + '\n'
        await ctx.channel.send(embed=Embed(title='Магазин ролей',
                                           description=shop_desc))

    @commands.command(name='buy', aliases=['b', 'купить', 'к'])
    async def buy(self, ctx, *role):
        await ctx.author.add_roles(get(ctx.guild.roles, name=' '.join(role)))
        await ctx.channel.send(embed=Embed(title='Вы купили роль',
                                           description=f'Вы купили роль '
                                                       f'{get(ctx.guild.roles, name=" ".join(role)).mention}'))


if __name__ == '__main__':
    db_session.global_init("db/city_guesser.db")
    DB_SESS = db_session.create_session()
    RANKS_COUNT = DB_SESS.query(Ranks).count()
    BOT = commands.Bot(command_prefix='$', help_command=None)
    BOT.add_cog(MOBotClient(BOT))
    BOT.run(TOKEN)
