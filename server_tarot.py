import socket
import selectors
import types
from tarot import Tarot
import phase as ph
import numpy as np
from xml.dom.minidom import parseString
import time
# import logging

#import xml.dom.minidom as dom 

# https://openclassrooms.com/fr/courses/235344-apprenez-a-programmer-en-python/234698-gerez-les-reseaux




def cards_as_string(cartes,triees=False):
        """
        affiche les abbréviations des cartes, éventuellement triées 
        Args :
           cartes : np.array or list of cards
           triees : if the cards are sorted
        Returns :
            chaine : the abreviations, coma separated (rtr,2tr,2,5), None is replaced by '_'
             
        """
        cartes = np.copy(cartes)
        if triees:
            valeurs = np.array([carte.valeur for carte in cartes ])
            cartes = cartes[np.argsort(valeurs)]
            familles = np.array([carte.famille for carte in cartes ])
            cartes = cartes[np.argsort(familles,kind='stable')]
        abrs = np.array( [carte.abr if carte else '_' for carte in cartes ] )
        return ",".join(abrs)       





class Server():
    def __init__(self,partie,port=12850,test=False):
        self.host = ''
        self.port = port
        #self.number_of_players=number_of_players
        # selectors manages the connections
        self.selector = selectors.DefaultSelector()
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        
        if test:
            self.connexions_clients = [None]
            noms_test=['Martin','Pierre','Georges','Thomas','Jean']
            self.noms = [noms_test[i] for i in range(partie.number_of_players)]
        else :
            self.noms=[self.nommer(i,"") for i in range(partie.number_of_players)] #["Joueur{}".format(i) for i in range(partie.number_of_players) ] # le nom des joueurs
        self.partie = partie  # the partie of tarot
        self.phase = None     # phase of the game
        self.result = None    # the result of the preceeding phase

        self.test = test # true, server runs to test : only one client 
        self.free_connections = list(range(partie.number_of_players)) # index of free connexions new players can get 
        

    def start(self):
        
        self.lsock.bind((self.host, self.port))
        self.lsock.listen()
        print("listening on", (self.host, self.port))
        self.lsock.setblocking(False)
        self.selector.register(self.lsock, selectors.EVENT_READ, data=None)

    




    def accept_wrapper(self,sock):
        conn, addr = sock.accept()  # Should be ready to read
        index = self.free_connections.pop(0)
        print("accepted connection from", addr,"this is Joueur",index)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr,index =index,inb="")
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.selector.register(conn, events, data=data)
    
    
    
    
    def service_connection(self,key, mask,commands,infos):
        """
        

        Parameters
        ----------
        key : TYPE
            DESCRIPTION.
        mask : TYPE
            DESCRIPTION.
        commands : TYPE
            DESCRIPTION.
        infos : TYPE
            DESCRIPTION.

        """
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                data.inb += recv_data.decode()
                if len(data.inb)>4 and data.inb[-4:]=="#EOM":
                    print("{} bytes received from Joueur{}.".format(len(data.inb),data.index))
                    command = data.inb[:-4]
                    data.inb=""
                    # adds the command to the pile
                    commands.append((command,data.index))
            else:
                print("closing connection to Joueur{}".format(data.index))
                self.free_connections.append(data.index)
                self.selector.unregister(sock)
                sock.close()
        if mask & selectors.EVENT_WRITE:
            # print("server is trying to write(124)")
            # print(infos[data.index],data.index)
            if infos[data.index] != b"" :
                sent = sock.send(infos[data.index])  # Should be ready to write
                print("sending {} bytes to Joueur{}.".format(sent,data.index))

                infos[data.index] = infos[data.index][sent:]
    

    def nommer(self,index,nom):
        """
        Name or rename one of the player. The name cannot be blank

        Parameters
        ----------
        index : Integer
        nom : String
        Returns
        -------
        The name of the player (eventualy Joueur#index).

        """
        if nom!="":
            return(nom)
        else :
            return "Joueur{}".format(index)
    
    
    def close(self):
        print("Fermeture des connexions")
        conn_clients = [conn for conn in self.connexions_clients if not conn is None]
        for client in conn_clients:
             client.close()

        self.connexion_principale.close()
 

    def getInfos(self):
        test = self.test 
        
        n_joueurs_attendus = len(self.free_connections)        
        number_of_players = self.partie.number_of_players
        


        if (n_joueurs_attendus>0) and not test:
            infos = [("<infos joueur='{}'> <message>En attente de tous les joueurs</message> </infos>#EOM".format(i)).encode() for i in range(number_of_players)]
            return infos
    
        dom = self.getXML()    
        infos = [None]*number_of_players
        for element in dom.getElementsByTagName("infos"):
            if not test :
                i =  int(element.getAttribute("joueur"))
            else :
                i = 0
            infos[i] = (element.toprettyxml()+"#EOM").encode()
    
        return infos    


    
    
    def getXML(self):
        """
        Builds the XML message that server sends to clients.
        Parameters
        ----------    
        Returns
        -------
        dom : Domdocument
            XML-DOM that can be sent to the client.
    
        """
        partie = self.partie
        phase = self.phase 
        noms = self.noms 
        result = self.result
        test = self.test 

        
        dom = parseString("<root/>")
        root = dom.getElementsByTagName("root")[0]
    
        
        """ PHASE DE TEST 1 SEUL CLIENT """
        if test :
            irange = [0]
        else: irange = range(partie.number_of_players)    
        
        for i in irange:
            joueur = dom.createElement("infos")
            
            if test: 
                joueur.setAttribute("joueur",str(phase.prompt()))
            else:
                 joueur.setAttribute("joueur",str(i))   
            root.appendChild(joueur)
        
            les_noms = dom.createElement("noms")
            for index,name in enumerate(noms):
                j = dom.createElement("joueur")
                j.setAttribute("index",str(index))
                j.appendChild(dom.createTextNode(name))
                les_noms.appendChild(j)
            joueur.appendChild(les_noms)    
            
            # choices are added only to the prompted player
            if True :
                boolean = True
                if not test:
                    boolean = phase.prompt() == i
                if  boolean:
                    choices = dom.createElement("choices")
                    for c,t in phase.choix():  #command and text
                        choix = dom.createElement("choix")
                        choix.setAttribute("commande",c)
                        choix.appendChild(dom.createTextNode(t))
                        choices.appendChild(choix)
                    joueur.appendChild(choices)
            
            
             
            if test:
                boolean =  len(partie.mains[phase.prompt()]) != 0
            else :
                boolean =  len(partie.mains[i]) != 0 
            if boolean :
                child = dom.createElement("cartes")
                child.setAttribute("place","main")
                if test:
                    child.appendChild(dom.createTextNode(cards_as_string(partie.mains[phase.prompt()],triees=True)))
                else :
                    child.appendChild(dom.createTextNode(cards_as_string(partie.mains[i],triees=True)))
                joueur.appendChild(child)
            
            
            
            
            m = phase.message() 
            if  m:
                child = dom.createElement("message")
                child.appendChild(dom.createTextNode(m))
                joueur.appendChild(child)
            if result :
                child = dom.createElement("result")
                child.appendChild(dom.createTextNode(result))
                joueur.appendChild(child)
    
                
                
            if "Ecarter" in str(phase):
                contrat,_ = partie.get_contrat() 
    
                if contrat <= Tarot.GARDE  :
                    if partie.variante != Tarot.APPEL_AU_ROI or partie.roi_appele !='' or contrat==Tarot.PASSE:
                        if len(partie.chien) != 0 :
                            child = dom.createElement("cartes")
                            child.setAttribute("place","chien")
                            child.appendChild(dom.createTextNode(cards_as_string(partie.chien)))
                            joueur.appendChild(child)
    
            if "Jouer" in str(phase):
                child = dom.createElement("cartes")
                child.setAttribute("place","pli")
                child.appendChild(dom.createTextNode(cards_as_string(partie.pli)))
                joueur.appendChild(child)
                
                # adds who is playing and who has played first in the turn
                child = dom.createElement("index_entame")
                child.appendChild(dom.createTextNode(str(partie.minute)))
                joueur.appendChild(child)
                
                child = dom.createElement("index_joueur")
                child.appendChild(dom.createTextNode(str(partie.seconde)))
                joueur.appendChild(child)
                
                c,p = partie.get_contrat()
                child = dom.createElement("index_preneur")
                child.appendChild(dom.createTextNode(str(p)))
                joueur.appendChild(child)
                
                # adds the symbol for the second attaquant in this variante
                if partie.variante == Tarot.APPEL_AU_ROI:
                    roi_appele =  partie.who_has_played(partie.roi_appele)
                    # only if the one who has played the roi_appele is not the preneur
                    if roi_appele:
                        index,_ = roi_appele
                        if index and index != p:
                            child = dom.createElement("index_attaquant")
                            child.appendChild(dom.createTextNode(str(index)))
                            joueur.appendChild(child)

                        
                if partie.variante == Tarot.MORT:
                    child = dom.createElement("index_mort")
                    child.appendChild(dom.createTextNode(str(partie.heure)))
                    joueur.appendChild(child)
            
                    
    
                
                
                
            if "Conclure" in str(phase):
                if phase.state==0:
                    child = dom.createElement("cartes")
                    child.setAttribute("place","ecart")
                    child.appendChild(dom.createTextNode(cards_as_string(partie.ecart)))
                    joueur.appendChild(child)
    
    
                elif phase.state==1:
                    child = dom.createElement("cartes")
                    child.setAttribute("place","levee")
                    child.appendChild(dom.createTextNode(cards_as_string(phase.levee_attaque)))
                    joueur.appendChild(child)
    
                
        return dom





          
def serve(partie,test=False,port=12800): 

    server=Server(partie=partie,test=test,port=port)
    server.phase = ph.search_phase(partie)
    # names of the players index:name
    server.start()
    # all the infos about the phase
    
    infos=server.getInfos() # infos about the partie it is an array of size number_of_players
    commands = []            # commands sent by the clients (string command,int index)

    
    while True :
        if not server.selector.get_map():
            break 

        events = server.selector.select(timeout=1)
        time.sleep(0.2)
        
        for key, mask in events:

            if key.data is None and len(server.free_connections)>0:
                server.accept_wrapper(key.fileobj)
                infos= server.getInfos()  
                
            else:
                server.service_connection(key, mask,commands,infos)
                if len(commands)>0 : 
                    command,index = commands.pop(0) 
                    if "NOMMER" in command  :
                        i = command.find(" ")
                        _,nom = command[:i],command[i+1:]  
                        server.noms[index] = server.nommer(index,nom)
                    elif command == "FIN":
                        server.selector.close()
                        break 
                    else :
                      i = command.find(" ")
                      if i==-1 :
                          command,cartes = command,""
                      else: 
                          command,cartes = command[:i],command[i+1:]    
                      # if commande in ["QUITTER",""]:
                      #     return "INCOMPLET"
                      server.phase.action(command,cartes)
                      
                      serve.result = server.phase.result()
                      phase2 = ph.search_phase(server.partie)
                      if type(phase2) != type(server.phase):
                          server.phase = phase2
                      infos= server.getInfos()   
    print("BYE BYE (SERVER)")
 


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)

    partie = Tarot(3,Tarot.SANS)
    serve(partie,test=False,port=12853)
    
    print("BYE BYE (SERVER)")

     
