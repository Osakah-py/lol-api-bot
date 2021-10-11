import os
import tri
import data

#discord API
import discord
from discord.utils import get
from dotenv import load_dotenv, find_dotenv

#Riot API
from riotwatcher import LolWatcher, ApiError

#load_dotenv(find_dotenv())
#TOKEN = os.getenv('DISCORD_TOKEN')

############################
# Environnements Variables #
############################

# Discord
TOKEN = "ODkwMjI4NDE2NTEzNzA4MDQy.YUsv0g.pCT1iug2eWsz1m-jirgkRmtwWdQ"
client = discord.Client()

# Riot 
api_key = 'RGAPI-909e469f-2c99-46b3-b66f-eca9e87580a5'
watcher = LolWatcher(api_key)
my_region = 'euw1'

##################
# Discord events #
##################

@client.event
async def on_ready():
    print(f"{client.user} has connected to Discord!")
    print("**********************\n* LISTE DES SERVEURS *\n**********************")
    for guild in client.guilds:
        print(f"{guild.name} (id: {guild.id})")

@client.event

async def on_message(message):
    
    # Pour éviter que le bot se réponde tout seul
    if message.author == client.user:
        return
    
    # Suppression des majuscules
    msg = message.content.lower()
    
    # Liste des commandes utilisables
    if msg == 'bonjour':
        await message.channel.send("Bonsoir")

    if msg.startswith("rank"):
        user = msg.split("rank ",1)[1]

        try:
            me = watcher.summoner.by_name(my_region, user)
            rank = watcher.league.by_summoner(my_region, me['id'])
            masteries = watcher.champion_mastery.by_summoner(my_region, me['id'])
            
            solo = tri.solo(rank)
            flex = tri.flex(rank)

            embed = data.rank(solo, flex, me, masteries)
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
        
        except ApiError as err:
            if err.response.status_code == 429:
                await message.channel.send("Trop de requête envoyés pour le profil *" + user + "*")
            
            elif err.response.status_code == 404:
                await message.channel.send("L'utilisateur *" + user + "* est introuvable sur le serveur euw")
            
            else:
                await message.channel.send("Erreur inconnue : "+ str(err.response.status_code))
                raise Exception("Erreur inconnue : " + str(err.response.status_code))
    
    if msg.startswith("history"):
        user = msg.split("history ",1)[1]

        try:
            me = watcher.summoner.by_name(my_region, user)
            my_matches = watcher.match_v5.matchlist_by_puuid('EUROPE', me['puuid'])  

            for i in range(0, 5):
                embed = data.history(my_matches, me, i)
                await message.channel.send(embed=embed)

        except ApiError as err:
            if err.response.status_code == 429:
                await message.channel.send("Trop de requête envoyés pour le profil *" + user + "*")
            
            elif err.response.status_code == 404:
                await message.channel.send("L'utilisateur *" + user + "* est introuvable sur le serveur euw")
            
            else:
                await message.channel.send("Erreur inconnue : "+ str(err.response.status_code))
                raise Exception("Erreur inconnue : " + str(err.response.status_code))

    if msg.startswith("live"):
        user = msg.split("live ",1)[1]
    
        try:
            me = watcher.summoner.by_name(my_region, user)

            spec = watcher.spectator.by_summoner(my_region, me['id'])

            embed=data.live(spec)

            await message.channel.send(embed=embed)

        except ApiError as err:
            if err.response.status_code == 429:
                await message.channel.send("Trop de requête envoyés pour le profil *" + user + "*")
            
            elif err.response.status_code == 404:
                await message.channel.send("L'utilisateur *" + user + "* est introuvable sur le serveur euw ou n'est pas en game.")
            
            else:
                await message.channel.send("Erreur inconnue : "+ str(err.response.status_code))
                raise Exception("Erreur inconnue : " + str(err.response.status_code))
client.run(TOKEN)