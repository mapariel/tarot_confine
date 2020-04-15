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
     PRISE : ["Qui prend ?","{} a pris.",""],
     AFFICHAGE_CHIEN : ["Voici le chien:",""],
     ECART : ["{} doit faire son écart",""],
     PASSE : ["Tout le monde a passé.",""],
     PLI_EN_COURS : ["{} : ","",],
     PLI_FINI  : ["{} a emporté le pli.","L'excuse revient à {} en ećhange d'une carte."],
     PARTIE_FINIE : ["La partie est finie. Voici l'écart de {} :",""],
     AFFICHAGE_SCORE : ["{} a marqué {:.1f} points.",""],
     PARTIE_TERMINEE : ["La partie est terminée. Recommencer ?(O/n) ",""],
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

    # retourne la carte de ce joueur qui correspond à l'abbréviation
    def joue(self,abbr):
        
        carte =  self.main.pop(abbr,None)
        return carte
        
# un pli correspond à un tour de jeu
# lorque tout le monde a joué, le pli détermine le gagnant        
class Pli:
    def __init__(self,cartes=[None,None,None,None],entame_index=0):
        self.cartes = cartes
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
        if n==len(self.cartes) : return True
        return False
    
    # détermine le gagnant de ce pli
    def gagnant(self):  
        atouts =[0,0,0,0]
        for i in range(4):
            if self.cartes[i].famille=="atout":
                atouts[i] = self.cartes[i].valeur
        # teste s'il y a des atouts
        atouts = np.array(atouts)
        maxi = np.max(atouts)
        g = np.argmax(atouts)
        if maxi>0 : return g  # l y a au moin un atout qui n'est pasl'excuse
  
        # cas particulier ou l'excuse est jouee en premier
        if self.cartes[self.entame_index].abbr=='e':
            self.entame_index = (self.entame_index+1)%4 
        valeurs=[0,0,0,0]
        for i in range(4):
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
    

    
    
    
    def __init__(self,noms_joueurs,donneur_index=0,distributeur=None,debug=False):
        """
        Débute la partie, crée le jeu, le mélange, initialise le donneur,
        l'entame, le joueur, le chien et les levées
        Args : 
         noms_joueurs : array of string
         donneur   : (int) l'indice du premier donneur
         distributeur : s'occupe d'envoyer les mails pour la distribution
        """   
        self.distributeur = distributeur
        self.jeu= []
        self.joueurs = [Joueur(nom=n)  
                    for  n in noms_joueurs]
        self.donneur_index = donneur_index
        # charge le jeu de cartes
        self.preneur_index = -1 # pas de preneur
        self.joueur_index = (donneur_index+1)%self.nombre()
        self.entame_index = self.joueur_index
        
        self.chien= []
        self.pli = Pli(entame_index=self.entame_index)
        
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
        
            
    def nombre(self):
        """
        Returns :
            nombre : le nombre de joueurs
        """
        return len(self.joueurs)
    
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
            
    
    def finie(self):
        """
        Returns :
            True si la partie est finie
        """
        restes = [ len(j.main)  for j in self.joueurs ]
        restes = sorted(restes)
        if restes == [0,0,0,6] :
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
            # distribue le chien
            
            index_chien = np.arange(21)
            index_chien = np.random.choice(index_chien,6,replace=False)
            index_chien.sort()
            print(index_chien)
            direction = (self.donneur_index+1)%self.nombre()
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
                     
                 direction = (direction+1)%self.nombre()
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
         joueur = self.joueur()
         if self.debug :
             abbr = list(joueur.main.values())[0].abbr         
         carte = joueur.joue(abbr)
         cartes = self.pli.cartes
         # la carte jouée n'existe pas
         if carte is None : 
             return [],False
 
         self.pli.ajoute(self.joueur_index,carte)
         self.joueur_index = (self.joueur_index+1)%self.nombre()  
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
                
                    


            self.entame_index = (gagnant_index)%self.nombre()
            self.joueur_index = self.entame_index 
             # ajouter les cartes aux levees de l'attaque ou de la défense
            if gagnant_index == self.preneur_index:
                self.levee[0]= self.levee[0]+self.pli.cartes
            else :
                 self.levee[1]=self.levee[1]+self.pli.cartes
            if excuse_echangee : 
                self.levee[self.echange] = self.levee[self.echange]+[excuse]
             # initialise le pli
            self.pli.cartes = [None,None,None,None]
            self.pli.entame_index = self.entame_index
            
            return excuse_echangee

                
            
        

    def compter(self):
        """
        Place les cartes de l'écart dans la levée et compte les points
        Returns :
           score : le score de l'attaquant
        """
        if self.etat==AFFICHAGE_SCORE:
            # carte en echange de l'excuse
            
            if self.echange != -1 :
                for carte in self.levee[self.echange]:
                    if carte.valeur == 0.5:
                        break
                print("carte echangee :",carte.abbr)    
                self.levee[self.echange].remove(carte)
                self.levee[(self.echange+1)%2].append(carte)
            
            # ajoute l'écart à la levée de l'attaquant
            self.levee[0] = list(self.preneur().main.values())+self.levee[0] 
            self.preneur().main = {}
            score = sum([carte.points for carte in self.levee[0] ])
            self.etat = AFFICHAGE_SCORE 
            return score
            
        
    def rejouer(self):
         """
         Les joueurs ont accepté de rejouer une partie
         """
         self.echange = -1  # pour l'echange de l'excuse
         # remet les levées dans les tas de cartes
         self.jeu = self.levee[0]+self.levee[1]
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
         if self.debug :
             print("ligne 483 ",len(self.jeu))
         
         

        
    def couper(self,int=-1):
        """
        reconstitue le jeu à partir des jeux des joueurs si personne
        n'a pris, ou à partir des levées si la partie s'est jouée
        puis coupe le jeu
        """
        if self.etat==CARTES_RASSEMBLEES:
            self.jeu = self.jeu[:15]+self.jeu[15:]



    def get_message(self):
        """
        retourne le message correspondant à l'etat du jeu
        """
        message = MESSAGE[self.etat][0]
        if self.etat == DISTRIBUE :
            message = message.format(str(self.donneur()))
            # affiche toutes les cartes des joueurs

        elif self.etat == ECART :
            self.ecarter()
            message = message.format(self.preneur())
        elif self.etat == PLI_EN_COURS :
            # affiche les cartes du joueurs
            print(self.affiche(joueur_index = self.joueur_index))
            message = message.format(self.joueur())
        elif self.etat == PLI_FINI :
            gagnant = self.gagnant()
            message = message.format(gagnant)
        elif self.etat == PARTIE_FINIE :
            message = message.format(self.preneur())
            
        elif self.etat == AFFICHAGE_SCORE :
            score = self.compter()
            message = message.format(self.preneur(),score)
        return(message)     

    def action(self,entry_input):
        """
        recupère input si nécessaire et change l'état vers une autre action
        Return :
            message : le message de cette action
            cartes  : un tableau ['1','3','2tr'] contenant les abbréviations des cartes
        """
        if entry_input == 'FIN':
            return 'FIN',[]
        message = MESSAGE[self.etat][1]
        cartes = []
        if self.etat == PRET:
            if self.distribuer() :
                self.etat = DISTRIBUE
        elif self.etat == DISTRIBUE :
            # les jeux ne sont pas envoyés par email
            if not self.distributeur:
                print(self.affiche()) 
            else :
                self.distributeur.send(self)    

            self.etat = PRISE
        elif self.etat == PRISE :
            if entry_input in ['-1','0','1','2','3']:
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
            cartes,complet = self.jouer(entry_input)
            if cartes :
                cartes = [(carte.abbr if carte  else "_") for carte in cartes]
            if complet :
                self.etat = PLI_FINI
        elif self.etat == PLI_FINI:
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
            self.etat = PARTIE_TERMINEE
        elif self.etat == PARTIE_TERMINEE:
            if entry_input =='n' :
                return "FIN",[]
            else : 
                self.rejouer()
                self.etat = CARTES_RASSEMBLEES
        elif self.etat == CARTES_RASSEMBLEES:
            self.couper()
            self.etat = PRET               
           
        
        return message,cartes




if __name__ == "__main__":
    joueurs = ['Martin','Pierrot','Georges','Thomas']
    score = 0
    donneur = int(input("Premier donneur : "))
    partie = Partie(joueurs,donneur_index=donneur,debug=True)
    
    while True:
        

        message = partie.get_message() 
        reponse = input(message)
        message,cartes  = partie.action(reponse)
        if partie.debug : 
            partie.affiche_etat()
        print(message)
        if len(cartes)>0 : print(cartes)
        if message =='FIN' : break
 

    
 

    
    
   