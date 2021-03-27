#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 07:30:55 2020

@author: martin
"""
from tarot import Tarot
import numpy as np

class Phase:
    """
    To implement different phase of the tarot game, with the different interactions
    """
    def __init__(self,partie):
        """

        Parameters
        ----------
        partie : Tarot
            The game of tarot that is ongoing.

        Returns
        -------
        None.

        """
        self.partie = partie
        
    def message(self):
        """
        In this phase, will return the message to display before each turn

        Returns
        -------
        None. Will return a string

        """
        pass

        
    def choix(self):
        pass
        """
        The choices offered to the players
        returns
            dictionary key are player index and values are list of tuple with the command, the text and the index of the player that can make the choice
        """
    def prompt(self):
        """
        Return : 
            int. The index of the next player that has to make a choice 
        """
        return self.partie.seconde

    def cartes_visibles(self):
        """
        Return : 
            array of cartes. The cartes that all the players can see at this moment of the game 
        """

        return []
    


    def action(self,commande,cartes=""):
        """
        Actally does the stuff, what happens when the player prompted has made a game decision.

        Parameters
        ----------
        commande : String
            The command to execute (for instance "JOUER", "DONNER"...).
        cartes : String
            The cards that eventually make sens with the command  (for instance : "rtr,2co")
        Returns
        -------
        bool
            DESCRIPTION.

        """
        if commande == "ANNULER":
            self.partie.ramasser()
            self.partie.recommencer()
            return True
    def result(self):
        pass
   
    
   
class Couper(Phase):
    def __init__(self,partie):
        super().__init__(partie) 

    def message(self):
        return "C'est à {{Joueur[{}]}} de couper le paquet".format(self.partie.heure)
    
    def choix(self):
        return {self.prompt() : [("COUPER","couper le jeu")] }

    def prompt(self):
        return self.partie.heure
    
    def action(self,commande,cartes=""):
        if super().action(commande):
            return True
        if commande== "COUPER":
            #self.partie.ramasser()
            #self.partie.recommencer()
            self.partie.couper()
            return True



class Donner(Phase):
    def __init__(self,partie):
        super().__init__(partie)  
    
    def message(self):
        return "C'est à {{Joueur[{}]}} de distribuer".format(self.partie.heure)
    
    
    def choix(self):
        return {self.prompt() :[("DONNER","donner le jeu")] }
    def prompt(self):
        return self.partie.heure
    
    
    def action(self,commande,cartes=""):
        if super().action(commande):
            return True
        if commande== "DONNER":
            self.partie.donner()
            return True
    
    
class Encherir(Phase):
    def __init__(self,partie):
        super().__init__(partie)
    def message(self):
        if len(self.partie.contrats[self.partie.contrats==-1])==self.partie.number_of_players:
            return "Les joueurs vont passer leurs contrats. C'est {{Joueur[{index}]}} qui commence.".format(index=self.partie.seconde)
        else : 
            return "C'est à {{Joueur[{index}]}} de passer son contrat".format(index=self.partie.seconde)
    def choix(self):
        contrat,_ = self.partie.get_contrat()
        retour = [(str(c),v) for c,v in Tarot.LES_CONTRATS.items()  if c>contrat]
        if contrat >= Tarot.PASSE :
            retour = [(str(Tarot.PASSE),Tarot.LES_CONTRATS[Tarot.PASSE])]+retour
        # add 'passe'
        return {self.prompt() :retour}
    def prompt(self):
        return self.partie.seconde
    def action(self,commande,cartes=""):
        commande = int(commande)
        self.partie.encherir(commande)
    def result(self):
        j = self.partie.precedent(self.prompt())
        c = self.partie.contrats
        if (len(c[c==-1]) == 0) or (len(c[c==-1]) == 1 and self.partie.variante==Tarot.MORT):
            c,p = self.partie.get_contrat()
            if c==Tarot.PASSE:
                #self.partie.ramasser()
                #self.partie.recommencer()
                return "Personne n'a pris."
            return "C'est {{Joueur[{}]}} qui a pris, il a fait une {}.".format(p,self.partie.LES_CONTRATS[c])
        c = c[j]
        return "{{Joueur[{}]}} a fait une {}.".format(str(j),self.partie.LES_CONTRATS[c])




        
class Appeler_Roi(Phase):
    def __init__(self,partie,hasard=False):
        super().__init__(partie)
        self.hasard = hasard # pour jouer au hasard en phase de test

    def message(self):
        contrat,joueur =  self.partie.get_contrat()
        message = ""
        message = "Il doit maintenant appeler un roi."
        return message   
    
    def choix(self):
        contrat,joueur =  self.partie.get_contrat() 
        return {self.prompt() :[("APPELER_rtr","Le roi de pique."), 
                    ("APPELER_rca","Le roi de carreau."), 
                    ("APPELER_rco","Le roi de coeur."),
                    ("APPELER_rtr","Le roi de trèfle."),
                    ]}
        
    def prompt(self):
        contrat,preneur =  self.partie.get_contrat() 
        return preneur
        
    def action(self,commande,cartes=""):
        if "APPELER" in commande:
            roi = commande[-3:]
            self.partie.roi_appele = roi
            return True 
        
    def result(self):
            contrat,preneur =  self.partie.get_contrat()
            if self.partie.roi_appele=='rpi':
                roi = "pique"
            elif self.partie.roi_appele=='rca':
                roi = "carreau"
            elif self.partie.roi_appele=='rco':
                roi = "coeur"
            elif self.partie.roi_appele=='rtr':
                roi = "trefle"

                
            return "{{Joueur[{}]}} a appelé le roi de {}.".format(preneur,roi)




class Ramasser_chien(Phase):
    """
    On montre le chien quand tout le monde passe ou quand le contrat est une petite ou une garde
    """
    def __init__(self,partie):
        super().__init__(partie)  
    def message(self):
        contrat,joueur =  self.partie.get_contrat()
        message = ""
        if contrat in [Tarot.PASSE]:
            message = "Voici le chien."
        elif contrat in [Tarot.PETITE,Tarot.GARDE]:
            message = "Voici le chien. {{Joueur[{}]}} peut le ramasser une fois que tout le monde l'a vu.".format(joueur) 
        elif contrat in [Tarot.GARDE_SANS,Tarot.GARDE_CONTRE]:    
           if contrat == Tarot.GARDE_SANS:
               message = "Il doit mettre le chien à l'écart.".format(joueur)
           else:
               message = "Et le chien revient à la défense."    
        return message      

    def choix(self):
        contrat,joueur =  self.partie.get_contrat() 
        if contrat == Tarot.PASSE:
            return {self.prompt() :[("RECOMMENCER","refaire une partie.")] }
        if contrat in [Tarot.PETITE,Tarot.GARDE]:
                return {self.prompt() : [("RAMASSER_CHIEN","ramasser le chien")] }
        if contrat in [Tarot.GARDE_SANS,Tarot.GARDE_CONTRE]:
                return {self.prompt() :[("CHIEN_ECART","mettre le chien à l'écart.")]}

    def prompt(self):
        contrat,preneur =  self.partie.get_contrat() 
        if contrat == Tarot.PASSE:
            return self.partie.heure
        if contrat in [Tarot.PETITE,Tarot.GARDE,Tarot.GARDE_SANS]:
            return preneur
        if contrat in [Tarot.GARDE_CONTRE]:
            # in that case, the donneur is putting the cards in ecart
            return self.partie.heure


    def cartes_visibles(self):
        return self.partie.chien

        
    def action(self,commande,cartes=""):
        if commande == "RECOMMENCER":
            self.partie.ramasser()
            self.partie.recommencer()
            return True
            
        if commande=="CHIEN_ECART" : 
            # chien is put directly to ecart
            self.partie.ecarter()
            return True
        elif commande=="RAMASSER_CHIEN" :
            self.partie.integrer_chien()




class Ecarter(Phase):
    def __init__(self,partie):
        super().__init__(partie)
    def message(self):
        contrat,preneur =  self.partie.get_contrat()
        
        cheville=''
        if len(self.partie.ecart) >0: 
            cheville='encore '
        reste = self.partie.taille_chien-len(self.partie.ecart)
        
        message = "{{Joueur[{index}]}} doit {cheville}mettre {reste} cartes à l'écart.".format(index=preneur,cheville=cheville,reste=reste)
        return message   
    
    def choix(self):
        return {self.prompt() :[("ECARTER","Mettre à l'écart."),
                                ("REPRENDRE","Reprendre les cartes.")
                                ]}
        
    def prompt(self):
        contrat,preneur =  self.partie.get_contrat() 
        return preneur



        
    def action(self,command,cartes=""):
            
        contrat,joueur =  self.partie.get_contrat()
        if command == "REPRENDRE":
            self.partie.ecarter(reverse=True)
            return True
        if command == "ECARTER":
            cartes = np.array(cartes.split(','))
            self.partie.ecarter(cartes)
            return True


        
        
class Jouer(Phase):
    def __init__(self,partie,hasard=False):
        super().__init__(partie)
        self.hasard = hasard # pour jouer au hasard en phase de test
    def message(self):
        pass
    def choix(self):
        """
        The prompted player can play a card. The preceding player (if any) has the possibility to 
        take his card back inorder to play another one.
        """
        partie = self.partie
        retour = {self.prompt() :[("JOUER","Jouer"),]}
        if not partie.pli[partie.minute]:
            # none has played yet, there is no card to remove
            return retour
        
        if  partie.pli[partie.seconde]: # everyone has played
            if len(partie.V)>0:   # it is not the first round
                precedent = partie.precedent(partie.V[-1])
            else :
                precedent = partie.precedent(partie.minute)
        else :
            precedent = partie.precedent(partie.seconde)
        if precedent == self.prompt():
            retour[precedent].append(("ANNULER","annuler le coup"))
        else :
            retour[precedent] = [("ANNULER","annuler le coup")]
        return retour   
        
    def cartes_visibles(self):
        return self.partie.pli


    def action(self,commande,cartes=""):
        if commande == "JOUER":
            if self.hasard :
                rng = np.random.default_rng()
                carte = rng.choice(self.partie.mains[self.partie.seconde])
                cartes = carte.abr
            self.partie.jouer(cartes)
            return True
        elif commande == "ANNULER":
            self.partie.jouer("CANCEL")
    def result(self):
        pli = np.array(self.partie.pli)
        # message to print when someone wins the pli
        if len(pli[pli!=None])== self.partie.number_of_players :
            m = "{{Joueur[{}]}} a remporté le pli.".format(self.partie.minute)
            return m



class Montrer_Ecart(Phase):
    """
    Shows the cards in ecart and put them in the right levee
    """
    def __init__(self,partie):
        super().__init__(partie)
    def message(self):
        contrat,preneur = self.partie.get_contrat()
        if contrat<self.partie.GARDE_SANS:
            return "Voici l'écart de {{Joueur[{}]}}".format(preneur)
        elif contrat==self.partie.GARDE_SANS:
            return "Voici le chien qui revient à l'attaque."
        elif contrat==self.partie.GARDE_CONTRE:
            return "Voici le chien qui revient à la défense."
        
    def choix(self):
        contrat,preneur = self.partie.get_contrat()
        return {self.prompt() :[("VOIR","Voir la levée de {{Joueur[{}]}}.".format(preneur))] }
    def cartes_visibles(self):
        return self.partie.ecart

    def action(self,commande,cartes=""):
        if commande == "VOIR":
            self.partie.game_over = True


        
class Conclure(Phase):
    def __init__(self,partie):
        super().__init__(partie)
        self.levee_attaque,self.levee_defense,self.score = self.partie.get_levees() # les cartes remportées (attaque,defense)
    def message(self):
        contrat,preneur = self.partie.get_contrat()
        return "{{Joueur[{}]}} a fait une {}. Il a réalisé {} points".format(preneur,self.partie.LES_CONTRATS[contrat],self.score)
    def choix(self):
        contrat,preneur = self.partie.get_contrat()
        return {self.prompt() :[("REJOUER","Refaire une partie")]}
    def cartes_visibles(self):
        return self.levee_attaque

    def action(self,commande,cartes=""):
        if commande == "REJOUER":
            self.partie.ramasser()
            self.partie.recommencer()
        
                
def search_phase(partie):
    if not partie.coupe:
        return Couper(partie)
    if len(partie.paquet) == 78:
        return Donner(partie)
    contrats_restants = len(partie.contrats[partie.contrats== -1])
    if (contrats_restants != 0 and partie.variante != Tarot.MORT) or ( contrats_restants != 1 and partie.variante == Tarot.MORT ) :
            return Encherir(partie)
    # alors les cartes sont distribuees, les contrats sont passes
    c,p = partie.get_contrat()   
    if (partie.variante == Tarot.APPEL_AU_ROI) and partie.roi_appele=='':
        return Appeler_Roi(partie)
    if len(partie.chien)>0:
        return Ramasser_chien(partie)
    
    # l'écart est incomplet
    if c in [Tarot.PETITE,Tarot.GARDE] and len(partie.ecart)<partie.taille_chien:
        return Ecarter(partie)
    
    if partie.levees.shape[0]*partie.levees.shape[1] != 78-partie.taille_chien :
        return Jouer(partie)    
    elif not partie.game_over:
        return Montrer_Ecart(partie)
    else :
        return Conclure(partie)
    
    #return Phase(partie)    
    






if __name__ == "__main__":
    
    # test de partie avec un seuk joueur

    partie = Tarot(Tarot.TROIS)
    phase = None  
    
    
    while True:
        phase = search_phase(partie)
        # message to introduce what is to do next (if needed)
        print(phase.partie.get_main(phase.prompt()))
        
        if phase.message() : print(phase.message())
        # get the choices for the answer
        if len(phase.cartes_visibles())>0:
            print(list(phase.cartes_visibles()))
        
        
        choix = phase.choix()[phase.prompt()]
        for e,c in choix:
            print("{}-{}".format(e,c))
        # the player prompted is the one that can do the next choice
        #print(getXML(phase).toprettyxml())
        entree = input("Joueur{} > ".format(phase.prompt()))
        
        # search the commands and the cards
        i = entree.find(" ")
        if i==-1 :
            commande,cartes = entree,""
        else: 
            commande,cartes = entree[:i],entree[i+1:]    
        phase.action(commande,cartes)
        if commande == "QUITTER":
            break
        # prints some feedback (if needed)
        result = phase.result()
        if result:
            print(result)
    
                           
