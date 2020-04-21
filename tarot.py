# -*- coding: utf-8 -*-
"""
Created on Fri Apr  3 16:11:55 2020

@author: MartinMoritz
"""
import numpy as np
import csv 



PRET=0
DISTRIBUE=1
PRISE = 2
AFFICHAGE_CHIEN=3
ECART = 4
PASSE = 5
PLI_EN_COURS = 6
PLI_FINI = 7
PARTIE_FINIE=8
AFFICHAGE_SCORE = 9
PARTIE_TERMINEE=10
CARTES_RASSEMBLEES = 11


ENCHERE_NORMAL = 100    
ENCHERE_PASSE = 101
ENCHERE_SANS = 102
ENCHERE_CONTRE = 103



MESSAGE={
     PRET : ["Le jeu est prêt pour la distribution.",""],
     DISTRIBUE : ["{} a distribué le jeu. Prenez connaissance de vos cartes.",""],
     PRISE : ["Qui prend ? [-1/0/1/2/...]","{} a pris.",""],
     AFFICHAGE_CHIEN : ["Voici le chien:",""],
     ECART : ["{} doit faire son écart",""],
     PASSE : ["Tout le monde a passé.",""],
     PLI_EN_COURS : ["{} : ","",],
     PLI_FINI  : ["{} a emporté le pli.","L'excuse revient à {} en ećhange d'une carte."],
     PARTIE_FINIE : ["La partie est finie. Voici l'écart de {} :",""],
     AFFICHAGE_SCORE : ["{} a pris","Il a fait {:.0f} points."],
     PARTIE_TERMINEE : ["La partie est terminée. Recommencer ?[O/n] ",""],
     CARTES_RASSEMBLEES : ["Le jeu est prêt. Couper.",""]
    }






class Carte:
    def __init__(self,infos=[]):
        self.famille=infos[0]
        self.nom=infos[1]
        self.valeur=int(infos[2])
        self.points = float(infos[3])
        self.abbr = infos[4]
    
    def __str__(self):
        return self.nom
    def __eq__(self,other):
        if not other : 
            return False
        return self.valeur==other.valeur
    def __lt__(self,other):
        return self.valeur < other.valeur

class Joueur:
    def __init__(self,nom="Joueur"):
        self.nom=nom
        self.main=dict() #les cartes dans la main de ce joueur, 
        # key est l'abbreviation
    def __str__(self):
        return self.nom
    ## retourne les cartes triées par couleur et valeur
    def main_triee(self):
            main = sorted(self.main.values())
            main = sorted(main,key = lambda x:x.famille )
            return([carte for carte in main ] ) 

    # 
    def joue(self,abbr,famille):
        """
        retourne la carte de ce joueur qui correspond à l'abbréviation
        quand l'abbréviation est courte (1 caractère) envoie la carte de la famille
        si elle existe.
        Il y a le problème de l'écart....
        """
        carte =None
        #if famille :
        #    if famille != 'atout':
        #        if len(abbr)==1 or abbr=='10':
        #            abbr = abbr+famille[0:2]
        #            carte =  self.main.pop(abbr,None)
        #if carte is None :    
        carte =  self.main.pop(abbr,None)
        return carte
        
# un pli correspond à un tour de jeu
# lorque tout le monde a joué, le pli détermine le gagnant        
class Pli:
    """
    Ce sont les cartes jouées sur la table lors d'un pli
    Lorsqu'il y a un mort, cela signifie qu'un des joueursne joue pas (en général c'est le donneur)
    """
    def __init__(self,n,entame_index):
        """
        Args :
            n : le nombre de joueurs
        """
        self.cartes = [None]*n
        self.mort = False
        if n==5 :
            self.mort = True
        self.entame_index = entame_index
    
    
    def ajoute(self,index,carte):
        """
        Args : 
            index : où ajouter la carte
            carte : la Carte à ajouter
        """
        self.cartes[index]=carte
    
    def complet(self):
        """
        Returns :
            True si le tour est complet
            False sinon
        """
        n = sum([1 for carte in self.cartes if carte])
        if self.mort :
            n = n+1
        if n==len(self.cartes) : 
            return True
        return False
    
    # détermine le gagnant de ce pli
    def gagnant(self): 
        n = len(self.cartes) 
        atouts =[0]*n
        for i in range(n):
            carte = self.cartes[i]
            if carte :
                if self.cartes[i].famille=="atout":
                    atouts[i] = self.cartes[i].valeur
                # teste s'il y a des atouts
        atouts = np.array(atouts)
        maxi = np.max(atouts)
        g = np.argmax(atouts)
        if maxi>0 : return g  # l y a au moin un atout qui n'est pasl'excuse
  
        # cas particulier ou l'excuse est jouee en premier
        if self.cartes[self.entame_index].abbr=='e':
            self.entame_index = (self.entame_index+1)%n
            # quand le suivant est le mort
            if not self.cartes[self.entame_index]:
                self.entame_index = (self.entame_index+1)%n
        valeurs=[0]*n
        for i in range(n):
            carte = self.cartes[i]
            if carte :
                if self.cartes[i].famille==self.cartes[self.entame_index].famille:
                    valeurs[i] = self.cartes[i].valeur
        valeurs = np.array(valeurs)
        g = np.argmax(valeurs)
        return g


# c'est une partie de tarot
# le jeu est mélangé au début
# le donneur change à chaque partie
class Partie:
    """
    Properties :
     distributeur : envoie les cartes aux joueurs (par email ?)   
     jeu     : array of Carte, le paquet de carte (plein avant distribution)   
     joueurs : array of Joueurs
     donneur_index : int  indiquant le donneur de la partie en cours
     preneur_index : int indiquant le joueur qui a pris
     joueur_index  : int indiquant le joueur qui met la prochaine carte
     entame_index  : int indiquant le premier joueur pour le tour en cours
     chien   : array of Carte , le chien qui après la distribution
     pli     : array of Carte , les cartes jouées pour le tour en cours
     levee   : array de longueur 2 array[0] est un array de Cartes, les cartes 
               levées par l'attaquant et array[1] par le défenseur
     enchere : NORMAL,PASSE,SANS, CONTRE
     echange : sur la partie en cours, 
               l'excuse revient à l'attaque ou à la défense en échange d'une carte            
    """
    

    
    
    
    def __init__(self,n_joueurs=4,donneur_index=0,distributeur=None,debug=False):
        """
        Débute la partie, crée le jeu, le mélange, initialise le donneur,
        l'entame, le joueur, le chien et les levées
        Args : 
         noms_joueurs : array of string
         donneur   : (int) l'indice du premier donneur
         distributeur : s'occupe d'envoyer les mails pour la distribution
        """   
        self.distributeur = distributeur
        # initialise les joueurs
        self.donneur_index = donneur_index
        self.preneur_index = -1 # pas de preneur
        self.joueur_index = 1
        self.entame_index  = 1
        self.initialise_joueurs(n_joueurs=n_joueurs)
        
        self.jeu= []
        
        # charge le jeu de cartes
    
        self.chien= []
        self.pli = Pli(n=self.nombre(),entame_index=self.entame_index)
        
        self.levee = [[],[]]
        self.enchere = ENCHERE_NORMAL
        self.echange = - 1  # pas d'excuse à échanger
        self.debug=debug
        
        
        
        with open('cartes.csv', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for line in reader:
                carte = Carte(line)
                self.jeu = np.append(self.jeu,carte)
        # melange le jeu
        np.random.shuffle(self.jeu)
        self.jeu = self.jeu.tolist()
        self.etat = PRET
        
        # pour tester si la logique fonctionnne
        #self.jeu =self.jeu[:18] 
        
    def initialise_joueurs(self,n_joueurs=4):
        if self.distributeur:
            self.joueurs = [Joueur(nom=n)  
                        for  n in self.distributeur.noms]
        else :
            noms = ['joueur '+str(i) for i in range(n_joueurs) ]
            self.joueurs = [Joueur(nom=n)  
                        for  n in noms]
        # au cas où le nombre de joueurs a changé depuis la partie précédente
        self.donneur_index = self.donneur_index%self.nombre()
        self.joueur_index = self.index_direction_suivante(self.donneur_index)
        self.entame_index = self.joueur_index
        self.pli = Pli(n=self.nombre(),entame_index=self.entame_index)
        
    
    
    def nombre(self):
        """
        Returns :
            nombre : le nombre de joueurs
        """
        return len(self.joueurs)
    
    def index_direction_suivante(self,index_courant,sens=1):
        """
        Lors d'une partie, donne l'index du porchain joueur. Lors d'une partie à 5, le donneur ne participe pas
        Args :
            index_courant : l'index courant
            sens : vaut 1 par défaut, si c'est -1, alors on obtient l'index du joueur précédent
        Returns:
            index_suivant
        """
        index_courant = (index_courant+sens)%self.nombre()
        # à 5, le donneur ne prend pas part au jeu
        if self.nombre()==5 and index_courant == self.donneur_index:
            
            index_courant = (index_courant+sens)%self.nombre()
        return index_courant   
        
    
    def suivant(self,joueur):
        """
        Returns :
         suivant : le joueur qui suit ce joueur, dans le sens du jeu    
        """
        index = self.joueurs.index(joueur)
        index = (index+1)%self.nombre()
        return self.joueurs[index]
     
    def donneur(self):
        return self.joueurs[self.donneur_index]
    
    def preneur(self):
        """
        Returns :
            le Joueur qui a pris. None si personne ne prend
        """
        if self.preneur_index==-1 : return None
        return self.joueurs[self.preneur_index]
    
    def entame(self):
        return self.joueurs[self.entame_index]
    
    def joueur(self):
        return self.joueurs[self.joueur_index]   
    def gagnant(self):
        """ retourne le gagnant du pli, si le pli est fini"""
        return self.joueurs[self.pli.gagnant()]
    


    def affiche_etat(self):
        """ affiche l'état de la partie
        pour aider le déboguage 
        """
        l1 = len(self.jeu)
        l2 = len(self.chien)
        l3 = sum([ len(j.main.values())  for j in self.joueurs])
        l4 = len(self.levee[0])
        l5 = len(self.levee[1])
        l6 = len([1 for carte in self.pli.cartes if carte is not None])
        print("jeu ",l1,"chien",l2,"mains",l3)
        print('levee attaque ',l4,'levee defense', l5)
        print('pli ',l6)
        print('total',l1+l2+l3+l4+l5+l6 )

    
    def affiche(self,joueur_index=None):
        """
        affiche les cartes des joueurs triées
        Args :
           joueur : int, affiche le jeu d'un seul joueur
        Returns :
            chaine : le jeu de ce joueur
             
        """
        if joueur_index is None:
            joueurs = self.joueurs 
        else : joueurs = [self.joueurs[joueur_index]]    
        familles = ["pique","coeur","carreau","trefle","atout"]  
        chaine = '\n'
        for j in joueurs:
            main = [carte for carte in j.main_triee() ]
            for f in familles:
                noms = [carte.nom for carte in main if carte.famille==f]
                if len(noms)!=0 : chaine = chaine+f+" : \t"+" ".join(noms)+"\n"
        return chaine       
            
    
    def score(self):
        """
        Losque la partie est finie, retourne le score du preneur.
        RETURNS :
            score : 0 si la partie n'est pas finie
        """
        score = 0
        if self.finie():
            return score
        score = sum( [carte.points for carte in self.levee[0] ] )
        return score
    
    
    def finie(self):
        """
        Returns :
            True si la partie est finie
        """
        restes = [ len(j.main)  for j in self.joueurs ]
        restes = sorted(restes)
        if restes == [0]*(self.nombre()-1)+[6] :
            return True
        
        return False
    
    
    def distribuer(self):
        """
        distribue les cartes du jeu aux joueurs et au chien
        à la fin de la distribution, le jeu est vide
        """  
        if self.debug :
            if len(self.jeu) != 78 :
                print("Anomalie",len(self.jeu))
                return None
            
        if self.etat == PRET :
                       
            #distribue le chien
            index_chien = np.arange(21)
            index_chien = np.random.choice(index_chien,6,replace=False)
            index_chien.sort()
            #print(index_chien)
            direction = self.index_direction_suivante(self.donneur_index)
            #direction = (self.donneur_index+1)%self.nombre()
            tour = 0
            while(len(self.jeu)>0):
                 for i in range(3):
                     carte,self.jeu = self.jeu[0],self.jeu[1:]
                     j = self.joueurs[direction]
                     main = j.main
                     try :
                         main[carte.abbr] = carte
                     except AttributeError:
                         print("#########################",carte)
                 if len(index_chien>0) :
                     if tour == index_chien[0]:
                         carte,self.jeu = self.jeu[0],self.jeu[1:]
                         self.chien.append(carte)
                         index_chien = index_chien[1:]
                 tour = tour +1     
                 
                 direction = self.index_direction_suivante(direction)
                 #direction = (direction+1)%self.nombre()
        return True  # tout se passe bien        
                  
                 

    def prise(self,index=-1):
        """
        le preneur prend les cartes du chien dans son jeu
        Args :
         preneur : int, indice du preneur    
        Returns :
          chien : Array of cartes  
        """    
        #index = self.joueurs.index(preneur)
        if self.etat==PRISE :
            self.etat = AFFICHAGE_CHIEN 
            
            self.preneur_index = index
            
            if index != -1 :  # quelqun a pris
                self.enchere = ENCHERE_NORMAL
            else : self.enchere = ENCHERE_PASSE     # partie passée
            
            return index,self.chien
    
    
    def ecarter(self):
            """
            Le joueur qui a pris doit faire son écart. 
            Ici, les cartes du chien sont ajoutés
            à son jeu
            """
            if self.etat==ECART :
                for carte in self.chien:
                     self.joueurs[self.preneur_index].main[carte.abbr]=carte
                     self.chien=[]
     
                
                
    def annuler_coup(self):
        """
        Lorsqu'un pli est en cours, cela annule la dernière carte jouée
        """
        self.joueur_index = self.index_direction_suivante(self.joueur_index,sens=-1)
        #self.joueur_index = (self.joueur_index-1)%self.nombre()  
        carte = self.pli.cartes[self.joueur_index]
        self.joueur().main[carte.abbr]=carte
        self.pli.cartes[self.joueur_index]=None
        return  self.pli.cartes,False



        
        
            
    def jouer(self,abbr):
         """
         La carte jouée par le prochain joueur est ajoutée au pli
         Args :
           abbr : String désignant l'abbréviation de la carte jouée
         Returns :
           cartes : array of Carte, le pli si le tour est terminé, 
                 dans ce cas, le pli est aussi ajouté à la levée de 
            l'attaque ou de la défense
           True : le pli est terminé
               
         """
         
         if self.etat == PLI_EN_COURS : 
             joueur = self.joueur()
             if self.debug :
                 try :
                     abbr = list(joueur.main.values())[0].abbr         
                 except IndexError:
                     print('IndexError')
             famille = None        
             if self.joueur_index != self.entame_index:
                famille = self.pli.cartes[self.entame_index].famille
                
             carte = joueur.joue(abbr,famille)
             cartes = self.pli.cartes
             # la carte jouée n'existe pas
             if carte is None : 
                 return [],False
     
             self.pli.ajoute(self.joueur_index,carte)
             self.joueur_index = self.index_direction_suivante(self.joueur_index)
             #self.joueur_index = (self.joueur_index+1)%self.nombre()  
             return cartes,self.pli.complet()
    
    def emporter_pli(self):
            """
            Lorsque le pli est complet, détermine le gagnant et met les 
            cartes dans sa levée
            Returns : 
                echange
                    -1 : pas d'excuse à échanger dans le pli
                    0  : l'excuse revient à l'attaque en échange d'une carte
                    1  : l'excuse revient à la défense en échange d'une carte
            """
            gagnant_index = self.pli.gagnant()
            
            excuse_trouvee = False
            excuse_echangee = False
            # l'echange d'excuse n'arrive qu'une fois par partie
            
            if self.echange == -1 :
                # l'excuse est dans le pli
                for i,carte in enumerate(self.pli.cartes) :
                    if not carte:
                        continue 
                    if carte.abbr == 'e':
                        excuse_trouvee = True
                        excuse = carte
                        break
                if excuse_trouvee :    
                    # le preneur a gagné le pli, l'excuse est à la défense
                    if self.gagnant() == self.preneur() :
                        # l'excuse revient à la défense en échange d'une carte
                        self.echange = 1 
                        self.pli.cartes.remove(excuse)
                        excuse_echangee = True
                    # le preneur a joué l'excuse 
                    if i == self.preneur_index :
                        # l'excuse revient à l'attaque en échange d'une carte
                        self.echange = 0
                        self.pli.cartes.remove(excuse)
                        excuse_echangee = True
                
                    

            self.entame_index  = gagnant_index
            #self.entame_index = (gagnant_index)%self.nombre()
            self.joueur_index = self.entame_index 
             # ajouter les cartes aux levees de l'attaque ou de la défense
            if gagnant_index == self.preneur_index:
                self.levee[0]= self.levee[0]+[carte for carte in self.pli.cartes if carte]
            else :
                 self.levee[1]=self.levee[1]+[carte for carte in self.pli.cartes if carte]
            if excuse_echangee : 
                self.levee[self.echange] = self.levee[self.echange]+[excuse]
             # initialise le pli
            self.pli = Pli(self.nombre(),self.entame_index)
            #self.pli.entame_index = self.entame_index
            
            return excuse_echangee

                

    def peigne(self,cartes):
        binaire = [carte.points != 0.5 for carte in cartes]
        print(binaire)
        
        debut,milieu,fin = cartes[:0],cartes[0:2],cartes[2:]
        d,m,f = binaire[:0],binaire[0:2],binaire[2:]
        
        ok = True
        i = 0
        while True:
            i = i+1
            if i==100 :
                break
            if sum(m)==2 :
                mini,index = np.amin(f),np.argmin(f)
                if mini == 1 :
                    ok=False
                    break
                milieu[0],fin[index] = fin[index],milieu[0]
                m[0],f[index] = f[index],m[0]
                if len(fin)<=2 :
                    break
            debut = np.hstack((debut,milieu))
            d = np.hstack((d,m))
            milieu = fin[:2]   
            m = f[:2]
            fin = fin[2:]
            f = f[2:]
        cartes = np.hstack((debut,milieu,fin))
        return cartes.tolist(),ok
                
                
            
        

    def compter(self):
        """
        Place les cartes de l'écart dans la levée et peigne les cartes de la levee 
        pour éviter que deux cartes à points se suivent
        """
        if self.etat==AFFICHAGE_SCORE:
            # carte en echange de l'excuse
            
            if self.echange != -1 :
                for carte in self.levee[self.echange]:
                    if carte.points == 0.5:
                        break
                print("carte echangee :",carte.abbr)    
                self.levee[self.echange].remove(carte)
                self.levee[(self.echange+1)%2].append(carte)
            
            # ajoute l'écart à la levée de l'attaquant
            self.levee[0] = list(self.preneur().main.values())+self.levee[0] 
            self.preneur().main = {}
            self.levee[0],ok = self.peigne(self.levee[0])
            # s'il reste un paquet de cartes à points sur la fin
            if not ok :
                self.levee[0] = np.flip(self.levee[0])
                self.levee[0],_ = self.peigne(self.levee[0])
                self.levee[0] = np.flip(self.levee[0])
            
            
        
    def rejouer(self):
         """
         Les joueurs ont accepté de rejouer une partie
         """
         self.echange = -1  # pour l'echange de l'excuse

         # pour une partie interrompue, il faut remettre les cartes du pli dans le jeu
         self.jeu =  [ carte for carte in self.pli.cartes if carte ]
         # remet les levées dans les tas de cartes         
         self.jeu = self.jeu +self.levee[0]+self.levee[1]
         self.levee[0]=[]
         self.levee[1]=[]
         # ajoute les cartes qui restent dans les mains
         for j in self.joueurs:
            liste = list(j.main.values())
            self.jeu = self.jeu+liste
            j.main = {} # plus de cartes dans les mains
         #ajoute le chien
        
         self.jeu = self.jeu+self.chien
         self.chien = []
         self.donneur_index = (self.donneur_index+1)%self.nombre()
         self.pli = Pli(self.nombre(),(self.donneur_index+1)%self.nombre())

         
         

        
    def couper(self,int=-1):
        """
        reconstitue le jeu à partir des jeux des joueurs si personne
        n'a pris, ou à partir des levées si la partie s'est jouée
        puis coupe le jeu
        """
        if self.etat==CARTES_RASSEMBLEES:
            coupe = np.random.binomial(78,0.5)
            self.jeu = self.jeu[:coupe]+self.jeu[coupe:]



    def get_message(self):
        """
        retourne le message correspondant à l'etat du jeu
        """
        message = MESSAGE[self.etat][0]
        if self.etat == PRET :
            pass
        elif self.etat == DISTRIBUE :
            message = message.format(str(self.donneur()))
            # affiche toutes les cartes des joueurs

        elif self.etat == ECART :
            self.ecarter()
            message = message.format(self.preneur())
        elif self.etat == PLI_EN_COURS :
            # affiche les cartes du joueurs
            if self.debug:
                print(self.affiche(joueur_index = self.joueur_index))
            message = message.format(self.joueur())
        elif self.etat == PLI_FINI :
            gagnant = self.gagnant()
            message = message.format(gagnant)
        elif self.etat == PARTIE_FINIE :
            message = message.format(self.preneur())
            
        elif self.etat == AFFICHAGE_SCORE :
            self.compter()
            message = message.format(self.preneur())

        return(message)     

    def action(self,entry_input):
        """
        recupère input si nécessaire et change l'état vers une autre action
        Return :
            message : le message de cette action
            cartes  : un tableau ['1','3','2tr'] contenant les abbréviations des cartes
        """
        message = MESSAGE[self.etat][1]
        cartes = []
        if entry_input == 'FIN':
            self.etat = PARTIE_TERMINEE
        elif self.etat == PRET:
            if self.distribuer() :
                self.etat = DISTRIBUE
        elif self.etat == DISTRIBUE :
            # les jeux ne sont pas envoyés par email
            if not self.distributeur:
                print(self.affiche()) 
            # les jeux sont distribués par le distributeur
            else :
                self.distributeur.send(self)    

            self.etat = PRISE
        elif self.etat == PRISE :
            if self.prise(int(entry_input)):
                    message = message.format(self.preneur())
        elif self.etat == AFFICHAGE_CHIEN:
            cartes = [carte.abbr for carte in self.chien]
            if self.enchere == ENCHERE_PASSE:
                self.etat = PASSE
            else : self.etat = ECART
        elif self.etat == ECART:
            self.etat = PLI_EN_COURS
        elif self.etat == PLI_EN_COURS :
            if entry_input == 'VOIR':
                message =self.affiche(joueur_index = self.joueur_index)
            if entry_input=='A':
                cartes,_ = self.annuler_coup()
                cartes = [(carte.abbr if carte  else "_") for carte in cartes]
                self.etat = PLI_EN_COURS
                message = "Le coup est annulé."
            else :
                cartes,complet = self.jouer(entry_input)
                if cartes :
                    cartes = [(carte.abbr if carte  else "_") for carte in cartes]
                    if complet :
                        self.etat = PLI_FINI
        elif self.etat == PLI_FINI:
            if entry_input=='A':
                cartes,_ = self.annuler_coup()
                cartes = [(carte.abbr if carte  else "_") for carte in cartes]
                self.etat = PLI_EN_COURS
                message = "Le coup est annulé."
            else :
                echange_excuse = self.emporter_pli()
                if echange_excuse  :
                    if self.echange == 0 :
                        message = message.format("l'attaque")
                    elif self.echange == 1 :    
                        message = message.format("la défense")
                else :
                    message = ''
                
                if self.finie():
                    self.etat = PARTIE_FINIE
                else :
                    self.etat = PLI_EN_COURS
                    cartes = []
                    

        elif self.etat == PASSE:
            self.etat = PARTIE_TERMINEE
        elif self.etat == PARTIE_FINIE:
            ecart = list(self.preneur().main.values())
            cartes = [carte.abbr for carte in ecart]
            self.etat = AFFICHAGE_SCORE
        elif self.etat == AFFICHAGE_SCORE :
            cartes = [carte.abbr for carte in self.levee[0]]
            message = message.format(self.score())
            self.etat = PARTIE_TERMINEE
        elif self.etat == PARTIE_TERMINEE:
            if entry_input =='n' :
                return "FIN",[]
            else : 
                self.rejouer()
                self.etat = CARTES_RASSEMBLEES
        elif self.etat == CARTES_RASSEMBLEES:
            if self.debug:
                self.initialise_joueurs(n_joueurs = np.random.randint(3,5) )
            self.couper()
            self.etat = PRET               
           
        
        return message,cartes




if __name__ == "__main__":
    score = 0
    donneur = int(input("Premier donneur : "))
    partie = Partie(donneur_index=donneur,n_joueurs=5,debug=True)
    
    while True:
        

        message = partie.get_message() 
        reponse = input(message)
        message,cartes  = partie.action(reponse)
        if partie.debug : 
            partie.affiche_etat()
        print(message)
        if len(cartes)>0 : print(cartes)
        if message =='FIN' : break
 

    
 

    
    
   