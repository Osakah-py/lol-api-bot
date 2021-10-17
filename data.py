import tri

#discord API
import discord
from dotenv import load_dotenv, find_dotenv

#Riot API
from riotwatcher import LolWatcher, ApiError

api_key = 'RGAPI-909e469f-2c99-46b3-b66f-eca9e87580a5'
watcher = LolWatcher(api_key)
my_region = 'euw1'

# Récuperation de la dernière version de data dragon
versions = watcher.data_dragon.versions_for_region(my_region)
champions_version = versions['n']['champion']
champ_list = watcher.data_dragon.champions(champions_version, False, 'fr_FR')
runes_list = watcher.data_dragon.runes_reforged(champions_version, 'fr_FR')
summonerspells_list = watcher.data_dragon.summoner_spells(champions_version, 'fr_FR')
# Dictionnaire permettant de donner le nom d'un champion depuis sa clé
champ_dict = {}

for key in champ_list['data']:
    row = champ_list['data'][key]
    champ_dict[row['key']] = row['id']

# Même chose pour les runes
runes_dict = {}

for i in runes_list:
    for runes in i['slots'][0]['runes']:
        runes_dict[runes['id']] = runes['name']

# Même chose pours les branches de rune
branches = {}
for i in runes_list:
    branches[i['id']] = i['name']

# Même chose pours les summoner spells et les Queues
summonerspells = {1:"Cleanse", 3:"Exhaust", 4:"Flash", 6:"Ghost", 7:"Heal", 11:"Smite", 12:"Teleport", 14:"Ignite", 21:"Barrier"}
queue = {0:"Custom games", 430:"Blind Pick", 420:"Ranked Solo/Duo", 440:"Ranked Flex", 400:"Draft"}
#######################################################Fonctions#######################################################

def rank(solo, flex, me, masteries):
    embed = discord.Embed(title=me['name'], description="Level " + str(me['summonerLevel']), color=0xFF5733)
    embed.set_thumbnail(url="https://static.u.gg/assets/lol/riot_static/11.19.1/img/profileicon/"+str(me['profileIconId'])+".png")

    if solo != None:
        embed.add_field(name="Ranked Solo/Duo", value = "%s %s - %d LP \n %dW %dL" % (solo['tier'], solo['rank'], solo['leaguePoints'], solo['wins'], solo['losses']), inline=True)
    if flex != None:
         embed.add_field(name="Ranked Flex", value=  "%s %s - %d LP \n %dW %dL" % (flex['tier'], flex['rank'], flex['leaguePoints'], flex['wins'], flex['losses']), inline=True)
    if solo == None and flex == None:
         embed.add_field(name="Unranked", value = "Level " + str(me['summonerLevel']), inline=False)

    embed.add_field(name= "\u200b", value = "\u200b", inline=True)
    best_champions = ""
    points = ""

    for i in range(0, 3):
          name = champ_dict[str(masteries[i]["championId"])]
          points = f"{masteries[i]['championPoints']:,}"
          best_champions = best_champions + name + (13-len(name))*" " + points.replace(",", " ") + " points \n" 
          points = points + str(masteries[i]['championPoints'])+ "\n"

    embed.add_field(name= "Meileurs Champions", value = "```" + best_champions + "```", inline=True)
    return embed

def history(my_matches, me, i=int):
    
     match_detail = watcher.match_v5.by_id('EUROPE', my_matches[i])
     for pid in range(0, 10):
          if match_detail["metadata"]["participants"][pid] == me["puuid"]:
               player = match_detail['info']['participants'][pid]
               break
     
     if match_detail['info']['gameMode'] == "CLASSIC":
        match_detail['info']['gameMode'] = queue[match_detail['info']['queueId']]
     
     if player['win']:
          embed = discord.Embed(title=match_detail['info']['gameMode'], description=summonerspells[player['summoner1Id']] + " / " + summonerspells[player['summoner2Id']] + " | " + str(player['totalMinionsKilled'] + player['neutralMinionsKilled']) + " cs" + " | Niveau " + str(player['champLevel']), color=0x33FF57)
     else :
          embed = discord.Embed(title=match_detail['info']['gameMode'], description=summonerspells[player['summoner1Id']] + " / " + summonerspells[player['summoner2Id']] + " | " + str(player['totalMinionsKilled'] + player['neutralMinionsKilled']) + " cs" + " | Niveau " + str(player['champLevel']), color=0xFF5733)
     
     embed.set_thumbnail(url="https://opgg-static.akamaized.net/images/lol/champion/"+champ_dict[str(player['championId'])]+".png")

     kills = "\u200b"
     if player['largestMultiKill']==5:
          kills = "PentaKills  "
     elif player['largestMultiKill']==4:
          kills = "Quadra Kills  "
     elif player['largestMultiKill']==3:
          kills = "Triple Kills  "
     elif player['largestMultiKill']==2:
          kills = "Double Kills  " 
     
     embed.add_field(name=str(player['kills']) + "/" + str(player['deaths']) + "/" + str(player['assists']), value = kills, inline=True)
     
     embed.add_field(name=runes_dict[player['perks']['styles'][0]['selections'][0]['perk']], value = branches[player['perks']['styles'][1]['style']], inline=True)
     
     return embed

def live(spec):

     BanBleu = []
     BanRed = []
     for i in spec['bannedChampions']:
          if i['teamId']==100:
               if i['championId'] != -1:
                    BanBleu.append(champ_dict[str(i['championId'])])
               else:
                    BanBleu.append("No Ban")
          else :
               if i['championId'] != -1:
                    BanRed.append(champ_dict[str(i['championId'])])
               else :
                    BanRed.append("No Ban")
     
     BluePlayers = []
     RedPlayers = []
     
     for player in spec['participants']:
    
        if player['teamId'] == 100:            
          rank = watcher.league.by_summoner(my_region, player['summonerId'])
          solo = tri.solo(rank)

          if solo != None:
               BluePlayers.append("**%s** : \n %s : %s %s - %d%s WR" % (champ_dict[str(player['championId'])], player['summonerName'], solo['tier'], solo['rank'], solo['wins']*100/(solo['wins']+solo['losses']), "%"))
          else:
               BluePlayers.append("**%s** : \n %s : Unranked" % (champ_dict[str(player['championId'])], player['summonerName']))
    
        else:
          rank = watcher.league.by_summoner(my_region, player['summonerId'])
          solo = tri.solo(rank)
          if solo != None:
               RedPlayers.append("**%s** : \n %s : %s %s - %d%s WR" % (champ_dict[str(player['championId'])], player['summonerName'], solo['tier'], solo['rank'], solo['wins']*100/(solo['wins']+solo['losses']), "%"))
          else:
               RedPlayers.append("**%s** : \n %s : Unranked" % (champ_dict[str(player['championId'])], player['summonerName']))
          
     embed = embed = discord.Embed(title=spec['gameMode'], description=" Durée de la game : %d min %d sec" % (spec['gameLength'] // 60,spec['gameLength'] % 60), color=0x00FFFF)
     embed.add_field(name="Equipe bleue", value ="*Bans : " +  " / ".join(BanBleu) + "* \n\n" + "\n".join(BluePlayers), inline=False)
     embed.add_field(name="Equipe rouge", value ="*Bans : " +  " / ".join(BanRed) + "* \n\n" + "\n".join(RedPlayers), inline=False)
     return embed