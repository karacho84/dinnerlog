'''
Created on 18.08.2013

@author: jannik'''
from datetime import datetime


class Mahlzeit(object):
    '''
    Eine Mahlzeit, die aus mehreren Zutaten besteht.
    '''


    def __init__(self, name, zutaten, angelegt=datetime.now()):
        '''Initialisieren mit Name und Zutaten-Dictionary'''
        self.name = name
        self.zutaten = zutaten
        self.angelegt = angelegt
        
    def addZutatenMitMenge(self, zutaten):
        '''Fuegt das dictonary bestehend aus Zutat und Menge zur Mahlzeit hinzu'''
        for zutat, menge in zutaten.items():
            self.addZutat(zutat, menge)
        
    def addZutat(self, zutat, menge):
        self.zutaten[zutat] = menge
        
    