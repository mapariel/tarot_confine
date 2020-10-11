#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 09:14:09 2020

@author: martin
"""

import PySimpleGUI as sg
import PIL.Image
import io
import base64
import math 
import threading 
import server_tarot as sv
import tarot as ta


# for the nework connexions
import socket
import types
# import  select
import selectors
import xml.dom.minidom as dom

# import logging
# logging.basicConfig(level=logging.WARNING)



sg.theme('DarkAmber')
WIDTH = 1200
HEIGHT = 780
W_CARTE = 96
H_CARTE = 171


selector = selectors.DefaultSelector()

# messages from and to the server 
msg = {"command":"".encode(),"infos":""} 
# command = "".encode()
# infos = ""






def convert_to_bytes(file_or_bytes, resize=None):
    '''
    Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
    Turns into  PNG format in the process so that can be displayed by tkinter
    :param file_or_bytes: either a string filename or a bytes base64 image object
    :type file_or_bytes:  (Union[str, bytes])
    :param resize:  optional new size
    :type resize: (Tuple[int, int] or None)
    :return: (bytes) a byte-string object
    :rtype: (bytes)
    '''
    if isinstance(file_or_bytes, str):
        img = PIL.Image.open(file_or_bytes)
    else:
        try:
            img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
        except Exception:
            dataBytesIO = io.BytesIO(file_or_bytes)
            img = PIL.Image.open(dataBytesIO)

    cur_width, cur_height = img.size
    if resize:
        new_width, new_height = resize
        scale = min(new_height/cur_height, new_width/cur_width)
        img = img.resize((int(cur_width*scale), int(cur_height*scale)), PIL.Image.ANTIALIAS)
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    del img
    return bio.getvalue()





def connect_server(host,port,nom):
    server_addr = (host, port)
    print("starting connection to", server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(inb="")
    selector.register(sock, events,data=data)
    return True




def service_connection(key, mask,msg):
    global state
    global menu_def 
    
    sock = key.fileobj
    data = key.data 
    if mask & selectors.EVENT_READ:
        try:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                data.inb += recv_data.decode()
                if len(data.inb)>4 and data.inb[-4:]=="#EOM":
                    print("{} bytes received from Server.".format(len(data.inb)))
                    info = data.inb[:-4]
                    data.inb=""
                    return info     
            else :
               print("Fermeture de la connexion client.")
               selector.unregister(sock)
               sock.close()
               state = 0 
               menu_def = get_menu_layout(state)
        except:
            print("Connexion refusée")

    if mask & selectors.EVENT_WRITE:
         if msg["command"] != b"":
             
             # we just leave the server
             if msg["command"] in [b"STOP#EOM"] :
                  print("close the connexion")
                  selector.unregister(sock)
                  sock.close()
                  return

                 
             sent = sock.send(msg["command"])
             print("sending {} bytes to server.".format(sent))
             msg["command"] = msg["command"][sent:]
             


    




def window_connexion():
        layout = [
                 [sg.Text(text="Entrez les informations de connexion",size=(30,1)) ],
                 [sg.Text('{:15}:'.format('hôte'),size=(12,1)),sg.Input(key='__HOST__',size=(20,1),default_text="localhost")],
                 [sg.Text('{:15}:'.format('port'),size=(12,1)),sg.Input(key='__PORT__',size=(20,1),default_text="12800")],
                 [sg.Text('{:15}:'.format('Votre nom'),size=(12,1)),sg.Input(key='__NOM__',size=(20,1),default_text="")],
                 [sg.Button('Valider'),sg.Button('Annuler')]
                 ] 
        window2 = sg.Window("Connexion au serveur", layout,keep_on_top=True)
        event,values = window2.read()
        window2.close()
        if event == 'Valider':
            host = values['__HOST__']
            port = int(values['__PORT__'])
            nom = values['__NOM__']
            return host,port,nom
        
        
            
def window_demarrer_serveur():
    number_of_players = 3
    variante = ta.Tarot.SANS 
    layout = [
        [sg.Text(text="Entrez les informations sur la partie et sur le serveur",size=(30,1))],
        [sg.Text('{:15}:'.format('port'),size=(12,1)),sg.Input(key='__PORT__',size=(20,1),default_text="12800")],
        
        [sg.Text('{:15}:'.format('Votre nom'),size=(12,1)),sg.Input(key='__NOM__',size=(20,1))],  
        [sg.Radio("trois",1,key="__TROIS__"),sg.Radio("quatre",1,key="__QUATRE__"),sg.Radio("cinq (appel au roi)",1,key="__APPEL__")
                  ,sg.Radio("cinq (avec un mort)",1,key="__MORT__")],

        [sg.Radio("Jeu à plusieurs",2,default=True,key="__PLUSIEURS__"),sg.Radio("Jouer tout seul",2,key="__SEUL__")],
        
        [sg.Button('Valider'),sg.Button('Annuler')],
        ]
    window2 = sg.Window("Démarrer le serveur", layout,keep_on_top=True)
    event,values = window2.read()
    window2.close()
    
    if event == 'Valider':
            if values["__QUATRE__"]:
                number_of_players = 4
            elif values["__APPEL__"]:
                number_of_players = 5
                variante = ta.Tarot.APPEL_AU_ROI
            elif values["__MORT__"]:    
                number_of_players = 5
                variante = ta.Tarot.MORT
            test=False
            if values["__SEUL__"]:
                test = True        
            partie = ta.Tarot(number_of_players,variante)
            port = int(values['__PORT__'])
            nom = values['__NOM__']
            threaded_server = threading.Thread(target=sv.serve, args=(partie,test,port,), daemon=True)
            threaded_server.start()
            
            return '',port,nom
    window2.close()
    
            






class Jeu():
    def __init__(self,window,message=""):
        self.infos = {}
        self.infos["choix"] = []
        self.window = window 
        # load the cards
        if message :
            xml = dom.parseString(message)
            
            if xml.getElementsByTagName("infos")[0].hasAttribute("joueur"):
                self.infos["my_index"] = int(xml.getElementsByTagName("infos")[0].getAttribute("joueur"))
            else :
                self.infos["my_index"] = 0
            # index of this player in the game
            
            # fetches the name of the players
            n_joueurs = len(xml.getElementsByTagName("joueur"))
            self.infos["noms"] = ['']*n_joueurs                            
            for nom in xml.getElementsByTagName("joueur"):
                index = int(nom.getAttribute("index"))
                self.infos["noms"][index] = nom.lastChild.data
            
            for child in xml.getElementsByTagName("cartes"):
                place = child.getAttribute("place")
                cartes = child.lastChild.data
                cartes = cartes.split(',')
                self.infos[place] = cartes
            for choix in xml.getElementsByTagName("choix"):
                c = choix.getAttribute("commande")
                t = choix.lastChild.data
                self.infos["choix"].append((c,t))
                                                 
            if len(xml.getElementsByTagName("message"))==1:
                self.infos["message"] = xml.getElementsByTagName("message")[0].lastChild.data
            if len(xml.getElementsByTagName("result"))==1:
                self.infos["result"] = xml.getElementsByTagName("result")[0].lastChild.data
            if len(xml.getElementsByTagName("index_entame"))==1:
                self.infos["index_entame"] = int(xml.getElementsByTagName("index_entame")[0].lastChild.data)
            if len(xml.getElementsByTagName("index_joueur"))==1:
                self.infos["index_joueur"] = int(xml.getElementsByTagName("index_joueur")[0].lastChild.data)
            if len(xml.getElementsByTagName("index_preneur"))==1:
                self.infos["index_preneur"] = int(xml.getElementsByTagName("index_preneur")[0].lastChild.data)
            # the second attaquant in case of variante appel au roi
            if len(xml.getElementsByTagName("index_attaquant"))==1:
                self.infos["index_attaquant"] = int(xml.getElementsByTagName("index_attaquant")[0].lastChild.data)
            if len(xml.getElementsByTagName("index_mort"))==1:
                self.infos["index_mort"] = int(xml.getElementsByTagName("index_mort")[0].lastChild.data)




        else :
            self.infos["message"] = "Vous pouvez joindre un jeu."
            # self.infos["main"] = ['1','2','3','4','2tr']
            #self.infos["pli"] =['rtr','3tr','_','_']
            self.infos["ecart"] =['1','21','e']
            self.infos["noms"]=[]
            # self.infos["my_index"]=2
            # self.infos["index_entame"]=0
            # self.infos["index_joueur"]=2
            # self.infos["index_preneur"]=3
            # self.infos["choix"]=[("JOUER","joueur la carte"),("ANNULER","annuler le coup")]
            # self.infos["levee"] = ['1','2','3','4','2tr','5tr','rtr','4pi','5pi','5','6','cco','e',
            #                      '1','2','3','4','2tr','5tr','rtr','4pi','5pi','5','6','cco','e']
        self.pointable_items = {}  # {1:'rpi',4:'2tr'} keys are items of cards in main 
        self.selected_abr = []    # ['rpi','2tr'] abreviations of the selected cards
    
    
    def get_baseline(self,ratio=1):
        """
        Where (vertically) to put the cards that are not selected

        Returns
        -------
        baseline : int
            y-coordinates of the cards in main.
        offset : int
            how much to push the selected cards.

        """
        baseline = HEIGHT-(H_CARTE+10)  # y-coordinate of the cards in main
        offset = -50
        return baseline*ratio,offset*ratio
    

    def align_main(self,ratio=1):
            """
            Put the cards of main on the correct y-coordinate (+offset when selected)

            Returns
            -------
            None.

            """
            for i,a in self.pointable_items.items():
                x,y = self.window['__TAPIS__'].GetBoundingBox(i)[0]
                y,offset = self.get_baseline(ratio)
                if a in self.selected_abr:
                    y = y+offset
                self.window['__TAPIS__'].RelocateFigure(i,x,y)


    def draw_canvas(self,ratio=1): 
        
        baseline,offset =  self.get_baseline()
        self.pointable_items = {} 
        self.window['__TAPIS__'].Erase()      
        # draw the main
        if "main" in self.infos:
            # there are n cards, k of it is visible, the rest covered by the following
            n = len(self.infos["main"])
            k = (WIDTH-50-W_CARTE)/((12)*W_CARTE)
            hspace = (WIDTH-W_CARTE-(n-1)*k*W_CARTE)/2
            if n>=13 :
                k = (WIDTH-50-W_CARTE)/((n-1)*W_CARTE)
                hspace = 25  # gap on the left and on the right
            
            for i,abr in enumerate(self.infos["main"]):
                a = self.window['__TAPIS__'].DrawImage(
                data=convert_to_bytes('cartes/'+abr+'.png',resize=(W_CARTE*ratio,H_CARTE*ratio)),
                location=(hspace+i*W_CARTE*k,baseline))
                self.pointable_items[a]=abr
        if "chien" in self.infos:
            n = len(self.infos['chien'])
            k = 1.1
            hspace = (WIDTH-W_CARTE-(n-1)*k*W_CARTE)/2
            for i,abr in enumerate(self.infos['chien']):
                x,y = hspace+i*W_CARTE*k,HEIGHT/2-H_CARTE
                self.window['__TAPIS__'].DrawImage(
                        data=convert_to_bytes('cartes/'+abr+'.png',resize=(W_CARTE*ratio,H_CARTE*ratio)),
                        location=(x,y))
                
                
        if "ecart" in self.infos:
            n = len(self.infos['ecart'])
            k = 1.1
            hspace = (WIDTH-W_CARTE-(n-1)*k*W_CARTE)/2
            for i,abr in enumerate(self.infos['ecart']):
                x,y = hspace+i*W_CARTE*k,HEIGHT/2-H_CARTE
                self.window['__TAPIS__'].DrawImage(
                        data=convert_to_bytes('cartes/'+abr+'.png',resize=(W_CARTE*ratio,H_CARTE*ratio)),
                        location=(x,y))



        if "pli" in self.infos:
            angle0 = (self.infos["my_index"]+1)*2*math.pi/len(self.infos["noms"])
            # angle to have this player always playing South (subjective view) 

            n = len(self.infos['pli'])
            # draw the pli
            for i,abr in enumerate(self.infos['pli']):
                angle = angle0-i*2*math.pi/n
                x,y = 600+240*math.cos(angle), 300+230*math.sin(angle)
                self.window['__TAPIS__'].DrawText(self.infos["noms"][i],(x,y),font='Courier 14')
                
                if abr != '_':
                    x,y = 600-W_CARTE/2+120*math.cos(angle), 300-H_CARTE/2+80*math.sin(angle)
                    self.window['__TAPIS__'].DrawImage(
                        data=convert_to_bytes('cartes/'+abr+'.png',resize=(W_CARTE*ratio,H_CARTE*ratio)),
                        location=(x,y))
                 
            angle = angle0-self.infos["index_entame"]*2*math.pi/n    
            x,y = 600+240*math.cos(angle), 300+230*math.sin(angle)+20
            self.window['__TAPIS__'].DrawImage(
                        data=convert_to_bytes('cartes/chevron1.png',resize=(20*ratio,20*ratio)),
                        location=(x,y))   
            angle = angle0-self.infos["index_joueur"]*2*math.pi/n    
            x,y = 600+240*math.cos(angle), 300+230*math.sin(angle)+20
            self.window['__TAPIS__'].DrawImage(
                        data=convert_to_bytes('cartes/chevron2.png',resize=(20*ratio,20*ratio)),
                        location=(x,y))    
            angle = angle0-self.infos["index_preneur"]*2*math.pi/n    
            x,y = 600+240*math.cos(angle), 300+230*math.sin(angle)-50
            self.window['__TAPIS__'].DrawImage(
                        data=convert_to_bytes('cartes/couronne1.png',resize=(30*ratio,30*ratio)),
                        location=(x,y))    
            if  "index_attaquant" in self.infos:
                angle = angle0-self.infos["index_attaquant"]*2*math.pi/n    
                x,y = 600+240*math.cos(angle), 300+230*math.sin(angle)-50
                self.window['__TAPIS__'].DrawImage(
                        data=convert_to_bytes('cartes/couronne2.png',resize=(30*ratio,30*ratio)),
                        location=(x,y))    
            if  "index_mort" in self.infos:
                angle = angle0-self.infos["index_mort"]*2*math.pi/n    
                x,y = 600+240*math.cos(angle), 300+230*math.sin(angle)-50
                self.window['__TAPIS__'].DrawImage(
                        data=convert_to_bytes('cartes/mort.png',resize=(30*ratio,30*ratio)),
                        location=(x,y))    


                


            
            
        if "levee" in self.infos:
             n = len(self.infos['levee'])
             n_cols = (n//2)//10+1
             hspace = (WIDTH-n_cols*W_CARTE*2-(n_cols-1)*W_CARTE*0.1)/2
             for col in range(n_cols):
                 x = hspace+W_CARTE*col*1.1*2
                 for j in range(10):
                         y = H_CARTE*j*0.4
                         index = 2*(10*col+j)
                         try:
                             abr = self.infos['levee'][index]
                             self.window['__TAPIS__'].DrawImage(
                                data=convert_to_bytes('cartes/'+abr+'.png',resize=(W_CARTE*ratio,H_CARTE*ratio)),
                                location=(x,y))
                             abr = self.infos['levee'][index+1]
                             self.window['__TAPIS__'].DrawImage(
                                data=convert_to_bytes('cartes/'+abr+'.png',resize=(W_CARTE*ratio,H_CARTE*ratio)),
                                location=(x+W_CARTE,y))
                         except:
                              pass
                     
             
            
            

    def draw(self):
        self.draw_canvas()            
        # update the choices
        for i in range(6):
            self.window["BOUTON"+str(i)].update(visible=False,button_color=("black","yellow"))
        for i,choi in enumerate(self.infos['choix']):
            txt_choix = self.infos['choix'][i][1]
            for j,nom in enumerate(self.infos["noms"]):
                txt_choix = txt_choix.replace("Joueur{}".format(j), nom)
            self.window["BOUTON"+str(i)].update(text=txt_choix,visible=True)
            if i==0 :
                self.window["BOUTON"+str(i)].SetFocus()
        self.align_main()  
        message = ""
        if "result" in self.infos: message = message+self.infos["result"]+'\n'         
        if "message" in self.infos: message = message+self.infos["message"] 
        
        # put the names of the players
        for i,nom in enumerate(self.infos["noms"]):
            message = message.replace("Joueur{}".format(i), nom)
        
        self.window["__MESSAGE__"].update(message)




def get_layout():
    boutons =[[sg.InputText(key="__NOM__",size=(20,1)),sg.OK()]]+ [[sg.Text("",size=(30,5),auto_size_text=True,key="__MESSAGE__")]] +[[
        sg.Button(button_text="BOUTON"+str(0),key="BOUTON"+str(0),size=(40,2),visible=False,bind_return_key=True)]]+ [[
        sg.Button(button_text="BOUTON"+str(i),key="BOUTON"+str(i),size=(40,2),visible=False)] 
        for i in range(1,6) ]  
    colonne = sg.Column(boutons,key="__COLONNE__") 
    layout = [  [sg.Menu([],key="__MENU__"),],
               [sg.Graph((WIDTH,HEIGHT),(0,HEIGHT),(WIDTH,0)
              ,background_color='green',key='__TAPIS__'
              ,float_values=True,enable_events=True,drag_submits=False),colonne ]]

    return layout    


def get_menu_layout(state):
    menu_def = []
    if state == 0 :
        menu_def = [ ['&Serveur',
                          ['&Joindre une partie::JOINDRE',
                           '!&Quitter la partie::STOP',
                           '&Créer une partie::CREER'
                           ,'!&Supprimer la partie::SUPPRIMER'],
                          ],
                        ['&Tailles de cartes',['&Augmenter(+)::PLUS_GRAND','&Diminuer(-)::PLUS_PETIT']],
                        ['&Aide',['&aide rapide','&licence','à &propos'] ]
                    ]
    elif state == 1 :
        menu_def = [ ['&Serveur',
                          ['&!Joindre une partie::JOINDRE',
                           '!&Quitter la partie::STOP',
                           '!&Créer une partie::CREER',
                           '&Supprimer la partie::SUPPRIMER'],
                          ],
                    ['&Tailles de cartes',['&Augmenter(+)::PLUS_GRAND','&Diminuer(-)::PLUS_PETIT']],
                    ['&Aide',['&aide rapide','&licence','à &propos']]
                    ]
    elif state == 2 :
        menu_def = [ ['&Serveur',
                          ['&!Joindre une partie::JOINDRE',
                           '&Quitter la partie::STOP',
                           '&!Créer une partie::CREER'
                           ,'&!Supprimer la partie::SUPPRIMER'],
                          ],
                      ['&Tailles de cartes',['&Augmenter(+)::PLUS_GRAND','&Diminuer(-)::PLUS_PETIT']],
                     ['&Aide',['&aide rapide','&licence','à &propos']]
                    ]
    return menu_def


def rescale():
    # draws the game with the correct ratio
    # thos must be called immediately after jeu.draw has been called
    global jeu
    global ratio
    global canvas 
    jeu.draw_canvas(ratio)
    canvas.scale("all",0,0,ratio,ratio)
    jeu.align_main(ratio) 
    canvas.config(width=WIDTH*ratio, height=HEIGHT*ratio)



         
if __name__ == '__main__':
               
    """                
    """
    host = ""
    port = None
    nom = ""  # name of this player
    connexion_avec_serveur = None # connection to the server
    
    """
    """
    state = 0 # not connected # 1: game created # 2 : game joined
    
    
    layout = get_layout()
    menu_def = get_menu_layout(state)
    
    
    window = sg.Window('Tarot en Ligne',layout,return_keyboard_events=True
                       ,resizable=True,no_titlebar=False
                       ,use_default_focus=False,finalize=True)
  
    window["__MENU__"].update(menu_def)
    window['__COLONNE__'].expand(expand_y=True)
    window['__TAPIS__'].expand(expand_x=True,expand_y=True)
    window['__TAPIS__'].bind("<Motion>",'MOTION')
    window['__TAPIS__'].bind("<Double-Button-1>",'DOUBLE')
    
    canvas = window['__TAPIS__'].TKCanvas 
    
    
    jeu =Jeu(window)
    jeu.draw()
    ratio = 1  #, zoom in if ratio>1, zoom out if <1
    
    
    
    
    while True:

        if selector.get_map():
            socket_events = selector.select(timeout=-1)
            if socket_events:
                for key, mask in socket_events:
                    msg["infos"] = service_connection(key, mask,msg)
                    if msg["infos"]:
                        jeu =Jeu(window,msg["infos"])  
                        jeu.draw()
                        rescale()

        else : 
            jeu = Jeu(window)
            jeu.draw()
            rescale()

        window.Refresh()    
     
        event,values = window.read(timeout=10)
        if True :
            # if event != "__TIMEOUT__" : print(event,values)
            if event in (None, 'QUITTER'):
                selector.close()
                break
            
            # management of the connection with the server 
            if "JOINDRE" in event:
                rep =  window_connexion()
                if rep:
                    host,port,nom = rep
                    connexion_avec_serveur = connect_server(host,port,nom)
                    state = 2
                    menu_def  = get_menu_layout(state)
                    window['__NOM__'].update(value=nom)
                    window['__MENU__'].update(menu_def)
                    sg.popup("{} vous venez de rejoindre la partie sur le port {} de l'hôte {}.".format(nom,port,host))
                    msg["command"] = ("NOMMER {}#EOM".format(nom)).encode()
            
            elif "SUPPRIMER" in event :
                msg["command"] = 'FIN#EOM'.encode()
                state = 0
                menu_def  = get_menu_layout(state)
                window['__MENU__'].update(menu_def)
                sg.popup('La partie est supprimée.')
    
            
            elif "STOP" in event :
                msg["command"] = 'STOP#EOM'.encode()
                state = 0
                menu_def  = get_menu_layout(state)
                window['__MENU__'].update(menu_def)
    
                
            elif "CREER" in event:
                rep = window_demarrer_serveur()
                if rep :
                    host,port,nom  = rep                
                    connexion_avec_serveur = connect_server('localhost',port,nom)
                    state = 1
                    menu_def  = get_menu_layout(state)
                    window['__MENU__'].update(menu_def)
                    window['__NOM__'].update(value=nom)
                    sg.popup('{}, vous venez de créer une partie'.format(nom),'Demandez aux autres joueurs de vous rejoindre.',
                             "Le port est {} et l'hôte est votre adresse IP".format(port))
                    msg["command"] = ("NOMMER {}#EOM".format(nom)).encode()
            elif event in ('aide rapide','licence','à propos','voir le jeu du prochain joueur'):  
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
                sg.popup_scrolled(texte,title=event,size=size)
                window.active=True
                continue

    
    
            if event=="OK":
                nom = window["__NOM__"].get()
                if selector.get_map():
                    msg["command"] = ("NOMMER {}#EOM".format(nom)).encode()
                
       
            if "BOUTON" in event :
                window[event].update(button_color=("red","green"))
                # get the aaction corresponding to the button pressed
                action = jeu.infos['choix'][int(event[-1])][0]
                cartes = jeu.selected_abr
                if len(cartes)==0:
                    msg_temp = action+"#EOM" 
                    # action always finishes with #EOM
                else : msg_temp = action+" "+",".join(cartes)+"#EOM"
                
                if connexion_avec_serveur :
                    msg["command"] = msg_temp.encode()
                    #connexion_avec_serveur.send(msg.encode())
                
                
            elif event == '+' or 'PLUS_GRAND' in event:
                ratio = ratio*1.1
                rescale()
            elif event == '-' or 'PLUS_PETIT' in event:
                ratio = ratio/1.1
                rescale()
                
            elif event in ["__TAPIS__MOTION"]:
                jeu.align_main(ratio)
                carte = canvas.find_withtag("current")
                
                if len(carte) != 0 : 
                    i = carte[0]  # item
                    if i in jeu.pointable_items: # the card belongs to main
                        a = jeu.pointable_items[i]          # abreviation
                        x,y = window['__TAPIS__'].GetBoundingBox(i)[0]
                        _,offset = jeu.get_baseline(ratio)
                        if a not in jeu.selected_abr:    
                            y = y+offset
                            window['__TAPIS__'].RelocateFigure(i,x,y) 
            elif event in ["__TAPIS__DOUBLE"]:
                carte = canvas.find_withtag("current")
                if 'choix' in jeu.infos and len(jeu.infos['choix'])>0:
                    # double click works only when the player can make a choice
                    window['BOUTON0'].Click()
                         
            elif event in ["__TAPIS__"]:
                carte = canvas.find_withtag("current")
                if len(carte) != 0 :
                    i = carte[0]
                    if i in jeu.pointable_items: # the card belongs to main
                        a = jeu.pointable_items[i]
                        if a in jeu.selected_abr:
                            jeu.selected_abr.remove(a)
                        else:
                            jeu.selected_abr.append(a)
                    jeu.align_main(ratio)        
    
    
                
                        
                    
            
        #elif not event in ["__TIMEOUT__",'+']: print(event,values)
            
    
    
    
