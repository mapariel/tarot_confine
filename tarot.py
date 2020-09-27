import numpy as np
import csv



class Carte:
    def __init__(self,infos=[]):
        self.famille=infos[0]
        self.nom=infos[1]
        self.valeur=int(infos[2])
        self.points = float(infos[3])
        self.abr = infos[4]
    
    def __str__(self):
        return self.abr
    def __eq__(self,other):
        if not other : 
            return False
        return self.valeur==other.valeur
    def __lt__(self,other):
        return self.valeur < other.valeur


"""
This class represents a game of tarot
"""
class Tarot:
    # constantes de jeu
    SANS = 0
    APPEL_AU_ROI = 1
    MORT = 2
    LES_VARIANTES = {SANS:"",APPEL_AU_ROI:"avec appel du roi",MORT:"avec un mort"}
    
    PASSE = 1
    PETITE = 2
    GARDE = 3
    GARDE_SANS = 4
    GARDE_CONTRE = 5
    LES_CONTRATS = {PASSE:"passe",PETITE:"petite",GARDE:"garde",GARDE_SANS:"garde sans le chien",GARDE_CONTRE:"garde contre le chien"}
    
    
    
    def __init__(self,number_of_players,variante):
        self.number_of_players = number_of_players
        self.paquet = np.array([])  
        with open('cartes.csv', newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for line in reader:
                        carte = Carte(line)
                        self.paquet = np.append(self.paquet,carte)
        # mix the pack of cards
        np.random.shuffle(self.paquet)
        self.heure = 0 # l'indice du donneur
        self.minute=1  # sous indice, celui qui a joué le premier (qui a entamé) 
        self.seconde = 1 # sous-sous-indice, désigne le prochain joueur
        self.commencer(self.number_of_players,variante)


    def commencer(self,n_joueurs,variante):
        """
        Parametrise the game (number of players and variant). 

        Parameters
        ----------
        n_joueurs : int
            number of players.
        variante : int, optional
            can be self.MORT, APPEL_AU_ROI or SANS. The default is 0. (self.MORT)

        Returns
        -------
        None.

        """
        self.number_of_players = n_joueurs
        self.coupe = False # le paquet n'est pas coupé
        # each player will have a main of cards
        self.mains = []
        for n in range(self.number_of_players):
            self.mains.append(np.array([])) 
        
        # checks variante and number_of_players are valid
        if n_joueurs in (3,4):
            self.variante = self.SANS
        elif n_joueurs==5 :
            if variante in (self.APPEL_AU_ROI,self.MORT) : 
                self.variante = variante
            else : self.variante = self.MORT    
        
        
        # puts minute and second accordingly to hour
        self.minute = self.suivant(self.heure)
        self.seconde = self.minute 
        
        # sets the size of chien and lot_donne
        self.taille_chien = 6
        if self.variante == self.APPEL_AU_ROI:
            self.taille_chien = 3

        
        if self.number_of_players == 3:
            self.lot_donne = 4
        else:
            self.lot_donne = 3
        
        # creates the pli and the contrats
        self.pli = self.create_pli()
        self.contrats = np.array([-1]*self.number_of_players)
        self.levees = np.array([],dtype=np.int8)
        self.levees.shape = (0,self.number_of_players)
        self.V = np.array([],dtype=np.int8) 
        self.chien = np.array([])
        self.ecart = np.array([])
        # the king to be called in case of variante = APPEL_AU_ROI
        self.roi_appele = ""
    
        
    def recommencer(self):
        """
        Just call it to play a new game with the same parameters (number of players and variante)

        """
        self.commencer(self.number_of_players,self.variante)
    
    def couper(self):
        self.coupe = True
        self.heure = self.suivant(self.heure)
        self.minute = self.suivant(self.heure)
        self.seconde = self.minute 
        coupe = np.random.binomial(78,0.5)
        self.paquet = np.append(self.paquet[:coupe],self.paquet[coupe:])


    

    def create_pli(self):
        """
        creates a pli, where each player plays a card at each round

        Returns
        -------
        pli : array
            array is initialised with [None,None,...].
            further, it will get instance of Card

        """
        pli = []
        for i in range(self.number_of_players):
            pli.append(None)
        return pli    




    def who_has_played(self,abr):
        """
        Who has played a certain card, and when

        Parameters
        ----------
        abr : str
            abbreviation of the card you are looking for ('e', 'rtr'...).

        Returns
        -------
        None if the card has not been played yet
        player : int
            Who has played.
        tour : int
            And when.

        """
        if len(self.levees)==0: return 
        abrs = np.array([[carte.abr if carte  else '' for carte in pli] for pli in self.levees])
        tour,player = np.where(abrs==abr)
        if len(player) == 0 : return # card has not been played, it is in the chien or ecart
        return player[0],tour[0]


    def precedent(self,index,oublie_mort=True):
        index = (index-1)%self.number_of_players
        if oublie_mort and index==self.heure and self.variante==self.MORT:
            index = (index-1)%self.number_of_players
        return index    


    def suivant(self,index,oublie_mort=True):
        """
        returns the next index, if mort is True and variante=MORT, then, the next index cannot
        be the "donneur" (self.heure)

        Parameters
        ----------
        index : int
            index which the follower to be found.
        mort : boolean, optional
            DESCRIPTION. The default is False.

        Returns
        -------
        index : int
            DESCRIPTION.

        """
        index = (index+1)%self.number_of_players
        if oublie_mort and index==self.heure and self.variante==self.MORT:
            index = (index+1)%self.number_of_players
        return index    
        
        
        


 

    def donner(self):
        """
        Distribue les mains aux joueurs et au chien.
        
        Returns
        -------
        None.
    
        """
        
        # combien de paquets sont à donner aux joueurs
        tours_donne = (len(self.paquet)-self.taille_chien)//(self.lot_donne)
        rng = np.random.default_rng()
        # indice des cartes du chien pendant la donne
        indexes = rng.choice(tours_donne-1, self.taille_chien,replace=False)
        
        # n est le joueur qui recoit un lot, au début, il est à droite du donneur
        n = self.suivant(self.heure)
        tour=0
        
        while tour<tours_donne:
            self.mains[n],self.paquet = np.append(self.mains[n],self.paquet[:self.lot_donne]),self.paquet[self.lot_donne:]
            if tour in indexes:
                self.chien,self.paquet = np.append(self.chien,self.paquet[:1]),self.paquet[1:]
            tour=tour+1
            n=self.suivant(n)
        
        # the player at the left of the donneur will be the first to call his contract.     
        #self.seconde = self.suivant(self.seconde)
            
         
        
    def encherir(self,contrat):
         """        
         Parameters
         ----------
         contrat : int
             can be PASSE, PETITE, GARDE, GARDE_SANS or GARDE_CONTRE

         Returns
         -------
         None.

         """
         # checks if the contrat is a correct value
         if contrat not in (self.PASSE,self.PETITE,self.GARDE,self.GARDE_SANS,self.GARDE_CONTRE):
             return
         c,j = self.get_contrat()
         # if not passe, contrat must be higher than the current higher contrat
         if contrat != self.PASSE and contrat <= c:
             contrat = self.PASSE
         # only one contrat for each game
         if self.contrats[self.seconde] != -1 :
             return 
         self.contrats[self.seconde] = contrat
         self.seconde = self.suivant(self.seconde)


    
    def get_contrat(self):
        """
        evaluates the highest contrat

        Returns
        -------
        int
            the contrat of the player.
        j : int
            the player with highest contrat.

        """
        j = np.argmax(self.contrats)
        return self.contrats[j],j
    
    
    def get_attaque_defense(self):
        """
        To know who is attaque and who is defense in this game. For 3 and 4 players, attaque is only preneur
        For 5 players, it depends on the variante.

        Returns
        -------
        attaque : numpy array of integers
            index ot hte player in attaque.
        defense : numpy array of integers
            index ot hte player in attaque..

        """
        _,p = self.get_contrat()
        attaque = np.array([p])  # attaque is the "preneur" and the one he calls in case of variante APPEL_AU_ROI
        if self.variante == self.APPEL_AU_ROI:
            rep = self.who_has_played(self.roi_appele)
            if rep :  # in case the roi appele has not been played
                p2,_ = rep  
                if p2 != p : # when someone is calling himself, do nothing
                    attaque = np.append(attaque,p2)
        defense = np.delete(np.arange(self.number_of_players),attaque)
        if self.variante == self.MORT :
            defense = defense[defense != self.heure]
        return attaque,defense  
    
        

    def integrer_chien(self,cartes=None):
        """
        Put the chien in the mains of the preneur.

        Parameters
        ----------
        cartes : np.array of strings, optional
            DESCRIPTION. The default is None. All the cards are put directly to the main

        Returns
        -------
        None.

        """
        contrat,preneur = self.get_contrat()
        # only for petite and garde
        if contrat>self.GARDE:
            return
        if not cartes:
            self.mains[preneur] = np.append(self.mains[preneur],self.chien)
            self.chien = []
            
    def ecarter(self,cartes=None):
        """
        Remove carts from the main of the preneur and put them to the ecart.
        Cartes are taken directly from chien in case of garde sans or garde contre
        Number of cards in ecart has to be less than self.taille_chien (usually 6)

        Parameters
        ----------
        cartes : list of string
            the strings are the abbreviations of the cards to remove.

        Returns
        -------
        None.

        """
        contrat,preneur = self.get_contrat()
        # only for passe and garde
        if contrat>self.GARDE:
            self.ecart,self.chien = self.chien,np.array([])
            return
        # cannot have more cards than maximum size
        if len(self.ecart)+len(cartes)>self.taille_chien:
            return
        abrs = np.array([carte.abr for carte in self.mains[preneur] ])
        indices = np.intersect1d(abrs,cartes,return_indices=True)[1]
        self.mains[preneur],ajouts = np.delete(self.mains[preneur],indices),self.mains[preneur][indices]
        self.ecart = np.append(self.ecart,ajouts)


    def jouer(self,abr):
        """
        play a card from the main of the player when it's his time to play (self.seconde).
        if the card doesn't belong to the player, nothing happens.
        
        when a card is played, value of self.seconde is updated to the next player
        if the pli is over, then self.minute is updated to the winner and the pli is 
        put int levees, whith the index of the winner.
        Parameters
        ----------
        abr : string
            abbreviation of the card to play. I f abr="CANCEL", then remove the last card played
            

        Returns
        -------
        None.

        """
        # logging.debug(f'heure : {self.heure}, minute :{self.minute}, seconde :{self.seconde} ')

        
        if abr == "CANCEL":
            precedent = self.precedent(self.seconde)
            if  self.pli[precedent] is None :
                return # there is no card played by the preceding player
            # tests if the pli is already finished
            if  self.pli[self.seconde]:
                # finds who has played the last card
                if len(self.V)>0 :
                    self.minute = self.V[-1]
                else : self.minute = self.suivant(self.heure)   
                precedent = self.precedent(self.minute)
            
            self.mains[precedent] = np.hstack((self.mains[precedent],[self.pli[precedent]]))
            self.pli[precedent] = None
            self.seconde = precedent
            return True


        # gets (and remove from it) the card from the main of the player,
        main = self.mains[self.seconde] 
        cartes_abr = [carte.abr for carte in main ]
        cartes_abr = np.array(cartes_abr)
        carte,self.mains[self.seconde] = main[cartes_abr == abr],main[cartes_abr != abr]
        
        # if the card is not in the main of the player, do nothing
        if len(carte)==0 : return
        
        # tests if the pli is already finished
        if  self.pli[self.seconde]: 
            self.levees = np.vstack((self.levees,self.pli))
            self.V = np.append(self.V,self.seconde)
            self.pli = self.create_pli()

        
        # plays the carte
        self.pli[self.seconde] = carte[0] 
        self.seconde = self.suivant(self.seconde)
        
        # in case everyone has played, find the winner of the pli
        if  self.pli[self.seconde]: 
            valeur_gagnant = 0
            coupe = False
            joueur_gagnant = self.minute 
            c = self.pli[self.minute]
            if c.abr != 'e' :
                entame = c.famille
            else :
                joueur_gagnant = self.suivant(joueur_gagnant)
                entame = self.pli[joueur_gagnant].famille 
            
            
            
            playeri = self.minute
            for i in range(self.number_of_players):
                playeri = self.suivant(playeri)
                carte = self.pli[playeri]
                if carte.famille == entame and carte.valeur>valeur_gagnant and not coupe:
                    joueur_gagnant = playeri 
                    valeur_gagnant = carte.valeur
                    
                # coupe
                elif carte.famille == "atout" and carte.abr != 'e' and not coupe and entame != "atout":
                    coupe = True
                    joueur_gagnant = playeri
                    valeur_gagnant = carte.valeur
                    continue 
                # surcoupe 
                elif coupe and carte.famille == "atout" and carte.valeur > valeur_gagnant :
                    joueur_gagnant = playeri
                    valeur_gagnant = carte.valeur
            
            self.minute = joueur_gagnant
            self.seconde = joueur_gagnant
            
            # in case the game is over, don't wait to put the pli on levees
            if len(self.mains[joueur_gagnant])==0 :
                self.levees = np.vstack((self.levees,self.pli))
                self.V = np.append(self.V,self.seconde)
                self.pli = self.create_pli()

                
            

              
              
            
    def echanger(self):
        """
        Makes the exchange if excuse has been played and lost. 
        It doesn't modify self.levees but makes a copy of it

        Returns
        -------
        levees : np array (number_of_turns,number_of_players) of cards
            Modified version of self levees.

        """
        a,d = self.get_attaque_defense()
        levees = np.copy(self.levees)
        points = np.array([[carte.points if carte else -1 for carte in pli] for pli in levees])
        plis_a = np.sort(np.hstack([np.where(self.V == j) for j in a ])).flatten()
        plis_d = np.sort(np.hstack([np.where(self.V == j) for j in d ])).flatten()
        
        # in case of grand chelem, the excuse is lost
        if len(plis_a)==0 or len(plis_d)==0:
            return levees
        
     
        plis_a_d = [plis_a,plis_d] 
     
        temp = self.who_has_played('e')
        if temp is None : return levees # excuse has not been played 
        joueur,tour =temp 
    

        # tests if excuse must be exchanged
        echange = (joueur in a) ^ (self.V[tour] in a)
      
        if echange :
            col = int(self.V[tour] in a) # 0 pour chercher le pli de l'echange dans les plis de l'attaque, 
                                            # 1 dans ceux de la defense
            plis_a_scanner = plis_a_d[col][plis_a_d[col]<tour]
            if len(plis_a_scanner)>0 :
                debut_scan = np.max(plis_a_scanner)
            else:     
                debut_scan = tour                   
            
               
            # indices of tours where to look for echange card  among plis won by attaque or defense  
            scan = plis_a_d[col][plis_a_d[col]>=debut_scan]   
            
            # in case there is no "carte blanche" in the scan area
            if len(np.where(points[scan]==0.5)[0])==0:
                scan = plis_a_d[col]
           
                        
            row_echange = scan[np.min(np.where(points[scan]==0.5)[0])]   # the smallest possible row
            column_echange = np.where(points[row_echange]==0.5)[0][0]    # any column where the card has no value
            # makes the echange
            levees[row_echange,column_echange] , levees[tour,joueur] =  levees[tour,joueur] , levees[row_echange,column_echange]
        return levees

    
    def get_levees(self):
        """
        When the game is over, we put together the cards of attaque and defense  and return
        the two levees. Doesn't change levees (can still be used for statistical reasons or 
        to replay the game).

        Returns
        -------
        levee_attaque : numpy list of cards
            cards of atttaque.
        levee_defense : numpy list of cards
            cards of defense.
        score : score of attaque    

        """
        a,d = self.get_attaque_defense()
        # the function does not change self.levees, we copy it
        levees = self.echanger()
        ecart = np.copy(self.ecart)
        c,p = self.get_contrat()
        
        plis_a = np.sort(np.hstack([np.where(self.V == j) for j in a ]))
        plis_d = np.sort(np.hstack([np.where(self.V == j) for j in d ]))
        
        # remove a column of None if there is a Mort
        if self.variante == Tarot.MORT:
            levees = np.delete(levees,self.heure,axis=1)
        
        levee_attaque = levees[plis_a,:].flatten()
        levee_defense = levees[plis_d,:].flatten()
        
        if c<=Tarot.GARDE_SANS:
            levee_attaque = np.append(ecart,levee_attaque)
        elif c==Tarot.GARDE_CONTRE:
            levee_defense = np.append(ecart,levee_defense)

        score = np.sum([carte.points for carte in levee_attaque])  

        return levee_attaque,levee_defense,score

        

    def ramasser(self):
        """
        Gather all the cards to put them back in the card deck (paquet).
        To call at the end of the game or when a game is stopped.
                
        Returns
        -------
        None.

        """
        # the cards of the players and chien are mixed
        # if len(self.paquet) != 78 :
        
        # takes the cards the player still have
        lots = [main for main in self.mains if len(main)>0 ]
        # takes the cards already played
        if len(self.levees)>0:
            attaque,defense,_ = self.get_levees()
            self.ecart = np.array([])
            lots.append(attaque)
            lots.append(defense)
        
        if len(self.chien)>0 : 
            lots.append(self.chien) 
        
        
        lots = np.array(lots)
        rng = np.random.default_rng()
        rng.shuffle(lots)
        for lot in lots:
             self.paquet = np.append(self.paquet,lot)
        self.coupe = False
        assert len(self.paquet)==78,"Le jeu ne contient pas 78 cartes !"
