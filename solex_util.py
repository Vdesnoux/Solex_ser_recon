"""
@author: valerie desnoux
with improvements by Andrew Smith

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
#import circle_fit as cf

mylog=[]

def clearlog():
    mylog.clear()

def logme(s):
    print(s)
    mylog.append(s+'\n')

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

def circularise (img,iw,ih,options):
    y1,y2=detect_bord (img, axis=1,offset=5)    # bords verticaux
    x1,x2=detect_bord (img, axis=0,offset=5)    # bords horizontaux
    logme('X-position of left and right solar limb, x1, x2 : '+str(x1)+' '+str(x2))
    TailleX=int(x2-x1)
    if (TailleX+10<int(iw/5) or TailleX+10>int(iw*.99)) and ('ratio_fixe' not in options):
        logme('Can\'t find solar limbs to auto-correct geometry')
        logme('Perform a manual geometric correction')
        ratio=1.0
        flag_nobords=True
        cercle=[0,0,1]
    else:
        y_x1,y_x2=detect_y_of_x(img, x1, x2)
        flag_nobords=False
        logme('Y-position of top and bottom solar limb, y1, y2 : '+str(y_x1)+' '+str(y_x2))
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
      
        if not 'ratio_fixe' in options:
            # il faut calculer les ratios du disque dans l'image en y 
            ratio=diam_cercle/(x2-x1)
        else:
            ratio=options['ratio_fixe']
            
        # paramètre du cercle
        x0= int((x1+((x2-x1)*0.5))*ratio)
        y0=y_x1
        cercle=[x0,y0, diam_cercle]
        logme('Centre of circle x0, y0 and diametre : '+str(x0)+' '+str(y0)+' '+str(diam_cercle))
        
    logme('Ratio Y/X : '+"{:.3f}".format(ratio))
    
    if ratio >=50:
        logme('ERROR: Rapport hauteur sur largeur supérieur à 50 - Exit')
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

def detect_fit_cercle (myimg,y1,y2):
    edgeX=[]
    edgeY=[]
    cercle_edge=[]

    for i in range(y1,y2):
        li=myimg[i,:-5]
        li_filter=savgol_filter(li,51,3)
        li_gr=np.gradient(li_filter)
        a=np.where((abs(li_gr)>80))
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
