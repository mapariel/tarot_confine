# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 13:29:26 2020

@author: MartinMoritz
"""


import PySimpleGUI as sg
import PIL as pil  # ImageTk,Image
import PIL.ImageTk as pitk
import PIL.ImageDraw as pildraw
import PIL.ImageFont as pilfont
import tkinter.font as tkFont
import tarot as tr
from mail import Distributeur
import numpy as np
import time

sg.theme('DarkAmber')   # Add a little color to your windows
# All the stuff inside your window. This is the PSG magic code compactor...
# les dimensions du tapis de jeu
width = 1000
height = 700
images_cartes = {}
distributeur = Distributeur()
partie = tr.Partie(donneur_index=0,distributeur=distributeur,debug=False)
message = partie.get_message()



#print(values)





"""
Définition de l'interface graphique
"""
entames = [ [sg.Text(size=(16,1),key='INFOS_'+famille,font=('Helvetica',14),text_color='white',justification='center')]   
                        for famille in ['pique','coeur','carreau','trefle','atout']   ] 


colonne =[ [sg.Multiline(default_text=message,disabled=True,size=(30,20),key='-OUTPUT-',font=('Helvetica',12),autoscroll=True)],
            [sg.InputText(size=(10,1),key='-INPUT-',font=('Monospace', 16)),
             sg.Button('Ok'),sg.Button('Cancel'),
             ]
          ]  
colonne = colonne+entames           
          
menu_def=[
          ['&Paramètres',["modifier l'&organisateur",'modifier les &joueurs','&quitter']],
          ['&Jeu',['annuler la &partie','annuler le &coup','&voir le jeu du prochain joueur']] , 
          ['&Aide',['&aide rapide','&licence','à &propos']]
         ]

            

layout = [
           [sg.Menu(menu_def)], 
           [sg.Text('Historique')],
           [sg.Column(colonne),
                     sg.Canvas(size=(width,height),background_color='green', key='canvas')],
        ]  
        
# Create the Window           


def window_organisateur(distributeur,partie):
        email = distributeur.email_user
        password = distributeur.email_password
        layout = [
                 [sg.Text(text=
"""Entrez votre email et votre mot de passe de messagerie Google.Le mot de passe ne sera pas sauvegardé et vous pourrez modifier ces informations plus tard""",size=(40,5)) ],
                 [sg.Text('{:20}:'.format('email')),sg.Input(key='username',size=(20,1),default_text=email)],
                 [sg.Text('{:15}:'.format('mot de passe')),sg.Input(key='password',password_char='*',size=(20,1),default_text=password)],
                 [sg.Button('Valider'),sg.Button('Annuler')]
                 ] 
        window2 = sg.Window("messagerie de l'organisateur", layout,keep_on_top=True)
        event,values = window2.read()
        if event == 'Valider':
            print('ici')
            distributeur.email_user = values['username']
            distributeur.email_password = values['password']
        window2.close()

def window_joueurs(distributeur,partie):
        n = len(distributeur.noms)
        noms = distributeur.noms+['']*(5-n)
        emails = distributeur.emails+['']*(5-n)
        
        
        layout2= [  
                   [sg.Input(default_text=noms[i],size=(30,1),key='nom'+str(i),tooltip='Nom'),
                     sg.Input(default_text=emails[i],size=(30,1),key='email'+str(i),tooltip='email')]
                   for i in range(5)
                ]  
        layout2 =[[sg.Text(text="Entrez les noms emails des joueurs. Il faut minimum 3 joueurs. En modifiant ces informations, vous annulez le jeu en cours.",size=(50,2))]]+layout2+ [[sg.Button('Valider'),sg.Button('Annuler')]]
        window2 = sg.Window('Noms et messagerie des joueurs', layout2,keep_on_top=True)
        event,values = window2.read() 
                #print(values2)
        if event == 'Valider':
            
            distributeur.noms=[]
            distributeur.emails=[]
            for i in range(5):
                nom = values['nom'+str(i)].strip() 
                email = values['email'+str(i)].strip()
                if  nom  != '':
                    distributeur.noms.append(nom)
                    distributeur.emails.append(email)
            # rassembler les cartes des joueurs
            partie.rejouer()
            # attribuer les nouveaux joueurs
            partie.initialise_joueurs()
            partie.etat=tr.CARTES_RASSEMBLEES
        window2.close()








def load_image_cartes():

    f2 = pilfont.truetype("arial.ttf", 22)
    
    for carte in partie.jeu:
        abbr = carte.abbr
        img = pil.Image.open('cartes/'+abbr+'.jpg')
        if carte.famille != 'atout':
            if carte.famille == "coeur" or carte.famille == "carreau":
                color = (203,95,66)
            else :
                color = (0,0,0)
            if carte.valeur<11:
                pildraw.Draw(img).text((5,5),str(carte.valeur),color,font=f2)
                if carte.valeur==10:
                    pildraw.Draw(img).text((107,5),str(carte.valeur),color,font=f2)
                else :
                    pildraw.Draw(img).text((115,5),str(carte.valeur),color,font=f2)
                img = img.rotate(180)
                if carte.valeur==10:
                    pildraw.Draw(img).text((107,5),str(carte.valeur),color,font=f2)                    
                else :
                    pildraw.Draw(img).text((115,5),str(carte.valeur),color,font=f2)
                pildraw.Draw(img).text((5,5),str(carte.valeur),color,font=f2)
                
        img2 = pitk.PhotoImage(img)
        images_cartes[abbr] =  img2
    return images_cartes


def affiche_noms(canvas,partie):
    """
    Affiche les noms des joueurs
    """
    width,height = canvas.Size
    canvastk = canvas.tk_canvas 
    global f
    canvastk.delete('nom_joueur')    

    n = partie.nombre()
    angles = np.arange(n)
    angles = angles*2*np.pi/n
    angles = np.array(angles)
    centre = np.array([width/2,height/2])
    centre.shape=(2,1)
    
    coord_noms = centre+np.vstack((width*0.4*np.cos(-angles),height*0.45*np.sin(-angles)))
    for i in range(n):
        nom = str(i)+' : '+str(partie.joueurs[i])
        f_ = f.copy()
        if partie.joueur_index == i :
            f_.configure(underline=True)
            #canvastk.create_text(coord_noms[0,i],coord_noms[1,i],fill="darkblue"
                #,font=f_,text=nom,tags='nom_joueur')
        if partie.preneur_index == i:
            f_.configure(weight='bold',slant='italic')
            #canvastk.create_text(coord_noms[0,i],coord_noms[1,i],fill="darkblue"
                #,font=f_,text=nom,tags='nom_joueur')
        canvastk.create_text(coord_noms[0,i],coord_noms[1,i],fill="darkblue"
                ,font=f_,text=nom,tags='nom_joueur')
    canvastk.update()  


def affiche_cartes(canvas,partie,cartes,images_cartes):
    """
    Affiche les cartes de la parties, la disposition change en fonction du nombre de
    cartes : 4 (un pli), 6 (chien ou écart), sinon (levée)
    """
    # les joueurs sont 0: Nord, 1 : Ouest, 2 :sud, 3. Est
    width,height = canvas.Size
    canvastk = canvas.tk_canvas
    # efface toutes les cartes (avec le tag carte)
    canvastk.delete('carte')
    global f
    
    
    
    if partie.etat in (tr.PLI_EN_COURS,tr.PLI_FINI ):
        n = partie.nombre()
        angles = np.arange(n)
        angles = angles*2*np.pi/n
        angles = np.array(angles)
        centre = np.array([width/2,height/2])
        centre.shape=(2,1)
        coord = centre+100*np.vstack((np.cos(-angles),np.sin(-angles)))
        coord[0,:] = coord[0,:]+np.cos(-angles)*20

        cartes = cartes[partie.entame_index:]+cartes[:partie.entame_index]
        coord = np.hstack((coord[:,partie.entame_index:],coord[:,:partie.entame_index]))
        for i in range(n):
            carte = cartes[i]
            if carte != '_':
              img = images_cartes[carte]
              canvastk.create_image(coord[0,i],coord[1,i],image=img,tags='carte') 
    elif partie.etat in (tr.PASSE,tr.ECART,tr.AFFICHAGE_SCORE ):
        x = 200
        dx = width-500
        for i,carte in enumerate(cartes) :
            img = images_cartes[carte]
            x = x+dx/len(cartes)
            canvastk.create_image(x,height/2,image=img,tags='carte') 
    elif partie.etat in (tr.PARTIE_TERMINEE,) :
        compteur = 0 
        score = canvastk.create_text(width/2,height-200,fill='black',font=f,text=str(compteur),tags=('score','carte')  )
        iterator = iter(partie.levee[0]) 
        while True :
            coord = [[width/2-50,height/2],[width/2+50,height/2]] +np.random.normal(loc=0.0, scale=10,size =(2,2))
            try:
                carte1 =next(iterator)
                carte2 =next(iterator)
                compteur +=  carte1.points+carte2.points
                img1 = images_cartes[carte1.abbr]
                img2 = images_cartes[carte2.abbr]
                canvastk.create_image(coord[0,1],coord[0,1],image=img1,tags='carte') 
                canvastk.create_image(coord[1,0],coord[1,1],image=img2,tags='carte')
                canvastk.delete('score')
                score = canvastk.create_text(width/2,height-200,fill='black',font=f,text=str(compteur),tags=('score','carte')  )
                time.sleep(0.5)
                canvastk.update()
            except StopIteration:
                break
           

def affiche_entames(window,partie):
    for famille in ['pique','carreau','coeur','trefle']:
        if partie.entames[famille]:
            window['INFOS_'+famille].update(famille)
        else:
            window['INFOS_'+famille].update('')
    if partie.entames['atout']>0:
        window['INFOS_atout'].update(str(partie.entames['atout']))
    else:
        window['INFOS_atout'].update('')
            
    


# fenetre principale
window = sg.Window('Tarot Confiné', layout,return_keyboard_events=True)
window.read(timeout=100)
f = tkFont.Font()
f.configure(family="Times",size=20)        
"""
chargement des cartes
"""            
images_cartes = load_image_cartes()            
#window.Disable() 
window_organisateur(distributeur,partie)
window_joueurs(distributeur,partie)
#window.Enable()

# Event Loop to process "events"
while True:             
    event, values = window.read(timeout=100)
    if event in (None, 'quitter'):
        break
    elif event not in ('voir le jeu du prochain joueur','à propos','\r','aide rapide','licence',
                       'modifier les joueurs',"modifier l'organisateur",'annuler la partie','annuler le coup','Ok'):
        continue

        
        
    elif event in ('aide rapide','licence','à propos','voir le jeu du prochain joueur'):  
        window_active=False
        size=(68,48)
        texte = ''
        if event=='licence':
            file = open("./LICENSE", "r")
            texte=file.read()
            file.close()
        elif event=='aide rapide':
            file = open("./README.md","r",encoding='utf8')
            texte=file.read()
            file.close()
        elif event=='à propos':
            texte = """\n TAROT CONFINE \n \n Martin MORITZ - 2020 
            \n https://github.com/mapariel/tarot_confine \n\n Bon jeu !"""
            size=(50,8)
        elif event == 'voir le jeu du prochain joueur':
             texte = partie.affiche(joueur_index=partie.joueur_index)
             size=(50,8)
        sg.popup_scrolled(texte,title=event,size=size)
        window.active=True
        continue
    
    elif event == 'modifier les joueurs':
        window.Disable()
        window_joueurs(distributeur,partie)
        window.Enable()
        continue
    elif event == "modifier l'organisateur":
        window.Disable()
        window_organisateur(distributeur,partie)
        window.Enable()
        continue
        
    
    if event in ('annuler la partie'):
        entry_input = 'FIN'  
    elif event in ('annuler le coup'):
        entry_input = 'A'  
    elif event in ('Ok','\r'):
        #if True: #values['-INPUT-']:
        entry_input =  values['-INPUT-']
        print("{:>50}".format(entry_input))
        window['-INPUT-'].update('')
    message,cartes = partie.action(entry_input)
    #if partie.etat in (tr.DISTRIBUE,tr.ECART,tr.CARTES_RASSEMBLEES,tr.PLI_EN_COURS):
    affiche_noms(window['canvas'],partie)
    if len(cartes)>0 or partie.etat==tr.PRET :
        window['-OUTPUT-'].print(' '.join(cartes))
        affiche_cartes(window['canvas'],partie,cartes,images_cartes)
    affiche_entames(window,partie)
    window['-OUTPUT-'].print(message)
    message = partie.get_message()
    window['-OUTPUT-'].print(message)
            
       

window.close()
