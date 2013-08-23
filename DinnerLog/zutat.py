'''
Created on 18.08.2013

@author: jannik
'''

class Zutat(object):
    '''
    Eine Zutat, bestehend aus name und kcalpro 100 Gramm
    '''

    def __init__(self, name, fett, eiweiss, kh):
        '''
        Constructor
        '''
        self.name = name
        self.fett = fett
        self.eiweiss = eiweiss
        self.kh = kh
        
    @property
    def kcal(self):
        return self.fett*9.3+self.eiweiss*4.1+self.kh*4.1