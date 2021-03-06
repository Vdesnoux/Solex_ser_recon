# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 11:42:32 2020

@author: valerie desnoux


------------------------------------------------------------------------
Version du 3 juillet

Remplace circularisation algo des limbes par fit ellipse
Conserve calcul de l'angle de slant par methode des limbes
supprime ratio_fixe

Version 30 mai 2021

modif seuil dans section flat sur NewImg pour eviter de clamper à background 1000
mise en commentaire d'un ajout d'une detection des bords du disque solaire et d'un ajustement ce cercle apres
la circularisation en calculant le rayon a partir de la hauteur du disque

version du 20 mai

ajout d'un seuil sur profil x pour eviter les taches trop brillantes 
en image calcium
seuil=50% du max
ajout d'un ratio_fixe qui n'est pris en compte que si non egal a zero


------------------------------------------------------------------------

-----------------------------------------------------------------------------
calcul sur une image des ecarts simples entre min de la raie
et une ligne de reference
-----------------------------------------------------------------------------
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
from scipy.ndimage import gaussian_filter1d
import circle_fit as cf
import ellipse as el
from matplotlib.patches import Ellipse



def detect_bord (img, axis, offset):
    #axis donne la direction de detection des bords si 1 vertical, ou 0 horiz
    #offset decalage la coordonnée pour prendre en compte le lissage gaussien
    ih=img.shape[0]
    iw=img.shape[1]
    if axis==1:
        # Determination des limites de la projection du soleil sur l'axe Y
        ymean=np.mean(img,1)
        #plt.plot(ymean)
        #plt.title('Profil Y')
        #plt.show()
        ymean=gaussian_filter1d(ymean, 11)
        yth=np.gradient(ymean)
        y1=yth.argmax()-offset
        y2=yth.argmin()+offset
        if y1<=11:
            y1=0
        if y2>ih-11:
            y2=ih
        a1=y1
        a2=y2
        #plt.plot(yth)
        #plt.title('Gradient Profil Y - filtre gaussien')
        #plt.show()
    else:
        # Determination des limites de la projection du soleil sur l'axe X
        # Elimine artefact de bords
        xmean=np.mean(img[10:,:-10],0)
        #plt.title('Profil X ')
        #plt.plot(xmean)
        #plt.show()
        b=np.max(xmean)
        bb=b*0.5
        xmean[xmean>bb]=bb
        xmean=gaussian_filter1d(xmean, 11)
        xth=np.gradient(xmean)
        #plt.plot(xth)
        #plt.title('Gradient Profil X - filtre gaussien ')
        #plt.show()
        x1=xth.argmax()-offset
        x2=xth.argmin()+offset
        #test si pas de bord en x
        if x1<=11 or x2>iw:
            x1=0
            x2=iw
        a1=x1
        a2=x2
    return (a1,a2)

def detect_y_of_x (img, x1,x2):
    # trouve les coordonnées y des bords du disque dont on a les x1 et x2 
    # pour avoir les coordonnées y du grand axe horizontal
    # on seuil pour eviter les gradients sues aux protus possibles
    # hauteur bord gauche
    yl1=np.copy(img[:,x1-5:x1+5])
    #plt.plot(yl1)
    #plt.show()
    Seuil_bas=np.percentile(yl1,25)
    yl1[yl1<Seuil_bas*3]=Seuil_bas
    yl1_1=np.mean(yl1,1)
    #plt.plot(yl1_1)
    #plt.show()
    yl1_1=gaussian_filter1d(yl1_1, 11)
    yl1_11=np.gradient(yl1_1)
    #plt.plot(yl1_11)
    #plt.show()
    yl1_11[abs(yl1_11)>20]=20
    try:
        index=np.where (yl1_11==20)
        #plt.plot(yl1_11)
        #plt.title('bord')
        #plt.show()
        h1=index[0][0]
        h2=index[0][-1]
    except:
        yl1_11=np.gradient(yl1_1)
        h1=np.argmax(yl1_11)
        h2=np.argmin(yl1_11)    
    #plt.plot(yl1_11)
    #plt.show()
    y_x1=int((h1+h2)/2)
    
    #Hauteur bord droit
    yl2=np.copy(img[:,x2-5:x2+5])
    Seuil_bas=np.percentile(yl2,25)
    yl2[yl2<Seuil_bas*3]=Seuil_bas
    yl2_1=np.mean(yl2,1)
    yl2_1=gaussian_filter1d(yl2_1, 11)
    yl2_11=np.gradient(yl2_1)
    #plt.plot(yl2_11)
    #plt.show()
    yl2_11[abs(yl2_11)>20]=20
    try:
        index=np.where (yl2_11==20)
        h1=index[0][0]
        h2=index[0][-1]
    except:
        yl2_11=np.gradient(yl2_1)
        h1=np.argmax(yl2_11)
        h2=np.argmin(yl2_11)
    #plt.plot(yl2_11)
    #plt.show()
    y_x2=int((h1+h2)/2)
    
    return y_x1,y_x2

def circularise (img,iw,ih,ratio_fixe): #methode des limbes
    print()
    y1,y2=detect_bord (img, axis=1,offset=5)    # bords verticaux
    x1,x2=detect_bord (img, axis=0,offset=5)    # bords horizontaux
    toprint='Position X des limbes droit et gauche x1, x2 : '+str(x1)+' '+str(x2)
    mylog.append(toprint+'\n')
    print (toprint)
    TailleX=int(x2-x1)
    if TailleX+10<int(iw/5) or TailleX+10>int(iw*.99):
        toprint='Pas de limbe solaire pour determiner la geometrie'
        print(toprint)
        mylog.append(toprint+'\n')        
        toprint='Reprendre les traitements en manuel avec ISIS'
        print(toprint)
        mylog.append(toprint+'\n')
        #print(TailleX, iw)
        ratio=0.5
        flag_nobords=True
        cercle=[0,0,1]
    else:
        y_x1,y_x2=detect_y_of_x(img, x1, x2)
        flag_nobords=False
        toprint='Position Y des limbes droit et gauche x1, x2 : '+str(y_x1)+' '+str(y_x2)
        print(toprint)
        mylog.append(toprint+'\n')
        # on calcul la coordonnée moyenne du grand axe horizontal 
        ymoy=int((y_x2+y_x1)/2)
        #ymoy=y_x1
        #print('ymoy :', ymoy)
        
        # on fait l'hypothese que le point bas du disque solaire y2 
        # moins la coordonnée ymoy du grand axe de l'ellipse est le rayon
        # qu'aurait le soleil
        # Il faut donc suffisemment de disque solaire pour avoir
        # le grand axe et pas une corde
        deltaY=max(abs(y1-ymoy),abs(y2-ymoy))
        #print ('delta Y: ', deltaY)
        diam_cercle= deltaY*2
      
        if ratio_fixe==0:
            # il faut calculer les ratios du disque dans l'image en y 
            ratio=diam_cercle/(x2-x1)
        else:
            ratio=ratio_fixe
            
        # paramètre du cercle
        x0= int((x1+((x2-x1)*0.5))*ratio)
        y0=y_x1
        cercle=[x0,y0, diam_cercle]
        toprint='Centre cercle x0,y0 et diamètreY, diamètreX :'+str(x0)+' '+str(y0)+' '+str(diam_cercle)+' '+str((x2-x1))
        print(toprint)
        mylog.append(toprint+'\n')
        
    toprint='Ratio SY/SX :'+"{:.3f}".format(ratio)
    print(toprint)
    mylog.append(toprint+'\n')
    
    if ratio >=50:
        toprint='Rapport hauteur sur largeur supérieur à 50 - Exit'
        print(toprint)
        mylog.append(toprint+'\n')
        sys.exit()
    #nouvelle taille image en y 
    newiw=int(iw*ratio)
    
    #on cacule la nouvelle image reinterpolée
    NewImg=[]
    for j in range(0,ih):
        y=img[j,:]
        x=np.arange(0,newiw+1,ratio)
        x=x[:len(y)]
        xcalc=np.arange(0,newiw)
        f=interp1d(x,y,kind='linear',fill_value="extrapolate")
        ycalc=f(xcalc)
        NewImg.append(ycalc)
    
    return NewImg, newiw, flag_nobords, cercle

def circularise2 (img,iw,ih,ratio): #methode par fit ellipse préalable
    
    #nouvelle taille image en y 
    newiw=int(iw*ratio)
    
    #on cacule la nouvelle image reinterpolée
    NewImg=[]
    for j in range(0,ih):
        y=img[j,:]
        x=np.arange(0,newiw+1,ratio)
        x=x[:len(y)]
        xcalc=np.arange(0,newiw)
        f=interp1d(x,y,kind='linear',fill_value="extrapolate")
        ycalc=f(xcalc)
        NewImg.append(ycalc)
    
    return NewImg, newiw

def detect_fit_cercle (myimg,y1,y2): #obsolete
    edgeX=[]
    edgeY=[]
    cercle_edge=[]

    for i in range(y1+10,y2-10):
        li=myimg[i,:-5]
        li_filter=savgol_filter(li,51,3)
        li_gr=np.gradient(li_filter)
        a=np.where((abs(li_gr)>80))
        if i==650:
            plt.plot(li_gr)
            plt.show()
        s=a[0]
        if s.size !=0:
            c_x1=s[0]
            c_x2=s[-1]
            edgeX.append(c_x1)
            edgeY.append(i)
            edgeX.append(c_x2)
            edgeY.append(i)
            cercle_edge.append([c_x1,i])
            cercle_edge.append([c_x2,i])

        
    #best fit du cercle centre, radius, rms
    CercleFit=cf.hyper_fit(cercle_edge)
    #print (CercleFit)
    
    #calcul des x,y cercle
    cy=CercleFit[1]
    cx=CercleFit[0]
    radius= CercleFit[2]
    cercle=[]
    for y in range(y1,y2):
        x=((radius*radius-((y-cy)*(y-cy)))**0.5)
        xa=cx-x
        cercle.append([xa,y])
        xb= cx+x
        cercle.append([xb,y])
        

    # plot cercle sur image
    np_m=np.asarray(cercle_edge)
    xm,ym=np_m.T
    np_cercle=np.asarray(cercle)
    xc, yc = np_cercle.T
    plt.imshow(myimg)
    plt.scatter(xm,ym,s=0.1, marker='.', edgecolors=('red'))
    plt.scatter(xc,yc,s=0.1, marker='.', edgecolors=('green'))
    
    plt.show()

    return CercleFit

def detect_fit_ellipse (myimg,y1,y2,zexcl):
    edgeX=[]
    edgeY=[]
    cercle_edge=[]
    
    #detect si pas de limbes droits et/ou gauche
    print()
    y1,y2=detect_bord (myimg, axis=1,offset=5)    # bords verticaux
    x1,x2=detect_bord (myimg, axis=0,offset=5)    # bords horizontaux
    toprint='Position X des limbes droit et gauche x1, x2 : '+str(x1)+' '+str(x2)
    mylog.append(toprint+'\n')
    print (toprint)
    iw=myimg.shape[1]
    TailleX=int(x2-x1)
    if TailleX+10<int(iw/5) or TailleX+10>int(iw*.99):
        toprint='Pas de limbe solaire pour determiner la geometrie'
        print(toprint)
        mylog.append(toprint+'\n')        
        toprint='Reprendre les traitements en manuel avec ISIS'
        print(toprint)
        mylog.append(toprint+'\n')
        #print(TailleX, iw)
        ratio=0.5
        EllipseFit=[0,0,ratio,1,0]
        section=0

    
    zone_fit=abs(y2-y1)
    ze=int(zexcl*zone_fit)

    for i in range(y1+ze,y2-ze):
        li=myimg[i,:-5]
        #li_filter=savgol_filter(li,31,3)
        li_filter=gaussian_filter1d(li, 11)
        li_gr=np.gradient(li_filter)

        #if i==650:
            #plt.plot(li)
            #plt.plot(li_gr)
            #plt.show()
            
        a=np.where((abs(li_gr)>80))
        s=a[0]
        if s.size !=0:
            c_x1=s[0]+10
            c_x2=s[-1]-10
            edgeX.append(c_x1)
            edgeY.append(i)
            edgeX.append(c_x2)
            edgeY.append(i)
            cercle_edge.append([c_x1,i])
            cercle_edge.append([c_x2,i])

    zy=np.mean(edgeY)    
    X = np.array(list(zip(edgeX, edgeY)))
    reg = el.LsqEllipse().fit(X)
    center, width, height, phi = reg.as_parameters()
    EllipseFit=[center,width,height,phi]
    r=height/width
    section=((zy-center[1])/center[1])

    print(f'center: {center[0]:.3f}, {center[1]:.3f}')
    print(f'width: {width*2:.3f}')
    print(f'height: {height*2:.3f}')
    print(f'phi: {np.rad2deg(phi):.3f}')
    print(f'SY/SX ellipse: {r:.3f}')
   # print(f'Section: {section:.3f}')

    """
    plt.imshow(myimg)
   
    #plt.plot(edgeX, edgeY, 'ro', zorder=1)
    ellipse = Ellipse(
        xy=center, width=2*width, height=2*height, angle=np.rad2deg(phi),
        edgecolor='b', fc='None', lw=1, label='Fit', zorder=2)
     # plot cercle sur image
    np_m=np.asarray(cercle_edge)
    xm,ym=np_m.T
    plt.scatter(xm,ym,s=0.1, marker='.', edgecolors=('red'))
    ax=plt.gca()
    ax.add_patch(ellipse)

    plt.show()
    """
    

    return EllipseFit,section
    

def solex_proc(serfile,shift, flag_display, ratio_fixe):
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
    plt.gray()              #palette de gris si utilise matplotlib pour visu debug
    
    global mylog
    mylog=[]
    
    WorkDir=os.path.dirname(serfile)+"/"
    os.chdir(WorkDir)
    base=os.path.basename(serfile)
    basefich=os.path.splitext(base)[0]
    
    #affiche ou pas l'image du disque qui se contruit en temps reel
    #gain de temps si affiche pas, mis en dur dans le script
    #print(flag_display)
    #flag_display=False
  
    """
    ----------------------------------------------------------------------------
    Calcul polynome ecart sur une image au centre de la sequence
    ----------------------------------------------------------------------------
    """

    
    savefich=basefich+'_mean'
    ImgFile=savefich+'.fits'
    #ouvre image _mean qui la moyenne de toutes les trames spectrales du fichier ser
    hdulist = fits.open(ImgFile)
    hdu=hdulist[0]
    myspectrum=hdu.data
    ih=hdu.header['NAXIS2']
    iw=hdu.header['NAXIS1']
    myimg=np.reshape(myspectrum, (ih,iw))
    
    y1,y2=detect_bord(myimg, axis=1, offset=5)
    toprint='Limites verticales y1,y2 : '+str(y1)+' '+str(y2)
    print(toprint)
    mylog.append(toprint+'\n')
    PosRaieHaut=y1
    PosRaieBas=y2
    
    
    """
    -----------------------------------------------------------
    Trouve les min intensité de la raie
    -----------------------------------------------------------
    """
    # construit le tableau des min de la raie a partir du haut jusqu'en bas
    """
    MinOfRaie=[]
    
    for i in range(PosRaieHaut,PosRaieBas):
        line_h=myimg[i,:]
        MinX=line_h.argmin()
        MinOfRaie.append([MinX,i])
        #print('MinOfRaie x,y', MinX,i)
        
    np_m=np.asarray(MinOfRaie)
    xm,ym=np_m.T
    #best fit d'un polynome degre 2, les lignes y sont les x et les colonnes x sont les 
    p=np.polyfit(ym,xm,2)

    """
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
        fit.append([int(x)-LineRecal,deci,y])
        #ecart.append([x-LineRecal,y])
    
    toprint='Coef A2,A1,A0 :'+str(a)+' '+str(b)+' '+str(c)
    print(toprint)
    mylog.append(toprint+'\n')
    
    np_fit=np.asarray(fit)
    xi, xdec,y = np_fit.T
    xdec=xi+xdec+LineRecal
    xi=xi+LineRecal
    #imgplot1 = plt.imshow(myimg)
    #plt.scatter(xm,ym,s=0.1, marker='.', edgecolors=('blue'))
    #plt.scatter(xi,y,s=0.1, marker='.', edgecolors=('red'))
    #plt.scatter(xdec,y,s=0.1, marker='.', edgecolors=('green'))
    
    #plt.show()

    #on sauvegarde les params de reconstrution
    #reconfile='recon_'+basefich+'.txt'
    #np.savetxt(reconfile,ecart,fmt='%f',header='fichier recon',footer=str(LineRecal))
    
    
    """
    ----------------------------------------------------------------------------
    ----------------------------------------------------------------------------
    Applique les ecarts a toute les lignes de chaque trame de la sequence
    ----------------------------------------------------------------------------
    ----------------------------------------------------------------------------
    """
     
    #ouverture et lecture de l'entete du fichier ser
    f=open(serfile, "rb")
    b=np.fromfile(serfile, dtype='int8',count=4)
    offset=14

    b=np.fromfile(serfile, dtype=np.uint32, count=1, offset=offset)
    #print (LuID[0])
    offset=offset+4
    
    b=np.fromfile(serfile, dtype='uint32', count=1, offset=offset)
    #print(ColorID[0])
    offset=offset+4
    
    b=np.fromfile(serfile, dtype='uint32', count=1,offset=offset)
    #print(little_Endian[0])
    offset=offset+4
    
    Width=np.fromfile(serfile, dtype='uint32', count=1,offset=offset)
    Width=Width[0]
    #print('Width :', Width)
    offset=offset+4
    
    Height=np.fromfile(serfile, dtype='uint32', count=1,offset=offset)
    Height=Height[0]
    #print('Height :',Height)
    offset=offset+4
    
    PixelDepthPerPlane=np.fromfile(serfile, dtype='uint32', count=1,offset=offset)
    PixelDepthPerPlane=PixelDepthPerPlane[0]
    #print('PixelDepth :',PixelDepthPerPlane)
    offset=offset+4
    
    FrameCount=np.fromfile(serfile, dtype='uint32', count=1,offset=offset)
    FrameCount=FrameCount[0]
    #print('nb de frame :',FrameCount)
    
    toprint=('width, height : '+str(Width)+' '+str(Height))
    print(toprint)
    mylog.append(toprint+'\n')
    toprint=('Nb frame : '+str(FrameCount))
    print(toprint)
    mylog.append(toprint+'\n')
   
    
    count=Width*Height       # Nombre d'octet d'une trame
    FrameIndex=1             # Index de trame, on evite les deux premieres
    offset=178               # Offset de l'entete fichier ser
    
    if Width>Height:
        flag_rotate=True
        ih=Width
        iw=Height
    else:
        flag_rotate=False
        iw=Width
        ih=Height
    
    #debug
    ok_resize=True

    
    if flag_display:
        cv2.namedWindow('disk', cv2.WINDOW_NORMAL)
        FrameMax=FrameCount
        cv2.resizeWindow('disk', FrameMax, ih)
        cv2.moveWindow('disk', 100, 0)
        #initialize le tableau qui va recevoir la raie spectrale de chaque trame
        Disk=np.zeros((ih,FrameMax), dtype='uint16')
        
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.moveWindow('image', 0, 0)
        cv2.resizeWindow('image', int(iw), int(ih))
    else:
        #Disk=np.zeros((ih,1), dtype='uint16')
        FrameMax=FrameCount
        Disk=np.zeros((ih,FrameMax), dtype='uint16')
        
    # init vector to speed up from Andrew Smiths 
    ind_l = (np.asarray(fit)[:, 0] + np.ones(ih) * (LineRecal + shift)).astype(int)
    ind_r = (ind_l + np.ones(ih)).astype(int)
    left_weights = np.ones(ih) - np.asarray(fit)[:, 1]
    right_weights = np.ones(ih) - left_weights
    
    # lance la reconstruction du disk a partir des trames
    while FrameIndex < FrameCount :
        #t0=float(time.time())
        img=np.fromfile(serfile, dtype='uint16',count=count, offset=offset)
        img=np.reshape(img,(Height,Width))
        
        if flag_rotate:
            img=np.rot90(img)
        
        if flag_display:
            cv2.imshow('image', img)
            if cv2.waitKey(1)==27:
                cv2.destroyAllWindows()
                sys.exit()
                
        
        #new code from Andraw Smiths to speed up reconstruction
        # improve speed here
        left_col = img[np.arange(ih), ind_l]
        right_col = img[np.arange(ih), ind_r]
        IntensiteRaie = left_col*left_weights + right_col*right_weights
        
        #ajoute au tableau disk 
        Disk[:,FrameIndex]=IntensiteRaie
        
        """
        ---------------------------------------------------------
        original code
        ---------------------------------------------------------
        IntensiteRaie=np.empty(ih,dtype='uint16')
        
        for j in range(0,ih):
            dx=fit[j][0]+shift
            deci=fit[j][1]
            try:
                IntensiteRaie[j]=(img[j,LineRecal+dx] *(1-deci)+deci*img[j,LineRecal+dx+1])
                if img[j,LineRecal+dx]>=65000:
                    IntensiteRaie[j]=64000
                    #print ('intensite : ', img[j,LineRecal+dx])
            except:
                IntensiteRaie[j]=IntensiteRaie[j-1]

        #ajoute au tableau disk 

        Disk[:,FrameIndex]=IntensiteRaie
        
        #cv2.resizeWindow('disk',i-i1,ih)
        if ok_resize==False:
            Disk=Disk[1:,FrameIndex:]
            #Disp=Disk
        """
        if flag_display and FrameIndex %5 ==0:
            cv2.imshow ('disk', Disk)
            if cv2.waitKey(1) == 27:                     # exit if Escape is hit
                     cv2.destroyAllWindows()    
                     sys.exit()
    
        FrameIndex=FrameIndex+1
        offset=178+FrameIndex*count*2

    
    #ferme fichier ser
    f.close()
   
    #sauve fichier disque reconstruit 
    hdu.header['NAXIS1']=FrameCount-1
    DiskHDU=fits.PrimaryHDU(Disk,header=hdu.header)
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
    

    # correction de lignes par filtrage median 13 lignes, empririque
    for c in listcol:
        m=img[c-7:c+6,]
        s=np.median(m,0)
        img[c-1:c,]=s
    
    #sauvegarde le fits
    DiskHDU=fits.PrimaryHDU(img,header=hdu.header)
    DiskHDU.writeto(basefich+'_corr.fits', overwrite='True')
     
    
    """
    ------------------------------------------------------------
    calcul de la geometrie si on voit les bords du soleil
    sinon on applique un facteur x=0.5
    ------------------------------------------------------------
    """
    
    img2=np.copy(img)
    print()

    #methode des limbes
    #NewImg, newiw,flag_nobords,cercle =circularise(img2,iw,ih,ratio_fixe)
    
    #methode fit ellipse
    zexcl=0.01 #zone d'exclusion des points contours
    EllipseFit,section=detect_fit_ellipse(img,y1,y2,zexcl)
    ratio=EllipseFit[2]/EllipseFit[1]
    NewImg, newiw=circularise2(img2,iw,ih,ratio)
    if section==0:
        flag_nobords=True
    else:
        flag_nobords=False
    
    # sauve l'image circularisée
    frame=np.array(NewImg, dtype='uint16')
    hdu.header['NAXIS1']=newiw
    DiskHDU=fits.PrimaryHDU(frame,header=hdu.header)
    DiskHDU.writeto(basefich+'_circle.fits',overwrite='True')
   
    #on fit un cercle !!!
    #CercleFit=detect_fit_cercle (frame,y1,y2)
    #print(CercleFit)
    #print()
    
    print()
    
    """
    NewImg, newiw =circularise2(img,iw,ih,ratio)
    frame=np.array(NewImg, dtype='uint16')
    hdu.header['NAXIS1']=newiw
    DiskHDU=fits.PrimaryHDU(frame,header=hdu.header)
    DiskHDU.writeto(basefich+'_circle2.fits',overwrite='True')
    #on fit un cercle
    CercleFit=detect_fit_cercle (frame,y1,y2)
    print(CercleFit)
    print()
    
    #EllipseFit,section=detect_fit_ellipse(frame,y1,y2,0.01)
    #x0=EllipseFit[0][0]
    #y0=EllipseFit[0][1]
    #diam_cercle=EllipseFit[2]
    #cercle=[x0,y0, diam_cercle]
    """
    
    """
    --------------------------------------------------------------
    on echaine avec la correction de transversallium
    --------------------------------------------------------------
    """
    
    # on cherche la projection de la taille max du soleil en Y
    y1,y2=detect_bord(frame, axis=1,offset=0)
    #print ('flat ',y1,y2)
    # si mauvaise detection des bords en x alors on doit prendre toute l'image
    if flag_nobords:
        ydisk=np.median(img,1)
    else:
        #plt.hist(frame.ravel(),bins=1000,)
        #plt.show()
        #plt.hist(frame.ravel(),bins=1000,cumulative=True)
        #plt.show()
        #seuil_bas=np.percentile(frame,25)
        seuil_haut=np.percentile(frame,97) 
        #print ('Seuils de flat: ',seuil_bas, seuil_haut)
        #print ('Seuils bas x: ',seuil_bas*4)
        #print ('Seuils haut x: ',seuil_haut*0.25)
        #myseuil=seuil_haut*0.2
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
    y1=y1
    y2=y2
    ToSpline= ydisk[y1:y2]
 
    
    Smoothed2=savgol_filter(ToSpline,301, 3) # window size, polynomial order
    #best fit d'un polynome degre 4
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
    plt.plot(ToSpline)
    plt.plot(Smoothed)
    plt.plot(Smoothed2)
    plt.show()
    """

    
    # divise le profil reel par son filtre ce qui nous donne le flat
    hf=np.divide(ToSpline,Smoothed2)
       
    # elimine possible artefact de bord
    hf=hf[5:-5]
    
    #reconstruit le tableau du pofil complet 
    a=[1]*(y1+5)
    b=[1]*(ih-y2+5)
    hf=np.concatenate((a,hf,b))
    
    
    Smoothed=np.concatenate((a,Smoothed,b))
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
    for i in range(0,newiw):
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
    # sauvegarde de l'image deflattée
    DiskHDU=fits.PrimaryHDU(frame,header=hdu.header)
    DiskHDU.writeto(basefich+'_flat.fits',overwrite='True')
   
    """
    -----------------------------------------------------------------------
    correction de Tilt du disque
    -----------------------------------------------------------------------
    """
    img=frame
    
    if not(flag_nobords) and abs(section)<0.1:
        # correction de slant uniquement si on voit les limbes droit/gauche
        # trouve les coordonnées y des bords du disque dont on a les x1 et x2 
        # pour avoir les coordonnées y du grand axe horizontal
        # on cherche la projection de la taille max du soleil en Y et en X
        BackGround=1000
        x1,x2=detect_bord(frame, axis=0,offset=0)
        y_x1,y_x2=detect_y_of_x(img, x1, x2)
        
        # test que le grand axe de l'ellipse est horizontal
        if abs(y_x1-y_x2)> 5 :
            #calcul l'angle et fait une interpolation de slant
            dy=(y_x2-y_x1)
            dx=(x2-x1)
            TanAlpha=(-dy/dx)
            AlphaRad=math.atan(TanAlpha)
            AlphaDeg=math.degrees(AlphaRad)
            print ('tan ', TanAlpha)
            toprint='Angle slant limbes: '+"{:+.2f}".format(AlphaDeg)
            print(toprint)
            mylog.append(toprint+'\n')
            
            #decale lignes images par rapport a x1
            colref=x1
            NewImg=np.empty((ih,newiw))
            for i in range(0,newiw):
                x=img[:,i]
                NewImg[:,i]=x
                y=np.arange(0,ih)
                dy=(i-colref)*TanAlpha
                #print (dy)
                #ycalc=[]
                ycalc = y + np.ones(ih)*dy # improvements TheSmiths
                #x et y sont les valeurs de la ligne originale avant decalge
                #for j in range(0, len(y)):
                    #ycalc.append(y[j]+dy)
                f=interp1d(ycalc,x,kind='linear',fill_value=(BackGround,BackGround),bounds_error=False)
                xcalc=f(y)
                NewLine=xcalc
                NewImg[:,i]=NewLine
            NewImg[NewImg<=0]=0  #modif du 19/05/2021 etait a 1000
            img=NewImg
        """
        #decale lignes images par rapport a x1
        AlphaRad=np.deg2rad(angle_slant)
        TanAlpha=math.tan(AlphaRad)
        print()
        print ('tan ellipse', TanAlpha)
        print ('Angle_slant ellipse :',angle_slant)
        colref=x1
        NewImg=np.empty((ih,newiw))
        for i in range(0,newiw):
            x=img[:,i]
            NewImg[:,i]=x
            y=np.arange(0,ih)
            dy=(i-colref)*TanAlpha
            #print (dy)
            ycalc=[]
            #x et y sont les valeurs de la ligne originale avant decalge
            for j in range(0, len(y)):
                ycalc.append(y[j]+dy)
            f=interp1d(ycalc,x,kind='linear',fill_value=(BackGround,BackGround),bounds_error=False)
            xcalc=f(y)
            NewLine=xcalc
            NewImg[:,i]=NewLine
        NewImg[NewImg<=0]=0  #modif du 19/05/2021 etait a 1000
        img=NewImg
        """
        
    # refait un calcul de mise a l'echelle
    # le slant peut avoir legerement modifié la forme
    
    #methode fit ellipse
    print()
    print('recircularise apres slant')
    if (abs(section)<0.1):
        zexcl=0.1
    else:
        zexcl=0.01
        
    EllipseFit,section=detect_fit_ellipse(img,y1,y2,zexcl)
    ratio=EllipseFit[2]/EllipseFit[1]
    NewImg, newiw=circularise2(img,newiw,ih,ratio)
    flag_nobords=False
    print()
    img=np.copy(NewImg)
    

    #on refait un test de fit ellipse
    print('ellipse finale')
    EllipseFit,section=detect_fit_ellipse(img,y1,y2,zexcl)
    xc=int(EllipseFit[0][0])
    yc=int(EllipseFit[0][1])
    wi=int(EllipseFit[1])
    he=int(EllipseFit[2])
    cercle=[xc,yc,wi,he]
    print()
   
    
    # sauvegarde en fits de l'image finale
    frame=np.array(img, dtype='uint16')
    DiskHDU=fits.PrimaryHDU(frame,header=hdu.header)
    DiskHDU.writeto(basefich+'_recon.fits', overwrite='True')
    
    with  open(basefich+'.txt', "w") as logfile:
        logfile.writelines(mylog)
    
    return frame, hdu.header, cercle
    