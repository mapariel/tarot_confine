# Version WS

This version uses Websockets so that we are able to use an HTML client.

You can test the client at https://mapariel.asuscomm.com/tarot/   (and the code ``masterplayer`` if you don't want to play alone)

Tarot is quite popular in France, that's why the programme, and the comments below, are in French.


# Tarot confiné
Pour jouer au tarot, comme en vrai, avec ses amis en réseau.
On peut jouer à 3, 4 ou à 5, avec appel du roi ou avec un mort.


## Aspect technique
Le code est testé avec Python 3.7.7, on a besoin des modules websockets numpy et tabulate.

## Préparation de la partie

- Il faut lancer le server ``python server.py``. Le server est accessible sur la machine locale sur le port 6789. 

- On accède au jeu en utilisant le client HTML. Si on souhaite accepter des clients en dehors du réseau local, il faut changer l'hôte à la ligne 112.
Le client s'adapte à l'écran du joueur, on peut joueur sur ordinateur ou bien sur smartphone).

## La partie

Quand on charge la page du client, le jeu demande un code. Il faut saisir ``masterplayer`` pour être l'organisateur de la partie. L'organisateur peut changer le type de partie (3,4 ou 5 joueurs) et a connaissance des codes à communiquer aux autres joueurs. 

Si on ne saisit pas de code, on peut devenir observateur de la partie. En l'absence d'organisateur, on accède à une partie test, où l'on joue tour à tour le rôle des différents joueurs, ce qui permet de tester l'interface.


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








