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
height = 800
images_cartes = {}
distributeur = Distributeur()
partie = tr.Partie(donneur_index=0,distributeur=distributeur,debug=False)
message = partie.get_message()



"""
Définition de l'interface graphique
"""
entames = [ [sg.Text(size=(20,1),key='INFOS_'+famille,font=('Helvetica',14),text_color='white',justification='center')]   
                        for famille in ['pique','coeur','carreau','trefle','atout']   ] 


colonne =[ [sg.Multiline(default_text=message,disabled=True,size=(30,30),key='-OUTPUT-',font=('Helvetica',12),autoscroll=True)],
            [sg.InputText(size=(10,1),key='-INPUT-',font=('Monospace', 16)),
             sg.Button('Ok'),sg.Button('Cancel'),
             ]
          ]  
colonne = colonne+[[sg.Text(size=(20,3))]]+entames           
          
            

layout = [  [sg.Text('Jeu de tarot')],
            [sg.Column(colonne),
             sg.Canvas(size=(width,height),background_color='green', key='canvas')
             ]
        ]
# Create the Window
window = sg.Window('Tarot Confiné', layout,return_keyboard_events=True)



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
    canvastk.delete('noms_joueurs')    

    n = partie.nombre()
    angles = np.arange(n)
    angles = angles*2*np.pi/n
    angles = np.array(angles)
    centre = np.array([width/2,height/2])
    centre.shape=(2,1)
    coord_noms = centre+350*np.vstack((np.cos(-angles),np.sin(-angles)))
    for i in range(n):
        nom = str(i)+'_'+str(partie.joueurs[i])
        print(partie.preneur_index)
        if partie.preneur_index == i:
            f_ = f.copy()
            f_.configure(underline=True)
            canvastk.create_text(coord_noms[0,i],coord_noms[1,i],fill="darkblue"
                ,font=f_,text=nom,tags='nom_joueurs')
        else:
            canvastk.create_text(coord_noms[0,i],coord_noms[1,i],fill="darkblue"
                ,font=f,text=nom,tags='nom_joueurs')
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
    
    print('line 122',partie.entames)
    
    
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
            
    



window.read()

f = tkFont.Font()
f.configure(family="Times",size=20,weight="bold")          
"""
chargement des cartes
"""            
images_cartes = load_image_cartes()            
            

window.Refresh()




# Event Loop to process "events"
while True:             
    event, values = window.read()
    if event in (None, 'Cancel'):
        break
    
    if event in ('Ok','\r'):
        #if True: #values['-INPUT-']:
        entry_input =  values['-INPUT-']
        print("{:>50}".format(entry_input))
        window['-INPUT-'].update('')
        message,cartes = partie.action(entry_input)
        if partie.etat in (tr.DISTRIBUE,tr.ECART,tr.CARTES_RASSEMBLEES,):
            affiche_noms(window['canvas'],partie)
        if len(cartes)>0 :
                window['-OUTPUT-'].print(cartes)
                affiche_cartes(window['canvas'],partie,cartes,images_cartes)
        affiche_entames(window,partie)
        window['-OUTPUT-'].print(message)
        message = partie.get_message()
        window['-OUTPUT-'].print(message)
            
        

window.close()