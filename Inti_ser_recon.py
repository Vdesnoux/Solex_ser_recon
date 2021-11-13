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
from Inti_functions import *
import yaml
#import tkinter as tk


#import time

import PySimpleGUI as sg

SYMBOL_UP =    '▲'
SYMBOL_DOWN =  '▼'


def collapse(layout, key):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this seciton visible / invisible
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key))



def UI_SerBrowse (WorkDir, dec_pix_dop, dec_pix_cont):
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

    
    section1 = [
            [sg.Checkbox('Affiche reconstruction en direct', default=False, key='-DISP-')],
            [sg.Checkbox('Ne sauve pas fichiers fits intermédiaires ', default=True, key='-SFIT-')],
            [sg.Text('Ratio SY/SX (auto:0, fixe: valeur differente de zero) ', size=(45,1)), sg.Input(default_text='0', size=(5,1),key='-RATIO-')],
            [sg.Text('Angle Tilt en degrés (auto:0, fixe: valeur differente de zero) ', size=(45,1)), sg.Input(default_text='0', size=(5,1),key='-TILT-')]
            ]
    
    tab1_layout = [
        [sg.Text('Nom du fichier', size=(15, 1)), sg.InputText(default_text='',size=(65,1),key='-FILE-'),
         sg.FilesBrowse('Open',file_types=(("SER Files", "*.ser"),),initial_folder=WorkDir)],
        #### Section 1 part ####
        [sg.T(SYMBOL_UP, enable_events=True, k='-OPEN SEC1-', text_color='white'), sg.T('Advanced', enable_events=True, text_color='white', k='-OPEN SEC1-TEXT')],
        [collapse(section1, '-SEC1-')],
        [sg.Text('Decalage pixels',size=(15,1)),sg.Input(default_text='0',size=(5,1),key='-DX-',enable_events=True)]
        ]
    
    tab2_layout =[
        [sg.Checkbox('Calcul images doppler et continuum', default=False, key='-DOPCONT-')],
        [sg.Text('Decalage doppler',size=(15,1)),sg.Input(default_text=dec_pix_dop,size=(5,1),key='-DopX-',enable_events=True)],
        [sg.Text('Decalage continuum',size=(15,1)),sg.Input(default_text=dec_pix_cont,size=(5,1),key='-ContX-',enable_events=True)]
        ]
    layout = [
        [sg.TabGroup([[sg.Tab('General', tab1_layout), sg.Tab('Doppler & Continuum', tab2_layout,)]],tab_background_color='#404040')],  
        [sg.Button('Ok', size=(14,1)), sg.Cancel()],
        [sg.Text('Inti V3.1.1 by V.Desnoux et.al. ', size=(30, 1),text_color='Tan', font=("Arial", 8, "italic"))]
        ] 
    
    window = sg.Window('INTI', layout, finalize=True)
    opened1 = False
    window['-SEC1-'].update(visible=opened1)
    
    window['-FILE-'].update(WorkDir) 
    window.BringToFront()
    
    while True:
        event, values = window.read()
        if event==sg.WIN_CLOSED or event=='Cancel': 
            break
        
        if event=='Ok':
            break
        
        if event.startswith('-OPEN SEC1-'):
            opened1 = not opened1
            window['-OPEN SEC1-'].update(SYMBOL_DOWN if opened1 else SYMBOL_UP)
            window['-SEC1-'].update(visible=opened1)

    window.close()
               
    FileNames=values['-FILE-']

    if FileNames==None :
            FileNames=''
    Shift=[]
    Flags={}
    Shift.append(int(values['-DX-']))
    Shift.append(int(values['-DopX-']))
    Shift.append(int(values['-ContX-']))
    Flags["RTDISP"]=values['-DISP-']
    Flags["DOPCONT"]=values['-DOPCONT-']
    Flags["ALLFITS"]=values['-SFIT-']
    #flag_display=values['-DISP-']
    #flag_dopcont=values['-DOPCONT-']
    #flag_dopcont=True
    #flag_display=False
    ratio_fixe=float(values['-RATIO-'])
    #sfit_onlyfinal=values['-SFIT-']
    #sfit_onlyfinal=False
    ang_tilt=values['-TILT-']
    
    return FileNames, Shift, Flags, ratio_fixe,ang_tilt

"""
-------------------------------------------------------------------------------------------
Program starts here !
--------------------------------------------------------------------------------------------
"""

# inti.yaml is a bootstart file to read last directory used by app
# this file is stored in the module directory

#my_ini=os.path.dirname(sys.argv[0])+'/inti.yaml'
my_ini=os.getcwd()+'/inti.yaml'
my_dictini={'directory':'', 'dec doppler':3, 'dec cont':15}
#print('myini de depart:', my_ini)

try:
    #my_ini=os.path.dirname(sys.argv[0])+'/inti.yaml'
    #print('mon repertoire : ', mydir_ini)
    with open(my_ini, "r") as f1:
        my_dictini = yaml.safe_load(f1)
except:
   print('creating inti.yaml as: ', my_ini)

WorkDir=my_dictini['directory']
dec_pix_dop=int(my_dictini['dec doppler'])
dec_pix_cont=int(my_dictini['dec cont'])

# Recupere paramatres de la boite de dialogue
serfiles, Shift, Flags, ratio_fixe,ang_tilt = UI_SerBrowse(WorkDir, dec_pix_dop, dec_pix_cont)
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
        logme('erreur nom de fichier : '+serfile)
        sys.exit()
    
    # met a jour le repertoire et les flags dans le fichier ini, oui a chaque fichier pour avoir le bon rep
    my_dictini['directory']=WorkDir
    my_dictini['dec doppler']=Shift[1]
    my_dictini['dec cont']=Shift[2]
    
    try:
        with open(my_ini, "w") as f1:
            yaml.dump(my_dictini, f1, sort_keys=False)
    except:
        logme ('error saving inti.yaml as : '+my_ini)
        


    # appel au module d'extraction, reconstruction et correction
    #
    # basefich: nom du fichier ser sans extension et sans repertoire
    # dx: decalage en pixel par rapport au centre de la raie 
    
    
    frames, header, cercle=sol.solex_proc(serfile,Shift,Flags,ratio_fixe,ang_tilt)
    

    
    
    #t0=time.time()
    base=os.path.basename(serfile)
    basefich='_'+os.path.splitext(base)[0]
    
    #if Shift != 0 :
        #add shift value in filename to not erase previous file
        #basefich=basefich+'_dp'+str(Shift) # ajout '_' pour avoir fichier en tete dans explorer/finder

    ih=frames[0].shape[0]
    newiw=frames[0].shape[1]

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
    ImgFile=basefich+'_raw.fits'
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
    # image leger seuils
    frame1=np.copy(frames[0])
    Seuil_bas=np.percentile(frame1, 25)
    Seuil_haut=np.percentile(frame1,99.9999)
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
    else:           
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
            frameC=np.copy(frames[3])
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
            cv2.imwrite(basefich+'_cont.png',frame_continuum)
        
        
        top_w=top_w+tw
        left_w=left_w+lw
        cv2.namedWindow('doppler', cv2.WINDOW_NORMAL)
        cv2.moveWindow('doppler', top_w, left_w)
        cv2.resizeWindow('doppler',(int(newiw*sc), int(ih*sc)))
    
        #on se tente une image couleur...
        flag_erreur_doppler=False
        try :
            img_doppler=np.zeros([ih, frames[1].shape[1], 3],dtype='uint16')
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
            print ('erreur image doppler')
            flag_erreur_doppler=True
            cv2.destroyWindow('doppler')
            pass

        #sauvegarde en png de continuum
        if flag_erreur_doppler==False:
            cv2.imwrite(basefich+'_doppler.png',img_doppler)

    
    #sauvegarde en png disk quasi sans seuillage
    cv2.imwrite(basefich+'_raw.png',Disk2)
    #sauvegarde en png disk quasi seuils max
    cv2.imwrite(basefich+'_disk.png',frame_contrasted)
    #sauvegarde en png seuils serrés
    cv2.imwrite(basefich+'_diskHC.png',frame_contrasted2)
    #sauvegarde en png seuils protus
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
    #t1=time.time()
    #print('affichage : ', t1-t0)

    cv2.waitKey(tempo)
    #sauvegarde le fits
    frame2=np.copy(frames[0])
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

