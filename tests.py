from riotwatcher import LolWatcher, ApiError
import riotwatcher
import tri

api_key = 'RGAPI-909e469f-2c99-46b3-b66f-eca9e87580a5'
watcher = LolWatcher(api_key)
my_region = 'euw1'

me = watcher.summoner.by_name(my_region, 'Osakah')

# First we get the latest version of the game from data dragon
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

#même chose pour les runes
runes_dict = {}

for i in runes_list:
    for runes in i['slots'][0]['runes']:
        runes_dict[runes['id']] = runes['name']

# Même chose pours les branches de rune
branches = {}
for i in runes_list:
    branches[i['id']] = i['name']

# Même chose pours les summoner spells
summonerspells = {1:"Cleanse", 3:"Exhaust", 4:"Flash", 6:"Ghost", 7:"Heal", 11:"Smite", 12:"Teleport", 14:"Ignite", 21:"Barrier"}
queue = {0:"Custom games", 430:"Blind Pick", 420:"Ranked Solo/Duo", 440:"Ranked Flex", 400:"Draft"}

profil=watcher.league.by_summoner(my_region, me['id'])

solo = tri.solo(profil)
flex = tri.flex(profil)

print("RANK INFORMATIONS :")

print("SOLOQ : " + solo['tier'] + " " + solo['rank'])
#print("FLEX : " + flex['tier'] + " " + flex['rank'])
print("\n----------------\n")

my_match = watcher.match_v5.matchlist_by_puuid('EUROPE', me['puuid'])
for i in range(0, 5):
    match_detail = watcher.match_v5.by_id('EUROPE', my_match[i])
    if match_detail['info']['gameMode'] == "CLASSIC":
        match_detail['info']['gameMode'] = queue[match_detail['info']['queueId']]
    print (match_detail['info']['gameMode'])
