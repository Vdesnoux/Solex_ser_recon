# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 16:38:55 2020
Version 20 mai 2021

@author: valerie

Front end de traitements spectro helio de fichier ser
- interface pour selectionner un ou plusieurs fichiers
- appel au module inti_recon qui traite la sequence et genere les fichiers fits
- decalage en longueur d'onde avec Shift

- ajout d'une zone pour entrer un ratio fixe et un angle de tilt fixe. Si reste à zero alors il sera calculé
automatiquement
- sauvegarde fichier avec pixel shift in filename if shift<>0

-----------------------------------------------------------------------------------------------------------------
version du 27 avril 2022 - Paris
- correction bug multiple fichier test si pas de nom de fichier

version du 23 avril 2022 - Paris
- ajout onglet de calcul d'une sequence doppler
- ajout de generation film mp4
- ajout onglet de la fonction magnetogramme
- ajout de memoire de boucle sur fichier traité pour gérér sequence b et v 
- creation d'une version anglaise par swith LG a la compil
- ajout de sauvegarde des coefficients de polynomes
- ajout de sauvegarde angle de tilt et facteur echelle avec flag dans advanced


Version du 1er janv 2022
- correction bug si tilt important avec offset de y1,y2 lié au crop
- meilleure gestion des erreurs si mauvais scan

version du 26 sept 2021
- ajoute boucle pour generer images doppler et continuum
- flag dans ui pour activer ou pas  doppler et cont
- ajout pixel shift dans noms d1 et d2
- fichier ini en yaml avec valeurs dec dop et cont stockées


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
current_version = 'Inti V3.2.2 by V.Desnoux et.al. '

def collapse(layout, key):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this seciton visible / invisible
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key))



def UI_SerBrowse (WorkDir,saved_tilt, saved_ratio, dec_pix_dop, dec_pix_cont, poly):
    """
    Parameters
    ----------
    WorkDir : TYPE string
        repertoire par defaut à l'ouverture de la boite de dialogue

    Returns 
    -------
    Filenames : TYPE string
        liste des fichiers selectionnés, avec leur extension et le chemin complet
    Shift : Type array of int
        Ecart en pixel demandé pour reconstruire le disque, les deux images 
        doppler et le continuum sur une longeur d'onde en relatif par rapport au centre de la raie  
    ratio_fixe : ratio Y/X en fixe, si egal à zéro alors calcul automatique
    angle_fixe : angle de tilt, si egal à zéro alors calcul automatique
    flag_isplay: affiche ou non la construction du disque en temps réel
    """
    sg.theme('Dark2')
    sg.theme_button_color(('white', '#500000'))

    
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
        tab1_layout = [      
            #### Section 1 part ####
            [sg.T(SYMBOL_UP, enable_events=True, k='-OPEN SEC1-', text_color='white'), sg.T('Avancé', enable_events=True, text_color='white', k='-OPEN SEC1-TEXT')],
            [collapse(section1, '-SEC1-')],
            [sg.Text('Décalage en pixels :',size=(15,1)),sg.Input(default_text='0',size=(4,1),key='-DX-',enable_events=True)]
            ]
        
        tab2_layout =[
            [sg.Checkbox(' Calcul images Doppler et Continuum ', default=False, key='-DOPCONT-')],
            [sg.Text('Decalage doppler :',size=(16,1)),sg.Input(default_text=dec_pix_dop,size=(4,1),key='-DopX-',enable_events=True)],
            [sg.Text('Decalage continuum :',size=(16,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='-ContX-',enable_events=True)]
            ]
        
        tab3_layout =[
            [sg.Checkbox(' Synthèse d\'une séquence d\'images décalées spectralement ', default=False, key='-VOL-')],
            [sg.Text('Plage en pixels :',size=(12,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='Volume',enable_events=True), sg.Text('+/- pixels')]
            ]
       
        tab4_layout =[
            [sg.Checkbox(' Zeeman ', default=False, key='-POL-')],
            
            [sg.Text('Position raie :'),sg.Input(default_text=poly[2],size=(5,1),key='c'),
             sg.Text('  Ecartement en pixels :',size=(17,1)),sg.Input(default_text=2,size=(3,1),key='Zeeman_wide',enable_events=True), sg.Text('+/- pixels'),
             sg.Text('  Décalage :'), sg.Input(default_text=0,size=(4,1),key='Zeeman_shift',enable_events=True)],
        
            [sg.Text('Coefficient polynome forme fente : ',size=(24,1)),sg.Input(default_text=poly[0],size=(9,1),key='a'), sg.Text('x2'),
             sg.Input(default_text=poly[1],size=(9,1),key='b'), sg.Text('x')],
            
            [sg.Text('Nom fichier racine aile bleue :'), sg.Input(default_text="b-", size=(15,1), key='racine_bleu')],
            [sg.Text('Nom fichier racine aile rouge :'), sg.Input(default_text="r-", size=(15,1), key='racine_rouge')]
            ]
    else:
        tab1_layout = [      
            #### Section 1 part ####
            [sg.T(SYMBOL_UP, enable_events=True, k='-OPEN SEC1-', text_color='white'), sg.T('Advanced', enable_events=True, text_color='white', k='-OPEN SEC1-TEXT')],
            [collapse(section1, '-SEC1-')],
            [sg.Text('Shift in pixels :',size=(11,1)),sg.Input(default_text='0',size=(4,1),key='-DX-',enable_events=True)]
            ]
        
        tab2_layout =[
            [sg.Checkbox(' Compute Doppler and Continuum images ', default=False, key='-DOPCONT-')],
            [sg.Text('Doppler shift :',size=(12,1)),sg.Input(default_text=dec_pix_dop,size=(4,1),key='-DopX-',enable_events=True)],
            [sg.Text('Continuum shift :',size=(12,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='-ContX-',enable_events=True)]
            ]
        
        tab3_layout =[
            [sg.Checkbox(' Generate a spectraly shifted images sequence ', default=False, key='-VOL-')],
            [sg.Text('Range in pixels :',size=(12,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='Volume',enable_events=True), sg.Text('+/- pixels')]
            ]
       
        tab4_layout =[
            [sg.Checkbox(' Zeeman ', default=False, key='-POL-')],
            
            [sg.Text('Line position :'),sg.Input(default_text=poly[2],size=(5,1),key='c'),
             sg.Text(' Pixels spacing :',size=(12,1)),sg.Input(default_text=2,size=(3,1),key='Zeeman_wide',enable_events=True), sg.Text('+/- pixels'),
             sg.Text(' Shift  :'), sg.Input(default_text=0,size=(4,1),key='Zeeman_shift',enable_events=True)],
        
            [sg.Text('Polynom terms of slit distorsion : ',size=(24,1)),sg.Input(default_text=poly[0],size=(9,1),key='a'), sg.Text('x2'),
             sg.Input(default_text=poly[1],size=(9,1),key='b'), sg.Text('x')],
            
            [sg.Text('Bleu line wing generic file name :'), sg.Input(default_text="b-", size=(15,1), key='racine_bleu')],
            [sg.Text('Red line wing generic file name  :'), sg.Input(default_text="r-", size=(15,1), key='racine_rouge')]
            ]
    
    if LG == 1:
        layout = [
            [sg.Text('Fichier(s) :', size=(6, 1)), sg.InputText(default_text='',size=(66,1),key='-FILE-'),
             sg.FilesBrowse(' Ouvrir ',file_types=(("SER Files", "*.ser"),),initial_folder=WorkDir)],
            
            [sg.TabGroup([[sg.Tab('  Général  ', tab1_layout), sg.Tab(' Doppler & Continuum ', tab2_layout,), 
                sg.Tab(' Séquence Doppler ', tab3_layout,),
                sg.Tab(' Magnétogramme ',tab4_layout,)]],tab_background_color='#404040')],  
            [sg.Button('Ok', size=(14,1)), sg.Cancel('  Annuler  ')],
            [sg.Text(current_version, size=(30, 1),text_color='Tan', font=("Arial", 8, "italic"))]
            ]
    else:
        layout = [
            [sg.Text('File(s) :', size=(5, 1)), sg.InputText(default_text='',size=(70,1),key='-FILE-'),
             sg.FilesBrowse(' Open ',file_types=(("SER Files", "*.ser"),),initial_folder=WorkDir)],
            
            [sg.TabGroup([[sg.Tab('  General  ', tab1_layout), sg.Tab(' Doppler & Continuum ', tab2_layout,), 
                sg.Tab(' Doppler sequence ', tab3_layout,),
                sg.Tab(' Magnetogram ',tab4_layout,)]],tab_background_color='#404040')],  
            [sg.Button('Ok', size=(14,1)), sg.Cancel('  Cancel  ')],
            [sg.Text(current_version, size=(30, 1),text_color='Tan', font=("Arial", 8, "italic"))]
            ]
            
    
    window = sg.Window('INTI', layout, finalize=True)
    opened1 = False
    window['-SEC1-'].update(visible=opened1)
    
    window['-FILE-'].update(WorkDir) 
    window.BringToFront()
    
    while True:
        event, values = window.read()
        if event==sg.WIN_CLOSED or event=='  Cancel  ' or event=='  Annuler  ': 
            break
        
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

    window.close()
    try:          
        FileNames=values['-FILE-']
    except:
        FileNames=''

    #if FileNames==None :
            #FileNames=''
    Shift=[]
    Flags={}
    Poly=[]
    Racines=[]


    Poly.append(float(values['a']))
    Poly.append(float(values['b']))
    Poly.append(float(values['c']))
    Flags["RTDISP"]=values['-DISP-']
    Flags["DOPCONT"]=values['-DOPCONT-']
    Flags["ALLFITS"]=values['-SFIT-']
    Flags["VOL"]=values['-VOL-']
    Flags["POL"]=values['-POL-']
    ratio_fixe=float(values['-RATIO-'])
    ang_tilt=values['-TILT-']
    if values['-F_ANG_SXSY-']!=True:
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
    
    return FileNames, Shift, Flags, ratio_fixe,ang_tilt, Poly, Racines

"""
-------------------------------------------------------------------------------------------
Program starts here !
--------------------------------------------------------------------------------------------
"""

# inti.yaml is a bootstart file to read last directory used by app
# this file is stored in the module directory

#my_ini=os.path.dirname(sys.argv[0])+'/inti.yaml'
my_ini=os.getcwd()+'/inti.yaml'
my_dictini={'directory':'', 'dec doppler':3, 'dec cont':15, 'poly_slit_a':0, "poly_slit_b":0,'poly_slit_c':0, 'ang_tilt':0, 'ratio_sysx':0}
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
poly.append(float(my_dictini['poly_slit_a']))
poly.append(float(my_dictini['poly_slit_b']))
poly.append(float(my_dictini['poly_slit_c']))
saved_tilt=float(my_dictini['ang_tilt'])
saved_ratio=float(my_dictini['ratio_sysx'])

# Recupere paramatres de la boite de dialogue
serfiles, Shift, Flags, ratio_fixe,ang_tilt, poly, racines= UI_SerBrowse(WorkDir, saved_tilt, saved_ratio,dec_pix_dop, dec_pix_cont, poly)
serfiles=serfiles.split(';')
ii=1

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
    
    # met a jour le repertoire et les flags dans le fichier ini, oui a chaque fichier pour avoir le bon rep
    my_dictini['directory']=WorkDir
    my_dictini['dec doppler']=Shift[1]
    my_dictini['dec cont']=Shift[2]
    my_dictini['poly_slit_a']=poly[0]
    my_dictini['poly_slit_b']=poly[1]
    my_dictini['poly_slit_c']=poly[2]
    my_dictini['ang_tilt']=ang_tilt
    my_dictini['ratio_sysx']=ratio_fixe
    
    try:
        with open(my_ini, "w") as f1:
            yaml.dump(my_dictini, f1, sort_keys=False)
    except:
        if LG == 1:
            logme ('Erreur lors de la sauvegarde de inti.yaml comme : '+my_ini)
        else:
            logme ('Error saving inti.yaml as: '+my_ini)

    # appel au module d'extraction, reconstruction et correction
    #
    # basefich: nom du fichier ser sans extension et sans repertoire
    # dx: decalage en pixel par rapport au centre de la raie 
    
    if Flags['POL'] and ii>1:
        ratio_fixe=geom[0]
        ang_tilt=geom[1]
    
    frames, header, cercle, range_dec, geom=sol.solex_proc(serfile,Shift,Flags,ratio_fixe,ang_tilt, poly)
    
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
    cv2.imshow('contrast',frame_contrasted2)
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
        
        if Flags["DOPCONT"]:
   
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
        lum_roi_ref=30000
        sub_frame=frame0[5:,:-5]*(lum_roi_ref/lum_roi)
        Seuil_haut=np.percentile(sub_frame,99.999)
        Seuil_bas=(Seuil_haut*0.15)
        
        # fenetre doppler ajutée
        #cv2.namedWindow('video', cv2.WINDOW_NORMAL)
        #cv2.moveWindow('video', 0, 0)
        #h, w=(int(frame0.shape[0]*0.2),int(frame0.shape[1]*0.2))
        #cv2.resizeWindow('video',(w, h))
   
        
        for i in range(1, len(range_dec)) :
            # image seuils moyen 
            framedec=np.copy(frames[i])
            sub_frame=framedec[5:,:-5]
            
            # calcul moyenne intensité au centre du disque
            lum_roi=np.mean(framedec[roy1:roy2,rox1:rox2])
            lum_coef=lum_roi_ref/lum_roi
            framedec=framedec*lum_coef

            framedec[framedec>Seuil_haut]=Seuil_haut
            fdec=(framedec-Seuil_bas)* (65500/(Seuil_haut-Seuil_bas))
            fdec[fdec<0]=0
            frame_dec=np.array(fdec, dtype='uint16')
            cv2.waitKey(300)
            cv2.imshow('doppler',frame_dec)
            
            if range_dec[i]+range_dec[i-1]==0 :
                frame0=np.copy(frames[0])
                sub_frame=frame0[5:,:-5]
                
                # calcul moyenne intensité au centre du disque
                lum_roi=np.mean(frame0[roy1:roy2,rox1:rox2])
                lum_coef=lum_roi_ref/lum_roi
                frame0=frame0*lum_coef
                
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

  
    #sauvegarde le fits
    frame2=np.copy(frames[0])
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

