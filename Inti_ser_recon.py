# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 16:38:55 2020
Version 20 mai 2021

@author: valerie

Front end de traitements spectro helio de fichier ser
- interface pour selectionner un ou plusieurs fichiers
- appel au module inti_recon qui traite la sequence et genere les fichiers fits


-------------------------------------------------------------------------------
version 6.2
- tk error 6.1b
- histogram pour seuil non uniformity pic max * 0.5
- bug fix : ligne blanche dans non unif - mettre à 1 etait erreur car non norm
- creation routine pic_histo(frame) pour eliminer histo des valeurs de fond

Version en cours V6.0b > V6.0c>V6.0d > 6.1 a publier ! 
- ajout correction bad pixel sur ligne du polynome pour chaque trame > en commentaire 
- message log datetime sur fichier SER si pb
- image mix
- ajout colorisation en rouge h-alpha, calcium et jaune
- selection couleur auto sur histogramme des intensités
- ajout param grille on/off dans yaml, a editer dans yaml - pas de GUI
- bouton Fr-En
6.0c
- abaisse seuil calcium histo de 80 à 70
- prend en compte valeur longeur d'onde de database pour "overrider" le mode auto (sécurité)
6.0d
- bug saturation overflow division flat dans recon
- max visu protu *0.6 au lieu de 0.5
- augemente la luminosité images couleurs et leur gamma
- accorde flip images png couleurs
- ajout dans recon des coordonnées y1,y2 et x1,x2 des bords du disque dans log et header
- modif couleur jaune > pale 
- suppression sauvegarde fichier fits BASS2000 si le label wave est a Manual
6.1
- nom fichier color avec la couleur pour ne pas ecraser couleur continuum
- stonyhurst on/off dans les advanced settings
6.1.1
- fix selection Ha2cb 

Version en cours Paris 5.8a>b>c>d> 6.0 publiée
- gestion seuil max sliders pour protus à 50 au lieu de 255
- bug fix sur imgdata apres sliders change pour garder l'image originale
- ajoute generation profil spectral depuis image _mean en .dat dans complements
- offset decalage doppler
- ajout egalisation luminosité des couleurs si doppler est decalé
- ajout bouton pour afficher le profil spectral
- remise de la barre de titre
- plus de barre de titre et grab_anywhere
- ajout d'un bouton pour traiter le dernier fichier du repertoire
- limite image autour du disque pour detection bords apres tilt
- TODO : seuils disks en calcium sont trop contrastés, prefere clahe
- TODO : bandes images helium

version 5.8 du 10 fev 2024 paris
- retour en arriere sur le clamp du profil pour la detection de edge

version 5.7 du 3 fevrier 2024 Antibes
- ajout lignes en haut et bas sur fort tilt plutot qu'une valeur unique dans la zone de padding
- ajout du fichier de config pour variable globale
- ajout variable LowDyn pour scan faible dynamique
- modif clamp zone brillante sur detection edge comme en faible dynamique
- modif ligne zero et derniere pour detection bord disque partiel sans etre en echec sur disque calcium avec diffusé

version 13 janvier 2024
- modif autocrop padding a droite
- test mode seuil inversé
- ajout image seuils inversés _inv

Version 5.6 paris 6 janvier 2024
- bug fix :ajout test os si pas windows pour detection taille ecran
- ajout d'un override avec param screen_scale dans inti.yaml

Version 5.5 paris 28 decembre
- ajout de 3 sous rep BASS2000, Clahe et Complements
- ajout de disk stonyhurst et gestion disk non entier
- calcul angle P, B0 en local
- gestion ecran 4k
- oriente grid si P=0 avec calcul en local
- acquisition 8bits

Version 5.3 paris 6 decembre
- test si deux edges droit et gauche sont trop proches dans le cas d'une protuberances

Version 5.2 paris 6 decembre
- fit polynomiale pour edge - soleil partiel
- refinement zone haute et basse pour image calcium

Version 5.1 paris 12 nov
- ajout mode auto ZEE_AUTOPOLY dans POl (magnetogramme)
- gestion background améiorée pour image a fort diffusé (calcium)

Version V4.1.8 paris 21 juillet 23 > V5.0
- meilleure gestion background pour padding
- ajout poly auto et decalage en mode free auto et manuel
- gestion mode degradé scan statique
- sauve _check de la trame
- decalage en decimal

version V4.1.7 antibes 15 juillet 2023
- gestion overflow doppler avec passage en float
- creer un mode sauve polynome
- stocke valeur de zeeman_shift
- menage fichier _dp2_raw, manual, jpg
- ajouter la diff r-b dans zeeman et faire r-b aussi dans mode free
- ajoute reduction bruit en mode general et free

Version V4.1.4 antibes du 14 juillet 2023
- mode frame redressée avec suppression du calcul raie
- ajout luminance moyenne
- accepte ang_tilt à zero et gere sur flag_force 
- ajout calcul intensité sur zone centrale image
- sauve forcage tilt et ratio pour modes magn et free
- reactive shift_zeeman

version V4.1.2 paris du 7 juillet 2023
- ajout cas difficiles
- inversion doppler
- gestion serveur meudon ne repond pas
- ajout calcul ROI intensite pour mode free
- ROI devient Intensity et valeur en int

version V4.1.1 du 3 juillet 2023
- suppression decalage zeeman
- remplace _moy par _sum
- BUGFIX : close popup_get_file si pas de fichier choisi
- BUGFIX : sauvegarde b-1.png sauvait raie centrale dans zeeman mais fits ok

version V4.1.0 du 2 juillet 2023
- remplace circularisation limbes en mode forcé par la circu mode auto avec ajustement des coor cercle et cercle0
- ajout force tilt dans zeeman
- ajout filtre sur _mean.fits dans trame

version 4.0.9 paris 1 juillet 2023
- gestion autocrop dans ini.yaml
- ajout gestion trame dans zeeman
- remplace position par decalage dans free

Version 4.0.8 paris juin 2023
- angle tilt RA
- autocrop

version 4.0.7 11-17 juin - Paris
- prends en compte le facteur de rescaling pour orienter axe RA
- BUGFIX : calculette Ang/Pix

version 4.0.6 du 3 mai - Antibes
- ajout calculette pour disp par longueur d'onde

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
import config as cfg
try :
    from serfilesreader.serfilesreader import Serfile
except ImportError : 
    from serfilesreader import Serfile
import stonyhurst as sth

import PySimpleGUI as sg
try :
    import ctypes
except:
    pass

import matplotlib
import matplotlib.pyplot as plt
import time


SYMBOL_UP =    '▲'
SYMBOL_DOWN =  '▼'
short_version = 'Inti V6.2'
current_version = short_version + ' by V.Desnoux et.al. '

def Colorise_Image (couleur, frame_contrasted, basefich, suff):
    
 
    
    # gestion couleur auto ou sur dropdown database compatibility
    # 'Manual','Ha','Ha2cb','Cah','Cah1v','Cak','Cak1v','HeID3'
    couleur_lbl=couleur
    if couleur_lbl == 'Manual' :
        couleur = 'on' # mode detection auto basé sur histogramme simple
    else :
        if couleur_lbl[:2] == 'Ha' :
            couleur='H-alpha'
        if couleur_lbl[:3] == 'Ha2' :
            couleur='Pale'
        if couleur_lbl[:2] == 'Ca' :
            couleur='Calcium'
        if couleur_lbl[:2] == 'He' :
            couleur='Pale'
    
    f=frame_contrasted/256
    f_8=f.astype('uint8')
    
    #hist = cv2.calcHist([f_8],[0],None,[256],[10,256])
    # separe les 2 pics fond et soleil
    th_otsu,img_binarized=cv2.threshold(f_8, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    hist = cv2.calcHist([f_8],[0],None,[256],[0,256])
    hist[0:int(th_otsu)]=0
    pos_max=np.argmax(hist)
    """
    plt.plot(hist)
    plt.show()
    print('couleur : ',pos_max)
    """
    
    # test ombres >> provoque des applats 
    ombres=False
    if ombres :
        
        i_low=[]
        i_hi=[]
        fr=np.copy(frame_contrasted)
        i_low=np.array((fr<(pos_max*256))*fr*1.01, dtype='uint16')
        i_hi=(fr>=pos_max)*fr
        fr=i_low+i_hi
        f=fr/256
        f_8=f.astype('uint8')
    
    
    if couleur =='on' :  
        if pos_max<200 and pos_max>=70 :
            couleur="H-alpha"
        if pos_max<70 :
            couleur="Calcium"
        if pos_max>=200 :
            couleur="Pale"

    
    # test ombres >> provoque des applats 
    ombres=False
    if ombres :
        f8_low=[]
        f8_hi=[]
        f8_low=np.array((f_8<pos_max)*f_8*1.05, dtype='uint8')
        f8_hi=(f_8>=pos_max)*f_8
        f_8=f8_low+f8_hi
    
    
    #couleur="H-alpha"
    
    if couleur != '' :
        # image couleur en h-alpha
        if couleur == 'H-alpha' :
            # build a lookup table mapping the pixel values [0, 255] to
            # their adjusted gamma values
            gamma=0.3   # was gam 1.3 > 0.3 ok un peu plus clair et 0.1 plus sombre sombre
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            f1_gam= cv2.LUT(f_8, table)
            
            gamma=0.55 # was gam 0.5 - 0.3 trop rouge, 0.6 un peu jaune - 0.55 ok
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            f2_gam= cv2.LUT(f_8, table)
            
            gamma=1 # gam is 1.0
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            f3_gam= cv2.LUT(f_8, table)
            
            i1=(f1_gam*0.1).astype('uint8')     # was 0.05 - 1 trop pale - 0.1 ok
            i2=(f2_gam*1).astype('uint8')       # is 1
            i3=(f3_gam*1).astype('uint8')       # is 1
            
            gamma=1.5 # gam total image 2 est trop fade, 1.2 pas assez, 1.5 pas mal
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            i1= cv2.LUT(i1, table)
            i2= cv2.LUT(i2, table)
            i3= cv2.LUT(i3, table)
            
            img_color=np.zeros([frame_contrasted.shape[0], frame_contrasted.shape[1], 3],dtype='uint8')
            img_color[:,:,0] = np.array(i1, dtype='uint8') # blue
            img_color[:,:,1] = np.array(i2, dtype='uint8') # blue
            img_color[:,:,2] = np.array(i3, dtype='uint8') # blue
            
            # gestion gain alpha et luminosité beta
            #alpha=(255//2+10)/pos_max
            #print('alpha ', alpha)
            #img_color=cv2.convertScaleAbs(img_color, alpha=alpha, beta=0) # was 1.3 - 1.1 plus sombre - 1.2 ok
            
            # affiche dans clahe window for test
            #cv2.imshow('clahe',img_color)
            #cv2.setWindowTitle("clahe", "color")

            
        # image couleur en calcium
        if couleur == 'Calcium' :
            # build a lookup table mapping the pixel values [0, 255] to
            # their adjusted gamma values
            gamma=1.2  # was 1
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            f1_gam= cv2.LUT(f_8, table)
            
            gamma=1 # was 0.8
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            f2_gam= cv2.LUT(f_8, table)
            
            gamma=1 # was 0.8
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            f3_gam= cv2.LUT(f_8, table)
            
            # i1: bleu, i2: vert, i3:rouge
            i1=(f1_gam*1).astype('uint8')     # was 0.05 - 1 trop pale - 0.1 ok
            i2=(f2_gam*0.7).astype('uint8')       # is 1
            i3=(f3_gam*0.7).astype('uint8')       # was 0.8 un peu trop violet
            
            gamma=1 # gam total image finalement aucun, 1.2 un peu fade
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            i1= cv2.LUT(i1, table)
            i2= cv2.LUT(i2, table)
            i3= cv2.LUT(i3, table)
            
            img_color=np.zeros([frame_contrasted.shape[0], frame_contrasted.shape[1], 3],dtype='uint8')
            img_color[:,:,0] = np.array(i1, dtype='uint8') # blue
            img_color[:,:,1] = np.array(i2, dtype='uint8') # green
            img_color[:,:,2] = np.array(i3, dtype='uint8') # red
            
            vp=np.percentile(f_8, 99.7)
            alpha=(255//2)/(vp*0.5)
            #print('alpha ', alpha)
            
            img_color=cv2.convertScaleAbs(img_color, alpha=alpha) # was 1.5 ok
            
            # affiche dans clahe window for test
            #cv2.imshow('clahe',img_color)
            #cv2.setWindowTitle("clahe", "color")
        
        # image couleur en jaune-orange (helium, sodium, continuum)
        if couleur == 'Pale' :
            # build a lookup table mapping the pixel values [0, 255] to
            # their adjusted gamma values
            gamma=1  # 
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            f1_gam= cv2.LUT(f_8, table)
            
            gamma=1 # was 0.7
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            f2_gam= cv2.LUT(f_8, table)
            
            gamma=1 # 
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            f3_gam= cv2.LUT(f_8, table)
            
            # i1: bleu, i2: vert, i3:rouge
            i1=(f1_gam*0.92).astype('uint8')     # was 0.5 
            i2=(f2_gam*0.98).astype('uint8')       # was 0.9
            i3=(f3_gam*1).astype('uint8')       # is 1
            
            gamma=0.5 # gam total image 1 trop fade, 0.7 pas mal
            invGamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
                # apply gamma correction using the lookup table
            i1= cv2.LUT(i1, table)
            i2= cv2.LUT(i2, table)
            i3= cv2.LUT(i3, table)
            
                
            img_color=np.zeros([frame_contrasted.shape[0], frame_contrasted.shape[1], 3],dtype='uint8')
            img_color[:,:,0] = np.array(i1, dtype='uint8') # blue
            img_color[:,:,1] = np.array(i2, dtype='uint8') # green
            img_color[:,:,2] = np.array(i3, dtype='uint8') # red
            
            #alpha=(255//2+50)/pos_max
            #alpha=1
            #print('alpha ', alpha)
            #img_color=cv2.convertScaleAbs(img_color, alpha=alpha) # was 1
            
            # affiche dans clahe window for test
            #cv2.imshow('clahe',img_color)
            #cv2.setWindowTitle("clahe", "color")
        
        #img_color=cv2.flip(img_color,0)
        
        #cv2.imshow('clahe',img_color)
        #cv2.setWindowTitle("clahe", "color")
            
        cv2.imwrite(basefich+suff+'_color_'+str(couleur)+'.png',img_color)
        
        if cfg.LG == 1:
            logme("Couleur : "+ str(couleur))
        else:
            logme("Color : "+ str(couleur))
        
        return img_color

def seuil_image (img):
    Seuil_haut=np.percentile(img,99.999)
    Seuil_bas=(Seuil_haut*0.25)
    img[img>Seuil_haut]=Seuil_haut
    img_seuil=(img-Seuil_bas)* (65535/(Seuil_haut-Seuil_bas)) # was 65500
    img_seuil[img_seuil<0]=0
    
    return img_seuil, Seuil_haut, Seuil_bas

def seuil_image_force (img, Seuil_haut, Seuil_bas):
    img[img>Seuil_haut]=Seuil_haut
    img_seuil=(img-Seuil_bas)* (65535/(Seuil_haut-Seuil_bas)) # was 65500
    img_seuil[img_seuil<0]=0
    
    return img_seuil

def get_lum_moyenne(img) :
    # ajout calcul intensité moyenne sur ROI centrée
    ih, iw =img.shape
    dim_roi = 100
    rox1 = iw//2 - dim_roi
    rox2 = iw//2 + dim_roi
    roy1 = ih//2 - dim_roi
    roy2 = ih//2 + dim_roi
    #print('roi ', rox1,rox2,roy1,roy2)
    try :
        lum_roi=np.mean(img[roy1:roy2,rox1:rox2])
    except:
        lum_roi=0
    return lum_roi

def on_change_slider(x):
    # x est la valeur du curseur
    global source_window
    global img_data
        
    #print(params[0])
    sb = cv2.getTrackbarPos('Seuil bas', 'sliders')
    sh = cv2.getTrackbarPos('Seuil haut', 'sliders')
    if sh>255:
        sh=255
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
    #param=np.copy(cc)
    param2=np.copy(img_data)
    paramh=s_haut
    paramb=s_bas
    cv2.setMouseCallback(source_window,mouse_event_callback, [source_window, cc,param2,paramh,paramb])
    cc=cv2.flip(cc,0)
   
    cv2.imshow(source_window,cc)


def mouse_event_callback( event,x,y,flags,params):
    global source_window
    global img_data
    try :
        if event==cv2.EVENT_LBUTTONDOWN or event==cv2.EVENT_LBUTTONUP:
            source_window=params[0]
            img_data=np.copy(params[2])
            #print('mouse: ',params[0])
    
            sh=int(params[3]/65535*255)
            sb=int(params[4]/65635*255)
            cv2.setTrackbarPos('Seuil bas','sliders',sb)
            cv2.setTrackbarPos('Seuil haut','sliders',sh)
            if source_window == 'protus' :

                cv2.setTrackbarMax('Seuil haut', 'sliders', 100) #was 50
                cv2.setTrackbarMax('Seuil bas', 'sliders', 100) #was 50
            else :
                cv2.setTrackbarMax('Seuil haut', 'sliders', 255)
                cv2.setTrackbarMax('Seuil bas', 'sliders', 255) 
                
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
        print('pb sliders')
        pass

def mouse_event2_callback( event,x,y,flags,param):
    global mouse_x, mouse_y
    if event==cv2.EVENT_LBUTTONDOWN:
        try:
            font = cv2.FONT_HERSHEY_PLAIN
            font_scale=1
            font_thickness=1
            mouse_x, mouse_y=x,y
            text_size, _ = cv2.getTextSize(str(x)+';'+str(y)+'  '+str(param[y,x]), font, font_scale, font_thickness)
            text_w, text_h = text_size
            cv2.rectangle(param, (10,30), (text_w+10,text_h), 0, cv2.FILLED)
            cv2.putText(param, str(x)+';'+str(y)+'  '+str(param[y,x]), (10, 30), font, font_scale, 65000, font_thickness, cv2.LINE_AA)
            cv2.imshow('mean', param)
        except:
            pass

def get_sun_meudon (date_jd1):
    # obsolete
    date_jd2=date_jd1+1
    r1="http://voparis-tap-helio.obspm.fr/__system__/tap/run/sync?LANG=ADQL&format=txt&"
    r2="request=doQuery&query=select%20access_url%20from%20bass2000.epn_core%20where%20time_min%20between%20"
    r3=str(date_jd1)+"%20and%20"+str(date_jd2)+"%20and%20access_format=%27image/jpeg%27%20"
    r4="and%20filter=%27H%20Alpha%27"
    Vo_req=r1+r2+r3+r4

    reponse_web=rq.get(Vo_req)
    sun_meudon=reponse_web.text.split("\n")[0]
    
    return sun_meudon

def display_mean_img2 ():
    # Lecture et affiche image disque brut
    ImgFile = sg.popup_get_file("Select file", file_types=(('Mean Files', '*mean.fits'), ('ALL Files', '*.*'),))

    if ImgFile != None :
        try :
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
        except :
            pass
        
def display_mean_img (poly):
    # version image redressee
    # Lecture et affiche image disque brut
    ImgFile = sg.popup_get_file("Select file", file_types=(('Mean Files', '*mean.fits'), ('ALL Files', '*.*'),))

    if ImgFile != None :
        try :
            hdulist = fits.open(ImgFile, memmap=False)
            hdu=hdulist[0]
            myspectrum=hdu.data
            mih=hdu.header['NAXIS2']
            miw=hdu.header['NAXIS1']
            mean_trame=np.reshape(myspectrum, (mih,miw))
            hdulist.close()
                        
            # redresse raies pour faciliter la prise de position de la raie
            try :
                image_mean_redresse = translate_img(mean_trame, poly)
            except :
                image_mean_redresse = np.copy(mean_trame)
            
            if miw<178:
                # window title bar CV2 force image minimal size at 178, so pad to avoid autorescale

                mean_trame_pad=np.array(np.zeros((mih, 178)), dtype="uint16")
                mean_trame_pad[:mih, :miw]=image_mean_redresse
                #mean2_trame_pad=np.array(np.zeros((mih, 178)), dtype="uint16")
                #mean2_trame_pad[:mih, :miw]=np.copy(mean_trame)
            else:
                mean_trame_pad=np.array(mean_trame,dtype='uint16')
                #mean2_trame_pad=np.array(mean_trame,dtype='uint16')
            
            #sauvegarde du fits en _check
            WorkDir=os.path.dirname(ImgFile)+"/"
            base=os.path.basename(ImgFile)
            basefich=os.path.splitext(base)[0].split('_mean')[0]
            DiskHDU=fits.PrimaryHDU(mean_trame_pad,hdu.header)
            DiskHDU.writeto(WorkDir+basefich+'_check.fits', overwrite='True')
            
            print(WorkDir+basefich+'_check.fits')
            #fenetre pour image mean de trame 
            sc=1
            cv2.namedWindow('mean')
            cv2.moveWindow('mean', 100, 0)
            cv2.resizeWindow('mean', (int(miw*sc), int(mih*sc)))

        
            cv2.imshow('mean',mean_trame_pad)
            cv2.setMouseCallback('mean',mouse_event2_callback, mean_trame_pad)

            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except :
            pass
    
def UI_calculette(size_pix_cam, bin_cam):
    sg.theme('Dark2')
    sg.theme_button_color(('white', '#500000'))
    resultat=0
    disp=0
    wav_name=''
    wav_dict={'Ha':6562.762,'Ca':3968.469,'He':5877.3}
    if cfg.LG==1 : # en français
        layout=[
            [sg.Radio('Ha', 'wav',key="-HA-", default=True), sg.Radio('Ca', 'wav',key='-CA-'), sg.Radio('He', 'wav', key='-HE-')],
            [sg.Text("Valeur en angströms : ", size=(20,1)), sg.Input(default_text='1', size=(7,1), key='-ang-', background_color='light yellow')],
            [sg.Text("Taille pixel caméra en mm : ", size=(20,1)), sg.Input(default_text=str(size_pix_cam), size=(7,1), key='-size-')],
            [sg.Text("Facteur de Binning : ", size=(20,1)), sg.Input(default_text=str(bin_cam), size=(7,1), key='-bin-')],
            [sg.Text(str(resultat)+ " en pixels", size=(28,1), key='-RESULT-', background_color='dark green')],
            [sg.Text('Dispersion en Ang/Pix : '),sg.Text(str(disp), key='-DISP-')],
            [sg.Button("Calcul ", key='-VALID-'),sg.Text('     '),sg.Button('Fermer', key='-Exit-')]
            ]
    else: # en anglais
        layout=[
            [sg.Radio('Ha', 'wav',key="-HA-", default=True), sg.Radio('Ca', 'wav',key='-CA-'), sg.Radio('He', 'wav', key='-HE-')],
            [sg.Text("Value in angströms : ", size=(20,1)), sg.Input(default_text='1', size=(8,1),key='-ang-',background_color='light yellow')],
    
            [sg.Text("Camera pixel size in mm : ", size=(20,1)), sg.Input(default_text=str(size_pix_cam), size=(8,1), key='-size-')],
            [sg.Text("Binning factor : ", size=(20,1)), sg.Input(default_text=str(bin_cam), size=(8,1),key='-bin-')],
            [sg.Text(str(resultat) + " in pixels", size=(28,1), key='-RESULT-', background_color='dark green')],
            [sg.Text('Dispersion in Ang/Pix : '),sg.Text(str(disp),key='-DISP-')],
            [sg.Button("Compute ", key='-VALID-'),sg.Text('     '),sg.Button('Exit', key='-Exit-')]
            ]
    a,b=win_pos
    win2_pos=(a+250, b+150)
    window2 = sg.Window('Sol\'Ex calculette', layout, location=win2_pos,finalize=True)
    window2.BringToFront()
    
    while True:
        event, values = window2.read()
        #print(event, values)
        if event == sg.WIN_CLOSED or event == '-Exit-': 
            break          
        if event == '-VALID-' : 
            if values['-HA-'] == True :
                wav_name = 'Ha'
            if values['-CA-'] == True:
                wav_name = 'Ca'
            if values['-HE-'] == True:
                wav_name = 'He'
            wave=wav_dict[wav_name]*1e-7
            alpha=np.degrees(np.arcsin((2400*wave)/(2*np.cos(np.radians(17)))))+17
            beta=alpha-34
            size_pix_cam=float(values['-size-'])
            bin_cam=float(values['-bin-'])
            val_toconvert=float(values['-ang-'])
            disp = 1e7 * size_pix_cam* np.cos(np.radians(beta)) / 2400 / 125
            val_ang_onepix= disp * bin_cam
            #print(val_ang_onepix)
            resultat=round(val_toconvert / val_ang_onepix)
            window2['-RESULT-'].update(str(resultat)+'  pixels')
            window2['-DISP-'].update("{:.3f}".format(disp))
            
            
    window2.close()
    return resultat, size_pix_cam, bin_cam

def collapse(layout, key):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param layout: The layout for the section
    :param key: Key used to make this seciton visible / invisible
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return sg.pin(sg.Column(layout, key=key))

def UI_graph():
    if sys.platform=="win32" :
        sg.set_options(dpi_awareness=True, scaling=screen_scale)
    else:
        sg.set_options(scaling=screen_scale)
    
    if cfg.LG == 1 :
        color_list=['Jaune', 'Noir']
        c=color_list[0]
        g=True
        layout=[
            [sg.Text('')],
            [sg.Text('Couleur grille : '), sg.Combo(color_list,default_value=color_list[0], key='-GRID_COLOR-', enable_events=True)],
            [sg.Text('')],
            [sg.Checkbox('Graduations On', default=True,key='-GRADU_ON-',enable_events=True)],
            [sg.Text('')],
            [sg.Button('Ok',size=(20,1))]
            ]
        Title='Grille'
    else :
        color_list=['yellow', 'Black']
        c=color_list[0]
        g=True
        layout=[
            [sg.Text('')],
            [sg.Text('Grid Color : '), sg.Combo(color_list,default_value=color_list[0], key='-GRID_COLOR-', enable_events=True)],
            [sg.Text('')],
            [sg.Checkbox('Graduations On', default=True,key='-GRADU_ON-',enable_events=True)],
            [sg.Text('')],
            [sg.Button('Ok', size=(20,1))]
            ]
        Title='Grid'
    a,b=win_pos
    win3_pos=(a+400, b+300)
    window3 = sg.Window(Title, layout, location=win3_pos,finalize=True)

    while True:
        event, values = window3.read()

        if event==sg.WIN_CLOSED or event=='Ok': 
            break
        else :
            g=values['-GRADU_ON-']
            c=values['-GRID_COLOR-']

    window3.close()
    
    return c, g

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
# Interface INTI
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

def UI_SerBrowse (WorkDir,saved_tilt, saved_ratio, dec_pix_dop, dec_pix_cont, poly, pos_free_blue, 
                  pos_free_red,free_shift, zee_shift, win_pos, previous_serfile, data_entete,saved_angP,Flags, size_pix_cam, bin_cam, screen_scale):

    if sys.platform=="win32" :
        sg.set_options(dpi_awareness=True, scaling=screen_scale)
    else:
        sg.set_options(scaling=screen_scale)
    
    #sg.set_options(font="Arial, 10")
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
    list_wave=[['Manual','Ha','Ha2cb','Cah','Cah1v','Cak','Cak1v','HeID3'],[0,6562.762,6561.432,3968.469,3966.968,3933.663,3932.163,5877.3]]
    
    if cfg.LG == 1 :
        LG_str='FR'
    else :
        LG_str='EN'

    if cfg.LG == 1 :
        colonne0=[
            [sg.Checkbox(' Inversion E-W', default=Flags['FLIPRA'], key='-RA_FLIP-')],
            [sg.Checkbox(' Inversion N-S', default=Flags['FLIPNS'], key='-NS_FLIP-')]
            ]
        colonne1=[[sg.Button('Grille', key='Graph')]]
    else :
        colonne0=[
            [sg.Checkbox(' E-W flip', default=Flags['FLIPRA'], key='-RA_FLIP-')],
            [sg.Checkbox(' N-S flip', default=Flags['FLIPNS'], key='-NS_FLIP-')]
            ]
        colonne1=[[sg.Button('Grid', key='Graph')]]
        
    if cfg.LG == 1:
        section1 = [
                [sg.Checkbox(' Affichage de la reconstruction en temps réel ', default=False, key='-DISP-')],
                #[sg.Checkbox(' Non sauvegarde des fichiers FITS intermédiaires', default=True, key='-SFIT-')],
                [sg.Checkbox('Réduction de bruit (modes general, magnétogramme, libre)', default=Flags['NOISEREDUC'], key='-NOISEREDUC-')],
                [sg.Checkbox(' Sauve  paramètres polynome pour magnétogramme et libre ', default=Flags['SAVEPOLY'], key='-SAVEPOLY-')],
                [sg.Checkbox(' Autocrop', default=Flags['Autocrop'], key='-AUTOCROP-')],
                [sg.Checkbox(' Stonyhurst', default=Flags['Grid'], key='-GRID-', enable_events=True)],
                [sg.Checkbox(' Force les valeurs tilt et facteur d\'échelle', default=False, key='-F_ANG_SXSY-')],
                [sg.Text('Angle Tilt en degrés :', size=(15,1)), sg.Input(default_text=saved_tilt, size=(6,1),key='-TILT-')],
                [sg.Text('Ratio SY/SX :', size=(15,1)), sg.Input(default_text=saved_ratio, size=(6,1),key='-RATIO-')]
                
                ]
    else:
        section1 = [
                [sg.Checkbox(' Real time reconstruction display ', default=False, key='-DISP-')],
                #[sg.Checkbox(' No intermediate files FITS saving', default=True, key='-SFIT-')],
                [sg.Checkbox('Noise reduction (general and free modes)', default=Flags['NOISEREDUC'], key='-NOISEREDUC-')],
                [sg.Checkbox(' Save polynome parameters for magnetogram and free ', default=Flags['SAVEPOLY'], key='-SAVEPOLY-')],
                [sg.Checkbox(' Autocrop', default=Flags['Autocrop'], key='-AUTOCROP-')],
                [sg.Checkbox(' Stonyhurst', default=Flags['Grid'], key='-GRID-', enable_events=True)],
                [sg.Checkbox(' Force values of tilt and scale ratio', default=False, key='-F_ANG_SXSY-')],
                [sg.Text('Tilt angle in degrees :', size=(15,1)), sg.Input(default_text=saved_tilt, size=(6,1),key='-TILT-')],
                [sg.Text('SY/SX ratio :', size=(15,1)), sg.Input(default_text=saved_ratio, size=(6,1),key='-RATIO-')]
                
                ]
        
    
    if cfg.LG == 1:
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
                     sg.Button('Date', key='-GETDATE-'),sg.Button('Gong', key='-CLIMSO-'),
                     sg.Text('BASS2000', key='-BASS-', enable_events=True, font="None 9 italic underline"), 
                     sg.Text('NSO', key='-NSO-',enable_events=True, font="None 9 italic underline")],
                [sg.Text('Angle P :', size=(12,1)), sg.Input(default_text=saved_angP, size=(10,1),key='-ANGP-'), 
                 sg.Text("Nord en haut, Est à gauche, angle P positif vers l\'Est"), sg.Button('KSO',key='-KSO-')],
                [sg.Column(colonne0, size=(400,100)),sg.Column(colonne1, vertical_alignment='Top') ]
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
                     sg.Button('Date', key='-GETDATE-'),sg.Button('Gong', key='-CLIMSO-'),
                     sg.Text('BASS2000', key='-BASS-', enable_events=True, font="None 9 italic underline"), 
                     sg.Text('NSO', key='-NSO-',enable_events=True, font="None 9 italic underline")],
                [sg.Text('P Angle :', size=(12,1)), sg.Input(default_text=saved_angP, size=(10,1),key='-ANGP-'), 
                 sg.Text("North up, Est left, P angle positive towards Est"), sg.Button('KSO',key='-KSO-')],
                [sg.Column(colonne0, size=(400,100)),sg.Column(colonne1, vertical_alignment='Top') ]               
                ]
      
    if cfg.LG == 1:
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
            [sg.Text('Décalage en pixels :',size=(15,1)),sg.Input(default_text='0',size=(4,1),key='-DX-',enable_events=True), sg.Button('Calc')]
            ]
        
        tab2_layout =[
            [sg.Text("")],
            [sg.Text('Amplitude doppler :',size=(16,1)),sg.Input(default_text=dec_pix_dop,size=(4,1),key='-DopX-',enable_events=True)],
            [sg.Text('Décalage doppler :', size=(16,1)), sg.Input(default_text=0, size=(4,1), key='-SHIFTDOP-', enable_events=True),
             sg.Text('    '), sg.Button('Profil', key='-PROFIL-')],
            [sg.Checkbox(' Inversion B - R ', default=Flags['DOPFLIP'], key='-DOP_FLIP-')],
            [sg.Text('Décalage continuum :',size=(16,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='-ContX-',enable_events=True)]
            ]
        
        tab3_layout =[
            [sg.Text("")],
            [sg.Text('Plage en pixels :',size=(12,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='Volume',enable_events=True), sg.Text('+/- pixels')],
            [sg.Checkbox(' Création FITS 3D', default=False, key='-FITS3D-')],
            ]
       
        tab4_layout =[
            # zeeman
            [sg.Text("")],
            [sg.Checkbox('Polynome automatique', default=Flags["ZEE_AUTOPOLY"], key='-ZEE_AUTOPOLY-')],
            [sg.Text('Coefficient polynome forme fente : ',size=(24,1)),sg.Input(default_text="{:.4e}".format(poly[0]),size=(12,1),key='a'), sg.Text('* x**2 +'),
             sg.Input(default_text="{:.4e}".format(poly[1]),size=(12,1),key='b'), sg.Text('* x')],
            [sg.Text('Constante :'),sg.Input(default_text="{:.2f}".format(poly[2]),size=(6,1),key='c'),
             sg.Text('- Ecart Zeeman :',size=(12,1)),sg.Input(default_text=2,size=(2,1),key='Zeeman_wide',enable_events=True), sg.Text('+/- pixels'),
             sg.Text('- Décalage :'), sg.Input(default_text=zee_shift,size=(5,1),key='Zeeman_shift',enable_events=True)],
            [sg.Button("Trame")],
            #[sg.Button("trame"),sg.Text('Position raie :'),sg.Input(default_text=0,size=(5,1),background_color='gray',key='xmin'),sg.Text('à hauteur y:'),
            #sg.Input(default_text=0,size=(5,1),background_color='gray',key='y_xmin'), sg.Button("Calcul",key="Calcul")],
            [sg.Text('Nom fichier racine aile bleue :'), sg.Input(default_text="b-", size=(12,1), key='racine_bleu')],
            [sg.Text('Nom fichier racine aile rouge :'), sg.Input(default_text="r-", size=(12,1), key='racine_rouge')],
            [sg.Checkbox(' Force les valeurs tilt et facteur d\'échelle', default=Flags["FORCE_FREE_MAGN"], key='-F_ANG_SXSY3-')],
            [sg.Text('Angle Tilt en degrés :', size=(15,1)), sg.Input(default_text=saved_tilt, size=(6,1),key='-TILT3-'),
             sg.Text('Ratio SY/SX :', size=(10,1)), sg.Input(default_text=saved_ratio, size=(6,1),key='-RATIO3-')]
            ]
        tab5_layout =[
            #Free line
            [sg.Text("")],
            [sg.Checkbox('Polynome automatique', default=Flags["FREE_AUTOPOLY"], key='-FREE_AUTOPOLY-')],
            [sg.Text('Coefficient polynome forme fente : ',size=(24,1)),sg.Input(default_text="{:.4e}".format(poly[0]),size=(12,1),key='fa'), sg.Text(' * x**2 + '),
             sg.Input(default_text="{:.4e}".format(poly[1]),size=(12,1),key='fb'), sg.Text('* x')],
            [sg.Text('Constante :'),sg.Input(default_text="{:.2f}".format(poly[2]),size=(6,1),key='fc'), sg.Text('Decalage de base:'),sg.Input(default_text=free_shift,size=(5,1),key='-FREE_SHIFT-')],
            [sg.Button("Trame")],
            #[sg.Button("trame"),sg.Text('Position raie :', visible=False),sg.Input(default_text=0,size=(5,1),background_color='gray',key='xminf', visible=False),
            #sg.Text('à hauteur y:', visible=False),
            #sg.Input(default_text=0,size=(5,1),background_color='gray',key='y_xminf', visible=False), sg.Button("Calcul",key="Calculf", visible=False)],
            [sg.Text('Décalage 1 :'),sg.Input(default_text=pos_free_blue,size=(5,1),key='wb'),sg.Text('Décalage 2 :'),sg.Input(default_text=pos_free_red,size=(5,1),key='wr')],
            [sg.Checkbox(' Force les valeurs tilt et facteur d\'echelle', default=Flags["FORCE_FREE_MAGN"], key='-F_ANG_SXSY2-')],
            [sg.Text('Angle Tilt en degrés :', size=(15,1)), sg.Input(default_text=saved_tilt, size=(6,1),key='-TILT2-'),
             sg.Text('Ratio SY/SX :', size=(10,1)), sg.Input(default_text=saved_ratio, size=(6,1),key='-RATIO2-')]
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
            [sg.Text('Shift in pixels :',size=(11,1)),sg.Input(default_text='0',size=(4,1),key='-DX-',enable_events=True), sg.Button('Calc')]
            ]
        
        tab2_layout =[
            #[sg.Checkbox(' Compute Doppler and Continuum images ', default=False, key='-DOPCONT-')],
            [sg.Text("")],
            [sg.Text('Doppler amplitude :',size=(16,1)),sg.Input(default_text=dec_pix_dop,size=(4,1),key='-DopX-',enable_events=True)],
            [sg.Text('Doppler shift :', size=(16,1)), sg.Input(default_text=0, size=(4,1), key='-SHIFTDOP-', enable_events=True), 
             sg.Text('     '), sg.Button('Profile', key='-PROFIL-',)],
            [sg.Checkbox('B - R flip ', default=Flags['DOPFLIP'], key='-DOP_FLIP-')],
            [sg.Text('Continuum shift :',size=(16,1)),sg.Input(default_text=dec_pix_cont,size=(4,1),key='-ContX-',enable_events=True)]
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
            [sg.Checkbox('Automatic polynome', default=Flags["FREE_AUTOPOLY"], key='-FREE_AUTOPOLY-')],
            [sg.Text('Polynom terms of slit distorsion : ',size=(24,1)),sg.Input(default_text="{:.4e}".format(poly[0]),size=(12,1),key='a'), sg.Text('* x**2 + '),
             sg.Input(default_text="{:.4e}".format(poly[1]),size=(12,1),key='b'), sg.Text('* x')],
            [sg.Text('Constante :'),sg.Input(default_text="{:.2f}".format(poly[2]),size=(6,1),key='c'),
             sg.Text('-  Shift zeeman :',size=(12,1)),sg.Input(default_text=2,size=(2,1),key='Zeeman_wide',enable_events=True), sg.Text('+/- pixels'),
             sg.Text('-  Shift :'), sg.Input(default_text=zee_shift,size=(5,1),key='Zeeman_shift',enable_events=True)],
            [sg.Button("Trame")],
            #[sg.Button("frame"),sg.Text('Line position :'),sg.Input(default_text=0,size=(5,1),background_color='gray',key='xmin'),sg.Text('at height y:'),
            #sg.Input(default_text=0,size=(5,1),background_color='gray',key='y_xmin'), sg.Button("Calcul",key="Calcul")],
            [sg.Text('Bleu line wing generic file name :'), sg.Input(default_text="b-", size=(12,1), key='racine_bleu')],
            [sg.Text('Red line wing generic file name  :'), sg.Input(default_text="r-", size=(12,1), key='racine_rouge')],
            [sg.Checkbox(' Force values of tilt and scale ratio', default=Flags["FORCE_FREE_MAGN"], key='-F_ANG_SXSY3-')],
            [sg.Text('Tilt angle in degrees :', size=(15,1)), sg.Input(default_text=saved_tilt, size=(6,1),key='-TILT3-'),
             sg.Text('SY/SX ratio :', size=(10,1)), sg.Input(default_text=saved_ratio, size=(6,1),key='-RATIO3-')]
            ]
        
        tab5_layout =[
            #[sg.Checkbox(' Free line ', default=False, key='-WEAK-')],
            [sg.Text("")],
            [sg.Checkbox('Automatic polynome', default=Flags["ZEE_AUTOPOLY"], key='-ZEE_AUTOPOLY-')],
            [sg.Text('Polynom terms of slit distorsion : ',size=(24,1)),sg.Input(default_text="{:.4e}".format(poly[0]),size=(12,1),key='fa'), sg.Text('* x**2 +'),
             sg.Input(default_text="{:.4e}".format(poly[1]),size=(12,1),key='fb'), sg.Text('* x')],
            [sg.Text('Constante :'),sg.Input(default_text="{:.2f}".format(poly[2]),size=(6,1),key='fc'),sg.Text('Base Shift :'),sg.Input(default_text=free_shift,size=(5,1),key='-FREE_SHIFT-')],
            [sg.Button("Frame")],
            #[sg.Button("frame"),sg.Text('Position line :',visible=False),sg.Input(default_text=0,size=(5,1),background_color='gray',key='xminf',visible=False),
            # sg.Text('at height y:',visible=False), sg.Input(default_text=0,size=(5,1),background_color='gray',key='y_xminf',visible=False), 
            #sg.Button("Calcul", key="Calculf",visible=False)],
            [sg.Text('Shift 1 :'),sg.Input(default_text=pos_free_blue,size=(5,1),key='wb'),sg.Text('Shift 2 :'),sg.Input(default_text=pos_free_red,size=(5,1),key='wr')],
            [sg.Checkbox(' Force values of tilt and scale ratio', default=Flags["FORCE_FREE_MAGN"], key='-F_ANG_SXSY2-')],
            [sg.Text('Tilt angle in degrees :', size=(15,1)), sg.Input(default_text=saved_tilt, size=(6,1),key='-TILT2-'),
             sg.Text('SY/SX ratio :', size=(10,1)), sg.Input(default_text=saved_ratio, size=(6,1),key='-RATIO2-')]
            ]
    
    if cfg.LG == 1:
        layout = [
            [sg.Text('Fichier(s) :', size=(8, 1)), sg.InputText(default_text='',size=(66,1),enable_events=True,key='-FILE-'),
             sg.FilesBrowse(' Ouvrir ',file_types=(("SER Files", "*.ser"),),initial_folder=os.path.join(WorkDir,previous_serfile)),
             sg.Button("Dernier", key='-LASTFILE-')],
            
            [sg.TabGroup([[sg.Tab('  Général  ', tab1_layout), sg.Tab('Doppler & Continuum', tab2_layout,), 
                sg.Tab('Séquence Doppler', tab3_layout,),
                sg.Tab('Magnétogramme',tab4_layout,),
                sg.Tab('Raie libre', tab5_layout)]],change_submits=True,key="TabGr",title_color='#796D65',tab_background_color='#404040')],  
            [sg.Button('Ok', size=(14,1)), sg.Cancel('  Sortir  ')],
            [sg.Button(button_text=LG_str, key='-LANG-', font=("Arial", 8),border_width=0, button_color='#404040'),sg.Text(current_version, size=(30, 1),text_color='Tan', font=("Arial", 8, "italic"))]
            ]
    else:
        layout = [
            [sg.Text('File(s) :', size=(7, 1)), sg.InputText(default_text='',size=(70,1),enable_events=True,key='-FILE-'),
             sg.FilesBrowse(' Open ',file_types=(("SER Files", "*.ser"),),initial_folder=os.path.join(WorkDir,previous_serfile)),
             sg.Button("Last", key='-LASTFILE-')],
            
            [sg.TabGroup([[sg.Tab('  General  ', tab1_layout), sg.Tab('Doppler & Continuum', tab2_layout,), 
                sg.Tab('Doppler Sequence', tab3_layout,),
                sg.Tab('Magnetogram',tab4_layout,),
                sg.Tab('Free line', tab5_layout)]],change_submits=True,key="TabGr",title_color='#796D65',tab_background_color='#404040')],  #title_color='#796D65',
            [sg.Button('Ok', size=(14,1)), sg.Cancel('  Exit  ')],
            [sg.Button(button_text=LG_str, key='-LANG-',font=("Arial", 8), border_width=0, button_color='#404040'),sg.Text(current_version, size=(30, 1),text_color='Tan', font=("Arial", 8, "italic"))]
            ]
            
    
    window = sg.Window(short_version, layout, location=win_pos,grab_anywhere=True,
                       no_titlebar=False,finalize=True)
    opened1 = False
    window['-SEC1-'].update(visible=opened1)
    opened2=False
    window['-SEC2-'].update(visible=opened2)
    
    window['-FILE-'].update(os.path.join(WorkDir,previous_serfile)) 
    window.BringToFront()
    #dpi=window.TKroot.winfo_fpixels('1i')
    #print('dpi',dpi)
    Flag_sortie=False
    wavelength_found=list_wave[1][0]
    solar_dict={}
    grid_graph={'color_grid':'yellow', 'gradu_on': True}
    
    
    while True:
        event, values = window.read()
        #print(event)
                    
        if event==sg.WIN_CLOSED or event=='  Exit  ' or event=='  Sortir  ': 
            Flag_sortie=True
            break
        
        if event == '-LANG-' :
            if window['-LANG-'].get_text() == 'FR' :
                window['-LANG-'].update('EN')
                cfg.LG=2
                my_dictini['lang']='EN'
            else :
                window['-LANG-'].update('FR')
                cfg.LG=1
                my_dictini['lang']='FR'
                
        if event == '-GRID-' :
            Flags['Grid'] = values['-GRID-']

                
        if event=="-PROFIL-":
            # charge le fichier profil .dat
            WorkDir=os.path.dirname(values['-FILE-'])+os.path.sep
            base=os.path.basename(values['-FILE-'])
            basefich=os.path.splitext(base)[0]
            pro_file=WorkDir+"Complements"+os.path.sep+'_'+basefich+'.dat'
            #print('profile ', pro_file)
            if basefich != '' :
                try :
                    pro_lamb=np.loadtxt(pro_file)
                    pro=pro_lamb[:,1]
                    lamb=pro_lamb[:,0]        
                    # calcul centre de la raie
                    centre_raie = np.argmin(pro)
                    
                    lamb=lamb-centre_raie
                    # affiche
                    plt.close('all')
                    matplotlib.use("Qt5Agg")
                    plt.figure(figsize=(8,5))
                    plt.scatter(lamb, pro, marker='.')
                    plt.title("line profile")
                    plt.show()
                except:
                    pass
                
            
        
        if event=="Trame" or event=="Frame" or event=="Trame0" or event=='Frame0' :
            poly_trame=[]
            if Flags['POL'] :
                poly_trame.append(float(values['a']))
                poly_trame.append(float(values['b']))
                poly_trame.append(float(values['c']))
            else:
                
                poly_trame.append(float(values['fa']))
                poly_trame.append(float(values['fb']))
                poly_trame.append(float(values['fc']))
            
            display_mean_img(poly_trame)
            
            if Flags['POL'] :
                #window['xmin'].update(str(mouse_x))
                #window['y_xmin'].update(str(mouse_y))
                if mouse_x != 0 :
                    window['c'].update(str(mouse_x))
                poly_trame=[]
                poly_trame.append(float(values['a']))
                poly_trame.append(float(values['b']))
                poly_trame.append(float(values['c']))
            else:
                #window['xminf'].update(str(mouse_x))
                #window['y_xminf'].update(str(mouse_y))
                if mouse_x != 0 :
                    window['fc'].update(str(mouse_x))
                poly_trame=[]
                poly_trame.append(float(values['fa']))
                poly_trame.append(float(values['fb']))
                poly_trame.append(float(values['fc']))
            
        if event=='Calc':
            res_dec, size_pix_cam, bin_cam =UI_calculette(size_pix_cam, bin_cam)
            window['-DX-'].update(str(res_dec))

        
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
                        if cfg.LG==1 :
                            logme('Erreur datetime fichier SER : '+serfile)
                        else:
                            logme('File datetime error : '+serfile)
                    
                    
        if event=="-LASTFILE-":
            files = [x for x in os.listdir(WorkDir) if x.endswith(".ser")]
            paths = [os.path.join(WorkDir, basename) for basename in files]
            newest = max(paths , key = os.path.getctime)
            window['-FILE-'].update(newest)
            window.write_event_value('Ok','')

        if event=='Ok':

            #WorkDir=os.path.dirname(values['-FILE-'])+"/"
            #os.chdir(WorkDir)
            base=os.path.basename(values['-FILE-'])
            basefich=os.path.splitext(base)[0]
            
            if basefich!='':
                break
            else:
                if cfg.LG==2:
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
            
        if event=="Calcul":
            try :
                y_xmin=int(values['y_xmin'])
                if y_xmin!=0 :
                    xmin=int(values['xmin'])
                    y_xmin=int(values['y_xmin'])
                    xline=xmin-float(values['a'])*y_xmin**2-float(values['b'])*y_xmin
                    window["c"].update("{:.1f}".format(xline))
                    poly[2]=xline
            except:
                print("doit etre valeur entiere")
                
        if event=="Calculf":
            try :
                y_xmin=int(values['y_xminf'])
                if y_xmin!=0 :
                    xmin=int(values['xminf'])
                    y_xmin=int(values['y_xminf'])
                    xline=xmin-float(values['fa'])*y_xmin**2-float(values['fb'])*y_xmin
                    window["fc"].update("{:.1f}".format(xline))
                    poly[2]=xline
            except:
                print("doit etre valeur entiere")
                
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
                KSO_P="{:+.3f}".format(float(reponse_web.text))
                # autres services 
                webservice='https://www.kso.ac.at/beobachtungen/ephem_api.php?date='+date_obs+'&time='+heure_obs+'&lat='+str_site_lat+'&lon='+str_site_long+"&B0&Lon&Carr"
                #print(webservice)
                reponse_web=rq.get(webservice)
                solar_data=reponse_web.text.split('\n')
                solar_dict['B0']=solar_data[0]
                solar_dict['L0']=solar_data[1]
                solar_dict['Carr']=solar_data[2]
                #print('Angle B0 : ', str(solar_data[0]))
                P,B0,L0, Rot_Carr=angle_P_B0 (fits_dateobs)
                """
                print('Angle P : ', KSO_P)
                print('Angle B0 : ', str(solar_data[0]))
                P,B0=angle_P_B0 (fits_dateobs)
                print('Angle P : ', str(P))
                print('Angle B0 : ', str(B0))
                """
                
            except:
                if cfg.LG==1 :
                    logme("Erreur dans le format des données")
                else:
                    logme("Error in data formatting")
                    
        if event=='-CLIMSO-' :
            fmt = '%Y%m%d'
            #date_obs='20211213'
            fits_dateobs=values['-DATEOBS-']
            if fits_dateobs!='' :
                """
                date_obs=fits_dateobs.split('T')[0].replace('-','')
                s=date_obs
                my_date = datetime.strptime(s, fmt)
                date_jd1=float(my_date.toordinal() + 1721424.5)
                sun_meudon=get_sun_meudon(date_jd1)
                
                it=0
                # recherche sur date ecart de 50 jours au plus
                while sun_meudon =='' and it<50:
                    date_jd1=date_jd1-1
                    sun_meudon=get_sun_meudon(date_jd1)
                    it=it+1
                    try :
                        #print('Meudon Spectro Halpha at closest date : ',sun_meudon)
                        urllib.request.urlretrieve(sun_meudon, 'meudon.jpg')
                    
                        # affiche meudon.jpg depuis le site de BASS2000
                        web.open('meudon.jpg')
                    except:
                        pass
                if it==50 :
                    print('no file found around this date')
                else:
                    print('Meudon Spectro Halpha at closest date : ',sun_meudon)
                """

                datemonth=fits_dateobs.split('T')[0].replace('-','')[:6]
                dateday=fits_dateobs.split('T')[0].replace('-','')
                r1="https://gong2.nso.edu/HA/hag/"+datemonth+"/"+dateday+"/"
                Vo_req=r1

                reponse_web=rq.get(Vo_req)
                sun_meudon=reponse_web.text.split("\n")
                t=sun_meudon[11].split('href=')[1].split(">")[0]
                t=t.replace('"','')
                web.open(r1+t)
                
                
                # recupère le nom du fichier en cours
                base=os.path.basename(values['-FILE-'])
                basefich=os.path.splitext(base)[0]
                # son repertoire
                curr_dir=os.path.split(values['-FILE-'])[0]
                
                if basefich!='':
                    # contruit le nom du fichier _clahe.png 
                    myimage=curr_dir+'/Clahe/_'+basefich+'_clahe.png'
                    # affiche le fichier si il existe
                    if os.path.exists(myimage):
                        web.open(myimage)
        
        if event=='-NSO-':
            web.open('https://nso.edu/')
            
        if event=='-BASS-':
            web.open('https://bass2000.obspm.fr/home.php')
            
        if event == 'Graph' :
            grid_graph['color_grid'], grid_graph['gradu_on'] = UI_graph()
            if cfg.LG==1 :
                if grid_graph['color_grid']=='Jaune' :
                    grid_graph['color_grid']='Yellow'
                if grid_graph['color_grid']=='Noir' :
                    grid_graph['color_grid']='Black'  


    window.close()
    try:          
        FileNames=values['-FILE-']
    except:
        FileNames=''

    #if FileNames==None :
            #FileNames=''

    
    try :
        Flags["RTDISP"] = values['-DISP-']
    except:
        pass
    #Flags["DOPCONT"]=values['-DOPCONT-']
    #Flags["ALLFITS"] = values['-SFIT-']
    Flags["ALLFITS"] = True
    #Flags["VOL"]=values['-VOL-']
    #Flags["POL"]=values['-POL-']
    #Flags["WEAK"]=values['-WEAK-']
    Flags["sortie"] = Flag_sortie
    Flags["FLIPRA"] = values['-RA_FLIP-']
    Flags["FLIPNS"] = values['-NS_FLIP-']
    Flags["FITS3D"] = values['-FITS3D-']
    Flags["Autocrop"] = values['-AUTOCROP-']
    Flags["Grid"] = values['-GRID-']
    Flags["DOPFLIP"] = values['-DOP_FLIP-']
    Flags["FORCE"] = values["-F_ANG_SXSY-"]
    Flags["SAVEPOLY"] = values["-SAVEPOLY-"]
    Flags["NOISEREDUC"] = values["-NOISEREDUC-"]    
    Flags["FREE_AUTOPOLY"] = values["-FREE_AUTOPOLY-"]
    Flags["ZEE_AUTOPOLY"] = values["-ZEE_AUTOPOLY-"] 
    
   # print(Flags)
    
    ratio_fixe = float(values['-RATIO-'])
    ang_tilt = values['-TILT-']
    centered_wave = wavelength_found
    centered_wave_label = values['-WAVE-']
    
    if centered_wave_label.isdigit():
        centered_wave =str(round(float(centered_wave)))
    
    Data_entete = [values['-OBSERVER-'], values['-INSTRU-'], 
                 float(values['-SITE_LONG-']), float(values['-SITE_LAT-']), values['-CONTACT-'], 
                 centered_wave, centered_wave_label]
    ang_P=float(values['-ANGP-']) 
    
    if Flags["WEAK"] :
        poly=[]
        poly.append(float(values['fa']))
        poly.append(float(values['fb']))
        poly.append(float(values['fc']))
        Shift.append(0)
        Shift.append(int(int(values['wb'])-0))
        Shift.append(int(int(values['wr'])-0))
        Shift.append(float(values['-FREE_SHIFT-']))
        Flags["FORCE"]=values['-F_ANG_SXSY2-']
        
        if values['-F_ANG_SXSY2-'] != True:
            ratio_fixe=0
            ang_tilt=0
        else :
            ratio_fixe=float(values['-RATIO2-'])
            ang_tilt=float(values['-TILT2-'])
        values['-F_ANG_SXSY3-']= values['-F_ANG_SXSY2-']

        
    if Flags["POL"]:
        poly=[]
        poly.append(float(values['a']))
        poly.append(float(values['b']))
        poly.append(float(values['c']))
        Flags["FORCE"]=values['-F_ANG_SXSY3-']
        
        if values['-F_ANG_SXSY3-'] != True: 
            # mode auto
            ratio_fixe=0
            ang_tilt=0
        else :
            # mode force
            ratio_fixe=float(values['-RATIO3-'])
            ang_tilt=float(values['-TILT3-'])

        values['-F_ANG_SXSY2-']=values['-F_ANG_SXSY3-']
    
    if values['-F_ANG_SXSY-'] != True and Flags["WEAK"] != True :
        if  Flags["POL"] != True :
            ratio_fixe=0
            ang_tilt=0
    
    Flags["FORCE_FREE_MAGN"]=values['-F_ANG_SXSY3-'] or values['-F_ANG_SXSY2-']
    Shift.append(float(values['-DX-']))
    Shift.append(int(values['-DopX-']))
    Shift.append(int(values['-ContX-']))

    
    if Flags["POL"]:
        Shift.append(int(values['Zeeman_wide']))
        Shift.append(float(values['Zeeman_shift']))
    else:
        Shift.append(int(values['Volume']))
        Shift.append(0.0)
    
    Shift.append(float(values['-SHIFTDOP-']))
    #print('shift dop ', Shift[5])
    
    Racines.append(values['racine_bleu'])
    Racines.append(values['racine_rouge'])
    

    
    return FileNames, Shift, Flags, ratio_fixe,ang_tilt, poly, Racines, Data_entete,ang_P, solar_dict, size_pix_cam, bin_cam, grid_graph

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


if sys.platform=="win32" :
    # gestion dynamique de la taille ecran
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # if your windows version >= 8.1
    except:
        ctypes.windll.user32.SetProcessDPIAware() # win 8.0 or less 

screen = tk.Tk()
scw,sch = screensize = screen.winfo_screenwidth(), screen.winfo_screenheight()
#dpi=screen.winfo_fpixels('1i')
#print('screen DPI', dpi)
screen.update()
screen.destroy()
#print('screen size', screensize)

while not Flag_sortie :
    
    if sch >1500 :
        # on a moniteur 4k
        screen_scale = 3
        screen_scaleZ=2
    else:
        screen_scale = 1.5 
        screen_scaleZ=2
        
    if sch<=800 :
        screen_scale = 1
        screen_scaleZ=1
    
# --------------------------------------------------------------------------------------
# recuperation des parametres de configuration memorisé au dernier traitement
# --------------------------------------------------------------------------------------

    # inti.yaml is a bootstart file to read last directory used by app
    # this file is stored in the module directory
    
    #my_ini=os.path.dirname(sys.argv[0])+'/inti.yaml'
    #my_ini=os.getcwd()+'/inti.yaml'
    my_dictini={'directory':'', 'dec doppler':3, 'dec cont':15, 
                'size_pix_cam':'0.0024', 'bin_cam':'1',
                'poly_slit_a':0, "poly_slit_b":0,'poly_slit_c':0, 
                'ang_tilt':0, 'ratio_sysx':1,
                'free_autpoly':0, 'zee_autpoly':0,'poly_free_a':0,'poly_free_b':0,'poly_free_c':0,
                'pos_free_blue':0, 'pos_free_red':0, 'free_shift':0,
                'force_free_magn': False,
                'win_posx':300, 'win_posy':200, 'screen_scale':0,'observer':'', 'instru':'','site_long':0, 'site_lat':0,
                'angle P':0,'contact':'','wavelength':0, 'wave_label':'Manuel', 'inversion NS':0, 'inversion EW':0,
                'autocrop':1, 'pos fente min':0, 'pos fente max':0,'crop fixe hauteur':0, 'crop fixe largeur':0,
                "zeeman_shift":0, "reduction bruit":0, 'grid disk':'on', 'lang' :'FR'}

    poly=[]
    
    try:
        #my_ini=os.path.dirname(sys.argv[0])+'/inti.yaml'
        #print('mon repertoire : ', mydir_ini)
        with open(my_ini, "r") as f1:
            my_dictini = yaml.safe_load(f1)
    except:
       if cfg.LG == 1:
           print('Création de inti.yaml comme : ', my_ini)
       else:
           print('creating inti.yaml as: ', my_ini) 
    
    WorkDir=my_dictini['directory']
    dec_pix_dop=int(my_dictini['dec doppler'])
    dec_pix_cont=int(my_dictini['dec cont'])
    saved_tilt=float(my_dictini['ang_tilt'])
    saved_angP=float(my_dictini['angle P'])
    saved_ratio=float(my_dictini['ratio_sysx'])
    if saved_ratio == 0 :
        saved_ratio= 1
    poly.append(float(my_dictini['poly_free_a']))
    poly.append(float(my_dictini['poly_free_b']))
    poly.append(float(my_dictini['poly_free_c']))
    pos_free_blue=int(my_dictini['pos_free_blue'])
    pos_free_red=int(my_dictini['pos_free_red'])
    w_posx=int(my_dictini['win_posx'])
    w_posy=int(my_dictini['win_posy'])
    Flags['DOPFLIP']=0
    Flags["SAVEPOLY"]=0
    if 'inversion EW' in my_dictini:
        Flags['FLIPRA']=my_dictini['inversion EW']
        Flags['FLIPNS']=my_dictini['inversion NS']
    else:
        Flags['FLIPRA']=0
        Flags['FLIPNS']=0
        
    if 'force_free_magn' in my_dictini :
        Flags['FORCE_FREE_MAGN']  = my_dictini['force_free_magn']
    else:
        Flags['FORCE_FREE_MAGN'] = False
    
    if 'size_pix_cam' not in my_dictini:
        # si pas dans fichier ini
        my_dictini['size_pix_cam']='0.0024'
        size_pix_cam='0.0024'
    else :
        size_pix_cam=my_dictini['size_pix_cam']
    
    if 'bin_cam' not in my_dictini:
        my_dictini['bin_cam']='1'
        bin_cam='1'
    else:
        bin_cam=my_dictini['bin_cam']
     
    if 'autocrop' not in my_dictini:
        my_dictini['autocrop']='1'
        Flags['Autocrop']=1
    else:
        Flags['Autocrop']=my_dictini['autocrop']
        
    if 'free_autopoly' not in my_dictini:
        my_dictini['free_autopoly']=0
        Flags['FREE_AUTOPOLY']=0
    else:
        Flags['FREE_AUTOPOLY']=my_dictini['free_autopoly']
    
    if 'zee_autopoly' not in my_dictini:
        my_dictini['zee_autopoly']=0
        Flags['ZEE_AUTOPOLY']=0
    else:
        Flags['ZEE_AUTOPOLY']=my_dictini['zee_autopoly']
        
    if 'free_shift' not in my_dictini:
        my_dictini['free_shift'] = 0 #decalage en mode zeeman
        free_shift = 0
    else :
        free_shift = my_dictini['free_shift']
        
        
    if 'zeeman_shift' not in my_dictini:
        my_dictini['zeeman_shift'] = 0 #decalage en mode zeeman
        zee_shift = 0
    else :
        zee_shift = my_dictini['zeeman_shift']
        
        
    if 'reduction_bruit' not in my_dictini:
        # si pas dans fichier ini
        my_dictini['reduction_bruit']=0
        Flags['NOISEREDUC'] = 0
    else :
        Flags['NOISEREDUC']=my_dictini['reduction_bruit']
        
    if 'grid disk' not in my_dictini:
        # si pas dans fichier ini
        my_dictini['grid disk']='on'
        grid_on=True
        Flags['Grid'] = 1
    else :
        if my_dictini['grid disk'] == 'on' :
            grid_on=True
            Flags['Grid'] = 1
        else :
            grid_on=False
            Flags['Grid'] = 0
    
    # param cas difficiles
    if 'crop fixe hauteur' not in my_dictini:
        my_dictini['crop fixe hauteur']='0'
    if 'crop fixe largeur' not in my_dictini:
        my_dictini['crop fixe largeur']='0'
    if 'pos fente min' not in my_dictini:
        my_dictini['pos fente min']='0'
    if 'pos fente max' not in my_dictini:
        my_dictini['pos fente max']='0'
        
    # param echelle UI ecran override mode auto
    if 'screen_scale' not in my_dictini:
        my_dictini['screen_scale']='0'
    else :
        if int(my_dictini['screen_scale'])!=0 :
            screen_scale=float(my_dictini['screen_scale'])
            if screen_scale >= 1 :      
                screen_scaleZ=2     # facteur de zoom
                
    #gestion langue dans inti.yaml
    if 'lang' not in my_dictini :
        my_dictini['lang']='FR'
        LG_str='FR'
    else :
        LG_str = my_dictini['lang']
        if LG_str == 'FR' : cfg.LG=1
        if LG_str !='FR' : cfg.LG=2
        
    
    param=[my_dictini['pos fente min'],my_dictini['pos fente max'],my_dictini['crop fixe hauteur'],my_dictini['crop fixe largeur']]
    win_pos=(w_posx,w_posy)
    data_entete=[my_dictini['observer'], my_dictini['instru'],float(my_dictini['site_long']),float(my_dictini['site_lat']),my_dictini['contact'],
                 my_dictini['wavelength'],my_dictini['wave_label']]
    

# ------------------------------------------------------------------------------------    
# Lance GUI 
# ------------------------------------------------------------------------------------    

    serfiles, Shift, Flags, ratio_fixe,ang_tilt, poly, racines, data_entete,ang_P,solar_dict, size_pix_cam, bin_cam, grid_graph= UI_SerBrowse(WorkDir, saved_tilt, saved_ratio,
                                                                             dec_pix_dop, dec_pix_cont, poly,pos_free_blue, pos_free_red,free_shift,zee_shift,
                                                                             win_pos, previous_serfile, data_entete,saved_angP, Flags,
                                                                             size_pix_cam, bin_cam, screen_scale)
    
    # recupere les fichiers
    serfiles=serfiles.split(';')
    #print('serfile : ',  len(serfiles))
    if len(serfiles)==1 :
        previous_serfile=os.path.basename(serfiles[0])

    # init seq number pour magnetogramme
    ii=1
    # permet de ne pas fermer INTI et d'entrer de nouveaux fichiers à traiter
    Flag_sortie=Flags["sortie"]

    # pour gerer la tempo des affichages des images resultats dans cv2.waitKey
    # si plusieurs fichiers à traiter
    if len(serfiles)==1:
        tempo=90000 #tempo 60 secondes, pour no tempo mettre tempo=0 et faire enter pour terminer
        if  Flags["POL"]:
            tempo=3000 # tempo raccourcie après extraction zeeman 
    else:
        tempo=1000 #temp 1 sec
        
# ------------------------------------------------------------------------------------             
# sauvegarde des param de lang et rep dans fichier de configuration avant traitement

    # met a jour le repertoire et les flags dans le fichier ini, oui a chaque fichier pour avoir le bon rep
    my_dictini['directory']=WorkDir
    LG_str = my_dictini['lang']
    
    if Flags['Grid']==True :
        my_dictini['grid disk']='on'
    else:
        my_dictini['grid disk']='off'

    if cfg.LG ==1 :
        my_dictini['lang']='FR'
    else :
        my_dictini['lang']='EN'
       
    try:
        with open(my_ini, "w") as f1:
            yaml.dump(my_dictini, f1, sort_keys=False)
    except:
        if cfg.LG == 1:
            logme ('Erreur lors de la sauvegarde de inti.yaml comme : '+my_ini)
        else:
            logme ('Error saving inti.yaml as: '+my_ini)
    
        
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------       
# boucle sur la liste des fichers
# -----------------------------------------------------------------------------------------   
# -----------------------------------------------------------------------------------------  
 
    for serfile in serfiles:
        #print (serfile)
        
        if Flag_sortie :
            sys.exit()
    
        if serfile=='':
            sys.exit()
        
        WorkDir=os.path.dirname(serfile)+"/"
        os.chdir(WorkDir)
        # Creation des trois sous-repertoires 
        subrep=WorkDir+'BASS2000'
        if not os.path.isdir(subrep):
           os.makedirs(subrep)
        subrep=WorkDir+'Clahe'
        if not os.path.isdir(subrep):
           os.makedirs(subrep)
        subrep=WorkDir+'Complements'
        if not os.path.isdir(subrep):
           os.makedirs(subrep)
        # extrait nom racine
        base=os.path.basename(serfile)
        # basefich: nom du fichier ser sans extension et sans repertoire
        basefich=os.path.splitext(base)[0]
        if base=='':
            if cfg.LG == 1:
                logme('Erreur de nom de fichier : '+serfile)
            else:
                logme('File name error: '+serfile)
            sys.exit()

# ------------------------------------------------------------------------------------                     
# appel au module d'extraction, reconstruction et correction
# ------------------------------------------------------------------------------------     
        
        # ajout d'un ordre de sequence pour mode magnetorgramme
        if Flags['POL'] and ii>1:
            ratio_fixe=geom[0]
            ang_tilt=geom[1]
        
        # lance ser_recon
        frames, header, cercle, range_dec, geom, polynome=sol.solex_proc(serfile,Shift,Flags,ratio_fixe,ang_tilt, 
                                                                         poly, data_entete,ang_P, solar_dict, param)


# ------------------------------------------------------------------------------------             
# sauvegarde des param dans fichier de configuration

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
        my_dictini['size_pix_cam']=size_pix_cam
        my_dictini['bin_cam']=bin_cam
        my_dictini['autocrop']=Flags['Autocrop']
        my_dictini['grid disk']=Flags['Grid']
        my_dictini['pos fente min']=param[0]
        my_dictini['pos fente max']=param[1]
        my_dictini['crop fixe hauteur']=param[2]
        my_dictini['crop fixe largeur']=param[3]
        my_dictini['force_free_magn'] = Flags["FORCE_FREE_MAGN"]
        my_dictini['zeeman_shift'] = Shift[4]
        my_dictini['reduction_bruit'] = Flags['NOISEREDUC']
        my_dictini['screen_scale'] = screen_scale
        LG_str = my_dictini['lang']

        if cfg.LG ==1 :
            my_dictini['lang']='FR'
        else :
            my_dictini['lang']='EN'
        
        if Flags['WEAK']:
            my_dictini['free_autopoly']=Flags['FREE_AUTOPOLY']
            my_dictini['pos_free_blue']=round(0+Shift[1])
            my_dictini['pos_free_red']=round(0+Shift[2])
            my_dictini['free_shift'] = Shift[3]
           
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
            
        if Flags["SAVEPOLY"] != 0 :
            #on met ajour les params poly dans mode free et magn
            my_dictini['poly_free_a']=float(polynome[0])
            my_dictini['poly_free_b']=float(polynome[1])
            my_dictini['poly_free_c']=float(polynome[2])
            
        if Flags['WEAK']==True and Flags['FREE_AUTOPOLY']==1 :
            my_dictini['poly_free_a']=float(polynome[0])
            my_dictini['poly_free_b']=float(polynome[1])
            my_dictini['poly_free_c']=float(polynome[2])
        
        
        try:
            with open(my_ini, "w") as f1:
                yaml.dump(my_dictini, f1, sort_keys=False)
        except:
            if cfg.LG == 1:
                logme ('Erreur lors de la sauvegarde de inti.yaml comme : '+my_ini)
            else:
                logme ('Error saving inti.yaml as: '+my_ini)

# ------------------------------------------------------------------------------------             
# formation des noms de base des fichiers
        
        # le noms de bases des fichiers
        # basefich: nom du fichier ser sans extension et sans repertoire
        base=os.path.basename(serfile)
        basefich='_'+os.path.splitext(base)[0]
        basefich_comple="Complements"+os.path.sep+basefich
        basefich_bass="BASS2000"+os.path.sep+basefich
        basefich_clahe="Clahe"+os.path.sep+basefich
        #print(basefich_comple, basefich_bass, basefich_clahe)
 
# ------------------------------------------------------------------------------------             
# gestion taile fentere avec ecran, surtout ecran 4K

        ih = frames[0].shape[0]
        newiw = frames[0].shape[1]
        #print('newimg w et h', newiw,ih)
        
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

# ------------------------------------------------------------------------------------             
# lecture sur le disque des images fits 16 bits crées par Ser_recon raw et recon
    
        # Lecture et affiche image disque brut
        if range_dec[0]==0 :
            if Shift[0] ==0 :
                ImgFile=basefich_comple+'_raw.fits'   
            else :
                ImgFile=basefich_comple+'_dp'+str(int(Shift[0]))+'_raw.fits'
        else:
            ImgFile=basefich_comple+'_dp'+str(range_dec[0])+'_raw.fits'
        
        hdulist = fits.open(ImgFile, memmap=False)
        hdu=hdulist[0]
        myspectrum=hdu.data
        rih=hdu.header['NAXIS2']
        riw=hdu.header['NAXIS1']
        Disk=np.reshape(myspectrum, (rih,riw))
        
        # Lecture  image recon
        if range_dec[0]==0:
            if Shift[0] ==0 :
                ImgFile=basefich+'_recon.fits'   
            else :
                ImgFile=basefich+'_dp'+str(int(Shift[0]))+'_recon.fits'
        else :
            ImgFile=basefich+'_dp'+str(range_dec[0])+'_recon.fits'
            
        hdulist = fits.open(ImgFile, memmap=False)
        hdu=hdulist[0]
        base_filename=hdu.header['FILENAME'].split('.')[0]
        
        # facteur de brightness sur image raw uniquement
        #Ratio_lum=(65536/np.max(Disk))*0.8
        Ratio_lum=(65535/np.max(Disk))
        #print ('ratio_lum ', Ratio_lum)
        #print ('max Disk ', np.max(Disk))
        Disk2=np.array((np.copy(Disk)*Ratio_lum),dtype='uint16')
        hdulist.close()
        
# ------------------------------------------------------------------------------------             
# prepare fenetres pour affichage des images

        # variable top_w gere en fait la position horizonatale
        # left_w la position verticale
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
            cv2.moveWindow('Zoom', lw,5*lw)
            cv2.resizeWindow('Zoom', int(300*screen_scaleZ), int(300*screen_scaleZ))
            #
            cv2.namedWindow('sliders', cv2.WINDOW_AUTOSIZE)
            cv2.moveWindow('sliders', int(top_w*1.3), 0)
            cv2.resizeWindow('sliders',(600,100))
            source_window='clahe'
            
            cv2.createTrackbar('Seuil haut', 'sliders', 0,255, on_change_slider)
            cv2.createTrackbar('Seuil bas', 'sliders', 0,255, on_change_slider)

# ------------------------------------------------------------------------------------             
# png image generation 
# ------------------------------------------------------------------------------------             

        # image seuils moyen
        frame1=np.copy(frames[0])
        sub_frame=frame1[5:,:-5]
        Seuil_haut=np.percentile(sub_frame,99.999)
        Seuil_bas=(Seuil_haut*0.05) # was 0.15
        frame1[frame1>Seuil_haut]=Seuil_haut
        #print('seuil bas', Seuil_bas)
        #print('seuil haut', Seuil_haut)
        
        fc=(frame1-Seuil_bas)* (65535/(Seuil_haut-Seuil_bas)) # was 65500
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
        
        # ajout calcul intensité moyenne sur ROI centrée
        
        lum_roi= get_lum_moyenne(frame1)
        print()
        if cfg.LG == 1:
            print("Intensité moyenne : "+ str(int(lum_roi)))
        else:
            print("Average Intensity : "+ str(int(lum_roi)))
       
        cv2.imshow('contrast',frame_contrasted)
        
    
        # image raw
        Disk2=cv2.flip(Disk2,0)
        cv2.imshow('Raw',Disk2)
        
        # image protus 
        
        # hide disk before setting max threshold
        frame2=np.copy(frames[0])
        disk_limit_percent=0.002 # black disk radius inferior by 2% to disk edge (was 1%)
        if cercle[0]!=0:
            x0=cercle[0]
            y0=cercle[1]
            #wi=round(cercle[2])
            #he=round(cercle[3])
            wi=int(cercle[2])
            he=int(cercle[3])
            r=(min(wi,he))
            r=int(r- round(r*disk_limit_percent))-1 # retrait de 1 pixel modif de juin 2023
            #print('c0,c1', cercle[0], cercle[1])
            #print(cercle, wi,he,r)
            # MattC but prefer to really see deviation from circle
            fc3=cv2.circle(frame2, (x0,y0),r,80,-1,lineType=cv2.LINE_AA)
            #frame2=cv2.ellipse(frame2, (x0,y0),(wi,he),0,0,360,(0,0,0),-1,lineType=cv2.LINE_AA ) #MattC draw ellipse, change color to black
            frame1=np.copy(fc3)
            Threshold_Upper=np.percentile(frame1,99.9999)*0.6  #preference for high contrast was 0.5
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
            if cfg.LG == 1:
                print("Erreur disque occulteur.")
            else:
                print("Mask disk error.")
                
        #frame_contrasted3=frame_contrasted
        
        # create a CLAHE object (Arguments are optional)
        clahe = cv2.createCLAHE(clipLimit=0.8, tileGridSize=(2,2))
        cl1 = clahe.apply(frames[0])
        
        Seuil_bas=np.percentile(cl1, 25)
        Seuil_haut=np.percentile(cl1,99.9999)*1.05
        if Seuil_haut>65535 :
            Seuil_haut=65535
        cc=(cl1-Seuil_bas)*(65535/(Seuil_haut-Seuil_bas))
        cc[cc<0]=0
        cc=np.array(cc, dtype='uint16')
        
        # creation des sliders
        if len(frames)==1 and len(serfiles)==1:
            param=np.copy(cc)
            param2=np.copy(cl1)
            source_window='clahe'
            img_data=np.copy(param2)   # modif en copy
            paramh=Seuil_haut
            paramb=Seuil_bas
            cv2.setMouseCallback('clahe',mouse_event_callback, [source_window,param,param2,paramh, paramb])
            sb=int(Seuil_bas/65535*255)
            sh=int(Seuil_haut/65535*255)
            if sh > 65535 :
                sh=65535
            cv2.setTrackbarPos('Seuil bas','sliders',sb)
            cv2.setTrackbarPos('Seuil haut','sliders',sh)
            
        cc=cv2.flip(cc,0)
        cv2.imshow('clahe',cc)

# ------------------------------------------------------------------------------------             
# si traitement de plus d'une longueur d'onde
        
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
                        f1=np.array(frames[1], dtype="float64")
                        fn=np.array(frames[len(frames)-1], dtype="float64")
                        moy=np.array(((f1+fn)/2), dtype='uint16')
                    else:
                        f1=np.array(frames[1], dtype="float64")
                        f2=np.array(frames[2], dtype="float64")
                        moy=np.array(((f1+f2)/2), dtype='uint16')
                        if Shift[5] != 0 :
                            lum_roi1 = get_lum_moyenne(frames[1])
                            lum_roi2 = get_lum_moyenne(frames[2])
                            lum_roimoy = get_lum_moyenne(moy)
                            ratio_l1 = lum_roimoy/lum_roi1
                            ratio_l2 = lum_roimoy/lum_roi2
                            frames[2] = frames[2]*ratio_l2
                            frames[1] = frames[1]*ratio_l1
                    
                        #frames[1]=np.array((moy-f1), dtype='uint16')
                        #frames[2]=np.array((f2-moy), dtype='uint16')

                    
                    i2,Seuil_haut, Seuil_bas=seuil_image(moy)
                    i1=seuil_image_force (frames[1],Seuil_haut, Seuil_bas)
                    i3=seuil_image_force(frames[2],Seuil_haut, Seuil_bas)
                    #i1,Seuil_haut, Seuil_bas=seuil_image(frames[1])
                    #i3,Seuil_haut, Seuil_bas=seuil_image(frames[2])
                    if Flags['DOPFLIP'] !=0 : 
                        img_doppler[:,:,0] = i3
                        img_doppler[:,:,1] = i2
                        img_doppler[:,:,2] = i1
                    else :
                        img_doppler[:,:,0] = i1 # blue
                        img_doppler[:,:,1] = i2 # green
                        img_doppler[:,:,2] = i3 # red
                    img_doppler=cv2.flip(img_doppler,0)
                    cv2.imshow('doppler',img_doppler)
               
                except:
                    if cfg.LG == 1:
                        print ('Erreur image doppler.')
                    else:
                        print ('Doppler image error.')
                    flag_erreur_doppler=True
                    cv2.destroyWindow('doppler')
                    pass
    
                #sauvegarde en png de doppler
                if flag_erreur_doppler==False:
                    cv2.imwrite(basefich+'_doppler'+str(abs(range_dec[1]))+'.png',img_doppler)
    
            
            if Flags["POL"] :
                
                
                try :
                    #moy=(frames[1]+frames[2])/2
                    #img_weak_array= frames[0]-moy
                    fr1=np.copy(frames[1])
                    fr2=np.copy(frames[2])
                    fr0=np.copy(frames[0])
                    #s=np.array(np.array(fr1, dtype='float32')+np.array(fr2, dtype='float32'),dtype='float32')
                    #moy=s*0.5
                    img_diff=np.array(np.array(fr2, dtype='float32')-np.array(fr1, dtype='float32'),dtype='int32')
                except:
                    if cfg.LG == 1:
                        print ('Erreur image difference ')
                    else:
                        print ('Image difference error.')
            
            
            if Flags["WEAK"] :
       
                
                flag_erreur_weak=False
                try :
                    #moy=(frames[1]+frames[2])/2
                    #img_weak_array= frames[0]-moy
                    fr1=np.copy(frames[1])
                    fr2=np.copy(frames[2])
                    fr0=np.copy(frames[0])
                    s=np.array(np.array(fr1, dtype='float64')+np.array(fr2, dtype='float64'),dtype='float64')
                    moy=s*0.5
                    img_diff=np.array(fr2, dtype='float64')-np.array(fr1, dtype='float64')
                    
                    d=(np.array(fr0, dtype='float64')-moy)
    
                    
                    offset=-np.min(d)
                    #img_weak_array_nooff=np.copy(d)
                    print(offset)
                    img_weak_array=d+float(offset+100)
                    img_weak_uint=np.array((img_weak_array), dtype='uint16')
                    #Seuil_bas=int(offset/2)
                    Seuil_bas=0
                    Seuil_haut=int(np.percentile(img_weak_uint,99.95))
                    if (Seuil_haut-Seuil_bas) != 0 :
                        img_weak=seuil_image_force(img_weak_uint, Seuil_haut, Seuil_bas)
                    else:
                        img_weak=np.array((img_weak_array), dtype='uint16')
                    img_weak=np.array(img_weak, dtype='uint16')
                    img_weak=cv2.flip(img_weak,0)
                    cv2.imshow('doppler',img_weak)
                    cv2.setWindowTitle("doppler", "free line")
                    img_weak_array=d
                
                except:
                    if cfg.LG == 1:
                        print ('Erreur image ')
                    else:
                        print ('Image error.')
                    flag_erreur_doppler=True
                    cv2.destroyWindow('doppler')
                    pass
    
                #sauvegarde en png de doppler
                if flag_erreur_weak==False:
                    cv2.imwrite(basefich+'_free'+'.png',img_weak)

# ------------------------------------------------------------------------------------             
# sauve les png raw, disk, inversée et mix, colorisée
        
        #sauvegarde en png de l'image raw, avant correction geomtrique et flat
        if range_dec[0]==0:
            img_suffix=""
            cv2.imwrite(basefich_comple+img_suffix+'_raw.png',Disk2)
        else:
            img_suffix="_dp"+str(range_dec[0])
        
        #sauvegarde en png disk quasi seuils max
        cv2.imwrite(basefich+img_suffix+'_disk.png',frame_contrasted)
        
        # image contraste inversé
        frame_sub=65535-frame_contrasted
        cv2.imwrite(basefich+img_suffix+'_inv.png',frame_sub)
        # test mix mais c'est moche...
        frame_sub[frame_sub==65535]=1000
        frame_combo=np.maximum(frame_contrasted3, frame_contrasted)
        frame_combo[frame_combo==65535]=0
        cv2.imwrite(basefich+img_suffix+'_mix.png',frame_combo)
        # image colorisée
        couleur = my_dictini['wave_label']
        img_color = Colorise_Image(couleur, frame_contrasted, basefich, img_suffix)
        
        
        # si pas de flag mode magneto et ou raie libre
        if Flags["POL"] != True  and  Flags["WEAK"] != True : 
            
            # sauve en format jpg pour BASS2000 si pas en manuel
            if couleur != 'Manual' :
                cv2.imwrite("BASS2000"+os.path.sep+base_filename+'.jpg',frame_contrasted*0.0038)
                cv2.imwrite("BASS2000"+os.path.sep+base_filename+'_protus.jpg',frame_contrasted3*0.0038)

            # genere image avec stonyhurtdisk
            nomfich=basefich+img_suffix+'_disk.png'
            nomrep1=WorkDir
            nomrep2=WorkDir+"BASS2000"+os.path.sep
            fich_param={}
            graph_param={}
            fich_param['date'] = header['DATE-OBS']
            #hdr['SEP_LAT']=float(solar_dict['B0'])
            #hdr['SEP_LON']=float(solar_dict['L0'])
            #hdr['SOLAR_P']=float(ang_P)
            #hdr['CAR_ROT']=float(solar_dict['Carr'])
            fich_param['P']=0
            fich_param['PDisp']=0
            #grid_on=True
            if Flags ['Grid']==1 :
                try :
                    fich_param['P'] = header['SOLAR_P']  # Only for display, INTI puts heliographic pole on top
                    fich_param['PDisp'],a,b,c=angle_P_B0 (fich_param['date'] ) # modif 14 janvier, il faut l'afficher
                except:
                    fich_param['PDisp'],a,b,c=angle_P_B0 (fich_param['date'] )
                try :
                    fich_param['B0'] = float(header['SEP_LAT'])
                    if fich_param['B0'] == 0 :  # modif du 14 janvier 24
                        a, fich_param['B0'],b,c=angle_P_B0 (fich_param['date'] )
                        fich_param['B0']=float(fich_param['B0'])
                        
                except:
                    a, fich_param['B0'],b,c=angle_P_B0 (fich_param['date'] )
                    #print('B0: ', fich_param['B0'])
                    fich_param['B0']=float(fich_param['B0'])
                    
                fich_param['xcc'] = x0
                
                if y0<ih or y0>ih :
                    fich_param['ycc'] = ih-y0
                else :
                    fich_param['ycc'] = y0
                fich_param['radius'] = r
                graph_param['gradu'] = grid_graph['gradu_on']
                graph_param['opacity'] = 0.5
                graph_param['lwidth'] = 0.2
                graph_param['color'] = grid_graph['color_grid']
                graph_param['color_inv'] = 'black'
                graph_param['disp']=False
                
                # creation et sauvegarde du fichier avec grille coor helio
                sth.draw_stonyhurst(nomrep1, nomrep2,nomfich, fich_param, graph_param)
 
# ------------------------------------------------------------------------------------             
# sauve les png protus et clahe
        
        #sauvegarde en png seuils protus
        cv2.imwrite(basefich+img_suffix+'_protus.png',frame_contrasted3)

        #sauvegarde en png de clahe
        cv2.imwrite(basefich_clahe+img_suffix+'_clahe.png',cc)

# ------------------------------------------------------------------------------------             
# sauve les png multispectraux et cree une video
       
        if (Flags["VOL"] or Flags["POL"]) and len(range_dec)!=1:
            
            k=1
            
            #ROi de 200 pixels autour du centre du disque
    
            dim_roi=100
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
            
            if Flags["POL"] :
                flag_lum_auto=False
                flag_seuil_auto=True
            else:
                flag_lum_auto=True
                flag_seuil_auto=False
                
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
                    
 # ------------------------------------------------------------------------------------      
 # sauvegarde les fits
 
        frame2=np.copy(frames[0])
        if Flags['WEAK']:
            frame2=np.copy(img_weak_array)
            DiskHDU=fits.PrimaryHDU(frame2,header)
            DiskHDU.writeto(basefich+'_free.fits', overwrite='True')
            if len(serfiles)>1 :
                DiskHDU.writeto(basefich+'_free-'+str(ii)+'.fits', overwrite='True')
            frame3=np.copy(img_diff)
            DiskHDU=fits.PrimaryHDU(frame3,header)
            DiskHDU.writeto(basefich_comple+'_diff.fits', overwrite='True')
            # sauve les images individuelles pour debug
            DiskHDU=fits.PrimaryHDU(fr0,header)
            DiskHDU.writeto(basefich_comple+'_x0.fits', overwrite='True')
            DiskHDU=fits.PrimaryHDU(fr1,header)
            DiskHDU.writeto(basefich_comple+'_x1.fits', overwrite='True')
            DiskHDU=fits.PrimaryHDU(fr2,header)
            DiskHDU.writeto(basefich_comple+'_x2.fits', overwrite='True')
            DiskHDU=fits.PrimaryHDU(moy,header)
            DiskHDU.writeto(basefich_comple+'_sum.fits', overwrite='True')
            
        else:
            """
            frame2=np.array(cl1, dtype='uint16')
            DiskHDU=fits.PrimaryHDU(frame2,header)
            DiskHDU.writeto(basefich+'_clahe.fits', overwrite='True')
            """
        
        if Flags['POL']:
            # image difference en fits
            frame3=np.copy(img_diff)
            DiskHDU=fits.PrimaryHDU(frame3,header)
            DiskHDU.writeto(basefich_comple+'_diff.fits', overwrite='True')
            # renomme les dp fits en r et b
            ImgFileb=basefich+'_dp'+str(range_dec[1])+'_recon.fits'
            ImgFiler=basefich+'_dp'+str(range_dec[2])+'_recon.fits'
            os.replace(ImgFileb,racines[0]+str(ii)+".fits")
            os.replace(ImgFiler,racines[1]+str(ii)+".fits")
            print('Sorties :')
            print(racines[0]+str(ii)+".fits")
            print(racines[1]+str(ii)+".fits")
            # renomme les dp png en r et b
            ImgFileb=basefich+'_dp1.png'
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
            try :
                filename_3D=a[0]+'SOLEX_fullprofile'+a[1]
            except:
                filename_3D=a[0]+'SOLEX_fullprofile.fits'
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
            
    
# -----------------------------------------------------------------------------------------      
# Affichage des images resultats
# -----------------------------------------------------------------------------------------   

        cv2.waitKey(tempo)
        
        # mise en attente action utilisateur ou tempo
        cv2.destroyAllWindows()
          
        # utile de rappeler le nom du dernier fichier traité sans avoir a remonter dans les logs
        print (serfile)
        ii=ii+1 # boucle sur non de fichier pour generer sequence en polarimetrie
        print() # ligne vide pour separer log des prochain traitement

