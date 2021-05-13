# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 11:42:32 2020

@author: valerie desnoux




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
    yl2_11[abs(yl2_11)>20]=1
    try:
        index=np.where (yl2_11==1)
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

def circularise (img,iw,ih):
    y1,y2=detect_bord (img, axis=1,offset=5)    # bords verticaux
    x1,x2=detect_bord (img, axis=0,offset=5)    # bords horizontaux
    print ('Limites horizontales x1, x2 : ',x1,x2)
    TailleX=int(x2-x1)
    if TailleX+10<int(iw/5) or TailleX+10>int(iw*.99):
        print ('Pas de bord solaire pour determiner la geometrie')
        print('Reprendre les traitements en manuel avec ISIS')
        #print(TailleX, iw)
        ratio=0.5
        flag_nobords=True
        #sys.exit()
    else:
        y_x1,y_x2=detect_y_of_x(img, x1, x2)
        flag_nobords=False
        print('Axe y_x1, y_x2',y_x1,y_x2)
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
      
        # il faut calculer les ratios du disque dans l'image en y 
        ratio=diam_cercle/(x2-x1)
        
        # paramètre du cercle
        x0= int((x1+((x2-x1)*0.5))*ratio)
        y0=y_x1
        cercle=[x0,y0, diam_cercle]
        print ('Centre cercle x0,y0 et diamètre :',x0, y0, diam_cercle)
        
    print('Ratio:', ratio)
    if ratio >=10:
        print('Rpport hauteur sur largeur supérieur à 10')
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
    

def solex_proc(serfile,shift, flag_display):
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
    ImgFile=savefich+'.fit'
    #ouvre image _mean qui la moyenne de toutes les trames spectrales du fichier ser
    hdulist = fits.open(ImgFile)
    hdu=hdulist[0]
    myspectrum=hdu.data
    ih=hdu.header['NAXIS2']
    iw=hdu.header['NAXIS1']
    myimg=np.reshape(myspectrum, (ih,iw))
    
    y1,y2=detect_bord(myimg, axis=1, offset=5)
    print ('Limites verticales y1,y2 : ', y1,y2)
    PosRaieHaut=y1
    PosRaieBas=y2
    
    """
    -----------------------------------------------------------
    Trouve les min intensité de la raie
    -----------------------------------------------------------
    """
    # construit le tableau des min de la raie a partir du haut jusqu'en bas
    MinOfRaie=[]
    
    for i in range(PosRaieHaut,PosRaieBas):
        line_h=myimg[i,:]
        MinX=line_h.argmin()
        MinOfRaie.append([MinX,i])
        #print('MinOfRaie x,y', MinX,i)
    
    #best fit d'un polynome degre 2, les lignes y sont les x et les colonnes x sont les y
    np_m=np.asarray(MinOfRaie)
    xm,ym=np_m.T
    #LineRecal=xm.min()
    LineRecal=1
    p=np.polyfit(ym,xm,2)
    
    #calcul des x colonnes pour les y lignes du polynome
    a=p[0]
    b=p[1]
    c=p[2]
    fit=[]
    ecart=[]
    for y in range(0,ih):
        x=a*y**2+b*y+c
        deci=x-int(x)
        fit.append([int(x)-LineRecal,deci,y])
        ecart.append([x-LineRecal,y])
    
    print('Coef A0,A1,A12', a,b,c)
    
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
    reconfile='recon_'+basefich+'.txt'
    np.savetxt(reconfile,ecart,fmt='%f',header='fichier recon',footer=str(LineRecal))
    
    
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

        IntensiteRaie=np.empty(ih,dtype='uint16')
        
        for j in range(0,ih):
            dx=fit[j][0]+shift
            deci=fit[j][1]
            try:
                IntensiteRaie[j]=(img[j,LineRecal+dx] *(1-deci)+deci*img[j,LineRecal+dx+1])*1.5
            except:
                IntensiteRaie[j]=IntensiteRaie[j-1]

        #ajoute au tableau disk 

        Disk[:,FrameIndex]=IntensiteRaie
        
        #cv2.resizeWindow('disk',i-i1,ih)
        if ok_resize==False:
            Disk=Disk[1:,FrameIndex:]
            #Disp=Disk
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
    DiskHDU.writeto(basefich+'_img.fit',overwrite='True')
    
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
   
    """
    # correction de lignes
    for i in range(0,len(listcol)-1):
        c=listcol[i]
        if c<=y2-15 and c>=y1+15:
            j=i
            it=1
            while (listcol[j+1]-listcol[i])==it and j<len(listcol)-2:
                j=j+1
                it=it+1
                i=i+1
                img[listcol[i]-1:listcol[i],]=img[c-2:c-1,]
                #img[listcol[i]-1:listcol[i],]=0
            if it==1:
                m=img[c-3:c+1,]
                s=np.median(m,0)
                img[c-1:c,]=s
     """  
    
    #sauvegarde le fits
    DiskHDU=fits.PrimaryHDU(img,header=hdu.header)
    DiskHDU.writeto(basefich+'_corr.fit', overwrite='True')
     
    
    """
    ------------------------------------------------------------
    calcul de la geometrie si on voit les bords du soleil
    sinon on applique un facteur x=0.5
    ------------------------------------------------------------
    """
    NewImg, newiw, flag_nobords, cercle =circularise(img,iw,ih)
    # sauve l'image circularisée
    frame=np.array(NewImg, dtype='uint16')
    hdu.header['NAXIS1']=newiw
    DiskHDU=fits.PrimaryHDU(frame,header=hdu.header)
    DiskHDU.writeto(basefich+'_circle.fit',overwrite='True')
    
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
       # plt.show()
        seuil_bas=np.percentile(frame,25)
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
    DiskHDU.writeto(basefich+'_flat.fit',overwrite='True')
   
    """
    -----------------------------------------------------------------------
    correction de distorsion tilt disque
    -----------------------------------------------------------------------
    """
    img=frame
    if flag_nobords==False:
        # correction de tilt uniquement si on voit les bords droit/gauche
        # trouve les coordonnées y des bords du disque dont on a les x1 et x2 
        # pour avoir les coordonnées y du grand axe horizontal
        # on cherche la projection de la taille max du soleil en Y et en X
        x1,x2=detect_bord(frame, axis=0,offset=0)
        y_x1,y_x2=detect_y_of_x(img, x1, x2)
        BackGround=1000
    
        # test que le grand axe de l'ellipse est horizontal
        if abs(y_x1-y_x2)> 5 :
            #calcul l'angle et fait une interpolation de slant
            dy=(y_x2-y_x1)
            dx=(x2-x1)
            TanAlpha=(-dy/dx)
            AlphaRad=math.atan(TanAlpha)
            AlphaDeg=math.degrees(AlphaRad)
            print('Angle slant: ',AlphaDeg)
            
            #decale lignes images par rapport a x1
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
                f=interp1d(ycalc,x,kind='linear',fill_value=(BackGround, BackGround),bounds_error=False)
                xcalc=f(y)
                NewLine=xcalc
                NewImg[:,i]=NewLine
            NewImg[NewImg<=BackGround]=BackGround
            img=NewImg
   
    # refait un calcul de mise a l'echelle
    # le tilt peut avoir legerement modifié la forme
    # mais en fait pas vraiment...
    # img, newiw=circularise(img,newiw, ih)
    
    # sauvegarde en fits de l'image finale
    frame=np.array(img, dtype='uint16')
    DiskHDU=fits.PrimaryHDU(frame,header=hdu.header)
    DiskHDU.writeto(basefich+'_recon.fit', overwrite='True')
    
    return frame, hdu.header, cercle
    
    



if __name__ == "__main__":
    # execute only if run as a script

    basefich='C:/Data astro/2021-01 Christian/12_18_19.ser'
    shift=0
    flag_display=False
    frame, header, cercle=solex_proc(basefich,shift,flag_display)
    
    base=os.path.basename(basefich)
    basefich=os.path.splitext(base)[0]
   
    ih=frame.shape[0]
    newiw=frame.shape[1]
    
    #gere mon affichage sur mon ecran taille en Y limitée sinon affiche image pas au format
    if ih>800:
        sc=700/ih
        
    cv2.namedWindow('sun', cv2.WINDOW_NORMAL)
    cv2.moveWindow('sun', 0, 0)
    cv2.resizeWindow('sun', (int(newiw*sc), int(ih*sc)))

    cv2.namedWindow('clahe', cv2.WINDOW_NORMAL)
    cv2.moveWindow('clahe', int(newiw*sc), 0)
    cv2.resizeWindow('clahe',(int(newiw*sc), int(ih*sc)))
    
    # create a CLAHE object (Arguments are optional)
    #clahe = cv2.createCLAHE(clipLimit=0.8, tileGridSize=(5,5))
    clahe = cv2.createCLAHE(clipLimit=0.8, tileGridSize=(2,2))
    cl1 = clahe.apply(frame)
    cv2.imwrite(basefich+'_clahe.png',cl1)
    
    Seuil_bas=np.percentile(frame, 35)
    Seuil_haut=np.max(frame)*1.05
    print('Seuil bas: ',Seuil_bas)
    print('Seuil_haut: ',Seuil_haut)
    fc=(frame-Seuil_bas)* (65000/Seuil_haut)
    fc[fc<0]=0
    frame_contrasted=np.array(fc, dtype='uint16')
    cv2.imshow('sun',frame)
    cv2.imshow('clahe',frame_contrasted)
    cv2.waitKey(0)
    
    Seuil_bas=np.percentile(cl1, 35)
    Seuil_haut=np.max(cl1)*1.05
    print('Seuil bas: ',Seuil_bas)
    print('Seuil_haut: ',Seuil_haut)
    cv2.imshow('sun',frame_contrasted)
    cc=(cl1-Seuil_bas)*(65000/Seuil_haut)
    cc[cc<0]=0
    cc=np.array(cc, dtype='uint16')
    cv2.imshow('clahe',cc)
    cv2.waitKey(15000)  #affiche 15s et continue

    #sauvegarde en png pour appliquer une colormap par autre script
    cv2.imwrite(basefich+'_disk.png',frame_contrasted)
    #sauvegarde en png de clahe
    cv2.imwrite(basefich+'_clahe.png',cc)
    
    """
    #create colormap
    im = cv2.imread(basefich+'_disk.png')
    im_max=(np.amax(im))*1.3
    im[im>im_max]=200
    print ('im_max : ',im_max)
    scale=255/im_max
    imnp=np.array(im*scale, dtype='uint8')
    imC = cv2.applyColorMap(imnp, cv2.COLORMAP_HOT)
    iw=int(imC.shape[1]*sc)
    ih=int(imC.shape[0]*sc)
    cv2.resize(imC,dsize=(ih,iw))
    cv2.namedWindow('color', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('color', iw, ih)
    cv2.moveWindow('color', 105+int(newiw*sc), 0)
    cv2.imshow('color',imC)
    cv2.waitKey(0)
    cv2.imwrite(basefich+'_color.png',imC)
    """
    
    #sauvegarde le fits
    frame=np.array(cl1, dtype='uint16')
    DiskHDU=fits.PrimaryHDU(frame,header)
    DiskHDU.writeto(basefich+'_clahe.fit', overwrite='True')

    cv2.destroyAllWindows()

