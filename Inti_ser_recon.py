# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 16:38:55 2020
Version 20 mai 2021

@author: valerie

Front end de traitements spectro helio de fichier ser
- interface pour selectionner un ou plusieurs fichiers
- appel au module inti_recon qui traite la sequence et genere les fichiers fits


----------------------------------------------------------------------------------------------------------------
version 4.0.5 du 3 mai - Antibes
- ajout des labels et longueurs d'onde d'apres fichier Meudon
- test depassement pixel_shift

version du 22 mars 2023 - paris
- bug base_filename fi si dpx
- ajout creation fits3D avec checkbox dans sequence doppler
- typo N et E dans labels GUI

version du 12 mars 2023 - paris
- gestion des seuils avec sliders
- force fenetres zoom et sliders en premier


version du 21 fev 2023 - Paris V4.0.3bis
- oubli de mettre a jour en anglais la valeur par defaut des inversions

version du 18 fev 2023 - Paris
- sauvegarde des inversions dans my_dictini
- gere cas ou fichier ini n'a pas les mots clef inversion (evite plantage avec ancien fichier ini)
- bug fix erreur longueur d'onde CaH/HeID3
- ajustement taille ecran dynamique avec screen size

version du 3 fev 2023 - Paris
- ajout bouton pour avoir la date du fichier ser 
- affiche date du fichier ser a la selection du fichier

version du 29 jan 2022 antibes V4.0.2
- ajout sauvegarde jpg avec facteur compression de 0.0038 des intensités et nom fichier fits database filename
- ajout de requete VO pour recuperer image jpg a la date d'observation pour affichage
- inversion coordonnées zoom et flip image
- bug fix sur hauteur image doppler

Version 26 dec 2022 Paris V4.0.1
- ajout rotation angle P manuel dans mode avancé
- ajout des mots clef fits demandé par JM Malherbe
FILENAME= 'solex_meudon _ha_20180620_122805.fits' /instrument, raie, date, heure (voir ci-dessous)
DATE_OBS= '2018-06-20T12:28:05.000' /date et heure TU de l’observation
INSTRUME= 'meudon' /instrument (à changer)
CONTACT = 'observateurs.solaires@obspm.fr' /adresse de contact
PHYSPARA= 'Intensity'
WAVELNTH= 6562.762 / en Angström, à changer selon raie (voir ci-dessous)
WAVEUNIT= -10
- inversion haut-bas des images png pour etre en conformité avec orientation image fits
- ajout de la connexion avec site kso pour obtention angle P a partir d'un champ dataobs
- inverse sens angle tilt correction avec flip

Version 17 sept 2022 Paris V3.3.6 > V4.0.0
- image trame mean en cv2 pour pointer une raie avec la souris en mode raie libre
- capture data entete observer, site long & lat, instrument
- transmission data_entete à la routine de traitement
    
Version 11 sept 2022 Paris V3.3.5
- sauvegarde poly_slit si pas POL ou WEAK flags

Version du 28 Aout 2022 V3.3.4
- gere la selection des onglets, suppression des checkbox 
- ajoute des decimales dans raie libre
- avoir possiblité de fixer tilt et scaling dans raie libre

Version du 22 Aout V3.3.3
- revient en arriere sur sauvegarde du polynome calculé
- sauve des coeff de polynome pour raie libre
- raie libre position x bleue et rouge en absolu

Version du 21 Aout Paris V3.3.2
- conservation du dernier nom de fichier unique traité
- gestion disque saturé pour ne pas faire de flat

Version 14 aout 2022 Antibes V3.3.1
- ajout onglet decalage pour raie libre
- ajout lecture des coef du dernier polynome
- ajout calcul constante polynome pour raie libre
- calcul image free et diff
- positionne fenetre à 300,300
- boucle tant que pas cancel ou win_closed ou fichier ser vide
- position depart fenetre dans inti.yaml win_posx et win_posy
- 2 chiffres apres virgule pour constante polynome


Version du 12 mai 2022 - V3.3.0
- ajout fenetre de zoom avec curseur souris sur disk, protus, clahe

version du 27 avril 2022 - Paris
- correction bug multiple fichier test si pas de nom de fichier

version du 23 avril 2022 - Paris
- ajout onglet de calcul d'une sequence doppler
- ajout de generation film mp4
- ajout onglet de la fonction magnetogramme
- ajout de memoire de boucle sur fichier traité pour gérér sequence b et v 
- creation d'une version anglaise par swith LG a la compil
- ajout de sauvegarde des coefficients de polynomes
- ajout4

version 18 sept 2021 - antibes
- reserre un peu seuils pour la visu des protuberances

version 16 sept 2021 - antibes
- back to circle display of black disk, not ellipse to really check deviation from circle
- adjust black disk size versus disk edge with disk_limit_percent variable

version 12 sept 2021 - antibes
- affichage disque noir et seuils protus sur suggestion de mattC

Version 8 sept 2021
- gestion erreur absence nom de fichier
- disque noir plus grand de 97% a 98 %
- ne sauve plus les fichiers fits intermediaires par defaut (_mean, _tilt et _flat)

Version 19 aout 2021
- suppression des flags dans la GUI pour simplification
- ajout '_' pour avoir fichier en tete dans explorer/finder
- ajout de _dp pour valeur de decalage différente de zéro dans noms de fichier pour eviter d'ecraser le precedent traitement

Version 16 juillet 
- remplacement des methodes des limbes par fit_ellipse
- modification code avec code de Doug & Andrew Smith pour acceleration stupefiante
    o vectorisation dans calcul extraction des intensités pour reconstruction du disque
    o vectorisation dans le calcul de slant, qui est en fait un calcul de tilt
- fichier ini a la racine du repertoire ou est le script (etait en dur)
- ajout d'un flag pour afficher ou pas le disque noir dans image png ayant les seuils adequats pour les protus

To be noted... image fits data are the image pixels value, no change of dynamic, no thresholding. Only png images are thresholded.
Black disk is a python graphic overlay, not burned into images. Circle data are logged for ISIS processing.



"""
import numpy as np
import cv2
import os
import sys
#import Inti_recon as sol - test gestion multi decalage
import Inti_recon as sol
from astropy.io import fits
from Inti_functions import *
import yaml
# import shutil
import tkinter as tk
import math
import requests as rq
import webbrowser as web
import urllib.request
from datetime import datetime 
from serfilesreader.serfilesreader import Serfile


import PySimpleGUI as sg

# -------------------------------------------------------------
global LG # Langue de l'interfacer (1 = FR ou 2 = US)
LG = 2
# -------------------------------------------------------------

SYMBOL_UP =    '▲'
SYMBOL_DOWN =  '▼'
current_version = 'Inti V4.0.5 by V.Desnoux et.al. '

def on_change_slider(x):
    # x est la valeur du curseur
    global source_window
    global img_data
        
    #print(params[0])
    sb = cv2.getTrackbarPos('Seuil bas', 'sliders')
    sh = cv2.getTrackbarPos('Seuil haut', 'sliders')
    s_bas=int(sb*65535/255)
    s_haut=int(sh*65535/255)
    #print('non inv : ',s_haut, s_bas)
    diff=s_haut-s_bas
    if diff==0:
        diff=65535
    
        
    f1=np.copy(img_data)
    if diff<0 :
        f1=np.copy(img_data)   
        f1=65535-f1
        s_bas=65535-s_bas
        s_haut=65535-s_haut

    f1=np.copy(img_data)
    f1[f1>s_haut]=s_haut
    f1[f1<s_bas]=s_bas
    f=(f1-s_bas)* (65535/abs(diff))
    f[f<0]=0
        

    cc=np.array(f, dtype='uint16')
    param=np.copy(cc)
    param2=f1
    paramh=s_haut
    paramb=s_bas
    cv2.setMouseCallback(source_window,mouse_event_callback, [source_window, param,param2,paramh,paramb])
    cc=cv2.flip(cc,0)
   
    cv2.imshow(source_window,cc)

def get_sun_meudon (date_jd1):
    date_jd2=date_jd1+1
    r1="http://voparis-tap-helio.obspm.fr/__system__/tap/run/sync?LANG=ADQL&format=txt&"
    r2="request=doQuery&query=select%20access_url%20from%20bass2000.epn_core%20where%20time_min%20between%20"
    r3=str(date_jd1)+"%20and%20"+str(date_jd2)+"%20and%20access_format=%27image/jpeg%27%20"
    r4="and%20filter=%27H%20Alpha%27"
    Vo_req=r1+r2+r3+r4

    reponse_web=rq.get(Vo_req)
    sun_meudon=reponse_web.text.split("\n")[0]
    
    return sun_meudon


def mouse_event_callback( event,x,y,flags,params):
    global source_window
    global img_data
    try :
        if event==cv2.EVENT_LBUTTONDOWN or event==cv2.EVENT_LBUTTONUP:
            source_window=params[0]
            img_data=params[2]
            #print('mouse: ',params[0])
            sh=int(params[3]/65000*255)
            sb=int(params[4]/65000*255)
            cv2.setTrackbarPos('Seuil bas','sliders',sb)
            cv2.setTrackbarPos('Seuil haut','sliders',sh)
            cv2.setWindowProperty('sliders',cv2.WND_PROP_TOPMOST,1)
            cv2.setWindowProperty('Zoom',cv2.WND_PROP_TOPMOST,1)
        if event == cv2.EVENT_MOUSEMOVE:
            try :
                img=np.copy(params[1])
                y=img.shape[0]-y
                img=img[y-150:y+150,x-150:x+150]
                img=cv2.flip(img,0)
                cv2.imshow('Zoom', img)
            except:
                pass
    except:
        pass

def mouse_event2_callback( event,x,y,flags,param):
    global mouse_x, mouse_y
    if event==cv2.EVENT_LBUTTONDOWN:
        try:
            font = cv2.FONT_HERSHEY_DUPLEX
            mouse_x, mouse_y=x,y
            cv2.putText(param, str(x)+';'+str(y), (x, y), 
                    font, 1, 
                    65000, 
                    1,cv2.LINE_AA) 
            cv2.imshow('mean', param)
        except:
            pass

def display_mean_img ():
    # Lecture et affiche image disque brut
    ImgFile = sg.popup_get_file("Select file")

    hdulist = fits.open(ImgFile, memmap=False)
    hdu=hdulist[0]
    myspectrum=hdu.data
    mih=hdu.header['NAXIS2']
    miw=hdu.header['NAXIS1']
    mean_trame=np.reshape(myspectrum, (mih,miw))
    #print(mih, miw)
    hdulist.close()
    if miw<178:
        # window title bar CV2 force image minimal size at 178, so pad to avoid autorescale
        mean_trame_pad=np.array(np.zeros((mih, 178)), dtype="uint16")
        mean_trame_pad[:mih, :miw]=mean_trame
    else:
        mean_trame_pad=np.array(mean_trame,dtype='uint16')
    
    #fenetre pour image mean de trame
    sc=0.8
    cv2.namedWindow('mean', cv2.WINDOW_NORMAL)
    cv2.moveWindow('mean', 100, 0)
    cv2.resizeWindow('mean', (int(miw*sc), int(mih*sc)))

    cv2.imshow('mean',mean_trame_pad)
    cv2.setMouseCallback('mean',mouse_event2_callback, mean_trame_pad)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def collapse(layout, key):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this seciton visible / invisible
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key))



def UI_SerBrowse (WorkDir,saved_tilt, saved_ratio, dec_pix_dop, dec_pix_cont, poly, pos_free_blue, 
                  pos_free_red,win_pos, previous_serfile, data_entete,saved_angP,Flags):

    sg.theme('Dark2')
    sg.theme_button_color(('white', '#500000'))
    #print('ui :', os.path.join(WorkDir,previous_serfile))
    Shift=[]
    #Flags={}
    Flags["DOPCONT"]=False
    Flags["VOL"]=False
    Flags["POL"]=False
    Flags["WEAK"]=False
    Racines=[]
    list_wave=[['Manual','Ha','Ha2cb','Cak', 'Cak1v','Cah', 'Cah1v','HeID3'],[0,6562.762,6561.432,3933.663,3932.163, 3968.469,3966.968,5877.3]]

    
    if LG == 1:
        section1 = [
                [sg.Checkbox(' Affichage de la reconstruction en temps réel ', default=False, key='-DISP-')],
                [sg.Checkbox(' Non sauvegarde des fichiers FITS intermédiaires', default=True, key='-SFIT-')],
                [sg.Checkbox(' Force les valeurs tilt et facteur d\'echelle', default=False, key='-F_ANG_SXSY-')],
                [sg.Text('Angle Tilt en degrés :', size=(15,1)), sg.Input(default_text=saved_tilt, size=(6,1),key='-TILT-')],
                [sg.Text('Ratio SY/SX :', size=(15,1)), sg.Input(default_text=saved_ratio, size=(6,1),key='-RATIO-')]
                
                ]
    else:
        section1 = [
                [sg.Checkbox(' Real time reconstruction display ', default=False, key='-DISP-')],
                [sg.Checkbox(' No intermediate files FITS saving', default=True, key='-SFIT-')],
                [sg.Checkbox(' Force values of tilt and scale ratio', default=False, key='-F_ANG_SXSY-')],
                [sg.Text('Tilt angle in degrees :', size=(15,1)), sg.Input(default_text=saved_tilt, size=(6,1),key='-TILT-')],
                [sg.Text('SY/SX ratio :', size=(15,1)), sg.Input(default_text=saved_ratio, size=(6,1),key='-RATIO-')]
                
                ]
        
    
    if LG == 1:
        section2 = [
                [sg.Text('Observateur :', size=(12,1)), sg.Input(default_text=data_entete[0], size=(25,1),key='-OBSERVER-')],
                [sg.Text('Contact :', size=(12,1)), sg.Input(default_text=data_entete[4], size=(25,1),key='-CONTACT-')],
                [sg.Text('Site Long :', size=(12,1)), sg.Input(default_text=data_entete[2], size=(6,1),key='-SITE_LONG-'),sg.Text('E positif'),
                 sg.Text('  Site Lat :', size=(12,1)), sg.Input(default_text=data_entete[3], size=(6,1),key='-SITE_LAT-'), sg.Text('N positif'),
                 sg.Text(' in decimal degree')],
                [sg.Text('Instrument :', size=(12,1)), sg.Input(default_text=data_entete[1], size=(35,1),key='-INSTRU-')],
                [sg.Text('Longueur d\'onde :', size=(12,1)), sg.Combo(list_wave[0], default_value=list_wave[0][0], size=(10,1),key='-WAVE-',enable_events=True),
                 sg.Text(list_wave[1][0], key='-WAVEVAL-')],
                [sg.Text('Date et heure :',size=(12,1)),sg.Input(default_text='', size=(26,1),key='-DATEOBS-'),
                     sg.Button('Date', key='-GETDATE-'),sg.Button('Meudon', key='-CLIMSO-'),
                     sg.Text('BASS2000', key='-BASS-', enable_events=True, font="None 9 italic underline"), 
                     sg.Text('NSO', key='-NSO-',enable_events=True, font="None 9 italic underline")],
                [sg.Text('Angle P :', size=(12,1)), sg.Input(default_text=saved_angP, size=(10,1),key='-ANGP-'), 
                 sg.Text("Nord en haut, Est à gauche, angle P positif vers l\'Est"), sg.Button('KSO',key='-KSO-')],
                [sg.Checkbox(' Inversion E-W', default=Flags['FLIPRA'], key='-RA_FLIP-')],
                [sg.Checkbox(' Inversion N-S', default=Flags['FLIPNS'], key='-NS_FLIP-')]
            
                ]
    else:
        section2 = [
                [sg.Text('Observer :', size=(12,1)), sg.Input(default_text=data_entete[0], size=(25,1),key='-OBSERVER-')],
                [sg.Text('Contact :', size=(12,1)), sg.Input(default_text=data_entete[4], size=(25,1),key='-CONTACT-')],
                [sg.Text('Site Long :', size=(12,1)), sg.Input(default_text=data_entete[2], size=(6,1),key='-SITE_LONG-'),sg.Text('E positive'),
                 sg.Text('  Site Lat :', size=(12,1)), sg.Input(default_text=data_entete[3], size=(6,1),key='-SITE_LAT-'),sg.Text('N positive'),
                 sg.Text(' in decimal degree')],
                [sg.Text('Instrument :', size=(12,1)), sg.Input(default_text=data_entete[1], size=(35,1),key='-INSTRU-')],
                [sg.Text('Wavelength :', size=(12,1)), sg.Combo(list_wave[0], default_value=list_wave[0][0], size=(10,1),key='-WAVE-',enable_events=True), 
                 sg.Text(list_wave[1][0], key='-WAVEVAL-')],
                [sg.Text('Date and time :',size=(12,1)),sg.Input(default_text='', size=(26,1),key='-DATEOBS-'),
                     sg.Button('Date', key='-GETDATE-'),sg.Button('Meudon', key='-CLIMSO-'),
                     sg.Text('BASS2000', key='-BASS-', enable_events=True, font="None 9 italic underline"), 
                     sg.Text('NSO', key='-NSO-',enable_events=True, font="None 9 italic underline")],
                [sg.Text('P Angle :', size=(12,1)), sg.Input(default_text=saved_angP, size=(10,1),key='-ANGP-'), 
                 sg.Text("North up, Est left, P angle positive towards Est"), sg.Button('KSO',key='-KSO-')],
                [sg.Checkbox(' E-W flip', default=Flags['FLIPRA'], key='-RA_FLIP-')],
                [sg.Checkbox(' N-S flip', default=Flags['FLIPNS'], key='-NS_FLIP-')]
                
                
                ]
      
    if LG == 1:
        tab1_layout = [      
            [sg.T("")],
            #### Section 1 part ####
            [sg.T(SYMBOL_UP, enable_events=True, k='-OPEN SEC1-', text_color='white'), 
             sg.T('Avancé', enable_events=True, text_color='white', k='-OPEN SEC1-TEXT')],
            [collapse(section1, '-SEC1-')],
            [sg.T("")],
            #### Section 2 part ####
            [sg.T(SYMBOL_UP, enable_events=True, k='-OPEN SEC2-', text_color='white'), 
             sg.T('Database compatibilité', enable_events=True, text_color='white', k='-OPEN SEC2-TEXT')],
            [collapse(section2, '-SEC2-')],
            [sg.T("")],
            [sg.Text('Décalage en pixels :',size=(15,1)),sg.Input(default_text='0',size=(4,1),key='-DX-',enable_events=True)]
            ]
        
        tab2_layout =[
            #[sg.Checkbox(' Calcul images Doppler et Continuum ', default=False, key='-DOPCONT-')],
            [sg.Text("")],
            [sg.Text('Decalage doppler :',size=(16,1)),sg.Input(default_text=dec_pix_dop,size=(4,1),key='-DopX-',enable_events=True)],
            [sg.Text('Decalage continuum :',size=(16,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='-ContX-',enable_events=True)]
            ]
        
        tab3_layout =[
            #[sg.Checkbox(' Synthèse d\'une séquence d\'images décalées spectralement ', default=False, key='-VOL-')],
            [sg.Text("")],
            [sg.Text('Plage en pixels :',size=(12,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='Volume',enable_events=True), sg.Text('+/- pixels')],
            [sg.Checkbox(' Création FITS 3D', default=False, key='-FITS3D-')],
            ]
       
        tab4_layout =[
            #[sg.Checkbox(' Zeeman ', default=False, key='-POL-')],
            [sg.Text("")],
            
            [sg.Text('Position raie :'),sg.Input(default_text=poly[2],size=(5,1),key='c'),
             sg.Text('  Ecartement en pixels :',size=(17,1)),sg.Input(default_text=2,size=(3,1),key='Zeeman_wide',enable_events=True), sg.Text('+/- pixels'),
             sg.Text('  Décalage :'), sg.Input(default_text=0,size=(4,1),key='Zeeman_shift',enable_events=True)],
        
            [sg.Text('Coefficient polynome forme fente : ',size=(24,1)),sg.Input(default_text=poly[0],size=(9,1),key='a'), sg.Text('x2'),
             sg.Input(default_text=poly[1],size=(9,1),key='b'), sg.Text('x')],
            
            [sg.Text('Nom fichier racine aile bleue :'), sg.Input(default_text="b-", size=(15,1), key='racine_bleu')],
            [sg.Text('Nom fichier racine aile rouge :'), sg.Input(default_text="r-", size=(15,1), key='racine_rouge')]
            ]
        tab5_layout =[
            #[sg.Checkbox(' Raie libre ', default=False, key='-WEAK-')],
            [sg.Text("")],
            [sg.Text('Coefficient polynome forme fente : ',size=(24,1)),sg.Input(default_text="{:.4e}".format(poly[0]),size=(15,1),key='fa'), sg.Text('x2'),
             sg.Input(default_text="{:.4e}".format(poly[1]),size=(15,1),key='fb'), sg.Text('x')],
            [sg.Text('Constante polynome :'),sg.Input(default_text="{:.2f}".format(poly[2]),size=(8,1),key='fc')],
            [sg.Button("trame"),sg.Text('Position raie xmin:'),sg.Input(default_text=0,size=(5,1),background_color='gray',key='xmin'),sg.Text('à hauteur y:'),sg.Input(default_text=0,size=(5,1),background_color='gray',key='y_xmin'), sg.Button("Calcul")],
            [sg.Text('Position bleu :'),sg.Input(default_text=pos_free_blue,size=(5,1),key='wb'),sg.Text('Position rouge :'),sg.Input(default_text=pos_free_red,size=(5,1),key='wr')],
            [sg.Checkbox(' Force les valeurs tilt et facteur d\'echelle', default=False, key='-F_ANG_SXSY2-')],
            [sg.Text('Angle Tilt en degrés :', size=(15,1)), sg.Input(default_text=saved_tilt, size=(6,1),key='-TILT2-'),sg.Text('Ratio SY/SX :', size=(15,1)), sg.Input(default_text=saved_ratio, size=(6,1),key='-RATIO2-')]
            ]
    else:
        tab1_layout = [ 
            [sg.T("")],
            #### Section 1 part ####
            [sg.T(SYMBOL_UP, enable_events=True, k='-OPEN SEC1-', text_color='white'), sg.T('Advanced', enable_events=True, text_color='white', k='-OPEN SEC1-TEXT')],
            [collapse(section1, '-SEC1-')],
            [sg.T("")],
            #### Section 2 part ####
            [sg.T(SYMBOL_UP, enable_events=True, k='-OPEN SEC2-', text_color='white'), 
             sg.T('Database compatibility', enable_events=True, text_color='white', k='-OPEN SEC2-TEXT')],
            [collapse(section2, '-SEC2-')],
            [sg.T("")],
            [sg.Text('Shift in pixels :',size=(11,1)),sg.Input(default_text='0',size=(4,1),key='-DX-',enable_events=True)]
            ]
        
        tab2_layout =[
            #[sg.Checkbox(' Compute Doppler and Continuum images ', default=False, key='-DOPCONT-')],
            [sg.Text("")],
            [sg.Text('Doppler shift :',size=(12,1)),sg.Input(default_text=dec_pix_dop,size=(4,1),key='-DopX-',enable_events=True)],
            [sg.Text('Continuum shift :',size=(12,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='-ContX-',enable_events=True)]
            ]
        
        tab3_layout =[
            #[sg.Checkbox(' Generate a spectraly shifted images sequence ', default=False, key='-VOL-')],
            [sg.Text("")],
            [sg.Text('Range in pixels :',size=(12,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='Volume',enable_events=True), sg.Text('+/- pixels')],
            [sg.Checkbox(' Create FITS 3D', default=False, key='-FITS3D-')],
            ]
       
        tab4_layout =[
            #[sg.Checkbox(' Zeeman ', default=False, key='-POL-')],
            [sg.Text("")],
            
            [sg.Text('Line position :'),sg.Input(default_text=poly[2],size=(5,1),key='c'),
             sg.Text(' Pixels spacing :',size=(12,1)),sg.Input(default_text=2,size=(3,1),key='Zeeman_wide',enable_events=True), sg.Text('+/- pixels'),
             sg.Text(' Shift  :'), sg.Input(default_text=0,size=(4,1),key='Zeeman_shift',enable_events=True)],
        
            [sg.Text('Polynom terms of slit distorsion : ',size=(24,1)),sg.Input(default_text=poly[0],size=(9,1),key='a'), sg.Text('x2'),
             sg.Input(default_text=poly[1],size=(9,1),key='b'), sg.Text('x')],
            
            [sg.Text('Bleu line wing generic file name :'), sg.Input(default_text="b-", size=(15,1), key='racine_bleu')],
            [sg.Text('Red line wing generic file name  :'), sg.Input(default_text="r-", size=(15,1), key='racine_rouge')]
            ]
        
        tab5_layout =[
            #[sg.Checkbox(' Free line ', default=False, key='-WEAK-')],
            [sg.Text("")],
            [sg.Text('Polynom terms of slit distorsion : ',size=(24,1)),sg.Input(default_text="{:.4e}".format(poly[0]),size=(15,1),key='fa'), sg.Text('x2'),
             sg.Input(default_text="{:.4e}".format(poly[1]),size=(15,1),key='fb'), sg.Text('x')],
            [sg.Text('Polynome constante :'),sg.Input(default_text="{:.2f}".format(poly[2]),size=(10,1),key='fc')],
            [sg.Button("frame"),sg.Text('Position line xmin:'),sg.Input(default_text=0,size=(5,1),background_color='gray',key='xmin'),sg.Text('at height y:'),sg.Input(default_text=0,size=(5,1),background_color='gray',key='y_xmin'), sg.Button("Calcul")],
            [sg.Text('Blue position :'),sg.Input(default_text=pos_free_blue,size=(5,1),key='wb'),sg.Text('Red position :'),sg.Input(default_text=pos_free_red,size=(5,1),key='wr')],
            [sg.Checkbox(' Force values of tilt and scale ratio', default=False, key='-F_ANG_SXSY2-')],
            [sg.Text('Tilt angle in degrees :', size=(15,1)), sg.Input(default_text=saved_tilt, size=(6,1),key='-TILT2-'),sg.Text('SY/SX ratio :', size=(15,1)), sg.Input(default_text=saved_ratio, size=(6,1),key='-RATIO2-')]
            ]
    
    if LG == 1:
        layout = [
            [sg.Text('Fichier(s) :', size=(6, 1)), sg.InputText(default_text='',size=(66,1),enable_events=True,key='-FILE-'),
             sg.FilesBrowse(' Ouvrir ',file_types=(("SER Files", "*.ser"),),initial_folder=os.path.join(WorkDir,previous_serfile))],
            
            [sg.TabGroup([[sg.Tab('  Général  ', tab1_layout), sg.Tab('Doppler & Continuum', tab2_layout,), 
                sg.Tab('Séquence Doppler', tab3_layout,),
                sg.Tab('Magnétogramme',tab4_layout,),
                sg.Tab('Raie libre', tab5_layout)]],change_submits=True,key="TabGr",tab_background_color='#404040')],  
            [sg.Button('Ok', size=(14,1)), sg.Cancel('  Sortir  ')],
            [sg.Text(current_version, size=(30, 1),text_color='Tan', font=("Arial", 8, "italic"))]
            ]
    else:
        layout = [
            [sg.Text('File(s) :', size=(5, 1)), sg.InputText(default_text='',size=(70,1),enable_events=True,key='-FILE-'),
             sg.FilesBrowse(' Open ',file_types=(("SER Files", "*.ser"),),initial_folder=os.path.join(WorkDir,previous_serfile))],
            
            [sg.TabGroup([[sg.Tab('  General  ', tab1_layout), sg.Tab('Doppler & Continuum', tab2_layout,), 
                sg.Tab('Doppler Sequence', tab3_layout,),
                sg.Tab('Magnetogram',tab4_layout,),
                sg.Tab('Free line', tab5_layout)]],change_submits=True,key="TabGr",tab_background_color='#404040')],  
            [sg.Button('Ok', size=(14,1)), sg.Cancel('  Exit  ')],
            [sg.Text(current_version, size=(30, 1),text_color='Tan', font=("Arial", 8, "italic"))]
            ]
            
    
    window = sg.Window('INTI', layout, location=win_pos,finalize=True)
    opened1 = False
    window['-SEC1-'].update(visible=opened1)
    opened2=False
    window['-SEC2-'].update(visible=opened2)
    
    window['-FILE-'].update(os.path.join(WorkDir,previous_serfile)) 
    window.BringToFront()
    Flag_sortie=False
    wavelength_found=list_wave[1][0]
    solar_dict={}

    
    while True:
        event, values = window.read()
        #print(event)
        if event==sg.WIN_CLOSED or event=='  Exit  ' or event=='  Sortir  ': 
            Flag_sortie=True
            break
        
        if event=="trame" or event=="frame":
            display_mean_img()
            window['xmin'].update(str(mouse_x))
            window['y_xmin'].update(str(mouse_y))

        
        if event=='TabGr':
            tab_sel=values['TabGr']
            #print(tab_sel)
            if tab_sel== "Doppler & Continuum":
                Flags["DOPCONT"]=True
                Flags["VOL"]=False
                Flags["POL"]=False
                Flags["WEAK"]=False
            if tab_sel== "Séquence Doppler" or tab_sel=="Doppler Sequence":
                Flags["DOPCONT"]=False
                Flags["VOL"]=True
                Flags["POL"]=False
                Flags["WEAK"]=False
                Flags["FITS3D"]=False
            if tab_sel=="Magnétogramme" or tab_sel=="Magnetogram":
                Flags["DOPCONT"]=False
                Flags["VOL"]=False
                Flags["POL"]=True
                Flags["WEAK"]=False
            if tab_sel=="Raie libre" or tab_sel=="Free line":
                Flags["DOPCONT"]=False
                Flags["VOL"]=False
                Flags["POL"]=False
                Flags["WEAK"]=True
            if tab_sel== "  Général  " or tab_sel=="  General  ":
                Flags["DOPCONT"]=False
                Flags["VOL"]=False
                Flags["POL"]=False
                Flags["WEAK"]=False
                
        if event=='-FILE-' or event=='-GETDATE-':
            serfiles=values['-FILE-']
            serfiles=serfiles.split(';')
            serfile=serfiles[0]
            #print(serfiles)
            base=os.path.basename(values['-FILE-'])
            basefich=os.path.splitext(base)[0]
            if basefich!='':
                if len(serfiles)==1 :
                    try:
                        scan = Serfile(serfile, False)
                        #dateSerUTC = scan.getHeader()['DateTimeUTC']
                        f_dateSerUTC=datetime.utcfromtimestamp(SER_time_seconds(scan.getHeader()['DateTimeUTC']))
                        fits_dateobs=f_dateSerUTC.strftime('%Y-%m-%dT%H:%M:%S.%f7%z')
                        window['-DATEOBS-'].update(fits_dateobs)
                    except:
                        if LG==1 :
                            logme('Erreur ouverture fichier : '+serfile)
                        else:
                            logme('File open error : '+serfile)
                    
                    
        
        if event=='Ok':

            #WorkDir=os.path.dirname(values['-FILE-'])+"/"
            #os.chdir(WorkDir)
            base=os.path.basename(values['-FILE-'])
            basefich=os.path.splitext(base)[0]
            
            if basefich!='':
                break
            else:
                if LG==2:
                    print('Enter file name')
                else:
                    print('Entrez un nom de fichier')
        
        if event.startswith('-OPEN SEC1-'):
            opened1 = not opened1
            window['-OPEN SEC1-'].update(SYMBOL_DOWN if opened1 else SYMBOL_UP)
            window['-SEC1-'].update(visible=opened1)
        
        if event.startswith('-OPEN SEC2-'):
            opened2 = not opened2
            window['-OPEN SEC2-'].update(SYMBOL_DOWN if opened2 else SYMBOL_UP)
            window['-SEC2-'].update(visible=opened2)
            
        if event=="Calcul" :
            y_xmin=int(values['y_xmin'])
            if y_xmin!=0 :
                xmin=int(values['xmin'])
                y_xmin=int(values['y_xmin'])
                xline=xmin-float(values['fa'])*y_xmin**2-float(values['fb'])*y_xmin
                window["fc"].update("{:.1f}".format(xline))
                poly[2]=xline
                
        if event=="-WAVE-" :
            #print(values['-WAVE-'])
            search_label=values['-WAVE-']
            wavelength_found=list_wave[1][list_wave[0].index(search_label)]
            window['-WAVEVAL-'].update(wavelength_found)
            
        if event=="-KSO-" :
            try :
                fits_dateobs=values['-DATEOBS-']
                date_obs=fits_dateobs.split('T')[0].replace('-','')
                heure_obs=fits_dateobs.split('T')[1].split('.')[0].replace(':','%3A')
                str_site_lat=str(values['-SITE_LAT-'])
                str_site_long=str(values['-SITE_LONG-'])
                webservice='https://www.kso.ac.at/beobachtungen/ephem_api.php?date='+date_obs+'&time='+heure_obs+'&lat='+str_site_lat+'&lon='+str_site_long+"&P"
                #print(webservice)
                reponse_web=rq.get(webservice)
                #print(reponse_web.text)
                window['-ANGP-'].update("{:+.3f}".format(float(reponse_web.text)))
                # autres services 
                webservice='https://www.kso.ac.at/beobachtungen/ephem_api.php?date='+date_obs+'&time='+heure_obs+'&lat='+str_site_lat+'&lon='+str_site_long+"&B0&Lon&Carr"
                #print(webservice)
                reponse_web=rq.get(webservice)
                solar_data=reponse_web.text.split('\n')
                solar_dict['B0']=solar_data[0]
                solar_dict['L0']=solar_data[1]
                solar_dict['Carr']=solar_data[2]
                
            except:
                if LG==1 :
                    logme("Erreur dans le format des données")
                else:
                    logme("Error in data formatting")
                    
        if event=='-CLIMSO-' :
            fmt = '%Y%m%d'
            #date_obs='20211213'
            fits_dateobs=values['-DATEOBS-']
            if fits_dateobs!='' :
                date_obs=fits_dateobs.split('T')[0].replace('-','')
                s=date_obs
                my_date = datetime.strptime(s, fmt)
                date_jd1=float(my_date.toordinal() + 1721424.5)
                sun_meudon=get_sun_meudon(date_jd1)
    
                while sun_meudon =='' :
                    date_jd1=date_jd1-1
                    sun_meudon=get_sun_meudon(date_jd1) 
    
                print('Meudon Spectro Halpha at closest date : ',sun_meudon)
                urllib.request.urlretrieve(sun_meudon, 'meudon.jpg')
                
                # affiche meudon.jpg depuis le site de BASS2000
                web.open('meudon.jpg')
                
                # recupère le nom du fichier en cours
                base=os.path.basename(values['-FILE-'])
                basefich=os.path.splitext(base)[0]
                # son repertoire
                curr_dir=os.path.split(values['-FILE-'])[0]
                
                if basefich!='':
                    # contruit le nom du fichier _clahe.png 
                    myimage=curr_dir+'/_'+basefich+'_clahe.png'
                    # affiche le fichier si il existe
                    if os.path.exists(myimage):
                        web.open(myimage)
        
        if event=='-NSO-':
            web.open('https://nso.edu/')
            
        if event=='-BASS-':
            web.open('https://bass2000.obspm.fr/home.php')


    window.close()
    try:          
        FileNames=values['-FILE-']
    except:
        FileNames=''

    #if FileNames==None :
            #FileNames=''

    
    try :
        Flags["RTDISP"]=values['-DISP-']
    except:
        pass
    #Flags["DOPCONT"]=values['-DOPCONT-']
    Flags["ALLFITS"]=values['-SFIT-']
    #Flags["VOL"]=values['-VOL-']
    #Flags["POL"]=values['-POL-']
    #Flags["WEAK"]=values['-WEAK-']
    Flags["sortie"]=Flag_sortie
    Flags["FLIPRA"]=values['-RA_FLIP-']
    Flags["FLIPNS"]=values['-NS_FLIP-']
    Flags["FITS3D"]=values['-FITS3D-']
   # print(Flags)
    
    ratio_fixe=float(values['-RATIO-'])
    ang_tilt=values['-TILT-']
    centered_wave=wavelength_found
    centered_wave_label=values['-WAVE-']
    if centered_wave_label.isdigit():
        centered_wave=str(round(float(centered_wave)))
    
    Data_entete=[values['-OBSERVER-'], values['-INSTRU-'], 
                 float(values['-SITE_LONG-']), float(values['-SITE_LAT-']), values['-CONTACT-'], 
                 centered_wave, centered_wave_label]
    ang_P=float(values['-ANGP-']) 
    
    if Flags["WEAK"] :
        poly=[]
        poly.append(float(values['fa']))
        poly.append(float(values['fb']))
        poly.append(float(values['fc']))
        Shift.append(0)
        Shift.append(int(int(values['wb'])-poly[2]))
        Shift.append(int(int(values['wr'])-poly[2]))
        if values['-F_ANG_SXSY2-']!=True:
            ratio_fixe=0
            ang_tilt=0
        else :
            ratio_fixe=float(values['-RATIO2-'])
            ang_tilt=values['-TILT2-']
        
    if Flags["POL"]:
        poly=[]
        poly.append(float(values['a']))
        poly.append(float(values['b']))
        poly.append(float(values['c']))
   
    
    if values['-F_ANG_SXSY-']!=True and Flags["WEAK"]!=True:
        ratio_fixe=0
        ang_tilt=0

    Shift.append(int(values['-DX-']))
    Shift.append(int(values['-DopX-']))
    Shift.append(int(values['-ContX-']))
    if Flags["POL"]:
        Shift.append(int(values['Zeeman_wide']))
        Shift.append(float(values['Zeeman_shift']))
    else:
        Shift.append(int(values['Volume']))
        Shift.append(0.0)
    Racines.append(values['racine_bleu'])
    Racines.append(values['racine_rouge'])
    
    return FileNames, Shift, Flags, ratio_fixe,ang_tilt, poly, Racines, Data_entete,ang_P, solar_dict

"""
-------------------------------------------------------------------------------------------
Program starts here !
--------------------------------------------------------------------------------------------
"""
Flag_sortie=False
serfiles=[]
Flags={}
previous_serfile=''
my_ini=os.getcwd()+'/inti.yaml'
global mouse_x, mouse_y
mouse_x,mouse_y=0,0
global img_data


# gestion dynamique de la taille ecran
screen = tk.Tk()
screensize = screen.winfo_screenwidth(), screen.winfo_screenheight()
screen.destroy()

#print(screensize)

while not Flag_sortie :
    
    # inti.yaml is a bootstart file to read last directory used by app
    # this file is stored in the module directory
    
    #my_ini=os.path.dirname(sys.argv[0])+'/inti.yaml'
    #my_ini=os.getcwd()+'/inti.yaml'
    my_dictini={'directory':'', 'dec doppler':3, 'dec cont':15, 'poly_slit_a':0, "poly_slit_b":0,'poly_slit_c':0, 
                'ang_tilt':0, 'ratio_sysx':0, 'poly_free_a':0,'poly_free_b':0,'poly_free_c':0,
                'pos_free_blue':0, 'pos_free_red':0,
                'win_posx':300, 'win_posy':200, 'observer':'', 'instru':'','site_long':0, 'site_lat':0,
                'angle P':0,'contact':'','wavelength':0, 'wave_label':'Manuel', 'inversion NS':0, 'inversion EW':0}
    #print('myini de depart:', my_ini)
    poly=[]
    
    
    try:
        #my_ini=os.path.dirname(sys.argv[0])+'/inti.yaml'
        #print('mon repertoire : ', mydir_ini)
        with open(my_ini, "r") as f1:
            my_dictini = yaml.safe_load(f1)
    except:
       if LG == 1:
           print('Création de inti.yaml comme : ', my_ini)
       else:
           print('creating inti.yaml as: ', my_ini) 
    
    WorkDir=my_dictini['directory']
    dec_pix_dop=int(my_dictini['dec doppler'])
    dec_pix_cont=int(my_dictini['dec cont'])
    saved_tilt=float(my_dictini['ang_tilt'])
    saved_angP=float(my_dictini['angle P'])
    saved_ratio=float(my_dictini['ratio_sysx'])
    poly.append(float(my_dictini['poly_free_a']))
    poly.append(float(my_dictini['poly_free_b']))
    poly.append(float(my_dictini['poly_free_c']))
    pos_free_blue=int(my_dictini['pos_free_blue'])
    pos_free_red=int(my_dictini['pos_free_red'])
    w_posx=int(my_dictini['win_posx'])
    w_posy=int(my_dictini['win_posy'])
    if 'inversion EW' in my_dictini:
        Flags['FLIPRA']=my_dictini['inversion EW']
        Flags['FLIPNS']=my_dictini['inversion NS']
    else:
        Flags['FLIPRA']=0
        Flags['FLIPNS']=0
        
    win_pos=(w_posx,w_posy)
    data_entete=[my_dictini['observer'], my_dictini['instru'],float(my_dictini['site_long']),float(my_dictini['site_lat']),my_dictini['contact'],
                 my_dictini['wavelength'],my_dictini['wave_label']]
    
    
    # Recupere paramatres de la boite de dialogue
    #print('serfile previous : ', previous_serfile)
    serfiles, Shift, Flags, ratio_fixe,ang_tilt, poly, racines, data_entete,ang_P,solar_dict= UI_SerBrowse(WorkDir, saved_tilt, saved_ratio,
                                                                             dec_pix_dop, dec_pix_cont, poly,pos_free_blue, pos_free_red,
                                                                             win_pos, previous_serfile, data_entete,saved_angP, Flags)
    serfiles=serfiles.split(';')
    #print('serfile : ',  len(serfiles))
    if len(serfiles)==1 :
        #print('ok')
        previous_serfile=os.path.basename(serfiles[0])
        #print('serfile previous : ', previous_serfile)
    ii=1
    Flag_sortie=Flags["sortie"]
    
    # pour gerer la tempo des affichages des images resultats dans cv2.waitKey
    # si plusieurs fichiers à traiter
    if len(serfiles)==1:
        tempo=90000 #tempo 60 secondes, pour no tempo mettre tempo=0 et faire enter pour terminer
        if  Flags["POL"]:
            tempo=3000 # tempo raccourcie après extraction zeeman 
    else:
        tempo=1000 #temp 1 sec
        
    # boucle sur la liste des fichers
    for serfile in serfiles:
        #print (serfile)
        
        if Flag_sortie :
            sys.exit()
    
        if serfile=='':
            sys.exit()
        
        WorkDir=os.path.dirname(serfile)+"/"
        os.chdir(WorkDir)
        base=os.path.basename(serfile)
        basefich=os.path.splitext(base)[0]
        if base=='':
            if LG == 1:
                logme('Erreur de nom de fichier : '+serfile)
            else:
                logme('File name error: '+serfile)
            sys.exit()
         
          
        # appel au module d'extraction, reconstruction et correction
        #
        # basefich: nom du fichier ser sans extension et sans repertoire
        # dx: decalage en pixel par rapport au centre de la raie 
        
        if Flags['POL'] and ii>1:
            ratio_fixe=geom[0]
            ang_tilt=geom[1]
        
        # 11 aout 22 ajout coef polynome en param de retour
        frames, header, cercle, range_dec, geom, polynome=sol.solex_proc(serfile,Shift,Flags,ratio_fixe,ang_tilt, poly, data_entete,ang_P, solar_dict)
        
        # met a jour le repertoire et les flags dans le fichier ini, oui a chaque fichier pour avoir le bon rep
        my_dictini['directory']=WorkDir
        # ajout data entete
        my_dictini['observer']=str(data_entete[0])
        my_dictini['instru']=str(data_entete[1])
        my_dictini['site_long']=data_entete[2]
        my_dictini['site_lat']=data_entete[3]
        my_dictini['contact']=data_entete[4]
        my_dictini['wavelength']=data_entete[5]
        my_dictini['wave_label']=data_entete[6]
        my_dictini['inversion EW']=Flags['FLIPRA']
        my_dictini['inversion NS']=Flags['FLIPNS']
        
        if Flags['WEAK']:
           my_dictini['pos_free_blue']=round(poly[2]+Shift[1])
           my_dictini['pos_free_red']=round(poly[2]+Shift[2])
        else:
            my_dictini['dec doppler']=Shift[1]
            my_dictini['dec cont']=Shift[2]

        my_dictini['ang_tilt']=ang_tilt
        my_dictini['angle P']=0 # ne conserve pas angle P pour eviter confusion
        my_dictini['ratio_sysx']=ratio_fixe
        my_dictini['win_posx']=w_posx
        my_dictini['win_posy']=w_posy
        if Flags['WEAK']==False and Flags['POL']==False:
            my_dictini['poly_slit_a']=float(polynome[0])
            my_dictini['poly_slit_b']=float(polynome[1])
            my_dictini['poly_slit_c']=float(polynome[2])
        else:
            my_dictini['poly_free_a']=float(polynome[0])
            my_dictini['poly_free_b']=float(polynome[1])
            my_dictini['poly_free_c']=float(polynome[2])
            my_dictini['poly_slit_a']=0
            my_dictini['poly_slit_b']=0
            my_dictini['poly_slit_c']=0
            
        
        
        try:
            with open(my_ini, "w") as f1:
                yaml.dump(my_dictini, f1, sort_keys=False)
        except:
            if LG == 1:
                logme ('Erreur lors de la sauvegarde de inti.yaml comme : '+my_ini)
            else:
                logme ('Error saving inti.yaml as: '+my_ini)
        
        #t0=time.time()
        base=os.path.basename(serfile)
        basefich='_'+os.path.splitext(base)[0]

    
        ih = frames[0].shape[0]
        newiw = frames[0].shape[1]
        
        # my screensize is 1536x864 - harcoded as tk.TK() produces an error in spyder
        # plus petit for speed up
        myscreen_sw, myscreen_sh=screensize
    
        top_w=0
        left_w=0
        #tw=150
        tw=int(myscreen_sw/10)
        lw=34
        

        screensizeH = (myscreen_sh-50) - (3*lw) 
        screensizeW = (myscreen_sw)-(3*tw)
        
        # gere reduction image png
        nw = screensizeW/newiw
        nh = screensizeH/ih
        sc=min(nw,nh)
        
        if sc >= 1 :
            sc = 1
        
        # Lecture et affiche image disque brut
        if range_dec[0]==0:
            ImgFile=basefich+'_raw.fits'
        else:
            ImgFile=basefich+'_dp'+str(range_dec[0])+'_raw.fits'
        
        hdulist = fits.open(ImgFile, memmap=False)
        hdu=hdulist[0]
        myspectrum=hdu.data
        rih=hdu.header['NAXIS2']
        riw=hdu.header['NAXIS1']
        Disk=np.reshape(myspectrum, (rih,riw))
        
        # Lecture nom filename  image recon
        if range_dec[0]==0:
            ImgFile=basefich+'_recon.fits'
        else :
            ImgFile=basefich+'_dp'+str(range_dec[0])+'_recon.fits'
            
        hdulist = fits.open(ImgFile, memmap=False)
        hdu=hdulist[0]
        base_filename=hdu.header['FILENAME'].split('.')[0]
        #print('filename : ',base_filename)
        
        Ratio_lum=(65536/np.max(Disk))*0.8
        Disk2=np.array((np.copy(Disk)*Ratio_lum),dtype='uint16')
        hdulist.close()
        
        
        # prepare fenetres pour affichage des images
        cv2.namedWindow('Raw', cv2.WINDOW_NORMAL)
        cv2.moveWindow('Raw', top_w, left_w)
        cv2.resizeWindow('Raw', (int(riw*sc), int(rih*sc)))
        
        
        top_w=top_w+tw
        left_w=left_w+lw
        cv2.namedWindow('contrast', cv2.WINDOW_NORMAL)
        cv2.moveWindow('contrast', top_w, left_w)
        cv2.resizeWindow('contrast', (int(newiw*sc), int(ih*sc)))
        
        top_w=top_w+tw
        left_w=left_w+lw
        cv2.namedWindow('protus', cv2.WINDOW_NORMAL)
        cv2.moveWindow('protus', top_w, left_w)
        cv2.resizeWindow('protus', (int(newiw*sc), int(ih*sc)))
    
        top_w=top_w+tw
        left_w=left_w+lw
        cv2.namedWindow('clahe', cv2.WINDOW_NORMAL)
        cv2.moveWindow('clahe', top_w, left_w)
        cv2.resizeWindow('clahe',(int(newiw*sc), int(ih*sc)))
        
              
        
        # ne fait un zoom que si on traite un seul fichier et pas doppler/continuum
        if len(frames)==1 and len(serfiles)==1:
            cv2.namedWindow('Zoom', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Zoom', 300, 300)
            cv2.moveWindow('Zoom',20,20)
            #
            cv2.namedWindow('sliders', cv2.WINDOW_AUTOSIZE)
            cv2.moveWindow('sliders', int(top_w*1.3), 0)
            cv2.resizeWindow('sliders',(600,100))
            source_window='clahe'
            
            cv2.createTrackbar('Seuil haut', 'sliders', 0,255, on_change_slider)
            cv2.createTrackbar('Seuil bas', 'sliders', 0,255, on_change_slider)
    
        
        # png image generation
        # image seuils moyen
        frame1=np.copy(frames[0])
        #Seuil_bas=np.percentile(frame1, 25)
        #Seuil_haut=np.percentile(frame1,99.9999)
        sub_frame=frame1[5:,:-5]
        Seuil_haut=np.percentile(sub_frame,99.999)
        Seuil_bas=(Seuil_haut*0.15)
        frame1[frame1>Seuil_haut]=Seuil_haut
        #print('seuil bas', Seuil_bas)
        #print('seuil haut', Seuil_haut)
        
        fc=(frame1-Seuil_bas)* (65000/(Seuil_haut-Seuil_bas))
        fc[fc<0]=0
        frame_contrasted=np.array(fc, dtype='uint16')
        if len(frames)==1 and len(serfiles)==1:
            param=np.copy(frame_contrasted)
            param2=np.copy(frame1)
            paramh=Seuil_haut
            paramb=Seuil_bas
            source_window='contrast'
            cv2.setMouseCallback('contrast',mouse_event_callback, [source_window,param, param2,paramh, paramb])
            
        frame_contrasted=cv2.flip(frame_contrasted,0)
       
        cv2.imshow('contrast',frame_contrasted)
        
        
        #cv2.imshow('sun',frame_contrasted)
        #cv2.waitKey(0)
    
        # image raw
        Disk2=cv2.flip(Disk2,0)
        cv2.imshow('Raw',Disk2)
        
        # image seuils serres 
        frame1=np.copy(frames[0])
        sub_frame=frame1[5:,:-5]
        Seuil_haut=np.percentile(sub_frame,99.999)
        Seuil_bas=(Seuil_haut*0.25)
        #print('seuil bas HC', Seuil_bas)
        #print('seuil haut HC', Seuil_haut)
        frame1[frame1>Seuil_haut]=Seuil_haut
        fc2=(frame1-Seuil_bas)* (65500/(Seuil_haut-Seuil_bas))
        fc2[fc2<0]=0
        frame_contrasted2=np.array(fc2, dtype='uint16')
        frame_contrasted2=cv2.flip(frame_contrasted2,0)
        #cv2.imshow('contrast',frame_contrasted2)
        #cv2.waitKey(0)
        
        if 2==1:   
            # image seuils protus original
            frame1=np.copy(frames[0])
            Seuil_haut=np.percentile(frame1,99.9999)*0.18
            Seuil_bas=0
            frame1=seuil_image_force(frame1, Seuil_haut, Seuil_bas)
            frame_contrasted3=np.array(frame1, dtype='uint16')
            
            #calcul du disque noir pour mieux distinguer les protuberances
            if cercle[0]!=0:
                x0=cercle[0]
                y0=cercle[1]
                wi=round(cercle[2]*0.998)
                he=round(cercle[3]*0.998)
            
            r=int(min(wi,he)-3)
            r=int(r-round(0.002*r))
            #c=(0,0,0)
            frame_contrasted3=cv2.circle(frame_contrasted3, (x0,y0),r,80,-1,lineType=cv2.LINE_AA)
            #frame_contrasted3=cv2.ellipse(frame_contrasted3, (x0,y0),(wi,he),0,0,360,(0,0,0),-1,lineType=cv2.LINE_AA ) #MattC apply tilt, change color to black
            frame_contrasted3=cv2.flip(frame_contrasted3,0)
            cv2.imshow('protus',frame_contrasted3)
            #cv2.waitKey(0)
        
        #improvements suggested by mattC to hide sun with disk
        else :           
            # hide disk before setting max threshold
            frame2=np.copy(frames[0])
            disk_limit_percent=0.001 # black disk radius inferior by 1% to disk edge
            if cercle[0]!=0:
                x0=cercle[0]
                y0=cercle[1]
                wi=round(cercle[2])
                he=round(cercle[3])
                r=(min(wi,he))
                r=int(r- round(r*disk_limit_percent))
                #print(cercle, wi,he,r)
                # prefer to really see deviation from circle
                fc3=cv2.circle(frame2, (x0,y0),r,80,-1,lineType=cv2.LINE_AA)
                #frame2=cv2.ellipse(frame2, (x0,y0),(wi,he),0,0,360,(0,0,0),-1,lineType=cv2.LINE_AA ) #MattC draw ellipse, change color to black
                frame1=np.copy(fc3)
                Threshold_Upper=np.percentile(frame1,99.9999)*0.5  #preference for high contrast
                Threshold_low=0
                img_seuil=seuil_image_force(frame1, Threshold_Upper, Threshold_low)
                
                frame_contrasted3=np.array(img_seuil, dtype='uint16')
                
                if len(frames)==1 and len(serfiles)==1:
                    param=np.copy(frame_contrasted3)
                    param2=np.copy(fc3)
                    paramh=Threshold_Upper
                    paramb=Threshold_low
                    source_window = 'protus'
                    cv2.setMouseCallback('protus',mouse_event_callback, [source_window,param,param2, paramh, paramb])

                
                frame_contrasted3=cv2.flip(frame_contrasted3,0)
                cv2.imshow('protus',frame_contrasted3)
            else:
                if LG == 1:
                    print("Erreur disque occulteur.")
                else:
                    print("Mask disk error.")
                    
                frame_contrasted3=frame_contrasted

        # create a CLAHE object (Arguments are optional)
        #clahe = cv2.createCLAHE(clipLimit=0.8, tileGridSize=(5,5))
        clahe = cv2.createCLAHE(clipLimit=0.8, tileGridSize=(2,2))
        cl1 = clahe.apply(frames[0])
        
        Seuil_bas=np.percentile(cl1, 25)
        Seuil_haut=np.percentile(cl1,99.9999)*1.05
        cc=(cl1-Seuil_bas)*(65000/(Seuil_haut-Seuil_bas))
        cc[cc<0]=0
        cc=np.array(cc, dtype='uint16')
        

        if len(frames)==1 and len(serfiles)==1:
            param=np.copy(cc)
            param2=np.copy(cl1)
            source_window='clahe'
            img_data=param2
            paramh=Seuil_haut
            paramb=Seuil_bas
            cv2.setMouseCallback('clahe',mouse_event_callback, [source_window,param,param2,paramh, paramb])
            sb=int(Seuil_bas/65000*255)
            sh=int(Seuil_haut/65000*255)
            cv2.setTrackbarPos('Seuil bas','sliders',sb)
            cv2.setTrackbarPos('Seuil haut','sliders',sh)
            
        cc=cv2.flip(cc,0)
        cv2.imshow('clahe',cc)

        
        if len(frames) >1:
            if len(frames)>3:
                #creation windows CV2 continuum
                top_w=top_w+tw
                left_w=left_w+lw
                cv2.namedWindow('continuum', cv2.WINDOW_NORMAL)
                cv2.moveWindow('continuum', top_w, left_w)
                cv2.resizeWindow('continuum',(int(newiw*sc), int(ih*sc)))
                # seuils image continuum 
                frameC=np.copy(frames[len(frames)-1])
                sub_frame=frameC[5:,:-5]
                Seuil_haut=np.percentile(sub_frame,99.999)
                Seuil_bas=(Seuil_haut*0.25)
                #print('seuil bas HC', Seuil_bas)
                #print('seuil haut HC', Seuil_haut)
                frameC[frameC>Seuil_haut]=Seuil_haut
                fcc=(frameC-Seuil_bas)* (65500/(Seuil_haut-Seuil_bas))
                fcc[fcc<0]=0
                frame_continuum=np.array(fcc, dtype='uint16')
                # display image
                frame_continuum=cv2.flip(frame_continuum,0)
                cv2.imshow('continuum',frame_continuum)
                # sauvegarde en png de continuum
                
                cv2.imwrite(basefich+'_dp'+str(range_dec[len(range_dec)-1])+'_cont.png',frame_continuum)
            
            top_w=top_w+tw
            left_w=left_w+lw
            cv2.namedWindow('doppler', cv2.WINDOW_NORMAL)
            cv2.moveWindow('doppler', top_w, left_w)
            cv2.resizeWindow('doppler',(int(newiw*sc), int(ih*sc)))
            
            if Flags["DOPCONT"] :
       
                #on se tente une image couleur...
                flag_erreur_doppler=False
                try :
                    img_doppler=np.zeros([frames[1].shape[0], frames[1].shape[1], 3],dtype='uint16')
                    if Flags["VOL"] :
                        moy=np.array(((frames[1]+frames[len(frames)-1])/2), dtype='uint16')
                    else:
                        moy=np.array(((frames[1]+frames[2])/2), dtype='uint16')
                    i2,Seuil_haut, Seuil_bas=seuil_image(moy)
                    i3=seuil_image_force(frames[2],Seuil_haut, Seuil_bas)
                    i1=seuil_image_force (frames[1],Seuil_haut, Seuil_bas)
                    #i1,Seuil_haut, Seuil_bas=seuil_image(frames[1])
                    #i3,Seuil_haut, Seuil_bas=seuil_image(frames[2])
                    img_doppler[:,:,0] = i1
                    img_doppler[:,:,1] = i2
                    img_doppler[:,:,2] = i3
                    img_doppler=cv2.flip(img_doppler,0)
                    cv2.imshow('doppler',img_doppler)
               
                except:
                    if LG == 1:
                        print ('Erreur image doppler.')
                    else:
                        print ('Doppler image error.')
                    flag_erreur_doppler=True
                    cv2.destroyWindow('doppler')
                    pass
    
                #sauvegarde en png de doppler
                if flag_erreur_doppler==False:
                    cv2.imwrite(basefich+'_doppler'+str(abs(range_dec[1]))+'.png',img_doppler)
    
            if Flags["WEAK"] :
       
                
                flag_erreur_weak=False
                try :
                    #moy=(frames[1]+frames[2])/2
                    #img_weak_array= frames[0]-moy
                    fr1=np.copy(frames[1])
                    fr2=np.copy(frames[2])
                    fr0=np.copy(frames[0])
                    s=np.array(np.array(fr1, dtype='float32')+np.array(fr2, dtype='float32'),dtype='float32')
                    moy=s*0.5
                    img_diff=np.array(np.array(fr1, dtype='float32')-np.array(fr2, dtype='float32'),dtype='int32')
                    
                    d=np.array((fr0-moy), dtype='int32')
    
                    
                    offset=-np.min(d)
                    #img_weak_array_nooff=np.copy(d)
                    #print(offset)
                    img_weak_array=d+offset
                    img_weak_uint=np.array((img_weak_array), dtype='uint16')
                    Seuil_bas=int(offset/2)
                    Seuil_haut=np.percentile(img_weak_array,99.95)
                    img_weak=seuil_image_force(img_weak_uint, Seuil_haut, Seuil_bas)
                    img_weak=np.array(img_weak, dtype='uint16')
                    img_weak=cv2.flip(img_weak,0)
                    cv2.imshow('doppler',img_weak)
                    cv2.setWindowTitle("doppler", "free line")
                    img_weak_array=d
    
               
                except:
                    if LG == 1:
                        print ('Erreur image ')
                    else:
                        print ('Image error.')
                    flag_erreur_doppler=True
                    cv2.destroyWindow('doppler')
                    pass
    
                #sauvegarde en png de doppler
                if flag_erreur_weak==False:
                    cv2.imwrite(basefich+'_free'+'.png',img_weak)
        
        #sauvegarde en png disk quasi sans seuillage de image sans decalage
        if range_dec[0]==0:
            img_suffix=""
        else:
            img_suffix="_dp"+str(range_dec[0])
            
        cv2.imwrite(basefich+img_suffix+'_raw.png',Disk2)
        #sauvegarde en png disk quasi seuils max
        cv2.imwrite(basefich+img_suffix+'_disk.png',frame_contrasted)
        cv2.imwrite(base_filename+'.jpg',frame_contrasted*0.0038)
        #sauvegarde en png seuils serrés
        cv2.imwrite(basefich+img_suffix+'_diskHC.png',frame_contrasted2)
        #sauvegarde en png seuils protus
        cv2.imwrite(basefich+img_suffix+'_protus.png',frame_contrasted3)
        cv2.imwrite(base_filename+'_protus.jpg',frame_contrasted3*0.0038)
        #sauvegarde en png de clahe
        cv2.imwrite(basefich+img_suffix+'_clahe.png',cc)
            
        
        # sauve les png multispectraux et cree une video
       
        if (Flags["VOL"] or Flags["POL"]) and len(range_dec)!=1:
            
            k=1
            
            #ROi de 200 pixels autour du centre du disque
    
            dim_roi=200
            rox1= cercle[0]-dim_roi
            rox2=cercle[0]+dim_roi
            roy1=cercle[1]-dim_roi
            roy2=cercle[1]+dim_roi
            
            # calcul moyenne intensité au centre du disque
            frame0=np.copy(frames[0])
            
            
            lum_roi=np.mean(frame0[roy1:roy2,rox1:rox2])
            lum_roi_ref=lum_roi*(65500/Seuil_haut)
            lum_roi_max=np.mean(frames[1][roy1:roy2,rox1:rox2])
           
            sub_frame=frame0[5:,:-5]*(lum_roi_ref/lum_roi)
            Seuil_haut=np.percentile(sub_frame,99.999)
            if Seuil_haut>65500: Seuil_haut=65500
            Seuil_bas=(Seuil_haut*0.15)
    
    
            a=1-(lum_roi_ref/lum_roi_max)
            mlum=a/((len(range_dec)-1)/2)
            #mlum=0
            flag_seuil_auto=False
            flag_lum_auto=True
            for i in range(1, len(range_dec)) :
                # image seuils moyen 
                framedec=np.copy(frames[i])
                sub_frame=framedec[5:,:-5]
                
                # calcul moyenne intensité au centre du disque
                lum_roi=np.mean(framedec[roy1:roy2,rox1:rox2])
                lum_coef=(lum_roi_ref/lum_roi)+(abs(range_dec[i])*mlum)
                
                if flag_lum_auto==True : 
                    framedec=framedec*lum_coef
                
                if flag_seuil_auto==True:
                    Seuil_haut=np.percentile(framedec[5:-5],99.999)
                    if Seuil_haut>65500: Seuil_haut=65500
                    Seuil_bas=(Seuil_haut*0.15)
              
                framedec[framedec>Seuil_haut]=Seuil_haut
                fdec=(framedec-Seuil_bas)* (65500/(Seuil_haut-Seuil_bas))
                fdec[fdec<0]=0
                frame_dec=np.array(fdec, dtype='uint16')
                cv2.waitKey(300)
                frame_dec=cv2.flip(frame_dec,0)
                cv2.imshow('doppler',frame_dec)
                
                if range_dec[i]+range_dec[i-1]==0 :
                    # il faut traiter le fait que l'image 0 est la premiere et
                    # n'est pas au milieu de la liste
                    frame0=np.copy(frames[0])
                    sub_frame=frame0[5:,:-5]
                    
                    # calcul moyenne intensité au centre du disque
                    lum_roi=np.mean(frame0[roy1:roy2,rox1:rox2])
                    lum_coef=(lum_roi_ref/lum_roi)+(abs(range_dec[i])*mlum)
                    
                    if flag_lum_auto==True:
                        frame0=frame0*lum_coef
                    if flag_seuil_auto==True:
                        Seuil_haut=np.percentile(frame0[5:-5],99.999)
                        if Seuil_haut>65500: Seuil_haut=65500
                        Seuil_bas=(Seuil_haut*0.15)
                    
                    frame0[frame0>Seuil_haut]=Seuil_haut
                    f0=(frame0-Seuil_bas)* (65500/(Seuil_haut-Seuil_bas))
                    f0[f0<0]=0             
                    frame_0=np.array(f0, dtype='uint16')
                    cv2.waitKey(500)
                    frame_0=cv2.flip(frame_0,0)
                    cv2.imshow('doppler',frame_0)
                    cv2.imwrite(basefich+'_dp'+str(k)+'.png',frame_0)
                    k=k+1
                
                cv2.imwrite(basefich+'_dp'+str(k)+'.png',frame_dec)
                k=k+1
                
            if  Flags["POL"]==False:
                #genere un fichier video
                filename=basefich+'.mp4'
                h, w=frames[0].shape
                height, width=(int(h*0.4),int(w*0.4))
                img=[]
                fourcc = cv2.VideoWriter_fourcc(*'h264')
                out = cv2.VideoWriter(filename, fourcc, 1.5, (width, height),0)
                for i in range(1,len(range_dec)+1) :
                    filename=basefich+'_dp'+str(i)+'.png'
                    img=cv2.imread(filename)
                    img2=cv2.resize(img,(width, height),interpolation = cv2.INTER_AREA)
                    out.write(img2)
        
                out and out.release()
                #cv2.destroyAllWindows() 
                    
        
        """
        #create colormap
        im = cv2.imread(basefich+'_clahe.png')
        im_max=(np.amax(im))*1.3
        im[im>im_max]=200
        #print ('im_max : ',im_max)
        scale=255/im_max
        imnp=np.array(im*scale, dtype='uint8')
        imC = cv2.applyColorMap(imnp, cv2.COLORMAP_HOT)
        iw=int(imC.shape[1]*sc)
        ih=int(imC.shape[0]*sc)
        cv2.resize(imC,dsize=(ih,iw))
        cv2.namedWindow('color', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('color', iw, ih)
        top_w=top_w+tw
        left_w=left_w+lw
        cv2.moveWindow('color',top_w, left_w)
        cv2.imshow('color',imC)
        cv2.waitKey(tempo)
        cv2.imwrite(basefich+'_color.png',imC)
        """
        #t1=time.time()
        #print('affichage : ', t1-t0)
    
      
        #sauvegarde les fits
        frame2=np.copy(frames[0])
        if Flags['WEAK']:
            frame2=np.copy(img_weak_array)
            DiskHDU=fits.PrimaryHDU(frame2,header)
            DiskHDU.writeto(basefich+'_free.fits', overwrite='True')
            frame3=np.copy(img_diff)
            DiskHDU=fits.PrimaryHDU(frame3,header)
            DiskHDU.writeto(basefich+'_diff.fits', overwrite='True')
            # sauve les images individuelles pour debug
            DiskHDU=fits.PrimaryHDU(fr0,header)
            DiskHDU.writeto(basefich+'_x0.fits', overwrite='True')
            DiskHDU=fits.PrimaryHDU(fr1,header)
            DiskHDU.writeto(basefich+'_x1.fits', overwrite='True')
            DiskHDU=fits.PrimaryHDU(fr2,header)
            DiskHDU.writeto(basefich+'_x2.fits', overwrite='True')
            DiskHDU=fits.PrimaryHDU(moy,header)
            DiskHDU.writeto(basefich+'_moy.fits', overwrite='True')
            
        else:
            """
            frame2=np.array(cl1, dtype='uint16')
            DiskHDU=fits.PrimaryHDU(frame2,header)
            DiskHDU.writeto(basefich+'_clahe.fits', overwrite='True')
            """
        
        if Flags['POL']:
            # renomme les dp fits en r et b
            ImgFileb=basefich+'_dp'+str(range_dec[1])+'_recon.fits'
            ImgFiler=basefich+'_dp'+str(range_dec[2])+'_recon.fits'
            os.replace(ImgFileb,racines[0]+str(ii)+".fits")
            os.replace(ImgFiler,racines[1]+str(ii)+".fits")
            print('Sorties :')
            print(racines[0]+str(ii)+".fits")
            print(racines[1]+str(ii)+".fits")
            # renomme les dp png en r et b
            ImgFileb=basefich+'_dp2.png'
            ImgFiler=basefich+'_dp3.png'
            os.replace(ImgFileb,racines[0]+str(ii)+".png")
            os.replace(ImgFiler,racines[1]+str(ii)+".png")
    
        if Flags['VOL'] and Flags["FITS3D"]:
            
            hdr_vol=header
            hdr_vol['NAXIS']=3
            hdr_vol['NAXIS3']=len(frames)
            hdr_vol['CTYPE3']='wavelength'
            hdr_vol['CUNIT3']='Angstrom'
            # insert fullprofile dans le nom
            a=header['FILENAME'].split('SOLEX')
            filename_3D=a[0]+'SOLEX_fullprofile'+a[1]
            hdr_vol['FILENAME']=filename_3D
            #print(hdr_vol['FILENAME'])
            hdr_vol['CDELT3']=0.155
            n=len(frames)-1
            demi_n=int(n/2)
            # remet la premiere frame au centre car correspond a dec=0
            t=frames[0]
            frames[0:demi_n-1]=frames[1:demi_n]
            frames[demi_n+1:]=frames[demi_n:]
            frames[demi_n]=t
            
            DiskHDU=fits.PrimaryHDU(frames,hdr_vol)
            DiskHDU.writeto(filename_3D, overwrite='True')
            
    
        # V3.2 -> tempo après sauvegarde des fichiers
        cv2.waitKey(tempo)
        
        cv2.destroyAllWindows()
          
        """
        not really useful, too small, better to use png or fits
        and strange message on spyder when UI display "can't invoke "event" command"
        seems to be linked to tk (procedure "ttk::ThemeChanged" line 6)
        
        # ajout de feuille de summary
        screen = tk.Tk()
        screensize = screen.winfo_screenwidth(), screen.winfo_screenheight()
        screen.destroy()
        im_1= cv2.hconcat([frame_contrasted, frame_contrasted2])
        im_2=cv2.hconcat([frame_contrasted3, cc])
        im=cv2.vconcat([im_1,im_2])
        scale=min(screensize[0]/im.shape[1], screensize[1]/im.shape[0])
        cv2.namedWindow('summary', cv2.WINDOW_NORMAL)
        cv2.moveWindow('summary', 0,0)
        cv2.resizeWindow('summary', int(im.shape[1]*scale), int(im.shape[0]*scale))
        cv2.imshow('summary', im)
    
        #sauvegarde en png pour appliquer une colormap par autre script
        cv2.imwrite(basefich+'_summary.png',im)
    
        cv2.waitKey(tempo)
        cv2.destroyAllWindows()
        """
        print (serfile)
        ii=ii+1 # boucle sur non de fichier pour generer sequence en polarimetrie
        print()

