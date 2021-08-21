# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 11:42:32 2020

@author: valerie desnoux


------------------------------------------------------------------------
Version du 19 aout 2021 - Antibes
- ajout de extension au nom de fichier si decalage en pixels non égale à zéro

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
#import matplotlib.pyplot as plt
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

    

def solex_proc(serfile,shift, flag_display, ratio_fixe,sfit_onlyfinal,ang_tilt):
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
    
    
    clearlog()
    
    
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
        print('erreur ouverture fichier : ',serfile)
        
    FrameCount = scan.getLength()    #      return number of frame in SER file.
    Width = scan.getWidth()          #      return width of a frame
    Height = scan.getHeight()        #      return height of a frame
    dateSerUTC = scan.getHeader()['DateTimeUTC']
    dateSer=scan.getHeader()['DateTime']
    logme (serfile)
    logme ('ser frame width, height : ' + str(Width)+','+str(Height))
    logme ('ser number of frame : '+str( FrameCount))
    try:
        #logme ('ser date : '+str(dateSer))
        f_dateSerUTC=datetime.fromtimestamp(SER_time_seconds(scan.getHeader()['DateTimeUTC']))
        logme('ser date UTC :' + f_dateSerUTC.strftime('"%Y-%m-%dT%H:%M:%S.%f7%z"'))
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
    calcul image moyenne de toutes les trames
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

    
    if sfit_onlyfinal==False:
        # sauve en fits l'image moyenne avec suffixe _mean
        savefich=basefich+'_mean'              
        SaveHdu=fits.PrimaryHDU(myimg,header=hdr)
        SaveHdu.writeto(savefich+'.fits',overwrite=True)
        
        #debug
        #t1=float(time.time())
        #print('image mean saved',t1-t0)
    
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
    Calcul polynome ecart sur une image au centre de la sequence
    ----------------------------------------------------------------------------
    """
    # detect up and down limit of the spectrum of the mean image
    y1,y2=detect_bord(myimg, axis=1, offset=5)
    
    logme('Limites verticales y1,y2 : '+str(y1)+' '+str(y2))
    
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
    
    logme('Coef A2,A1,A0 :'+str(a)+' '+str(b)+' '+str(c))
    
    np_fit=np.asarray(fit)
    xi, xdec,y = np_fit.T
    xdec=xi+xdec+LineRecal
    xi=xi+LineRecal
    
    #imgplot1 = plt.imshow(myimg)
    #plt.scatter(xm,ym,s=0.1, marker='.', edgecolors=('blue'))
    #plt.scatter(xi,y,s=0.1, marker='.', edgecolors=('red'))
    #plt.scatter(xdec,y,s=0.1, marker='.', edgecolors=('green'))
    
    #plt.show()
    
    
    """
    ----------------------------------------------------------------------------
    ----------------------------------------------------------------------------
    Applique les ecarts a toute les lignes de chaque trame de la sequence
    ----------------------------------------------------------------------------
    ----------------------------------------------------------------------------
    """
     
    
    
    FrameIndex=1             # Index de trame, on evite les deux premieres

    
    if Width>Height:
        flag_rotate=True
        ih=Width
        iw=Height
    else:
        flag_rotate=False
        iw=Width
        ih=Height
    
    
    if flag_display:
                   
        cv2.namedWindow('disk', cv2.WINDOW_NORMAL)
        FrameMax=FrameCount
        cv2.resizeWindow('disk', int(FrameMax*sc), int(ih*sc))
        cv2.moveWindow('disk', int(iw*sc)+1, 0)
        #initialize le tableau qui va recevoir les intensités spectrale de chaque trame
        Disk=np.zeros((ih,FrameMax), dtype='uint16')
        
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.moveWindow('image', 0, 0)
        cv2.resizeWindow('image', int(iw*sc), int(ih*sc))
    else:
        #Disk=np.zeros((ih,1), dtype='uint16')
        FrameMax=FrameCount
        Disk=np.zeros((ih,FrameMax), dtype='uint16')
        
    # init vector to speed up from Andrew & Doug Smiths 
    ind_l = (np.asarray(fit)[:, 0] + np.ones(ih) * (LineRecal + shift)).astype(int)
    ind_r = (ind_l + np.ones(ih)).astype(int)
    left_weights = np.ones(ih) - np.asarray(fit)[:, 1]
    right_weights = np.ones(ih) - left_weights
    
    # lance la reconstruction du disk a partir des trames
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
                
        
        # new code from Andrew & Doug  Smiths to speed up reconstruction
        left_col = img[np.arange(ih), ind_l]
        right_col = img[np.arange(ih), ind_r]
        
        # prevent saturation overflow for very high bright spots
        left_col[left_col>64000]=64000
        right_col[right_col>64000]=64000
        IntensiteRaie = left_col*left_weights + right_col*right_weights
        
        #ajoute au tableau disk 
        Disk[:,FrameIndex]=IntensiteRaie
        
        # display reconstruction of the disk refreshed every 30 lines
        refresh_lines=int(20)
        if flag_display and FrameIndex %refresh_lines ==0:
            cv2.imshow ('disk', Disk)
            if cv2.waitKey(1) == 27:             # exit if Escape is hit
                     cv2.destroyAllWindows()
                     sys.exit()
    
        FrameIndex=FrameIndex+1

   
    #sauve fichier disque reconstruit pour affichage image raw en check final
    #hdu.header['NAXIS1']=FrameCount-1
    hdr['NAXIS1']=FrameCount-1
    
    #DiskHDU=fits.PrimaryHDU(Disk,header=hdu.header)
    DiskHDU=fits.PrimaryHDU(Disk,header=hdr)
    DiskHDU.writeto(basefich+'_img.fits',overwrite='True')
    
    if flag_display:
        cv2.destroyAllWindows()
        
    
    """
    --------------------------------------------------------------------
    --------------------------------------------------------------------
    on passe au calcul des mauvaises lignes et de la correction geometrique
    --------------------------------------------------------------------
    --------------------------------------------------------------------
    """
    iw=Disk.shape[1]
    ih=Disk.shape[0]
    img=Disk
    
    y1,y2=detect_bord (img, axis=1,offset=5)    # bords verticaux
    
    #detection de mauvaises lignes
    
    # somme de lignes projetées sur axe Y
    ysum=np.mean(img,1)
    #plt.plot(ysum)
    #plt.show()
    # ne considere que les lignes du disque avec marge de 15 lignes 
    ysum=ysum[y1+15:y2-15]
    
    # filtrage sur fenetre de 31 pixels, polynome ordre 3 (etait 101 avant)
    yc=savgol_filter(ysum,31, 3)

    # divise le profil somme par le profil filtré pour avoir les hautes frequences
    hcol=np.divide(ysum,yc)

    # met à zero les pixels dont l'intensité est inferieur à 1.03 (3%)
    hcol[abs(hcol-1)<=0.03]=0

    
    # tableau de zero en debut et en fin pour completer le tableau du disque
    a=[0]*(y1+15)
    b=[0]*(ih-y2+15)
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
    
    # on cherche la projection de la taille max du soleil en Y
    y1,y2=detect_bord(frame, axis=1,offset=0)
    #x1,x2=detect_bord(frame, axis=0,offset=0)

    flag_nobords=detect_noXlimbs(frame)
    
    # si mauvaise detection des bords en x alors on doit prendre toute l'image
    if flag_nobords:
        ydisk=np.median(img,1)
    else:

        seuil_haut=np.percentile(frame,97) 
        myseuil=seuil_haut*0.5
        
        # filtre le profil moyen en Y en ne prenant que le disque
        ydisk=np.empty(ih+1)
        for j in range(0,ih):
            temp=np.copy(frame[j,:])
            temp=temp[temp>myseuil]
            if len(temp)!=0:
                ydisk[j]=np.median(temp)
            else:
                ydisk[j]=1

    # ne prend que le profil des intensités pour eviter les rebonds de bords
    ToSpline= ydisk[y1:y2]
    
    Smoothed2=savgol_filter(ToSpline,301, 3) # window size, polynomial order
    
    """
    #best fit d'un polynome degre 4 - test pour ISIS modif
    np_m=np.asarray(ToSpline)
    ym=np_m.T
    xm=np.arange(y2-y1)
    p=np.polyfit(xm,ym,4)
    
    #calcul des x colonnes pour les y lignes du polynome
    a=p[0]
    b=p[1]
    c=p[2]
    d=p[3]
    e=p[4]
    Smoothed=[]
    for x in range(0,y2-y1):
        y=a*x**4+b*x**3+c*x**2+d*x+e
        Smoothed.append(y)
    """
    """
    plt.plot(ToSpline)
    plt.plot(Smoothed)
    plt.plot(Smoothed2)
    plt.show()
    """
    
    # divise le profil reel par son filtre ce qui nous donne le flat
    hf=np.divide(ToSpline,Smoothed2)
       
    # elimine possible artefact de bord
    hf=hf[5:-5]
    
    #reconstruit le tableau du profil complet an completant le debut et fin
    a=[1]*(y1+5)
    b=[1]*(ih-y2+5)
    hf=np.concatenate((a,hf,b))
    
    #Smoothed=np.concatenate((a,Smoothed,b))
    ToSpline=np.concatenate((a,ToSpline,b))
    Smoothed2=np.concatenate((a,Smoothed2,b))
    
    """
    plt.plot(ToSpline)
    plt.plot(Smoothed2)
    plt.show()
    
    plt.plot(hf)
    plt.show()
    """
    
    # genere tableau image de flat 
    flat=[]
    for i in range(0,iw):
        flat.append(hf)
        
    np_flat=np.asarray(flat)
    flat = np_flat.T
    
    #evite les divisions par zeros...
    flat[flat==0]=1
    
    """
    plt.imshow(flat)
    plt.show()
    """
    
    # divise image par le flat
    BelleImage=np.divide(frame,flat)
    frame=np.array(BelleImage, dtype='uint16')
    
    if sfit_onlyfinal==False:
        # sauvegarde de l'image deflattée
        #DiskHDU=fits.PrimaryHDU(frame,header=hdu.header)
        DiskHDU=fits.PrimaryHDU(frame,header=hdr)
        DiskHDU.writeto(basefich+'_flat.fits',overwrite='True')
   
    """
    ------------------------------------------------------------
    calcul du tilt si on voit les bords du soleil
    sinon on n'applique pas de correction de tilt,
    on applique un facteur SY/SX=0.5
    et on renvoit a ISIS
    ------------------------------------------------------------
    """
    
    img2=np.copy(frame)
    EllipseFit=[]


    if float(ang_tilt)==0:
              
        # methode fit ellipse pour calcul de tilt
        # zone d'exclusion des points contours zexcl en pourcentage de la hauteur image 
        X = detect_edge (img2, zexcl=0.1, disp_log=False)
        EllipseFit,XE=fit_ellipse(img2, X,disp_log=False)

    
    if not(flag_nobords):
        # correction de tilt uniquement si on voit les limbes droit/gauche
        # trouve les coordonnées y des bords du disque dont on a les x1 et x2 
        # pour avoir les coordonnées y du grand axe horizontal
        # on cherche la projection de la taille max du soleil en Y et en X
        BackGround=100
        
        """
        # good old method...
        x1,x2=detect_bord(frame, axis=0,offset=0)
        y_x1,y_x2=detect_y_of_x(img2, x1, x2)
        print ('check veille methode x1,x2:', x1, x2)
        print ('check veille methode  y_x1, y_x2:', y_x1, y_x2)
        """
        
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
        
        # calcul l'angle de tilt ellipse
        dy=(el_y_x2-el_y_x1)
        dx=(el_x2-el_x1)
        TanAlpha=(-dy/dx)
        AlphaRad=math.atan(TanAlpha)
        AlphaDeg=math.degrees(AlphaRad)
        
        if float(ang_tilt) !=0 :
            AlphaDeg=float(ang_tilt)
            AlphaRad=math.radians(AlphaDeg)
            TanAlpha=np.arctan(AlphaRad)
            
        logme('Angle Tilt : '+"{:+.2f}".format(AlphaDeg))

        """
        # calcul l'angle de tilt old method
        dy=(y_x2-y_x1)
        dx=(x2-x1)
        TanAlpha2=(-dy/dx)
        AlphaRad2=math.atan(TanAlpha2)
        AlphaDeg2=math.degrees(AlphaRad2)
            
        toprint='Angle Tilt limbes: '+"{:+.2f}".format(AlphaDeg2)
        print(toprint)
        mylog.append(toprint+'\n')
        """
        
        # test si correction de tilt si angle supérieur a 0.3 degres
        if abs(AlphaDeg)> 0.3 :
            #decale lignes images par rapport a x1
            #colref=x1
            colref=el_x1
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
            logme('alignment better than 0.3°, no tilt correction needed')
    
    if sfit_onlyfinal==False:
        # sauvegarde en fits de l'image tilt
        img2=np.array(img2, dtype='uint16')
        DiskHDU=fits.PrimaryHDU(img2,header=hdr)
        DiskHDU.writeto(basefich+'_tilt.fits', overwrite='True')
    
    
    """
    ----------------------------------------------------------------
    calcul du parametre de scaling SY/SX
    ----------------------------------------------------------------
    """
    
    if flag_nobords:
        ratio_fixe=0.5
        

    if ratio_fixe==0:
        # methode fit ellipse pour calcul du ratio SY/SX

        #y_x1,y_x2=detect_y_of_x(img2, x1, x2)
        #flag_nobords=False
        #toprint='Position Y des limbes droit et gauche x1, x2 : '+str(y_x1)+' '+str(y_x2)
        #print(toprint)
        X = detect_edge (img2, zexcl=0.1,disp_log=False)
        EllipseFit,XE=fit_ellipse(img2, X,disp_log=False)
        
        ratio=EllipseFit[2]/EllipseFit[1]
        logme('Scaling SY/SX : '+"{:+.2f}".format(ratio))
        NewImg, newiw=circularise2(img2,iw,ih,ratio)
    
    else:
        #methode des limbes pour forcer le ratio SY/SX
        logme('Scaling SY/SX fixe: '+"{:+.2f}".format(ratio_fixe))
        NewImg, newiw,flag_nobords,cercle =circularise(img2,iw,ih,ratio_fixe)
    

    frame=np.array(NewImg, dtype='uint16')
   
    
   
    """
    ----------------------------------------------------------------------
    sanity check, second iteration et calcul des parametres du disk occulteur
    ----------------------------------------------------------------------
    """
    if flag_nobords:
        cercle=[0,0,0,0]
        
    else:
        # fit ellipse pour denier check
        # zone d'exclusion des points contours zexcl en pourcentage de la hauteur image 

        X = detect_edge (frame, zexcl=0.1, disp_log=False)
        EllipseFit,XE=fit_ellipse(frame, X, disp_log=False)
       
        ratio=EllipseFit[2]/EllipseFit[1]
        
        if abs(ratio-1)>=0.01:
            print('ratio iteration2 :', ratio)
            NewImg, newiw=circularise2(frame,newiw,ih,ratio)
            frame=np.array(NewImg, dtype='uint16')
            X= detect_edge (frame, zexcl=0.1, disp_log=False)
            EllipseFit,XE=fit_ellipse(frame, X, disp_log=False)
          
        
        xc=int(EllipseFit[0][0])
        yc=int(EllipseFit[0][1])
        wi=int(EllipseFit[1]) # diametre
        he=int(EllipseFit[2])
        cercle=[xc,yc,wi,he]
        r=int(min(wi-5,he-5)-3)
        logme('Final SY/SX :'+ "{:+.2f}".format(he/wi))
        logme('Centre xc,yc et rayon : '+str(xc)+' '+str(yc)+' '+str(int(r)))

    
    # sauvegarde en fits de l'image finale
    frame=np.array(frame, dtype='uint16')
    hdr['NAXIS1']=newiw
    DiskHDU=fits.PrimaryHDU(frame,header=hdr)
    DiskHDU.writeto(basefich+'_recon.fits', overwrite='True')
    
    with  open(basefich+'_log.txt', "w") as logfile:
        logfile.writelines(mylog)
    
    #return frame, hdu.header, cercle
    return frame, hdr, cercle
    