# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 11:42:32 2020

@author: valerie desnoux


------------------------------------------------------------------------
Version 5.1 paris 1 er nov
- ajout mode auto dans POl (magnetogramme)

Version 5.0 paris 27 juillet
- passage en decimal du shift avec gestion dans la constante

Version V4.1.8 paris 21 juillet 23
- ajout poly auto et decalage en mode free auto et manuel
- decalage en decimal

Version V4.1.6 du 17 juillet 2023
- ajout mode reduction de bruit sur 3 colonnes en standard, free et magnet

version V4.1.6 du 15 juiller 2023
- force = True pour disk k <> 0
- menage fichier _dp2_raw, manual en mode manuels
- correction bug coordonnée centre entete fits 

version V4.1.4 du 14 juillet 2023
- gere sur flag_force et accepte angle de tilt à zero
- format des coeff du polynome
- reactive zeeamn_shift

version V4.1.2 du 8 juillet 2023
- gestion cas difficiles

version V4.1.1 du 3 juillet 2023
- suppression decalage zeeman
- recalcul position de depart dans poly zeeman pour get_line_pos_absorption

version 4.0.9 paris 1 juillet 2023
- autcrop depuis flag
- angle alignement RA prend scaling en compte
- free ligne remplace position par decalage

version 4.0.5 du 3 mai - Antibes
- ajout des labels et longueurs d'onde d'apres fichier Meudon
- test depassement pixel_shift

version du 19 mars 2023 - paris
- autorise inversions et rotations sur toutes les images
- decale de 1 pixel le centre du disque en inversion NS

version du 12 mars 2023 - paris
- ne prends plus en compte les inversions si plus d'une image traitée

version du 18 fev 2023 - paris
- correction bug timestamp heure pc de traitement en utc fichier ser


version du 29 jan 2023 - Antibes
- reduit bande auto si rotation en fontion de l'angle de rotation
- ajoute passage de solar_dict pour sauvegarde dans entete si non vide
- WAVELENGTH en longueur d'onde
- elimine premieres et derniers colonnes pour calcul lignes défectueuses

version du 22 jan 2023 - paris
- ajout des mots clefs base BASS2000 
    CENTER_X, CENTER_Y (ou CRPIX1, CRPIX2)
    SOLAR_R => rayon du Soleil en pixels

- mot clef wavelnth doit avoir un nombre

version du 26 dec 2022 - paris
- ajout fonction de rotation sur image finale
- ajout mots clefs entete JM.Malherbe
    hdr['CONTACT']=data_entete[4]
    hdr['WAVELNTH']=data_entete[5]
    hdr['PHYSPARA']= 'Intensity'
    hdr['WAVEUNIT']= -10
    hdr['FILENAME']=filename_wave_20180620_122805.fits
-inverse sens angle tilt correction avec flip

Version du 17 sept 2022 - paris
- ajout data_entete dans fichiers fits
 hdr['DATE-OBS']
 hdr['OBSERVER']
 hdr['INSTRUME']
 hdr['SITELONG'] #Longitude of the telescope in decimal degrees, count East as positive
 hdr['SITELAT'] #Latitude of the telescope in decimal degrees 
 hdr['OBJNAME']='Sun'
 
Version du 15 mai 2022 - paris
- autorise correction de tilt pour angle >0.2° au lieu de 0.3

Version du 28 avril 2022 - paris
- mise en commentaire malheureuse de la zone de filtrage disque qui n'excluait plus les bords

version du 23 avril 2022 - Paris
- factorisation des tableaux indices left et rigth
- ajout de calcul d'une sequence doppler
- ajout de la fonction magnetogramme
- creation d'une version anglaise par switch LG a la compil
- ajout mot clef fits 
     coord centre et rayon du disque
         hdr['INTI_XC'] = cercle0[0]
         hdr['INTI_YC'] = cercle0[1]
         hdr['INTI_R'] = cercle0[2]
     coord haut et bas du disque
         hdr['INTI_Y1'] = y1_img
         hdr['INTI_Y2'] = y2_img
- gestion shift hors limite

Version du 1er Nov - Paris
- modif detection bords dans correction de transversallium
- ajout d'un switch pour debug
- ajout message erreur if 8 bits scan
- multiply by 2 instensity of the real time disk display 

Bac à sable le 15 sept 2021 - Paris
- test de dopplergram et continuum
- ne pas mettre y1 et y2 fixe pour circularisation des images dop et cont
- coord cercle de l'image raw première


version 18 septembre 2021 - antibes
- gere depassement indices avec le shift
- ajuste de 64000 a 64500 le clamp pour la saturation

version 12 sept 2021 - antibes
- affichage disque noir et seuils protus sur suggestion de mattC

Version du 8 sept 2021 - paris
- Augmente à 3 decimales l'affichage angle et ratio scaling
- changement suffixe _img par _raw
- tilt par rapport au centre
- agrandi image apres tilt pour ne pas couper l'image
- calculs avec round plutot que int

Version du 19 aout 2021 - Antibes
- ajout de extension au nom de fichier si decalage en pixels non égale à zéro
- add underscore at beggining of any processed file to retrieve them faster as for isis

Version 11 aout 2021 - Antibes
Large modification
- remove scaling before transversallium
- add function of no limbs on horizontal axis (not really tested...)
- compute tilt from ellipse model then apply
- compute scaling from ellipse width and hight of tilted image
- check after scaling if close to circle
- if not perform second scaling
- split function detect_edges and ellipse_fit
- add _log to log file to avoid firecapture settings overwrite (issue)
- add internal flag to debug and display graphics for ellipse_fit
- mise en fonction logme des prints from A&D Smiths
- conversion date de ficier ser en format lisible


Version 5 aout 2021 - OHP

- amelioration de la gestion du flag_noboards
- adjust threshold for edge detection
- adjust threshold for section detection (partial sun up/down or centered)
- fix: reimplement the clamp at 64000 to avoid overflow in image reconstruction
- ajout de SY/SX dans fichier txt


Version 17 juillet 2021

- modification code avec code de Doug & Andrew Smith pour acceleration stupefiante
    o vectorisation dans calcul extraction des intensités pour reconstruction du disque
- vectorisation dans le calcul de slant, qui est en fait un calcul de tilt
- transfer de lecture ser et calcul image mean dans la routine pour eviter de sauver le fichier _mean.fits
- ajout flag sfit_onlyfinal pour ne pas sauver fichiers fits intermediaires
- ajout angle de tilt manuel
- correction bug indice dans tableau fit si modele de polynome depasse la largeur de image

Version du 3 juillet

- Remplace circularisation algo des limbes par fit ellipse
- Conserve calcul de l'angle de slant par methode des limbes
- supprime ratio_fixe

Version 30 mai 2021

- modif seuil dans section flat sur NewImg pour eviter de clamper à background 1000
- mise en commentaire d'un ajout d'une detection des bords du disque solaire et d'un ajustement ce cercle apres
la circularisation en calculant le rayon a partir de la hauteur du disque

version du 20 mai

- ajout d'un seuil sur profil x pour eviter les taches trop brillantes 
en image calcium
seuil=50% du max
- ajout d'un ratio_fixe qui n'est pris en compte que si non egal a zero


"""

import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.interpolate import interp1d
import scipy.ndimage as ndimage
import os
#import time
from scipy.signal import savgol_filter
import cv2
import sys
import math
import config as cfg
from datetime import datetime

from Inti_functions import *
try :
    from serfilesreader.serfilesreader import Serfile
except ImportError : 
    from serfilesreader import Serfile


def solex_proc(serfile,Shift, Flags, ratio_fixe,ang_tilt, poly, data_entete,ang_P, solar_dict,param):
    """
    ----------------------------------------------------------------------------
    Reconstuit l'image du disque a partir de l'image moyenne des trames et 
    des trames extraite du fichier ser
    avec un fit polynomial
    Corrige de mauvaises lignes et transversallium
 
    basefich: nom du fichier de base de la video sans extension, sans repertoire
    shift: ecart en pixel par rapport au centre de la raie pour explorer 
    longueur d'onde decalée
    ----------------------------------------------------------------------------
    """
    #plt.gray()              #palette de gris si utilise matplotlib pour visu debug
    
    #t0=time.time()
    
    clearlog()
    #print (Shift)
    shift = Shift[0]
    shift_offdop=Shift[5]
    shift_dop1 = shift_offdop-Shift[1]
    shift_dop2 = shift_offdop+Shift[1]
    shift_cont = Shift[2]
    shift_offdop = Shift[5]

    shift_vol=Shift[3] # decacalage zeeman +/- 
    if Flags["WEAK"]:
        free_shift=Shift[3]
    if Flags["POL"]:
        shift_vol=Shift[3] # decacalage zeeman +/- 
        shift_zeeman=Shift[4] # decalage zeeman additionel
  
    flag_dopcont = Flags["DOPCONT"]
    flag_display = Flags["RTDISP"]
    sfit_onlyfinal = Flags["ALLFITS"]
    flag_pol = Flags['POL']
    flag_volume = Flags["VOL"]
    flag_weak = Flags["WEAK"]
    flag_flipRA = Flags["FLIPRA"]
    flag_flipNS = Flags["FLIPNS"]
    auto_crop = Flags["Autocrop"]
    # pour forcer les valeurs tilt et ratio
    flag_force = Flags["FORCE"]

    
    # cas difficile fente 
    try :
        pos_fente_min=int(param[0])
        pos_fente_max=int(param[1])
    except :
        pos_fente_min = 0
        pos_fente_max = 0

    
    geom=[]

    # gere ici le nombre de longueur d'onde aka decalages à gérer
    # decalage nul pour l'image de la raie spectrale
    # decalage de shift_dop pour le doppler, decalage de shift_cont pour celui du continuum sur flag_dopcont
    # serie de décalage de 1 pixel entre les bornes +/- shift_vol sur flag_volume
    
    #img_suff=(['.fits','_d1_'+str(shift_dop)+'.fits', '_d2_'+str(shift_dop)+'.fits','_cont_'+str(shift_cont)+'.fits'])
    
    if flag_dopcont :
        range_dec=[0,shift_dop1,shift_dop2,shift_cont]
        print('shift doppler 1 : ',shift_dop1)
        print('shift doppler 2 : ',shift_dop2)
    else:
        range_dec=[0]
        """
        if shift==0:
            range_dec=[0]
        else:
            range_dec=[int(shift)]
        """
    
    if flag_volume :
        range_dec1=np.arange(-shift_vol,0)
        range_dec2=np.arange(1,shift_vol+1)
        range_dec=np.concatenate(([0],range_dec1,range_dec2), axis=0)
    
    if flag_pol :
        range_dec=[0,-shift_vol,shift_vol]
        
    if flag_weak :
        range_dec=[0, Shift[1], Shift[2]]
        flag_dopcont=True
        
    kend=len(range_dec)
        
    #print ('nombre de traitements ',kend)
    WorkDir=os.path.dirname(serfile)+"/"
    os.chdir(WorkDir)
    base=os.path.basename(serfile)
    basefich='_'+os.path.splitext(base)[0]
    
    if shift != 0 :
        #add shift value in filename to not erase previous file
        basefich=basefich+'_dp'+str(int(shift)) # ajout '_' pour fichier en tete d'explorer
    
    # ouverture du fichier ser

    try:
        scan = Serfile(serfile, False)
    except:
        logme('Erreur ouverture fichier : '+serfile)
        
    FrameCount = scan.getLength()    #      return number of frame in SER file.
    Width = scan.getWidth()          #      return width of a frame
    Height = scan.getHeight()        #      return height of a frame
    dateSerUTC = scan.getHeader()['DateTimeUTC']  
    dateSer=scan.getHeader()['DateTime']
    bitdepth=scan.getHeader()['PixelDepthPerPlane']
    #ser_header=scan._readExistingHeader()
    #print(ser_header)
    if bitdepth==8:
        if cfg.LG == 1:
            logme('Acquisition 8 bits.')
        else:
            logme('Acquisition 8 bits.') 
        #sys.exit()
    logme (serfile)
    
    if cfg.LG == 1:
        logme ('Largeur et hauteur des trames SER : ' + str(Width)+','+str(Height))
        logme ('Nombre de trames : '+str( FrameCount))
    else:
        logme ('Width and Height of SER frames : ' + str(Width)+','+str(Height))
        logme ('Number of frames : '+str( FrameCount))
 
    try:
        # Date UTC
        # Correction bug fromtimestamp convertie en prenant en compte heure locale PC
        # Fonction utc ne tient pas compte du reglage pc
        f_dateSerUTC=datetime.utcfromtimestamp(SER_time_seconds(dateSerUTC))
        logme('SER date UTC :' + f_dateSerUTC.strftime('"%Y-%m-%dT%H:%M:%S.%f7%z"'))
        fits_dateobs=f_dateSerUTC.strftime('%Y-%m-%dT%H:%M:%S.%f7%z')
        # date ser du PC
        f_dateSer=datetime.utcfromtimestamp(SER_time_seconds(dateSer))
        logme('SER date local :' + f_dateSer.strftime('"%Y-%m-%dT%H:%M:%S.%f7%z"'))
        

    except:
        if cfg.LG == 1:
            logme('Erreur lecture date-time fichier SER')
        else :
            logme('Error reading date-time SER file')
    
    ok_flag=True              # Flag pour sortir de la boucle de lexture avec exit
    FrameIndex=1              # Index de trame    

    # fichier ser avec spectre raies verticales ou horizontales (flag true)
    if Width>Height:
        flag_rotate=True
        cam_height=Width
    else:
        flag_rotate=False
        cam_height=Height
    
    # initialisation d'une entete fits (etait utilisé pour sauver les trames individuelles
    hdr= fits.Header()
    hdr['SIMPLE']='T'
    hdr['BITPIX']=32
    hdr['NAXIS']=2
    if flag_rotate:
        hdr['NAXIS1']=Height
        hdr['NAXIS2']=Width
    else:
        hdr['NAXIS1']=Width
        hdr['NAXIS2']=Height
    hdr['BZERO']=0
    hdr['BSCALE']=1
    hdr['BIN1']=1
    hdr['BIN2']=1
    hdr['EXPTIME']=0
    try :
        hdr['DATE-OBS']=fits_dateobs
    except:
        fits_dateobs="2024-01-01T00:00:00"
        hdr['DATE-OBS']=hdr['DATE-OBS']=fits_dateobs
    hdr['OBSERVER']=data_entete[0]
    hdr['INSTRUME']=data_entete[1]
    #hdr['TELESCOP']=data_entete[1]
    hdr['SITELONG']=data_entete[2] #Longitude of the telescope in decimal degrees, could East as positive
    hdr['SITELAT']=data_entete[3]  #Latitude of the telescope in decimal degrees 
    hdr['OBJNAME']='Sun'
    hdr['CONTACT']=data_entete[4]
    hdr['WAVELNTH']=data_entete[5]
    hdr['PHYSPARA']= 'Intensity'
    hdr['WAVEUNIT']= -10
    filename_suffixe=data_entete[1]+'_'+ data_entete[6]+'_'+fits_dateobs.split('T')[0].replace('-','')+'_'+fits_dateobs.split('T')[1].split('.')[0].replace(':','')
    
    
    
    #debug
    #t0=float(time.time())
    
    """
    ---------------------------------------------------------------------------
    Calcul image moyenne de toutes les trames
    ---------------------------------------------------------------------------
    """
    
    if bitdepth == 8 :
        factor=256
    else:
        factor=1

    
    #initialize le tableau qui recevra l'image somme de toutes les trames
    mydata=np.zeros((hdr['NAXIS2'],hdr['NAXIS1']),dtype='uint64')
    kept_frame=0
    
    while FrameIndex < FrameCount and ok_flag:
        try :
            num = scan.readFrameAtPos(FrameIndex)
        except:
            print(FrameIndex)

        if flag_rotate:
            num=np.rot90(num)
        num=num*factor
        #ajoute les trames pour creer une image haut snr pour extraire
        #les parametres d'extraction de la colonne du centre de la raie et la
        #corriger des distorsions
        frame_mean=np.mean(num)
        if frame_mean>0 : # seuil arbitraire etait a 3000
            mydata=np.add(num,mydata)
            kept_frame=kept_frame+1
        
        #increment la trame et l'offset pour lire trame suivant du fichier .ser
        FrameIndex=FrameIndex+1
    
    #print('frame kept :', kept_frame, 'over ', FrameIndex)
    # calcul de l'image moyenne
    myimg=mydata/(kept_frame-1)             # Moyenne sur les kept frame
    myimg=np.array(myimg, dtype='uint16')   # Passe en entier 16 bits
    ih= hdr['NAXIS2']                     # Hauteur de l'image
    iw= hdr['NAXIS1']                     # Largeur de l'image
    myimg=np.reshape(myimg, (ih, iw))   # Forme tableau X,Y de l'image moyenne
    
    # sauve en fits l'image moyenne avec suffixe _mean
    savefich="Complements"+os.path.sep+basefich+'_mean'              
    SaveHdu=fits.PrimaryHDU(myimg,header=hdr)
    SaveHdu.writeto(savefich+'.fits',overwrite=True)
    
    
    #gestion taille des images Ser et Disk
    # my screensize is 1536x864 - harcoded as tk.TK() produces an error in spyder
    # plus petit for speed up
    screensizeH = (864-50)*0.8
    screensizeW = (1536)*0.8
    
    # gere reduction image png
    nw = screensizeW/iw
    nh = screensizeH/ih
    sc=min(nw,nh)

    if sc >= 1 :
        sc = 1
    
    #affiche image moyenne
    cv2.namedWindow('Ser', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Ser', int(iw*sc), int(ih*sc))
    cv2.moveWindow('Ser', 100, 0)
    cv2.imshow ('Ser', myimg)
    if cv2.waitKey(2000) == 27:  # exit if Escape is hit otherwise wait 2 secondes
           cv2.destroyAllWindows()
           sys.exit()
    
    cv2.destroyAllWindows()
    
    #affiche ou pas l'image du disque qui se contruit en temps reel
    #gain de temps si affiche pas avec flag_display

  
    """
    ----------------------------------------------------------------------------
    Calcul polynome ecart sur l'image moyenne
    ----------------------------------------------------------------------------
    """
    # detect up and down limit of the spectrum of the mean image
    y1,y2=detect_bord(myimg, axis=1, offset=5, flag_disk=False)
    
    # calcul profile spectral en bonus
    pro = bin_to_spectre(myimg,y1,y2)
    lamb = np.arange(0,iw)
    pro_lamb=np.column_stack((lamb,pro))

    
    if cfg.LG == 1:
        logme('Image moyenne - Limites verticales y1,y2 : '+str(y1)+' '+str(y2))
    else:
        logme('Mean Image - Vertical limits y1,y2 : '+str(y1)+' '+str(y2))
    
    PosRaieHaut=y1
    PosRaieBas=y2
    
    if (flag_weak and Flags["FREE_AUTOPOLY"]!=1)   or (flag_pol and Flags["ZEE_AUTOPOLY"]!=1) : 
        # on force le polynome
        a=poly[0]
        b=poly[1]
        c=poly[2]
        LineRecal=1
        if Flags["WEAK"]==1 and free_shift !=0 :
            c=poly[2]+free_shift
    else :
        # on calcul le polynome à partir des min de la raie du haut jusqu'en bas
        c_offset=0 # offset de la constante polynome si l'image est croppée pour detection fente
        try :
            if pos_fente_min != 0 :
                myimg = myimg[:,pos_fente_min:]
                c_offset=pos_fente_min
                if cfg.LG == 1 :
                    logme ("zone detection fente xmin : "+str(pos_fente_min))
                else :
                    logme ("slit detection zone xmin : "+ str(pos_fente_min))
            if pos_fente_max != 0:
                myimg = myimg[:,0:-int(iw)+pos_fente_max]
                if cfg.LG == 1 :
                    logme ("zone detection fente xmax : "+ str(pos_fente_max))
                else :
                    logme ("slit detection zone xmax : "+ str(pos_fente_max))
        except:
            pass
        
        
        # THE calcul pour obtenir la position de la fente sur la raie la plus sombre
        MinX=np.argmin(myimg, axis=1)
        # on reduit à la zone du spectre
        MinX=MinX[PosRaieHaut+30:PosRaieBas-30]
        IndY=np.arange(PosRaieHaut+30, PosRaieBas-30,1)
        LineRecal=1
        #best fit d'un polynome degre 2, les lignes y sont les x et les colonnes x sont les y
        p=np.polyfit(IndY,MinX,2)
        

        """
        # test ajustement pour centre raie >> pas ou peu de difference, abandon
        MinX_img=np.argmin(myimg, axis=1)
        # on reduit à la zone du spectre
        MinX=MinX_img[PosRaieHaut+30:PosRaieBas-30]
        posx=[]
        for j in range (PosRaieHaut+30, PosRaieBas-30) :
            posx.append (get_line_pos_absoption(myimg[j:j+1:][0],MinX_img[j],13))
        #ecart=np.array((MinX-posx), dtype='float64')
        IndY=np.arange(PosRaieHaut+30, PosRaieBas-30,1)
       
        #np.savetxt("c:/codepy/Simu/polymin.txt", ecart,fmt='%.2f',delimiter=',',newline='\n')

        LineRecal=1
        #best fit d'un polynome degre 2, les lignes y sont les x et les colonnes x sont les y
        p=np.polyfit(IndY, posx,2)
        """

        
        #calcul des x colonnes pour les y lignes du polynome
        a=p[0]
        b=p[1]
        c=p[2]+c_offset
        if Flags["WEAK"]==1 :
            if free_shift !=0 :
                c=p[2]+c_offset+free_shift
            else:
                c=p[2]+c_offset
        if not Flags["WEAK"] and not Flags["POL"]:
            if shift !=0:
                c= p[2]+c_offset+shift
                if cfg.LG == 1 :
                    logme("Inclut décalage de : " + str(shift))
                else :
                    logme("Include shift of : " + str(shift))
            
        
        # ajout du 11 Sept 2022
        poly=np.copy(p)
    
    if flag_pol :
        a=poly[0]
        b=poly[1]
        px=poly[2] # constante a y=0
        
        # Extraction zeeman
        # Calcul position X precise de la raie d'absortion d'où on extrait la polarisation
        # On extrait la ligne centrale dans myimg (au centre Y de l'image)
        posy = int(ih/2)
        line = myimg[posy:posy+1, 0: iw]
        # calcul constante à mi hauteur
        pos_line_mihauteur = a*posy**2 + b*posy + c
        print('pos_line_mihauteur ',pos_line_mihauteur)
        # On calcul la position précise de la raie à mi hauteur
        posx = get_line_pos_absoption(line[0], pos_line_mihauteur, 13)
        print('pos_line_mihauteur ajustee ',posx)
        # On calcule la constante actualisée du polynôme en incluant le decalage du a l'effet zeeman (zeeman wide)
        c = posx - a*posy**2 - b*posy + shift_zeeman
        #c = posx - a*posy**2 - b*posy 

              
    fit=[]
    #ecart=[]
    
    for y in range(0,ih):
        x=a*y**2+b*y+c
        deci=x-int(x)
        # gere si modele polynome de la fente depasse la dimension image iw
        # sinon code vectorisation va generer un pb d'indice 
        if x<iw-3:
            fit.append([int(x)-LineRecal,deci,y])
        else:
            fit.append([iw-3,0,y])
        #ecart.append([x-LineRecal,y])
    
    logme('Coef a*x2,b*x,c :'+"{:.4e}".format(a)+' '+str("{:.4e}".format(b))+' '+str("{:.2f}".format(c)))
    # 11 aout 22 ajout du retour en param des coef du polynome pour logger dans ini.yaml
    # 22 aout on ne veut plus sauver le polynome
    # polynome=[a,b,c]
    
    np_fit=np.asarray(fit)
    xi, xdec,y = np_fit.T
    xdec=xi+xdec+LineRecal
    xi=xi+LineRecal
    

    posX_min_slit=int(min(xi[PosRaieHaut], xi[PosRaieBas]))
    posX_max_slit=int(max(xi[PosRaieHaut], xi[PosRaieBas]))
    
    debug_poly=False
    if debug_poly :
        imgplot1 = plt.imshow(myimg)
        plt.scatter(xdec,y,s=0.1, marker='.', edgecolors=('red'))
        plt.show()
        #plt.scatter(min_ajust,IndY[0:-1],s=0.1, marker='.', edgecolors=('green'))
        plt.scatter(MinX,IndY,s=0.1, marker='.', edgecolors=('blue'))
        plt.scatter(xdec,y,s=0.1, marker='.', edgecolors=('red'))
        plt.show()

   
    
    # Test position de la fente décalée
    if len(range_dec)!=1 :   # si il y des decalages à prendre en compte
        shift_max=range_dec[len(range_dec)-1]
        shift_min=range_dec[1]

        if ((posX_min_slit-shift_max)<=1) or ((posX_max_slit+shift_max)>=iw):
            v=min(posX_min_slit-2, iw-posX_max_slit-1)
            logme('*******************************')
            if cfg.LG == 1:
                logme ('Warning !! Valeur de décalage trop importante')
                logme ('Valeur de décalage maximum:'+str(v))
                logme ('Image au centre la raie sera calculée à la place')
            else:
                logme ('Warning!! Shift value too large')
                logme ('Maximum shift value :'+str(v))
                logme ('Image at line center will be computed instead')
            logme('*******************************')
            range_dec=[0]
            kend=len(range_dec)
            
    else:
        shift_max=abs(range_dec[0])
        if ((posX_min_slit-shift_max)<=1) or ((posX_max_slit+shift_max)>=iw):
            v=min(posX_min_slit-2, iw-posX_max_slit-1)
            logme('*******************************')
            if cfg.LG == 1:
                logme ('Warning !! Valeur de décalage trop importante')
                logme ('Valeur de décalage maximum:'+str(v))
                logme ('Image au centre la raie sera calculée à la place')
            else:
                logme ('Warning!! Shift value too large')
                logme ('Maximum shift value :'+str(v))
                logme ('Image at line center will be computed instead')
            logme('*******************************')
            range_dec=[0]
            kend=len(range_dec)
     

    
    
    """
    ----------------------------------------------------------------------------
    ----------------------------------------------------------------------------
    Applique les ecarts a toute les lignes de chaque trame de la sequence
    ----------------------------------------------------------------------------
    ----------------------------------------------------------------------------
    """
     
    FrameIndex=1            # Index de trame

    if Width>Height:
        flag_rotate=True
        ih=Width
        iw=Height
    else:
        flag_rotate=False
        iw=Width
        ih=Height
        
    FrameMax=FrameCount
    
    Disk=[]
    
    # reduction de bruit - moyenne de 3 colonnes
    if len(range_dec)==1 and Flags["NOISEREDUC"] == 1 :
        range_dec_ref=range_dec
        range_dec=[0,-1,1]
    if Flags["WEAK"] and Flags["NOISEREDUC"] == 1 :
        range_dec_ref=range_dec
        range_dec=[0,-1,1,Shift[1]-1, Shift[1], Shift[1]+1,Shift[2]-1,Shift[2],Shift[2]+1]
    if Flags["POL"] and Flags["NOISEREDUC"] == 1 :
        range_dec_ref=range_dec
        range_dec=[0,-1,1,-shift_vol-1, -shift_vol, -shift_vol+1,shift_vol-1,shift_vol,shift_vol+1]

    
    for k in range_dec:
        Disk.append(np.zeros((ih,FrameMax), dtype='uint16'))
    
    if flag_display:
                   
        cv2.namedWindow('disk', cv2.WINDOW_NORMAL)
        FrameMax=FrameCount
        cv2.resizeWindow('disk', int(FrameMax*sc), int(ih*sc))
        cv2.moveWindow('disk', int(iw*sc)+1, 0)
        #initialize le tableau qui va recevoir les intensités spectrale de chaque trame
        
        
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.moveWindow('image', 0, 0)
        cv2.resizeWindow('image', int(iw*sc), int(ih*sc))

        
    # init vector to speed up from Andrew & Doug Smiths BUIL2 calcul poids interpol
    left_weights = np.ones(ih) - np.asarray(fit)[:, 1]
    right_weights = np.ones(ih) - left_weights
    
    ind_l=[]
    ind_r=[]
    
    for s in range_dec:
        
        ind_l.append((np.asarray(fit)[:, 0] + np.ones(ih) * (LineRecal + s)).astype(int))
        # teste des bornes pour indices left
        ind_l[len(ind_l)-1][(ind_l[len(ind_l)-1])>iw-1]=iw-1
        ind_l[len(ind_l)-1][(ind_l[len(ind_l)-1])<=0]=0
        
        ind_r.append((ind_l[len(ind_l)-1] + np.ones(ih)).astype(int))
        #teste des bornes pour indices right
        ind_r[len(ind_l)-1][(ind_r[len(ind_l)-1])>iw-1]=iw-1
        ind_r[len(ind_l)-1][(ind_r[len(ind_l)-1])<=0]=0
    
    
    # Lance la reconstruction du disk a partir des trames
    while FrameIndex < FrameCount :
        #t0=float(time.time())
        img=scan.readFrameAtPos(FrameIndex)
        img=img*factor
        
        # si fente orientée verticale on remet le spectre à l'horizontal
        if flag_rotate:
            img=np.rot90(img)
        
        # si flag_display vrai montre trame en temps reel
        if flag_display:
            cv2.imshow('image', img)
            if cv2.waitKey(1)==27:
                cv2.destroyAllWindows()
                sys.exit()
                
        # Boucle sur les decalages
        i=0
        for i in range(0,len(range_dec)): 
            # vector slit
            left_col = img[np.arange(ih), ind_l[i]]
            right_col = img[np.arange(ih), ind_r[i]]
            # prevent saturation overflow for saturated areas
            #left_col[left_col>64500]=64500
            #right_col[right_col>64500]=64500
        
            IntensiteRaie = (left_col*left_weights + right_col*right_weights)

            
            # guillaume
            """
            #test point chaud
            #original=np.copy(IntensiteRaie)
            gr=np.divide(IntensiteRaie,savgol_filter(IntensiteRaie,41, 3))
            hot=np.argwhere(gr>1.1)
            a= ndimage.median_filter(IntensiteRaie, size=3)
            #IntensiteRaie=np.where(IntensiteRaie <th, a, IntensiteRaie)
            IntensiteRaie[hot]=a[hot]
            """
            
            # Ajoute au tableau disk 
            Disk[i][:,FrameIndex]=IntensiteRaie
            
        # Display reconstruction of the disk refreshed every 30 lines
        refresh_lines=int(20)
        if flag_display and FrameIndex %refresh_lines ==0:
            disk_display=[]
            disk_display=np.copy(Disk[0])*2
            cv2.imshow ('disk', disk_display)
            if cv2.waitKey(1) == 27:             # exit if Escape is hit
                     cv2.destroyAllWindows()
                     sys.exit()
    
        FrameIndex=FrameIndex+1
   
    # reduction de bruit - moyenne de 3 colonnes
    if (kend == 1 and Flags["NOISEREDUC"] ==1)  or (Flags["NOISEREDUC"]== 1 and Flags["WEAK"]) or (Flags["NOISEREDUC"]== 1 and Flags["POL"]) :
        d0=np.array(Disk[0], dtype='float64')
        d1=np.array(Disk[1], dtype='float64')
        d2=np.array(Disk[2], dtype='float64')
        disk_reducnoise = (d0+d1*0.5+d2*0.5) / 2
        Disk[0]=np.array(disk_reducnoise, dtype='uint16')
        if Flags["WEAK"] or Flags["POL"] :
            d3=np.array(Disk[3], dtype='float64')
            d4=np.array(Disk[4], dtype='float64')
            d5=np.array(Disk[5], dtype='float64')
            disk_reducnoise = (d3*0.5+d4+d5*0.5) / 2
            Disk[1]=np.array(disk_reducnoise, dtype='uint16')
            d6=np.array(Disk[6], dtype='float64')
            d7=np.array(Disk[7], dtype='float64')
            d8=np.array(Disk[8], dtype='float64')
            disk_reducnoise = (d6*0.5+d7+d8*0.5) / 2
            Disk[2]=np.array(disk_reducnoise, dtype='uint16')
            del Disk[3:]


        range_dec = range_dec_ref
        kend=len(range_dec)
        if cfg.LG == 1 :
            logme("Option Reduction de Bruit")
        else :
            logme("Noise reduction option")
    
    
    # Sauve fichier disque reconstruit pour affichage image raw en check final
    hdr['NAXIS1']=FrameCount-1
    img_suff=[]
    for i in range(0,kend):
        DiskHDU=fits.PrimaryHDU(Disk[i],header=hdr)
        if i>0 : 
            img_suff.append("_dp"+str(range_dec[i]))
        else:
            img_suff.append('')
            DiskHDU.writeto("Complements"+os.path.sep+basefich+img_suff[i]+'_raw.fits',overwrite='True')

    if flag_display:
        cv2.destroyAllWindows()
        
    #t1=time.time()
    #print('fin image raw :', t1-t0)
    #t0=time.time()
    
    frames=[]
    msg=[]
    if cfg.LG == 1:
        msg.append('...image centre...')
    else:
        msg.append('...center image...')

    if kend!=0 :
        for i in range(1,kend) :
            if cfg.LG == 1:
                msg.append('...décalage image '+str(range_dec[i])+"...")
            else:
                msg.append('...image shift '+str(range_dec[i])+"...")

    #msg=('...image centre...', '...image Doppler 1...', '...image Doppler 2...', '...image continuum...')
    
    
    """
    -------------------------------------------------------------------------
    -------------------------------------------------------------------------
    Boucle sur les disques de la liste de decalage range_dec
    -------------------------------------------------------------------------
    -------------------------------------------------------------------------
    """
    
    for k in range(0,kend):
        
        logme(' ')
        logme(msg[k])
        """
        --------------------------------------------------------------------
        Calcul des mauvaises lignes et de la correction geometrique
        --------------------------------------------------------------------
        """
        # guillaume
        # elimine premiere colonne qui serait à zéro
        #Disk[k][:,0]=4000
        
        iw=Disk[k].shape[1]
        ih=Disk[k].shape[0]
        img=Disk[k]
        
    
    
        y1,y2=detect_bord (img, axis=1,offset=5, flag_disk=True)    # bords verticaux
        
        #detection de mauvaises lignes
        
        # somme de lignes projetées sur axe Y
        #img_blur=cv2.GaussianBlur(img,(3,3),0)
        ysum_img=np.mean(img,1)
        
        
        # ne considere que les lignes du disque avec marge de 15 lignes 
        marge=15
        ysum=ysum_img[y1+marge:y2-marge]
        
        # choix methode par fit polynome et division
        # ou detection des lignes et mediane 
        methode_poly= False
        debug=False
 
        # filtrage sur fenetre de 31 pixels, polynome ordre 3 (etait 101 avant)
        yc=savgol_filter(ysum,41, 3)
        """
        #polynome
        xval=np.arange(0,y2-y1-2*marge,1)
        p = np.polyfit(xval,ysum,6)
        fit=[]
        for x in xval:
            fitv = p[0]*x**6+p[1]*x**5+p[2]*x**4+p[3]*x**3+p[4]*x**2+p[5]*x+p[6]
            fit.append(fitv)
        #print('Coef poly ',p)
        #fp = ysum-np.array(fit)
        yc=np.array(fit)
        """
        if debug :
            # affichage debug
            plt.plot(yc)
            plt.plot(ysum)
            plt.show()
      
    
        # divise le profil somme par le profil filtré pour avoir les hautes frequences
        hcol1=np.divide(ysum,yc)
        hcol=np.copy(hcol1)


        # met à zero les pixels dont l'intensité est inferieur à 1.03 (3%)
        #hcol[abs(hcol1-1)<= 0.02]=0
        hcol[(hcol1-1)>=-0.02]=0

        if debug :
            # affichage debug
            plt.plot(hcol1)
            plt.plot(hcol)
            plt.show()

        # tableau de zero en debut et en fin pour completer le tableau du disque
        a=[0]*(y1+marge)
        b=[0]*(ih-y2+marge)
        hcol=np.concatenate((a,hcol,b))
        

        # creation du tableau d'indice des lignes a corriger
        l_col=np.where(hcol!=0)
        listcol=l_col[0]
        #print(listcol)
        
        # doit etre abandonné
        # demarre a x constant et gain trop fort
        # et poly ne convient pas pour disque tronqué
    
        if methode_poly:
            # on ne clamp pas le profil
            hcol=1+((ysum-yc)/yc)
            hcol[hcol-1>-0.03]=1
            # tableau de zero en debut et en fin pour completer le tableau du disque
            a=[1]*(y1+marge)
            b=[1]*(ih-y2+marge)
            hcol=np.concatenate((a,hcol,b))
            
            if debug :
                #affichage debug
                plt.plot(hcol)
                plt.title('hcol_poly')
                plt.show()
            
            # Geénère tableau image de flat 
            flat_hf=[]
            for i in range(0,iw):
                flat_hf.append(hcol)
                
            np_flat_hf=np.asarray(flat_hf)
            flat_hf = np_flat_hf.T
            
            # Evite les divisions par zeros...
            flat_hf[flat_hf==0]=1
            
            # somme des lignes mauvaises le log de x
            #hsum=np.mean(img[listcol],0)
            m=np.mean(img,0)
            hsum=np.max(m)/m
            hsum[hsum>2]=1
            #hsum=savgol_filter(hsum,31, 3)
            
            if debug :
                plt.plot(hsum)
                plt.show()
            
            # flat pondere en x 
            
            for i in listcol :
                flat_hf[i,:]=flat_hf[i,:]/hsum
               
            if debug :
                # affichage debug
                plt.imshow(flat_hf)
                plt.show()
                
            # Divise image par le flat
            b=np.divide(img,flat_hf)
            img=np.array(b, dtype='uint16')
            
        else :
            origimg=np.copy(img)
            # correction de lignes par filtrage median 13 lignes, empririque
            if debug : print(listcol)
            lines=[]
            lines_collection=[]
            try :
                lines.append(listcol[0])
                for i in range(1,len(listcol)-1):
                    if listcol[i]-listcol[i-1] ==1 :
                        lines.append(listcol[i])
                    else :
                        lines_collection.append(lines)
                        lines=[]
                        lines.append(listcol[i])
                if debug : print(lines_collection)
            except:
                pass
            
            for c in listcol:
                m=origimg[c-11:c+10,] #now refer to original image
                # calcul de la mediane sur 10 lignes de part et d'autres
                # suppression de 2 colonnes en debut et fin qui peuvent être à zéro
                s=np.median(m[:,2:-2],0)
                
                #on prepare un patch de 2 valeurs 
                a=[m[0][3],m[0][-3]]
                #on ajoute les patchs
                s=np.concatenate((a,s,a))
                
                #on remplace la ligne defectueuse
                #s=0 #pour visualiser la ligne idetifiée comme defectueuse
                img[c:c+1,]=s #fix bug ecart une ligne
            
          
            """
            for c in lines_collection :
                d=2
                m1 = origimg[c[0]-d,]
                m2 = origimg[c[len(c)-1]+d,]
                m=np.array([m1,m2])
                # suppression de 2 colonnes en debut et fin qui peuvent être à zéro
                s=np.median(m[:,2:-2],0)
                #on prepare un patch de 2 valeurs 
                a=[s[0],s[-1]]
                #on ajoute les patchs
                s=np.concatenate((a,s,a))
                
                #on remplace la ligne defectueuse
                #s=0
                for i in c :
                    img[i:i+1,]=s #fix bug ecart une ligne
            """ 
        debug=False
        if debug :
            # affichage debug
            plt.plot(ysum_img)
            plt.plot(np.mean(img,1))
            plt.title('avant-apres')
            plt.show()
            # test sauve image apres correction pour debug
            DiskHDU=fits.PrimaryHDU(img,header=hdr)
            DiskHDU.writeto(basefich+img_suff[k]+'_line.fits',overwrite='True')
    
        
        """
        --------------------------------------------------------------
        Correction de flat - basse freq
        --------------------------------------------------------------
        """
        frame=np.copy(img)
        #plt.imshow(frame)
        #plt.show()
        
        debug=False
        
        # on cherche la projection de la taille max du soleil en Y
        y1,y2=detect_bord(frame, axis=1,offset=0, flag_disk=True) 
        #x1,x2=detect_bord(frame, axis=0,offset=0)
        if cfg.LG == 1:
            logme('Limites verticales y1,y2 : '+str(y1)+' '+str(y2))
        else:
            logme('Vertical limits y1,y2 : '+str(y1)+' '+str(y2))
        
    
        flag_nobords=detect_noXlimbs(frame)
        
        # si mauvaise detection des bords en x alors on doit prendre toute l'image
        if flag_nobords:
            ydisk=np.median(img,1)
            offset_y1=0
            offset_y2=0
        else:
    
            seuil_haut=np.percentile(frame,97) 
            myseuil=seuil_haut*0.5 # seuillage pour segmentation disque solaire
            
            if cfg.LowDyn :
                #guillaume
                myseuil=seuil_haut*0.7 # faible dynamique, seuil pour segmenter le disque solaire was 0.6
                print(seuil_haut, myseuil)
            
            # filtre le profil moyen en Y en ne prenant que le disque
            # pixel est dans disque si intensité supérieure à la moitié du percentile à 97%
            # value where 97% of the pixels are lower
            ydisk=np.empty(ih+1)
            offset_y1=0
            offset_y2=0
            for j in range(0,ih):
                temp=np.copy(frame[j,:])
                temp=temp[temp>myseuil]
                if len(temp)!=0:
                    ydisk[j]=np.median(temp)
                else:
                    # manage poor disk intensities inside disk
                    # avoid line artefact
                    if j>=y1 and j<=y2:
                        if abs(j-y1) < abs(j-y2):
                            offset_y1=offset_y1+1
                        else:
                            offset_y2=offset_y2-1

                    else:
                        ydisk[j]=1

    
        # ne prend que le profil des intensités pour eviter les rebonds de bords
        
        # manage flat range application
        y1=y1+offset_y1
        y2=y2+offset_y2
        
        ToSpline= ydisk[y1:y2]
        
        # traitement du cas ou le disque est saturé - cas de la couronne solaire raie verte
        moy_profil=np.mean(ToSpline)
        #print ('moy profil : ', moy_profil)
        if moy_profil <64000 :
        
            winterp=301
            if len(ToSpline)<301 :
                
                if cfg.LG == 1:
                    logme('Hauteur du disque anormalement faible : '+str(y1)+' '+str(y2))
                else:
                    logme('Disk Height abnormally low : '+str(y1)+' '+str(y2))
                
                if len(ToSpline)%2==0 :
                    winterp=len(ToSpline)-10+1
                else:
                    winterp=len(ToSpline)-10
            
            Smoothed2=savgol_filter(ToSpline,winterp, 3) # window size, polynomial order
        

            if debug:
                plt.plot(ToSpline)
                #plt.plot(Smoothed)
                plt.plot(Smoothed2)
                plt.show()
     
            
            # Divise le profil reel par son filtre ce qui nous donne le flat
            hf=np.divide(ToSpline,Smoothed2)
               
            # Elimine possible artefact de bord
            hf=hf[5:-5]
            
            #reconstruit le tableau du profil complet an completant le debut et fin
            a=[1]*(y1+5)
            b=[1]*(ih-y2+5)
            hf=np.concatenate((a,hf,b))
            
            #Smoothed=np.concatenate((a,Smoothed,b))
            ToSpline=np.concatenate((a,ToSpline,b))
            Smoothed2=np.concatenate((a,Smoothed2,b))
            
            if debug:
                plt.plot(ToSpline)
                plt.plot(Smoothed2)
                plt.show()
                
                plt.plot(hf)
                plt.show()
     
            # Génère tableau image de flat 
            flat=[]
            for i in range(0,iw):
                flat.append(hf)
                
            np_flat=np.asarray(flat)
            flat = np_flat.T
            
            # Evite les divisions par zeros...
            flat[flat==0]=1
            
            if debug:
                plt.imshow(flat)
                plt.show()
    
            # Divise image par le flat
            BelleImage=np.divide(frame,flat)
            BelleImage[BelleImage>65535]=65535 # bug saturation
            frame=np.array(BelleImage, dtype='uint16')
    
            if debug:
                # sauvegarde de l'image deflattée
                #DiskHDU=fits.PrimaryHDU(frame,header=hdu.header)
                DiskHDU=fits.PrimaryHDU(frame,header=hdr)
                DiskHDU.writeto(basefich+img_suff[k]+'_flat.fits',overwrite='True')
            
        else:
            # pas de correction de flat on reprend l'image
            print ("pas de correction de flat, profil saturé")
            
        
        # on sauvegarde les bords haut et bas pour les calculs doppler et cont
        if k==0: 
            y1_img=y1
            y2_img=y2
        
        
       
        """
        -----------------------------------------------------------------------
        Calcul du tilt si on voit les bords du soleil
        sinon on n'applique pas de correction de tilt,
        on applique un facteur SY/SX=0.5
        et on renvoit a ISIS
        -----------------------------------------------------------------------
        """
        
        img2=np.copy(frame)
        EllipseFit=[]
        crop=0
        
        if k != 0:
            flag_force = True
    
        #if float(ang_tilt)==0:
              
       
  
        if not(flag_nobords):
            
            # methode fit ellipse pour calcul de tilt
            # zone d'exclusion des points contours zexcl en pourcentage de la hauteur image 
            X = detect_edge (img2, zexcl=0.1, crop=crop, disp_log=False)
            EllipseFit,XE=fit_ellipse(img2, X,disp_log=False)
            
            # correction de tilt uniquement si on voit les limbes droit/gauche
            # trouve les coordonnées y des bords du disque dont on a les x1 et x2 
            # pour avoir les coordonnées y du grand axe horizontal
            # on cherche la projection de la taille max du soleil en Y et en X

            if y1<=10 :
                background= np.percentile(img2, 15)
                #print("Percentile h 15: ",background)
                img_dark1=np.full((2,iw), background)
            else :
                #img_dark1=img2[0:y1-10,]
                img_dark1=img2[0:10,]
            if y2>ih-10 :
                background= np.percentile(img2, 15)
                #print("Percentile b 15: ",background)
                img_dark2=np.full((2,iw), background)

            else :
                #img_dark2=img2[y2+10:,]
                img_dark2=img2[-10:,]
                
            img_dark=np.concatenate((img_dark1,img_dark2))
            img_fill1=np.mean(img_dark1,axis=0)
            img_fill2=np.mean(img_dark2, axis=0)
            background= np.percentile(img_dark, 55) # was 55
            #background= np.percentile(img2, 15)
            #print("zone fond: ",background)

           
            # methode calcul angle de tilt avec XE ellipse fit
            elX=XE.T[0]
            elY=XE.T[1]
            el_x1=np.min(elX)
            el_x2=np.max(elX)
            el_ind_x1= np.argmin(elX)
            el_ind_x2= np.argmax(elX)
            el_y_x1=elY[el_ind_x1]
            el_y_x2=elY[el_ind_x2]
            #print('ellipse x1,x2 : ', el_x1, el_x2)
            #print('ellipse y_x1,y_x2 : ', el_y_x1, el_y_x2)
            
            if k==0 :
                el_x1_img=el_x1
                el_x2_img=el_x2
                
            #if float(ang_tilt)==0:
            if flag_force != True :
                # calcul l'angle de tilt ellipse
                dy=(el_y_x2-el_y_x1)
                dx=(el_x2-el_x1)
                TanAlpha=(-dy/dx)
                AlphaRad=math.atan(TanAlpha)
                AlphaDeg=math.degrees(AlphaRad)
            
        
            else :
                AlphaDeg=float(ang_tilt)
                AlphaRad=math.radians(AlphaDeg)
                TanAlpha=math.tan(AlphaRad)
                
            
            if cfg.LG == 1:
                logme('Angle de Tilt : '+"{:+.4f}".format(AlphaDeg))
            else:
                logme('Tilt angle : '+"{:+.4f}".format(AlphaDeg))
            
            #on force l'angle de tilt pour les prochaines images
            ang_tilt=AlphaDeg
           
            
            # ne teste plus si correction de tilt si angle supérieur a 0.2 degres
            if abs(AlphaDeg)>= 0.0 :
                #decale lignes images par rapport au centre
                colref=round((el_x1+el_x2)/2)
                dymax=int(abs(TanAlpha)*(colref))
                #print ("background tilt : ", background)
                #background= np.percentile(img2, 5)
                #a=np.full((dymax,iw), background)
                #b=a
                a=np.atleast_2d(img_fill1).repeat(repeats=dymax, axis=0)
                b=np.atleast_2d(img_fill2).repeat(repeats=dymax, axis=0)
                img2=np.concatenate((a,img2,b))
                ih=ih+dymax*2
                crop=int(abs(TanAlpha)*iw)
                NewImg=np.empty((ih,iw))
                for i in range(0,iw):
                    x=img2[:,i]
                    NewImg[:,i]=x
                    y=np.arange(0,ih)
                    dy=(i-colref)*TanAlpha
                    ycalc = y + np.ones(ih)*dy # improvements TheSmiths
                    f=interp1d(ycalc,x,kind='linear',fill_value=(background,background),bounds_error=False)
                    xcalc=f(y)
                    NewLine=xcalc
                    NewImg[:,i]=NewLine
                NewImg[NewImg<=0]=0  #modif du 19/05/2021 etait a 1000
                img2=np.copy(NewImg)
                if dymax != 0 :
                    img2[:dymax,]=a
                    img2[-dymax:,]=b

            else:
                if cfg.LG == 1:
                    logme('Alignement meilleur que 0.2°, correction de tilt non nécessaire.')
                else:
                    logme('Alignment better than 0.2°, tilt correction not necessary.')
                   
        sfit_onlyfinal=False
        
        if sfit_onlyfinal==False:
            # sauvegarde en fits de l'image tilt
            img2=np.array(img2, dtype='uint16')
            DiskHDU=fits.PrimaryHDU(img2,header=hdr)
            DiskHDU.writeto(basefich+img_suff[k]+'_tilt.fits', overwrite='True')
        
        """
        ----------------------------------------------------------------
        Calcul du parametre de scaling SY/SX
        ----------------------------------------------------------------
        """
        
       
        
        if flag_nobords:
            ratio_fixe=0.5
            
        if k==1:
            ratio_fixe=ratio_fixe_d1
            
        #if ratio_fixe==0:
        if flag_force != True and not flag_nobords:
            # methode fit ellipse pour calcul du ratio SY/SX
            X = detect_edge (img2, zexcl=0.1,crop=crop, disp_log=False)
            EllipseFit,XE=fit_ellipse(img2, X,disp_log=False)
            
            ratio=EllipseFit[2]/EllipseFit[1]
       
            
            if cfg.LG == 1:
                logme('Facteur d\'échelle SY/SX : '+"{:+.4f}".format(ratio))
            else:
                logme('Scaling SY/SX : '+"{:+.4f}".format(ratio))
            
            NewImg, newiw=circularise2(img2,iw,ih,ratio)
        
        else:
            # Forcer le ratio SY/SX
            NewImg, newiw=circularise2(img2,iw,ih,ratio_fixe)

            if cfg.LG == 1:
                logme('Facteur d\'échelle fixe SY/SX : '+"{:+.4f}".format(ratio_fixe))
            else:
                logme('Fixed Scaling SY/SX : '+"{:+.4f}".format(ratio_fixe))

        
        if k==0:
            #if ratio_fixe==0:
            if flag_force != True and not flag_nobords:
                ratio_fixe_d1=ratio
            else:
                ratio_fixe_d1=ratio_fixe
        
        
        frame=np.array(NewImg, dtype='uint16')
        #print('shape',frame.shape)
        
        """
        if sfit_onlyfinal==False:
            # sauvegarde en fits de l'image rescaled
            hdr['NAXIS1']=frame.shape[1]
            hdr['NAXIS2']=frame.shape[0]
            #img2=np.array(frame, dtype='uint16')
            DiskHDU=fits.PrimaryHDU(frame,header=hdr)
            DiskHDU.writeto(basefich+"_"+str(k)+'_scaled.fits', overwrite='True')
        """
       
        """
        ----------------------------------------------------------------------
        Sanity check, second iteration et calcul des parametres du disk occulteur
        ----------------------------------------------------------------------
        """
        if flag_nobords:
            cercle=[0,0,0,0]
            r=0
            
        else:
            # fit ellipse pour denier check
            # zone d'exclusion des points contours zexcl en pourcentage de la hauteur image 
    
            X = detect_edge (frame, zexcl=0.1, crop=crop, disp_log=False)
            EllipseFit,XE=fit_ellipse(frame, X, disp_log=False)
            
            ratio=EllipseFit[2]/EllipseFit[1]
            
            if abs(ratio-1)>=1 and k==0 and ratio_fixe==0: #0.01
                logme('Ratio iteration2 :'+ str(ratio))
                NewImg, newiw=circularise2(frame,newiw,ih,ratio)
                frame=np.array(NewImg, dtype='uint16')
                X= detect_edge (frame, zexcl=0.1,crop=crop, disp_log=False)
                EllipseFit,XE=fit_ellipse(frame, X, disp_log=False)
                
            if k==0:
                xc=round(EllipseFit[0][0])
                yc=round(EllipseFit[0][1])
                wi=round(EllipseFit[1]) # diametre
                he=round(EllipseFit[2])
                cercle=[xc,yc,wi,he]              
                
                #if ratio_fixe==0 :
                if flag_force != True :
                    cercle=[xc,yc,wi,he]

                r=round(min(wi-5,he-5)-4)
                if cfg.LG == 1:
                    logme('Final SY/SX :'+ "{:+.3f}".format(he/wi))
                    #logme('Centre xc,yc et rayon : '+str(xc)+' '+str(yc)+' '+str(int(r)))
                else:
                    logme('Final SY/SX :'+ "{:+.3f}".format(he/wi))
                    #logme('xc,yc center and radius : '+str(xc)+' '+str(yc)+' '+str(int(r)))
    
        
        
        if k==0:
            cercle0=np.copy(cercle)
            geom.append(ratio_fixe_d1)
            geom.append(ang_tilt)
            

            
        x0=cercle0[0]
        y0=cercle0[1]
        wi=round(cercle0[2])
        he=round(cercle0[3])

        
        
        sensNS_corr_ang_tilt=1
        sensEW_corr_ang_tilt=1
             
        # retourne horizontalement image si flag de flip est vrai
        if flag_flipRA:
             frame=np.flip(frame, axis=1)
             # il faut recentrer le centre du disque en X...
             x0=frame.shape[1]-x0
             cercle[0]=x0
             #if k==0 : cercle0[0]=x0
             sensEW_corr_ang_tilt=-1
             if cfg.LG == 1:
                 logme("Inversion EW")
             else:
                 logme("EW inversion")
         
        if flag_flipNS:
             frame=np.flip(frame, axis=0)
             # il faut recentrer le centre du disque en Y...
             y0=frame.shape[0]-y0-1
             cercle[1]=y0
             #if k==0: cercle0[1]=y0
             sensNS_corr_ang_tilt=-1
             if cfg.LG == 1:
                 logme("Inversion NS")
             else:
                 logme("NS inversion")
          
        """
        -----------------------------------------------------------------------
        Correction rotation angle P et tilt
        -----------------------------------------------------------------------
        """
        # corrige angle P de rotation, par defaut il sera égal à zero
        # pour l'instant on applique la valeur dans le champs Angle P
        # on corrige aussi de l'angle de tilt dans geom[1]
        
        # recalcul angle de tilt apres circularisation
        # calcule angle de tilt apres rescaling
        
        if geom[1] != 0 :
            Arad=math.radians(geom[1])
            TanA=math.tan(Arad)
            TanA_scaled= TanA/geom[0]
            A2Rad=math.atan(TanA_scaled)
            Tilt_scaled_Deg=math.degrees(A2Rad)
        else :
            Tilt_scaled_Deg = 0
        
        angle_rot = ang_P+sensNS_corr_ang_tilt*sensEW_corr_ang_tilt*Tilt_scaled_Deg

        
        if angle_rot !=0 :
            if cfg.LG == 1:
                logme("Angle de correction : "+ str(angle_rot))
                logme("Angle P utilisé : "+str(ang_P))
            else:
                logme("Correction angle : "+ str(angle_rot))
                logme("P angle used : "+str(ang_P))
            
            # on copie l'image de travail et on recupere hauteur et largeur
            fr_avant_rot=np.copy(frame)
            hh,ww=fr_avant_rot.shape[:2]
            
            #calcul de bande max liée a la rotation d'angle
            RotRad=math.radians(angle_rot)
            TanRot=np.tan(RotRad)
            hy=int(abs(TanRot*ww*0.5))
           
            
    
            # y0 inferieur à hauteur on padde des bandes haut et bas pour ne pas cropper apres rotation
            if y0<he :
                #print('hauteur bande auto : ', hy)
                #print('hauteur fixe : ', abs(he+hy-y0))
                #hy=50
                """
                pad_area= np.ones((abs(he+hy-y0),ww))
                fr_avant_rot=np.concatenate((pad_area,fr_avant_rot,pad_area))
                cercle[1]=he+hy
                cercle0[1]=he+hy
                """
                pad_area= np.ones((hy,ww))
                fr_avant_rot=np.concatenate((pad_area,fr_avant_rot,pad_area))
                cercle[1]=y0+hy
                #if k==0: cercle0[1]=y0+hy
                
                        
            # et on met a jour dimensions de l'image avant rotation
            h,w=fr_avant_rot.shape[:2]
            # calcul de la matrice de rotation, angle en degre
            rotation_mat=cv2.getRotationMatrix2D((int(cercle[0]),int(cercle[1])),float(angle_rot),1.0)
                        
            # application de la matrice de rotation
            fr_rot=cv2.warpAffine(fr_avant_rot,rotation_mat,(w,h),flags=cv2.INTER_LINEAR)
            frame=np.array(fr_rot, dtype='uint16')
        else :
            h, w = frame.shape
            

        if cfg.LG == 1:
            logme('Centre xc,yc et rayon : '+str(cercle[0])+' '+str(cercle[1])+' '+str(int(r)))
        else:
            logme('xc,yc center and radius : '+str(cercle[0])+' '+str(cercle[1])+' '+str(int(r)))
        
        # on croppe et on centre
        # Hauteur du capteur est dans dam_Heigth=scan.height
        
        debug_crop=False
        #auto_crop=True
        
        if flag_nobords :
            auto_crop=False
            cercle=[0,0,0,0]
        
        if auto_crop :
            
            #cercleC, crop_he, crop_wi, crop_img=auto_crop_img(cam_height, h, w, frame, cercle0, debug_crop)
            cercleC, crop_he, crop_wi, crop_img=auto_crop_img(cam_height, h, w, frame, cercle, debug_crop, param)
            if crop_he==0 :
                auto_crop=False
                if cfg.LG == 1:
                    print("Erreur AutoCrop")
                else:
                    print ("Error AutoCrop")
        
        # doit changer les coord du centre
        
        if auto_crop :
            
            # Sauvegarde en fits de l'image finale
            frame=np.array(crop_img, dtype='uint16')
            hdr['NAXIS1']=crop_wi
            hdr['NAXIS2']=crop_he
            
            hdr['INTI_XC'] = cercleC[0]
            hdr['INTI_YC'] = cercleC[1]
            hdr['INTI_R'] = cercleC[2]
            # duplication keywords pour BASS2000
            hdr['CENTER_X'] = cercleC[0]
            hdr['CENTER_Y'] = cercleC[1]
            hdr['SOLAR_R'] = cercleC[2]
            
            # recalcul des coordonnées haut et bas du disque
            y1_img,y2_img = detect_bord(frame, axis=1, offset=0,flag_disk=True)
            x1_img,x2_img = detect_bord(frame, axis=0, offset=0,flag_disk=True)
            hdr['INTI_Y1'] = y1_img
            hdr['INTI_Y2'] = y2_img
            hdr['INTI_X1'] = x1_img
            hdr['INTI_X2'] = x2_img
        
        else :
            # Sauvegarde en fits de l'image finale
            #cercleC=cercle0
            cercleC=cercle
            frame=np.array(frame, dtype='uint16')
            hdr['NAXIS1']=newiw

            hdr['INTI_XC'] = cercle[0]
            hdr['INTI_YC'] = cercle[1]
            hdr['INTI_R'] = cercle[2]
            # duplication keywords pour BASS2000
            hdr['CENTER_X'] = cercle[0]
            hdr['CENTER_Y'] = cercle[1]
            hdr['SOLAR_R'] = cercle[2]
            
            # recalcul des coordonnées haut et bas du disque
            y1_img,y2_img = detect_bord(frame, axis=1, offset=0,flag_disk=True)
            x1_img,x2_img = detect_bord(frame, axis=0, offset=0,flag_disk=True)
            hdr['INTI_Y1'] = y1_img
            hdr['INTI_Y2'] = y2_img
            hdr['INTI_X1'] = x1_img
            hdr['INTI_X2'] = x2_img

        
        hdr['FILENAME']= basefich+img_suff[k]+'_'+filename_suffixe+".fits"
        
        if auto_crop :
            if cfg.LG == 1:
                logme('Centre xcc,ycc et rayon : '+str(cercleC[0])+' '+str(cercleC[1])+' '+str(int(r)))
                logme('Coordonnées y1,y2 et x1,x2 disque : '+str(y1_img)+','+str(y2_img)+' '+str(x1_img)+','+str(x2_img))
            else:
                logme('xcc,ycc center and radius : '+str(cercleC[0])+' '+str(cercleC[1])+' '+str(int(r)))
                logme('Coordinates y1,y2 and x1,x2 disk : '+str(y1_img)+','+str(y2_img)+' '+str(x1_img)+','+str(x2_img))
        try :
            print('solar data : ', solar_dict)
            hdr['SEP_LAT']=float(solar_dict['B0'])
            hdr['SEP_LON']=float(solar_dict['L0'])
            hdr['SOLAR_P']=float(ang_P)
            hdr['CAR_ROT']=float(solar_dict['Carr'])
        except:
            pass
        
        # sauve images _recon
        DiskHDU=fits.PrimaryHDU(frame,header=hdr)
        DiskHDU.writeto(basefich+img_suff[k]+'_recon.fits', overwrite='True')
        if flag_weak != True and flag_pol != True and data_entete[6] !='Manual':
            DiskHDU.writeto("BASS2000"+os.path.sep+hdr['FILENAME'], overwrite='True')
     
        with  open(basefich+'_log.txt', "w") as logfile:
            logfile.writelines(mylog)
        
        # sauve profile en dat
        if k==0 :
            
            np.savetxt("Complements"+os.path.sep+basefich+'.dat',pro_lamb)
        
        # ajoute l'image a la liste
        frames.append(frame)
        

        
        
    return frames, hdr, cercleC, range_dec, geom, poly
    