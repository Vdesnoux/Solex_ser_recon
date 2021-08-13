# -*- coding: utf-8 -*-
"""
Created on Thu Aug 12 10:36:58 2021

@author: valer
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
#import time
import sys
from scipy.ndimage import gaussian_filter1d
import ellipse as el
from matplotlib.patches import Ellipse

mylog=[]

#from matt considine
def SER_time_seconds(h):
    timestamp_1970 = int(621355967998300000) - int(1e7*(4*60*60-0.17))
    s=float(h-timestamp_1970)/1e7 # convert to seconds
    return s # number of seconds from 0001 to 1970

def clearlog():
    mylog.clear()

def logme(toprint):
    mylog.append(toprint+'\n')
    print (toprint)

def detect_bord (img, axis, offset):
    #axis donne la direction de detection des bords si 1 vertical, ou 0 horiz
    #offset decalage la coordonnée pour prendre en compte le lissage gaussien
    ih=img.shape[0]
    iw=img.shape[1]
    if axis==1:
        # Determination des limites de la projection du soleil sur l'axe Y
        #ymean=np.mean(img[10:,:-10],1)
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
    logme('Position X des limbes droit et gauche x1, x2 : '+str(x1)+' '+str(x2))
    
    TailleX=int(x2-x1)
    if TailleX+10<int(iw/5) or TailleX+10>int(iw*.99):
        logme('Pas de limbe solaire pour determiner la geometrie')
        logme('Reprendre les traitements en manuel avec ISIS')

        #print(TailleX, iw)
        ratio=0.5
        flag_nobords=True
        cercle=[0,0,1]
    else:
        y_x1,y_x2=detect_y_of_x(img, x1, x2)
        flag_nobords=False
        logme('Position Y des limbes droit et gauche x1, x2 : '+str(y_x1)+' '+str(y_x2))
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
        logme('Centre cercle x0,y0 et diamètreY, diamètreX :'+str(x0)+' '+str(y0)+' '+str(diam_cercle)+' '+str((x2-x1)))
        
    logme('Ratio SY/SX :'+"{:.3f}".format(ratio))
    
    if ratio >=50:
        logme('Rapport hauteur sur largeur supérieur à 50 - Exit')
        sys.exit()
    #nouvelle taille image en y 
    newiw=int(iw*ratio)
    
    # on cacule la nouvelle image reinterpolée
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

def detect_noXlimbs (myimg):
    
    flag_nobords=False
    x1,x2=detect_bord (myimg, axis=0,offset=5)    # bords horizontaux
    TailleX=int(x2-x1)
    iw=myimg.shape[1]
    
    if TailleX+10<int(iw/5) or TailleX+10>int(iw*.99):
        logme('Pas de limbe solaire pour determiner la geometrie')       
        logme('Reprendre les traitements en manuel avec ISIS')
        flag_nobords=True
    
    return flag_nobords

def detect_edge (myimg,zexcl,disp_log):
    edgeX=[]
    edgeY=[]
    
    #detect si pas de limbes droits et/ou gauche
    y1,y2=detect_bord (myimg, axis=1,offset=5)    # bords verticaux    
    #mid=int((y2-y1)/2)+y1

    zone_fit=abs(y2-y1)
    ze=int(zexcl*zone_fit)


    for i in range(y1+ze,y2-ze):
        li=np.copy(myimg[i,:-5])
        
        #method detect_bord same as flat median
        offset=0
        b=np.percentile(li,97)
        bb=b*0.5

        li[li>bb]=bb
        li_filter=gaussian_filter1d(li, 11)
        li_gr=np.gradient(li_filter)
        
        """
        for debug
        if i==mid:
            plt.plot(li)
            plt.title('Profil ligne - filtre gaussien ')
            plt.show()
            plt.plot(li_gr)
            plt.title('Gradient Profil ligne ')
            plt.show()
        """   
        x1=li_gr.argmax()
        x2=li_gr.argmin()

        s=np.array([x1,x2])
        
        if s.size !=0:
            c_x1=s[0]+offset
            c_x2=s[-1]-offset
            edgeX.append(c_x1)
            edgeY.append(i)
            edgeX.append(c_x2)
            edgeY.append(i)
                
        X = np.array(list(zip(edgeX, edgeY)))   

    return X

def fit_ellipse (myimg,X,disp_log):
    
    debug_graphics=False
    disp_log=False
        
    EllipseFit=[]
    reg = el.LsqEllipse().fit(X)
    center, width, height, phi = reg.as_parameters()
    EllipseFit=[center,width,height,phi]
    #section=((baryY-center[1])/center[1])
    XE=reg.return_fit(n_points=2000)
    
    
    if disp_log or debug_graphics:
        print()
        print(f'center: {center[0]:.3f}, {center[1]:.3f}')
        print(f'width: {width*2:.3f}')
        print(f'height: {height*2:.3f}')
        print(f'phi: {np.rad2deg(phi):.3f}')

    if debug_graphics:
        plt.imshow(myimg)
        # plot ellipse in blue
        ellipse = Ellipse(
            xy=center, width=2*width, height=2*height, angle=np.rad2deg(phi),
            edgecolor='b', fc='None', lw=1, label='Fit', zorder=2)
        # plot edges on image as red dots
        np_m=np.asarray(X)
        xm,ym=np_m.T
        plt.scatter(xm,ym,s=0.1, marker='.', edgecolors=('red'))
        ax=plt.gca()
        ax.add_patch(ellipse)
        plt.show()


    return EllipseFit, XE