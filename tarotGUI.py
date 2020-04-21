# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 14:46:32 2020

@author: MartinMoritz
"""

import tkinter as tk
import tkinter.font as tkFont
import tkinter.scrolledtext as tkS
import tarot as tr
import PIL as pil  # ImageTk,Image
import PIL.ImageTk as pitk
import PIL.ImageDraw as pildraw
import PIL.ImageFont as pilfont


from mail import Distributeur
from tarot import CARTES_RASSEMBLEES
import numpy as np
import time
#coord = [[300,200],[200,300],[300,400],[400,300]] +np.random.normal(loc=0.0, scale=10,size =(4,2))




def affiche_noms():
    """
    Affiche les noms des joueurs
    """
    global width,height

    n = partie.nombre()
    angles = np.arange(n)
    angles = angles*2*np.pi/n
    angles = np.array(angles)
    centre = np.array([width/2,height/2])
    centre.shape=(2,1)
    coord_noms = centre+350*np.vstack((np.cos(-angles),np.sin(-angles)))
    #coord_noms = np.array([[width],[height]])+coord_noms
    for i in range(n):
        thisf = f.copy()

        nom = str(i)+'_'+str(partie.joueurs[i])
        if partie.preneur_index == i:
            thisf.configure(underline=True)
        canvas.create_text(coord_noms[0,i],coord_noms[1,i],fill=couleur
                ,font=thisf,text=nom  )
    canvas.update()    
    

def affiche_cartes(cartes):
    """
    Affiche les cartes de la parties, la disposition change en fonction du nombre de
    cartes : 4 (un pli), 6 (chien ou écart), sinon (levée)
    """
    global images_cartes
    # les joueurs sont 0: Nord, 1 : Ouest, 2 :sud, 3. Est

    if len(cartes)<6:
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
              #img = pitk.PhotoImage(img)
              canvas.create_image(coord[0,i],coord[1,i],image=img) 
    else :
        x = 200
        dx = width-500
        # affichage du chien ou de l'écart
        if len(cartes)==6 : 
            for i,carte in enumerate(cartes) :
                img = images_cartes[carte]
                #img = pitk.PhotoImage(img)
                
                x = x+dx/len(cartes)
                canvas.create_image(x,height/2,image=img) 
        # les cartes sont affichées deux par deux
        else :
            compteur = 0 
            score = canvas.create_text(width/2,height-200,fill=couleur,font=f,text=str(compteur)  )
            
            iterator = iter(partie.levee[0]) 
            while True :
                coord = [[width/2-50,height/2],[width/2+50,height/2]] +np.random.normal(loc=0.0, scale=10,size =(2,2))
                try:
                    carte1 =next(iterator)
                    carte2 =next(iterator)
                    compteur +=  carte1.points+carte2.points
                    img1 = images_cartes[carte1.abbr]
                    img2 = images_cartes[carte2.abbr]
                    canvas.create_image(coord[0,1],coord[0,1],image=img1) 
                    canvas.create_image(coord[1,0],coord[1,1],image=img2)
                    canvas.delete(score)
                    score = canvas.create_text(width/2,height-200,fill=couleur,font=f,text=str(compteur)  )
                    time.sleep(0.5)
                    canvas.update()
                except StopIteration:
                    break

        
def maj_partie(event):
    global i
    global output_text
    global partie
    global instruction


    # après chaque partie 
    # les joueurs peuvent changer
    if partie.etat == CARTES_RASSEMBLEES:
        distributeur = Distributeur()
        partie.distributeur = distributeur
        partie.initialise_joueurs()
        canvas.delete("all")
        
        affiche_noms()
#    img = images_cartes[abbr]
#    canvas.create_image(coord[i][0],coord[i][1],image=img)   
#    i = (i+1)%4
    entry_input =  instruction.get()
    # supprime l'entree de la ligne de commande
    event.widget.delete(0,'end')
    
    if entry_input:
        output_text.insert(tk.END,"\n \t \t "+entry_input)

    message,cartes = partie.action(entry_input)
    if cartes :
        if len(cartes)>0:
            canvas.delete("all")
            affiche_noms()
            affiche_cartes(cartes)
            cartes = " ".join(cartes)
            output_text.insert(tk.END,"\n "+cartes)
    if message !='':
        output_text.insert(tk.END,"\n "+message)

            
    output_text.see(tk.END)
    
    
    
    message = partie.get_message()
    if message !='':
        output_text.insert(tk.END,"\n "+message)    
        output_text.see(tk.END)
    #view(tk.END)    
      
    
if __name__ == '__main__':



    

    i=0
    root = tk.Tk()
    couleur = "darkblue"
    f = tkFont.Font()
    f.configure(family="Times",size=20,weight="bold")



    # les dimensions du canvas
    width = 1000  
    height = 800

#    label = tk.Label(root, text = "Instruction")
#    label.pack()

    frame1 = tk.Frame()
    frame2 = tk.Frame()
    frame1.pack(side='left')
    frame2.pack(side='right')

    
    fontText = tkFont.Font(family="Arial", size=12)

    canvas = tk.Canvas(frame1,width=width,height=height,background='green')
    canvas.pack(fill='x') 

    
    output_text = tkS.ScrolledText(frame2,height=40,width=40,state='normal')
    output_text.configure(font=fontText)
    output_text.pack(fill='y')
    
    instruction = tk.StringVar()
    input_entry = tk.Entry(frame2, width=40,textvariable = instruction)
    input_entry.configure(font=fontText)
    input_entry.bind('<Return>',maj_partie)
    input_entry.pack(fill='x')

    
    # le canvas où se trouve le tapis de cartes
    
    
    # une carte posée sur le tapis
    
    distributeur = Distributeur()               
    
    #donneur = int(input("Premier donneur : "))
    partie = tr.Partie(donneur_index=0,distributeur=distributeur,debug=False)


#    https://stackoverflow.com/questions/43435805/photoimage-instance-has-no-attribute-resize
    
    images_cartes = {}
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
                pildraw.Draw(img).text((115,5),str(carte.valeur),color,font=f2)
                pildraw.Draw(img).text((5,213),str(carte.valeur),color,font=f2)
                pildraw.Draw(img).text((115,213),str(carte.valeur),color,font=f2)
        
        img = pitk.PhotoImage(img)
        images_cartes[abbr] =  img
        # 
    affiche_noms()  
    # charge le premier message
    message = partie.get_message()
    output_text.insert(tk.END,"\n "+message) 


    root.mainloop() 
    
    
    """
    button = tk.Button(root, text = "OK", command = clickMe)
    button.pack()   
    """

    
   

    

      