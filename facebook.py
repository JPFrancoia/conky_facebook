#!/usr/bin/python
# -*-coding:Utf-8 -*

from requests import get
import textwrap
from bs4 import BeautifulSoup
from dateutil.parser import parse
from dateutil import relativedelta
from dateutil.tz import *
import datetime
from clize import clize, run # sert à pouvoir passer des arguments au script


# Fonction inspirée de http://www.developpez.net/forums/d448416/autres-langages/python-zope/general-python/mode-console-couleur-shell/
def couleur(name):

    """ Couleur pour affichage dans le terminal"""

    colors = {
        "default"    :    "\033[0m",
        # style
        "bold"       :    "\033[1m",
        "underline"  :    "\033[4m",
        "blink"      :    "\033[5m",
        "reverse"    :    "\033[7m",
        "concealed"  :    "\033[8m",
        # couleur texte
        "black"      :    "\033[30m", 
        "red"        :    "\033[31m",
        "green"      :    "\033[32m",
        "yellow"     :    "\033[33m",
        "blue"       :    "\033[34m",
        "magenta"    :    "\033[35m",
        "cyan"       :    "\033[36m",
        "white"      :    "\033[37m",
        # couleur fond
        "on_black"   :    "\033[40m", 
        "on_red"     :    "\033[41m",
        "on_green"   :    "\033[42m",
        "on_yellow"  :    "\033[43m",
        "on_blue"    :    "\033[44m",
        "on_magenta" :    "\033[45m",
        "on_cyan"    :    "\033[46m",
        "on_white"   :    "\033[47m" 
    }

    return colors[name]

def conky_color(name):

    """ Couleurs pour affichage dans le conky """

    colors = {
        "red"  :    "$color5",
        "yellow"  :    "$color3",
        "default":    "$color2"
    }

    return colors[name]

# Décorateur permettant de parser les options
@clize(alias={'nbr': ('n',), 'conky': ('c',), 'length': ('l',)})
def main(url, nbr=5, conky=False, length=100) :

    try:
        notifs = get(url).text
    except:
        print("Non connecté")
        return

    soup = BeautifulSoup(notifs)

    now = datetime.datetime.now(tzutc())

    # traitements pour chaque item
    for item in soup.findAll('item')[0:nbr]:

        item.title.string = item.title.string.replace('\n\n', ' ')

        # On ajoute 3 heures à l'heure de l'xml, elle n'est pas bonne
        # On fait ça pour la date de toutes les notifs
        #TODO: ajouter une option pour l'offset des heures
        date = parse(item.pubdate.string) + relativedelta.relativedelta(hours=+2)

        hour = date.hour
        minute = date.minute

        if hour < 10:
            hour = "0" + str(hour)
        else:
            hour = str(hour)

        if minute < 10:
            minute = "0" + str(minute)
        else:
            minute = str(minute)

        #TODO: couper la notif si elle dépasse un certain nbr de caractères.
        #Pr ça, parser le conkyrc appelé pour connaitre le nbr de cara max par ligne.
        #Couper aussi après un mot, et retours à la ligne justifiés.


        pub = format_chaine(item.title.string, length)

        #Si le script est lancé par un conky
        if conky:
            # couleurs différentes en fonction de la date de pub
            # en rouge si la notif a moins de 2 heures
            if now - relativedelta.relativedelta(minutes =+ 60) < date:
                print(conky_color('red') + "- " + hour + ":" + minute + " " + pub + conky_color('default'))
            # en jaune si moins de 5 heures
            elif now - relativedelta.relativedelta(minutes =+ 220) < date :
                print(conky_color('yellow') + "- " + hour + ":" + minute + " " + pub + conky_color('default'))
            else :
                # On imprime le titre
                print("- " + pub)

        #Si le script est lancé en shell
        else:
            # Couleurs différentes en fonction de la date de pub
            # En rouge si la notif a moins de 2 heures. Attention,
            #une heure de décalage dû au temps de facebook
            if now - relativedelta.relativedelta(minutes =+ 60) < date:
                print(couleur('red') + "- " + hour + ":" + minute + " " + pub + couleur('default'))
                #print(type(item.title.string))
                pass
            # En jaune si moins de 5 heures
            elif now - relativedelta.relativedelta(minutes =+ 220) < date :
                print(couleur('yellow') + "- " + hour + ":" + minute + " " + pub + couleur('default'))
            else :
                # On imprime le titre
                print("- " + pub)


def format_chaine(publi, char):

    output = ""

    text = textwrap.fill(publi, char, replace_whitespace=True)
    text = text.split('\n')

    for indice, ligne in enumerate(text):

        if indice == 0:
            ligne += "\n"
        elif indice != len(text) -1:
            ligne = "  " + ligne
        else:
            ligne = "  " + ligne + "\n"

        output = output + ligne

    return output


if __name__ == "__main__":
    run(main)
