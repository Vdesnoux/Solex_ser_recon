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



Version 16 juillet 2021
- remplacement des methodes des limbes par fit_ellipse
- modification code avec code de Doug & Andrew Smith pour acceleration stupefiante
    o vectorisation dans calcul extraction des intensités pour reconstruction du disque
    o vectorisation dans le calcul de slant, qui est en fait un calcul de tilt
- fichier ini a la racine du repertoire ou est le script (etait en dur)
- ajout d'un flag pour afficher ou pas le disque noir dans image png ayant les seuils adequats pour les protus

To be noted... image fits data are the image pixels value, no change of dynamic, no thresholding. Only png images are thresholded.
Black disk is a python graphic overlay, not burned into images. Circle data are logged for ISIS processing.

Version 11 aout 2021
- suppression des flags dans la GUI pour simplification
- ajout image de summary from JF Pitet et gestion screen tk from JB Butet

"""
import numpy as np
import cv2
import os
import sys
import Inti_recon as sol
from astropy.io import fits
import tkinter as tk


#import time

import PySimpleGUI as sg

def UI_SerBrowse (WorkDir):
    """
    Parameters
    ----------
    WorkDir : TYPE string
        repertoire par defaut à l'ouverture de la boite de dialogue

    Returns 
    -------
    Filenames : TYPE string
        liste des fichiers selectionnés, avec leur extension et le chemin complet
    Shift : Type string
        Ecart en pixel demandé pour reconstruire le disque 
        sur une longeur d'onde en relatif par rapport au centre de la raie  
    ratio_fixe : ratio Y/X en fixe, si egal à zéro alors calcul automatique
    flag_isplay: affiche ou non la construction du disque en temps réel
    """
    sg.theme('Dark2')
    sg.theme_button_color(('white', '#500000'))
    
    layout = [
    [sg.Text('Nom du fichier', size=(15, 1)), sg.InputText(default_text='',size=(65,1),key='-FILE-'),
     sg.FilesBrowse('Open',file_types=(("SER Files", "*.ser"),),initial_folder=WorkDir)],
    #[sg.Checkbox('Affiche reconstruction ', default=False, key='-DISP-')],
    #[sg.Checkbox('Affiche disque noir sur image protuberances', default=True, key='-DISK-')],
    #[sg.Checkbox('Sauve uniquement fits _recon et _clahe ', default=True, key='-SFIT-')],
    [sg.Text('Ratio SY/SX (auto:0, fixe: valeur differente de zero) ', size=(45,1)), sg.Input(default_text='0', size=(5,1),key='-RATIO-')],
    [sg.Text('Angle Tilt en degrés (auto:0, fixe: valeur differente de zero) ', size=(45,1)), sg.Input(default_text='0', size=(5,1),key='-TILT-')],
    [sg.Text('Decalage pixel',size=(15,1)),sg.Input(default_text='0',size=(5,1),key='-DX-',enable_events=True)],  
    [sg.Button('Ok'), sg.Cancel()]
    ] 
    
    window = sg.Window('Processing', layout, finalize=True)
    
    window['-FILE-'].update(WorkDir) 
    window.BringToFront()
    
    while True:
        event, values = window.read()
        if event==sg.WIN_CLOSED or event=='Cancel': 
            break
        
        if event=='Ok':
            break

    window.close()
               
    FileNames=values['-FILE-']
    Shift=values['-DX-']
    
    #flag_display=values['-DISP-']
    flag_display=False
    ratio_fixe=float(values['-RATIO-'])
    #disk_display=values['-DISK-']
    disk_display=True
    #sfit_onlyfinal=values['-SFIT-']
    sfit_onlyfinal=False
    ang_tilt=values['-TILT-']
    
    return FileNames, Shift, flag_display, ratio_fixe, disk_display, sfit_onlyfinal,ang_tilt

"""
-------------------------------------------------------------------------------------------
Program starts here !
--------------------------------------------------------------------------------------------
"""

# inti.ini is a bootstart file to read last directory used by app
# this file is stored in the module directory

try:
    mydir_ini=os.path.dirname(sys.argv[0])+'/inti.ini'
    #print('mon repertoire : ', mydir_ini)
    with open(mydir_ini, "r") as f1:
        param_init = f1.readlines()
        WorkDir=param_init[0]
except:
    WorkDir=''

# Recupere paramatres de la boite de dialogue
serfiles, Shift, flag_display, ratio_fixe, disk_display,sfit_onlyfinal, ang_tilt = UI_SerBrowse(WorkDir)
serfiles=serfiles.split(';')


# pour gerer la tempo des affichages des images resultats dans cv2.waitKey
# si plusieurs fichiers à traiter
if len(serfiles)==1:
    tempo=60000 #tempo 60 secondes, pour no tempo mettre tempo=0 et faire enter pour terminer
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
        print('erreur nom de fichier : ',serfile)
        sys.exit()
    
    # met a jour le repertoire si on a changé dans le fichier ini
    try:
        with open(mydir_ini, "w") as f1:
            f1.writelines(WorkDir)
    except:
        pass
    

    # appel au module d'extraction, reconstruction et correction
    #
    # basefich: nom du fichier ser sans extension et sans repertoire
    # dx: decalage en pixel par rapport au centre de la raie 
    
    try:
        Shift=int(Shift)
    except:
        Shift=0
    
    frame, header, cercle=sol.solex_proc(serfile,Shift,flag_display,ratio_fixe,sfit_onlyfinal,ang_tilt)
    
    base=os.path.basename(serfile)
    basefich=os.path.splitext(base)[0]
    
    if Shift != 0 :
        #add shift value in filename to not erase previous file
        basefich=basefich+'_dp'+str(Shift)

    ih=frame.shape[0]
    newiw=frame.shape[1]

    top_w=0
    left_w=0
    tw=180
    lw=32
    
    
    # my screensize is 1536x864 - harcoded as tk.TK() produces an error in spyder
    # plus petit for speed up
    screensizeH = (800-50) - (3*lw) 
    screensizeW = (1200)-(3*tw)
    
    # gere reduction image png
    nw = screensizeW/newiw
    nh = screensizeH/ih
    sc=min(nw,nh)
    
    if sc >= 1 :
        sc = 1
    
    """
    cv2.namedWindow('sun0', cv2.WINDOW_NORMAL)
    cv2.moveWindow('sun0', 0, 0)
    cv2.resizeWindow('sun0', (int(newiw*sc), int(ih*sc)))
    cv2.imshow('sun0',frame)
  
    top_w=top_w+tw
    left_w=left_w+lw
    """
    cv2.namedWindow('sun', cv2.WINDOW_NORMAL)
    cv2.moveWindow('sun', top_w, left_w)
    cv2.resizeWindow('sun', (int(newiw*sc), int(ih*sc)))
    
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
    cl1 = clahe.apply(frame)
    
    #image leger seuils
    frame1=np.copy(frame)
    Seuil_bas=np.percentile(frame, 25)
    Seuil_haut=np.percentile(frame,99.9999)
    frame1[frame1>Seuil_haut]=Seuil_haut
    #print('seuil bas', Seuil_bas)
    #print('seuil haut', Seuil_haut)
    fc=(frame1-Seuil_bas)* (65000/(Seuil_haut-Seuil_bas))
    fc[fc<0]=0
    frame_contrasted=np.array(fc, dtype='uint16')
    cv2.imshow('sun',frame_contrasted)
    #cv2.waitKey(0)
    
    #image seuils serres 
    frame1=np.copy(frame)
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
    
    #image seuils protus
    frame1=np.copy(frame)
    Seuil_haut=np.percentile(frame1,99.9999)*0.18
    Seuil_bas=0
    #print('seuil bas protu', Seuil_bas)
    #print('seuil haut protu', Seuil_haut)
    frame1[frame1>Seuil_haut]=Seuil_haut
    fc2=(frame1-Seuil_bas)* (65000/(Seuil_haut-Seuil_bas))
    fc2[fc2<0]=0
    frame_contrasted3=np.array(fc2, dtype='uint16')
    if disk_display==True and cercle[0]!=0:
        x0=cercle[0]
        y0=cercle[1]
        wi=cercle[2]
        he=cercle[3]

        r=int(min(wi,he)-3)
        r=r-int(0.003*r)
        #c=(0,0,0)
        frame_contrasted3=cv2.circle(frame_contrasted3, (x0,y0),r,80,-1,lineType=cv2.LINE_AA)
    cv2.imshow('protus',frame_contrasted3)
    #cv2.waitKey(0)
    
    Seuil_bas=np.percentile(cl1, 25)
    Seuil_haut=np.percentile(cl1,99.9999)*1.05
    cc=(cl1-Seuil_bas)*(65000/(Seuil_haut-Seuil_bas))
    cc[cc<0]=0
    cc=np.array(cc, dtype='uint16')
    cv2.imshow('clahe',cc)
    #cv2.waitKey(tempo)  #affiche 15s et continue

    #sauvegarde en png pour appliquer une colormap par autre script
    cv2.imwrite(basefich+'_disk.png',frame_contrasted)
    #sauvegarde en png pour appliquer une colormap par autre script
    cv2.imwrite(basefich+'_diskHC.png',frame_contrasted2)
    #sauvegarde en png pour appliquer une colormap par autre script
    cv2.imwrite(basefich+'_protus.png',frame_contrasted3)
    #sauvegarde en png de clahe
    cv2.imwrite(basefich+'_clahe.png',cc)
    
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

    cv2.waitKey(tempo)
    #sauvegarde le fits
    frame2=np.copy(frame)
    frame2=np.array(cl1, dtype='uint16')
    DiskHDU=fits.PrimaryHDU(frame2,header)
    DiskHDU.writeto(basefich+'_clahe.fits', overwrite='True')

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
    print()

