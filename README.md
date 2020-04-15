# Tarot confiné
Pour jouer au tarot, comme en vrai, avec ses amis pendant le confinement.

## Préparation de la partie

Éditez le fichier organisateur.csv et indiquez-y votre adresse de courriel et le mot de passe de votre messagerie. La connexion se fait en SMTP. Pour un compte Google il faut activer les connexions moins sécurisées.

Ajoutez les noms et adresses de courriel des joueurs dans le fichier joueurs.csv.
Vous êtes prêts. Lancez tarot.GUI (python tarot.GUI). Vous avez besoin de Python3 et de quelques modules (numpy, tkinter...)

Pour le moment on peut joueur uniquement à 4 joueurs. Chaque joueur a une main de 18 cartes et il y a 6 cartes au chien. Pas de garde sans ni contre le chien non plus pour le moment...

## La partie

Ensuite le jeu démarre. Pour chaque distribution, les joueurs reçoivent leur main de cartes pas courriel.

Le jeu se fait par visioconférence, choisissez celle de votre choix, partagez votre écran avec les joueurs.

Ensuite, on joue normalement. Le preneur fait son écart, puis chacun indique la carte qu'il veut joueur. C'est l'organisateur qui saisit la carte jouée tour à tour par chacun des joueurs. Les abréviations sont par exemple : 1 pour le petit, 5 pour le 5 d'atout, e pour l'excuse, 5tr pour le 5 de trèfle, rpi pour le roi de pique.

Sur l'écran, tout le monde peut voir la partie se dérouler.

Respectez les règles du tarot en jouant, le jeu ne vérifie pas. Pas de "je coupe et j'en rejoue".

À la fin, le jeu compte les points du preneur et propose de jouer une nouvelle partie.
