'''
Created on 18.08.2013

@author: jannik
'''
from tkinter import Tk, Frame, Listbox, StringVar, Canvas
from tkinter.ttk import Label, Scrollbar, Button, Entry, OptionMenu, Labelframe
from tkinter.constants import GROOVE, VERTICAL, E, SINGLE

class GUI(object):
    '''Stellt die Oberflaeche dar.
    
    Alle steuerden Taetigkeiten werden (sollten) vom
    Controller Objekt uebernommen werden.
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.root = Tk()
        
        self.root.title("DinnerLog")
        self.root.minsize(800, 600)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=3)
        
        # Ein Frame für alles, das mit Zutaten zu tun hat
        self.fr_zutaten = Labelframe(self.root, borderwidth=2, relief=GROOVE, text="Zutaten")
        self.fr_zutaten.grid_columnconfigure(0, weight=1)
        self.fr_zutaten.grid_rowconfigure(0, weight=1)
        self.fr_zutaten.grid(row=0, column=0, sticky="NSWE")
        

        self.lb_zutaten = Listbox(self.fr_zutaten)
        sb_zutaten = Scrollbar(self.lb_zutaten, orient=VERTICAL)
        self.lb_zutaten.configure(yscrollcommand=sb_zutaten.set)
        sb_zutaten.config(command=self.lb_zutaten.yview)
        sb_zutaten.pack(side="right", fill="both")
        self.lb_zutaten.grid(row=0, column=0, sticky="NSEW")
        
        self.__addNeueZutatFrame()    

        # Ein Frame in den alles, das mit Mahlzeiten zu tun hat, kommt
        self.fr_mahlzeit = Labelframe(self.root, borderwidth=2, relief=GROOVE, text="Mahlzeiten")
        self.fr_mahlzeit.grid_columnconfigure(0, weight=1)
        self.fr_mahlzeit.grid_rowconfigure(0, weight=1)
        self.fr_mahlzeit.grid(row=1, column=0, sticky="NSWE")
        
        self.__addNeueMahlzeitFrame()
        

        self.lb_mahlzeiten = Listbox(self.fr_mahlzeit, selectmode=SINGLE)
        sb_mahlzeiten = Scrollbar(self.lb_mahlzeiten, orient=VERTICAL)
        sb_mahlzeiten.configure(command=self.lb_mahlzeiten.yview)
        self.lb_mahlzeiten.configure(yscrollcommand=sb_mahlzeiten.set)
        sb_mahlzeiten.pack(side="right", fill="both")
        self.lb_mahlzeiten.grid(row=0, column=0, sticky="NSEW")
        
        fr_neu_ok = Frame(self.fr_mahlzeit)
        fr_neu_ok.grid(row=1, column=0, columnspan=2, sticky="E")
    
        self.btn_neu = Button(fr_neu_ok, text="Neu")
        self.btn_neu.pack(side="left")
        
        self.btn_mahlzeit_als_zt = Button(fr_neu_ok, text="Als Zutat")
        self.btn_mahlzeit_als_zt.pack(anchor=E, side="right")
        
        self.btn_insert = Button(fr_neu_ok, text="Hinzufuegen")
        self.btn_insert.pack(anchor=E, side="right")
        
        self.btn_update = Button(fr_neu_ok, text="Update")
        self.btn_update.pack(anchor=E, side="right")
        
        self.btn_delete = Button(fr_neu_ok, text="Loeschen")
        self.btn_delete.pack(anchor=E, side="right")
        
        # Ein Frame der Statistiken darstellt
        self.fr_stats = Labelframe(self.root, borderwidth=2, relief=GROOVE, text="Statistik")
        self.fr_stats.grid(row=3, column=0, sticky="NSWE")

        self.statsHeight=80
        self.statsWidth=600
        self.cv_stats = Canvas(self.fr_stats, height=self.statsHeight, width=self.statsWidth)
        self.cv_stats.pack()
        
        # Prozentlinien in Grau
        defaultPadding=2
        for perc in [0, 20, 40, 60, 80, 100]:
            lineStartX, lineStartY = getAbsolutePos(self.statsWidth, self.statsHeight, defaultPadding, 0, perc)
            lineEndX, lineEndY = getAbsolutePos(self.statsWidth, self.statsHeight, defaultPadding, 100, perc)
        
            self.cv_stats.create_line(lineStartX, lineStartY, lineEndX, lineEndY, fill="#AAA")
        
        self.statsLineIDs = []
        
    def __addNeueMahlzeitFrame(self):
        self.fr_neue_mz = Frame(self.fr_mahlzeit)
        self.fr_neue_mz.grid_rowconfigure(2, weight=1)
        self.fr_neue_mz.grid(row=0, column=1, sticky="WSNE")
        
        lbl_name = Label(self.fr_neue_mz, text="Name:")
        lbl_name.grid(row=0, column=0, sticky="NW")
        
        self.en_name = Entry(self.fr_neue_mz)
        self.en_name.grid(row=0, column=1, columnspan=2, sticky="WNE")
        
        lbl_zutat = Label(self.fr_neue_mz, text="Zutaten:")
        lbl_zutat.grid(row=1, column=0, sticky="NW")
        

        self.lb_zutat = Listbox(self.fr_neue_mz)
        sb_zutat = Scrollbar(self.lb_zutat, orient=VERTICAL)
        self.lb_zutat.configure(yscrollcommand=sb_zutat.set)
        sb_zutat.configure(command=self.lb_zutat.yview)
        sb_zutat.pack(side="right", fill="both")
        self.lb_zutat.grid(row=2, column=0, columnspan=3, sticky="NWSE")
        
        self.var_zutat = StringVar(self.fr_neue_mz)
        
        self.opt_zutat = OptionMenu(self.fr_neue_mz, self.var_zutat, "Auswahl")
        self.opt_zutat.grid(row=3, column=0)
        
        self.en_menge = Entry(self.fr_neue_mz)
        self.en_menge.grid(row=3, column=1)
        
        self.btn_mahlzeit_hinzu = Button(self.fr_neue_mz, text="Hinzu")
        self.btn_mahlzeit_hinzu.grid(row=3, column=2, sticky="E")
        
    def __addNeueZutatFrame(self):
        fr_neue_zt = Frame(self.fr_zutaten)
        fr_neue_zt.grid(row=0, column=2,sticky="NWSE")
        
        lbl_name = Label(fr_neue_zt, text="Name:")
        lbl_name.grid(row=0, column=0, sticky="W")
        
        self.en_name_zt = Entry(fr_neue_zt)
        self.en_name_zt.grid(row=0, column=1, columnspan=2, sticky="WE")
        
        lbl_fett = Label(fr_neue_zt, text="Fett:")
        lbl_fett.grid(row=1, column=0, sticky="W")        
        
        self.en_fett = Entry(fr_neue_zt)
        self.en_fett.grid(row=1, column=1, columnspan=2)
        
        lbl_eiweiss = Label(fr_neue_zt, text="Eiweiss:")
        lbl_eiweiss.grid(row=2, column=0, sticky="W")        
        
        self.en_eiweiss = Entry(fr_neue_zt)
        self.en_eiweiss.grid(row=2, column=1, columnspan=2)
        
        lbl_kh = Label(fr_neue_zt, text="Kohlenhy.:")
        lbl_kh.grid(row=3, column=0, sticky="W")        
        
        self.en_kh = Entry(fr_neue_zt)
        self.en_kh.grid(row=3, column=1, columnspan=2)
        
        self.btn_zutat_insert = Button(fr_neue_zt, text="Hinzu")
        self.btn_zutat_insert.grid(row=4, column=1, sticky="E")
        
        self.btn_zutat_update = Button(fr_neue_zt, text="Update")
        self.btn_zutat_update.grid(row=5, column=1, sticky="E")
        
        self.btn_zutat_delete = Button(fr_neue_zt, text="Loeschen")
        self.btn_zutat_delete.grid(row=6, column=1, sticky="E")
        
    def viewStatistics(self, stats=[]):
        """Eine Liste von float oder int-Werten im Statistikpanel anzeigen"""
        # Alte linien loeschen
        for lineID in self.statsLineIDs:
            self.cv_stats.delete(lineID)
        
        # Neue linien zeichnen
        maxEntry=max(stats)+1
        
        defaultPadding=2
        
        startX=10
        stepX=(99-startX)/(len(stats)-1)
        for stat in stats:
            # Prozentuale hoehe, mindesten 1, um etwas anzuzeigen
            relHeight = stat/maxEntry*100.0
            topX,topY = getAbsolutePos(self.statsWidth, self.statsHeight, defaultPadding, startX, relHeight)
            bottomX,bottomY = getAbsolutePos(self.statsWidth, self.statsHeight, defaultPadding, startX, 0)
            if topY == bottomY:
                topY-=1 # Immer mindestens einen Pixel anzeigen
            lineID = self.cv_stats.create_line(bottomX, bottomY, topX, topY, fill="#77C", width=5)
            self.statsLineIDs.append(lineID)
            startX+=stepX
            print(startX)
        
def getAbsolutePos(absWidth,absHeight,absPad,relX,relY):
    """Liefert die absoluten Koordinaten fuer eine relative Eingabe.
    
    Wichtig:! relX=0 und relY=0 entspricht der linken unteren Ecke,
              relX=100 und relY=100 der rechten oberen
    """
    absWidth-=2*absPad
    absHeight-=2*absPad
    
    absX=round(absWidth/100*relX+absPad)
    absY=round(absHeight-(absHeight/100*relY)+absPad)
    
    return absX, absY
