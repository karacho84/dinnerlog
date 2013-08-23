'''
Created on 18.08.2013

@author: jannik
'''
from controller import Controller
from dbacccess import DBAccess

if __name__ == '__main__':
    
    Controller()
    
    dba = DBAccess("ernaehrung.db")
    
    #dba.addZutat(Zutat("Zucker", 500))
    #dba.addZutat(Zutat("Sahne", 800))
    
    #dba.addMahlzeit(Mahlzeit("Zuckersahne2", {Zutat("Zucker", 500):100, Zutat("Sahne", 800): 400}))