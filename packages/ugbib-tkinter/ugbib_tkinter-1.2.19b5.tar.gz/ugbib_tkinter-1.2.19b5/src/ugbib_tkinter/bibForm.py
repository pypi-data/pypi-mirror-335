""" bibForm - Implementiert Formulare u.a. für TkInter

    Namenskonventionen
    
        Klassen
            generell Großbuchstaben
            Bsp: class Modell
            
        Variablen, Attribute, Methoden
            generell Kleinschreibung, bei Bedarf camelCase, d.h. Großbuchstaben
            innen.
            Ausnahmen:
                - aus historischen Gründen, z.B. Attribut glb.DB
                - angepasst an SQL-Bezeichner (s.u.)
            Bsp.: (Modell.)save, getValue(...)
            
        Konstanten
            Üblicherweise nur Großbuchstaben, ggf. mit _ innen, also
            z.B. PSQL_USER
            
        Globales
            in der Klasse glb aus bibGlobal werden häufig Attribute, die sonst
            eher als Konstanten deklariert wären, in deren Schreibweise
            aufgenommen. Z.B. glb.PSQL_HOST
        
        SQL Bezeichner
            Generell Kleinschreibung und innen _
            Bsp.: name, gebdat, kurz_bez
        
        Präfixe für TkInter Widgets
            frm     Frame
            sfr     ScrolledFrame
            ent     Entry
    
    Tips und Tricks
        
        Beachte, dass in tkinter bzw. tkinter.ttk manche Widgets von anderen
        abgeleitet ist, so z.B. ttk.Combobox von ttk.Entry. Das ist bei 
        if-elif-Fallunterscheidungen ein Fallstrick, wenn verschiedene
        Typen von Widgets unterschieden werden sollen. Je nach konkreter
        Anforderung kann man verschiedene Wege gehen:
        
        1. Mit isinstance, dann aber die abgeleiteten Widgets zuerst:
        
              if isinstance(widget, ttk.Combobox):
                  ...
              elif isinstance(widget, ttk.Entry):
                  ...
                  
        2. Mit if - if statt if - elif:
        
              if isinstance(widget, ttk.Entry):
                  ...
              if isinstance(widget, ttk.Combobox):
                  ...
                  
        3. Mit type(...) statt isinstance(...)
        
              if type(widget) == ttk.Combobox:
                  ...
              elif type(widget) == ttk.Entry:
                  ...
                  
"""

#####################################################################
###   Logger herstellen
#####################################################################
import logging #, logging.handlers
logger = logging.getLogger()

try:
    logger.debug('Versuche glbl von __main__ zu importieren')
    from __main__ import glb
except:
    logger.debug('glb wird von ugbib_divers.bibGlobal importiert')
    from ugbib_divers.bibGlobal import glb

from ugbib_werkzeug.bibWerkzeug import checkPythonName

from decimal import Decimal
import datetime
from collections import OrderedDict
import os, sys
import io
import random

import base64
import importlib.resources
import yaml

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
import tkinter.messagebox as dialog

from PIL import Image, ImageTk
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.CRITICAL + 1)

#
# Format Strings für Typumwandlung von date, datetime und time
#
FORMATS_TIME = ('%H:%M',)
FORMATS_DATE = ('%d.%m.%Y', '%Y-%m-%d')
FORMATS_DATETIME = ('%Y-%m-%d %H:%M',)

#
# TRUES, TRUES_SHORT, FALSE - Liste zulässiger String Werte für True.
#
    #         Kleinschreibung reicht, letztlich wird nur der erste Buchstabe
    #         in Kleinschreibung verglichen. Siehe getValue -> Entry -> bool
    #
    #         Wichtig: Das erste Element wird verwendet für die Typumwandlung
    #                  von value --> String
TRUES = [
    'ja',
    'x',
    'yes',
    'true',
    'wahr'
    ]
TRUES_SHORT = [s[0] for s in TRUES]
FALSE = 'nein'

# class Image(tk.Canvas):
#     """Image - Widget zur Anzeige von Bildern
#     
#         Image soll in einer GUI für PostgreSQL-Datenbanken Bilder behandeln. Ähnlich
#         wie z.B. ttk.Entry soll Image
#         
#         1. Bild-Daten aus der Datenbank anzeigen
#         2. Bild-Daten aus einer Datei holen, nötigenfalls aufbereiten, und
#            anzeigen
#         3. Bild-Daten für die Datenbank verfügbar machen. Die Daten sollen
#            im PNG-Format in der Datenbank gespeichert werden.
#         4. NULL-Value soll erlaubt sein. In diesem Fall soll ersatzweise
#            etwas wie "kein Bild vorhanden" angezeigt werden
#         5. Das Widget soll (falls nicht readonly) auf einen Mausklick
#            (linke Maustaste) reagieren und einen Dialog zur
#            Auswahl einer Bild-Datei öffnen. Als Bild-Formate sollen wenigstens
#            PNG und JPG erlaubt sein.
#         6. Das Widget soll optionale Parameter zur Darstellungs-Größe und zur gewünschten
#            Auflösung der Bild-Daten kennen, z.B. xSize, ySize, dpi; mit sinnvollen
#            Default-Werten
#            
#         Parameter
#             xSize         int, x-Ausdehnung des Widgets
#                           Default: 100
#             ySize         int, y-Ausdehnung des Widgets
#                           Default: 141
#             resolution    int, Auflösung der Bild-Daten
#                           Default: None. In diesem Fall soll die Auflösung des
#                           Bildes beibehalten werden, so wie sie aus der
#                           ursprünglichen Bild-Datei war.
#                           Um Speicherplatz und auch Bearbeitungszeig zu
#                           sparen, soll eine resolution angegeben werden
#                           können.
#             readonly      Bilder können zwar angezeigt werden, nicht aber duch
#                           neue Bild-Daten ersetzt werden.
#                           Default: False
#             canSave       Bilder können als Datei gespeichert werden.
#                           Default: False
#         
#         Methoden
#             getValue    holt die Bild-Daten aus dem Widget und gibt sie als
#                         Python byte-String (oder anders?) zurück. In der
#                         PostgreSQL-Datenbank soll dieser Wert als bytea
#                         (PostgreSQL Typ)
#                         (oder anders?) gespeichert werden.
#             setValue    Setzt den Wert des Widgets und zeigt das Bild an.
#                         Diese Methode wird insb. intern verwendet, nachdem
#                         Bild-Daten aus einer Datei geholt wurden.
#             saveValue   Speichert die Bild-Daten als Datei ab.
#         
#         Natürlich sollen setValue und getValue sich genau entsprechen, d.h.
#         self.getValue(self.setValue(data)) == data
#         
#         Zu diskutieren:
#             1. Ist innerhalb von Python byte-String der geeignete Datentyp für
#                Bild-Daten?
#             2. Ist innerhalb von PostgreSQL bytea der geeigntee Datentyp für
#                Bild-Daten?
#             3. Ist tk.Canvas die geeignete Basis-Klasse für Image?
#             4. Reicht das Python-Modul Pillow (PIL) für die nötigen
#                Bild-Manipulationen aus? Dieses Modul ist aus anderen Gründen
#                ohnehin verfügbar, es wäre also wünschenswert, dass nicht ein
#                weiteres Modul geladen werden muss.
#             5. Ist es sinnvoll, nicht das ganze Widget auf Links-Klick
#                reagieren zu lassen, um ein neues Bild aus einer Datei zu holen,
#                sondern stattdessen am unteren Rand des Widgets einen eigenen
#                Button für diesen Zweck zu haben, z.B. mit dem Text
#                "Neues Bild" oder einem hübschen Icon? Das würde vor allem
#                erlauben, ggf. einen "Save"-Button daneben zu platzieren.
#             6. Ist es sinnvoll, Bilder im PNG-Format zu speichern? Ich habe es
#                gewählt, damit es ohne Qualitätsverlust funktioniert.
#     """
#     def __init__(self, *args, xSize=100, ySize=141, resolution=None, readonly=False, canSave=False, **nargs):
#         super().__init__(*args, **nargs)
#         self.xSize = xSize
#         self.ySize = ySize
#         self.resolution = resolution
#         self.readonly = readonly
#         self.canSave = canSave
#         ...
#     
#     def getValue(self):
#         """getValue - Gibt die Bild-Daten des Widgets im PNG-Format zurück
#         
#             getValue gibt die Bild-Daten des Widgets im PNG-Format zurück.
#             Das Ergebnis soll entweder als Datei gespeichert
#             (z.B. image.png) oder an die PostgreSQL-Datenbank übergeben
#             werden können.
#         """
#         ...
#     
#     def setValue(self, imageData):
#         """setValue - Setzt den Wert des Widgets auf imageData und zeigt das Bild an
#         
#             setValue bekommt PNG-Daten (entweder aus einer Datei oder aus der
#             PostgreSQL-Datenbank) und zeigt das Bild im Widget an. Die Daten
#             müssen so erhalten bleiben, dass getValue später genau diese Daten
#             zurück gibt.
#             
#             Parameter
#                 imageData
#         """
#         ...
#     
#     def saveValue(self, imagePath):
#         """saveValue - Speichet das Bild als Datei
#         
#             saveValue speichert die Bild-Daten als Datei. Dabei wird vorausgesetzt,
#             dass die Daten im PNG-Format vorliegen.
#             
#             imagePath wird in der Regel Ergebnis eines Datei-Name-Dialoges von
#             TkInter sein. Es wird entweder eine vorhandene zu überschreibende
#             oder eine neue Datei sein.
#             
#             Aus der Datei-Endung soll sich das Format der Bild-Datei ergeben:
#                 jpg, jpeg     JPEG
#                 png           PNG
#                 eventuell weitere übliche, kann aber eingeschränkt sein.
#             
#             Parameter
#                 imagePath   Pfad (relativ oder absolut), unter dem die Daten
#                             gespeichert werden sollen.
#                             Beispiele:
#                                 Portrait.png
#                                 Bilder/Portrait.jpg
#                                 /home/ulrich/Bilder/Portrait.jpeg
#         """
#         ...

class CopyPaste():
    """CopyPaste - Erweitert Text- und Entry-Widgets um Copy/Paste Funktionalität
    
        CopyPaste erweitert ttt.Entry und tk.Text um die üblichen Funktionen für
        Copy und Paste:
        
        Hot-Keys:
            Ctrl-A    Select All im Widget
            Ctrl-C    Copy markierten Text ins Clipboard kopieren
            Ctrl-X    Move markierten Text ins Clipboard (d.h. markierten
                      Text ins Clipboard und im Widget löschen)
            Ctrl-V    Paste Text aus dem Clipboard an der Cursorposition in das
                      Widget einfügen.
                      
        Als (erwünschten) Nebeneffekt triggern Ctrl-X und Ctrl-V iWasChanged.
    """
    def __init__(self, widget, form=None):
        self.widget = widget
        self.form = form
        self.add_bindings(widget)

    def add_bindings(self, widget):
        widget.bind("<Control-c>", self.copy)
        widget.bind("<Control-x>", self.cut)
        widget.bind("<Control-v>", self.paste)
        widget.bind("<Control-a>", self.selectAll)

    def copy(self, event):
        widget = event.widget
        if isinstance(widget, tk.Entry) or isinstance(widget, tk.Text):
            try:
                widget.clipboard_clear()
                widget.clipboard_append(widget.selection_get())
            except tk.TclError:
                pass

    def cut(self, event):
        widget = event.widget
        if isinstance(widget, tk.Entry) or isinstance(widget, tk.Text):
            try:
                widget.clipboard_clear()
                widget.clipboard_append(widget.selection_get())
                widget.delete("sel.first", "sel.last")
                if self.form:
                    self.form.iWasChanged()
            except tk.TclError:
                pass

    def paste(self, event):
        widget = event.widget
        if isinstance(widget, tk.Entry) or isinstance(widget, tk.Text):
            try:
                text = widget.selection_get(selection='CLIPBOARD')
            except tk.TclError:
                return
            widget.insert(tk.INSERT, text)
            if self.form:
                self.form.iWasChanged()
            return 'break'  # Prevent the default paste behavior
    
    def selectAll(self, event):
        widget = event.widget
        if isinstance(widget, tk.Entry):
            widget.select_range(0, tk.END)
        elif isinstance(widget, tk.Text):
            widget.tag_add(tk.SEL, "1.0", tk.END)
        widget.focus()
        return 'break'  # Prevent the default behavior

class CtxBase(object):
    """CtxBase - Basisklasse für Frames u.a. als Kontextmanager"""
    def __init__(self, parent, bez='', *args, **kwargs):
        self.bez = bez
        if not hasattr(parent, '_children'):
            parent._children = []
        parent._children.append(self)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(f"Error occurred: {exc_value}")
        return False  # Re-raise exceptions if any

    @staticmethod
    def get_widget_structure(widget, indent=0):
        widgetBez = f' -- Bez: {widget.bez}' if hasattr(widget, 'bez') else ''
        result = '    ' * indent + str(widget) + widgetBez + '\n'
        if hasattr(widget, '_children'):
            for child in widget._children:
                result += CtxBase.get_widget_structure(child, indent+1)
        return result
    
    @staticmethod
    def get_line_to_root(widget):
        result = []
        while widget is not None:
            widgetBez = f' (Bez: {widget.bez})' if hasattr(widget, 'bez') else ''
            result.append(str(widget) + widgetBez)
            parentName = widget.winfo_parent()
            widget = widget.nametowidget(parentName) if parentName else None
        return ' --> '.join(result[::-1])

class CtxFrame(ttk.Frame, CtxBase):
    """CtxFrame - ttk.Frame als Kontextmanager"""
    def __init__(self, parent, *args, bez='', **kwargs):
        super().__init__(parent, *args, **kwargs)
        CtxBase.__init__(self, parent, bez)

class CtxLabelFrame(ttk.LabelFrame, CtxBase):
    """CtxLabelFrame - ttk.LabelFrame als Kontextmanager"""
    def __init__(self, parent, *args, bez='', **kwargs):
        super().__init__(parent, *args, **kwargs)
        CtxBase.__init__(self, parent, bez)

class CtxPanedWindow(ttk.PanedWindow, CtxBase):
    """CtxPanedWindow - ttk.PanedWindow als Kontextmanager"""
    def __init__(self, parent, *args, bez='', **kwargs):
        super().__init__(parent, *args, **kwargs)
        CtxBase.__init__(self, parent, bez)

class CtxNotebook(ttk.Notebook, CtxBase):
    """CtxNotebook - ttk.Notebook als Kontextmanager"""
    def __init__(self, parent, *args, bez='', **kwargs):
        super().__init__(parent, *args, **kwargs)
        CtxBase.__init__(self, parent, bez)

class CtxCanvas(tk.Canvas, CtxBase):
    """CtxCanvas - tk.Canvas als Kontextmanager"""
    def __init__(self, parent, *args, bez='', **kwargs):
        super().__init__(parent, *args, **kwargs)
        CtxBase.__init__(self, parent, bez)

class CtxToplevel(tk.Toplevel, CtxBase):
    """CtxToplevel - tk.Toplevel als Kontextmanager"""
    def __init__(self, parent, *args, bez='', **kwargs):
        super().__init__(parent, *args, **kwargs)
        CtxBase.__init__(self, parent, bez)

class CtxMenu(tk.Menu, CtxBase):
    """CtxMenu - tk.Menu als Kontextmanager"""
    def __init__(self, parent, *args, bez='', **kwargs):
        super().__init__(parent, *args, **kwargs)
        CtxBase.__init__(self, parent, bez)

class CtxTreeview(ttk.Treeview, CtxBase):
    """CtxTreeview - ttk.Treeview als Kontextmanager"""
    def __init__(self, parent, *args, bez='', **kwargs):
        super().__init__(parent, *args, **kwargs)
        CtxBase.__init__(self, parent, bez)

class FilterEntry(ttk.Entry):
    def __init__(self, parent, *args, callback=None, delay=500, **nargs):
        super().__init__(parent, *args, **nargs)
        self.callback = callback
        self.delay = delay
        self.filterTimeout = None
        self.bind('<KeyRelease>', self.onKeyRelease)
        CopyPaste(self)
    
    def onKeyRelease(self, event):
        if self.filterTimeout is not None:
            self.after_cancel(self.filterTimeout)
        self.filterTimeout = self.after(self.delay, self.triggerCallback)
    
    def triggerCallback(self):
        if self.callback:
            self.callback(self.get())

class ButtonWithEnter(ttk.Button):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.bind('<Return>', lambda e: self.invoke())

class Tooltip():
    """Tooltip - Erzeugt einen Tooltip für ein beliebiges Tkinter Widget
    """
    def __init__(self, wdg, text):
        """
        Initialisiert den Tooltip
        
        Parameter:
            wdg     Das Tkinter Widget, für das der Tooltip erstellt werden soll
            text    Der anzuzeigende Text
        
        Verwendung z.B.
            btn = ttk.Button(...)
            Tooltip(btn, 'Aktion sowieso ausführen')
        """
        self.wdg = wdg
        self.text = text
        self.tooltip = None
        self.after_id = None  # Initialisierung
        
        # Binde Maus-Events
        self.wdg.bind('<Enter>', self.showTooltip)
        self.wdg.bind('<Leave>', self.hideTooltip)
    
        # Binde zusätzliche Events für Tastatureingaben
        self.wdg.bind('<Return>', self.hideTooltip, add='+')  # Tooltip bei Return ausblenden
        self.wdg.bind('<FocusOut>', self.hideTooltip, add='+')  # Tooltip bei Fokusverlust ausblenden

    def showTooltip(self, event=None):
        """Zeigt den Tooltip nach kurzer Verzögerung"""
        if self.tooltip is None and self.after_id is None:  # Verhindert mehrfaches Erstellen
            self.after_id = self.wdg.after(250, self._create_tooltip)  # 500ms Verzögerung
    
    def _create_tooltip(self):
        """Erstellt den Tooltip"""
        if self.tooltip is not None:
            return  # Tooltip existiert bereits

        x = self.wdg.winfo_rootx() + self.wdg.winfo_width() + 10
        y = self.wdg.winfo_rooty() + 10
        
        self.tooltip = tk.Toplevel(self.wdg)
        self.tooltip.wm_overrideredirect(True)
        
        label = tk.Label(self.tooltip, text=self.text,
                         justify=tk.LEFT,
                         background="#ffffe0",
                         relief=tk.SOLID,
                         borderwidth=1,
                         font=("TkDefaultFont", "8", "normal"))
        label.pack()
        
        self.tooltip.wm_geometry(f"+{x}+{y}")
        self.after_id = None  # Timer wurde ausgeführt
    
    def hideTooltip(self, event=None):
        """Versteckt den Tooltip und stoppt den Timer"""
        if self.after_id is not None:
            try:
                self.wdg.after_cancel(self.after_id)
            except ValueError:
                pass  # Fehler vermeiden, falls after_id ungültig ist
            self.after_id = None
            
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class TkIcons():
    """TkIcons - Stellt Icons im Format ImageTk.PhotoImage zur Verfügung
    
        Die Icons werden in verschiedenen Größen verfügbar gemacht:
            16x16   Originalgröße
            14x14   Verkleinert für die Anwendung im Navi
    
        Zugriff auf die Icons gibt es auf zweierlei Weise:
        
            Über den "bereinigten Dateinamen". D.h wenn ein Icon unter
                /usr/share/icons/oxygen/base/16x16/apps/preferences-system-bluetooth.png
            gespeichert ist, so ist der "bereinigte Dateiname"
                apps/preferences-system-bluetooth
        
        Zugriff über hier vergebene Namen
            Der Einfachheit/Lesbarkeit halber können hier weitere Namen für Icons vergeben werden.
            Das geschieht in dem Klassen Attribut _iconNames, das ein Dict ist, das diese Namen auf
            die "bereinigten Dateinamen" abbildet. Soll z.B. das icon
                /usr/share/icons/oxygen/base/16x16/actions/document-save-as.png
            auch unter dem Namen save verfügbar sein, muss _iconNames
                'save': 'actions/document-save-as'
            enthalten.
        
        TkIcons wird einmal Instanziiert, i.d.R. mit
            glb.icons = TkIcons()
        Dann sind die Icons global verfügbar über...
        
            über die Methode glb.icons.getIcon(name, size=0), die als ersten Parameter
            den "bereinigten Dateinamen" oder den neu vergebenen Namen bekommt und als
            zweiten Parameter die gewünschte Größe des Icons.
    """
    
    _iconShortCuts = {
        'oxygen': {
            'check':            'checkmark',
            'connect':          'network-connect',
            'copy':             'edit-copy',
            'database':         'server-database',
            'delete':           'edit-delete',
            'disconnect':       'network-disconnect',
            'emptyform':        'edit-clear-list',
            'icon-not-found':   'kalarm',
            'pdf':              'application-pdf',
            'quit':             'gtk-quit',
            'refresh':          'view-refresh',
            'save':             'document-save-as',
            'save-clear':       'document-save',
            'send':             'mail-send',
            'undo':             'edit-undo',
            },
        'breeze': {
            'check':            'checkmark',
            'connect':          'network-connect',
            'copy':             'edit-copy',
            'database':         'server-database',
            'disconnect':       'network-disconnect',
            'delete':           'edit-delete',
            'emptyform':        'edit-clear-all',
            'icon-not-found':   'emblem-question',
            'pdf':              'application-pdf',
            'quit':             'gtk-quit',
            'refresh':          'view-refresh',
            'save':             'document-save-as',
            'save-clear':       'document-save',
            'send':             'mail-send',
            'undo':             'edit-undo',
            }
        }
    
    def __init__(self):
        #
        # Icon Cache initialisieren
        self._iconCache = {}
        #
        # Icons aus Icons.yaml holen, soweit vorhanden
        with open('Icons.yaml', 'r') as f:
            self.iconsAsStrings = yaml.safe_load(f)
        #
        # Konsistenz der Icons Shortcuts prüfen
        for themeLinks in self._iconShortCuts:
            # gibt es rechts alle ShortCuts, die es links gibt?
            for themeRechts in self._iconShortCuts:
                if themeRechts != themeLinks:
                    for shortcut in self._iconShortCuts[themeLinks]:
                        if not shortcut in self._iconShortCuts[themeRechts]:
                            logger.warning(f'Für {themeRechts} fehlt Shortcut {shortcut}.')
            # gibt es für jedes shortcut das zugehörige Icon?
            for iconName in self._iconShortCuts[themeLinks].values():
                if not iconName in self.iconsAsStrings[themeLinks]:
                    logger.warning(f'Icon {iconName} nicht vorhanden.')
    
    def getIconNames(self, theme=None):
        if theme is None:
            theme = glb.ICON_THEME
        return [iconName for iconName in self.iconsAsStrings[theme]]
    
    def getThemes(self):
        return [theme for theme in self.iconsAsStrings]
    
    def getIcon(self, iconName, size=0, theme=None):
        """getIcon - gibt Icon in der gewünschten Größe zurück
        
            Parameter
                iconName    entweder Dateiname (ohne Pfad) aus dem Themes
                            oder Name aus _iconShortCuts
                size        Gewünschte Größe des Icons.
                            Möglich ist entweder
                                0 (Default), was die Originalgröße bedeutet, oder
                                ## (z.B. 14, was die Größe in Pixeln bedeutet
                            Siehe zu size weiter unten.
                            
            Zur Größe (size) der Icons:
                Während der Programmierung bin ich von einer Originalgröße von 16x16
                Pixeln ausgegangen. Diese Größe ist eine der vorhandenen Größen der
                Oxygen-Icons und der Umfang bei dieser Größe ist sehr hoch. Da die Größe
                16 auch bei Breeze-Icons vorhanden und sehr umfangreich ist, habe ich auch
                dafür diese Größe als Default genommen. Das schlägt sich nieder in dem
                kleinen Programm iconstoyaml.py, das eine Auswahl von icons aus den
                beiden Themes (Oxygen und Breeze) lädt.
                Alle anderen Größen werden bei Bedarf durch Vergrößerung bzw. Verkleinerung
                auf die gewünschte Größe hergestellt.
        """
        #
        # Neue Implementation
        if theme is None:
            theme = glb.ICON_THEME
        # Fallback, falls iconName nicht zu finden ist
        if iconName not in self.iconsAsStrings[theme] and iconName not in self._iconShortCuts[theme]:
            iconName = 'icon-not-found'
        # Ist iconName ein Shortcut?
        if iconName in self._iconShortCuts[theme]:
            iconName = self._iconShortCuts[theme][iconName]
        #
        cacheKey = (iconName, theme, size)
        if cacheKey in self._iconCache:
            return self._iconCache[cacheKey]
        
        image = self._loadEmbeddedIcon(iconName, theme)
        
        if size:
            image = image.resize((size, size), Image.Resampling.LANCZOS)
        
        photoImage = ImageTk.PhotoImage(image)
        self._iconCache[cacheKey] = photoImage
        return photoImage
            
        #
        # Größe klären
        if size == '':
            icons = self.icons
        elif size == 'small':
            icons = self.icons_small
        else:
            raise ValueError(f'Ungültige Icon-Größe: {size=}')
        #
        # Icon ausliefern
        return icons[iconName]
    
    def _loadEmbeddedIcon(self, iconName, theme=None):
        if theme is None:
            # glb.ICON_THEME ist zur Zeit der Definition der Fkt noch nicht
            # bekannt. Daher wird glb.ICON_THEME nicht als Default in den
            # Fkt Kopf geschrieben.
            theme = glb.ICON_THEME
        iconAsString = self.iconsAsStrings[theme][iconName]
        iconData = base64.b64decode(iconAsString)
        return Image.open(io.BytesIO(iconData))

class Notify(scrolledtext.ScrolledText):
    """_Notify - Widget zum Anzeigen von Nachrichten
    
        Notify dient v.a. für Rückmeldungen an den User. Es ist ein ScrolledText
        Widget, das mit den Methoden unten Nachrichten an den User geben kann.
        Gedacht ist dabei an Infos, Warnungen, Fehlermeldungen usw.
        
        Notify kann ein- oder mehrfach instanziiert und entsprechend oft
        in der GUI gepackt werden. Allerdings werden die Nachrichten immer
        gleichlautend in allen Instanzen angezeigt.
        
        Klassenattribute
            notifies      Liste der Instanzen
        
        Methoden
            notify    
            
    """
    notifies = []
    arten = {
        'Info':     {'foreground': 'blue'},
        'Hinweis':  {'foreground': 'brown'},
        'Erfolg':   {'foreground': 'green'},
        'Warnung':  {'foreground': 'orange'},
        'Fehler':   {'foreground': 'red'},
        }
    
    def __init__(self, parent):
        super().__init__(parent, height=3, wrap=tk.WORD)
        #
        # Setze Widget auf "inaktiv"
        self['takefocus'] = 0
        #
        # Konfiguriere Tags für die verschiedenen Nachrichtenarten
        for art, format in self.arten.items():
            self.tag_configure(art, **format)
        #
        # Standardformatierung für das gesamte Widget
        self.configure(font=('TkDefaultFont', 8))
        #
        # Widget merken (es könnten ja mehrere sein)
        __class__.notifies.append(self)
    
    @staticmethod
    def notify(nachricht, art='Info'):
        """notify - Zeigt die Nachricht in der Art art in allen Notify Instanzen
        
            notify zeigt die Nachricht am Ende aller Notify Instanzen. Dabei wird
            die Nachricht abhängig von art hervorgehoben.
            
            ACHTUNG: art ist noch nicht implementiert, d.h. es gibt noch keine
            differenzierte Hervorhebung.
            
            Parameter
                nachricht     Die zu zeigende Nachricht
                              Type: str
                art           Ein Wert aus __class__.arten
                              Abhängig davon wird die Nachricht hervorgehoben.
                              Default: 'Info', d.h. neutrale/keine Formatierung
        """
        #
        # Ist art zulässig?
        if art not in __class__.arten:
            raise ValueError(f'{art=} unzulässig.')
        #
        # Zeige nachricht in allen notifies
        for wdg in __class__.notifies:
            jetzt = datetime.datetime.now().strftime('%H:%M:%S')
            # Pos des Einfügepunktes merken
            start_pos = wdg.index('end-1c')
            # Text einsetzen
            wdg.insert(tk.END, f'\n{jetzt}: {str(nachricht)}')
            # Berechne End-Position
            end_pos = wdg.index('end-1c')
            # Entferne alle existierenden Tags von der neuen Nachricht
            for tag in wdg.tag_names():
                wdg.tag_remove(tag, start_pos, end_pos)
            # Tag von der Startpos bis zum Ende setzen
            wdg.tag_add(art, start_pos, end_pos)
            wdg.yview_moveto(1.0)
            # Sofortige Aktualisierung der GUI erzwingen
            wdg.update_idletasks()

def notify(nachricht, art='Info'):
    """notify - Zeigt nachricht in allen Instanzen von Notify
    
        Parameter
            nachricht         Die zu zeigende Nachricht
                              Type: str
            art               Ein Wert aus Notify.arten
                              Abhängig davon wird die Nachricht hervorgehoben.
                              Default: 'Info', d.h. neutrale/keine Formatierung
    """
    Notify.notify(nachricht, art)

class Fortschritt(ttk.Progressbar):
    """Fortschritt - Zeigt Fortschritt an
    
        Fortschritt ist ein Widget, abgeleitet von ttk.Progressbar, das eine erweiterte
        Funktionalität hat. Insb. soll der Max-Wert dynamisch gesetzt werden können.
        
        Initialisierung
            Genau wie ttk.Progressbar, so dass es mit Fortschritt.pack/grid in die
            GUI eingebaut werden kann.
            Fragen:
                Wie entscheidet sich, ob das Widget horizontal oder vertikal gezeigt wird?
                Wie kann man die Höhe/Breite angeben?
        
        Minimum/Maximum
            Der Minimum-Wert soll statisch 0 sein.
            Der Maximum-Wert soll dynamisch sein und mit der Methode setMax(max: int)
                festgelegt werden können.
        
        Start/Stop/Update
            Mit der Methode start() soll die Anzeige gestartet werden.
            Mit der Methode stop() soll die Anzeige gestoppt werden.
            Mit der Methode step() (oder anders genannt, um Konflikt
                mit ttk.Progressbar.step() zu vermeiden.
            Mit der Methode update(value: int) soll der aktuelle Wert gesetzt werden. Wird
                nur benötigt, wenn aus besonderen Gründen der Fortschritt auf einen
                bestimmten Wert gesetzt werden muss. Normalerweise wäre step() zu
                bevorzugen.
            Mit der Methode getValue() soll der aktuelle Wert abgefragt werden können.
                Wird vermutlich nur für Debugging-Zwecke eingesetzt
            Fragen:
                Sollten zusätzlich Methoden aktivate() bzw. deactivate() definiert werden,
                    die das Widget sichtbar/unsichtbar bzw. voll/ausgegraut machen? Mir scheint
                    dass könnte von start/stop mit erledigt werden.
        
        Verwendung z.B.
            Für einen Mail-Versand, in dem 5, 25 oder 250 (oder jede andere Anzahl von Mails)
            verschickt werden, soll der Fortschritt angezeigt werden.
            
            fortschritt = Fortschritt(parent, orient=HORIZONTAL, width=40)
            fortschritt.pack(...)
            
            mailList = someFuncion(...)     # liefert E-Mail-Adressen
            
            fortschritt.setMax = len(mailList)
            fortschritt.start()
            
            for address in mailList:
                fortschritt.step()
                sendMail(address)
            
            fortschritt.stop()
    """
    def __init__(self, parent, orient=tk.HORIZONTAL, **kwargs):
        """Initialisiert den Fortschrittsbalken mit dynamischer Größe."""
        super().__init__(parent, orient=orient, **kwargs)
        self.maxValue = None
        self.value = 0

    def setMax(self, maxValue: int):
        """Setzt den maximalen Fortschrittswert."""
        if maxValue <= 0:
            raise ValueError('Max-Wert muss größer als 0 sein.')
        self.maxValue = maxValue
        self.configure(maximum=maxValue)

    def start(self, maxValue=None):
        """Startet den Fortschritt, optional mit neuem Max-Wert."""
        if maxValue:
            self.setMax(maxValue)
        if self.maxValue is None:
            raise RuntimeError('Kein Max-Wert gesetzt.')
        self.value = 0
        self.configure(value=self.value)
        self.update_idletasks()

    def stop(self):
        """Stoppt und setzt den Fortschritt zurück."""
        self.maxValue = None
        self.value = 0
        self.configure(value=0)
        self.update_idletasks()

    def step(self):
        """Erhöht den Fortschritt um 1 Schritt."""
        if self.maxValue is None:
            raise RuntimeError('Fortschritt wurde nicht gestartet.')
        if self.value >= self.maxValue:
            raise ValueError('Max-Wert überschritten.')
        self.value += 1
        self.configure(value=self.value)
        self.update_idletasks()

    def update(self, value: int):
        """Setzt den Fortschritt auf einen bestimmten Wert."""
        if self.maxValue is None:
            raise RuntimeError('Fortschritt wurde nicht gestartet.')
        if not (0 <= value <= self.maxValue):
            raise ValueError(f'Wert {value} außerhalb des Bereichs 0-{self.maxValue}.')
        self.value = value
        self.configure(value=self.value)
        self.update_idletasks()

    def getValue(self):
        """Gibt den aktuellen Fortschrittswert zurück."""
        return self.value

class BearbVonAm(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        ttk.Label(self, text='Bearb. von', font=(None, 6)).grid(column=0, row=0, sticky=tk.W)
        ttk.Label(self, text='am', font=(None, 6)).grid(column=1, row=0, sticky=tk.W)
        ttk.Label(self, text='auto.', font=(None, 6)).grid(column=2, row=0, sticky=tk.W)
        self.entBearbVon = ttk.Entry(self, width=15, state=tk.DISABLED, font=(None, 6))
        self.entBearbAm = ttk.Entry(self, width=15, state=tk.DISABLED, font=(None, 6))
        self.entBearbAuto = ttk.Entry(self, width=15, state=tk.DISABLED, font=(None, 6))
        self.entBearbVon.grid(column=0, row=1, sticky=tk.W)
        self.entBearbAm.grid(column=1, row=1, sticky=tk.W)
        self.entBearbAuto.grid(column=2, row=1, sticky=tk.W)

    def connectToForm(self, form):
        """
        """
        form.addWidget(
            'bearb_von',
            self.entBearbVon,
            'text')
        form.addWidget(
            'bearb_am',
            self.entBearbAm,
            'datetime')
        form.addWidget(
            'bearb_auto',
            self.entBearbAuto,
            'datetime')

class DialogHilfeNaviButtons(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.lblTitel = ttk.Label(self, text='Die Navi Buttons')
        self.lblTitel.grid(row=0, column=0, columnspan=3)
        
        ttk.Label(self, image=glb.icons.getIcon('emptyform')).grid(row=1, column=0)
        ttk.Label(self, text='Formular leeren für neuen Datensatz').grid(
                    row=1,
                    column=1,
                    sticky=tk.W,
                    padx=5)
        ttk.Label(self, text='Strg-N').grid(row=1, column=2, sticky=tk.W)
        
        ttk.Label(self, image=glb.icons.getIcon('save')).grid(row=2, column=0)
        ttk.Label(self, text='Daten sichern und weiter bearbeiten').grid(
                    row=2,
                    column=1,
                    sticky=tk.W,
                    padx=5)
        
        ttk.Label(self, image=glb.icons.getIcon('save-clear')).grid(row=3, column=0)
        ttk.Label(self, text='Daten sichern').grid(
                    row=3,
                    column=1,
                    sticky=tk.W,
                    padx=5)
        ttk.Label(self, text='Strg-S').grid(row=3, column=2, sticky=tk.W)
        
        ttk.Label(self, image=glb.icons.getIcon('delete')).grid(row=4, column=0)
        ttk.Label(self, text='Datensatz löschen').grid(
                    row=4,
                    column=1,
                    sticky=tk.W,
                    padx=5)
        ttk.Label(self, text='Strg-D').grid(row=4, column=2, sticky=tk.W)
        
        ttk.Label(self, image=glb.icons.getIcon('refresh')).grid(row=5, column=0)
        ttk.Label(self, text='Auswahlliste neu aufbauen').grid(
                    row=5,
                    column=1,
                    sticky=tk.W,
                    padx=5)
        
        ttk.Label(self, image=glb.icons.getIcon('undo')).grid(row=6, column=0)
        ttk.Label(self, text='Änderungen verwerfen').grid(
                    row=6,
                    column=1,
                    sticky=tk.W,
                    padx=5)
        
        ttk.Label(self, image=glb.icons.getIcon('copy')).grid(row=7, column=0)
        ttk.Label(self, text='Kopie des Datensatzes anlegen').grid(
                    row=7,
                    column=1,
                    sticky=tk.W,
                    padx=5)
        
        self.btnOk = ttk.Button(
                self,
                text='OK',
                command=lambda: self.destroy()
                )
        self.btnOk.grid(row=8, column=0, columnspan=2)

class DialogLogin(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.lblTitel = ttk.Label(self, text='Login')
        self.lblTitel.grid(row=0, column=0, columnspan=2)
        
        self.lblErfolg = ttk.Label(self, text='Daten eingeben:')
        self.lblErfolg.grid(row=1, column=0, columnspan=2)
        
        self.lblBenutzer = ttk.Label(self, text='Benutzername:')
        self.lblBenutzer.grid(row=2, column=0, sticky=tk.E)
        
        self.lblPassword = ttk.Label(self, text='Passwort:')
        self.lblPassword.grid(row=3, column=0, sticky=tk.E)
        
        self.user = tk.StringVar()
        self.user.set(glb.PSQL_USER)
        self.entBenutzer = ttk.Entry(self, textvariable=self.user)
        self.entBenutzer.grid(row=2, column=1, sticky=tk.W)
        
        self.password = tk.StringVar()
        self.password.set(glb.PSQL_PASSWORD)
        self.entPassword = ttk.Entry(self, textvariable=self.password, show='*')
        self.entPassword.grid(row=3, column=1, sticky=tk.W)
        
        self.btnQuit = ttk.Button(
                self,
                text='Abbrechen',
                command=sys.exit
                )
        self.btnQuit.grid(row=4, column=0)
        
        self.btnLogin = ttk.Button(
                self,
                text='Login',
                command=self.setLoginDaten
                )
        self.btnLogin.grid(row=4, column=1)
    
    def setLoginDaten(self):
        glb.setvalue('PSQL_USER', self.user.get())
        glb.setvalue('PSQL_PASSWORD', self.password.get())
        self.destroy()

class DialogGemeindeAuswahl(tk.Toplevel):
    def __init__(self, parent, auswahl=[]):
        super().__init__(parent)
        self.parent = parent
        self.lblTitel = ttk.Label(self, text='Gemeinde auswählen')
        self.lblTitel.pack(side=tk.TOP)
        
        self.frmChoices = FrameScrolledListboxValueLabel(self)
        self.frmChoices.pack(side=tk.TOP)
        for (value, label) in auswahl:
            self.frmChoices.append(value, label)
        
        self.frmButtons = ttk.Frame(self)
        self.frmButtons.pack(side=tk.TOP)
        
        self.btnQuit = ttk.Button(
                self.frmButtons,
                text='Abbrechen',
                command=lambda: self.destroy
                )
        self.btnQuit.pack(side=tk.LEFT)
        
        self.btnGo = ttk.Button(
                self.frmButtons,
                text='OK',
                command=self.handleOK
                )
        self.btnGo.pack(side=tk.LEFT)
    
    def handleOK(self):
        glb.setvalue('schema', self.frmChoices.getValue())
        self.destroy()

class yScrolledFrame(ttk.Frame):
    """yScrolledFrame - Simuliert Frame mit senkrechtem Scrollbalken
    
        Tatsächlich kann Frame nicht mit Scrollbar. Vgl. dazu
        https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter
        Gelöst wird das durch ein ttk.Canvas, das zusammen mit einem Scrollbar in den
        äußersen Frame (= self) gepackt wird. In das ttk.Canvals kommt dann schließlich der
        Frame (= innerFrame), in den die Anwendung Widgets aller Art stecken kann (grid oder pack).
        Aus der zizierten Quelle stammt auch der Code von self.onFrameConfigure als
        Event-Handler für <Configure> von dem inneren Frame. Ganz verstehe ich dessen
        Notwendigkeit nicht...
        
        Parameter
            Wie ttk.Frame
            
        Attribute
            innerFrame    ttk.Frame, in den die Anwendung Widgets packen kann.
            canvas        Das tk.Canvas, in den innerFrame eingebaut wird
            yScrollbar    Der zugehörige Scrollbalken
        
        Anwendung z.B.
            scrolledFrame = yScrolledFrame(main)
            ttk.Label(scrolledFrame.innerFrame, text='Label im ScrolledFrame').pack()
                      ------------------------
                      ^
                      Nicht scrolledFrame!
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Style für den äußeren Frame
        style = ttk.Style()
        style.configure('UF.TFrame', borderwidth=2)
        self.config(style='UF.TFrame')
        
        # Canvas und Scrollbar
        self.canvas = tk.Canvas(self, borderwidth=2, relief=tk.GROOVE)
        self.yScrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.config(yscrollcommand=self.yScrollbar.set)
        
        # Layout
        self.canvas.pack(side=tk.LEFT, anchor=tk.W, fill=tk.BOTH, expand=True)
        self.yScrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Innerer Frame im Canvas
        self.innerFrame = ttk.Frame(self.canvas)
        self.inner_window = self.canvas.create_window(0, 0, window=self.innerFrame, anchor=tk.NW)
        
        # Scrollregion und Breitenanpassung
        self.innerFrame.bind('<Configure>', self.onFrameConfigure)
        self.canvas.bind('<Configure>', self.onCanvasConfigure)
    
    def onFrameConfigure(self, event):
        """Aktualisiert die Scrollregion basierend auf der Größe des inneren Frames."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def onCanvasConfigure(self, event):
        """Passt die Breite des inneren Frames an die Breite des Canvas an."""
        canvas_width = event.width
        self.canvas.itemconfig(self.inner_window, width=canvas_width)

class xScrolledFrame(ttk.Frame):
    """xScrolledFrame - Simuliert Frame mit waagerechtem Scrollbalken
    
        Tatsächlich kann Frame nicht mit Scrollbar. Vgl. dazu
        https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter
        Gelöst wird das durch ein ttk.Canvas, das zusammen mit einem Scrollbar in den
        äußersen Frame (= self) gepackt wird. In das ttk.Canvals kommt dann schließlich der
        Frame (= innerFrame), in den die Anwendung Widgets aller Art stecken kann (grid oder pack).
        Aus der zizierten Quelle stammt auch der Code von self.onFrameConfigure als
        Event-Handler für <Configure> von dem inneren Frame. Ganz verstehe ich dessen
        Notwendigkeit nicht...
        
        Parameter
            Wie ttk.Frame
            
        Attribute
            innerFrame    ttk.Frame, in den die Anwendung Widgets packen kann.
            canvas        Das tk.Canvas, in den innerFrame eingebaut wird
            xScrollbar    Der zugehörige Scrollbalken
        
        Anwendung z.B.
            scrolledFrame = xScrolledFrame(main)
            ttk.Label(scrolledFrame.innerFrame, text='Label im ScrolledFrame').pack()
                      ------------------------
                      ^
                      Nicht scrolledFrame!
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #
        # build canvas and scrollbars and pack it into (outer) frame (self)
        self.canvas = tk.Canvas(
            self,
            borderwidth=2,
            relief=tk.GROOVE)
        self.xScrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        self.canvas.config(xscrollcommand=self.xScrollbar.set)
        
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.xScrollbar.pack(side=tk.TOP, fill=tk.X, expand=True)
        #
        # build (internal) Frame and Scrollbars and put it into canvas
        self.innerFrame = ttk.Frame(self.canvas)
        self.canvas.create_window(0, 0, window=self.innerFrame, anchor=tk.NW, tags='self.innerFrame')
        #
        #
        self.innerFrame.bind('<Configure>', self.onFrameConfigure)
    
    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))

class ComboboxValueLabel(ttk.Combobox):
    """ComboboxValueLabelFilter - Erweitert Combobox um Value/Label Paare
    
        ttk.Combobox lässt eine Auswahl aus Strings zu. Wir möchten aber
        Value/Label-Paare bereitstellen, z.B.
        
            Value     | Label
            ==========+==================
            m         | männlich
            w         | weiblich
            d         | divers
            ?         | nicht angegeben
            
        Dabei sollen für die Value-Werte auch andere Typen, z.B. Int, zugelassen
        sein.
        
        Die Funktionalität von ttk.Combobox soll im Übrigen erhalten bleiben -
        mit einer Ausnahme: Die direkte Eingabe von Werten soll nicht möglich sein,
        nur Werte aus den Value/Label-Paaren sollen zugelassen sein. Das erreichen
        wir mit dem state 'readonly'.
        
        Beachte die Sprachverwirrung: Was in der Combobox letztlich angezeigt wird,
        steht in der Liste Combobox.values - das sind aber die Label aus unseren
        Value/Label-Paaren.
        
        None/'' als Value: Sollte vermieden werden, ist aber
        prinzipiell möglich. Klar, beides kann als (jeweils) ein Value in den
        Value/Label-Paaren vorkommen. Die Probleme entstehen aber, solange der
        Benutzer noch keinen Wert ausgewählt hat. In diesem Fall ist schwer zu
        unterscheiden, ob eben noch kein Wert ausgewählt wurde oder ob '' gemeint ist.
        
        Parameter
            Wie ttk.Combobox, wird ohne weitere Verarbeitung direkt weiter gereicht.
            Allerdings hat der Parameter values keinerlei Auswirkungen, da
            die Steuerung von values indirekt und (nur) über Methoden erfolgt.
            Ebenso bleibt der Parameter textvariable wirkungslos, da er mit einer
            neuen, internen Variable überschrieben wird.
        
            noneAllowed (bool): Ob None als Auswahlmöglichkeit erlaubt ist.
            
            noneLabel (str): Label, der für den Wert None gezeigt werden soll.
            
            filterEnabled (bool): Ob die Filterung der Labels durch Benutzereingabe aktiviert ist.
        
        Attribute
            _lv         Dict Label --> Value
                        Bildet Label auf Value ab. Das mag verwirrend erscheinen.
                        Wir können aber annehmen, dass die Label eindeutig sind.
                        Und über den Index ist später der Label leicht zugänglich,
                        s.d. über das Dict _lv der Value ermittel werden kann.
            _cv         Control Variable, die den aktuellen Wert (Label in unserer
                        Terminologie) hält.
    """
    def __init__(self, *args, noneAllowed=False, noneLabel='-', filterEnabled=False, **kwargs):
        super().__init__(*args, **kwargs)
        # to disable strange behaviour
        # see https://stackoverflow.com/questions/756662/how-to-select-at-the-same-time-from-two-listbox
        self.config(exportselection=0)
        #
        # Parameter merken
        self.noneAllowed = noneAllowed
        self.noneLabel = noneLabel
        self.filterEnabled = filterEnabled
        #
        # Die Combobox soll, wenn None nicht erlaubt ist, nur über DropDown bedient werden:
        if not self.filterEnabled:
            self.state(('readonly',))
        else:
            self.bind('<space>', self._filterLabels)
            self.bind('<FocusOut>', lambda event: self._validateSelection(event), add='+')
            self.bind('<<ComboboxSelected>>', self._unfilterLabels)
        #
        # Die Control Variable
        self._cv = tk.StringVar()
        self.config(textvariable=self._cv)
        #
        # Das Dict für die Value/Label-Paare (tatsächlich bilden wir Label --> Value ab!)
        self._lv = OrderedDict()
        #
        # Für den Fall, dass values als Parameter übergeben wurde, löschen wir die Liste
        self.clear()
        #
        # Falls None erlaubt, None-pair als erstes Element einfügen
        if self.noneAllowed:
            self.append(None, self.noneLabel)
    
    def clear(self):
        """clear - Löscht die Liste der Value/Label-Paare
        """
        self.config(values=[])
        while self._lv:
            self._lv.popitem()
    
    def append(self, value, label=None):
        """append - Hängt ein Value/Label-Paar ans Ende der Liste
        
            Parameter
                value     Wert in der Auswahlliste
                label     Angezeigter Label
                          Default: None. In diesem Fall wird als label str(value) gesetzt
        """
        if label:
            l = label
        else:
            l = str(value)
        if l in self._lv:
            # Label nicht eindeutig
            raise ValueError(f'Label {l} ist nicht eindeutig.')
        if value in self._lv.values():
            # Value nicht eindeutig
            raise ValueError(f'Value {value} ist nicht eindeutig.')
        self._lv[l] = value
        self._updateDisplayValues()
        
    def fill(self, pairs):
        """fill - Füllt die Auswahlliste neu mit pairs
        
            Leert die Auswahlliste und füllt sie dann neu mit den value/label
            Paaren aus pairs
            
            Parameter
                pairs   Liste/Tupel aus value/label Paaren
        """
        self.clear()
        if self.noneAllowed:
            self.append(None, self.noneLabel)
        for (value, label) in pairs:
            self.append(value, label)
    
    def setValue(self, value):
        """setValue - Wählt value in der Liste aus
        
            Parameter
                value   Dieser Wert wird ausgewählt, muss folglich einer der values
                        in der Liste der Value/Label-Paare sein
        """
        logger.debug(self._lv.values())
        if value not in self._lv.values():
            if value is None:
                try:
                    self.current(0)
                except:
                    pass
            else:
                raise ValueError(f'Der Wert {value} kommt in der Combobox nicht vor.')
                
        for label, val in self._lv.items():
            if val == value:
                self._cv.set(label)
                break
    
    def getValue(self):
        """getValue - Gibt den ausgewählten Wert zurück
        """
        return self._lv.get(self._cv.get(), None)

    def _filterLabels(self, event):
        """_filterLabels - Filtert die Labels basierend auf der Benutzereingabe"""
        searchText = self._cv.get().lower()
        filteredLabels = [label for label in self._lv if searchText in label.lower()]
        self.config(values=filteredLabels)
        self.event_generate('<Down>')
    
    def _unfilterLabels(self, event):
        self._updateDisplayValues()

    def _validateSelection(self, event):
        """_validateSelection - Stellt sicher, dass ein gültiger Wert ausgewählt wird"""
        if self._cv.get() not in self._lv:
            self._cv.set('')

    def _updateDisplayValues(self):
        """_updateDisplayValues - Aktualisiert die angezeigten Labels"""
        self.config(values=list(self._lv.keys()))
        
class ListboxValueLabel(tk.Listbox):
    """ListboxValueLabel - Erweitert Listbox um unabhängige Value/Label-Paare
    
        tk.Listbox hält immer eine Liste von String-Werten, aus denen ausgewählt
        werden kann. Wir möchten aber Value/Label-Paare bearbeiten, d.h. z.B.
        
            Value  | Label
            =======+===============
            m      | männlich
            w      | weiblich
            d      | divers
            ?      | nicht angegeben
        
        In der ListboxValueLabel sollen die Label angezeigt werden, als Wert soll
        der zugehörige Value herausgegeben werden.
        
        Die Funktionalität von Listbox soll ansonsten erhalten bleiben.
        
        Über selectmode kann eingestellt werden, ob ein Wert oder mehrere
        Werte ausgewählt werden können. Zwei Methoden liefern entsprechend
        sinnvolle Ergebnisse:
            getValues   Liefert eine Liste der ausgewählten Werte
            getValue    Liefert den ersten ausgewählten Wert oder None,
                        wenn kein Wert ausgewählt ist.
                        Das ist v.a. (und wohl nur) dann sinnvoll,
                        wenn nur ein Wert ausgewählt werden darf.
        
        Parameter
            Wie tk.Listbox, wird ohne weitere Verarbeitung direkt weiter
            gereicht.
        
        Attribute
            _lv     Dict Label --> Value
                    Bildet Label auf Value ab. Das mag verwirrend erscheinen.
                    Wir können aber annehmen, dass die Label eindeutig sind.
                    Und über den Index ist später der Label leicht zugänglich,
                    s.d. über das Dict _lv der Value ermittel werden kann.
    """
  
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # to disable strange behaviour
        # see https://stackoverflow.com/questions/756662/how-to-select-at-the-same-time-from-two-listbox
        self.config(exportselection=0)
        #
        self._lv = OrderedDict()
    
    def clear(self):
        """clear - Löscht die Auswahlliste
        """
        self.delete(0, tk.END)
        while self._lv:
            self._lv.popitem()
    
    def append(self, value, label=None):
        """append - Hängt ein value/label Paar ans Ende der Auswahlliste an
        """
        if label:
            l = label
        else:
            l = str(value).capitalize()
        if l in self._lv:
            logger.warning(f'Label {l} nicht eindeutig.')
            notify(
                f'ACHTUNG: Label {l} nicht eindeutig. Bitte Programmierer verständigen!',
                art='Fehler')
        else:
            self.insert(tk.END, l)
            self._lv[l] = value
    
    def fill(self, pairs):
        """fill - Füllt die Auswahlliste neu mit pairs
        
            Leert die Auswahlliste und füllt sie dann neu mit den value/label
            Paaren aus pairs
            
            Parameter
                pairs   Liste/Tupel aus value/label Paaren
        """
        self.clear()
        for (value, label) in pairs:
            self.append(value, label)
    
    def clearValue(self):
        """clearValue - Alle Elemente werden abgewählt
        """
        self.selection_clear(0, tk.END)
    
    def setValues(self, values):
        """setValues - Wählt genau die Werte aus values in der Liste aus
        
            setValues wählt genau die Werte aus values in der Liste aus.
        
            Parameter
                values    Tupel oder Liste von Werten
        """
        if not type(values) in (tuple, list):
            raise TypeError('values muss tuple oder list sein, ist aber {}'.type(values))
        self.clearValue()
        for value in values:
            self.setValue(value, exclusive=False)
    
    def setValue(self, value, exclusive=False):
        """setValue - Wählt value in der Liste aus (select)
        
            Parameter
                value       Dieser Wert wird ausgewählt
                            Typ: Typ des Widgets
                exclusive   Wenn True, werden alle anderen Auswahlen gelöscht.
                            Andernfalls bleiben alle anderen Auswahlen unverändert.
        """
        if value is None:
            self.clearValue()
            return
        if exclusive:
            self.clearValue()
        index = 0
        for label in self._lv.keys():
            if self._lv[label] == value:
                self.selection_set(index)
            index += 1
    
    def getValues(self):
        """getValues - Liefert Liste der ausgewählten Werte
        """
        return [self._lv[self.get(index)] for index in self.curselection()]
    
    def getValue(self):
        """getValue - Liefert den ersten der ausgewählten Werte
        
            Das ist v.a. dann hilfreich, wenn nur ein Wert ausgewählt werden
            darf.
        """
        values = self.getValues()
        if len(values) > 0:
            return values[0]
        else:
            return None

class FrameScrolledListbox(ttk.Frame):
    """FrameScrolledListbox - Frame mit enthaltener Listbox
    
        Frame, der eine einfache tk.Listbox enthält. Außerdem einen Scrollbalken.
        Als Werte kommen hier nur Strings infrage.
        
        Argumente
            wie tk.Listbox
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # build Control Variable
        self.listvariable = tk.StringVar()
        self.listvariable.set('')
        # build Listbox and Scrollbar. To prevent Listbox strange behaviour
        # see https://stackoverflow.com/questions/756662/how-to-select-at-the-same-time-from-two-listbox
        self.Listbox = tk.Listbox(self, listvariable=self.listvariable, exportselection=0)
        self.Scrollbar = ttk.Scrollbar(self)
        # configure these two
        self.Listbox.config(yscrollcommand=self.Scrollbar.set)
        self.Scrollbar.config(command=self.Listbox.yview)
        # pack them in Frame
        self.Listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.Scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH)
    
    def clear(self):
        """clear - Löscht die Auswahlliste
        """
        self.Listbox.delect(0, tk.END)
    
    def append(self, value):
        """append - Hängt einen Value ans Ende der Auswahlliste
        """
        if not type(value) == str:
            raise TypeError(f'Value muss Type str haben hat aber {type(value)}.')
        self.Listbox.insert(tk.END, value)
    
    def clearValue(self):
        """clearValue - Alle Elemente werden abgewählt
        """
        self.Listbox.selection_clear(0, tk.END)
    
    def setValues(self, values):
        """setValues - Wählt venau die Werte aus values in der Liste aus
        
            Parameter
                values    Tupel oder Liste von Werten (str)
        """
        if not type(values) in (tuple, list):
            raise TypeError('values muss tuple oder list sein, ist aber {}'.type(values))
        self.clearValue()
        for value in values:
            if not type(value) == str:
                raise TypeError(f'Value muss Type str haben hat aber {type(value)}.')
            self.setValue(value, exclusive=False)
    
    def setValue(self, value, exclusive=False):
        """setValue - Wählt value in der Liste aus (select)
        
            Parameter
                value       Dieser Wert wird ausgewählt
                            Typ: String oder None
                exclusive   Wenn True, werden alle anderen Auswahlen gelöscht.
                            Andernfalls bleiben alle anderen Auswahlen unverändert.
        """
        if type(value) in (list, tuple):
            self.setValues(value)
            return
        if value is None:
            self.clearValue()
            return
        if exclusive:
            self.clearValue()
        values = self.Listbox.get(0, tk.END)
        if not value in values:
            raise ValueError(f'{value=} ist nicht in der Auswahlliste.')
        index = values.index(value)
        self.Listbox.selection_set(index)
    
    def getValues(self):
        """getValues - Liefert Liste der ausgewählten Werte
        """
        return [self.Listbox.get(index) for index in self.Listbox.curselection()]
    
    def getValue(self):
        """getValue - Liefert den ersten der ausgewählten Werte
        
            Das ist v.a. dann hilfreich, wenn nur ein Wert ausgewählt werden
            darf.
        """
        values = self.getValues()
        if len(values) > 0:
            return values[0]
        else:
            return None

class FrameScrolledListboxValueLabel(ttk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #
        # build Listbox and Scrollbar
        self.Listbox = ListboxValueLabel(self)
        self.Scrollbar = ttk.Scrollbar(self)
        #
        # configure these two
        self.Listbox.config(yscrollcommand=self.Scrollbar.set)
        self.Scrollbar.config(command=self.Listbox.yview)
        #
        # pack them in Frame
        self.Listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.Scrollbar.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    
    def clear(self):
        self.Listbox.clear()
    
    def append(self, value, label=None):
        self.Listbox.append(value=value, label=label)
    
    def fill(self, pairs):
        self.Listbox.fill(pairs)
    
    def clearValue(self):
        self.Listbox.clearValue()
    
    def setValues(self, values):
        if not type(values) in (tuple, list):
            raise TypeError('values muss tuple oder list sein, ist aber {}'.type(values))
        self.clearValue()
        for value in values:
            self.Listbox.setValue(value=value, exclusive=False)
    
    def setValue(self, value, exclusive=False):
        self.Listbox.setValue(value=value, exclusive=exclusive)
    
    def getValues(self):
        return self.Listbox.getValues()
    
    def getValue(self):
        return self.Listbox.getValue()

class Validator():
    """Validator - Validatoren und Factories für Validatoren
    
        Validator wird nicht instanziiert. Stattdessen werden die benötigten
        Klassenmethoden in der TkInter Anwendung als Validatoren registriert
        und über den dort zurückgegebenen Namen referenziert.
        
        Vgl. Doku von TkInter, z.B.
        https://anzeljg.github.io/rin2/book2/2405/docs/tkinter/entry-validation.html
        
        Beachte insb., dass Validatoren immer an Entry bzw. Combobox Widgets
        gehängt werden. D.h. das Argument für die Validatoren ist immer str.
        Soll also z.B. eine Typenprüfung durchgeführt werden, wirt tatsächlich
        geprüft, ob sich der übergebene String in diesen Typen konvertieren
        lässt.
        
        Bsp.:
            import Validator as V
            valInt = widget.register(V.valInt)
            Entry(widget, validate='all', validatecommand=(valInt, '%P'))
        
        Alle Validatoren akzeptieren jeweils einen String Wert value,
        der geprüft wird.
        
        Alle Validatoren liefern True für value == ''. Wie letztlich ''
        interpretiert wird (None oder leerer String), und ob ggf. None
        zulässig ist, muss an anderer Stelle geklärt werden, i.d.R. beim
        Abspeichern in die DB.
        
        Factories für Validatoren
        =========================
        
        Neben den eigentlichen Validatoren werden auch drei Factories für
        Validatoren implementiert. Zwei davon verknüpfen beliebig viele Validatoren
        per and bzw. or. Die Dritte negiert einen Validator.
        So können z.B. die Validatoren valInt
        und valPositiv zu valPositivInt kombiniert werden.
        
        Diese Factories können nicht nur die hier bereitgestellten Validatoren
        kombinieren, sondern auch andere Funktionen, die z.B. von der Anwendung
        bereitgestellt werden. Denkbar wäre die Prüfung, ob ein value ein 
        Datum ist (valDate) und ob es innerhalb eines bestimmten Zeitraums liegt
    """
    def valInt(value):
        """valInt - True <-> int(value) erfolgreich oder value == ''
        """
        if value == '':
            return True
        try:
            int(value)
        except:
            return False
        return True
    
    def valFloat(value):
        """valFloat - True <-> float(value) erfolgreich oder value == ''
        """
        if value == '':
            return True
        try:
            float(value)
        except:
            return False
        return True

    def valDecimal(value):
        """valDecimal - True <-> Decimal(value) erfolgreich oder value == ''
        
            Anmerkung
                baut auf decimal.Decimal auf
        """
        if value == '':
            return True
        try:
            Decimal(value)
        except:
            return False
        return True
    
    def valBool(value):
        """valBool - True <--> value[0] in TRUES_SHORT
        """
        if value == '':
            return True
        else:
            return value[0].lower() in TRUES_SHORT
    
    def valDate(value):
        """valDate - True <--> value gültiges Datum oder leer
        """
        if value == '':
            return True
        for formatString in FORMATS_DATE:
            try:
                datetime.datetime.strptime(value, formatString)
                return True
            except:
                pass
        return False

    def valDatetime(value):
        """valDatetime - True <--> value gültiges Datum+Zeit oder leer
        """
        if value == '':
            return True
        for formatString in FORMATS_DATETIME:
            try:
                datetime.datetime.strptime(value, formatString)
                return True
            except:
                pass
        return False

    def valTime(value):
        """valTime - True <--> value gültige Zeit oder leer
        """
        if value == '':
            return True
        for formatString in FORMATS_TIME:
            try:
                datetime.datetime.strptime(value, formatString)
                return True
            except:
                pass
        return False
    
    def valFactoryAnd(*vals):
        """valFactoryAnd - Verknüpft Validatoren mit and
        
            ValFactoryAnd kombiniert eine Reihe von Validatoren und liefert
            einen neuen Validator, der genau dann True liefert, wenn alle
            übergebenen Validatoren True liefern.
            
            Dabei werden die übergebenen Validatoren in deren Reihenfolge
            aufgerufen. Diese Prüfung wird abgebrochen, nachdem die erste
            Prüfung False ergibt.
            
            Damit können Validatoren aufgebaut werden, die z.B. zuerst eine
            Typenprüfung vornehmen und anschließend noch Wertebereiche.
            Bsp.: valNumPositiv prüft erst, ob der Wert numerisch ist und
                  anschließend, ob er auch positiv ist.
        """
        
        def validator(x):
            for f in vals:
                if not f(x):
                    return False
            return True
        
        return validator
    
    def valFactoryOr(*vals):
        """valFactoryAnd - Verknüpft Validatoren mit aor
        
            ValFactoryAnd kombiniert eine Reihe von Validatoren und liefert
            einen neuen Validator, der genau dann True liefert, wenn mindestens
            einer der übergebenen Validatoren True liefert.
            
            Dabei werden die übergebenen Validatoren in deren Reihenfolge
            aufgerufen. Diese Prüfung wird abgebrochen, nachdem die erste
            Prüfung True ergibt.
        """
        
        def validator(x):
            for f in vals:
                if f(x):
                    return True
            return False
        
        return validator
    
    def valFactoryNot(val):
        """valFactoryNot - Liefert negierten Validator
        """
        
        def validator(x):
            return not val(x)
        
        return validator
    
    valNum = valFactoryOr(valInt, valFloat, valDecimal)
    valPositiv = valFactoryAnd(valNum, lambda x: float(x)>0)
    

class Form():
    """Form - Basisklasse für Formulare
    
    
        =======================================================================
        Grundsätzliches
        =======================================================================
        
        1. Formulare, also Instanzen von Ableitungen von Form, sind im
        Wesentlichen Sammlungen von TkInter Widgets oder selbst gebauten Widgets.
        Diese Sammlung von Widgets werden die Attribute der Instanz sein.
        Selbst gebaute Widgets können z.B. Listen von Checkbuttons innerhalb
        eines tk.Text Widgets, oder ein ergänztes tk.Listbox Widget.
        
        2. Jedes dieser Widgets gehört in aller Regel zu einer Spalte
        einer DB-Tabelle. Selbst wenn das nicht so ist, hat in aller Regel
        jedes Widget genau einen Wert, ist also kein zusammengesetztes Widget
        mit z.B. mehreren Entry Widgets.
        
        3. a) Zu jedem Widget wird ein passendes Label-Widget erzeugt. Optional
        kann dieses Label-Widget bereits beim Hinzufügen des Widgets
        fertig mitgegeben werden.
        
        4. Combobox und ähnliche Widgets können mit Werten z.B. aus der DB
        gefüllt werden. In diesem Fall setzt man mit setGetterAuswahl für das
        Widget eine Funktion, die solche Werte liefert.
        Natürlich kann als Getter auch ein Funktion übergeben werden, die nicht aus
        der DB, sondern aus einer anderen Quelle Werte liefert. 
        Um sie tatsächlich auszuführen, gibt es die Methoden updateSelect und
        updateSelects, die i.d.R. vom Navi aufgerufen werden.
        Es gibt aber auch die staticmethod resetForms, die (u.a.) für jedes
        hergestellte Formular updateSelects aufruft und so alle relevanten
        Felder mit den Werten versorgt.
        
        5. Es gibt einen Indicator für geänderte Daten. Einzelheiten siehe unten.
        
        
        =======================================================================
        Namenskonventionen
        =======================================================================
        
        Damit die Sachen am Ende auseinanderzuhalten sind, gilt folgende
        Namenskonvention für Attribute der Instanzen:
            
            Widgets             Wie Spalte in der DB-Tabelle
                                Falls unabhängig von einer DB-Tabelle, dann
                                frei wählbar, allerdings ohne Unterstrich
                                am Anfang.
                                In keinem Fall darf das Abbtribut mit
                                lbl_ beginnen (vgl. Label-Widgets)
                                Bsp.: self.id         Zu Spalte .. in DB-Tabelle
                                      self.name       "
                                      self.plz        "
                                      self.username   Ohne Bezug auf DB-Tabelle
            Label-Widgets       Beginnt immer mit lbl_, dann folgt das
                                Attribut des zugehörigen Widgets.
                                Bsp.: self.lbl_id
                                      self.lbl_name
                                      self.lbl_plz
                                Daher dürfen die Widget-Attribute nicht mit
                                lbl_ beginnen.
            Weitere Attribute   Alle weiteren Attribute beginnen mit
                                (mindestens) einem Unterstrich.
                                Bsp.: _id       ID des Formulars
                                      _typ      Dict für Typen der Widgets
                                      _navi     Navi für das Formular
        
        Die gleiche Namenskonvention soll ggf. für Properties gelten. Tatsächlich
        sollten alle Properties mit einem Unterstrich beginnen, da Properties
        nach den obigen Regeln weder Widgets noch Label-Widgets halten werden.
        
        Generell sollten Methoden mit einem Kleinbuchstaben beginnen und
        mindestens einen Großbuchstaben enthalten, z.B. addWidget, getWidgets usw.
        Da meine Datenbanken durchgehend Spaltenbezeichnungen aus Kleinbuchstaben
        und Unterstrichen enthalten (by the way: PostgreSQL keywords und namen sind
        case-insensitiv), werden so Namenskonflikte vermieden.
        
        Diese Namenskonvention ermöglicht es u.a.,
            1. die Liste der Widgets zu liefern,
            2. die Liste der Label-Widgets zu liefern,
            3. die Label-Widgets und Widgets
               eindeutig einander zuzuordnen.
        
        
        =======================================================================
        Bearbeitung der Widgets/Attribute
        =======================================================================
        
        Die Widgets und Label-Widgets, also die "normalen"
        Attribute, werden
        ausschließlich durch Methoden hinzugefügt. Späteres Überschreiben
        oder Hinzufügen eines Widgets mit einem schon verwendeten Namen
        ist nicht erlaubt.
        
        
        =======================================================================
        Label-Widgets zu den Widgets
        =======================================================================
        
        Zu jedem Widget, dass hinzugefügt wird, wird automatisch ein
        Label-Widget erzeugt und hinzugefügt. Dieses Label-Widget kann optional
        auch vorher erzeugt und beim Hinzufügen des Widgets mitgegeben werden.
        
        
        =======================================================================
        Schnittstelle zu den Widgets
        =======================================================================
        
        Eine einheitliche Schnittstelle für die Werte der Widgets
        wird über Methoden wie den folgenden hergestellt:
            getValue(colName)
            setValue(colName, value)
            clearValue(colName)
        Diese Methoden müssen
            1. selbst erkennen, um welche Art von Widget es sich handelt
               (TkInter Entry, Listbox usw.)
            2. je nach Typ (_typ) des Widgets/Feldes die Typenkonvertierung
               vornehmen.
        
        
        =======================================================================
        Implementierung als Kontext-Manager
        =======================================================================
        
        Wir implementieren Form als Kontext-Manager. Das machen wir
        eigentlich nur, um bei der Verwendung eine bessere Lesbarkeit zu
        erreichen. Der Aufruf kann so erfolgen:
            
            with Form(...) as Form_Person:
                ...
            with Form(...) as Form_Familie:
                ...
        
        Üblicherweise sind die Definitionen, die dann innerhalb des Kontextes
        auftauchen, sehr zahlreich. Dass das als Kontext möglich ist, erlaubt
        die Einrückung im Editor.
        
        Tatsächlich macht der Kontext-Manager nichts (vgl. __enter__ und
        __exit__). Das macht einen einfachen Aufruf möglich, ohne
        Funktionalität einzubüßen. Später könnten in __enter__ und/oder
        __exit__ relevante Dinge definiert werden.
        
        
        =======================================================================
        Indicator für geänderte Daten im Formular
        =======================================================================
        
        Widgets, mit denen Daten geändert werden können, geben an Form
        eine "Rückmeldung", sobald ihre Daten geändert sind. Form seinerseits
        gibt sich selbst den Status "geändert" (d.h. self._changed = True) und
        gibt eine Nachricht an das Navi (falls vorhanden). Navi schließlich
        zeigt einen optischen Indicator, s.d. der User darauf aufmerksam
        gemacht wird, dass wohl noch geänderte Daten gespeichert werden
        sollten. Umgekehrt
        
        Bestimmte Aktionen, z.B. Save, Anzeige neuer Daten, Leeren des
        Formulars u.ä., setzen den Indicator zurück.
        
        Optional kann später noch implementiert werden, dass, falls noch
        geänderte Daten im Formular sind, bestimmte Aktionen nur mit
        zusätzlicher Bestätigung durchgeführt werden können, um versehentlichen
        Verlust von Ändreungen zu verhindern.
        
        
        =======================================================================
        Auflistung der Eigenschaften
        =======================================================================
        
        Parameter
            remember    Nur wenn remember=True (Default), wird die erzeugte Instanz in __class__.FORMS
                        gespeichert.
                        Dieser Parameter wurde eingeführt, damit insb. Form Instanzen, die für
                        Listenansichten von einer Factory erzeugt werden, von __class__.FORMS
                        ausgeschlossen werden können. Hintergrund ist die Klassenmethode
                        resetForms, die sonst auch über alle diese Instanzen iteriert, was
                        1. überhaupt nicht sinnvoll ist und 2. extrem viel Zeit braucht.
        
        Klassen-Attribute
            TYPES           Liste der zulässigen Typen der Widget-Werte
                            z.B. ['text', 'int', ...]
        
        Attribute
            _navi           Ggf. Navi für das Formular (vgl. Klasse Navi)
            _types          Dict mit Zuordnungen colName: typ
            _colNames       List aller colName, also damit auch 
                            Widget-Namen (maßgebliche Reihenfolge)
            _getterAuswahl  Dict colName -> getterAuswahl
            _changed        True, wenn Daten im Formular geändert bzw. neu
                            eingegeben wurden.
        
        Static Methods
            resetForms          
        
        Methoden
            __enter__           Für den Kontext-Manager
            __exit__            "
            addWidget           Fügt ein Widget hinzu
            colType             Liefert type vom einem Widget
            getValue            Liefert value des Widgets, aber mit konvertiertem Type
            setValue            Setzt value des Widgets, aber aus konvertiertem Type
            clearValue          Löscht value des Widgets, d.h. setzt value = ''
            getValues           Liefert Dict der Werte aller Widgets
            setValues           Setzt die Werte aller Widgets
            clearValues         Löscht values aller Widgets
            updateSelect        
            updateSelects
            setGetterAuswahl    setzt GetterAuswahl für ein Widget. Diese Getter
                                sind dafür gedacht, später Auswahlen für
                                Select o.a. Widgets zu liefern.
    """
    #
    # Klassen-Attribute
    #
    
    # TYPES - Liste zulässiger Typen der Widgets
    TYPES = [
        'text',             # Einfacher Text (str)
        'int',              # Integer
        'float',            # Float (Fließkomma mit begrenzter Genauigkeit)
        'decimal',          # Decimal (Fließkomma mit ungebrenzter Genauigkeit)
                            # Python-Standardbibliothek decimal.Decimal
        'bool',             # Boolean, ggf. zuzgl. None ('Tristate')
        'datetime',         # datetime.datetime
        'date',             # datetime.date
        'time',             # datetime.time
        ]
    
    # FORMS - Liste aller Instanzen von Form
    FORMS = []
        
    def __init__(self, remember=True):
        self._navi = None
        self._types = {}
        self._colNames = []
        self._controlVars = {}
        self._getterAuswahl = {}
        self._changed = False
        #
        # ggf. neue Instanz merken
        self.remember = remember
        if self.remember:
            __class__.FORMS.append(self)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
    def __repr__(self):
        return f'Form mit Widgets für {self._colNames}'
    
    def setNavi(self, navi):
        """setNavi - Setzt das navi für das Formular
        
            Setzt das Navi für das Formular und informiert das Navi
            über das Formular
        
            Parameter
                navi    Navi für das Formualar
        """
        self._navi = navi
        self._navi.form = self
    
    def getNavi(self):
        """getNavi - Gibt das Navi des Widgets zurück
        
            Ergebnis
                Das Navi des Widgets
                None, falls nicht gesetzt
        """
        return self._navi
    
    def getType(self, colName):
        """getType - Gibt den Typ des Widgets zu colName zurück
        
            Parameter
                colName   Name des Widgets bzw. der Spalte aus der DB
        """
        return self._types[colName]
    
    def getColNames(self):
        """getColNames - Gibt Liste der colNames zurück
        """
        return self._colNames
    
    def existsColName(self, colName):
        """existsColName - True, wenn zu colName ein Widget existiert
        
            Parameter
                colName   Name des Widgets bzw. der Spalte aus der DB
            
            Ergebnis
                True      Wenn es ein Widget zu colName gibt
                False     Sonst
        """
        return colName in self._colNames
    
    def getWidget(self, colName):
        """getWidget - Gibt Widget zu colName zurück
        
            Parameter
                colName   Name des Widgets bzw. der Spalte aus der DB
        """
        if self.existsColName(colName):
            return getattr(self, colName)
        else:
            raise ValueError(f'Col Name {colName} existiert nicht.')
    
    def getWidgets(self):
        """getWidgets - Gibt Liste aller Widgets zurück
        
            Ergebnis
                Liste aller "normalen" Widgets (also ohne die Label Widgets)
        """
        return [self.getWidget(colName) for colName in self.getColNames()]
    
    def getLabel(self, colName):
        """getLabel - Gibt Label Widget zu colName
        
            Parameter
                colName   Name des Widgets bzw. der Spalte aus der DB
        """
        if self.existsColName(colName):
            return getattr(self, f'lbl_{colName}')
        else:
            raise ValueError(f'Col Name {colName} existiert nicht.')
    
    def iWasChanged(self, *args, **kwargs):
        logger.debug('iWasChanged aufgerufen')
        # Als erstes müssen wir ausschließen, dass ein Hotkey gedrückt wurde.
        # Hotkeys sind immer mit Control. D.h. falls iWasChanged als Event-Handler
        # aufgerufen wurde, prüfen wir, ob Control im Spiel war. In diesem Fall
        # beenden wir die Bearbeitung
        if args and isinstance(args[0], tk.Event):
            # iWasChanged wurde als Event-Handler aufgerufen
            event = args[0]
            if event.state & 0x4:
                # 0x4 steht für Control
                return
        if not self._changed:
            logger.debug('Status auf Changed=True geändert')
            self._changed = True
            if self._navi:
                self._navi.indicateChanged()
    
    def iWasReset(self, *args, **kwargs):
        logger.debug('iWasReset aufgerufen')
        if self._changed:
            self._changed = False

    def handleHotkey(self, event):
        """handleHotkey - Behandelt Hotkeys, die auf Formular-Ebene gebunden sind
        """
        if not event.state & 0x4:
            # 0x4 steht für Control. Nur wenn Control im Spiel war, arbeiten wir weiter
            logger.debug('Das war kein gültiger Hotkey')
            return
        logger.debug('Hotkey bearbeiten')
        hotkey = event.keysym
        if hotkey == 's':
            logger.debug('Control-s bearbeiten')
            self.getNavi().handleSave()
        elif hotkey == 'd':
            logger.debug('Control-d bearbeiten')
            self.getNavi().handleDelete()
        elif hotkey == 'n':
            logger.debug('Control-n bearbeiten')
            self.getNavi().handleEmptyform()

    def addWidget(self, colName, widget, typ, label=None):
        """addWidget - Fügt dem Formular ein Widget hinzu
        
            Fügt dem Formular ein Tk/Ttk Widget hinzu.
            
            Außerdem wird, je nach label, ein Label-Widget erzeugt und
            dem Formular hinzugefügt.
            
            Schließlich wird der LabelFrame erzeugt
            
            Es sind nur solche Widgets erlaubt, die einen Wert (value)
            haben bzw. die einen Wert (value) manipulieren können.
            Bsp.: Entry, Checkbutton, Selectbox, Text, oder entsprechende
                  selbst gebaute Widgets.
                  
            ACHTUNG:
            Das Widget muss mit einer Control Variable ausgestattet sein.
            Und zwar - vielleicht im Einzelfall anders als erwartet -
            mit den folgenden festgelegten Typen.
            
                    Hintergrund:
                    Sonst funktionieren die Methoden
                    getValue, setValue und clearValue nicht richtig.
                    Leider kann der Typ der Control Variable nicht festgestellt
                    werden. Folglich kann er auch nicht auf seine Richtigkeit
                    geprüft werden.
                
                Entry           tk.StringVar
                Checkbutton     tk.IntVar
            
            Besonderheiten für datetime, date und time Widgets
            
                Alle drei Typen können entweder None (d.h. '' im Widget)
                oder einen gültigen String enthalten. Als gültig betrachten wir
                im Wesentlichen die deutsche oder eine normierte internationale
                Schreibweise, d.h. z.B für...
                
                    time        23:54
                    date        23.05.2022 (23. Mai 2022) oder
                                23.04.22 (dto)
                                2022-05-23 (dto)
                    datetime    2022-05-23 23:54
                
                Vgl. dazu die Konstanten FORMATS_DATE, FORMATS_TIME, FORMATS_DATETIME
                Weitere Möglichkeiten können evt. über diese Konstanten ermöglicht
                werden.
                
                Alles darüber hinaus müsste ggf. über Validatoren implementiert
                werden.
            
            Parameter
                colName    i.d.R. Name der Spalte in der DB-Tabelle,
                            auf die sich das Widget bezieht.
                            Bezieht sich das Widget auf keine DB-Tabelle,
                            kann colName frei gewählt werden (im Rahmen
                            von checkPythonName)
                widget      Widget
                typ         Typ des Widgets, ein Wert aus TYPES
                label       Label für das Widget.
                            Optional. Im Fall von None wird ein
                            "leeres" Label Widget hergestellt
                            Typ: eine von Möglichkeiten:
                                str: Einfacher Text
                                Label Widget
                            Je nach dem Typ wird...
                                im ersten Label Widget hergestellt
                                im dritten Fall wird das Label Widget
                                einfach übernommen
        """
        #
        # Parameter prüfen
        #
        # colName erlaubt?
        # 1. muss eindeutig sein
        # 2. darf sich nicht mit irgendwelchen Attributen der
        #    Instanz überschneiden
        if colName in self._colNames:
            raise ValueError(f'colName {colName} bereits vergeben.')
        if colName in self.__dict__:
            raise ValueError(f'colName {colName} nicht erlaubt.')
        # colName muss ein zulässiger Python-Name sein
        checkPythonName(colName)
        # typ prüfen
        if typ not in __class__.TYPES:
            raise ValueError(f'{typ=} ungültig.')
        # Typ des Widgets prüfen
        if not (isinstance(widget, tk.Widget) or isinstance(widget, ttk.Widget)):
            raise TypeError('widget hat falschen Typ {type(widget)}.')
        #
        # Widget und typ kompatibel?
        #
        if isinstance(widget, ttk.Checkbutton):
            if typ != 'bool':
                raise ValueError(f'Checkbutton nur für bool, hat aber {typ=}')
        elif isinstance(widget, tk.Text) or isinstance(widget, scrolledtext.ScrolledText):
            if typ != 'text':
                raise ValueError(f'Text nur für text, hat aber {typ=}')
        #
        # Bei Bedarf Control Variable erzeugen und an Widget hängen
        #
        if type(widget) in (ttk.Entry, ttk.Combobox):
            self._controlVars[colName] = tk.StringVar()
            widget['textvariable'] = self._controlVars[colName]
        elif isinstance(widget, ttk.Checkbutton):
            self._controlVars[colName] = tk.IntVar()
            widget['variable'] = self._controlVars[colName]
        #
        # Hack für Combobox
        #
        if isinstance(widget, ttk.Combobox):
            logger.debug('Hack für Combobox')
            widget.config(exportselection=0)
        #
        # Widget mit Trigger für Changed Indicator ausstatten
        #
        if type(widget) == ttk.Entry:
            widget.bind('<KeyRelease>', self.iWasChanged)
        elif type(widget) == ttk.Combobox:
            widget.bind('<KeyRelease>', self.iWasChanged)
            widget.bind('<Button-4>', self.iWasChanged)
            widget.bind('<Button-5>', self.iWasChanged)
            widget.bind('<<ComboboxSelected>>', self.iWasChanged)
        elif type(widget) == ComboboxValueLabel:
            widget.bind('<Button-4>', self.iWasChanged)
            widget.bind('<Button-5>', self.iWasChanged)
            widget.bind('<<ComboboxSelected>>', self.iWasChanged)
        elif type(widget) == ttk.Checkbutton:
            if not widget.cget('command'):
                # command wird nur gesetzt, wenn nicht bereits gesetzt
                widget.config(command=self.iWasChanged)
        elif type(widget) in (tk.Text, scrolledtext.ScrolledText):
            widget.bind('<KeyRelease>', self.iWasChanged)
        elif type(widget) == ListboxValueLabel:
            widget.bind('<ButtonRelease-1>', self.iWasChanged)
            widget.bind('<Button-4>', self.iWasChanged)
            widget.bind('<Button-5>', self.iWasChanged)
        elif type(widget) in (FrameScrolledListbox, FrameScrolledListboxValueLabel):
            widget.Listbox.bind('<ButtonRelease-1>', self.iWasChanged)
        #
        # Widget mit Trigger für Hotkeys ausstatten
        #
        widget.bind('<Control-d>', self.handleHotkey)
        widget.bind('<Control-n>', self.handleHotkey)
        widget.bind('<Control-s>', self.handleHotkey)
        #
        # Widget ggf. mit Copy/Paste ausstatten
        #
        if type(widget) in (ttk.Entry, tk.Text, scrolledtext.ScrolledText):
            CopyPaste(widget, self)
        #
        #
        # Widget merken
        #
        setattr(self, colName, widget)
        #
        # colName und typ behandeln
        #
        self._colNames.append(colName)
        self._types[colName] = typ
        #
        # label bearbeiten
        #
        parentWidgetName = widget.winfo_parent()
        parentWidget = widget._nametowidget(parentWidgetName)
        if label is None:
            # Kein label angegeben, Default-Label erzeugen
            lbl = ttk.Label(
                        parentWidget,
                        text=str(colName))
        elif type(label) == str:
            # label ist ein String
            lbl = ttk.Label(
                        parentWidget,
                        text=label)
        elif isinstance(label, ttk.Label):
            # label ist bereits ein Label
            lbl = label
        else:
            # Typ von label falsch
            raise TypeError('Falscher label Typ: {}'.format(type(label)))
        lbl_text = lbl['text']
        # label merken
        setattr(self, f'lbl_{colName}', lbl)
        
        return colName
    
    def setValue(self, colName, value):
        """setValue - Setzt den Wert des Widgets auf (ggf. String-Variante von) value
        
            setValue konvertiert value nötigenfalls in eine String-Variante und
            setzt den Wert des Widgets darauf.
            
            Durch die zweifache Fallunterscheidung (Art des Widgets und
            typ des Widgets) ist der Code entsprechend zweifach
            geschachtelt...
            
            Parameter
                colName   Name des Widgets bzw. der Spalte in der DB
                value     Wert, i.d.R. aus der DB, in Python Type konvertiert
        """
        # Gibt es colName überhaupt?
        if not self.existsColName(colName):
            raise ValueError(f'Col Name {colName} existiert nicht.')
        # Widget und Typ des Widgets merken
        widget = self.getWidget(colName)
        typ = self.getType(colName)
        #
        # Haupt-Fallunterscheidung
        #
        if type(widget) in (ttk.Entry, ttk.Combobox):
            # Entry Widget
            if typ == 'text':
                self._controlVars[colName].set('' if value is None else value.strip())
            elif typ == 'int':
                self._controlVars[colName].set('' if value is None else str(value))
            elif typ == 'float':
                self._controlVars[colName].set('' if value is None else float(value))
            elif typ == 'decimal':
                self._controlVars[colName].set('' if value is None else Decimal(value))
            elif typ == 'bool':
                if value is None:
                    self._controlVars[colName].set('')
                elif value:
                    self._controlVars[colName].set(TRUES[0])
                else:
                    logger.debug(colName)
                    self._controlVars[colName].set(FALSE)
            elif typ == 'date':
                if value is None:
                    self._controlVars[colName].set('')
                else:
                    self._controlVars[colName].set(value.strftime(FORMATS_DATE[0]))
            elif typ == 'time':
                if value is None:
                    self._controlVars[colName].set('')
                else:
                    self._controlVars[colName].set(value.strftime(FORMATS_TIME[0]))
            elif typ == 'datetime':
                if value is None:
                    self._controlVars[colName].set('')
                else:
                    self._controlVars[colName].set(value.strftime(FORMATS_DATETIME[0]))
            else:
                raise ValueError(f'Ungültiger Widget Typ: {typ=}')
        elif type(widget) == ComboboxValueLabel:
            widget.setValue(value)
        elif isinstance(widget, ttk.Checkbutton):
            # Checkbutton Widget
            if typ == 'bool':
                self._controlVars[colName].set(1 if value else 0)
            else:
                raise TypeError(f'Checkbutton nur für bool, hier aber {typ}.')
        elif isinstance(widget, tk.Text) or isinstance(widget, scrolledtext.ScrolledText):
            # Text (oder ScrolledText) Widget
            if typ == 'text':
                widget.delete('0.0', tk.END)
                if value:
                    widget.insert('0.0', value)
            else:
                raise ValueError(f'Text Widget nur für text, hat aber {typ=}')
        elif isinstance(widget, ListboxValueLabel):
            # ListboxValueLabel Widget, abgeleitet von Listbox
            if type(value) in (tuple, list):
                widget.setValues(value)
            else:
                widget.setValue(value, exclusive=True)
        elif isinstance(widget, FrameScrolledListbox) \
              or isinstance(widget, FrameScrolledListboxValueLabel):
            if type(value) in (tuple, list):
                widget.setValues(value)
            else:
                widget.setValue(value, exclusive=True)
        elif isinstance(widget, ttk.Label):
            if typ == 'text':
                widget.config(text='' if value is None else value.strip())
            else:
                raise(TypeError(f'Label nur für Typ text implementiert, nicht für {typ}.'))
        else:
            raise TypeError('Für {} Widget nicht implementiert.'.format(type(widget)))
    
    def getValue(self, colName):
        """getValue - Gibt den konvertierten Wert des Widgets
        
            getValue holt den Wert aus dem Widget und gibt ihn je nach typ in
            den entsprechenden Python Type konvertiert zurück.
            
            getValue nimmt stillschweigend kleine Korrekturen vor, so werden z.B.
            bei text Widgets führende und folgende Whitespaces entfernt.
            
            Im Übrigen gehen wir davon aus, dass (z.B. durch Validatoren)
            sichergestellt ist, dass gültige Werte im Widget
            stehen. Wir nehmen hier also keine weitere Prüfung vor und
            nehmen in Kauf, wenn andernfalls Exceptions geworfen werden.
            
            Durch die zweifache Fallunterscheidung (Art des Widgets und
            typ des Widgets) ist der Code entsprechend zweifach
            geschachtelt...
            
            Parameter
                colName   Name des Widgets bzw. der Spalte in der DB
            
            Ergebnis
                In Python Type konvertierter Wert des Widgets.
        """
        # Gibt es colName überhaupt?
        if not self.existsColName(colName):
            raise ValueError(f'Col Name {colName} existiert nicht.')
        # Widget und Typ des Widgets merken
        widget = self.getWidget(colName)
        typ = self.getType(colName)
        #
        # Haupt-Fallunterscheidung
        #
        if type(widget) in (ttk.Entry, ttk.Combobox):
            # Entry Widget
            #
            value = self._controlVars[colName].get().strip()
            if typ == 'text':
                return value.strip()
            elif typ == 'int':
                if value == '':
                    return None
                else:
                    return int(value)
            elif typ == 'float':
                if value == '':
                    return None
                else:
                    return float(value.replace(',', '.'))
            elif typ == 'decimal':
                if value == '':
                    return None
                else:
                    return Decimal(value)
            elif typ == 'bool':
                if value == '':
                    return None
                elif value.lower()[0] in TRUES_SHORT:
                    return True
                else:
                    return False
            elif typ == 'date':
                if value == '':
                    return None
                else:
                    for formatString in FORMATS_DATE:
                        try:
                            Ergebnis = datetime.datetime.strptime(value, formatString).date()
                            return Ergebnis
                        except Exception as e:
                            pass
                    raise RuntimeError('Datum ungültig - dürfte nicht vorkommen.')
            elif typ == 'time':
                if value == '':
                    return None
                else:
                    for formatString in FORMATS_TIME:
                        try:
                            Ergebnis = datetime.datetime.strptime(value, formatString).time()
                            return Ergebnis
                        except Exception as e:
                            pass
                    raise RuntimeError('Datum ungültig - dürfte nicht vorkommen.')
            elif typ == 'datetime':
                if value == '':
                    return None
                else:
                    for formatString in FORMATS_DATETIME:
                        try:
                            Ergebnis = datetime.datetime.strptime(value, formatString)
                            return Ergebnis
                        except Exception as e:
                            pass
                    raise RuntimeError('Datum ungültig - dürfte nicht vorkommen.')
            else:
                raise ValueError(f'Ungültiger Widget Typ: {typ=}')
        elif type(widget) == ComboboxValueLabel:
            return widget.getValue()
        elif isinstance(widget, ttk.Checkbutton):
            # Checkbutton Widget
            value = self._controlVars[colName].get()
            if typ == 'bool':
                return value == 1
            else:
                raise TypeError(f'Checkbutton nur für bool, hier aber {typ}.')
        elif isinstance(widget, tk.Text) or isinstance(widget, scrolledtext.ScrolledText):
            # Text (oder ScrolledText) Widget
            if typ == 'text':
                return widget.get('0.0', tk.END).strip()
            else:
                raise ValueError(f'Text Widget nur für text, hat aber {typ=}')
        elif isinstance(widget, ListboxValueLabel):
            # ListboxValueLabel Widget, abgeleitet von Listbox
            liste = widget.getValues()
            laenge = len(liste)
            if laenge == 0:
                return None
            elif laenge == 1:
                return liste[0]
            else:
                return liste
        elif isinstance(widget, FrameScrolledListbox) \
                or isinstance(widget, FrameScrolledListboxValueLabel):
            liste = widget.getValues()
            laenge = len(liste)
            if laenge == 0:
                return None
            elif laenge == 1:
                return liste[0]
            else:
                return liste
        elif isinstance(widget, ttk.Label):
            return widget.cget('text')
        else:
            raise TypeError('Für {} Widget nicht implementiert.'.format(type(widget)))
    
    def setValues(self, values, check=False, keep=False):
        """setValues - Setzt die Werte der Widgets nach dem Dict values
        
            setValues setzt die Werte der Widgets nach dem Dict values. Dabei
            werden natürlich nur die Werte gesetzt, die in values vorkommen.
            
            Wenn keep False ist, werden vorher werden alle Werte gelöscht. Andernfalls
            werden die Werte überschrieben, folglich die nicht vorhandenen erhalten.
            
            Wenn check False ist, wird nicht geprüft, ob alle colNames von Form
            auch in values vorkommen. Dieser Check wird nur mit check = True
            vorgenommen und führt ggf. zu einer Exception.
        
            Parameter
                values    Dict von colName --> value
                check     Bool. 
                          True:   es wird geprüft, ob alle colNames von Form
                                  in values vorkommen. Andernfalls wird eine
                                  Exception geworfen.
                          False:  es wird nicht geprüft.
                keep      Bool
                          True:   Werte, die nicht in values vorkommen, werden
                                  erhalten
                          False:  Erst werden alle Werte in Form gelöscht.
        """
        # ggf. prüfen, ob alle colNames von Form in values vorkommen
        if check:
            for colName in self.getColNames():
                if not colName in values:
                    raise RuntimeError(f'values unvollständig: mindestens {colName=} fehlt.')
        # ggf. Werte vorher löschen
        if not keep:
            self.clearValues()
        # values durchgehen
        for colName in values.keys():
            self.setValue(colName, values[colName])
    
    def getValues(self):
        """getValues - Liefert die Werte aller Widgets als Dict
        
            Liefert die Werte aller Widgets als Dict. Die Werte kommen als Python
            Typen.
        """
        return {colName: self.getValue(colName) for colName in self.getColNames()}
    
    def clearValue(self, colName):
        """clearValue - Löscht den Wert in dem zugehörigen Widget
        
            clearValue setzt auf setValue auf und setzt den Wert auf None.
            In Zukunft könnte das anders implementiert werden.
        
            Parameter
                colName     Name des Widgets bzw. der Spalte in der DB
        """
        self.setValue(colName, None)
    
    def clearValues(self):
        """clearValues - Löscht die Werte aller Widgets
        """
        for colName in self.getColNames():
            self.clearValue(colName)
    
    def setGetterAuswahl(self, col_name, getter):
        """setGetterSelect - Setzt Getter für Auswahl (Select oder RadioSet)
            
            Der Getter muss eine Funktion sein, die
            value/label Paare für Combobox Widgets liefert.
        """
        self._getterAuswahl[col_name] = getter
    
    def updateSelect(self, col_name):
        """updateSelect - Versorgt das Widget zu col_name mit Auswahl
        
            Versorgt das Widget zu col_name mit Auswahl, falls es eine Auswahl gibt.
            Falls es zu col_name keine Möglichkeit gibt, eine Auswahl zu geben,
            wird eine Warnung gelogged.
            
            Parameter
                col_name    Spalte, zu der die Auswahl gefunden werden soll
        """
        if col_name not in self._getterAuswahl:
            logger.warning(f'Zu {col_name} gibt es keinen Getter')
            return
        logger.debug(f'{col_name=}')
        getter = self._getterAuswahl[col_name]
        auswahl = getter()
        logger.debug(auswahl)
        # Fallunterscheidung je nach Typ des Widgets
        wdg = self.getWidget(col_name)
        if type(wdg) == ttk.Combobox:
            wdg['values'] = [value for (value, label) in auswahl]
        elif type(wdg) in (ListboxValueLabel, FrameScrolledListboxValueLabel, ComboboxValueLabel):
            wdg.fill(auswahl)
        else:
            logging.warning(f'Für {type(wdg)} nicht implementiert.')
    
    def updateSelects(self):
        """updateSelects - Füllt relevante Select/Combobox Widgets mit Auswahl
        
            Geht die Felder durch, die einen GetterSelect haben und ruft dafür
            self.updateSelect auf.
        """
        for col_name in self._getterAuswahl:
            self.updateSelect(col_name)
    
    @staticmethod
    def resetForms():
        """resetForms - Setzt bestimmte Eigenschaften aller vorhandenen Instanzen
        
            resetForms setzt bestimmte Eigenschaften aller vorhandenen Instanzen.
            Das sind z.Zt.:
                
                1. Werte für Combobox und ähnliche Widgets über die Getter holen und einsetzen.
        """
        for form in __class__.FORMS:
            form.updateSelects()
            form.clearValues()
            navi = form.getNavi()
            if navi:
                navi.buildChoices()
        
    @staticmethod
    def deleteFORMS():
        """deleteFORMS - löscht Liste der Instanzen
        
            Vermutlich nur für Debugging-Zwecke gebraucht.
        """
        pass

            
class NaviWidget(ttk.Frame):
    """NaviWidget - Stellt Widgets für Navi Funktionalität bereit
    
        In abgeleiteten Klassen wird das Navi um Schnittstellen zu Modell/DB
        erweitert. Je nach Art dieser Schnittstelle eignet sich das Navi dann
        für Hauptformulare (Form), Unterformulare (ListForm) oder für
        ListForm als Listenansicht (also nicht als Unterformular).
        
        Mit diesen Ergänzungen wir das Navi zur "Schaltzentrale" zwischen
        Formular, Datenbank/Modell und Benutzer.
        
        In NaviWidget werden ausschließlich die nötigen Widgets bereitgestellt,
        schön angeordnet in ttkFrame (von dem NaviWidget abgeleitet ist),
        das später als Navi in das Formular eingbaut (z.B. gepackt) werden kann.
        
        Für die abgeleiteten Klassen initialisieren wir Attribute/Methoden,
        eigentlich aber nur um der Klarheit willen.
        
        In NaviWidget bauen wir folglich ein ttk.Frame der folgenden Form:
        
        +---------------------------+
        | Filter, Buttons           |
        +---------------------------+
        | Auswahlliste              | 
        |                           |
        +---------------------------+
        
        Dabei ist:
            Filter
                Ein Eingabefeld (Entry) (mit Icon (Lupe)?). Eingaben hier
                führen zu einer Filterung der Auswahlliste
            Buttons
                Eine Reihe von Buttons, die der Navigation und Funktionalität
                auf der Datenbank bzw. auf dem Formular dienen. Z.B. Sichern, Löschen,
                Refresh
            Auswahlliste
                Variante von tk.Listbox (i.d.R. FrameScrolledListboxValueLabel), darin
                untereinander für jeden Datensatz in der DB eine Zeile. Wird eine
                Zeile ausgewählt, d.h. der zugehörige
                Datensatz ausgewählt, wird er in dem Formular angezeigt.
                Diese Zeilen verhalten sich letztlich wie ein Button.
        
        Achtung: Icons (Images) für Buttons können erst gebaut werden, wenn es
        ein root-Window gibt. Daher kann bei der Instanziierung von NaviWidget
        i.d.R. den Buttons noch kein Image zugeteilt werden.
        Workaround: Bei der Instanziierung merken wir uns ohnehin die eingebauten
        Widgets, also auch die Buttons. Wir definieren die
            Static Method
                imageInit(), die nachträglich die Images erzeugt und
        den Buttons zuordnet.
        
        Parameter
            parent        Eltern Widget, wird an ttk.Frame weiter gegeben
            elemente      Liste/Tupel der Elemente, die in dem Navi tatsächlich eingebaut
                          werden sollen.
                          Default: () (leeres Tupel), d.h. alle verfügbaren Elemente
                              werden eingebaut
                          Die Elemente werden mit str-Werten angegeben. Mögliche
                          Werte sind:
                              filter      Input-Feld zum Filtern
                              emptyform   Formular leeren für neue Eingabe
                              save        Datensatz in der DB sichern (INSERT/UPDATE)
                              save-clear  Datensatz in der DB sichren (INSERT/UPDATE)
                                          Beachte
                                          Die beiden save Varianten unterscheiden sich
                                          nur dadurch, dass bei save nach dem
                                          Speichern der gespeicherte Datensatz
                                          im Formular wieder gezeigt wird. save-clear
                                          hingegen leert das Formular nach dem
                                          Speichern.
                              delete      Datensatz in der DB löschen (DELETE)
                              refresh     Auswahlliste neu aufbauen
                              undo        Datensatz neu aus der DB lesen, d.h.
                                          eventuell im Formular vorgenommene
                                          Änderungen verwerfen.
                              copy        Doublette des angezeigten Datensatzes
                                          anlegen und im Formular zeigen.
                              list        Auswahlliste, ggf. gefiltert
                          Bsp.: ('filter', 'save', 'delete')
                          Ungültige Werte führen zu ValueError
        
        Klassen Attribute
            GUELTIGE_ELEMENTE     Tupel der gültigen Elemente, vgl. Parameter elemente
        
        Attribute
            elemente              elemente, vgl. entspr. Parameter
            form                  Formular, an dem das Navi hängt. Wird z.B. durch
                                  BasisForm.setNavi gesetzt
            naviElemente          Dict der Navi-Elemente
                                  Für die Elemente, die nicht vorhanden sind (weil nicht
                                  in elemente angegeben), wird der Wert auf None gesetzt.
        
        Static Methods
            imageInit     Baut die Icons (Images) für die Buttons und
                          versorgt die Buttons damit.
        
        Methods
            buildNaviWidget   Baut Navi Widget auf
            
    """
    # Tupel der Elemente, die als Widgets o.ä. in das Navi eingebaut werden können.
    # GUELTIGE_ELEMENTE wird verwendet, um
        #   1.  Die übergebenen Elemente (elemente) auf ihre Gültigkeit zu überprüfen.
        #           Ungültigkeit wird einerseits mit einem DEBUG gelogged (nur einmal beim
        #           Instantiieren), andererseits später stillschweigend ignoriert.
        #   2.  Dict der Navi-Buttons zu initialisieren. GUELTIGE_ELEMENTE
        #           sollte also vollständig sein.
    GUELTIGE_ELEMENTE = (
        'filter',
        'emptyform',
        'save',
        'save-clear',
        'delete',
        'refresh',
        'undo',
        'copy',
        'list',
        )
    
        
    navis = []
    
    def __init__(self, parent, elemente=()):
        #
        # __init__ von super() aufrufen, in diesem Fall also von Widget.
        super().__init__(parent)
        #
        # Merken der übergebenen Parameter
        if elemente:
            # Es wurden Elemente übergeben
            self.elemente = elemente
        else:
            # Default, es wurden keine Elemente übergeben, gemeint
            # sind also alle erlaubten Elemente
            self.elemente = __class__.GUELTIGE_ELEMENTE
        #
        # Gültigkeit der Elemente prüfen
        for element in elemente:
            if not element in __class__.GUELTIGE_ELEMENTE:
                raise ValueError(f'')
        #
        # Attribut: Dict für Navi-Elemente initialisieren
        self.naviElemente = {element: None for element in self.GUELTIGE_ELEMENTE}
        #
        # Attribut: Var für Filter-Input initialisieren
        self.naviFilterEntry = None
        # Navi Widget
        self.buildNaviWidget()
        # Navi in Klassenattribut merken
        __class__.navis.append(self)
        
    def buildNaviWidget(self):
        """buildNaviWidget - baut Widgets und packt sie in ttk.Frame
        """
        style = ttk.Style()
        style.configure(
            'Changed.Navi.TFrame',
            background='red'
            )
        style.configure('Navi.TButton',
            borderwidth=0,
            padding=0,
            padx=0,
            pady=0,
            width='100px')
        self.buttons = ttk.Frame(self, borderwidth=2, relief='flat')
        self.buttons.pack(side=tk.TOP, anchor=tk.W)
        for element in self.elemente:
            if element == 'filter':
                self.naviElemente[element] = FilterEntry(
                        self.buttons,
                        callback=self.handleFilterChanged,
                        width=6)
                Tooltip(self.naviElemente[element], 'Auswahlliste filtern')
                # self.naviElemente[element].bind(
                #         '<KeyRelease>',
                #         self.handleFilterChanged
                #         )
                self.naviElemente[element].pack(side=tk.LEFT)
            if element == 'emptyform':
                self.naviElemente[element] = ttk.Button(
                        self.buttons,
                        text='Empty Form',
                        image=glb.icons.getIcon('emptyform', glb.ICON_NAVI_SIZE),
                        style='Navi.TButton',
                        command=self.handleEmptyform
                        )
                Tooltip(self.naviElemente[element], 'Formular leeren für neuen Datensatz')
                self.naviElemente[element].pack(side=tk.LEFT)
            if element == 'save':
                self.naviElemente[element] = ttk.Button(
                        self.buttons,
                        text='Save',
                        image=glb.icons.getIcon('save', glb.ICON_NAVI_SIZE),
                        style='Navi.TButton',
                        command=self.handleSave
                        )
                Tooltip(self.naviElemente[element], 'Datensatz speichern und weiter bearbeiten')
                self.naviElemente[element].pack(side=tk.LEFT)
            if element == 'save-clear':
                self.naviElemente[element] = ttk.Button(
                        self.buttons,
                        text='Save+Clear',
                        image=glb.icons.getIcon('save-clear', glb.ICON_NAVI_SIZE),
                        style='Navi.TButton',
                        command=self.handleSaveClear
                        )
                Tooltip(self.naviElemente[element], 'Datensatz speichern und Formular leeren')
                self.naviElemente[element].pack(side=tk.LEFT)
            if element == 'delete':
                # self.abc = glb.icons.getIcon('delete')
                self.naviElemente[element] = ttk.Button(
                        self.buttons,
                        text='Delete',
                        image=glb.icons.getIcon('delete', glb.ICON_NAVI_SIZE),
                        style='Navi.TButton',
                        command=self.handleDelete)
                Tooltip(self.naviElemente[element], 'Datensatz löschen')
                self.naviElemente[element].pack(side=tk.LEFT)
            if element == 'refresh':
                self.naviElemente[element] = ttk.Button(
                        self.buttons,
                        text='Refresh',
                        image=glb.icons.getIcon('refresh', glb.ICON_NAVI_SIZE),
                        style='Navi.TButton',
                        command=self.handleRefresh)
                Tooltip(self.naviElemente[element], 'Auswahlliste neu aufbauen')
                self.naviElemente[element].pack(side=tk.LEFT)
            if element == 'undo':
                self.naviElemente[element] = ttk.Button(
                        self.buttons,
                        text='Undo',
                        image=glb.icons.getIcon('undo', glb.ICON_NAVI_SIZE),
                        style='Navi.TButton',
                        command=self.handleUndo)
                Tooltip(self.naviElemente[element], 'Änderungen rückgängig machen')
                self.naviElemente[element].pack(side=tk.LEFT)
            if element == 'copy':
                self.naviElemente[element] = ttk.Button(
                        self.buttons,
                        text='Copy',
                        image=glb.icons.getIcon('copy', glb.ICON_NAVI_SIZE),
                        style='Navi.TButton',
                        command=self.handleCopy)
                Tooltip(self.naviElemente[element], 'Kopie des Datensatzes anlegen (soweit das möglich ist)')
                self.naviElemente[element].pack(side=tk.LEFT)
        if 'list' in self.elemente:
            self.naviElemente['list'] = FrameScrolledListboxValueLabel(self)
            self.naviElemente['list'].Listbox.bind(
                '<<ListboxSelect>>',
                self.handleOptionSelected)
            self.naviElemente['list'].pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    def destroyWidgets(self):
        """destroyWidgets - Zerstört die (primären) Widgets des Navis
        
            Diese Methode wird gebraucht, um Listenansichten zu löschen, damit
            keine Widgets im Speicher verbleiben. In Listenansichten haben die 
            Navis in aller Regel nur save und delete, insb. aber kein list Element.
            Daher berücksichtigen wir nur "primäre" Widgets und nichts in
            den (nicht vorhandenen) Auswahllisten. Das ist etwas unsauber
            programmiert...
        """
        for element in self.elemente:
            wdg = self.naviElemente.pop(element)
            wdg.pack_forget()
            wdg.destroy()
        self.buttons.pack_forget()
        self.buttons.destroy()

class NaviListe(NaviWidget):
    """NaviListe - ergänzt das NaviWidget um die Navi-Funktionen für Listenansichten
    """
    LISTNAVI_ELEMENTE = (
        'filter',
        'save',
        'refresh',
        )
    def __init__(self, parent, elemente=()):
        # Elemente des Navi aussortieren und merken
        # Als Elemente für NaviListe sind nur die aus LISTNAVI_ELEMENTE erlaubt,
        # d.h. wir übernehmen nur solche aus elemente, die auch darin enthalten
        # sind. Wurden keine elemente übergeben, verwenden wir
        # LISTNAVI_ELEMENTE
        if elemente:
            self.elemente = []
            for element in elemente:
                if element in __class__.LISTNAVI_ELEMENTE:
                    self.elemente.append(element)
        else:
            self.elemente = __class__.LISTNAVI_ELEMENTE
        #
        # damit nun init vom NaviWidget aufrufen
        super().__init__(parent, self.elemente)
        #
        # Attribute initialisieren
        self.getterDicts = None
    
    def setGetterDicts(self, getter):
        self.getterDicts = getter
    
    def buildFormulare(self):
        if 'filter' in self.elemente:
            filterValue = self.naviElemente['filter'].get()
        else:
            filterValue = None
        dicts = self.getterDicts(filterValue)
        self.form.build(dicts)
    
    def handleFilterChanged(self, event):
        self.buildFormulare()
    
    def handleSave(self):
        for form in self.form.forms:
            if form._changed:
                form.getNavi().handleSave()
    
    def handleRefresh(self):
        self.buildFormulare()
    
class NaviForm(NaviWidget):
    """NaviForm - Ergänzt das NaviWidget um die Funktionen des Navis
    
        NaviForm ergänzt NaviWidget um die Schnittstelle zwischen Formular und
        Datenbank/Modell. Damit wird das FormNavi zur "Schaltzentrale" des
        Formulars.
        
        Für bestimmte fälle merkt sich das Navi, welcher Datensatz - genauer:
        die Werte dieses Datensatzes - zuletzt im Formular angezeigt wurde.
            Die ursprüngliche Idee war, das über die highlighted Zeile in der
            Auswahlliste zu erledigen. Das geht aber nicht, da nicht jedes Navi
            eine Auswahlliste hat.
        Das merken wir uns in dem Dict valuesLast.
        
        Für die Schnittstelle zum Modell bekommt das Navi über die Methoden
        
            setGetterAuswahl
            setGetterValues
            setSaverValues
            setDeleterValues
        
        Methoden, die die Schnittstelle dann bilden. Bei der Herstellung des Navi
        greift man dazu z.B. auf die Methoden des Modells zurück:
        
            FactoryGetterAuswahl
            FactoryGetterValues
            FactorySaverValues
            FactoryDeleterValues
        
        Außerdem bekommt das Navi für Select/Combobox Widgets, die aus einer
        Relation Werte zur Auswahl stellen, jeweils eine Methode über
        
            setGetterSelect
        
        die die value/label Paare liefert. Dabei greift man i.d.R. auf die
        Factory Methode des Modells zurück:
        
            FactoryGetterChoices
        
        Diese Getter werden - anders als die anderen Getter - an Form, also an das
        Formular weiter gereicht und dort verwaltett und ggf. aktiviert.
        
        Unterformulare für n-1 und n-n Relationen
        
            FormNavi übernimmt das "Managment" eventueller "Unterformulare", in
            denen n-1 Relationen angezeigt werden können. Die Darstellung erfolgt
            als FormListe, d.h. die Datensätze werden als Liste von Formularen dargestellt.
            
            In der Praxis wird solch eine n-1 Relation häufig die eine Seite einer
            n-n sein. Die rechte Seite wird dann z.B. als Select-Feld erledigt.
            
            Für jede n-1 (oder n-n) Relation gibt es eine FormListe. Dafür haben wir
            ein Attribut formListen (Dict), das Relation auf FormListe abbildet.
    
        Attribute
            form                  Formular, zu dem das Navi gehört
            keyFeldNavi           Key Feld des Models (DB-Tabelle),
                                  über den die Datensätze im Formular
                                  identifiziert werden bzw. das als Key in der
                                  Auswahl Liste verwendet wird.
                                  I.d.R. ist das id (Default), kann aber
                                  z.B. auf kurz_bez gesetzt werden.
            valuesLast            Werte des zuletzt angezeigten Datensatzes
                                  Typ: Dict
            formListen            Dict Relation --> FormListe
        
        Methoden
            Schnittstelle zum Modell:
                setGetterAuswahl
                setGetterValues
                setSaverValues
                setDeleterValues
            
            Bedienung der Auswahlliste:
                optionsAppend
                optionsClear
            
            Event Handler
                handleButtonPressed     Behandelt alle Buttons
                handleFilterChanged     Behandelt Filter Entry
                handleOptionSelected    Behandelt Auswahl getroffen
            
            Ausführung der Schnittstelle zu DB/Modell
                save
                delete
            
            Umgang mit Daten in den Feldern
                showFromValue
                showLast
    """
    def __init__(self, parent, elemente=()):
        super().__init__(parent, elemente)
        
        self.GetterAuswahl = self._fakeGetterAuswahl
        self.GetterValues = self._fakeGetterValues
        self.SaverValues = self._fakeSaverValues
        self.DeleterValues = lambda: logger.warning('DeleterValues nicht gesetzt.')
        
        self.form = None
        self.keyFeldNavi = 'id'
        self.formListen = {}
    
    @staticmethod
    def _fakeGetterAuswahl(Filter=None):
        """_fakeGetterAuswahl - Platzhelter, bis setGetterAuswahl aufgerufen wird
        
            Dient nur zu Testzwecken. Simuliert einen entsprechenden Getter.
        """
        logger.warning('GetterAuswahl nicht gesetzt.')
        result = []
        for k in range(random.randrange(30)):
            result.append((k, str(k) + f': {Filter}'))
        return result
    
    @staticmethod
    def _fakeGetterValues(keyValue=None):
        """_fakeGetterValues - Platzhalter, bis setGetterAuswahl aufgerufen wird
        
            Dient nur zu Testzwecken. Simuliert einen entsprechenden Getter.
        """
        logger.warning('GetterValues nicht gesetzt.')
        return {'id': 123, 'name': 'Fake Name'}
    
    @staticmethod
    def _fakeSaverValues(values):
        """_fakeSaverValues - Platzhalter, bis setSaverValues aufgerufen wird
        
            Dient nur zu Testzwecken. Simuliert einen entsprechenden Saver.
        """
        logger.warning('SaverValues nicht gesetzt.')
        logger.debug(f'{values=}')
        if 'id' in values and values['id'] is None:
            values['id'] = 111
            return 111
        return None
    
    def connectToModell(self, model,
            selects=(),
            keyFeldNavi=None, labelFelder=None, filterFelder=None, Sort=None):
        """connectToModell - Setzt die Factories Getter, Saver, Deleter
        
            Setzt für das Navi die drei Standard-Verbindungen
            GetterValues, SaverValues und DeleterValues,
            außerdem - falls vorhanden, die Getter für Select-artige Felder.
            
            Parameter
                model           Modell, zu dem die Verbindung gesetzt werden soll
                                Von diesem Modell werden über die entsprechenden
                                Factories Funktionen erzeugt
                selects         Liste/Tupel von colNames, für die ein Select-artiges
                                Feld mit Werten gefüllt werden soll.
                                Bsp.: ('farbe', 'mail_art', 'nachfolge_status')
                                Default: ()
                keyFeldNavi     Wie bei Modell.FactoryGetterAuswahl
                labelFelder     "
                filterFelder    "
                Sort            "
            
            ACHTUNG: Falls keyFeldNavi angegeben wird, dann muss auch labelFelder
            angegeben werden. Und nur dann haben filterFelder und Sort eine Wirkung.
            
            ACHTUNG: Das funktioniert nur, wenn colName und der zugehörige Relations-Name
            in model identisch sind.
        """
        #
        # Instanz des Modells herstellen
        m = model()
        #
        # Standard-Verbindung
        self.setGetterValues(m.FactoryGetterValues())
        self.setSaverValues(m.FactorySaverValues())
        self.setDeleterValues(m.FactoryDeleterValues())
        #
        # ggf. Getter für Select-artige Felder
        for colName in selects:
            self.setGetterSelect(colName, m.FactoryGetterChoices(colName))
        #
        # ggf. Getter für Auswahlliste
        if keyFeldNavi:
            self.setGetterAuswahl(m.FactoryGetterAuswahl(
                    keyFeldNavi,
                    labelFelder,
                    filterFelder,
                    Sort))
    
    def setGetterAuswahl(self, getter):
        """setGetterAuswahl - Setzt den Getter für die Auswahl Liste
        
            Der Getter muss eine Funktion mit einem optionalen Argument filter
            sein, die eine Liste von (value, label) bzw. in der obigen
            Terminologie (value, prompt) Paaren liefert.
            
            Typischerweise greift der Getter auf Daten in einer DB zurück
            und liefert nach filter gefilterte Datensätze aus der DB. Diese
            Datensätze sind typischerewise aufbereitet in Paare (id, label),
            wobei label z.B. 'name, vorname' ist.
        """
        self.GetterAuswahl = getter
    
    def setGetterValues(self, getter):
        """setGetterValues - Setzt den Getter für die Values zu highlighted
        
            Der Getter muss eine Funktion mit einem optionalen Argument keyValue
            sein, die den zu keyValue passenden Datensatz bzw. im Fall von
            keyValue is None einen beliebigen Datensatz von dem Modell, d.h. aus
            der Datenbank, als Dictionary liefert.
            
            Auf welches Feld der DB-Tabelle sich keyValue bezieht, "weiß" das Modell
            über Modell.keyFeld.
        """
        self.GetterValues = getter
    
    def setSaverValues(self, saver):
        """setSaverValues - Setzt den Saver für die Values des Formulars in der DB
        
            Der Saver muss eine Funktion mit einem Argument values sein, die
            die Werte in values (Dict) - i.d.R. aus einem Formular - in der DB
            speichert.
        """
        self.SaverValues = saver
    
    def setDeleterValues(self, deleter):
        """setDeleterValues - Setzt den Deleter für die Values des Formulars in der DB
        
            Der Deleter muss eine Funktion mit einem Argument values sein, die
            die Werte in values (Dict) - i.d.R. aus einem Formular - in der DB löscht.
        """
        self.DeleterValues = deleter
    
    def setGetterSelect(self, col_name, getter):
        """setGetterSelect - Setzt Getter für Auswahl (Select oder RadioSet)
            
            Der Getter muss eine Funktion sein, die
            value/label Paare für Combobox Widgets liefert.
        """
        self.form.setGetterAuswahl(col_name, getter)
        
    def optionsClear(self):
        """listClear - Leert die Ausswahlliste
        
            Falls es eine Auswahlliste gibt, wird sie geleert
        """
        if 'list' in self.elemente:
            self.naviElemente['list'].clear()
    
    def optionsAppend(self, value, label=None):
        """optionsAppend - Hängt value/label Paar(e) an die Auswahlliste an
        
            Parameter
                value   Einzelner Wert oder
                        Liste/Tupel von value/label-Paaren
                label   Nur relevant, wenn value kein List/Tuple ist.
                        In diesem Fall ggf. Label zu value
        """
        if type(value) in (tuple, list):
            for (v, t) in value:
                self.naviElemente['list'].append(v, t)
        else:
            self.naviElemente['list'].append(value, label)
    
    def buildChoices(self):
        """buildChoices - baut die Auswahl neu auf, ggf. gefiltert
        """
        if 'list' in self.elemente:
            self.optionsClear()
            if 'filter' in self.elemente:
                filterValue = self.naviElemente['filter'].get()
            else:
                filterValue = None
            self.optionsAppend(self.GetterAuswahl(filterValue))
    
    def clearUnterformulare(self):
        for listeName in self.formListen:
            self.formListen[listeName].clear()
    
    def handleFilterChanged(self, event):
        """handleFilterChanged -
        """
        self.buildChoices()
        self.form.clearValues()
        self.clearUnterformulare()
    
    def handleEmptyform(self):
        """handleEmptyform
        """
        self.form.clearValues()
        self.indicateNormal()
        self.clearUnterformulare()

    def handleSave(self):
        """handleSave - Sichert den Datensatz und zeigt ihn erneut an
        """
        logger.debug('Save behandeln')
        self.save(clear=False)
        self.indicateNormal()

    def handleSaveClear(self):
        """handleSaveClear
        """
        logger.debug('SaveClear behandeln')
        self.save(clear=True)
        self.indicateNormal()

    def handleDelete(self):
        """handleDelete
        """
        if dialog.askokcancel(
                title='Achtung',
                message='Wirklich löschen?'
                ):
            self.delete()
            self.buildChoices()
            self.form.clearValues()
            self.indicateNormal()
            self.clearUnterformulare()

    def handleRefresh(self):
        """handleRefresh
        """
        self.buildChoices()
        self.form.clearValues()
        self.indicateNormal()
        self.clearUnterformulare()

    def handleUndo(self):
        """handleUndo
        """
        self.showLast()
        self.indicateNormal()

    def handleCopy(self):
        """handleCopy
        """
        ergebnis = self.copy()
        self.indicateNormal()
        #
        # Auswahlliste neu aufbauen
        self.buildChoices()
        #
        # Ergebnis bearbeiten
        if type(ergebnis) == str:
            notify(ergebnis, 'Warnung')
        elif type(ergebnis) == int:
            notify(f'Kopie erfolgreich angelegt mit id={ergebnis}.', 'Erfolg')
        return ergebnis
    
    def handleOptionSelected(self, event):
        """handleOptionSelected -
        """
        self.showHighlighted()
        self.indicateNormal()
    
    def save(self, clear=True):
        """save - Sichert die Daten aus dem Formular in die DB
        
            Dabei bedient sich save dem SaverValues, das die Verbindung zur DB
            "kennt".
            
            Je nach clear (True/False) werden die Daten im Formular anschließend
            gelöscht oder neu aus der DB gelesen. Das ist für die Bedienung der UI
            hilfreich, beide Möglichkeiten zu haben.
            
            Parameter
                clear   bool
                        True:   Nach dem Speichern wird das Formular gelöscht,
                                außerdem wird in der Auswahlliste (OptionList)
                                highlighted auf None gesetzt
                        False:  Nach dem Speichern wird der gerade gespeicherte
                                Datensatz 
        """
        #
        # Die Werte als den letzten angezeigent Datensatz merken
        self.valuesLast = self.form.getValues()
        #
        # Daten speichern
        logging.debug(self.valuesLast)
        ergebnis = self.SaverValues(self.valuesLast)
        #
        # Ggf. Formular leeren
        if clear:
            self.form.clearValues()
            self.valuesLast = {}
            self.clearUnterformulare()
        #
        # Ggf. Auswahl Liste neu aufbauen
        if 'list' in self.elemente:
            self.buildChoices()
            # Ggf. das richtige Element in der Auswahlliste auswählen
            # und Datensatz neu anzeigen.
            if not clear:
                self.naviElemente['list'].setValue(self.valuesLast[self.keyFeldNavi])
                self.showHighlighted()
        # Ergebnis bearbeiten
        if type(ergebnis) == str:
            notify(ergebnis, 'Warnung')
        elif ergebnis is None:
            notify('Datensatz erfolgreich geändert.', 'Erfolg')
        elif type(ergebnis) == int:
            notify(f'Datensatz erfolgreich angelegt mit id={ergebnis}.', 'Erfolg')
        return ergebnis
    
    def delete(self):
        """delete - Löscht den angezeigten Datensatz aus der DB
        
            Dabei bedient sich delete dem DeleterValues, das die Verbindung zur
            DB kennt.
            
            Gelöscht wird nur, wenn der Datensatz eine ID hat. Ansonsten wird
            nur das Formular gelöscht und eine Nachricht gegeben.
        """
        #
        # Die Werte als den letzten angezeigten Datensatz merken
        #
        self.valuesLast = self.form.getValues()
        # ggf. Daten löschen
        if self.valuesLast['id']:
            notify(self.DeleterValues(self.valuesLast), 'Erfolg')
        else:
            notify('Kein Datensatz zu löschen', 'Warnung')
    
    def copy(self):
        """copy - Legt eine Kopie des Datensatzes neu an
        """
        #
        # Die Werte merken
        self.valuesLast = self.form.getValues()
        #
        # ID auf None setzen - es soll ja ein neuer Datensatz angelegt werden
        self.valuesLast['id'] = None
        #
        # Ein sinnvolles Feld im Datensatz suchen, in dem angezeigt werden kann,
        # dass es sich bei dem neuen Datensatz um eine Kopie eines alten handelt.
        for colName in (
                'name', 'titel',
                'bez', 'kurz_bez',
                'farbe', 'anrede',
                'bemerkung'
                ):
            if colName in self.valuesLast:
                if colName == 'kurz_bez':
                    self.valuesLast[colName] = self.valuesLast[colName][0] + '-'
                else:
                    self.valuesLast[colName] += ' (K)'
                break
        #
        # Den Datensatz speichern
        # ergebnis = self.SaverValues(self.valuesLast)
        #
        # Kopie anzeigen
        self.showValues(self.valuesLast)
        self.indicateChanged()
        
        return True
        
    def showValues(self, values):
        """_showValues - Zeigt die Werte aus Dict values im Formular
        
            Parameter
                values    Dict col_name --> value
                          dabei ist value jeweils in Python Type
        """
        self.updateSelects()
        self.form.setValues(values)
        # Versorge ggf. Unterformulare
        for listeName in self.formListen:
            # versorge die FormListe zu relation mit Formularen
            liste = self.formListen[listeName]
            linkFeld = liste.linkFeldHauptformular
            linkValue = self.form.getValue(linkFeld)
            dicts = liste.GetterDicts(linkValue)
            liste.build(dicts)
    
    def showFromDB(self, value):
        """showFromDB - Zeigt den Datensatz aus der DB zu value an
            
            Hat das Navi keine Auswahlliste, so muss es einen anderen Weg geben,
            das Formular mit den Daten eines Datensatzes zu füllen. Das erledigt
            showFromDB. value bezeichnet den Wert von self.keyFeldNavi, was i.d.R.
            id ist (sonst typischerweise kurz_bez o.ä.).
        """
        self.valuesLast = self.GetterValues(value)
        self.showValues(self.valuesLast)
    
    def showLast(self):
        """showLast - Zeigt den zuletzt angezeigten Datensatz erneut an
            
            Dabei werden die Werte erneut aus der DB geholt.
        """
        self.value = self.valuesLast[self.keyFeldNavi]
        self.showFromDB(self.value)
    
    def showHighlighted(self):
        """showHighlighted - Zeigt den Datensatz zum ausgewählten Listenelement an
        """
        value = self.naviElemente['list'].getValue()
        # value kann None sein. Nämlich z.B. dann, wenn nichts ausgewählt ist. Dieser
        # Fall kann eintreten, z.B. wenn die Auswahlliste neu aufgebaut wird, vorher aber
        # dort ein Element ausgewählt war; dann wird das Event ListboxSelect gefeuert
        # und dadurch letztlich showHighlighted versucht.
        if value:
            self.showFromDB(value)
    
    def updateSelect(self, col_name):
        """updateSelect - Versorgt das Widget zu col_name mit Auswahl
        
            Versorgt das Widget zu col_name mit Auswahl, falls es eine Auswahl gibt.
            Falls es zu col_name keine Möglichkeit gibt, eine Auswahl zu geben,
            wird eine Warnung gelogged.
            
            Parameter
                col_name    Spalte, zu der die Auswahl gefunden werden soll
        """
        self.form.updateSelect(col_name)
    
    def updateSelects(self):
        """updateSelects - Füllt relevante Select/Combobox Widgets mit Auswahl
        
            Geht die Felder durch, die einen GetterSelect haben und ruft dafür
            self.updateSelect auf.
        """
        self.form.updateSelects()
    
    def indicateChanged(self):
        """indicateChanged - Zeigt Changed Indicator
        
            Im Wesentlichen ruft indicateChanged für die relevanten
            Navi-Buttons deren Methode indicateChanged auf
        """
        self.buttons.configure(style='Changed.Navi.TFrame')
        
    def indicateNormal(self):
        """indicateNormal - Setzt Indicatoren zurück
        
            Im Wesentlichen ruft indicateNormal für die relevanten
            Navi-Buttons deren Methode indicateNormal auf.
        """
        self.buttons.configure(style='TFrame')
        self.form.iWasReset()
        
class BasisFormListe():
    """BasisFormListe - Grundlage für Listenansicht und -bearbeitung von Datensätzen
        
        BasisFormListe wird nicht direkt instanziiert, sondern es werden für
        verschiedene Anwendungen Klassen davon abgeleitet. Allerdings kodieren wir
        in BasisFormListe bereits das meiste an Funktionalität. Beim Programmieren
        zeigte sich, dass dadurch sehr viel weniger Methoden überladen werden müssen,
        stattdessen geht es durch einfache Fallunterscheidungen.
        
        BasisFormListe und alle abgeleiteten Klassen können als Kontextmanager
        verwendet werden. Das hat - wie bei Form - nur den Zweck der Optik.
        
        Typische Anwendungen sind:
        
            1. Zum Bearbeiten von Datensätzen in Listenform.
            
                  Das ist vor allem für Modelle/DB-Tabellen mit wenig Feldern
                  sinnvoll (Farben, Gruppen u.ä.).
                  Aber auch, wenn aus Modellen/DB-Tabelen nur ein (kleiner)
                  Teil der Felder bearbeitet werden sollen. Z.B. könnten das
                  die Finanzdaten eines Tagungsteilnehmers sein; oder zum
                  "schnellen" Erfassen neuer Datensätze, die dann später
                  nötigenfalls um weitere Daten ergänzt werden können.
                  
                  In diesem Fall wird die FormListe auch ein Navi haben, s.d. u.a.
                  die angezeigten Zeilen gefiltert werden können.
                  
            2. Zum Anzeigen/Bearbeiten von n-1-Relationen in "Unterformularen"
            
                  In diesem Fall gibt es ein "Haupformular", in dem z.B.
                  Personen angezeigt werden. In jeweils einem "Unterformular",
                  also jeweils einer FormListe, könnten Rollen/Gruppen und
                  Versandarten erfasst werden.
                  
                  In diesem Fall gibt es eine "Verknüpfung" zwischen Haupt- und
                  "Unterformular(en)". Diese Verknüpfung wird von dem Navi des
                  "Hauptformulars" organisiert. Insb. werden in der FormListe in
                  diesem Fall nur "passende" Daten aus der Tabelle angezeigt,
                  d.h. das entsprechende Key-Feld (Fremdschlüssel) hat immer
                  denselben Wert. Das Key-Feld kann, muss aber nicht, mit in
                  den Zeilen angezeigt werden. In jedem Fall sollte das entsprechende
                  Widget "readonly" sein. Vermutlich wird das Widget in jedem
                  Fall vohanden sein müssen, je nach dem wird es auf "unsichtbar"
                  gestellt oder einfach nicht angezeigt.
    
        BasisFormListe hält für jeden (relevanten, anzuzeigenden) Datensatz aus einem
        Modell (= DB-Tabelle) ein
        Formular. Diese Formulare sollen später untereinander gezeigt werden, s.d.
        eine Listenansicht der Datensätze entsteht und so viele Datensätze
        in der Übersicht erscheinen und bearbeitet werden können.
        
        Wir sprechen bei den Listenelementen von "Zeilen", angelehnt an die spätere
        Darstellung in Zeilen.
        
        Jede Zeile enthält ein eigenes Formular mit jeweils eigenem Navi (i.d.R. nur mit
        save und delete)
        
        Am Ende der Liste werden keine, ein oder mehrere leere Formulare
        zur Erfassung neuer Datensätze angefügt. Ein Attribut/Parameter
        legt fest, wieviele Zeilen es sein sollen. Je nach Verwendungszweck
        liegen Werte wie folgt nahe:
            >= 2    Hauptsächlich Erfassen von neuen Datensätzen
            =  1    Hauptsächlich Ändern bestehender Datensätze
            =  0    Ausschließlich Ändern bestehender Datensätze
        
        Features
        
            Factory
                Attribut factory
                
                FormListe bekommt eine Funktion, mit der jeweils ein neues Formular
                incl. Navi für die Liste hergestellt wird.
            
            Liste löschen
                Methode clear
                
                Löscht die Liste vollständig. Entfernt die Formulare außerdem
                aus dem targetContainer. Gibt alle verwendeten id frei.
            
            Liste der Formulare aufbauen
                Methode build
                
                Führt letztlich für jedes übergebene values-Dict factory aus und
                zeigt die entstandenen Formulare. Zusätzlich werden die angeforderten
                leeren Formulare am Ende eingefügt.
                
                WICHTIG: Mit Daten wird/werden das/die neue(n) Formula(e) vom
                Navi der FormListe gefüllt! (Oder eben auch nicht, wenn es
                am Ende der Liste leere Zeilen zum Erfassen neuer Datensätze
                geben soll.)
            
            Save all
                Methode saveAll - klären, ob das von Form oder von Navi organisiert wird.
                
                Löst für alle Zeilen, in denen Daten geändert wurden, save aus.
                Diese Funktion kann zusätzlich zu dem jeweils auf eine Zeile
                bezogenen/beschränkten save des jeweiligen Navis angeboten werden,
                um alle Änderungen auf einen Schlag zu erledigen. In diesem Fall
                könnte auf die (Anzeige der) Navis in den einzelnen Zeilen auch
                verzichtet werden.
                
                Klären, ob saveAll auch eine eventuelle Neueingabe erledigt.
        
        Parameter
            targetContainer   vgl. Attribute
            factory           Factory (Funktion), die für neue Zeilen je ein
                              Formular incl. Navi liefert.
                              
                              Diese Funktion muss dem Formular eine id erstellen,
                              die aus einer Basis-id und einer Ergänzung idAdd
                              (Parameter der Funktion) besteht. Beim Aufruf
                              ist idAdd so zu wählen, dass insg. eine eindeutige
                              id entsteht.
            
            emptyLines        Anzahl der leeren Formulare zur Erfassung neuer Datensätze
                              am Ende der Liste.
                              Vgl. Erläuterung oben
                              Typ: int
                              Default: 1
            
            linked            Boolean
                              Zeigt an, ob die Formularliste mit einem Hauptformular
                              verlinkt ist, also "Unterformular" ist.
        
        BEACHTE:  emptyLines und linked müssen als Named Parameter verwendet werden.
        Das deswegen, weil in abgeleiteten Klassen evt. weitere Parameter
        gefordert werden.
        
        Attribute
            targetContainer   Container, in dem die Formulare gezeigt werden sollen.
                              targetContainer wird i.d.R. ein Grid mit passender
                              Anzahl von Cols sein (pro Feld in den einzelnen
                              Formularen eine Col), kann aber jedes andere Widget
                              sein, das die Methode mount kennt.
            factory           s. Parameter
            emtyLines         s. Parameter
            linked            s. Parameter
            forms             Liste der Formulare
            
    """
    def __init__(self, targetContainer, factory, *, emptyLines=1, linked=False):
        #
        # Parameter merken
        self.targetContainer = targetContainer
        self.factory = factory
        self.emptyLines = emptyLines
        self.linked = linked
        #
        # Attribute initialisieren
        self.forms = []
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
    def setGetterDicts(self, getter):
        self.GetterDicts = getter
    
    def clear(self):
        """clear - Löscht alle Formulare aus der Liste
        
            Leert die Liste der Formulare incl. Label in der ersten Zeile
            und löscht sie aus dem Container.
            
            Die erste Zeile des Container bleibt - falls vorhanden - erhalten; dort
            finden sich die Label.
        """
        #
        # Lösche alle Widgets aus dem Grid
        for wdg in self.targetContainer.grid_slaves():
            wdg.grid_forget()
        #
        # Zerstöre alle Widgets aller Formulare.
        # Dabei wird per pop auch die Liste der Formulare nach und nach geleert.
        while len(self.forms):
            form = self.forms.pop()
            for colName in form.getColNames():
                form.getLabel(colName).destroy()
                form.getWidget(colName).destroy()
    
    def build(self, dicts=[]):
        """build - baut die Liste der Formulare neu auf und zeigt die Formulare
        
            Zunächst werden alle vorhandenen Formulare entfernt, incl. der
            Label in der ersten Zeile.
            
            Dann wird für jedes values-Dict aus dicts ein Formular erzeugt mit den
            entsprechenden Werten und angezeigt.
            
            Schließlich werden die erforderlichen leeren Formulare angehängt
            (vgl. self.emptyLines). Falls linked True ist, 
        """
        #
        # Vorhandene Formulare entfernen
        self.clear()
        #
        # Label
        form = self.factory()
        self.forms.append(form)
        column = 0
        for colName in form.getColNames():
            form.getLabel(colName).grid(row=0, column=column, sticky=tk.W)
            column += 1
        ttk.Label(self.targetContainer, text='Navi').grid(row=0, column=column, sticky=tk.W)
        #
        # Formulare mit Werten
        row = 1
        for values in dicts:
            form = self.factory()
            navi = form.getNavi()
            navi.updateSelects()
            self.forms.append(form)
            form.setValues(values)
            column = 0
            for colName in form.getColNames():
                form.getWidget(colName).grid(row=row, column=column)
                column += 1
            navi.grid(row=row, column=column)
            row += 1
            
        #
        # Leere Formulare
        for zaehler in range(self.emptyLines):
            form = self.factory()
            navi = form.getNavi()
            navi.updateSelects()
            self.forms.append(form)
            if self.linked:
                form.setValue(
                    self.linkFeld,
                    self.hauptformular.getValue(self.linkFeldHauptformular)
                    )
            column = 0
            for colName in form.getColNames():
                form.getWidget(colName).grid(row=row, column=column)
                column += 1
            navi.grid(row=row, column=column)
            row += 1

class FormListe(BasisFormListe):
    """FormListe - Listenansicht von Datensätzen zur Eingabe/Bearbeitung/Ansicht
    
        Erweitert BasisFormListe um
        
        1. Steuerung durch Navi
        
            FormListe erhält über die Methode setNavi ein Navi, über das insb. die
            angezeigten Formulare gefiltert werden können.
    """
    # Klassen Attribute
    FORMS = []
    def __init__(self, targetContainer, factory, *, emptyLines=1, remember=True):
        super().__init__(
            targetContainer=targetContainer,
            factory=factory,
            emptyLines=emptyLines,
            linked=False)
        # neue Instanz merken, wenn gewünscht
        self.remember = remember
        if remember:
            __class__.FORMS.append(self)
    
    def setNavi(self, navi):
        """
        """
        self._navi = navi
        self.getNavi().form = self
    
    def getNavi(self):
        return self._navi
        
    @staticmethod
    def resetForms():
        """resetForms - Setzt bestimmte Eigenschaften aller vorhandenen Instanzen
        """
        for form in __class__.FORMS:
            logger.debug('Nächste FormListe')
            navi = form.getNavi()
            if navi:
                if 'filter' in navi.elemente:
                    navi.naviElemente['filter'].delete(0, tk.END)
                navi.buildFormulare()
    
    @staticmethod
    def deleteFORMS():
        """deleteFORMS - löscht Liste der Instanzen
        """
        __class__.FORMS = []

class FormListeUnterformular(BasisFormListe):
    """FormListeUnterformular - Liste von Formularen für 1-n Relationen
    
        Erweitert BasisFormListe um...
        
        1. Verlinkung zum Hauptformular
              Über die Attribute linkFeld und linkFeldHauptformular wird die Beziehung
              zwischen den Daten des Unterformulars und des Hauptformulars beschrieben.
              
              Zur Anzeige von passenden Daten im Unterformular wird selektiert nach
              linkFeld = linkFeldHauptformular.
              
              Für neu angelegte Daten im Unterformular wird implizit
              linFeld = linkFeldHauptformular gesetzt.
        
        Attribute
            linkFeld                Feld, über das auf das Hauptformular gezeigt wird
                                    Bsp.: person_id
            linkFeldHauptformular   Feld im Hauptformular, auf das gezeigt wird
                                    Bsp.: id
    """
    def __init__(
            self,
            targetContainer,
            factory,
            *,
            emptyLines=1,
            linkFeld,
            linkFeldHauptformular):
        super().__init__(
            targetContainer=targetContainer,
            factory=factory,
            emptyLines=emptyLines,
            linked=True
            )
        #
        # Parameter merken
        self.linkFeld = linkFeld
        self.linkFeldHauptformular = linkFeldHauptformular
        
    def setHauptformular(self, hauptformular):
        self.hauptformular = hauptformular
