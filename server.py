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
#    print(data)

    if data["commande"]=="COMMENCER":
        active=True
    elif data["commande"]=="PAUSE":
        active=False
    elif data["commande"]=="VARIANTE":
        variante = int(data["variante"])
        partie.ramasser()
        partie.commencer(variante)
        for j in (JOUEURS):
            if not j['websocket']:
                JOUEURS.remove(j)
        nmax=partie.number_of_players
        print("njoueurs:",nmax)
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
        
        
        

    
async def notify_players():
     """
     Sends the message to the players
     """
     messages = []
     phase=None
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
             message = message+"</pre><button type='button' class='command'   data-commande='COMMENCER' >commencer ou recommencer</button>"         
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
<button type='button' class='command'   data-commande='VARIANTE' >changer le jeu</button>
</form>
</div>
</div>
"""           
         messages.append(message)
         
         for j in range(1,partie.number_of_players):
             messages.append("<pre>Partie en attente ...</pre>")
         
     #########################
     ###### la partie est active 
     ##############################      
     else:
        tapis=""	 
        phase = ph.search_phase(partie)
        Joueur = [j['name'] for j in JOUEURS]
        
        # message to introduce what is to do next (if needed)
        
        tapis="<div class='table-responsive'><table class='mx-auto'>" 
        info_prise="<tr>"
        info_pli="<tr>"
        if 'Jouer' in str(phase):

            for index  in range(len(JOUEURS)):
                _,index_preneur = partie.get_contrat()
                if index == partie.minute:
                    info_pli = info_pli+"<td class='entame'>"
                else:
                    info_pli = info_pli+"<td>"
                if index == partie.seconde:
                    info_pli = info_pli+"<img width='20px' src='cartes/chevron2.png'>"
                info_pli = info_pli+"</td>"
                
                if index == index_preneur:
                    info_prise = info_prise+"<td class='preneur'/>"
                elif partie.variante==ta.Tarot.MORT and index==partie.heure:
                    info_prise = info_prise+"<td class='mort'/>"
                elif partie.variante==ta.Tarot.APPEL_AU_ROI and partie.who_has_played(partie.roi_appele) and index==partie.who_has_played(partie.roi_appele)[0]:
                            info_prise = info_prise+"<td class='roi_appele'/>"
                else:
                    info_prise = info_prise+"<td/>"
            info_prise=info_prise+"</tr>"
            info_pli=info_pli+"</tr>"
                    
                    
        
        if len(phase.cartes_visibles())>0:
            if phase.cartes_visibles()==partie.pli:
                # add a row with the name of the players
                noms = "".join(["<td>{}</td>".format(j['name']) for j in JOUEURS])
                tapis = tapis+info_prise+'<tr>'+noms+'</tr>'
                
            for c in  phase.cartes_visibles():
                abr=""
                if c:
                    abr=c.abr
                if c:
                    tapis=tapis+"<td> <img class='carte' src='cartes/{}.png'/>".format(abr)
                else :
                    tapis=tapis+"<td> <img class='carte' src='cartes/dos.png'/>"
        tapis=tapis+info_pli+"</table></div>" 
            
        mess = """
        <div> 
            <div class='row'>
            <div class='form-inline'>
            <div class="form-group">
                <label for="name">Nom</label> 
                <input  id='name' value='{name}'  data-token='{token}'  class='entry form-control'></input>
                <button type='button' class='command btn btn-info'  data-commande='RENAME'>renommer</button> 
            </div>
            </div>
            </div>
        </div>
        <div class='row vert_tapis'>
            <div class='col-lg-12'>
                <div  class="alert alert-primary" id='message'><pre>{result} \n {message} </pre> </div> 
                <div  id='tapis'> {tapis} </div> 
            </div>    
        </div>
        
        <div class='row border'>
        <div class='col-lg-3' id='choix'> {choix} </div> 
        
        <div class='col-lg-9' id='main'> {main} </div> 
        </div>
        """
        for j in range(partie.number_of_players): 
            main =""
            main_triee = partie.mains[j].copy()
            if len(main_triee)>0:
                main_triee = sorted(main_triee,key = lambda x:x.valeur,reverse=True )
                main_triee = sorted(main_triee,key = lambda x:x.famille )
                familles = ["pique","carreau","trefle","coeur","atout"] 
                for f in familles:
                    abrs = ["<img class='carte main' data-abr='{}' src='cartes/{}.png'/>".format(carte.abr,carte.abr) 
                          for carte in main_triee if f in carte.famille]
                    if len(abrs)!=0 : main = main+"<div class='table-responsive'><table> <tr> <td>"+"<td>".join(abrs)+"</tr> </table></div>"
                    
            
            choix=""
            try:
                choix = phase.choix()[j]
                choix="\n".join(["<button class='btn btn-primary btn-block command' type='button'  data-commande={}>{}</button>".format(e,c) for e,c in choix])
            except:
                pass
            
            finally:
                res=""
                if result : 
                    res=result
                message_phase = ""
                if phase.message():
                    message_phase = phase.message()
                messa=mess.format(name=JOUEURS[j]['name'],result=res,message=message_phase,
                                  token=JOUEURS[j]['token']
                                  ,tapis=tapis,choix=choix,main=main)
                messa= messa.format(Joueur=Joueur)
                messages.append(messa)   
     if active: 
         messages[0]=messages[0]+"<div class='row clearfix'><button type='button' class='command btn btn-warning float-right' data-commande='PAUSE'>Mettre le jeu en pause</button></div>"          
     selection='unique'
     if phase:
         if 'Ecarter' in str(phase):
             selection='multiple'
     for j in range(len(JOUEURS)):
             websocket = JOUEURS[j]["websocket"]
             mesjson = json.dumps({"htmlcontent":messages[j],'selection':selection})
             if websocket:
                 await websocket.send(mesjson) 
        
        
async def ask_token(websocket):
    message = """
<div class="form-inline">
  token : <input  class="entry" />
  <button type="button" class="command"   data-commande="token" >OK</button>   
</div>     
"""     
    mesjson = json.dumps({"htmlcontent":message})
    await websocket.send(mesjson) 



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
    connectes = [JOUEURS[i]['websocket'] for i in range(partie.number_of_players) if JOUEURS[i]['websocket']]
    if len(connectes)<partie.number_of_players:
            await ask_token(websocket)       
    try:
        #await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            if data["commande"]=="token":
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
                                    

    finally:
        await unregister(websocket)



create_joueurs(partie.number_of_players)
JOUEURS[0]['token']='P3t1tauBout'

start_server = websockets.serve(launch,None,6789)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
