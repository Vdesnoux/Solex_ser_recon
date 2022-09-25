# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 16:38:55 2020
Version 20 mai 2021

@author: valerie

Front end de traitements spectro helio de fichier ser
- interface pour selectionner un ou plusieurs fichiers
- appel au module inti_recon qui traite la sequence et genere les fichiers fits

----------------------------------------------------------------------------------------------------------------

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
# import tkinter as tk


#import time

import PySimpleGUI as sg

# -------------------------------------------------------------
global LG # Langue de l'interfacer (1 = FR ou 2 = US)
LG = 1
# -------------------------------------------------------------

SYMBOL_UP =    '▲'
SYMBOL_DOWN =  '▼'
current_version = 'Inti V4.0.0 by V.Desnoux et.al. '

def mouse_event_callback( event,x,y,flags,param):
    if event == cv2.EVENT_MOUSEMOVE:
        try :
            param=param[y-150:y+150,x-150:x+150]
            cv2.imshow('Zoom', param)
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



def UI_SerBrowse (WorkDir,saved_tilt, saved_ratio, dec_pix_dop, dec_pix_cont, poly, pos_free_blue, pos_free_red,win_pos, previous_serfile, data_entete):

    sg.theme('Dark2')
    sg.theme_button_color(('white', '#500000'))
    #print('ui :', os.path.join(WorkDir,previous_serfile))
    Shift=[]
    Flags={}
    Flags["DOPCONT"]=False
    Flags["VOL"]=False
    Flags["POL"]=False
    Flags["WEAK"]=False
    Racines=[]

    
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
                [sg.Text('Observateur :', size=(10,1)), sg.Input(default_text=data_entete[0], size=(20,1),key='-OBSERVER-')],
                [sg.Text('Site Long :', size=(10,1)), sg.Input(default_text=data_entete[2], size=(10,1),key='-SITE_LONG-'),
                 sg.Text('  Site Lat :', size=(10,1)), sg.Input(default_text=data_entete[3], size=(10,1),key='-SITE_LAT-'),
                 sg.Text(' in decimal degree')],
                [sg.Text('Instrument :', size=(10,1)), sg.Input(default_text=data_entete[1], size=(35,1),key='-INSTRU-')]
                ]
    else:
        section2 = [
                [sg.Text('Observer :', size=(10,1)), sg.Input(default_text=data_entete[0], size=(25,1),key='-OBSERVER-')],
                [sg.Text('Site Long :', size=(10,1)), sg.Input(default_text=data_entete[2], size=(10,1),key='-SITE_LONG-'),
                 sg.Text('  Site Lat :', size=(10,1)), sg.Input(default_text=data_entete[3], size=(10,1),key='-SITE_LAT-'),
                 sg.Text(' in decimal degree')],
                [sg.Text('Instrument :', size=(10,1)), sg.Input(default_text=data_entete[1], size=(35,1),key='-INSTRU-')]
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
             sg.T('Entête', enable_events=True, text_color='white', k='-OPEN SEC2-TEXT')],
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
            [sg.Text('Plage en pixels :',size=(12,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='Volume',enable_events=True), sg.Text('+/- pixels')]
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
             sg.T('Header', enable_events=True, text_color='white', k='-OPEN SEC2-TEXT')],
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
            [sg.Text('Range in pixels :',size=(12,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='Volume',enable_events=True), sg.Text('+/- pixels')]
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
            [sg.Text('Fichier(s) :', size=(6, 1)), sg.InputText(default_text='',size=(66,1),key='-FILE-'),
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
            [sg.Text('File(s) :', size=(5, 1)), sg.InputText(default_text='',size=(70,1),key='-FILE-'),
             sg.FilesBrowse(' Open ',file_types=(("SER Files", "*.ser"),),initial_folder=os.path.join(WorkDir,previous_serfile))],
            
            [sg.TabGroup([[sg.Tab('  General  ', tab1_layout), sg.Tab('Doppler & Continuum', tab2_layout,), 
                sg.Tab('Doppler sequence', tab3_layout,),
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
    
    while True:
        event, values = window.read()
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

    window.close()
    try:          
        FileNames=values['-FILE-']
    except:
        FileNames=''

    #if FileNames==None :
            #FileNames=''

    
    
    Flags["RTDISP"]=values['-DISP-']
    #Flags["DOPCONT"]=values['-DOPCONT-']
    Flags["ALLFITS"]=values['-SFIT-']
    #Flags["VOL"]=values['-VOL-']
    #Flags["POL"]=values['-POL-']
    #Flags["WEAK"]=values['-WEAK-']
    Flags["sortie"]=Flag_sortie
   # print(Flags)
    
    ratio_fixe=float(values['-RATIO-'])
    ang_tilt=values['-TILT-']
    Data_entete=[values['-OBSERVER-'], values['-INSTRU-'], float(values['-SITE_LONG-']), float(values['-SITE_LAT-'])]
    
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
    
    return FileNames, Shift, Flags, ratio_fixe,ang_tilt, poly, Racines, Data_entete

"""
-------------------------------------------------------------------------------------------
Program starts here !
--------------------------------------------------------------------------------------------
"""
Flag_sortie=False
serfiles=[]
previous_serfile=''
my_ini=os.getcwd()+'/inti.yaml'
global mouse_x, mouse_y
mouse_x,mouse_y=0,0

while not Flag_sortie :
    
    # inti.yaml is a bootstart file to read last directory used by app
    # this file is stored in the module directory
    
    #my_ini=os.path.dirname(sys.argv[0])+'/inti.yaml'
    #my_ini=os.getcwd()+'/inti.yaml'
    my_dictini={'directory':'', 'dec doppler':3, 'dec cont':15, 'poly_slit_a':0, "poly_slit_b":0,'poly_slit_c':0, 
                'ang_tilt':0, 'ratio_sysx':0, 'poly_free_a':0,'poly_free_b':0,'poly_free_c':0,
                'pos_free_blue':0, 'pos_free_red':0,
                'win_posx':300, 'win_posy':200, 'observer':'', 'instru':'','site_long':0, 'site_lat':0}
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
    saved_ratio=float(my_dictini['ratio_sysx'])
    poly.append(float(my_dictini['poly_free_a']))
    poly.append(float(my_dictini['poly_free_b']))
    poly.append(float(my_dictini['poly_free_c']))
    pos_free_blue=int(my_dictini['pos_free_blue'])
    pos_free_red=int(my_dictini['pos_free_red'])
    w_posx=int(my_dictini['win_posx'])
    w_posy=int(my_dictini['win_posy'])
    win_pos=(w_posx,w_posy)
    data_entete=[my_dictini['observer'], my_dictini['instru'],float(my_dictini['site_long']),float(my_dictini['site_lat'])]
    
    
    # Recupere paramatres de la boite de dialogue
    #print('serfile previous : ', previous_serfile)
    serfiles, Shift, Flags, ratio_fixe,ang_tilt, poly, racines, data_entete= UI_SerBrowse(WorkDir, saved_tilt, saved_ratio,
                                                                             dec_pix_dop, dec_pix_cont, poly,pos_free_blue, pos_free_red,
                                                                             win_pos, previous_serfile, data_entete)
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
        tempo=60000 #tempo 60 secondes, pour no tempo mettre tempo=0 et faire enter pour terminer
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
        frames, header, cercle, range_dec, geom, polynome=sol.solex_proc(serfile,Shift,Flags,ratio_fixe,ang_tilt, poly, data_entete)
        
        # met a jour le repertoire et les flags dans le fichier ini, oui a chaque fichier pour avoir le bon rep
        my_dictini['directory']=WorkDir
        # ajout data entete
        my_dictini['observer']=str(data_entete[0])
        my_dictini['instru']=str(data_entete[1])
        my_dictini['site_long']=data_entete[2]
        my_dictini['site_lat']=data_entete[3]
        
        if Flags['WEAK']:
           my_dictini['pos_free_blue']=round(poly[2]+Shift[1])
           my_dictini['pos_free_red']=round(poly[2]+Shift[2])
        else:
            my_dictini['dec doppler']=Shift[1]
            my_dictini['dec cont']=Shift[2]

        my_dictini['ang_tilt']=ang_tilt
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
             
        #if Shift != 0 :
            #add shift value in filename to not erase previous file
            #basefich=basefich+'_dp'+str(Shift) # ajout '_' pour avoir fichier en tete dans explorer/finder
    
        ih = frames[0].shape[0]
        newiw = frames[0].shape[1]
    
        top_w=0
        left_w=0
        tw=150
        lw=34
        
        # my screensize is 1536x864 - harcoded as tk.TK() produces an error in spyder
        # plus petit for speed up
        screensizeH = (864-50) - (3*lw) 
        screensizeW = (1536)-(3*tw)
        
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
        
              
        
        
        if len(frames)==1 and len(serfiles)==1:
            cv2.namedWindow('Zoom', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Zoom', 300, 300)
            cv2.moveWindow('Zoom',20,20)
    
        
        # create a CLAHE object (Arguments are optional)
        #clahe = cv2.createCLAHE(clipLimit=0.8, tileGridSize=(5,5))
        clahe = cv2.createCLAHE(clipLimit=0.8, tileGridSize=(2,2))
        cl1 = clahe.apply(frames[0])
        
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
            cv2.setMouseCallback('contrast',mouse_event_callback, param)
        cv2.imshow('contrast',frame_contrasted)
        
        
        #cv2.imshow('sun',frame_contrasted)
        #cv2.waitKey(0)
    
        # image raw
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
            cv2.imshow('protus',frame_contrasted3)
            #cv2.waitKey(0)
        
        #improvements suggested by mattC to hide sun with disk
        else :           
            # hide disk before setting max threshold
            disk_limit_percent=0.001 # black disk radius inferior by 1% to disk edge
            frame2=np.copy(frames[0])
            if cercle[0]!=0:
                x0=cercle[0]
                y0=cercle[1]
                wi=round(cercle[2])
                he=round(cercle[3])
                r=(min(wi,he))
                r=int(r- round(r*disk_limit_percent))
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
                    cv2.setMouseCallback('protus',mouse_event_callback, param)
                cv2.imshow('protus',frame_contrasted3)
            else:
                if LG == 1:
                    print("Erreur disque occulteur.")
                else:
                    print("Mask disk error.")
                    
                frame_contrasted3=frame_contrasted
            
        Seuil_bas=np.percentile(cl1, 25)
        Seuil_haut=np.percentile(cl1,99.9999)*1.05
        cc=(cl1-Seuil_bas)*(65000/(Seuil_haut-Seuil_bas))
        cc[cc<0]=0
        cc=np.array(cc, dtype='uint16')
        if len(frames)==1 and len(serfiles)==1:
            param=np.copy(cc)
            cv2.setMouseCallback('clahe',mouse_event_callback, param)
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
                    img_doppler=np.zeros([ih, frames[1].shape[1], 3],dtype='uint16')
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
        #sauvegarde en png seuils serrés
        cv2.imwrite(basefich+img_suffix+'_diskHC.png',frame_contrasted2)
        #sauvegarde en png seuils protus
        cv2.imwrite(basefich+img_suffix+'_protus.png',frame_contrasted3)
        #sauvegarde en png de clahe
        cv2.imwrite(basefich+img_suffix+'_clahe.png',cc)
            
        
        # sauve les png multispectraux et cree une video
       
        if Flags["VOL"] or Flags["POL"] :
            
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
            frame2=np.array(cl1, dtype='uint16')
            DiskHDU=fits.PrimaryHDU(frame2,header)
            DiskHDU.writeto(basefich+'_clahe.fits', overwrite='True')
        
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

