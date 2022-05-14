# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 11:42:32 2020

@author: valerie desnoux


------------------------------------------------------------------------


Version du 28 avril 2022 - paris
- mise en commentaire malheureuse de la zone de filtrage disque qui n'excluait plus les bords

version du 23 avril 2022 - Paris
- factorisation des tableaux indices left et rigth
- ajout de calcul d'une sequence doppler
- ajout de la fonction magnetogramme
- creation d'une version anglaise par swith LG a la compil
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
import os
#import time
from scipy.signal import savgol_filter
import cv2
import sys
import math
from datetime import datetime

from Inti_functions import *
from serfilesreader.serfilesreader import Serfile

# -------------------------------------------------------------
global LG # Langue de l'interfacer (1 = FR ou 2 = US)
LG = 2
# -------------------------------------------------------------

def solex_proc(serfile,Shift, Flags, ratio_fixe,ang_tilt, poly):
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
    
    shift = Shift[0]
    shift_dop = Shift[1]
    shift_cont =Shift[2]

    shift_vol=Shift[3]
    shift_zeeman=Shift[4]
  
    flag_dopcont=Flags["DOPCONT"]
    flag_display=Flags["RTDISP"]
    sfit_onlyfinal=Flags["ALLFITS"]
    flag_pol=Flags['POL']
    flag_volume=Flags["VOL"]
    
    geom=[]

    # gere ici le nombre de longueur d'onde aka decalages à gérer
    # decalage nul pour l'image de la raie spectrale
    # decalage de shift_dop pour le doppler, decalage de shift_cont pour celui du continuum sur flag_dopcont
    # serie de décalage de 1 pixel entre les bornes +/- shift_vol sur flag_volume
    
    #img_suff=(['.fits','_d1_'+str(shift_dop)+'.fits', '_d2_'+str(shift_dop)+'.fits','_cont_'+str(shift_cont)+'.fits'])
    
    if flag_dopcont :
        range_dec=[0,-shift_dop,shift_dop,shift_cont]
    else:
        if shift==0:
            range_dec=[0]
        else:
            range_dec=[shift]
    
    if flag_volume :
        range_dec1=np.arange(-shift_vol,0)
        range_dec2=np.arange(1,shift_vol+1)
        range_dec=np.concatenate(([0],range_dec1,range_dec2), axis=0)
    
    if flag_pol :
        range_dec=[0,-shift_vol,shift_vol]
    
    kend=len(range_dec)
        
    #print ('nombre de traitements ',kend)
    WorkDir=os.path.dirname(serfile)+"/"
    os.chdir(WorkDir)
    base=os.path.basename(serfile)
    basefich='_'+os.path.splitext(base)[0]
    
    if shift != 0 :
        #add shift value in filename to not erase previous file
        basefich=basefich+'_dp'+str(shift) # ajout '_' pour fichier en tete d'explorer
    
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
    if bitdepth==8:
        if LG == 1:
            logme('Acquisition non réalisée en 16 bits.')
        else:
            logme('Acquisition not done at 16 bits.') 
        sys.exit()
    logme (serfile)
    
    if LG == 1:
        logme ('Largeur et hauteur des trames SER : ' + str(Width)+','+str(Height))
        logme ('Nombre de trames : '+str( FrameCount))
    else:
        logme ('Wide and Heiht of SER frames : ' + str(Width)+','+str(Height))
        logme ('Frames number : '+str( FrameCount))
 
    try:
        #logme ('ser date : '+str(dateSer))
        f_dateSerUTC=datetime.fromtimestamp(SER_time_seconds(scan.getHeader()['DateTimeUTC']))
        logme('SER date UTC :' + f_dateSerUTC.strftime('"%Y-%m-%dT%H:%M:%S.%f7%z"'))
    except:
        pass
    
    ok_flag=True              # Flag pour sortir de la boucle de lexture avec exit
    FrameIndex=1              # Index de trame    

    # fichier ser avec spectre raies verticales ou horizontales (flag true)
    if Width>Height:
        flag_rotate=True
    else:
        flag_rotate=False
    
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
    
    #debug
    #t0=float(time.time())
    
    """
    ---------------------------------------------------------------------------
    Calcul image moyenne de toutes les trames
    ---------------------------------------------------------------------------
    """
    
    #initialize le tableau qui recevra l'image somme de toutes les trames
    mydata=np.zeros((hdr['NAXIS2'],hdr['NAXIS1']),dtype='uint64')
    
    while FrameIndex < FrameCount and ok_flag:
    
        num = scan.readFrameAtPos(FrameIndex)
        if flag_rotate:
            num=np.rot90(num)
        
        #ajoute les trames pour creer une image haut snr pour extraire
        #les parametres d'extraction de la colonne du centre de la raie et la
        #corriger des distorsions
        mydata=np.add(num,mydata)
        
        #increment la trame et l'offset pour lire trame suivant du fichier .ser
        FrameIndex=FrameIndex+1
    
   
    # calcul de l'image moyenne
    myimg=mydata/(FrameIndex-1)             # Moyenne
    myimg=np.array(myimg, dtype='uint16')   # Passe en entier 16 bits
    ih= hdr['NAXIS2']                     # Hauteur de l'image
    iw= hdr['NAXIS1']                     # Largeur de l'image
    myimg=np.reshape(myimg, (ih, iw))   # Forme tableau X,Y de l'image moyenne

    if sfit_onlyfinal==False or flag_pol :
        # sauve en fits l'image moyenne avec suffixe _mean
        savefich=basefich+'_mean'              
        SaveHdu=fits.PrimaryHDU(myimg,header=hdr)
        SaveHdu.writeto(savefich+'.fits',overwrite=True)
        
        #debug
        #t1=float(time.time())
        #print('image mean saved',t1-t0)
    
    #t1=time.time()
    #print('fin image moyenne :', t1-t0)
    #t0=time.time()
    
    
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
    y1,y2=detect_bord(myimg, axis=1, offset=5)
    
    if LG == 1:
        logme('Image moyenne - Limites verticales y1,y2 : '+str(y1)+' '+str(y2))
    else:
        logme('Mean Image - Vertical limits y1,y2 : '+str(y1)+' '+str(y2))
    
    PosRaieHaut=y1
    PosRaieBas=y2
    
    # construit le tableau des min de la raie a partir du haut jusqu'en bas
   
    MinX=np.argmin(myimg, axis=1)
    MinX=MinX[PosRaieHaut:PosRaieBas]
    IndY=np.arange(PosRaieHaut, PosRaieBas,1)
    LineRecal=1
    #best fit d'un polynome degre 2, les lignes y sont les x et les colonnes x sont les y
    p=np.polyfit(IndY,MinX,2)
    #p=np.polyfit(ym,xm,2)
    
    #calcul des x colonnes pour les y lignes du polynome
    
    a=p[0]
    b=p[1]
    c=p[2]
    #poly=[a,b,c]
    
    if flag_pol :
        a=poly[0]
        b=poly[1]
        px=poly[2]
        
        # Extraction zeeman
        # Calcul position X precise de la raie d'absortion d'où on extrait la polarisation
        # On extrait la ligne centrale dans myimg (au centre Y de l'image)
        posy = int(ih/2)
        line = myimg[posy:posy+1, 0: iw]
        # On calcul la position précise de la raie
        posx = get_line_pos_absoption(line[0], px, 13)
        # On calcule la constante actualisée du polynôme
        c = posx - a*posy**2 - b*posy + shift_zeeman
              
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
    
    logme('Coef a*x2,b*x,c :'+str(a)+' '+str(b)+' '+str(c))
    
    np_fit=np.asarray(fit)
    xi, xdec,y = np_fit.T
    xdec=xi+xdec+LineRecal
    xi=xi+LineRecal
    
    #posX_min_slit=int(min(xi)) modif du 2 avril 2022
    posX_min_slit=int(min(xi[PosRaieHaut], xi[PosRaieBas]))
    posX_max_slit=int(max(xi[PosRaieHaut], xi[PosRaieBas]))

    
    # Test position de la fente décalée
    if len(range_dec)!=1 :   # si il y des decalages à prendre en compte
        shift_max=range_dec[len(range_dec)-1]
        shift_min=range_dec[1]

        if ((posX_min_slit-shift_max)<=1) or ((posX_max_slit+shift_max)>=iw):
            if LG == 1:
                logme ('Valeur de décalage trop importante, calcul sans décalage.')
            else:
                logme ('Shift value too large, no shift computing.')
            range_dec=[0]
            kend=len(range_dec)
            
    else:
        shift_max=range_dec[0]
        if ((posX_min_slit-shift_max)<=1) or ((posX_max_slit+shift_max)>=iw):
            if LG == 1:
                logme ('Valeur de décalage trop importante, calcul sans décalage.')
            else:
                logme ('Shift value too large, no shift computing.')
            range_dec=[0]
            kend=len(range_dec)
            
      
    """
    imgplot1 = plt.imshow(myimg)
    plt.scatter(xdec,y,s=0.1, marker='.', edgecolors=('red'))
    plt.show()
    """
    
    """
    ----------------------------------------------------------------------------
    ----------------------------------------------------------------------------
    Applique les ecarts a toute les lignes de chaque trame de la sequence
    ----------------------------------------------------------------------------
    ----------------------------------------------------------------------------
    """
     
    FrameIndex=1             # Index de trame

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
        ind_l[len(ind_l)-1][(ind_l[len(ind_l)-1])>iw-1]=iw-1
        ind_l[len(ind_l)-1][(ind_l[len(ind_l)-1])<=0]=0
        ind_r.append((ind_l[len(ind_l)-1] + np.ones(ih)).astype(int))
        ind_r[len(ind_l)-1][(ind_r[len(ind_l)-1])>iw-1]=iw-1
        ind_r[len(ind_l)-1][(ind_r[len(ind_l)-1])<=0]=0
    
    
    # Lance la reconstruction du disk a partir des trames
    while FrameIndex < FrameCount :
        #t0=float(time.time())
        img=scan.readFrameAtPos(FrameIndex)
        
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
            # prevent saturation overflow for very high bright spots
            left_col[left_col>64500]=64500
            right_col[right_col>64500]=64500
        
            IntensiteRaie = left_col*left_weights + right_col*right_weights
            
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
   
    # Sauve fichier disque reconstruit pour affichage image raw en check final
    hdr['NAXIS1']=FrameCount-1
    img_suff=[]
    for i in range(0,kend):
        DiskHDU=fits.PrimaryHDU(Disk[i],header=hdr)
        if i>0 : 
            img_suff.append("_dp"+str(range_dec[i]))
        else:
            img_suff.append('')
            
        DiskHDU.writeto(basefich+img_suff[i]+'_raw.fits',overwrite='True')

    if flag_display:
        cv2.destroyAllWindows()
        
    #t1=time.time()
    #print('fin image raw :', t1-t0)
    #t0=time.time()
    
    frames=[]
    msg=[]
    if LG == 1:
        msg.append('...image centre...')
    else:
        msg.append('...center image...')

    if kend!=0 :
        for i in range(1,kend) :
            if LG == 1:
                msg.append('...décalage image '+str(range_dec[i])+"...")
            else:
                msg.append('...image shift '+str(range_dec[i])+"...")

    #msg=('...image centre...', '...image Doppler 1...', '...image Doppler 2...', '...image continuum...')
    
    for k in range(0,kend):
        
        logme(' ')
        logme(msg[k])
        """
        --------------------------------------------------------------------
        --------------------------------------------------------------------
        On passe au calcul des mauvaises lignes et de la correction geometrique
        --------------------------------------------------------------------
        --------------------------------------------------------------------
        """
        iw=Disk[k].shape[1]
        ih=Disk[k].shape[0]
        img=Disk[k]
        
        y1,y2=detect_bord (img, axis=1,offset=5)    # bords verticaux
        
        #detection de mauvaises lignes
        
        # somme de lignes projetées sur axe Y
        ysum=np.mean(img,1)
        
        
        # ne considere que les lignes du disque avec marge de 15 lignes 
        marge=15
        ysum=ysum[y1+marge:y2-marge]
        
        
        # filtrage sur fenetre de 31 pixels, polynome ordre 3 (etait 101 avant)
        yc=savgol_filter(ysum,31, 3)
        #plt.plot(yc)
        #plt.show()
    
        # divise le profil somme par le profil filtré pour avoir les hautes frequences
        hcol=np.divide(ysum,yc)

        # met à zero les pixels dont l'intensité est inferieur à 1.03 (3%)
        hcol[abs(hcol-1)<=0.03]=0
      
        # tableau de zero en debut et en fin pour completer le tableau du disque
        a=[0]*(y1+marge)
        b=[0]*(ih-y2+marge)
        hcol=np.concatenate((a,hcol,b))
        #plt.plot(hcol)
        #plt.show()
        
        # creation du tableau d'indice des lignes a corriger
        l_col=np.where(hcol!=0)
        listcol=l_col[0]
        
        origimg=np.copy(img) # as suggested by Matt considine 
        
        # correction de lignes par filtrage median 13 lignes, empririque
        for c in listcol:
            m=origimg[c-7:c+6,] #now refer to original image 
            s=np.median(m,0)
            img[c-1:c,]=s
    

        
        """
        --------------------------------------------------------------
        on echaine avec la correction de transversallium
        --------------------------------------------------------------
        """
        frame=np.copy(img)
        
        debug=False
        
        # on cherche la projection de la taille max du soleil en Y
        y1,y2=detect_bord(frame, axis=1,offset=0) 
        #x1,x2=detect_bord(frame, axis=0,offset=0)
        if LG == 1:
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
            myseuil=seuil_haut*0.5
            
            # filtre le profil moyen en Y en ne prenant que le disque
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
        
        winterp=301
        if len(ToSpline)<301 :
            
            if LG == 1:
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
 
        # Geénère tableau image de flat 
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
        frame=np.array(BelleImage, dtype='uint16')
        
        # on sauvegarde les bords haut et bas pour les calculs doppler et cont
        if k==0: 
            y1_img=y1
            y2_img=y2
        
        if sfit_onlyfinal==False:
            # sauvegarde de l'image deflattée
            #DiskHDU=fits.PrimaryHDU(frame,header=hdu.header)
            DiskHDU=fits.PrimaryHDU(frame,header=hdr)
            DiskHDU.writeto(basefich+img_suff[k]+'_flat.fits',overwrite='True')
       
        #t1=time.time()
        #print('fin flat :', t1-t0)
        #t0=time.time()
       
        """
        ------------------------------------------------------------
        Calcul du tilt si on voit les bords du soleil
        sinon on n'applique pas de correction de tilt,
        on applique un facteur SY/SX=0.5
        et on renvoit a ISIS
        ------------------------------------------------------------
        """
        
        img2=np.copy(frame)
        EllipseFit=[]
        crop=0
    
        #if float(ang_tilt)==0:
                  
        # methode fit ellipse pour calcul de tilt
        # zone d'exclusion des points contours zexcl en pourcentage de la hauteur image 
        X = detect_edge (img2, zexcl=0.1, crop=crop, disp_log=False)
        EllipseFit,XE=fit_ellipse(img2, X,disp_log=False)
  
        if not(flag_nobords):
            
            # correction de tilt uniquement si on voit les limbes droit/gauche
            # trouve les coordonnées y des bords du disque dont on a les x1 et x2 
            # pour avoir les coordonnées y du grand axe horizontal
            # on cherche la projection de la taille max du soleil en Y et en X
            BackGround=100
           
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
                
            if float(ang_tilt)==0:  
                # calcul l'angle de tilt ellipse
                dy=(el_y_x2-el_y_x1)
                dx=(el_x2-el_x1)
                TanAlpha=(-dy/dx)
                AlphaRad=math.atan(TanAlpha)
                AlphaDeg=math.degrees(AlphaRad)
            
            else :
                AlphaDeg=float(ang_tilt)
                AlphaRad=math.radians(AlphaDeg)
                TanAlpha=np.arctan(AlphaRad)
            
            if LG == 1:
                logme('Angle de Tilt : '+"{:+.3f}".format(AlphaDeg))
            else:
                logme('Tilt angle : '+"{:+.3f}".format(AlphaDeg))
            
            #on force l'angle de tilt pour les prochaines images
            ang_tilt=AlphaDeg
            
            # Test si correction de tilt si angle supérieur a 0.3 degres
            if abs(AlphaDeg)> 0.3 :
                
                #decale lignes images par rapport au centre
                colref=round((el_x1+el_x2)/2)
                dymax=int(abs(TanAlpha)*((el_x2-el_x1)/2))
                a=np.ones((dymax,iw))
                img2=np.concatenate((a,img2,a))
                
                ih=ih+dymax*2
                
                crop=int(abs(TanAlpha)*iw)
                #print ('crop : ', crop)
                
                NewImg=np.empty((ih,iw))
                for i in range(0,iw):
                    x=img2[:,i]
                    NewImg[:,i]=x
                    y=np.arange(0,ih)
                    dy=(i-colref)*TanAlpha
                    ycalc = y + np.ones(ih)*dy # improvements TheSmiths
                    f=interp1d(ycalc,x,kind='linear',fill_value=(BackGround,BackGround),bounds_error=False)
                    xcalc=f(y)
                    NewLine=xcalc
                    NewImg[:,i]=NewLine
                NewImg[NewImg<=0]=0  #modif du 19/05/2021 etait a 1000
                img2=np.copy(NewImg)

            else:
                if LG == 1:
                    logme('Alignement meilleur que 0.3°, correction de tilt non nécessaire.')
                else:
                    logme('Alignment better than 0.3°, tilt correction not necessary.')
                    
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
        
        #t1=time.time()
        #print('fin tilt  :', t1-t0)
        #t0=time.time()
        
        if flag_nobords:
            ratio_fixe=0.5
            
        if k==1:
            ratio_fixe=ratio_fixe_d1
            
        if ratio_fixe==0:
            # methode fit ellipse pour calcul du ratio SY/SX
    
            #y_x1,y_x2=detect_y_of_x(img2, x1, x2)
            #flag_nobords=False
            #toprint='Position Y des limbes droit et gauche x1, x2 : '+str(y_x1)+' '+str(y_x2)
            #print(toprint)
            X = detect_edge (img2, zexcl=0.1,crop=crop, disp_log=False)
            EllipseFit,XE=fit_ellipse(img2, X,disp_log=False)
            
            ratio=EllipseFit[2]/EllipseFit[1]
            if LG == 1:
                logme('Facteur d\'échelle SY/SX : '+"{:+.3f}".format(ratio))
            else:
                logme('Scaling SY/SX : '+"{:+.3f}".format(ratio))
            NewImg, newiw=circularise2(img2,iw,ih,ratio)
        else:
            # Methode des limbes pour forcer le ratio SY/SX
            if LG == 1:
                logme('Facteur d\'échelle fixe SY/SX : '+"{:+.3f}".format(ratio_fixe))
            else:
                logme('Fixed Scaling SY/SX : '+"{:+.3f}".format(ratio_fixe))

            if k==0:
                NewImg, newiw,flag_nobords,cercle =circularise(img2,iw,ih,ratio_fixe)
            else:
                NewImg, newiw,flag_nobords,cercle =circularise(img2,iw,ih,ratio_fixe,y1_img, y2_img)
        
        if k==0:
            if ratio_fixe==0:
                ratio_fixe_d1=ratio
            else:
                ratio_fixe_d1=ratio_fixe
        
        
        frame=np.array(NewImg, dtype='uint16')
        #print('shape',frame.shape)
       
        """
        ----------------------------------------------------------------------
        Sanity check, second iteration et calcul des parametres du disk occulteur
        ----------------------------------------------------------------------
        """
        if flag_nobords:
            cercle=[0,0,0,0]
            
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
                r=round(min(wi-5,he-5)-4)
                if LG == 1:
                    logme('Final SY/SX :'+ "{:+.3f}".format(he/wi))
                    logme('Centre xc,yc et rayon : '+str(xc)+' '+str(yc)+' '+str(int(r)))
                else:
                    logme('Final SY/SX :'+ "{:+.3f}".format(he/wi))
                    logme('xc,yc center and radius : '+str(xc)+' '+str(yc)+' '+str(int(r)))
    
        if k==0:
           cercle0=cercle
           geom.append(ratio_fixe_d1)
           geom.append(ang_tilt)
           
        # Sauvegarde en fits de l'image finale
        frame=np.array(frame, dtype='uint16')
        hdr['NAXIS1']=newiw
        
        hdr['INTI_XC'] = cercle0[0]
        hdr['INTI_YC'] = cercle0[1]
        hdr['INTI_R'] = cercle0[2]
        hdr['INTI_Y1'] = y1_img
        hdr['INTI_Y2'] = y2_img
    
        DiskHDU=fits.PrimaryHDU(frame,header=hdr)
        DiskHDU.writeto(basefich+img_suff[k]+'_recon.fits', overwrite='True')
     
        with  open(basefich+'_log.txt', "w") as logfile:
            logfile.writelines(mylog)
        
        #t1=time.time()
        #print('fin scaling  :', t1-t0)
        
        frames.append(frame)
        
    return frames, hdr, cercle0, range_dec, geom
    