from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from riotwatcher import LolWatcher, ApiError
import time
from decouple import config

# Enregistrez le temps de début
start_time = time.time()


#####################################################
api_key = config('RIOT_TOKEN')
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
#######################################################
# Recup du match 
match_detail = watcher.match.by_id('EUROPE', 'EUW1_6670579727')

image_urls = []
text_content = []
blue = []
red = []

for count, player in enumerate(match_detail['info']['participants']):
    image_urls.append("https://opgg-static.akamaized.net/images/lol/champion/"+champ_dict[str(player['championId'])]+".png")
    #image_urls.append(".\\assets\\img\\champion\\tiles\\"+champ_dict[str(player['championId'])]+"_0.jpg")
    if (count) >= 5:
        text_content[count%5] = text_content[count%5] + '    vs    ' + player['summonerName']
        red.append(player['summonerName'])
    else:
        text_content.append(player['summonerName'])
        blue.append(player['summonerName'])

plus_grand_txt = max(text_content, key=len)
max_len = len(plus_grand_txt)

for i in range(len(text_content)):
    l = (max_len - len(text_content[i]) + 1)
    print(l)
    if l != 0 :
        spaces = ' ' * l
        new = text_content[i].split(' vs ')
        text_content[i] = new[0] + spaces + 'vs' + spaces + new[1]
        print(text_content[i])

# Créer une nouvelle image avec un fond blanc
width, height = 800, 600
result_image = Image.new("RGB", (width, height), "white")

# URLs des images carrées sur Internet


# Position initiale pour la première colonne d'images
x_image_left, y_image_left = 50, 50

# Ajouter la première colonne d'images à l'image résultante
for image_url in image_urls[:5]:
    # Télécharger l'image depuis l'URL
    response = requests.get(image_url)
    square_image = Image.open(BytesIO(response.content))
    
    # Charger l'image carrée
    # square_image = Image.open(image_url)
    # Redimensionner l'image carrée si nécessaire
    square_image = square_image.resize((100, 100))

    # Ajouter l'image carrée à l'image résultante
    result_image.paste(square_image, (x_image_left, y_image_left))

    # Mettre à jour les coordonnées pour la prochaine image carrée
    y_image_left += 110  # Ajoute un espace de 10 pixels entre les images


# Ajouter une colonne de texte entre les deux colonnes d'images
x_text, y_text = x_image_left + 120, 50
draw = ImageDraw.Draw(result_image)
font = ImageFont.load_default()

# Spécifier la taille de la police
font_size = 18
font = ImageFont.load_default().font_variant(size=font_size)

#Pour adapter l'ecart entre les images
x_text_end = draw.textbbox((x_text, y_text), plus_grand_txt, font=font)[2]
print (x_text_end)

# Ajouter chaque ligne de texte (on fait blue + red en meme temps)
for i in range(len(blue)):
    #adversaire team blue
    draw.text((x_text, y_text), blue[i], font=font, fill=(0, 0, 0))

    line_box = draw.textbbox((x_text, y_text), red[i], font=font)
    largeur = line_box[2] - line_box[0]
    draw.text((x_text_end - largeur, y_text), red[i], font=font, fill=(0, 0, 0))
    y_text += font_size + 90  # Ajustez l'espacement entre les lignes selon vos besoins

# Position initiale pour la deuxième colonne d'images
x_image_right, y_image_right = x_text_end + 20, 50

# Ajouter la deuxième colonne d'images à l'image résultante
for image_url in image_urls[5:]:
    # Télécharger l'image depuis l'URL
    response = requests.get(image_url)
    square_image = Image.open(BytesIO(response.content))
    
    # Charger l'image carrée
    # square_image = Image.open(image_url)

    # Redimensionner l'image carrée si nécessaire
    square_image = square_image.resize((100, 100))

    # Ajouter l'image carrée à l'image résultante
    result_image.paste(square_image, (x_image_right, y_image_right))

    # Mettre à jour les coordonnées pour la prochaine image carrée
    y_image_right += 110  # Ajoute un espace de 10 pixels entre les images

# Enregistrer l'image résultante
result_image.save("resultat_image_avec_texte.png")

# Afficher l'image (nécessite une application par défaut associée aux images)
result_image.show()



# Enregistrez le temps de fin
end_time = time.time()

# Calculez la durée totale
execution_time = end_time - start_time

print(f"Le programme a mis {execution_time} secondes pour s'exécuter.")