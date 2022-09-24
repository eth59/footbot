from doctest import master
import discord
import interactions
import csv
from test_api import generate_standings

TOKEN = "MTAyMzE4MjY3ODY4Nzc1NjMwOA.GBrX3H.Z5kHoLFq3oBxu4xdTjmypRtiSifMXges3EolLk"
MY_GUILD = discord.Object(id=1010577304134623273)
PREFIX = '!'


bot = interactions.Client(token=TOKEN)

@bot.event
async def on_ready():
    print("Le bot est prêt.")

@bot.command(
    name="prono",
    description="Pronostique un match !",
    scope=MY_GUILD.id,
    options=[
        interactions.Option(
            name="domicile",
            description="Nom de l'équipe domicile",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="exterieur",
            description="Nom de l'équipe extérieure",
            type=interactions.OptionType.STRING,
            required=True
        ),
        interactions.Option(
            name="butdomicile",
            description="Nombre de buts marqués par l'équipe domicile",
            type=interactions.OptionType.INTEGER,
            required=True
        ),
        interactions.Option(
            name="butexterieur",
            description="Nombre de buts marqués par l'équipe extérieure",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def prono(ctx: interactions.CommandContext, domicile: str,
                exterieur: str, butdomicile: int, butexterieur: int):
    await ctx.send(f"{domicile} {butdomicile}-{butexterieur} {exterieur}")

@bot.command(
    name="classement",
    description="Affiche le classement de la ligue 1",
    scope=MY_GUILD.id
)
async def classement(ctx: interactions.CommandContext):
    # generate_standings()
    message = "```ansi\n+----+-----------------+----+----+----+----+----+----+-----+-----+------------+\n"
    file = open('l1_standings.csv')
    csvreader = csv.reader(file)
    for i, line in enumerate(csvreader):
        if i==1:
            message += "\u001b[0;34m"
        if i==3:
            message += "\u001b[0;33m"
        if i==4:
            message += "\u001b[0;32m"
        if i==5:
            message += "\u001b[0;36m"
        if i==6:
            message += "\u001b[0m"
        if i==17:
            message += "\u001b[0;31m"
        if i==0:
            message += f"| Rg |"
        else:
            message += f"| {line[0]:<2} |"
        if line[1] == 'Paris Saint Germain':
            message += f" PSG             |"
        elif line[1] == 'Stade Brestois 29':
            message += f" Brest           |"
        else:
            message += f" {line[1]:<15} |"
        message += f" {line[2]:<2} |"
        message += f" {line[3]:<2} |"
        message += f" {line[4]:<2} |"
        message += f" {line[5]:<2} |"
        message += f" {line[6]:<2} |"
        message += f" {line[7]:<2} |"
        message += f" {line[8]:<3} |"
        message += f" {line[9]:<3} |"
        if i==0:
            message += f" {line[10]} |\n"
        else:
            message += f" {' '.join(line[10])}  |\n"
        if i==0:
            message += "+----+-----------------+----+----+----+----+----+----+-----+-----+------------+\n"
    message += "\u001b[0m+----+-----------------+----+----+----+----+----+----+-----+-----+------------+\n```"
    await ctx.send(message)
    
bot.start()