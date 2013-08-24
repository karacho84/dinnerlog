'''
Created on 21.08.2013

@author: jannik
'''
from dbacccess import DBAccess
from gui import GUI
from tkinter.constants import END
from zutat import Zutat
from mahlzeit import Mahlzeit
from datetime import datetime, timedelta

class Controller(object):
    '''Vermittelt zwischen GUI und DBAccess'''

    def __init__(self):
        '''Initialisiert den Controller.'''
        self.__dba = DBAccess("ernaehrung.db")
        self.__gui = GUI()
        
        # Zutaten
        self.__data_zutaten = []
        # Mahlzeiten
        self.__data_mahlzeiten = []
        # Zutat mit Menge
        self.__data_zutaten_mahlzeit = {}
        # Zuletzt gewählte Zutat merken
        self.__hiddenName = None
        self.__hiddenAngelegt = None
        
        # Datenbank-Listener registieren, der uns bei
        # geaenderten daten informiert
        self.__dba.addListener(self)
        
        # Initialer Datenabruf
        self.__updateZutaten()
        self.__updateMahlzeiten()
        self.__updateStats()
        
        # View-Elemente der GUI mit Aktionen verbinden        
        setCallbackListBox(self.__gui.lb_mahlzeiten, self.__zeigeMahlzeitDetails)
        setCallbackListBox(self.__gui.lb_zutaten, self.__zeigeZutatenDetails)
        setCallback(self.__gui.btn_mahlzeit_hinzu, self.__zutatZuMahlzeitHinzu)
        
        setCallback(self.__gui.btn_zutat_insert, self.__zutatHinzu)
        setCallback(self.__gui.btn_zutat_update, self.__zutatUpdate)
        setCallback(self.__gui.btn_zutat_delete, self.__zutatDelete)
        
        setCallback(self.__gui.btn_insert, self.__mahlzeitHinzu)
        setCallback(self.__gui.btn_update, self.__mahlzeitUpdate)
        setCallback(self.__gui.btn_delete, self.__mahlzeitDelete)
        
        setCallback(self.__gui.btn_neu, self.__neueMahlzeit)
        setCallback(self.__gui.btn_mahlzeit_als_zt, self.__mahlzeitAlsZutat)
        
        # Fuer immer in den Main loop gehen
        self.__gui.root.mainloop()
    
    def update(self):
        """Veranlasst die Aktialisierung der Daten und das Neuzeichnen von GUI-Elementen."""
        self.__updateZutaten()
        self.__updateMahlzeiten()
    
    def __updateZutaten(self):
        self.__data_zutaten = self.__dba.getZutaten()
        
        # alle GUI Elemente aktialisieren, die Zutaten anzeigen
        
        # die zutaten listbox
        self.__gui.lb_zutaten.delete(0, END)
        self.__data_zutaten = self.__dba.getZutaten()
        for zutat in self.__data_zutaten:
            self.__gui.lb_zutaten.insert(END, "{}: {:.1f} kcal, {:.1f}g Fett, {:.1f}g Eiweiss, {:.1f}g KH".format(zutat.name, zutat.kcal, zutat.fett, zutat.eiweiss, zutat.kh))
        
        # das optionmenu
        self.__gui.opt_zutat['menu'].delete(0, END)
        for zutat in self.__data_zutaten:
            self.__gui.opt_zutat['menu'].insert("end", "command", label=zutat.name, command=lambda temp=zutat.name: self.__gui.var_zutat.set(temp))

    def __updateMahlzeiten(self):
        self.__data_mahlzeiten = self.__dba.getMahlzeiten()
        
        # alle GUI elemente die mahlzeiten anzeigen updaten
        self.__gui.lb_mahlzeiten.delete(0, END)
        
        for mahlzeit in self.__data_mahlzeiten:            
            kcal, fett, eiweiss, kh, __ = self.__getMahlzeitNaehrwert(mahlzeit)
            
            self.__gui.lb_mahlzeiten.insert(END, "{0}: {1:.1f} kcal, {2:.1f}g Fett, {3:.1f}g Eiweiss, {4:.1f}g Kh {5}".format(mahlzeit.name, kcal, fett, eiweiss, kh, mahlzeit.angelegt))
        
        self.__updateStats()
    
    def __updateMahlzeitZutaten(self):
        # Alle GUI Elemente die Zutaten zu Mahlzeiten anzeigen
        # updaten
        self.__gui.lb_zutat.delete(0, END)
        for zutat, menge in self.__data_zutaten_mahlzeit.items():
                # naehrwerte auf angegebene menge umrechnen:
                naehwerte = list(map(lambda x: x*menge/100, [zutat.fett, zutat.eiweiss, zutat.kh,zutat.kcal,]))
                self.__gui.lb_zutat.insert(END, "{0}: {1:.1f}g mit {2:.1f}g Fett, {3:.1f}g Ew, {4:.1f}g KH mit {5:.1f} kcal".format(zutat.name, menge, *naehwerte))
   
    
    def __zutatZuMahlzeitHinzu(self):
        zutat_name = self.__gui.var_zutat.get()
        if self.__gui.en_menge.get():
            menge = int(self.__gui.en_menge.get())
        
        # Zutat-Objekt per Name holen
        found = None
        for zutat in self.__data_zutaten:
            if zutat.name == zutat_name:
                found = zutat
                break               
        
        if not found is None and menge:
            self.__data_zutaten_mahlzeit[zutat] = menge
            self.__updateMahlzeitZutaten()
    
    def __zutatAuslesen(self):
        zutat_name = self.__gui.en_name_zt.get()
        fett = self.__gui.en_fett.get()
        eiweiss = self.__gui.en_eiweiss.get()
        kh = self.__gui.en_kh.get()
        
        if zutat_name and fett and eiweiss and kh:
            return Zutat(zutat_name, float(fett), float(eiweiss), float(kh))

    def __zutatHinzu(self):
        zutat = self.__zutatAuslesen()
        if zutat:
            self.__dba.insertZutat(zutat)
            
    def __zutatUpdate(self):
        zutat = self.__zutatAuslesen()
        if zutat:
            self.__dba.updateZutat(zutat)
    
    def __zutatDelete(self):
        zutat = self.__zutatAuslesen()
        if zutat:
            self.__dba.deleteZutat(zutat)
            
    def __mahlzeitHinzu(self):
        # Alle Felder auslesen und einen
        # neuen Datenbankeintrag anlegen
        name = self.__gui.en_name.get()
        if name:
            mahlzeit_neu = Mahlzeit(name, {})
            mahlzeit_neu.addZutatenMitMenge(self.__data_zutaten_mahlzeit)
                
            self.__dba.insertMahlzeit(mahlzeit_neu)
        else:
            print("Verweigere mich eine Mahlzeit ohne Name hinzuzufuegen")
            
    def __mahlzeitUpdate(self):
        if self._hiddenName and self._hiddenAngelegt:
            mahlzeit_neu = Mahlzeit(self._hiddenName, {}, self._hiddenAngelegt)
            mahlzeit_neu.addZutatenMitMenge(self.__data_zutaten_mahlzeit)
            self.__dba.updateMahlzeit(mahlzeit_neu)
            
    def __mahlzeitDelete(self):
        if self._hiddenName and self._hiddenAngelegt:
            mahlzeit_del = Mahlzeit(self._hiddenName, {}, self._hiddenAngelegt)
            mahlzeit_del.addZutatenMitMenge(self.__data_zutaten_mahlzeit)
            self.__dba.deleteMahlzeit(mahlzeit_del)
            

    
    def __zeigeMahlzeitDetails(self, event):
        lb_mahlzeit = event.widget
        
        self.__gui.en_name.delete(0, END)
        sel_idx = int(lb_mahlzeit.curselection()[0])
        self.__gui.en_name.insert(0, self.__data_mahlzeiten[sel_idx].name)
        
        self._hiddenName = self.__data_mahlzeiten[sel_idx].name
        self._hiddenAngelegt = self.__data_mahlzeiten[sel_idx].angelegt
        
        self.__data_zutaten_mahlzeit.clear()
        for zutat, menge in self.__data_mahlzeiten[sel_idx].zutaten.items():
            self.__data_zutaten_mahlzeit[zutat] = menge
        self.__updateMahlzeitZutaten()
        
    def __zeigeZutatenDetails(self, event):
        lb_zutaten = event.widget
        
        # Alle Felder leeren
        self.__gui.en_name_zt.delete(0, END)
        self.__gui.en_fett.delete(0, END)
        self.__gui.en_eiweiss.delete(0, END)
        self.__gui.en_kh.delete(0, END)
        
        sel_idx = int(lb_zutaten.curselection()[0])
        self.__gui.en_name_zt.insert(0, self.__data_zutaten[sel_idx].name)
        self.__gui.en_eiweiss.insert(0, self.__data_zutaten[sel_idx].eiweiss)
        self.__gui.en_fett.insert(0, self.__data_zutaten[sel_idx].fett)
        self.__gui.en_kh.insert(0, self.__data_zutaten[sel_idx].kh)
        
    def __neueMahlzeit(self):
        self.__gui.en_name.delete(0, END)
        self.__data_zutaten_mahlzeit.clear()
        
        self.__updateMahlzeitZutaten()
        

    def __getMahlzeitNaehrwert(self, mahlzeit_neu):
        gesamt_kcal = 0
        gesamt_fett = 0
        gesamt_eiweiss = 0
        gesamt_kh = 0
        gesamt_menge = 0
        for zutat, menge in mahlzeit_neu.zutaten.items():
            gesamt_kcal += zutat.kcal * menge / 100
            gesamt_fett += zutat.fett * menge / 100
            gesamt_eiweiss += zutat.eiweiss * menge / 100
            gesamt_kh += zutat.kh * menge / 100
            gesamt_menge += menge
        
        return gesamt_kcal, gesamt_fett, gesamt_menge, gesamt_eiweiss, gesamt_kh

    def __mahlzeitAlsZutat(self):
        """Eine Mahlzeit als Zutat in die DB einfuegen.
        
        Berechnet die Naehrwerte pro 100 und fuegt die 
        Mahlzeit als Zutat in die DB ein.
        """
        name = self.__gui.en_name.get()
        if name:
            mahlzeit_neu = Mahlzeit(name, {})
            mahlzeit_neu.addZutatenMitMenge(self.__data_zutaten_mahlzeit)
        
            __, gesamt_fett, gesamt_menge, gesamt_eiweiss, gesamt_kh = self.__getMahlzeitNaehrwert(mahlzeit_neu)
            
            zutat_neu = Zutat(mahlzeit_neu.name, gesamt_fett/gesamt_menge*100, gesamt_eiweiss/gesamt_menge*100, gesamt_kh/gesamt_menge*100)
            self.__dba.insertZutat(zutat_neu)
    
    def __getKCalFuerLetzteTage(self, tage=7):
        ergebnisse=[]
        heute = datetime.today()
        for tagNr in range(0,tage):
            gesucht=heute-timedelta(days=tagNr)
            ergebnis=0
            
            for mahlzeit in self.__data_mahlzeiten:
                if mahlzeit.angelegt.date() == gesucht.date():
                    kcal, __, __, __, __ = self.__getMahlzeitNaehrwert(mahlzeit)
                    ergebnis+=kcal
            ergebnisse.append(ergebnis)
            
        return ergebnisse
                    
    def __updateStats(self):
        kcalZuletzt = self.__getKCalFuerLetzteTage(7)
        kcalZuletzt.reverse()
        # Wir muessen die Liste umdrehen...
        self.__gui.viewStatistics(kcalZuletzt)
        

def setCallback(gui_elem, callback):
    """Hilfsmethode um in einem tkinter GUI-Element einen callback zu setzen"""
    gui_elem.configure(command=callback)
    
def setCallbackListBox(gui_elem, callback):
    """Hilfsmethode um in einem tkinter GUI-Element einen callback zu setzen.
    
    Speziell fuer Listbox-Elemente, da diese keinen command kennen.
    """
    gui_elem.bind("<Double-Button-1>", callback)