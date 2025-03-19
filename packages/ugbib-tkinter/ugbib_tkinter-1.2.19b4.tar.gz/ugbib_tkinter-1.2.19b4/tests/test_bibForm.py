import sys
sys.path.append('/home/ulrich/PythonHobby/bibs/bibtkinter/src/ugbib_tkinter/')

import pytest

from bibForm import *
glb.ICONS_PATH = './icons/'
glb.ICON_THEME = 'breeze'

import math
from decimal import Decimal
import datetime

import logging
from ugbib_werkzeug.bibWerkzeug import log_init
log_init('test_bibForm')
logger = logging.getLogger()

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

from PIL import ImageTk

class Main(tk.Tk):
    def __init__(self):
        super().__init__()

main = Main()

def test_contextManager():
    # nur klären, ob Form als Kontextmanager funktioniert
    with Form() as F:
        assert F._types == {}

def test_basics():
    for t in ['text', 'int', 'float', 'decimal', 'bool', 'datetime', 'date', 'time']:
        assert t in Form.TYPES
    F = Form()
    assert F._types == {}
    assert F._colNames == []
    assert F._navi is None
    assert F._getterAuswahl == {}
    assert str(F) == f'Form mit Widgets für {F._colNames}'
    assert F.getNavi() is None
    assert F.getColNames() == []
    assert not F.existsColName('name')
    with pytest.raises(ValueError):
        F.getWidget('name')
    assert F.getWidgets() == []

def test_addWidget():
    F = Form()
    #
    # Fehler klären
    #
    # name kein gültiger Python-Name
    with pytest.raises(ValueError):
        F.addWidget('vor-name', ttk.Entry(main), 'text')
    # name bereits vergeben
    with pytest.raises(ValueError):
        F.addWidget('name', ttk.Entry(main), 'text')
        F.addWidget('name', ttk.Entry(main), 'text')
    # name kollidiert mit Attribut von Form
    with pytest.raises(ValueError):
        F.addWidget('_navi', ttk.Entry(main), 'text')
    # ungültiger Typ
    with pytest.raises(ValueError):
        F.addWidget('xxx', ttk.Entry(main), 'Text')
    # widget ist kein Widget
    with pytest.raises(TypeError):
        F.addWidget('xxx', 'Kein Widget', 'text')
    #
    # Erfolgsfall: Rückgabewert, widget, colName und typ vorhanden
    #
    assert F.addWidget('vorname', ttk.Entry(main), 'text', label='Vorname') == 'vorname'
    assert len(F._colNames) == 2
    for col in ['name', 'vorname']:
        assert col in F.getColNames()
        assert F.getType(col) == 'text'
        assert isinstance(getattr(F, col), ttk.Widget)
    assert F.addWidget('alter', ttk.Entry(main), 'int') == 'alter'
    assert F.getType('alter') == 'int'
    for col in ['name', 'vorname', 'alter']:
        assert F.existsColName(col)
        assert isinstance(F.getWidget(col), ttk.Widget)
        assert isinstance(F.getLabel(col), ttk.Label)
    assert not F.existsColName('xxx')
    with pytest.raises(ValueError):
        F.getWidget('xxx')
    assert type(F.getWidgets()) == list
    for wdg in F.getWidgets():
        assert isinstance(wdg, ttk.Widget)
    # Fehlerhafte Einfügungen sind nicht in Verzeichnis gelandet
    for col in ['vor-name', 'navi', 'xxx']:
        assert col not in F.getColNames()
    #
    # Label Funktionalität
    #
    assert isinstance(F.lbl_name, ttk.Label)
    assert F.lbl_name['text'] == 'name'
    assert F.lbl_vorname['text'] == 'Vorname'
    F.addWidget('plz', ttk.Entry(main), 'text', ttk.Label(main, text='PLZ'))
    assert isinstance(F.lbl_plz, ttk.Label)
    assert F.lbl_plz['text'] == 'PLZ'
    assert F.getLabel('plz')['text'] == 'PLZ'

def test_valueGetSetClear():
    F = Form()
    
    F.addWidget('name', ttk.Entry(main), 'text')
    F.setValue('name', ' Ulrich ')
    assert F.getValue('name') == 'Ulrich'
    F.setValue('name', 'Goebel')
    assert F.getValue('name') == 'Goebel'
    F.clearValue('name')
    assert F.getValue('name') == ''
    
    F.addWidget('alter', ttk.Entry(main), 'int')
    F.setValue('alter', 56)
    assert F.getValue('alter') == 56
    F.clearValue('alter')
    assert F.getValue('alter') is None
    
    F.addWidget('bargeld', ttk.Entry(main), 'float')
    F.setValue('bargeld', 34.67)
    assert F.getValue('bargeld') == 34.67
    F.clearValue('bargeld')
    assert F.getValue('bargeld') is None
    
    F.addWidget('pi', ttk.Entry(main), 'decimal')
    F.setValue('pi', Decimal('3.1415926'))
    assert F.getValue('pi') == Decimal('3.1415926')
    F.clearValue('pi')
    assert F.getValue('pi') is None
    
    F.addWidget('boolEntry', ttk.Entry(main), 'bool')
    F.setValue('boolEntry', 'true')
    assert F.getValue('boolEntry')
    F.clearValue('boolEntry')
    assert F.getValue('boolEntry') is None
    
    F.addWidget(
        'boolCheck',
        ttk.Checkbutton(main), 'bool')
    F.setValue('boolCheck', True)
    assert F.getValue('boolCheck')
    F.clearValue('boolCheck')
    assert not F.getValue('boolCheck')
    
    F.addWidget('date', ttk.Entry(main), 'date')
    for date in ('13.01.1965', '1965-01-13'):
        F.setValue('date', datetime.date(1965, 1, 13))
        assert F.getValue('date') == datetime.date(1965, 1, 13)
    
    F.addWidget('time', ttk.Entry(main), 'time')
    F.setValue('time', datetime.time(23, 45))
    assert F.getValue('time') == datetime.time(23, 45)
    F.clearValue('date')
    assert F.getValue('date') is None
    F.clearValue('time')
    assert F.getValue('time') is None
    
    F.addWidget('datetime', ttk.Entry(main), 'datetime')
    F.setValue('datetime', datetime.datetime(2024, 10, 29, 23, 45))
    assert F.getValue('datetime') == datetime.datetime(2024, 10, 29, 23, 45)
    F.clearValue('datetime')
    assert F.getValue('datetime') is None
    
    # Die Combobox testen wir nur beispielhaft, da sie sich genau wie ein
    # Entry Widget verhalten sollte.
    F.addWidget('comboBox', ttk.Combobox(main), 'text')
    F.setValue('comboBox', 'Baustelle')
    assert F.getValue('comboBox') == 'Baustelle'
    F.clearValue('comboBox')
    assert F.getValue('comboBox') == ''
    
    # Listbox testen wir in einer eigenen Methode, siehe dort
    
    mustertext = 'Erste Zeile\nZweite Zeile\n\nVierte Zeile nach einer leeren Zeile'
    F.addWidget('text', tk.Text(main), 'text')
    assert F.getValue('text') == ''
    F.setValue('text', mustertext)
    assert F.getValue('text') == mustertext
    F.setValue('text', ' ' + mustertext + '\n\n')
    assert F.getValue('text') == mustertext
    F.clearValue('text')
    assert F.getValue('text') == ''
    F.addWidget('scrolledtext', scrolledtext.ScrolledText(main), 'text')
    assert F.getValue('text') == ''
    F.setValue('scrolledtext', mustertext)
    assert F.getValue('scrolledtext') == mustertext
    F.setValue('scrolledtext', ' ' + mustertext + '\n\n')
    assert F.getValue('scrolledtext') == mustertext
    F.clearValue('scrolledtext')
    assert F.getValue('scrolledtext') == ''
    #
    # Label
    F.addWidget('label', ttk.Label(main), 'text')
    F.setValue('label', '  Mein Text  ')
    assert F.getValue('label') == 'Mein Text'
    F.clearValue('label')
    assert F.getValue('label') == ''
    #
    # ComboboxValueLabel
    comboVL = ComboboxValueLabel(main)
    comboVL.fill(((1, 'Eins'), (2, 'Zwei'), ('3', 'Drei'), (4, None), (None, 'None')))
    F.addWidget('comboVL', comboVL, 'int')
    F.setValue('comboVL', 1)
    assert F.getValue('comboVL') == 1
    F.setValue('comboVL', None)
    assert F.getValue('comboVL') is None
    F.setValue('comboVL', '3')
    assert F.getValue('comboVL') == '3'
    F.clearValue('comboVL')
    assert F.getValue('comboVL') is None

def test_ListboxValueLabel():
    F = Form()
    # Zunächst erzeugen wir das Widget und testen dessen Funktionalität
    wdg = ListboxValueLabel()
    wdg.append(1, 'Eins')
    wdg.append(2, 'Zwei')
    wdg.append(3, 'Drei')
    assert wdg._lv['Eins'] == 1
    assert wdg._lv['Zwei'] == 2
    assert wdg._lv['Drei'] == 3
    wdg.setValue(2, exclusive=True)
    assert wdg.curselection() == (1,)
    assert wdg.getValue() == 2
    wdg.setValue(1, exclusive=True)
    wdg.setValue(3)
    assert wdg.curselection() == (0, 2)
    assert wdg.getValues() == [1, 3]
    
    wdg.clearValue()
    assert wdg.getValues() == []
    wdg.clear()
    assert wdg._lv == {}
    wdg.append(10, 'Zehn')
    wdg.append(11, 'Elf')
    wdg.append(12, 'Zwölf')
    wdg.append(13, 'Dreizehn')
    wdg.setValues((11, 13))
    assert wdg.getValues() == [11, 13]
    wdg.setValue(12)
    assert wdg.getValues() == [11, 12, 13]
    wdg.setValue(10, exclusive=True)
    assert wdg.getValue() == 10
    wdg.setValue(12)
    assert wdg.getValues() == [10, 12]
    wdg.clearValue()
    assert wdg.getValue() is None
    wdg.append(20, 'Zwanzig')
    wdg.setValue(20)
    assert wdg.getValue() == 20
    wdg.setValue(None)
    assert wdg.getValue() is None
    
    # Jetzt testen wir das in Form
    wdg.append(21, 'Einundzwanzig')
    wdg.append(22, 'Zweiundzwanzig')
    F.addWidget('listboxvl', wdg, 'int')
    F.setValue('listboxvl', 21)
    assert F.getValue('listboxvl') == 21
    F.setValue('listboxvl', (20, 22))
    assert F.getValue('listboxvl') == [20, 22]

def test_frameScrolledListbox():
    F = Form()
    F.addWidget('frmscrlistbox', FrameScrolledListbox(), 'text')
    wdg = F.getWidget('frmscrlistbox')
    # Typenprüfung bei append
    with pytest.raises(TypeError):
        wdg.append(45)
    # Werte einfügen
    for v in ('Eins', 'Zwei', 'Drei', 'Vier'):
        wdg.append(v)
    # noch nichts ausgewählt
    assert F.getValue('frmscrlistbox') is None
    # einen Wert auswählen
    F.setValue('frmscrlistbox', 'Zwei')
    assert F.getValue('frmscrlistbox') == 'Zwei'
    F.setValue('frmscrlistbox', 'Drei')
    assert F.getValue('frmscrlistbox') == 'Drei'
    # mehrere Werte
    F.setValue('frmscrlistbox', ('Eins', 'Vier'))
    assert F.getValue('frmscrlistbox') == ['Eins', 'Vier']
    # auf None setzen
    F.setValue('frmscrlistbox', None)
    assert F.getValue('frmscrlistbox') is None
    # clearValue nach mehreren Werten
    F.setValue('frmscrlistbox', ('Eins', 'Vier'))
    F.clearValue('frmscrlistbox')
    assert F.getValue('frmscrlistbox') is None

def test_frameScrolledListboxValueLabel():
    F = Form()
    F.addWidget('scrlistbox', FrameScrolledListboxValueLabel(), 'int')
    wdg = F.getWidget('scrlistbox')
    wdg.append(31, 'Einunddreißig')
    wdg.append(32, 'Zweiunddreißig')
    wdg.append(33, 'Dreiunddreißig')
    F.setValue('scrlistbox', 32)
    assert F.getValue('scrlistbox') == 32
    F.setValue('scrlistbox', (31, 33))
    assert F.getValue('scrlistbox') == [31, 33]
    F.setValue('scrlistbox', None)
    assert F.getValue('scrlistbox') is None
    F.setValue('scrlistbox', 32)
    F.clearValue('scrlistbox')
    assert F.getValue('scrlistbox') is None

def test_valuesAsDict():
    F = Form()
    F.addWidget('name', ttk.Entry(main), 'text')
    F.addWidget('alter', ttk.Entry(main), 'int')
    F.addWidget('veggi', ttk.Checkbutton(main), 'bool')
    F.addWidget('bem', scrolledtext.ScrolledText(main), 'text')
    F.setValue('name', 'Hans')
    F.setValue('alter', 34)
    F.setValue('veggi', True)
    F.setValue('bem', 'Zwei\nZeilen')
    values = F.getValues()
    assert values['name'] == 'Hans'
    assert values['alter'] == 34
    assert values['veggi']
    assert values['bem'] == 'Zwei\nZeilen'
    
    values = {'name': 'Moni', 'alter': 32, 'veggi': False}
    with pytest.raises(RuntimeError):
        F.setValues(values, check=True)
    F.setValues(values, keep=True)
    assert F.getValue('name') == 'Moni'
    assert F.getValue('alter') == 32
    assert not F.getValue('veggi')
    assert F.getValue('bem') == 'Zwei\nZeilen'
    F.setValues(values)
    assert F.getValue('bem') == ''
    values['bem'] = 'Drei\neinzelne\nZeilen'
    F.setValues(values)
    assert F.getValue('name') == 'Moni'
    assert F.getValue('alter') == 32
    assert not F.getValue('veggi')
    assert F.getValue('bem') == 'Drei\neinzelne\nZeilen'
    values['xxx'] = 'Unsinns'
    with pytest.raises(ValueError):
        F.setValues(values)

def test_widgetTypKompatibel():
    F = Form()
    with pytest.raises(ValueError):
        F.addWidget('x', ttk.Checkbutton(main), 'text')
    with pytest.raises(ValueError):
        F.addWidget('x', tk.Text(main), 'bool')
    with pytest.raises(ValueError):
        F.addWidget('x', scrolledtext.ScrolledText(main), 'bool')

def test_Validator():
    # valInt
    v = Validator.valInt
    assert v('')
    assert v('34')
    assert v('-89')
    assert not v('abc')
    assert not v('3.4')
    
    # valFloat
    v = Validator.valFloat
    assert v('')
    assert v('3.14')
    assert v('-3.14')
    assert not v('abc')
    
    # valDecimal
    v = Validator.valDecimal
    assert v('')
    assert v('3.14')
    assert v('-3.14')
    assert not v('abc')
    
    # valBool
    v = Validator.valBool
    assert v('')
    for t in TRUES:
        assert v(t)
        assert v(t.upper())
    assert not v('nein')
    assert not v('5')
    assert not v('Unsinn')
    
    # valDate
    v = Validator.valDate
    assert v('')
    assert v('13.01.1965')
    assert v('2002-12-31')
    assert not v('heute')
    assert not v('02.20.1955')
    assert not v('1955-20-02')
    
    # valDatetime
    v = Validator.valDatetime
    assert v('')
    assert not v('13.01.1965')
    assert not v('13.01.1965 22:35')
    assert v('2002-12-31 23:54')
    assert not v('jetzt')
    assert not v('02.20.1955')
    assert not v('1955-20-02 13:34')
    
    # valTime
    v = Validator.valTime
    assert v('')
    assert v('14:45')
    assert v('00:00')
    assert v('0:00')
    assert v('8:59')
    assert not v('34:12')
    assert not v('jetzt')

def test_ValidatorFactory():
    v = Validator.valNum
    assert v('')
    assert v('34')
    assert v('-28')
    assert v('3.1415926')
    assert v('-3.1415926')
    assert not v('hallo')
    
    v = Validator.valPositiv
    assert v('8')
    assert v('9.34')
    assert not v('-8')
    assert not v('-7.3')
    assert not v('hallo')
    
    v = Validator.valFactoryAnd(Validator.valNum, lambda x: float(x)>4 and float(x)<15)
    assert v('8')
    assert v('9.69')
    assert not v('4')
    assert not v('15')
    assert not v('2')
    assert not v('20')
    assert not v('hallo')
    
    v = Validator.valFactoryNot(Validator.valPositiv)
    assert v('0')
    assert not v('345')

def test_NaviForm():
    F = Form()
    glb.icons = TkIcons()
    N = NaviForm(main)
    Auswahl = N.naviElemente['list'].Listbox._lv
    for element in NaviWidget.GUELTIGE_ELEMENTE:
        assert element in N.elemente
    assert len(Auswahl) == 0
    N.optionsAppend(1, 'Eins')
    N.optionsAppend(2, 'Zwei')
    assert len(Auswahl) == 2
    N.optionsClear()
    assert len(Auswahl) == 0
    N.optionsAppend(((10, 'Zehn'), (11, 'Elf'), (12, 'Zwölf')))
    assert len(Auswahl) == 3

def test_ComboboxValueLabel():
    cb = ComboboxValueLabel(main, values=('Meise', 'Amsel'))
    assert isinstance(cb, ttk.Combobox)
    assert type(cb) == ComboboxValueLabel
    assert len(cb._lv) == 0
    with pytest.raises(RuntimeError):
        assert cb.getValue() == ''
    cb.append(1)
    assert len(cb._lv) == 1
    assert 1 in cb._lv.values()
    assert '1' in cb._lv
    cb.clear()
    assert len(cb._lv) == 0
    cb.fill(((1, 'Eins'), (2, 'Zwei'), ('3', 'Drei'), (4, None), (None, 'None')))
    assert len(cb._lv) == 5
    assert [v for v in cb._lv.values()] == [1, 2, '3', 4, None]
    assert [l for l in cb._lv.keys()] == ['Eins', 'Zwei', 'Drei', '4', 'None']
    assert cb.getValue() is None
    cb.setValue(2)
    assert cb.getValue() == 2
    cb.setValue('3')
    assert cb.getValue() == '3'
    cb.setValue(1)
    assert cb.getValue() == 1
    cb.setValue(4)
    assert cb.getValue() == 4
    cb.setValue(None)
    assert cb.getValue() is None
    with pytest.raises(ValueError):
        cb.setValue(3)

def test_BasisFormListe():
    Main = tk.Tk()
    frameNavi = ttk.Frame(main)
    frameNavi.pack(side=tk.TOP)
    frameScrolledListe = yScrolledFrame(main)
    frameScrolledListe.pack(side=tk.TOP)
    frameListe = frameScrolledListe.innerFrame
    
    glb.icons = TkIcons()
    
    def fake():
        return
    
    def factory():
        form = Form()
        form.addWidget(
            'id',
            ttk.Entry(frameListe, width=5, justify=tk.RIGHT),
            'int',
            label=ttk.Label(frameListe, text='ID'))
        form.addWidget(
            'name',
            ttk.Entry(frameListe, width=15),
            'text',
            label=ttk.Label(frameListe, text='Name', width=15))
        form.addWidget(
            'vorname',
            ttk.Entry(frameListe, width=15),
            'text',
            label=ttk.Label(frameListe, text='Navi'))
        navi = NaviForm(frameListe, elemente=('save', 'delete'))
        form.setNavi(navi)
        return form
    
    dicts = [
        {'id': 1, 'name': 'Walkes', 'vorname': 'Otto'},
        {'id': 2, 'name': 'Hü', 'vorname': 'Hotte'},
        {'id': 3, 'name': 'Ente', 'vorname': 'Lahme'},
        {'id': 4, 'name': 'Duck', 'vorname': 'Donald'},
        {'id': 5, 'name': 'König', 'vorname': 'Frosch'},
        ]
    
    fl = BasisFormListe(frameListe, factory, emptyLines=2)
    assert isinstance(fl.targetContainer, ttk.Frame)
    assert fl.targetContainer == frameListe
    assert fl.factory == factory
    assert fl.emptyLines == 2
    assert fl.forms == []
    fl.build(dicts=dicts)
    assert fl.forms[1].getValue('id') == 1
    assert fl.forms[6].getValue('id') is None
    assert len(fl.forms) == 8
    
    fl.clear()
    assert fl.forms == []
    fl.build(dicts=dicts)
    assert len(fl.forms) == 8
    
    # Main.mainloop()

def test_EmbeddedIcons():
    glb.icons = TkIcons()
    helpIcon = glb.icons.getIcon('system-help')
    assert type(helpIcon) == ImageTk.PhotoImage
    assert 'oxygen' in glb.icons.getThemes()
    assert 'breeze' in glb.icons.getThemes()
    helpIcon = glb.icons.getIcon('system-help', size='small')
    assert type(helpIcon) == ImageTk.PhotoImage
    