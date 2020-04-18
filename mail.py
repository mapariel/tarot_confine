# -*- coding: utf-8 -*-
"""
Created on Sun Apr 12 12:53:54 2020

@author: MartinMoritz
"""

import smtplib
#from tarot import Partie
from email.message import EmailMessage
import time
import csv

class Distributeur:
    
    
    def __init__(self):
        """
        Initialise le distributeur par email
        le fichier serveur.csv contient l'email et le mot de passe pour une connexion SMTP
        Les noms des joueurs ainsi que leur email sont dans le fichiers 
        joueurs.csv
        """
        self.noms=[]
        self.emails=[]
        with open('serveur.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                self.email_user = line[0]
                self.email_password = line[1]
        
        with open('joueurs.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                self.noms.append(line[0])
                self.emails.append(line[1])

    
    def send(self,partie):
        now = time.localtime(time.time())
        now = time.strftime("%H:%M", now)
        for i in range(len(self.noms)):
            if len(partie.joueurs[i].main)==0:
                continue
            
            msg = EmailMessage()
            texte = "{}, voici vos cartes pour cette nouvelle partie. \n".format(self.noms[i])
            
            
            msg.set_content(texte+partie.affiche(i))
            msg['Subject'] = 'Vos cartes ({})'.format(now)
            msg['From'] = self.email_user
            msg['To'] = self.emails[i]
            
            try:
                s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                s.ehlo()
                s.login(self.email_user,self.email_password )
                s.send_message(msg)
                s.quit()
                
            
                print('Le jeu de {}  lui a été envoyé par email à {}.'.format(self.noms[i],self.emails[i]))
            except:
                print("{} n'a pas recu son jeu.".format(self.noms[i]))       
            






"""

"""    
    