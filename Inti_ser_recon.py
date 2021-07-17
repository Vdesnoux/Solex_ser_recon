# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 16:38:55 2020
Version 20 mai 2021

@author: valerie

Front end de traitements spectro helio de fichier ser
- interface pour selectionner un ou plusieurs fichiers
- appel au module solex_recon qui traite la sequence et genere les fichiers fits
- propose avec openCV un affichage de l'image resultat ou pas
- decalage en longueur d'onde avec Shift
- ajout d'une zone pour entrer un ratio fixe. Si resteà zero alors il sera calculé
automatiquement
- ajout de sauvegarde png _protus avec flag disk_display en dur

Version 16 juillet 2021
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
import Inti_recon as sol
from astropy.io import fits


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
    [sg.Checkbox('Affiche disque noir sur image protuberances', default=True, key='-DISK-')],
    [sg.Checkbox('Sauve uniquement fits _recon et _clahe ', default=True, key='-SFIT-')],
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
    disk_display=values['-DISK-']
    sfit_onlyfinal=values['-SFIT-']
    ang_tilt=values['-TILT-']
    
    return FileNames, Shift, flag_display, ratio_fixe, disk_display, sfit_onlyfinal,ang_tilt

"""
-------------------------------------------------------------------------------------------
le programme commence ici !

si version windows
# recupere les parametres utilisateurs enregistrés lors de la session
# precedente dans un fichier txt "inti.ini" qui va etre placé ici dans le
repertoire du script

si version mac 
#recupere les noms de fichiers par un input console
#valeurs de flag_display, Shift et ratio_fixe sont en dur dans le progra

--------------------------------------------------------------------------------------------
"""

# pour christian
version_mac =False #mettre a true pour etre en version mac

if not(version_mac):
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

else: #version mac
    WorkDir='/Users/macbuil/ocuments/pyser/'
    serfiles=[]
    print('nom du fichier sans extension, ou des fichiers sans extension séparés par une virgule')
    basefichs=input('nom(s): ')
    basefichs=basefichs.split(',')
    for b in basefichs:
        serfiles.append(WorkDir+b.strip()+'.ser')
    # parametres en dur pour version mac
    flag_display=False  # affiche ou pas la recosntruction du disque
    ratio_fixe=0        # pas de ratio_fixe, calcul automatique sera fait
    Shift=0             # valeur du decalage en pixel pour la longueur d'onde
    disk_display=True   # affiche ou pas un disque noir sur image png avec seuils protus

    
#code commun mac ou windows
#************************************************************************************************

#pour gerer la tempo des affichages des images resultats dans cv2.waitKey
#sit plusieurs fichiers à traiter
if len(serfiles)==1:
    tempo=60000 #tempo 60 secondes, pour no tempo mettre tempo=0 et faire enter pour terminer
else:
    tempo=1
    
# boucle sur la liste des fichers
for serfile in serfiles:
    print (serfile)

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
   
    
    ih=frame.shape[0]
    newiw=frame.shape[1]
    
    dm=max(ih,newiw)
    
    
    # gere reduction image png
    if dm>600:
        sc=0.5
        
    # gere reduction image png
    if dm>1500:
        sc=0.4
        
    # gere reduction image png
    if dm>2500:
        sc=0.2
    
    top_w=0
    left_w=0
    tw=250
    lw=32
    
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
    if disk_display==True:
        x0=cercle[0]
        y0=cercle[1]
        wi=cercle[2]-5
        he=cercle[3]-5
        #ang=-int(cercle[3])
        r=int(min(wi,he)-3)
        c=(0,0,0)
        #r=int(cercle[2])-5
        frame_contrasted3=cv2.circle(frame_contrasted3, (x0,y0),r,80,-1,lineType=cv2.LINE_AA)
        #frame_constrasted3=cv2.ellipse(frame_contrasted3, (x0,y0),(wi,he),0,0,360,r,-1,lineType=cv2.LINE_AA )
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
    print (serfile)
    print()

