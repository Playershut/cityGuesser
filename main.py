from settings import *


class MOBotClient(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.chosen_city = ''
        self.game_in_progress = False

    @commands.command(name='start_city_guessing')
    async def start_city_guessing(self, ctx):
        self.chosen_city = choice(cities)
        self.game_in_progress = True
        response = requests.get(url + self.chosen_city).json()
        rspns = response['response']['GeoObjectCollection']['featureMember'][0]
        rspns = rspns['GeoObject']['boundedBy']['Envelope']
        lll_param = ','.join(rspns['lowerCorner'].split())
        ull_param = ','.join(rspns['upperCorner'].split())
        l_param = choice(['map', 'sat,skl'])
        start_embed.set_image(url=f'{img_url}bbox={lll_param}~{ull_param}&l={l_param}')
        await ctx.channel.send(embed=start_embed)

    @commands.command(name='city_guess')
    async def city_guess(self, ctx, city):
        if not self.game_in_progress:
            await ctx.channel.send(embed=not_game_embed)

        if city.lower() == self.chosen_city.lower():
            await ctx.channel.send(embed=win_embed)
        else:
            await ctx.channel.send(embed=lose_embed)


bot = commands.Bot(command_prefix='$')
bot.add_cog(MOBotClient(bot))
bot.run(TOKEN)
