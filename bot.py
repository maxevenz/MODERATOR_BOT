import discord
from discord.ext import commands, tasks
from cogs.misc import Choice
from cogs.misc import RockPaperScissorsView
from config import settings
import random
import aiohttp
from googletrans import Translator
import datetime
import json
import requests

bot = commands.Bot(command_prefix="+", intents=discord.Intents.all())
t = Translator()


@bot.event
async def on_ready():
    status_task.start()
    print("Успех!")


@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send('Привет! это Moderator Bot. Напишите +help для вывода всех доступных команд')
        break


@tasks.loop(seconds=60)
async def status_task() -> None:
    statuses = ["в ящик", "с людьми", "в 4D шахматы", "на нервах", "догони меня кирпич"]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))


@bot.command(brief='Проверка бота, живой ли он вообще', description='Проверка бота, живой ли он вообще')
async def ping(ctx):
    await ctx.send("pong!")


@bot.command(brief='Бот вас поприветствует', description='Бот вас поприветствует')
async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f'Привет, {author.mention}!')


@bot.command(brief='Бот скажет текущую цену биткойна', description='Бот скажет текущую цену биткойна')
async def bitcoin(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
        ) as request:
            if request.status == 200:
                data = await request.json(
                    content_type="application/javascript"
                )
                embed = discord.Embed(
                    title="Цена биткойна",
                    description=f"Текущая цена: {data['bpi']['USD']['rate']} :dollar:",
                    color=0x9C84EF,
                )
            else:
                embed = discord.Embed(
                    title="Ошибка!",
                    description="Что-то не так с сервисом, попробуйте позже",
                    color=0xE02B2B,
                )
    await ctx.send(embed=embed)


@bot.command(brief='Бот выдаст случайное число в заданном диапазоне',
             description='Бот выдаст случайное число в заданном диапазоне '
                         '(например, при вводе "+randomnumber 1 100" бот выдаст случайное число от 1 до 100)')
async def randomnumber(ctx, n1: str = commands.parameter(description="нижний предел диапазона"),
                       n2: str = commands.parameter(description="верхний предел диапазона")):
    randnum = random.randint(int(n1), int(n2))
    embed = discord.Embed(title=f"Случайное число - {randnum}")
    await ctx.send(embed=embed)


@bot.command(brief='Бот подбросит монетку, а вы попробуйте угадать, что выпадет',
             description='Бот подбросит монетку а вы попробуйте угадать, что выпадет')
async def coinflip(ctx):
    buttons = Choice()
    embed = discord.Embed(description="Я подкину монетку. На что ставите?", color=0x9C84EF)
    message = await ctx.send(embed=embed, view=buttons)
    await buttons.wait()
    result = random.choice(["орел", "решка"])
    if buttons.value == result:
        embed = discord.Embed(
            description=f"Повезло! Вы поставили, что выпадет `{buttons.value}` - так оно и получилось.",
            color=0x9C84EF,
        )
    else:
        embed = discord.Embed(
            description=f"Ой! Вы поставили, что выпадет `{buttons.value}`,"
                        f" а результат получился - `{result}`, удачи в следующий раз!",
            color=0xE02B2B,
        )
    await message.edit(embed=embed, view=None, content=None)


@bot.command(name="rps", brief="Бот сыграет с вами в камень-ножницы-бумага",
             description="Бот сыграет с вами в камень-ножницы-бумага")
async def rock_paper_scissors(ctx):
    view = RockPaperScissorsView()
    await ctx.send("Сыграем в камень-ножницы-бумага! Сделайте свой выбор:", view=view)


@bot.command(name="randomfact", brief="Бот расскажет вам случайный факт (иногда бывает корявый перевод).",
             description="Бот расскажет вам случайный факт (иногда бывает корявый перевод).")
async def randomfact(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                "https://uselessfacts.jsph.pl/random.json?language=en"
        ) as request:
            if request.status == 200:
                data = await request.json()
                embed = discord.Embed(description=t.translate(data['text'], dest="ru").text, color=0xD75BF4)
            else:
                embed = discord.Embed(
                    title="Ошибка!",
                    description="Что-то не так с сервисом, попробуйте позже",
                    color=0xE02B2B,
                )
            await ctx.send(embed=embed)


@bot.command(brief="Бот переведет написанный текст на нужный язык",
             description="Бот переведет написанный текст на нужный язык, ввод следующем в формате:\n"
                         "+translate 'язык' 'текст'\nНапример, при вводе "
                         "'+translate ru Hello, world!', бот выведет 'Привет, мир!'")
async def translate(ctx, lang: str = commands.parameter(description="нужный язык"), *,
                    args: str = commands.parameter(description="текст")):
    translation = t.translate(args, dest=lang)
    await ctx.send(translation.text)


@bot.command(brief="Забанить пользователя", description="Забанить пользователя, формат ввода:\n"
                                                        "+ban 'участник' 'причина'"
                                                        "Пример:\n+ban @Durak 'потому что он дурак'\n"
                                                        "Команда доступна только пользователям с надлежащими ролями")
@commands.has_any_role("Moderator", "Administrator", "Owner")
async def ban(ctx, member: discord.Member, *, reason: None):
    if reason is None:
        reason = "@" + ctx.message.author.name + " забанил пользователя " + member.name + \
                 ", потому что ему так захотелось"
    await member.ban(reason=reason)
    await ctx.send(reason)


@bot.command(brief="Выгнать пользователя", description="Выгнать пользователя, формат ввода:\n"
                                                       "+kick 'участник' 'причина'"
                                                       "Пример:\n+kick @Durak 'потому что он дурак'"
                                                       "Команда доступна только пользователям с надлежащими ролями")
@commands.has_any_role("Moderator", "Administrator", "Owner")
async def kick(ctx, member: discord.Member, *, reason: str = None):
    if reason is None:
        reason = "@" + ctx.message.author.name + " выгнал пользователя " + \
                 member.name + ", потому что ему так захотелось"
    await member.kick(reason=reason)
    await ctx.send(reason)


@bot.command(brief="Замутить пользователя")
@commands.has_any_role("Moderator", "Administrator", "Owner")
async def mute(ctx, member: discord.Member, timelimit):
    if "s" in timelimit:
        gettime = timelimit.strip("s")
        newtime = datetime.timedelta(seconds=int(gettime))
        await member.edit(timed_out_until=discord.utils.utcnow() + newtime)
        await ctx.send("@" + ctx.message.author.name + "замутил пользователя" +
                       member.name + " на " + timelimit + " секунд")
    elif "m" in timelimit:
        gettime = timelimit.strip("m")
        newtime = datetime.timedelta(minutes=int(gettime))
        await member.edit(timed_out_until=discord.utils.utcnow() + newtime)
        await ctx.send("@" + ctx.message.author.name + "замутил пользователя" +
                       member.name + " на " + timelimit + " минут")
    elif "h" in timelimit:
        gettime = timelimit.strip("h")
        newtime = datetime.timedelta(hours=int(gettime))
        await member.edit(timed_out_until=discord.utils.utcnow() + newtime)
        await ctx.send("@" + ctx.message.author.name + "замутил пользователя" +
                       member.name + " на " + timelimit + " часов")
    elif "d" in timelimit:
        gettime = timelimit.strip("d")
        newtime = datetime.timedelta(seconds=int(gettime))
        await member.edit(timed_out_until=discord.utils.utcnow() + newtime)
        await ctx.send("@" + ctx.message.author.name + "замутил пользователя" +
                       member.name + " на " + timelimit + " дней")


@bot.command(brief="Бот отправляет случайного котика")
async def cat(ctx):
    response = requests.get('https://some-random-api.com/img/cat')
    json_data = json.loads(response.text)

    embed = discord.Embed(color=0xff9900, title='Случайный котик')
    embed.set_image(url=json_data['link'])
    await ctx.send(embed=embed)

bot.run(settings["token"])
