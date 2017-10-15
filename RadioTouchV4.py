#!/usr/bin/python
# -*- coding: UTF-8 -*-

# -----------------------------------------------------------------------------------------------------
# Raspberry Pi Webradio mit pygame Oberfläche
# -----------------------------------------------------------------------------------------------------
# Autor   : Peter Schneider
# Python  : Python 2
# Datum   : 11.07.2017
# -----------------------------------------------------------------------------------------------------
# Dies ist ein Übungsprojekt um die Programmierung des Raspberry Pi unter Python zu erlernen.
# Ein paar Dinge sind zur Funktion notwendig
#   sudo apt-get install mpd mpc
#   sudo apt-get install python-pip
#   sudo apt-get install python2.7-dev
#   sudo apt-get install python-pygame
#   sudo apt-get -y purge python-kaa-imlib2 python-kaa-base python-mpd
#   sudo pip install python-mpd2
#   sudo apt-get install ttf-mscorefonts-installer
# -----------------------------------------------------------------------------------------------------

import pygame
from pygame.locals import *
import time
import datetime
import sys
import os
import subprocess
import json
import urllib2
import socket

from mpd import MPDClient

os.environ["SDL_FBDEV"]    = "/dev/fb1"
os.environ["SDL_MOUSEDRV"] = "TSLIB"
os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"

# font
SysFontPath = "/usr/share/fonts/truetype/msttcorefonts/arial.ttf"

# -----------------------------------------------------------------------------------------------------

WindowBreite = 320			   # Displagröße 320 x 240 Pixel (Adafruit Touch 2,8 Zoll)
WindowHoehe  = 240

HoeheInfo1   = 39          # Definiere Info Bereich 1 - oberer Bildschirmbereich
BreiteInfo1  = WindowBreite

HoeheButton  = 35
BreiteButton = 100
MitteButton  = ((BreiteButton / 2), (HoeheButton / 2))

HoehePanel   = 135          # definiere Button Bereich
BreitePanel  = WindowBreite

HoeheInfo2   = 66           # definiere Info Bereich 2 - unterer Bildschirmbereich  
BreiteInfo2  = WindowBreite 

LineSpace = 9
LineSpaceText = 17
CollumSpace = 9

PanelOffset = (0, HoeheInfo1 + LineSpace)
Info2Offset = (0, PanelOffset[1] + HoehePanel + LineSpace - 5)

ButtonPosition = [(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0),(0,0)]

TitleSize   = (0, 0)
ChannelSize = (0, 0) 

BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
BLUE   = (  0,   0, 255)
YELLOW = (255, 255,   0)
GREEN1 = ( 69, 132,   0)

ACTIVE   = GREEN  # (255, 0, 0)
NOACTIVE = GREEN1 # ( 60, 0, 0)

# Button Texte für Menü 1
ButonListM01 = [
  # Spalte 1
  "Play".decode("utf8"),		
  "Stop".decode("utf8"),
  "Info".decode("utf8"),
  # Spalte 2    
  "Station +".decode("utf8"),   
  "Station -".decode("utf8"),
  "Radio Aus".decode("utf8"),
  # Spalte 3   
  "Volume +".decode("utf8"),
  "Volume -".decode("utf8"),
  "Schließen".decode("utf8")
]

# Button Beschriftung Menü 2
ButonListM02 = [
  # Spalte 1
  "WLAN Info".decode("utf8"),
  " ".decode("utf8"), 
  "Zurück".decode("utf8"),
  # Spalte 2
  "Stream URL".decode("utf8"),
  " ".decode("utf8"),
  " ".decode("utf8"),
  # Spalte 3
  "Wetter Info".decode("utf8"),
  " ".decode("utf8"),
  " ".decode("utf8"),
]

ButtonText = ["11", "12", "13", "21", "22", "23", "31", "32", "33"]

# OpenWeatherMap city-ID - gibt den Ort für die Wetterdaten an
# Zu ermitteln über http://openweathermap.org
OWM_ID = '1234567'

# API-Key für die OpenWeatherMap API
# Der Key kann einfach über http://openweathermap.org/appid
# angefordert werden. Der Key ist hier als String anzugeben
OWM_KEY = '1234567890abcdef1234567890abcdef'

# -----------------------------------------------------------------------------------------------------

ReadData     = 0
StreamTitle  = "Warte auf neuen Titel".decode("utf8")
TextPowerOff = "Radio wird ausgeschaltet".decode("utf8")
ActiveMenue  = 1

TitelScrolling = 0
ChannelScrolling = 0
StreamUrlScrolling = 0
ZeitScrolling = 0

M02ShowStreamUrl = False
M02ShowWlanInfo  = False
M02ShowWetter    = False

TimeOutScreenSaver  = 0;
TimeOutButtonAktive = 0;
ScreenSaver = False

# Wetterdaten
Stadt       = 'n/a'
Temperatur  = '-'
Luftdruck   = '-'
Luftfeuchte = '-'
Wetterlage  = 'na'
Heute_min   = '-'
Heute_max   = '-'
Morgen_min  = '-'
Morgen_max  = '-'
Vorschau    = 'na'

# Pfad zum Programmverzeichnis
ScriptPath = os.path.dirname(__file__)

# Pfad zu den Button und Imagedateien des Skins
WeatherPath = os.path.join(ScriptPath,"wetter")

"""
try:
  d = open("/etc/network/interfaces","r")
  Daten = d.read()
  print(Daten)
except:
  print("Dateizugriff nicht erfolgreich")
"""

# -----------------------------------------------------------------------------------------------------
# Funktionen 
# -----------------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------------
# Wetterinformation vom Internet lesen 
# -----------------------------------------------------------------------------------------------------
def GetWetterInfo(OWM_ID, OWM_KEY):
  global Stadt
  global Temperatur
  global Luftdruck
  global Luftfeuchte
  global Wetterlage
  global Heute_min
  global Heute_max
  global Morgen_min
  global Morgen_max
  global Vorschau

  print("GetWetterInfo")
  
  if not OWM_KEY:
    waiting('Please get an API-Key from','openweathermap.org/appid')
    pygame.time.wait(5000)
    event = pygame.event.get() # werfe aufgelaufene Events weg

  OpenWeatherBase = 'http://api.openweathermap.org/data/2.5/'

  try:
    Wetter = urllib2.urlopen(OpenWeatherBase + 'weather?id=' + OWM_ID + '&units=metric&lang=de&mode=json&APPID=' + OWM_KEY)
    WetterDaten = json.load(Wetter)
    Stadt = WetterDaten['name']
    Temperatur = str(int(round(WetterDaten['main']['temp'],0))) #  - 273.15 if units!=metric
    Luftdruck = str(int(WetterDaten['main']['pressure']))
    Luftfeuchte = str(int(WetterDaten['main']['humidity']))
    Wetterlage = WetterDaten['weather'][0]['icon']
  except:
    print datetime.datetime.now().strftime('%H:%M') + ': No Weather Data.'

  try:
    pygame.time.wait(150) # Warte 150ms um HttpError 429 zu vermeiden
    daily = urllib2.urlopen(OpenWeatherBase + 'forecast/daily?id=' + OWM_ID + '&units=metric&lang=de&mode=json&APPID=' + OWM_KEY)
    daily_data = json.load(daily)
    Heute_min = str(round(daily_data['list'][0]['temp']['min'],1))
    Heute_max = str(round(daily_data['list'][0]['temp']['max'],1))
    Morgen_min = str(round(daily_data['list'][1]['temp']['min'],1))
    Morgen_max = str(round(daily_data['list'][1]['temp']['max'],1))
    Vorschau = daily_data['list'][1]['weather'][0]['icon']
  except:
    print datetime.datetime.now().strftime('%H:%M') + ': No Forecast Data.'
    
# -----------------------------------------------------------------------------------------------------
# Wetterinformation anzeigen 
# -----------------------------------------------------------------------------------------------------
def ShowWetterInfo():
  InfoLabel = font3.render("Aktuelles Wetter in ".decode("utf8") + Stadt, 1, RED)
  Info2Screen.blit(InfoLabel, (0, 0))	  
  InfoLabel = font3.render("Temperatur : ".decode("utf8") + Temperatur + "°C".decode("utf8"), 1, RED)
  Info2Screen.blit(InfoLabel, (0, LineSpaceText))	  
  InfoLabel = font3.render("Luftdruck : ".decode("utf8") + Luftdruck + "mbar".decode("utf8"), 1, RED)
  Info2Screen.blit(InfoLabel, (0, LineSpaceText * 2))	  
  
  # Zeige Wetter Icon von heute
  icon = os.path.join(WeatherPath, Wetterlage + '.png')
 
  if not os.path.exists(icon):
    icon = os.path.join(WeatherPath, 'na.png')
   
  IconPosition = (((BreiteInfo2 - (BreiteInfo2 / 3)) + (HoeheInfo2 / 2)), 0) 
  icon = pygame.image.load(icon).convert_alpha()
  icon = pygame.transform.smoothscale(icon,(HoeheInfo2 - 10, HoeheInfo2 - 10))
  Info2Screen.blit(icon, IconPosition)
 
# -----------------------------------------------------------------------------------------------------
# Wetterinformation mit Wettervorhersage anzeigen 
# -----------------------------------------------------------------------------------------------------
def ShowWetterInfoAll():
  Hoehe  = HoeheInfo1 + 20
  Info1  = 0 + (BreitePanel / 4) - (WindowHoehe / 4)
  Info2  = 3 * (BreitePanel / 4) - (WindowHoehe / 4)
  Zeile1 = HoeheInfo1 + (WindowHoehe / 2) + 20
  Zeile2 = Zeile1 + LineSpaceText
  Zeile3 = Zeile2 + LineSpaceText
 
  window.fill(BLACK)
  
  # Überschrift   
  lt = time.localtime()
  String   = "Wettervorhersage für ".decode("utf8") + Stadt
  Size     = fontM.size(String)
  Label    = fontM.render(String, 1, RED)
  Position = (((WindowBreite / 2) - (Size[0] / 2)), 0) 
  window.blit(Label, Position)

  String   = time.strftime("%d. %B %G - %T", lt)
  Size     = fontM.size(String)
  Label    = fontM.render(String, 1, RED)
  Position = (((WindowBreite / 2) - (Size[0] / 2)), (Size[1] + 8))
  window.blit(Label, Position)
  
  # Zeige Wetter Icon von heute
  icon = os.path.join(WeatherPath, Wetterlage + '.png')
  if not os.path.exists(icon):
    icon = os.path.join(WeatherPath, 'na.png')
   
  Position = (Info1, Hoehe)
  icon = pygame.image.load(icon).convert_alpha()
  icon = pygame.transform.smoothscale(icon, (WindowHoehe / 2, WindowHoehe / 2))
  window.blit(icon, Position)
 
  # schreibe Text zu Wetter heute
  String = "Heute"
  Size   = font3.size(String) 
  Label  = font3.render(String, 1, RED)
  Position = ((BreitePanel / 4) - (Size[0] / 2), Zeile1)
  window.blit(Label, Position)
  
  String = Heute_min + "°C - ".decode("utf8") + Heute_max + "°C".decode("utf8")
  Size   = font3.size(String) 
  Label  = font3.render(String, 1, RED)
  Position = ((BreitePanel / 4) - (Size[0] / 2), Zeile2)
  window.blit(Label, Position)

  # Zeige Wetter Icon von morgen
  icon = os.path.join(WeatherPath, Vorschau + '.png')
  if not os.path.exists(icon):
    icon = os.path.join(WeatherPath, 'na.png')
  
  Position = (Info2, Hoehe)
  icon = pygame.image.load(icon).convert_alpha()
  icon = pygame.transform.smoothscale(icon, (WindowHoehe / 2, WindowHoehe / 2))
  window.blit(icon, Position)
 
  # schreibe Text zu Wetter morgen
  String = "Morgen"
  Size   = font3.size(String) 
  Label  = font3.render(String, 1, RED)
  Position = (3 * (BreitePanel / 4) - (Size[0] / 2), Zeile1)
  window.blit(Label, Position)
  
  String = Morgen_min + "°C - ".decode("utf8") + Morgen_max + "°C".decode("utf8")
  Size   = font3.size(String) 
  Label  = font3.render(String, 1, RED)
  Position = (3 * (BreitePanel / 4) - (Size[0] / 2), Zeile2)
  window.blit(Label, Position)
  
  # schreibe Screen auf das Display
  pygame.display.flip()

  
# -----------------------------------------------------------------------------------------------------
# Lese IP Adresse 
# -----------------------------------------------------------------------------------------------------
def GetIpAdr():
  # get and display ip
  IpAdrData = subprocess.check_output('hostname -I', shell=True)
  return(IpAdrData.decode("UTF-8")[:-1])
  
# -----------------------------------------------------------------------------------------------------
# Verbindung zum mpd herstellen
# -----------------------------------------------------------------------------------------------------
def ConnectMpd():
  try:
    mpd = MPDClient()               			# create client object
    mpd.timeout = 10                			# network timeout in seconds (floats allowed), default: None
    mpd.idletimeout = None          			# timeout for fetching the result of the idle command is handled seperately, default: None
    mpd.connect("localhost", 6600)  			# connect to localhost:6600
    mpd.play()                                  # starte Wiedergabe der Playlist
    MpdStatus = mpd.status()
    print("connected using unix socket...")    
    print("mpd Version : " + mpd.mpd_version)   # print the MPD version
    #print(MpdStatus)
    #print(mpd.playlistinfo())
    #print(mpd.stats())
    #print(mpd.playlist())
    #print(mpd.decoders())
    #print(mpd.currentsong())
  except mpd.ConnectionError as e:
     if str(e) == 'Already connected':
       # Das folgende disconnect() schlägt fehl (broken pipe)
       # obwohl von python_mpd2 'Already connected' gemeldet wurde
       # Aber erst ein auf das disconnect() folgender connect()
       # ist erfolgreich...
      try:
        mpd.disconnect()
        pygame.time.wait(1500)
        ConnectMpd()
      except socket.error:
        ConnectMpd()
  except socket.error as e:
    # socket.error: [Errno 111] Connection refused
    # socket.error: [Errno 2] No such file or directory
    # print str(e)
    try:
      # Nötig, um einen 'service mpd restart' zu überstehen
      pygame.time.wait(1500)
      print("connected using localhost:6600")
    except:
      e, v = sys.exc_info()[:2]
      print(str(e) + ': ' + str(v))
      print("restarting mpd...")
      subprocess.call("sudo service mpd restart", shell=True)
      pygame.time.wait(1500)
      ConnectMpd()

  return(mpd, MpdStatus)

# -----------------------------------------------------------------------------------------------------
# Power Off
# -----------------------------------------------------------------------------------------------------
def PowerOff():
  mpd.stop()
  LabelPowerOff = fontM.render(TextPowerOff, 1, RED)
  TextSize = fontM.size(TextPowerOff)
  window.fill(BLACK)
  window.blit(LabelPowerOff, (((WindowBreite / 2) - (TextSize[0] / 2)), ((WindowHoehe / 2) - (TextSize[1] / 2))))
  pygame.display.flip()
  time.sleep(3)
  window.fill(BLACK)
  pygame.display.flip()
  
  pygame.quit()
  subprocess.call('sudo poweroff', shell=True)

# -----------------------------------------------------------------------------------------------------
# Text ausgeben als Scrolltext oder Normal je nach Textlänge
# -----------------------------------------------------------------------------------------------------
# Parameter
#  	Szurface   aktueller Surface zum Anzeigen des Textes
#   Label      aktueller Text
#   Size	     Textlägne 
#   Pos        Position der Schrift
#   Width      Fesnterbreite
#   Vel        Scrollgeschwindigkeit
#
# Rückgabe
#   Aktueller Scrollwert
# -----------------------------------------------------------------------------------------------------
# Zur Funktion :
# Damit der Text kontinuierlich durch das Fenster scrollt, muss er evtl. 2 mal mit unterschidlichen
# Startpositionen ausgegeben werden. Der Text scrollt links aus dem Fenster herraus und scrollt rechts 
# wieder ins Fenster hinein (2. Ausgabe des Textes)
# -----------------------------------------------------------------------------------------------------
def ScrollText(Surface, Label, Size, Pos, Width, Scrolling, Vel):
  ScrollSpace = 30
   
  if Size > Width:                                          # Prüfe ob Scrollen notwendig ist
    Scrolling = Scrolling - Vel								# Text nach links scrollen
    Surface.blit(Label, (Scrolling, Pos))                   # gescrollter Text ins Surface schreiben 1. Ausgabe
    NewLine = Scrolling + Size								
    if NewLine < (Width - ScrollSpace):						
      Surface.blit(Label, (NewLine + ScrollSpace, Pos))     # 2. Ausgabe des Textes
    if (NewLine + ScrollSpace) < 0:
      Scrolling = 0 
  else:
    Scrolling = 0
    Surface.blit(Label, (0, Pos))
  
  return (Scrolling)

# -----------------------------------------------------------------------------------------------------
# WLan Level 
# -----------------------------------------------------------------------------------------------------
def GetWlanLevel():
  level = 0
  with open('/proc/net/wireless') as f:
    for line in f:
      wlan = line.split()
      if wlan[0] == 'wlan0' + ':':
        value = float(wlan[3])
        if value < 0:
          # Näherungsweise Umrechnung von dBm in %
          # -35dBm -> 100, -95dBm -> 0
          level = int((value + 95)/0.6)
        else:
          level = int(value)
  return level

# -----------------------------------------------------------------------------------------------------
# Bildschirmschoner
# -----------------------------------------------------------------------------------------------------
def ShowScreenSaver():
  global ZeitScrolling

  ShowWetterInfoAll()
  """
  lt = time.localtime()
  window.fill(BLACK)
  UhrZeitString = time.strftime("%A, %d. %B %G, %T", lt)
  UhrZeitSize = fontM.size(UhrZeitString)
  UhrZeitSizeLabel = fontM.render(UhrZeitString, 1, RED)
  ZeitScrolling = ScrollText(window, UhrZeitSizeLabel, UhrZeitSize[0], (WindowHoehe / 2) - (UhrZeitSize[1] / 2), WindowBreite, ZeitScrolling, 2)
  pygame.display.flip()
  """

# -----------------------------------------------------------------------------------------------------
# Berechnen die Position der Buttons 
# -----------------------------------------------------------------------------------------------------
def CalcButtonPosition():
  # Berechnen Position der Buttons
  ButtonZeile = [0, 0, 0] 
  
  for i in range(len(ButtonZeile)):
    ButtonZeile[i] = i * (HoeheButton + LineSpace)
      	  
  k = 0
  for i in range(len(ButtonZeile)):
    ButtonPosition[k] = (((i * BreiteButton) + CollumSpace * i), ButtonZeile[0])
    k = k + 1
    ButtonPosition[k] = (((i * BreiteButton) + CollumSpace * i), ButtonZeile[1])
    k = k + 1
    ButtonPosition[k] = (((i * BreiteButton) + CollumSpace * i), ButtonZeile[2])
    k = k + 1
        	
# -----------------------------------------------------------------------------------------------------
# Setze Texte für Buttons  
# -----------------------------------------------------------------------------------------------------
def SetButtonTextMenue(ButtonList):
  # Button Beschriftung Menü 1
  for i in range(len(ButtonList)):
    ButtonText[i] = ButtonList[i]

# -----------------------------------------------------------------------------------------------------
# Zeichen die Buttons 
# -----------------------------------------------------------------------------------------------------
def DrawButtons():
  global ButtonSurface
  global labelText
   
  labelText     = [0, 1, 2, 3, 4, 5, 6, 7, 8]        # Dummy Befüllung damit die Liste eine Länge hat
  ButtonSurface = [0, 1, 2, 3, 4, 5, 6, 7, 8]   
  
  
  PanelScreen.fill(BLACK)
  window.fill(BLACK)   
  
  # definiere Button Surface BS
  ButtonRect = (BreiteButton, HoeheButton)

  for i in range(len(labelText)):
    labelText[i] = fontT.render(ButtonText[i], 1, YELLOW)
    ButtonSurface[i] = (pygame.Surface(ButtonRect)) 
    ButtonSurface[i].fill(NOACTIVE)
    StartPos = fontT.size(ButtonText[i])
    ButtonSurface[i].blit(labelText[i], ((MitteButton[0] - (StartPos[0] / 2)), (MitteButton[1] - (StartPos[1] / 2))))
    PanelScreen.blit(ButtonSurface[i], ButtonPosition[i])
  
  pygame.draw.line(PanelScreen, BLUE, (0, HoehePanel - 3), (BreitePanel, HoehePanel - 3))
  window.blit(PanelScreen, PanelOffset)

# -----------------------------------------------------------------------------------------------------
# Markiere einen Button als "betätigt" 
# -----------------------------------------------------------------------------------------------------
def MarkButtonAktiv(Number):
  global ButtonText
  global ButtonSurface
  global labelText
  	
  ButtonSurface[Number].fill(RED)
  StartPos = fontT.size(ButtonText[Number])
  ButtonSurface[Number].blit(labelText[Number], ((MitteButton[0] - (StartPos[0] / 2)), (MitteButton[1] - (StartPos[1] / 2))))
  PanelScreen.blit(ButtonSurface[Number], ButtonPosition[Number])
  window.blit(PanelScreen, PanelOffset)

# -----------------------------------------------------------------------------------------------------
# Prüfe ob Taste gedrückt wurde
# -----------------------------------------------------------------------------------------------------
def CheckForButtonTouch(TouchPosition, ButtonPosition):
  if ButtonPosition[0] <= TouchPosition[0] <= (ButtonPosition[0] + BreiteButton): 
    Touch1 = True
  else:
	Touch1 = False
	      
  if ButtonPosition[1] <= TouchPosition[1] <= (ButtonPosition[1] + HoeheButton):     
    Touch2 = True
  else:
    Touch2 = False
    
  Touch = Touch1 and Touch2  	  	
  return (Touch)
	
# -----------------------------------------------------------------------------------------------------
# Prüfe welche Taste gedrückt wurde (Touch Menü 1)
# -----------------------------------------------------------------------------------------------------
def OnTouchMenue01(MausPosIn):
  global ActiveMenue
   
  MausPos = (MausPosIn[0], MausPosIn[1] - PanelOffset[1]) 

  # Spalte 1
  # Play
  if CheckForButtonTouch(MausPos, ButtonPosition[0]) == True:  
    MarkButtonAktiv(0)
    mpd.play()  
  # Stop
  if CheckForButtonTouch(MausPos, ButtonPosition[1]) == True:  
    MarkButtonAktiv(1)     
    mpd.stop() 
  # Funktionen
  if CheckForButtonTouch(MausPos, ButtonPosition[2]) == True:    
    MarkButtonAktiv(2)
    SetButtonTextMenue(ButonListM02)
    DrawButtons()
    ActiveMenue = 2

  # Spalte 2
  # Station +
  if CheckForButtonTouch(MausPos, ButtonPosition[3]) == True:    
    MarkButtonAktiv(3)
    if int(CurrentSong.get('id', '0')) == int(MpdStatus.get('playlistlength', '0')):    
      mpd.playid(1)
    else:
      mpd.next() 
  # Station -
  if CheckForButtonTouch(MausPos, ButtonPosition[4]) == True:    
    MarkButtonAktiv(4)
    if int(CurrentSong.get('id', '0')) == 1:
      mpd.playid(int(MpdStatus.get('playlistlength', '0')))     
    else:
      mpd.previous() 
  # Radio Ausschalten
  if CheckForButtonTouch(MausPos, ButtonPosition[5]) == True:        
    MarkButtonAktiv(5)
    mpd.stop() 
    PowerOff()

  # Spalte 3
  # set volume +
  if CheckForButtonTouch(MausPos, ButtonPosition[6]) == True:              
    MarkButtonAktiv(6)
    AktVolume = MpdStatus.get('volume', '0')
    if (int(AktVolume) + 5) < 100:
      mpd.setvol(int(AktVolume) + 5)
    else:
      mpd.setvol(100)
  # Volume -
  if CheckForButtonTouch(MausPos, ButtonPosition[7]) == True:     
    MarkButtonAktiv(7)
    AktVolume = MpdStatus.get('volume', '0')
    if (int(AktVolume) - 5) > 0:
      mpd.setvol(int(AktVolume) - 5)
    else:
      mpd.setvol(0)
  # Programm Schließen
  if CheckForButtonTouch(MausPos, ButtonPosition[8]) == True:         
    MarkButtonAktiv(8)
    pygame.quit()

# -----------------------------------------------------------------------------------------------------
# Prüfe welche Taste gedrückt wurde (Touch Menü 2)
# -----------------------------------------------------------------------------------------------------
def OnTouchMenue02(MausPosIn):
  global ActiveMenue
  global M02ShowStreamUrl
  global M02ShowWlanInfo
  global M02ShowWetter
   
  M02ShowStreamUrl = False
  M02ShowWlanInfo  = False
  M02ShowWetter    = False
  
  MausPos = (MausPosIn[0], MausPosIn[1] - PanelOffset[1]) 

  # Spalte 1
  if CheckForButtonTouch(MausPos, ButtonPosition[0]) == True:    
    MarkButtonAktiv(0)
    M02ShowWlanInfo = True
  if CheckForButtonTouch(MausPos, ButtonPosition[1]) == True:        
    MarkButtonAktiv(1)
  if CheckForButtonTouch(MausPos, ButtonPosition[2]) == True:    
    MarkButtonAktiv(2)
    M02ShowStreamUrl = False
    SetButtonTextMenue(ButonListM01)
    DrawButtons()
    ActiveMenue = 1

  # Spalte 2
  if CheckForButtonTouch(MausPos, ButtonPosition[3]) == True:      
    MarkButtonAktiv(3)
    M02ShowStreamUrl = True
  if CheckForButtonTouch(MausPos, ButtonPosition[4]) == True:       
    MarkButtonAktiv(4)
  if CheckForButtonTouch(MausPos, ButtonPosition[5]) == True:         
    MarkButtonAktiv(5)

  # Spalte 3
  if CheckForButtonTouch(MausPos, ButtonPosition[6]) == True:       
    MarkButtonAktiv(6)
    M02ShowWetter = True
  if CheckForButtonTouch(MausPos, ButtonPosition[7]) == True:    
    MarkButtonAktiv(7)
  if CheckForButtonTouch(MausPos, ButtonPosition[8]) == True:         
    MarkButtonAktiv(8)
    
# -----------------------------------------------------------------------------------------------------
# schreibe Infobereich - Prg. Daten und Uhrzeit
# -----------------------------------------------------------------------------------------------------
def UpdateInfo():
  InfoScreen.fill(BLACK)
   
  lt = time.localtime()
  InfoScreen.blit(label0, (0,0))       
  InfoScreen.blit(labelIp, (BreiteInfo1 - IpSize[0], 0))                     

  UhrZeitString = time.strftime("%H:%M:%S ", lt)
  UhrZeitString = "Zeit : ".decode("utf8")  + UhrZeitString
  UhrZeitSize = font1.size(UhrZeitString)
  
  label1 = font1.render(UhrZeitString, 1, YELLOW)
  InfoScreen.blit(label1, (BreiteInfo1 - UhrZeitSize[0], LineSpaceText))

  label2 = font1.render(time.strftime("%a %d.%m.%Y ", lt), 1,YELLOW)
  InfoScreen.blit(label2, (0, 35))
  InfoScreen.blit(labelCr, (0, LineSpaceText))

  pygame.draw.line(InfoScreen, BLUE, (0, HoeheInfo1 - 1), (BreiteInfo1, HoeheInfo1 - 1))
  window.blit(InfoScreen, (0, 0)) 

# -----------------------------------------------------------------------------------------------------
# schreibe Infobereich 2 - Menü 1
# -----------------------------------------------------------------------------------------------------
def UpdateScreenMenue01():
  global TitelScrolling
  global ChannelScrolling
  global CurrentSong
  global MpdStatus
 
  # Ausgabe mpd lesen
  Info2Screen.fill(BLACK)
  CurrentSong = mpd.currentsong()  # lese die die Daten zum aktuellen Titel
  MpdStatus   = mpd.status()       # lese den aktuellen mpd Status
  
  # Lautstärke lesen
  AktVolume = MpdStatus.get('volume', '0')
  labelVolume = font3.render("Volume : ".decode("utf8") + AktVolume +"%".decode("utf8"), 1, RED)
  Info2Screen.blit(labelVolume, (ButtonPosition[0][0], 0))

  # Aktuelle Playlistposition
  AktiverSender = CurrentSong.get('id', '0')
  if AktiverSender == '0':
    mpd.playid(1) 
    AktiverSender = CurrentSong.get('id', '0')
        
  labelPosition = font3.render("Station : ".decode("utf8") + AktiverSender, 1, RED)
  Info2Screen.blit(labelPosition, (ButtonPosition[3][0], 0))

  # Aktueller Sender
  ChannelName  = CurrentSong.get('name', '0')
  ChannelSize  = font3.size(ChannelName.decode("utf8"))
  ChannelLabel = font3.render(ChannelName.decode("utf8"), 1, RED)
  ChannelScrolling = ScrollText(Info2Screen, ChannelLabel, ChannelSize[0], LineSpaceText, BreiteInfo2, ChannelScrolling, 1)
  
  # Aktueller Titel
  TitleName  = CurrentSong.get('title', '0')   
  TitleSize  = font3.size(TitleName.decode("utf8"))
  TitelLabel = font3.render(TitleName.decode("utf8"), 1, RED)
  TitelScrolling = ScrollText(Info2Screen, TitelLabel, TitleSize[0], LineSpaceText * 2, BreiteInfo2, TitelScrolling, 1)
  
  # Aktuelle Bitrate lesen
  BitRate = MpdStatus.get('bitrate', '0')
  labelBitrate = font3.render(BitRate + "kbps".decode("utf8"), 1, RED)
  Info2Screen.blit(labelBitrate, (ButtonPosition[6][0], 0))
  
  # -------------------------------------------------------------------------------------------------

  window.blit(Info2Screen, Info2Offset)
  pygame.display.flip()    

# -----------------------------------------------------------------------------------------------------
# schreibe Infobereich 2 - Menü 2
# -----------------------------------------------------------------------------------------------------
def UpdateScreenMenue02():
  global CurrentSong	
  global M02ShowStreamUrl
  global M02ShowWlanInfo
  global M02ShowWetter
  global StreamUrlScrolling
	
  Info2Screen.fill(BLACK)

  if M02ShowStreamUrl == True:
    # Aktuelle Stream URL augeben
    InfoLabel = font3.render("Stream URL :".decode("utf8"), 1, RED)
    Info2Screen.blit(InfoLabel, (0, 0))	  
    StreamUrl = CurrentSong.get('file', '0')  
    StreamUrlSize  = font3.size(StreamUrl.decode("utf8"))
    StreamUrlLabel = font3.render(StreamUrl.decode("utf8"), 1, RED)
    StreamUrlScrolling = ScrollText(Info2Screen, StreamUrlLabel, StreamUrlSize[0], LineSpaceText, BreiteInfo2, StreamUrlScrolling, 1)
  elif M02ShowWlanInfo == True:
    WlanLevel = GetWlanLevel()	  
    InfoLabel = font3.render("WLan Level : ".decode("utf8") + str(WlanLevel) + "%".decode("utf8"), 1, RED) 
    Info2Screen.blit(InfoLabel, (0, 0))	  
  elif M02ShowWetter == True:
    ShowWetterInfo()
    
  window.blit(Info2Screen, Info2Offset)
  pygame.display.flip()    

# -----------------------------------------------------------------------------------------------------
# Hauptprogramm / Eventschleife
# -----------------------------------------------------------------------------------------------------
window = pygame.display.set_mode((WindowBreite,WindowHoehe))
pygame.init()
pygame.mouse.set_visible(0)                    # Mauszeiger sichtbar / unsichtbar

font0 = pygame.font.Font(SysFontPath, 16)      # Schriftart Überschrift
font1 = pygame.font.Font(SysFontPath, 16)      # Anzeige Uhr und Datum
font2 = pygame.font.Font(SysFontPath, 16)      # Anzeige Datum
font3 = pygame.font.Font(SysFontPath, 16)      # Anzeige Sendername
fontT = pygame.font.Font(SysFontPath, 15)      # Beschriftung der Tasten
fontM = pygame.font.Font(SysFontPath, 20)      # Bildschirmschoner / ShutDown

label0  = font0.render("WebRadio Touch V4".decode("utf8"), 1, RED)
labelCr = font3.render("by PSch 2017".decode("utf8"), 1, RED)

pygame.time.set_timer(USEREVENT + 1, 150)      # Timer Event 150 ms zur aktuallisierung des Bildschirmes
pygame.time.set_timer(USEREVENT + 2, 1000)     # Timer Event 1 sec  Bildschirmschoner
pygame.time.set_timer(USEREVENT + 3, 60000)    # Timer für Wetterbericht 1 min

window.fill(BLACK)                             # esrt mal alles schwarz machen

InfoRect   = (BreiteInfo1, HoeheInfo1)         # definiere Info 
InfoScreen = pygame.Surface(InfoRect) 

PanelRect    = (BreitePanel, HoehePanel)       # definiere Bedienfeld
PanelScreen  = pygame.Surface(PanelRect)

Info2Rect   = (BreiteInfo2, HoeheInfo2)        # definiere Info 2
Info2Screen = pygame.Surface(Info2Rect) 

CalcButtonPosition()                           # Berechne die Position der Buttons
SetButtonTextMenue(ButonListM01)               # Beschrifte die Buttons				
DrawButtons()                                  # Zeige die Buttons an

mpd, MpdStatus = ConnectMpd()                  # Verbindung mit mpd herstellen

WetterTimer = 0

IpAdr   = "IP : ".decode("UTF-8") + GetIpAdr()
labelIp = font1.render(IpAdr, 1, YELLOW)
IpSize  = font1.size(IpAdr)

GetWetterInfo(OWM_ID, OWM_KEY)

while True:
  for event in pygame.event.get():
    if event.type == pygame.MOUSEBUTTONDOWN:   # Maus Event ButtonDown
      TimeOutScreenSaver = 0
      TimeOutButtonAktive = 0;
      if (ScreenSaver != True):	
        if ActiveMenue == 1:
          OnTouchMenue01(pygame.mouse.get_pos())
        elif ActiveMenue == 2:
          OnTouchMenue02(pygame.mouse.get_pos())
      else:
        try: 
          mpd.ping()
        except:
          mpd, MpdStatus = ConnectMpd()  
        
        ActiveMenue = 1		
        M02ShowStreamUrl = False
        M02ShowWlanInfo  = False
        M02ShowWetter    = False
        SetButtonTextMenue(ButonListM01)
        DrawButtons()
        OnTouchMenue01((0, 0)) 
        ScreenSaver = False
      break
    
    if event.type == pygame.MOUSEBUTTONUP:    # Maus Event ButtonUp
      DrawButtons()
      break
    
    if event.type == USEREVENT + 1:   			  # Timer Event - update screen
      if (ScreenSaver != True):	
        UpdateInfo()						              # oberer Bildschirmbereich mit Uhr
        if ActiveMenue == 1:                   
          UpdateScreenMenue01()               # Infobereich 2, Menü 1 
        elif ActiveMenue == 2:
          UpdateScreenMenue02()               # Infobereich 2, Menü 2

        TimeOutButtonAktive = TimeOutButtonAktive + 1;
        if (TimeOutButtonAktive == 4):
          DrawButtons()        
      else:
        ShowScreenSaver()
      break
    
    if event.type == USEREVENT + 2:
      TimeOutScreenSaver = TimeOutScreenSaver + 1	  	
      if (TimeOutScreenSaver == 60):
        ScreenSaver = True	
      break	    
    
    if event.type == USEREVENT + 3:
      WetterTimer = WetterTimer + 1
      if WetterTimer == 30:
        GetWetterInfo(OWM_ID, OWM_KEY)
        WetterTimer = 0
			
