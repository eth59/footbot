import sqlite3
import discord
import interactions
import csv
from api import *

TOKEN = "MTAyMzE4MjY3ODY4Nzc1NjMwOA.GBrX3H.Z5kHoLFq3oBxu4xdTjmypRtiSifMXges3EolLk"
MY_GUILD = discord.Object(id=1010577304134623273)
MY_GUILD2 = discord.Object(id=667683204710531088)
PREFIX = '!'

bot = interactions.Client(token=TOKEN)

@bot.event
async def on_ready():
    print("Le bot est prêt.")
    
    
@bot.command(
    name="mes_pronos",
    description="Envoie tes pronos en DM",
    scope=[MY_GUILD.id, MY_GUILD2.id]
)
async def mes_pronos(ctx: interactions.CommandContext):
    conn = sqlite3.connect('prono.db')
    cursor = conn.cursor()
    cursor.execute("""
    SELECT domicile, exterieur, pronos.butDomicile, pronos.butExterieur FROM matchs
    JOIN pronos ON pronos.id_match = matchs.id_match
    WHERE id_user = ?
    """, (int(str(ctx.user.id)),))
    res = cursor.fetchall()
    message = ''
    for elt in res:
        message += f"{elt[0]} {elt[2]}-{elt[3]} {elt[1]}"
    await ctx.author.send(message)
    await ctx.send("Va voir tes DMs BG !")


@bot.command(
    name="pronos_journee",
    description="Affiche tes pronos sur une journée (VISIBLE DE TOUS).",
    scope=[MY_GUILD.id, MY_GUILD2.id],
    options=[
        interactions.Option(
            name="numero_journee",
            description="Le numero de la journée que tu veux voir",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def pronos_journee(ctx: interactions.CommandContext, numero_journee: int):
    try:
        conn = sqlite3.connect('prono.db')
        cursor = conn.cursor()
        cursor.execute("""
        SELECT domicile, exterieur, matchs.butDomicile, matchs.butExterieur, pronos.butDomicile, pronos.butExterieur, pronos.points FROM matchs
        JOIN pronos ON matchs.id_match = pronos.id_match
        WHERE id_user = ? AND numero_journee = ?
        """, (int(str(ctx.user.id)), numero_journee))
        message="```\n+---------------------------+-------+-------+\n"
        message += "|           Match           | Score | Prono |\n"
        message += "+---------------------------+-------+-------+\n"        
        for (dom, ext, butDR, butER, butDP, butEP, pts) in cursor.fetchall():
            if dom == "Paris Saint Germain":
                dom = "PSG"
            elif ext == "Paris Saint Germain":
                ext = "PSG"
            if dom == "Stade Brestois 29":
                dom = "Brest"
            elif ext == "Stade Brestois 29":
                ext = "Brest"
            if dom == "Estac Troyes":
                dom = "Troyes"
            elif ext == "Estac Troyes":
                ext = "Troyes"
            if dom == "Clermont Foot":
                dom = "Clermont"
            elif ext == "Clermont Foot":
                ext = "Clermont"
            if butDR is None or butER is None:
                message += f"| {dom:>12}-{ext:<12} |  TBD  | {butDP:>2}-{butEP:<2} |\n"
            else:
                message += f"| {dom:>12}-{ext:<12} | {butDR:>2}-{butER:<2} | {butDP:>2}-{butEP:<2} |\n"
        message += "+---------------------------+-------+-------+\n```"
        await ctx.send(message)
        
    except Exception as e:
        print(f"\n\n\n")
        print(type(e))
        print(f"Erreur lors de l'affichage des pronos d'une journée :\n {e}\n\n\n")
        conn.rollback()
        await ctx.send("Une erreur inconnue s'est produite.")
    finally:
        conn.close()


@bot.command(
    name="prono",
    description="Pronostique un match !",
    scope=[MY_GUILD.id, MY_GUILD2.id],
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
    await ctx.defer()
    dom = nickname(domicile)
    ext = nickname(exterieur)
    try:
        update_bdd()
    except Exception as e:
        print(f"\n\n\n")
        print(type(e))
        print(f"Erreur lors d'une tentative d'ajout d'un pronostic (maj BDD) :\n {e}\n\n\n")
        await ctx.send("Une erreur inconnue s'est produite lors de la tentative d'actulasation des matchs.")
    else:
        try:
            conn = sqlite3.connect('prono.db')
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id_match, domicile, exterieur, commence FROM matchs
            """)
            match_list = cursor.fetchall()
            for match in match_list:
                if match[1] == dom and match[2] == ext:
                    id_match = match[0]
                    if match[3] == 1:
                        raise ValueError
                    break
                
            id_user = int(str(ctx.user.id))
            cursor.execute("""
            SELECT id_user FROM users WHERE id_user = ?
            """,[id_user])
            users_list = cursor.fetchall()
            if users_list == []:
                user_values = (
                    id_user,
                    ctx.user.username,
                    ctx.user.discriminator
                )
                cursor.execute("""
                INSERT INTO users (id_user, pseudo, discriminator) VALUES (?, ?, ?)            
                """, user_values)
                conn.commit()
            
            values = (id_match, id_user, butdomicile, butexterieur)
            cursor.execute("""
            INSERT INTO pronos (id_match, id_user, butDomicile, butExterieur)
            VALUES (?, ?, ?, ?)
            """, values)
            conn.commit()
            await ctx.send("Votre pronostic a été pris en compte.")
        except sqlite3.IntegrityError:
            cursor.execute("""
            UPDATE pronos
            SET butDomicile = ?, butExterieur = ?
            WHERE id_match = ? AND id_user = ?            
            """, (values[2], values[3], values[0], values[1]))
            conn.commit()
            await ctx.send("Votre pronostic a été modifié.")
        except UnboundLocalError:
            await ctx.send("Ce match n'existe pas.")
        except ValueError:
            await ctx.send("Espèce de tricheur ! On ne parie pas sur un match qui est fini !")
        except Exception as e:
            print(f"\n\n\n")
            print(type(e))
            print(f"Erreur lors d'une tentative d'ajout d'un pronostic :\n {e}\n\n\n")
            conn.rollback()
            await ctx.send("Une erreur inconnue s'est produite.")
        finally:
            conn.close()
    
    
@bot.command(
    name="liste_equipe",
    description="Donne la liste de toutes les équipes",
    scope=[MY_GUILD.id, MY_GUILD2.id]
)
async def liste_equipe(ctx: interactions.CommandContext):
    team_list = get_team_list()
    message = "```\n"
    for team in team_list:
        if team == 'Lille':
            message += f"Lille (ou LOSC)\n"
        elif team == 'Lyon':
            message += f"Lyon (ou OL)\n"
        elif team == 'Marseille':
            message += f"Marseille (ou OM)\n"
        elif team == 'Paris Saint Germain':
            message += f"Paris Saint Germain (ou PSG)\n"
        elif team == 'Toulouse':
            message += f"Toulouse (ou TFC)\n"
        elif team == 'Clermont Foot':
            message += f"Clermont Foot (ou Clermont)\n"
        elif team == 'Stade Brestois 29':
            message += f"Stade Brestois 29 (ou Brest)\n"
        elif team == 'Estac Troyes':
            message += f"Estac Troyes (ou Troyes)\n"
        elif team == 'Lens':
            message += f"Lens (ou RCL)\n"
        else:
            message += f"{team}\n"
    message += "```"
    await ctx.send(message)
    
    
@bot.command(
    name="info_match",
    description="Donne quelques infos sur un match",
    scope=[MY_GUILD.id, MY_GUILD2.id],
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
        )
    ]
)
async def info_match(ctx: interactions.CommandContext, domicile: str, exterieur: str):
    dom = nickname(domicile)
    ext = nickname(exterieur)
    match = get_match(dom, ext)
    if match == None:
        await ctx.send("Ce match n'existe pas.")
    else:
        message = '```\n'
        if match['fixture']['status']['short'] in ['P', 'PEN']:
            message += f"{dom} {match['goals']['home']} ({match['score']['penalty']['home']})-"
            message += f"({match['score']['penalty']['away']}) {match['goals']['away']} {ext}\n"
        else:
            message += f"{dom} {match['goals']['home']}-{match['goals']['away']} {ext}\n"
        message += f"Statut : {match['fixture']['status']['long']} ({match['fixture']['status']['short']})\n"
        message += f"Temps écoulé : {match['fixture']['status']['elapsed']}\n"
        date = match['fixture']['date']
        message += f"Coup d'envoi : le {date[8:10]}-{date[5:7]}-{date[:4]} à {date[11:16]} {match['fixture']['timezone']}\n"
        message += f"Lieu du match : {match['fixture']['venue']['name']} ({match['fixture']['venue']['city']})\n"
        message += f"Arbitré par : {match['fixture']['referee']}\n"
        message += "```"
        await ctx.send(message)
     
        
@bot.command(
    name="points",
    description="Affiche les points des utilisateurs.",
    scope=[MY_GUILD.id, MY_GUILD2.id]
)
async def points(ctx: interactions.CommandContext):
    try:
        res = get_points()
    except Exception as e:
        print(f"\n\n\n")
        print(type(e))
        print(f"Erreur lors de l'obtention des points :\n {e}\n\n\n")
        
    message = "```\n+-----------------+------- +\n"
    message += "| Pseudo          | Points |\n"
    message += "+-----------------+------- +\n"
    for row in res:
        message += f"| {row[0]:<15} | {row[1]:<6} |\n"
    message += "+-----------------+--------+\n```"
    await ctx.send(message)
    

@bot.command(
    name="classement",
    description="Affiche le classement de la ligue 1",
    scope=[MY_GUILD.id, MY_GUILD2.id]
)
async def classement(ctx: interactions.CommandContext):
    generate_standings()
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
    
    
@bot.command(
    name="actualise",
    description="Met à jour la base de données des matchs.",
    scope=[MY_GUILD.id, MY_GUILD2.id]
)
async def actualise(ctx: interactions.CommandContext):
    await ctx.defer()
    try:
        update_bdd()
    except Exception as e:
        print(f"\n\n\n")
        print(type(e))
        print(f"Erreur lors de la mise à jour de la BDD :\n {e}\n\n\n")
        await ctx.send("Une erreur inconnue s'est produite.")
    else:
        await ctx.send("Les matchs ont bien été actualisés.")


@bot.command(
    name='requetes_restantes',
    description="Affiche le nombre de requêtes restantes pour la journée",
    scope=[MY_GUILD.id, MY_GUILD2.id]
)
async def requetes_restantes(ctx: interactions.CommandContext):
    answer = get_remaining_requests()
    await ctx.send(f"Il vous reste {answer} requêtes pour la journée.")


@bot.command(
    name='help',
    description='Aide les noobs.',
    scope=[MY_GUILD.id, MY_GUILD2.id]
)
async def help(ctx: interactions.CommandContext):
    message = "```\n"
    message += "Salut moi c'est Footbot, le meilleur bot de pronostic footballistique (ou plutôt de Ligue 1 car je ne fais pas plus).\n"
    message += "La liste des différentes choses que je maîtrise :\n"
    message += "- classement : Affiche le classement actuel de la ligue 1\n"
    message += "- liste_equipe : Affiche la liste des équipes (dans le format pris en charge par les commandes)\n"
    message += "- info_match : Affiche quelques infos plus ou moins utiles sur un match\n"
    message += "- affiche_journee : Affiche les matchs d'une journée\n"
    message += "- prono (et pas porno) : Le plus important ! Permez de pronostiquer un match\n"
    message += "- mes_pronos (et pas mes_pornos) : Envoie des pornos en DM\n"
    message += "- pronos_journee (et pas pornos_journee) : Affiche vos pronos sur une journée\n"
    message += "- actualise : Permet d'actualiser la base de données et donc de vous donner des points (si vous avez pronostiqué bien sûr)\n"
    message += "- points : Affiche les points de chaque utilisateur\n"
    message += "- requetes_restantes : Affiche le nombre de requêtes restantes (cf plus bas)\n"
    message += "\nLes points sont attribués de cette manière :\n"
    message += "- 20 points si vous avez pronostiqué avec le cul\n"
    message += "- 100 points si vous avez pronostiqué le bon vainqueur (ou le nul)\n"
    message += "- 50 points bonus si vous avez la bonne différence de buts\n"
    message += "- 100 points bonus si vous avez le score exact (cumulable avec la différence de buts)\n"
    message += "\nQu'est-ce que les requêtes ?\n"
    message += "L'API que j'utilise est limitée à 100 requêtes par jour. "
    message += "Il faut donc retenir que chaque commande correspond à 1 requête, "
    message += "à l'exception de requetes_restantes et mes_pronos qui sont gratuites. N'abuse pas de moi jeune padawan !\n"
    message += "\nJe te souhaite de m'utiliser comme il se doit ! ;)\n```"
    await ctx.send(message)
    

@bot.command(
    name='affiche_journee',
    description="Affiche les matchs d'une journee",
    scope=[MY_GUILD.id, MY_GUILD2.id],
    options=[
        interactions.Option(
            name="numero",
            description="Le numero de la journée que tu veux voir.",
            type=interactions.OptionType.INTEGER,
            required=True
        )
    ]
)
async def affiche_journee(ctx: interactions.CommandContext, numero: int):
    res = get_journee(numero)
    res.sort(key=lambda tup: tup[7])
    res.sort(key=lambda tup: tup[4])
    res.sort(key=lambda tup: tup[5])
    res.sort(key=lambda tup: tup[6])
    message = "```\n"
    for (dom, ext, butDom, butExt, jour, mois, annee, heure, timezone, status) in res:
        if status == 'TBD':
            message += f"{dom} - {ext} TBD ({jour}-{mois}-{annee})\n"
        else:
            if butDom is None or butExt is None:
                message += f"{dom} - {ext} le "
            else:
                message += f"{dom} {butDom}-{butExt} {ext} le "
            message += f"{jour}-{mois}-{annee} à {heure} {timezone}\n"
    message += "```"
    await ctx.send(message)
    
    
bot.start()