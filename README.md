# Version WS

This uses Websockets instead of "bare" sockets. First I'll need few changes on phase module...

Une version de démonstration est visible sur http://tarot-confine.my-wan.de/demo


# Tarot confiné
Pour jouer au tarot, comme en vrai, avec ses amis en réseau.
On peut jouer à 3, 4 ou à 5, avec appel du roi ou avec un mort.


## Aspect technique
Le code est testé avec Python 3.7.7, on a besoin des modules websockets numpy et tabulate.

## Préparation de la partie

- Il faut lancer le server ``python server.py``

- On accède au jeu en utilisant le client HTML

## La partie

Ensuite le jeu démarre. Chaque joueur se voit proposer une ou des actions possibles quand c'est son tour.
Pendant le jeu, des icônes désigne qui à qui est le tour de jouer, qui a entamé, qui a pris. Ainsi éventuellement qui est le mort ou bien qui a joué le roi qui a été appelé.

Bon jeu !


## Crédits 

Les icônes et les images utilisées proviennent de wikimedia commons

Les cartes :
https://commons.wikimedia.org/wiki/Category:Tarot_nouveau_-_Grimaud_-_1898

solid chevron-circle-up and solid chevron-up
Font Awesome Free 5.2.0 by @fontawesome - https://fontawesome.com / CC BY (https://creativecommons.org/licenses/by/4.0)

crowns OpenMoji-color 1F451 and OpenMoji-black 1F451
OpenMoji / CC BY-SA (https://creativecommons.org/licenses/by-sa/4.0)








