#!/usr/bin/env python

# WS server example
import asyncio
import json
import logging
import websockets
import secrets

import tarot as ta
import phase as ph

# to format tables
import tabulate as tab

logging.basicConfig()



# nombre de joueurs attendus pour la partie
active  = False #the gam eis not active, we are waitong for players to register
partie = ta.Tarot(ta.Tarot.TROIS)
result = ""  # le resultat de la phase de jeu précédente

JOUEURS = []

def get_token():
    token = secrets.token_urlsafe(6)
    token = token.replace('-','_')
    return token


def create_joueurs(n):
    """
    Creates the array for n players
    """
    for i in range(n):
        token = get_token()
        JOUEURS.append({"websocket":None,"name":"Joueur{}".format(i+1),'token':token})

def is_registered(websocket):
    """
    tells if that websocket is a player of the game
    """
    sockets = [j['websocket'] for j in JOUEURS]
    try:
        sockets.index(websocket)
        return True
    except:
        return False
    
def fire_action(data):
    """
    data : JSON
        the command and parameters made by one of the players
    """
    global  result
    global active

    if data["commande"]=="COMMENCER":
        active=True
    elif data["commande"]=="PAUSE":
        active=False
    elif data["commande"]=="SELECT_VARIANTE":
        variante = int(data["variante"])
        partie.ramasser()
        partie.commencer(variante)
        for j in (JOUEURS):
            if not j['websocket']:
                JOUEURS.remove(j)
        nmax=partie.number_of_players
        n=len(JOUEURS)
        if n<nmax:
            for i in range(nmax-n):
                token = get_token()
                JOUEURS.append({"websocket":None,"name":"Joueur{}".format(n+i+1),'token':token})
        elif n>nmax:
            for i in range(n-nmax):
                JOUEURS.pop(-1)
        for j in range(len(JOUEURS)):
            if "Joueur" in JOUEURS[j]['name']:
                JOUEURS[j]['name']="Joueur{}".format(j)
                
    
    else:
        phase = ph.search_phase(partie)
        cartes=""
        if 'cartes' in data:
            cartes = data['cartes']
        commande = data['commande']
        phase.action(commande,cartes)
        result = phase.result()
        
        

def getJson():
    jsons = []
    Joueur = [j['name'] for j in JOUEURS]
    phase = ph.search_phase(partie)
    n = len(JOUEURS)
    for j in range(n):
        dico={}
        dico["names"]=[ j["name"] for j in JOUEURS   ]  
        dico["joueur"]={}
        dico["joueur"]["name"]=JOUEURS[j]["name"]
        dico["joueur"]["token"]=JOUEURS[j]["token"]
        if result:
            resultat=result.format(Joueur=Joueur)
        else:
            resultat=""
        if phase.message():
            message = phase.message().format(Joueur=Joueur)
        else:
            message=""
        
        dico["infos_phase"]={"result":resultat,"message":message}
        dico["tapis"] = {}
        dico["tapis"]["cartes"]=[c.abr if c else "" for c in phase.cartes_visibles() ]
        if "Jouer" in str(phase):
            dico["tapis"]["info_pli"]=[""]*n
            dico["tapis"]["info_prise"]=[""]*n

            dico["tapis"]["info_pli"][partie.seconde]="suivant"
            dico["tapis"]["info_pli"][partie.minute]="entame"
            
            
            if partie.variante==ta.Tarot.APPEL_AU_ROI:
                index = partie.who_has_played(partie.roi_appele)
                if index:
                    dico["tapis"]["info_prise"][index]="appele" 
            _,index_preneur=partie.get_contrat()
            dico["tapis"]["info_prise"][index_preneur]="preneur"        
            if partie.variante==ta.Tarot.MORT:
                dico["tapis"]["info_prise"][partie.heure]="mort"        

        main_triee = partie.mains[j].copy()
        if len(main_triee)>0:
                main_triee = sorted(main_triee,key = lambda x:x.valeur,reverse=True )
                main_triee = sorted(main_triee,key = lambda x:x.famille )
                familles = ["pique","carreau","trefle","coeur","atout"] 
                abrs = [ [carte.abr  for carte in main_triee if f in carte.famille] for f in familles]
                dico["main"]=abrs
        
        dico['selection'] ='unique'
        if phase:
             if 'Ecarter' in str(phase):
                 dico['selection']='multiple'

        
        if j in phase.choix():
            dico["choix"]=phase.choix()[j]
        jsons.append(json.dumps(dico,indent=3))
    return jsons   

    
async def notify_players():
     """
     Sends the message to the players
     """
  
    
    
     messages = []
     if not active :
         n_conn=0
         connexions = [] #JOUEURS.copy()
         for j in JOUEURS:
             c={}
             c['name']=j['name']
             c['token'] =j['token']
             if j['websocket']:
                    c['state']='OK'
                    n_conn=n_conn+1
             else :
                    c['state']='déconnecté'
             connexions.append(c)       
                #del c['websocket']
            
         message = "<pre> Voici les joueurs : \n"
         message = message+tab.tabulate(connexions,headers='keys',tablefmt="grid")
         if n_conn< partie.number_of_players:
             message = message+"\n Merci de communiquer aux autre joueurs leur token </pre>"
         else:
# changer la variante (3,4 ou 5 joueurs)
             message = message+"</pre><button type='button'   id='commencer' >commencer ou recommencer</button>"         
         message = message+"""
<div class='row'>
<div class='col-lg-12'>
<form>
<input type="radio"  id="trois" name="variante" value="0">
<label for="trois">trois</label><br>
<input type="radio"  id="quatre" name="variante" value="1">
<label for="quatre">quatre</label><br>
<input type="radio"  id='appel' name="variante" value="2">
<label for="appel">cinq (avec appel)</label><br> 
<input type="radio" id='mort'  name="variante" value="3">
<label for="mort">cinq (avec un mort)</label> <br> 
<button type='button' id='select_variante'>changer le jeu</button>
</form>
</div>
</div>
"""           
         mesjson = [json.dumps({"modalContent":message})]
         
         for j in range(1,partie.number_of_players):
             message=("<pre>Partie en attente ...</pre>")
             mesjson.append(json.dumps({"modalContent":message}))    
         
     #########################
     ###### la partie est active 
     ##############################      
     else:
              # next version, message will only be a table of json
              mesjson = getJson()
     for j in range(len(JOUEURS)):
             websocket = JOUEURS[j]["websocket"]
             if websocket:
                 await websocket.send(mesjson[j]) 



async def register(websocket,token):
    tokens = [j['token'] for j in JOUEURS]
    try:
        index = tokens.index(token)
        # the player has the right to play
        # correct token and noone else playing
        if JOUEURS[index]['websocket']==None:
            JOUEURS[index]['websocket'] =websocket

            await notify_players()
    finally :
        return


async def unregister(websocket):
    sockets = [j['websocket'] for j in JOUEURS ]
    global active
    try:
        index = sockets.index(websocket)
        JOUEURS[index]['websocket']=None
        active=False
        await notify_players()
    finally:
        return 


async def launch(websocket, path):
    try:
        async for message in websocket:
            data = json.loads(message)
            if data["commande"]=="SEND_TOKEN":
                token = data["entry"]
                await register(websocket,token)
            elif data["commande"]=="RENAME":
                token = data["token"]
                tokens = [j['token'] for j in JOUEURS]
                try:
                    index = tokens.index(token)
                    JOUEURS[index]['name']=data['entry']
                finally:
                    pass            
            else :
                fire_action(data)
            await notify_players()
            sockets = [j["websocket"] for j in JOUEURS]
            if not websocket in sockets:
                phase = ph.search_phase(partie)
                await websocket.send(getJson()[phase.prompt()])                         

    finally:
        await unregister(websocket)



create_joueurs(partie.number_of_players)
JOUEURS[0]['token']='P3t1tauBout'

start_server = websockets.serve(launch,None,6789)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
