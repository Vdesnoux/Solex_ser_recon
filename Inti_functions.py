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
import cv2 as cv2

"""
version du xx 
- introduit le clamp des zones brillantes aussi dans fit_ellipse

version du 12 mai 2022
- modif fonction detect_bord avec clip moyenne pour eviter mauvaise detection
sur zone brillante avec le calcul du gradient

Version 23 avril 2022
- Christian: ajout fonction de detection du min local d'une raie GET_LINE_POS_ABSORPTION

Version du 19 oct 2021
- variable debug 
- utilitaire de seuillage image

Version du 19 aout 2021
- correction de la formule de matt  pour le calcul de l'heure des fichiers SER 


"""

mylog=[]

#from matt considine
def SER_time_seconds(h):
    # removed last part to avoid removing 4 hours to the UTC time
    timestamp_1970 = int(621355967998300000) #- int(1e7*(4*60*60-0.17))
    s=float(h-timestamp_1970)/1e7 # convert to seconds
    return s # number of seconds from 0001 to 1970

def clearlog():
    mylog.clear()

def logme(toprint):
    mylog.append(toprint+'\n')
    print (toprint)

def detect_bord (img, axis, offset):
    #axis donne la direction de detection des bords si 1 vertical, ou 0 horiz
    #offset: decalage la coordonnée pour prendre en compte le lissage gaussien
    

    # pretraite l'image pour eliminer les zone trop blanche
    img_mean=1.3*np.mean(img) #facteur 1.3 pour eviter des artefacts de bords
    img_c=np.copy(img)
    img_c[img_c>img_mean]=img_mean
    
    # on part de cette image pour la detection haut bas
    ih=img.shape[0]
    iw=img.shape[1]
    debug=False
    if axis==1:
        # Determination des limites de la projection du soleil sur l'axe Y
        #ymean=np.mean(img[10:,:-10],1)
        if 2==1:  #MattC thresh == True
            timg=np.array((((img-np.min(img))/(np.max(img)-np.min(img)))*255), dtype='uint8')
            timg2 = cv2.threshold(timg, 25, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
            ymean=np.mean(timg2[1],1)
        

        ymean=np.mean(img_c,1) #MattC
        if debug:
            plt.imshow(img_c)
            plt.show()
            plt.plot(ymean)
            plt.title('Profil Y')
            plt.show()
        ymean=gaussian_filter1d(ymean, 11)
        yth=np.gradient(ymean)
        y1=yth.argmax()-offset
        y2=yth.argmin()+offset
        if y1<=11:
            y1=0
        if y2>ih-11:
            y2=ih-1
        a1=y1
        a2=y2
        if debug:
            plt.plot(yth)
            plt.title('Gradient Profil Y - filtre gaussien')
            plt.show()
    else:
        # Determination des limites de la projection du soleil sur l'axe X
        # Elimine artefact de bords
        xmean=np.mean(img_c[10:,:-10],0)
        if debug:
            plt.title('Profil X ')
            plt.plot(xmean)
            plt.show()
        b=np.max(xmean)
        bb=b*0.5
        xmean[xmean>bb]=bb
        xmean=gaussian_filter1d(xmean, 11)
        xth=np.gradient(xmean)
        if debug:
            plt.plot(xth)
            plt.title('Gradient Profil X - filtre gaussien ')
            plt.show()
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

def circularise (img,iw,ih,ratio_fixe,*args): #methode des limbes

    if len(args)==0: 
        y1,y2=detect_bord (img, axis=1,offset=5)    # bords verticaux
    else:
        y1=args[0]
        y2=args[1]
       # print ("force y1,y2 ",y1,y2)
    
    x1,x2=detect_bord (img, axis=0,offset=5)    # bords horizontaux
    #logme('Position X des limbes droit et gauche x1, x2 : '+str(x1)+' '+str(x2))
    
    TailleX=int(x2-x1)
    if TailleX+10<int(iw/5) or TailleX+10>int(iw*.99):
        logme('Pas de limbe solaire pour determiner la géométrie')
        logme('Reprendre les traitements en manuel avec ISIS')

        #print(TailleX, iw)
        ratio=0.5
        flag_nobords=True
        cercle=[0,0,1]
    else:
        y_x1,y_x2=detect_y_of_x(img, x1, x2)
        flag_nobords=False
        #logme('Position Y des limbes droit et gauche x1, x2 : '+str(y_x1)+' '+str(y_x2))
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
        #logme('Centre cercle x0,y0 et diamètreY, diamètreX :'+str(x0)+' '+str(y0)+' '+str(diam_cercle)+' '+str((x2-x1)))
        
    #logme('Ratio SY/SX :'+"{:.3f}".format(ratio))
    
    if ratio >=50:
        logme('Erreur, rapport hauteur sur largeur supérieur à 50.')
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
        logme('Pas de limbe solaire pour déterminer la géometrie')       
        logme('Reprendre les traitements en manuel avec ISIS.')
        flag_nobords=True
    
    return flag_nobords

def detect_edge (myimg,zexcl, crop, disp_log):
    edgeX=[]
    edgeY=[]
    
    debug=False
    
    if crop!=0:
        myimg_crop=myimg[crop:-crop,:]
        #print("crop...", crop)
    else:
        myimg_crop=myimg
    #detect si pas de limbes droits et/ou gauche
    
    y1,y2=detect_bord (myimg_crop, axis=1,offset=5)    # bords verticaux
    y1=y1+crop
    y2=y2+crop
    
    #print('detect edge y1,y2', y1, y2)
    
    #mid=int((y2-y1)/2)+y1

    zone_fit=abs(y2-y1)
    ze=int(zexcl*zone_fit)
    
    # pretraite l'image pour eliminer les zone trop blanche
    img_mean=1.3*np.mean(myimg) #facteur 1.3 pour eviter des artefacts de bords
    img_c=np.copy(myimg)
    img_c[img_c>img_mean]=img_mean
    k=0


    for i in range(y1+ze,y2-ze):
        li=np.copy(img_c[i,:-5])
        
        
        #method detect_bord same as flat median
        offset=0
        b=np.percentile(li,97)
        bb=b*0.7 #was 0.5
        #print("seuil edge : ", b," ",bb)

        li[li>bb]=bb
        li_filter=gaussian_filter1d(li, 11)
        li_gr=np.gradient(li_filter)
        
        
        if debug==True:
            if i in range(y1+ze+1, y1+ze+3):
                plt.plot(li)
                plt.title('Profil ligne - filtre gaussien '+str(i))
                plt.show()
                plt.plot(li_gr)
                plt.title('Gradient Profil ligne '+str(i))
                plt.show()
           
        x1=li_gr.argmax()
        x2=li_gr.argmin()
        x_argsort=li_gr.argsort()

        s=np.array([x1,x2])
        
        if s.size !=0:
            c_x1=s[0]+offset
            c_x2=s[-1]-offset
            edgeX.append(c_x1)
            edgeY.append(i)
            edgeX.append(c_x2)
            edgeY.append(i)
            k=k+1
    if debug:
        ex=np.copy(edgeX)
        gr_ex=np.gradient(ex)
        plt.plot(ex)
        plt.show()
        plt.plot(gr_ex)
        plt.show()
    X = np.array(list(zip(edgeX, edgeY)))   

    return X

def fit_ellipse (myimg,X,disp_log):
    
    debug_graphics=False
    #disp_log=True
        
    EllipseFit=[]
    reg = el.LsqEllipse().fit(X)
    center, width, height, phi = reg.as_parameters()
    EllipseFit=[center,width,height,phi]
    #section=((baryY-center[1])/center[1])
    XE=reg.return_fit(n_points=2000)
    
    
    if disp_log or debug_graphics:
        print("Paramètres ellipse ............")
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

def seuil_image (img):
    Seuil_haut=np.percentile(img,99.999)
    Seuil_bas=(Seuil_haut*0.25)
    img[img>Seuil_haut]=Seuil_haut
    img_seuil=(img-Seuil_bas)* (65500/(Seuil_haut-Seuil_bas))
    img_seuil[img_seuil<0]=0
    
    return img_seuil, Seuil_haut, Seuil_bas

def seuil_image_force (img, Seuil_haut, Seuil_bas):
    img[img>Seuil_haut]=Seuil_haut
    img_seuil=(img-Seuil_bas)* (65500/(Seuil_haut-Seuil_bas))
    img_seuil[img_seuil<0]=0
    
    return img_seuil


#=========================================================================================
# GET_LINE_POS_ABSORPTION
# Retourne la coordonnée du coeur d'une raie d'aborption (ajustement d'une parabole 3 pt)
# dans le tableau "profil". La position approximative de la raie est "pos".
# La largeur de la zone de recherche est "seach_wide".
# =======================================================================================
def get_line_pos_absoption(profil, pos, search_wide):
            
    w = search_wide
    
    p1 = int(pos - w/2)
    p2 = int(pos + w/2)
    
    if p1<0:  # quelques contrôles
        p1 = 0 
    if p2>profil.shape[0]:
        p2 = profil.shape[0]
        
    x = profil[p1:p2]         # sous-profil
    
    xmin = np.argmin(x)       # coordonnée du point à valeur minimale dans le sous profil
    
    
    # On calcule une parabole qui passe par les deux points adjacents 
    y = [x[xmin-1], x[xmin], x[xmin+1]]   
    xx = [0.0, 1.0, 2.0]        
    z = np.polyfit(xx, y, 2, full = True)
    
    coefficient = z[0]   # coefficients de la parabole
    
    # On charche le minima dans la parabole avec un pas de 0,01 pixel
    xxx = np.arange(0.0,2.0,0.01)
    pmin= 1.0e10
    for px in xxx:
        v = coefficient[0] * px * px + coefficient[1] * px + coefficient[2]
        if v < pmin:
            pmin = v
            xpmin = px
        
    posx = p1 + xmin - 1 + xpmin
  
    return posx    



