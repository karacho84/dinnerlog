'''
Created on 18.08.2013

@author: jannik
'''
import sqlite3
from zutat import Zutat
from mahlzeit import Mahlzeit

class DBAccess(object):
    '''Uebernimmt den Zugriff auf eine SQLite Datenbank, und versteckt alle direkten Datenbank-Zugriffe.
    
    Dies ist die Model-Klasse kann beobachtet werden, und so alle Zuhoehrer ueber etwaige
    Aenderungen der Daten informieren.
    
    Beispiel:
    >>>dba = DBAccess('meine_db')
    >>>dba.insertMahlzeit(Mahlzeit("Test", {}))
    >>>mz = dba.getMahlzeiten()
    >>>mahlzeit = mz.fetchone()
    >>>print(mahlzeit[0].name)
    Test    
    '''

    def __init__(self, dbname):
        '''Setzt den Datenbanknamen und legt ggf. die Tabellen an.
        
        Prueft ob schon Datenbanktabllen existieren und legt sie ggf an.
        '''
        self.__dbname = dbname
        
        # Zuhoehrer merken
        self.__listeners = []
        
        # Mit der Datenbank verbinden
        conn = sqlite3.connect(self.__dbname, detect_types=sqlite3.PARSE_DECLTYPES)
        
        # Einen cursor holen
        c = conn.cursor()
        
        # Die Tabelle mahlzeiten anlegen, wenn es sie noch nicht gibt
        c.execute("SELECT * FROM sqlite_master WHERE name = 'mahlzeiten' AND type = 'table'")
        exists = False
        for __ in c:
            exists = True
            break
        if exists == False:
            c.execute("CREATE TABLE mahlzeiten (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, angelegt TIMESTAMP);")
                         
        # Die Tabelle zutaten anlegen, wenn es sie noch nicht gibt
        c.execute("SELECT * FROM sqlite_master WHERE name = 'zutaten' AND type = 'table'")
        exists = False
        for __ in c:
            exists = True
            break
        if exists == False:
            c.execute("CREATE TABLE zutaten (name TEXT PRIMARY KEY, fett INTEGER, eiweiss INTEGER, kh INTEGER);")
        
        # Die Tabelle mengen anlegen, wenn es sie noch nicht gibt
        c.execute("SELECT * FROM sqlite_master WHERE name = 'mengen' AND type = 'table'")
        exists = False
        for __ in c:
            exists = True
            break
        if exists == False:
            c.execute("CREATE TABLE mengen (id INTEGER PRIMARY KEY AUTOINCREMENT, mahlzeit_id CONSTRAINT mahlzeit_fkey REFERENCES mahlzeiten (id), zutat_name CONSTRAINT zutat_fkey REFERENCES zutaten (name), menge INTEGER);")
        
        # Verbindung schliessen
        conn.close()
        
    def getMahlzeiten(self):
        """Liefert alle Mahlzeiten mit Zutaten zurueck"""
        # Eine Mahlzeit besteht aus einem Namen und einem
        # Dictionary bestehend aus Zutat und Menge der Zutat
        mahlzeiten = []
        # Mit der Datenbank verbinden
        conn = sqlite3.connect(self.__dbname)
        
        # Einen cursor holen
        c = conn.cursor()
        
        # Die Tabelle Mahlzeit durchsuchen und fuer alle Mahlzeiten
        # die Menge der Zutaten aus der Tabelle menge abrufen,
        # Sowie die Kalorien aus der Tabelle zutaten
        c.execute("SELECT id, name, angelegt FROM mahlzeiten;")
        for mahlzeit in c:
            # Zweiten cursor fuer Zutaten holen
            c2 = conn.cursor()
            c2.execute("SELECT zutat_name, menge FROM mengen WHERE mahlzeit_id = ?;", (mahlzeit[0],))
            mahlzeit_hinzu = Mahlzeit(mahlzeit[1], {}, mahlzeit[2])
            
            # kcal holen
            for menge in c2:
                # Dritten cursor holen
                c3 = conn.cursor()
                c3.execute("SELECT fett, eiweiss, kh FROM zutaten WHERE name = ?;", (menge[0],))
                
                # kcal aus Ergenis holen
                zutat_result = c3.fetchone()
                if zutat_result:
                    mahlzeit_hinzu.zutaten[Zutat(menge[0], zutat_result[0], zutat_result[1], zutat_result[2])] = menge[1]
            
            mahlzeiten.append(mahlzeit_hinzu)
    
        # Verbindung schliessen
        conn.close()
        
        return mahlzeiten
        
        
    def getZutaten(self):
        """Liefert alle Zutaten"""
        zutaten = []
        
        # Mit der Datenbank verbinden
        conn = sqlite3.connect(self.__dbname)
        
        # Einen cursor holen
        c = conn.cursor()
        
        # Die Zutat aus der Datenbank lesen
        c.execute("SELECT name, fett, eiweiss, kh FROM zutaten ORDER BY name;")
        for result in c:
            zutaten.append(Zutat(result[0], result[1], result[2], result[3]))
    
        # Verbindung schliessen
        conn.close()
        
        return zutaten
        
        
    def insertMahlzeit(self, mahlzeit):
        """Fuegt eine Mahlzeit mit ihren Zutaten in die Datenbank ein"""
        # Eine Mahlzeit besteht aus einem Namen und einem
        # Dictionary bestehend aus Zutat und Menge der Zutat
        # Mit der Datenbank verbinden
        conn = sqlite3.connect(self.__dbname)
        
        # Einen cursor holen
        c = conn.cursor()
        
        # Die Mahlzeit in die Tabelle mahlzeit einfuegen, 
        # danach alle Zutaten mit ihrer Menge in die 
        # Tabelle menge eintragen
        mahlzeit_db = (mahlzeit.name, mahlzeit.angelegt)
        c.execute("INSERT INTO mahlzeiten (name, angelegt) VALUES (?, ?);", mahlzeit_db)
        
        # Die ID der Mahlzeit holen, die wir eben angelegt haben
        c.execute("SELECT last_insert_rowid();")
        mahlzeit_id = c.fetchone()
        
        for zutat, menge in mahlzeit.zutaten.items():
            zutat_menge = (mahlzeit_id[0], zutat.name, menge)
            c.execute("INSERT INTO mengen (mahlzeit_id, zutat_name, menge) VALUES (?, ?, ?);", zutat_menge)
            
        
        # Aenderungen speichern
        conn.commit()
    
        # Verbindung schliessen
        conn.close()
        
        # Zuletzt alle Zuhoerer ueber die neuen Daten informieren
        self._notifyListeners()
        
    def updateMahlzeit(self, mahlzeit):
        """Aktualisiert eine Mahlzeit"""
        # Eine Mahlzeit besteht aus einem Namen und einem
        # Dictionary bestehend aus Zutat und Menge der Zutat
        # Mit der Datenbank verbinden
        conn = sqlite3.connect(self.__dbname)
        
        # Einen cursor holen
        c = conn.cursor()
        
        # Die Mahlzeit in die Tabelle mahlzeit einfuegen, 
        # danach alle Zutaten mit ihrer Menge in die 
        # Tabelle menge eintragen
        mahlzeit_db = (mahlzeit.name, mahlzeit.angelegt)
        c.execute("SELECT id FROM mahlzeiten WHERE name=? AND angelegt=?;", mahlzeit_db)
        
        # Die ID der Mahlzeit holen
        mahlzeit_id = c.fetchone()
        
        # Alle Mengen die zu dieser ID in der DB stehen, loeschen
        if mahlzeit_id[0]:
            print("Aktualisiere Mahlzeit mit ID {}".format(mahlzeit_id[0]) )
            c.execute("DELETE FROM mengen WHERE mahlzeit_id=?", (mahlzeit_id[0],))
        
            for zutat, menge in mahlzeit.zutaten.items():
                zutat_menge = (mahlzeit_id[0], zutat.name, menge)
                c.execute("INSERT INTO mengen (mahlzeit_id, zutat_name, menge) VALUES (?, ?, ?);", zutat_menge)
            
        
        # Aenderungen speichern
        conn.commit()
    
        # Verbindung schliessen
        conn.close()
        
        # Zuletzt alle Zuhoerer ueber die neuen Daten informieren
        self._notifyListeners()
        
    def deleteMahlzeit(self, mahlzeit):
        """Loescht eine Mahlzeit"""
        # Eine Mahlzeit besteht aus einem Namen und einem
        # Dictionary bestehend aus Zutat und Menge der Zutat
        # Mit der Datenbank verbinden
        conn = sqlite3.connect(self.__dbname)
        
        # Einen cursor holen
        c = conn.cursor()
        
        # Die Mahlzeit in die Tabelle mahlzeit einfuegen, 
        # danach alle Zutaten mit ihrer Menge in die 
        # Tabelle menge eintragen
        mahlzeit_db = (mahlzeit.name, mahlzeit.angelegt)
        c.execute("SELECT id FROM mahlzeiten WHERE name=? AND angelegt=?;", mahlzeit_db)
        
        # Die ID der Mahlzeit holen
        mahlzeit_id = c.fetchone()
        
        if mahlzeit_id[0]:
            print("Loesche Mahlzeit mit ID {}".format(mahlzeit_id[0]) )
        
            # Alle Mengen die zu dieser ID in der DB stehen, loeschen
            c.execute("DELETE FROM mengen WHERE mahlzeit_id=?", (mahlzeit_id[0],))
        
            # Jetzt auch die Mahlzeit loeschen
            c.execute("DELETE FROM mahlzeiten WHERE id=?", (mahlzeit_id[0],))
        
        # Aenderungen speichern
        conn.commit()
    
        # Verbindung schliessen
        conn.close()
        
        # Zuletzt alle Zuhoerer ueber die neuen Daten informieren
        self._notifyListeners()
        
    def insertZutat(self, zutat):
        """Fuegt eine Zutat in die Datenbank ein"""
        # Mit der Datenbank verbinden
        conn = sqlite3.connect(self.__dbname)
        
        # Einen cursor holen
        c = conn.cursor()
        
        # Die Zutat in die Datenbank einfuegen
        einfuegen = (zutat.name, zutat.fett, zutat.eiweiss, zutat.kh)
        c.execute("INSERT INTO zutaten (name,fett,eiweiss,kh) VALUES (?, ?, ?, ?);", einfuegen)
        
        # Aenderungen speichern
        conn.commit()
    
        # Verbindung schliessen
        conn.close()
        
        # Zuletzt alle Zuhoerer ueber die neuen Daten informieren
        self._notifyListeners()
        
    def updateZutat(self, zutat):
        """Aktualisiert eine Zutat in der Datenbank"""
        # Mit der Datenbank verbinden
        conn = sqlite3.connect(self.__dbname)
        
        # Einen cursor holen
        c = conn.cursor()
        
        # Die Zutat in die Datenbank einfuegen
        einfuegen = (zutat.fett, zutat.eiweiss, zutat.kh, zutat.name)
        c.execute("UPDATE zutaten SET fett=?,eiweiss=?,kh=? WHERE name=?;", einfuegen)
        
        # Aenderungen speichern
        conn.commit()
    
        # Verbindung schliessen
        conn.close()
        
        # Zuletzt alle Zuhoerer ueber die neuen Daten informieren
        self._notifyListeners()
        
    def deleteZutat(self, zutat):
        """Loescht eine Zutat aus der Datenbank"""
        # Mit der Datenbank verbinden
        conn = sqlite3.connect(self.__dbname)
        
        # Einen cursor holen
        c = conn.cursor()
        
        # Die Zutat in die Datenbank einfuegen
        loeschen = (zutat.name,)
        c.execute("DELETE FROM zutaten WHERE name=?;", loeschen)
        
        # Aenderungen speichern
        conn.commit()
    
        # Verbindung schliessen
        conn.close()
        
        # Zuletzt alle Zuhoerer ueber die neuen Daten informieren
        self._notifyListeners()
    
    def _notifyListeners(self):
        for listener in self.__listeners:
            listener.update()
        
    def addListener(self, listener):
        """Fuegt einen Zuhoerer hinzu.
        
        Der Zuhoerer muss eine Methode mit dem Namen update besitzen!
        """
        self.__listeners.append(listener)