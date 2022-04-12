from settings import *


class MOBotClient(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.chosen_city = ''
        self.game_in_progress = False

    # используется для отправки карточки со списком команд
    @commands.command(name='help', aliases=['h', 'помощь', 'п'])
    async def help(self, ctx):
        await ctx.channel.send(embed=help_embed)

    #  используется для начала игры
    @commands.command(name='start_city_guessing', aliases=['scg', 'начать_угадывание_города', 'нуг'])
    async def start_city_guessing(self, ctx):
        if not self.game_in_progress:
            self.chosen_city = choice(CITIES)
            self.game_in_progress = True
            response = requests.get(URL + self.chosen_city).json()
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
    async def city_guess(self, ctx, city=None):
        if not self.game_in_progress:
            await ctx.channel.send(embed=not_game_embed)

        if city:
            if city.lower() == self.chosen_city.lower():
                await self.player_stats_calc(ctx.author.id)
                await ctx.channel.send(embed=win_embed)
            else:
                await ctx.channel.send(embed=lose_embed)

            self.chosen_city = ''
            self.game_in_progress = False
        else:
            await ctx.channel.send(embed=not_city_get_embed)

    # используется для подсчета и изменения статистики игрока
    async def player_stats_calc(self, author_id):
        if not DB_SESS.query(Player).filter(Player.user_id == author_id).first():
            player = Player()
            player.user_id = author_id
            player.money = 0
            player.cities_guessed = 0
            player.level = 0
            player.rank = 'Newbie'
            DB_SESS.add(player)
            DB_SESS.commit()

        player = DB_SESS.query(Player).filter(Player.user_id == author_id).first()
        player.money += 10
        player.cities_guessed += 1
        player.level = len(format(player.cities_guessed, 'b'))
        DB_SESS.commit()

    # используется для отображения статистики игрока
    @commands.command(name='profile', aliases=['p', 'профиль', 'пр'])
    async def profile(self, ctx):
        player = DB_SESS.query(Player).filter(Player.user_id == ctx.author.id).first()
        await ctx.channel.send(embed=Embed(title=f'Профиль игрока {ctx.author.display_name}',
                                           description=f'Уровень: {player.level}\n'
                                                       f'Ранг: {player.rank}\n'
                                                       f'Угадано городов: {player.cities_guessed}\n'
                                                       f'Баланс: {player.money}'))

    # используется для остановки игры
    @commands.command(name='stop', aliases=['s', 'стоп', 'с'])
    async def stop(self, ctx):
        self.chosen_city = ''
        self.game_in_progress = False
        await ctx.channel.send(embed=game_stopped_embed)


if __name__ == '__main__':
    db_session.global_init("db/players.db")
    DB_SESS = db_session.create_session()
    bot = commands.Bot(command_prefix='$', help_command=None)
    bot.add_cog(MOBotClient(bot))
    bot.run(TOKEN)
