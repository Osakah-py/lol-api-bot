#discord API
import discord

'''
L'API de Riot retourne les stats ranked flex et ranked solo/duo dans un ordre aléatoire.
Ces fonctions permettent de détecter laquelle est la solo/duo et laquelle et la Flex.
'''

# Détéction des stats de ranked Solo/Duo
def solo(x):
    if len(x) > 0: 
        if x[0]['queueType'] == "RANKED_SOLO_5x5":
            z = x[0]
        else : 
            if len(x) == 2: 
                z = x[1]
            else:
                z = None
    else :
        z = None
    return z

# Détéction des stats de ranked Flex
def flex(x):
    if len(x) > 0: 
        if x[0]['queueType'] == "RANKED_FLEX_SR":
            z = x[0]
        else :
            if len(x) == 2: 
                z = x[1]
            else:
                z = None
    else :
        z = None
    return z
