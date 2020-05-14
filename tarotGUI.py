# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 13:29:26 2020

@author: MartinMoritz
"""


import PySimpleGUI as sg
import PIL as pil  # ImageTk,Image
import PIL.Image as pilim
import tarot as tr
from mail import Distributeur
import numpy as np
import time
import csv 
from io import BytesIO
import base64

sg.theme('DarkAmber')   # Add a little color to your windows
# All the stuff inside your window. This is the PSG magic code compactor...
# les dimensions du tapis de jeu

# taille initiale du tapis et des cartes
WIDTH = 800
HEIGHT = 600
W_CARTE = 120
H_CARTE = 214
W_NOM = 100
H_NOM = 20
# constante utilisee pour calculer les coordonnees d'affichage
AFFICHAGE_LIGNE = 0
AFFICHAGE_CERCLE = 1
AFFICHAGE_NOMS = 2

# lors des animations (calcul du score)
# animation est mis sur start
# puis sur stop a la fin
# pour ne lancer l'animation qu'une seule fois
ANIM_NOT = 0
ANIM_START = 1
ANIM_STOP = 2
animation = ANIM_NOT



images_cartes = {}
distributeur = Distributeur()
partie = tr.Partie(donneur_index=0,distributeur=distributeur,debug=False)
message = partie.get_message()





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
           [sg.Text('Zoom'),
            sg.Slider(range=(100,150),default_value=100,orientation='horizontal',
                     key='zoom',enable_events=True,tick_interval=50),
            sg.Sizer(h_pixels=(WIDTH+80)/2,v_pixels=2),
            sg.Text(text='compteur : '),
            sg.Text(text='--',text_color='black',background_color='white',
                    font=('Monospace',16),key='compteur',size=(4,1),justification='center')
            ],
           [sg.Column(colonne),
            sg.Graph((WIDTH,HEIGHT),(0,HEIGHT),(WIDTH,0),background_color='green',key='tapis')],
        ]  


def get_coordonnee(n_elements,affichage,compact=False):
    """
    Parameters
    ----------
    n_elements : TYPE
        DESCRIPTION.
    affichage : TYPE
        DESCRIPTION.
    compact: Boolean
        False : les cartes en ligne utilisent la largeur disponible
    Returns
    -------
    coordonnees : TYPE
        DESCRIPTION.
    """
    # affichage centre horizontal 
    if affichage == AFFICHAGE_LIGNE:
        coordonnees = np.ones(shape=(n_elements,2))
        coordonnees[:,1] = coordonnees[:,0]*(HEIGHT-H_CARTE)/2

        if compact :
            coordonnees[:,0] = WIDTH/2-0.9*W_CARTE*n_elements/2+np.arange(n_elements)*W_CARTE*0.9
        else:
            coordonnees[:,0] = np.arange(n_elements)*(WIDTH-2*W_NOM-W_CARTE)/(n_elements-1)+W_NOM
        return coordonnees
    if affichage in(AFFICHAGE_CERCLE,AFFICHAGE_NOMS) :
        angles = np.arange(n_elements)
        angles = angles*2*np.pi/n_elements
        #angles = np.array(angles)
        centre = np.array([WIDTH/2,HEIGHT/2])
        if affichage == AFFICHAGE_CERCLE :
            rayon_h = (WIDTH-2*W_NOM-W_CARTE)/4
            rayon_v = (HEIGHT - 2*H_NOM-H_CARTE)/4
        elif affichage == AFFICHAGE_NOMS :
            rayon_h = (WIDTH-2*W_NOM)/2
            rayon_v = (HEIGHT-2*H_NOM)/2
        centre.shape=(1,2)
        coordonnees = centre+np.vstack((rayon_h*np.cos(-angles),rayon_v*np.sin(-angles))).T
        if affichage == AFFICHAGE_CERCLE :
            coordonnees = coordonnees-[W_CARTE/2,H_CARTE/2]
        return coordonnees


def load_images_cartes():
    """
    Loads the images of the cards. This function is called once for all at the beginning
    returns:
        a dictionary with the images
    """
    images_cartes = {}
    with open('cartes.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for line in reader:
            abbr = line[4]
            im = pilim.open('cartes/'+abbr+'.png')
            im = im.resize((W_CARTE, H_CARTE))
            images_cartes[abbr] = im
    return images_cartes     

def scale_image_cartes(images_cartes,zoom,cartes):
    """
    calcules the scaled picture(accroding to the zoom) of the cards, only for cards that are visible on the screen
    returns :
        a dictionary with the scaled pictures
    """
    scaled_images_cartes = {}
    for carte in cartes:
        if carte is None:
            continue 
        abbr = carte.abbr
        im = images_cartes[abbr]
        (width, height) = (int(im.width *zoom) , int(im.height*zoom))
        im_resized = im.resize((width, height))
        buffered = BytesIO()
        im_resized.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue())
        scaled_images_cartes[abbr] = img_str
    return scaled_images_cartes 


        
def update_noms(tapis,partie,zoom):
    """
    affiche les noms sur le tapis
    """ 
    noms = [j.nom for j in  partie.joueurs]
    coordonnees = get_coordonnee(partie.nombre(), AFFICHAGE_NOMS)*zoom
    for i,nom in enumerate(noms):
        nom = "{}: {}".format(i,nom)
        style= ''
        if i == partie.preneur_index:
            style = 'bold italic '
        if i == partie.joueur_index and not partie.pli.complet():
            style = style+'underline'
            
        tapis.DrawText(nom,font=('Any',16,style),color='darkblue',
                       location=(coordonnees[i,0],coordonnees[i,1]))  
        
        
    

def update_cartes(tapis,cartes,coordonnees,images_cartes,zoom,lot_de_cartes=0): 
    """
    affiche les cartes sur le tapis aux coordonnées indiquées
    Args :
        cartes              : un tableau contenant les cartes à afficher
        coordonnees         : un array numpy de shape (len(cartes),2)
        coordonnees images  : le tableau qui contient toutes les cartes
        zoom                : le niveau de zoom à afficher
        lot_de_cartes           : entier, affiche les cartes par lot dans le cas d'une animation
        
    """ 
    global animation
    images_cartes = scale_image_cartes(images_cartes,zoom,cartes)
    coordonnees = coordonnees*zoom
    for i,carte in enumerate(cartes):
        if carte is None: 
            continue
        if lot_de_cartes !=0 : index = i % lot_de_cartes
        else : index = i
        tapis.DrawImage(data = images_cartes[carte.abbr],location=(coordonnees[index,0],coordonnees[index,1]))
        if lot_de_cartes !=0 and index == lot_de_cartes-1:
            score = sum(c.points for c in cartes[:i+1])
            window['compteur'].update('{:d}'.format(int(score)).zfill(2))
            time.sleep(1)
            coordonnees = coordonnees+[0.005*W_CARTE*zoom,0.005*H_CARTE*zoom]
            window.Refresh()
    if animation == ANIM_START:
         animation = ANIM_STOP

    
        
def update(tapis,partie,images_cartes,zoom):
    """
    Met à jour l'affichage de la partie :
    Selon la phase de jeu
    1_affiche le noms des joueurs    
    2_selon la phase de jeu affiche les cartes sur le tapis
    """
    tapis.erase()
    lot_de_cartes = 0
    update_noms(tapis,partie,zoom)
    if partie.etat == tr.PLI_EN_COURS:
        window['compteur'].update(str(partie.tours_restants()).zfill(2))
    
    if partie.etat == tr.AFFICHAGE_CHIEN:
        coordonnees = get_coordonnee(6, AFFICHAGE_LIGNE)
        cartes = partie.chien
    elif partie.etat == tr.PARTIE_FINIE:
        coordonnees = get_coordonnee(6, AFFICHAGE_LIGNE)
        cartes = list(partie.preneur().main.values())
        update_cartes(tapis,cartes,coordonnees,images_cartes,zoom)
        
    elif partie.etat in (tr.PLI_EN_COURS,tr.PLI_FINI):
        coordonnees = get_coordonnee(partie.nombre(), AFFICHAGE_CERCLE)
        cartes = partie.pli.cartes
        cartes = cartes[partie.entame_index:]+cartes[:partie.entame_index]
        coordonnees = np.vstack((coordonnees[partie.entame_index:,:],coordonnees[:partie.entame_index,:]))
    elif partie.etat  == tr.AFFICHAGE_SCORE:
        if animation == ANIM_START:
            cartes = partie.levee[0]
            coordonnees = get_coordonnee(2, AFFICHAGE_LIGNE,compact=True)
            lot_de_cartes = 2
        elif animation == ANIM_STOP :
            cartes = partie.levee[0][-2:]
            coordonnees = get_coordonnee(2, AFFICHAGE_LIGNE,compact=True)
            lot_de_cartes = 0
    else:
        return
    update_cartes(tapis,cartes,coordonnees,images_cartes,zoom,lot_de_cartes)
    
        

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
window = sg.Window('Tarot Confiné', layout,return_keyboard_events=True,resizable=True)
window.read(timeout=100)      
"""
chargement des cartes
"""            
images_cartes = load_images_cartes()            
#window.Disable() 
window_organisateur(distributeur,partie)
window_joueurs(distributeur,partie)
#window.Enable()
zoom = 1
# Event Loop to process "events"
window['tapis'].expand(expand_x=True,expand_y=True)
window.read(timeout=100)

while True:             
    event, values = window.read(timeout=100)
    if event and len(event)==1 and event != '\r':
        continue 
    if event in (None, 'quitter'):
        break
    window['tapis'].expand(expand_x=True,expand_y=True)
    update(window['tapis'],partie,images_cartes,zoom)
    if event in ('zoom'):
        zoom = float(values['zoom'])/100     
       
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
               
            texte = """\n TAROT CONFINE \n \n Martin MORITZ - 2020 \n https://github.com/mapariel/tarot_confine \n\n Bon jeu !"""
   
            size=(50,8)
        elif event == 'voir le jeu du prochain joueur':
             texte = partie.affiche(joueur_index=partie.joueur_index)
             size=(50,8)
        sg.popup_scrolled(texte,title=event,size=size)
        window.active=True
        continue
    
    elif event == 'modifier les joueurs':
        #window.Disable()
        window_joueurs(distributeur,partie)
        #window.Enable()
        continue
    elif event == "modifier l'organisateur":
        #window.Disable()
        window_organisateur(distributeur,partie)
        #window.Enable()
        continue
        
    
    elif event in ('annuler la partie'):
         partie.etat = tr.PARTIE_TERMINEE
         message = partie.get_message()
         window['-OUTPUT-'].print(message)
         continue 
    elif event in ('annuler le coup'):
        partie.annuler_coup()
        
    if event in ('Ok','\r'):
        entry_input =  values['-INPUT-']
        if entry_input!='' : window['-OUTPUT-'].print("{:>50}".format(entry_input))
        window['-INPUT-'].update('')
        message,cartes = partie.action(entry_input)
        if len(cartes)>0 or partie.etat==tr.PRET :
            window['-OUTPUT-'].print(' '.join(cartes))
        #affiche_entames(window,partie)
        window['-OUTPUT-'].print(message)
        message = partie.get_message()
        window['-OUTPUT-'].print(message)
        affiche_entames(window,partie)
        if partie.etat == tr.AFFICHAGE_SCORE:
            if animation == ANIM_NOT:
                animation = ANIM_START
        else :
            animation = ANIM_NOT
          
       

window.close()
