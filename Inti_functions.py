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
from scipy.ndimage import gaussian_filter1d, rotate, median_filter
from scipy.signal import savgol_filter
import ellipse as el
from matplotlib.patches import Ellipse
import cv2 as cv2
import astropy.time
import math
import config as cfg
#import imutils


"""
version du 13 janvier 2024
- modif autocrop padding a droite

version V4.1.2 du 8 juiller 2023
- ajout detection outlier avec polynome
- gestion seuil haut = seuil bas dans seuil_force

version 1 juillet 23 Paris
- gestion outliers edge chgt zone filtre gaussien de 31 a 21 et zecl=0

version 1 juillet 23 Paris
- gestion outliers edge

version du 29 janvier 23 Antibes
- correction cercle dimensions si ratio fixe
- ajout ligne zero en debut et fin pour meilleure detection bords

version du 24 dec 22
- fonction de rotation image > non

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


# from J.Meeus
def angle_P_B0 (date_utc):
    time = astropy.time.Time(date_utc)
    myJD=time.jd
    date_1853JD2=2398167.2763889 # ref 9 nov 1853 18:37 
    theta = ((myJD - date_1853JD2) /27.2743) +1
    a=360*(theta-int(theta))
    L0=360-a
    Rot_Carrington = (myJD - 2398220) * 360/25.38

    I = 7.25
    K = 73.6667 + 1.3958333*(myJD - 2396758)/36525
    T = (myJD - 2451545)/36525
    Lo = (0.0003032*T + 36000.76983)*T + 280.46645
    M = ((-0.00000048*T - 0.0001559)*T + 35999.05030)*T + 357.52910
    C = ((-0.000014*T - 0.004817)*T + 1.914600)*math.sin(math.radians(M))
    C = C +(-0.000101*T - 0.019993)*math.sin(math.radians(2*M)) + 0.000290*math.sin(math.radians(3*M))
    S_true_long = Lo + C
    Lambda = S_true_long - 0.00569 - 0.00478*math.sin(math.radians(125.04 - 1934.136*T))
    Lambda_cor = Lambda + 0.004419
    x = math.degrees(math.atan(-math.cos(math.radians(Lambda_cor)) * math.tan(math.radians(23.440144))))
    y = math.degrees(math.atan(-math.cos(math.radians(Lambda - K)) * math.tan(math.radians(I))))
    P = x + y
    Bo = math.degrees(math.asin(math.sin(math.radians(Lambda - K)) * math.sin(math.radians(I))))

    return(str(round(P,2)),str(round(Bo,2)), str(L0), str(int(Rot_Carrington)))


#from matt considine
def SER_time_seconds(h):
    # From Matt C + modified 4 > -2 > 0
    timestamp_1970 = int(621355967998300000) - int(1e7*(0*60*60-0.17)) #aligned with compiled V4.0.2 version
    s=float(h-timestamp_1970)/1e7 # convert to seconds
    return s # number of seconds from 0001 to 1970

def clearlog():
    mylog.clear()

def logme(toprint):
    mylog.append(toprint+'\n')
    print (toprint)

def detect_bord (img, axis, offset, flag_disk):
    # ajout d'un flag pour distinguer les images de disk de l'image spectrale moyenne
    
    #axis donne la direction de detection des bords si 1 vertical, ou 0 horiz
    #offset: decalage la coordonnée pour prendre en compte le lissage gaussien
    debug=False
    # pretraite l'image pour eliminer les zone trop blanche
    img_mean=1.3*np.mean(img) #facteur 1.3 pour eviter des artefacts de bords
    img_c=np.copy(img)
    img_c[img_c>img_mean]=img_mean
    
    
    #img_c[0,:]=0 # pour meilleure detection bord pour soleil partiel
    #img_c[-1,:]=0
    
    img_c[0,:]= np.percentile(img,10) # pour meilleure detection bord pour soleil partiel
    img_c[-1,:]=np.percentile(img,10)
    
    
    #guillaume
    if cfg.LowDyn :
        img_c[0:7,:]=np.percentile(img_c, 15) # valeur du fond noir sur
        img_c[-7:,:]=np.percentile(img_c, 15) # valeur du fond noir sur
        #print('LOWDYN percentile 15', np.percentile(img_c, 15))

    
    # on part de cette image pour la detection haut bas
    ih=img.shape[0]
    iw=img.shape[1]
    
    if axis==1:
        # Determination des limites de la projection du soleil sur l'axe Y
        #ymean=np.mean(img[10:,:-10],1)

            
        if flag_disk :
            if 2==1:  # ne marche pas pour toutes les situations en calcium
                t=np.array((((img_c-np.min(img_c))/(np.max(img_c)-np.min(img_c)))*255), dtype='uint8')
                t2 = cv2.threshold(t, 25, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                img_c=t2[1]

            """
            background=np.percentile(img_c,25)
            background2=np.percentile(img_c,15)
            img_c[img_c<background]=0
            a=np.true_divide(img_c.sum(1),(img_c!=0).sum(1))
            b=np.array(np.nan_to_num(a,nan=background2), dtype='int16')
            b=np.reshape(b,(ih,1))
            ymean=np.mean(b[1:-1,:],1)
            """
            ymean=np.mean(img_c,1)
            
        else :
            ymean=np.mean(img_c,1) 
        
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
            print("Position Y des limbes y1, y2 :",a1,a2)
    else:
        # Determination des limites de la projection du soleil sur l'axe X
        # Elimine artefact de bords

        xmean=np.mean(img_c[10:-10,1:],0) #evite si premiere trame du fichier ser est à zero
        if debug:
            plt.title('Profil X ')
            plt.plot(xmean)
            plt.show()
        
        b=np.max(xmean)
        bb=b*0.5
        
        if cfg.LowDyn :
            #guillaume
            #bb=b*0.9 # faible dynamique, ne pas ecréter les plages blanches trop fortement
            bb=b*1
        
        xmean[xmean>bb]=bb
        
        if debug:
            plt.title('Profil Xclip ')
            plt.plot(xmean)
            plt.show()
        
        xmean=gaussian_filter1d(xmean, 11)
        xth=np.gradient(xmean)
  
    
        x1=xth.argmax()-offset+1 # prend en compte decalage de 1 du tableau moyenne
        x2=xth.argmin()+offset+1 # prend en compte decalage de 1 du tableau moyenne
        #test si pas de bord en x
        #if x1<=11 or x2>iw:
            
        if x1<=11 or x2>iw:
            x1=0
            x2=iw
        a1=x1
        a2=x2
        if debug:
            plt.plot(xth)
            plt.title('Gradient Profil X - filtre gaussien ')
            plt.show()
            print("Position X des limbes x1, x2 :",a1,a2)
        
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
        y1,y2=detect_bord (img, axis=1,offset=5, flag_disk=True)    # bords verticaux
    else:
        y1=args[0]
        y2=args[1]
       # print ("force y1,y2 ",y1,y2)
    
    x1,x2=detect_bord (img, axis=0,offset=5, flag_disk=True)    # bords horizontaux
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
            diam_cercle=int(abs(x2-x1)*ratio*0.5)
            
        # paramètre du cercle
        x0= int((x1+((x2-x1)*0.5))*ratio)
        y0=y_x1
        cercle=[x0,y0, diam_cercle, diam_cercle]
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
    x1,x2=detect_bord (myimg, axis=0,offset=5, flag_disk=True)    # bords horizontaux
    TailleX=int(x2-x1)
    iw=myimg.shape[1]
    
    if TailleX+10<int(iw/5) or TailleX+10>int(iw*.99):
        logme('Pas de limbe solaire pour déterminer la géometrie')       
        logme('Reprendre les traitements en manuel avec ISIS.')
        flag_nobords=True
    
    return flag_nobords


def detect_edge (myimg,zexcl, crop, disp_log):
    edgeX = []
    edgeY = []
    bord_droit = []
    bord_gauche = []
    bord_droitY = []
    bord_gaucheY = []
    zexcl = 0.01 # rendu obsolete
    #ih = myimg.shape[0]  not used
    iw = myimg.shape[1]
    

    
    debug=False # les images
    debug1=False #les courbes
    #print("crop...", crop)
    
    if debug:
        plt.imshow(myimg)
        plt.show()
        
    # au cas ou il fallait faire differament avec fort tilt
    if crop!=0:
        myimg_crop=myimg
        #myimg_crop=myimg[crop:-crop,:]

    else:
        myimg_crop=myimg
        
    #detect bord
    y1,y2=detect_bord (myimg_crop, axis=1,offset=0, flag_disk=True)    # bords verticaux
    x1,x2= detect_bord(myimg_crop,axis=0, offset=0, flag_disk=True)
    #print("edge y1,y2 : ", y1, y2)
    milieu=int(x1+(x2-x1)/2)
    rayon=int((x2-x1)/2)
    
    if crop >=100 : # fort tilt
        zexcl=0
        zone_bin_agauche=max(0,milieu-rayon-50)
        sub_img1=myimg_crop[:,zone_bin_agauche:milieu]
        #sub_img2=myimg_crop[:,milieu:-5]
        zone_bin_adroite=min(2*milieu+50,iw)
        sub_img2=myimg_crop[:,milieu:zone_bin_adroite]
        # bords vertical gauche et droit
        y1g,y2g=detect_bord (sub_img1, axis=1,offset=0,flag_disk=True)
        y1d,y2d=detect_bord (sub_img2, axis=1,offset=0,flag_disk=True)
        y1=min(y1g,y1d)
        y2=max(y2g,y2d)
        #print('y1,y2 crop', y1,y2, crop)
        
        

    zone_fit=abs(y2-y1)
    ze=int(zexcl*zone_fit)
    
    # guillaume
    if not cfg.LowDyn :
        # pretraite l'image pour eliminer les zone trop blanche
        # modif du 24 fev pour limiter a 50 pixels de part et d'autre du disque
        img_mean=1.3*np.mean(myimg[1:-1,milieu-rayon-50:milieu+rayon+50]) #facteur 1.3 pour eviter de clamper trop fort si diffusé
        img_c=np.copy(myimg)
        img_c[img_c>img_mean]=img_mean
        #print("img mean", img_mean)
    else:
        # releve seuil moyenne pour eviter clamp trop fort
        img_mean=3*np.mean(myimg[1:-1,milieu-rayon-50:milieu+rayon+50]) #facteur 1.3 pour eviter des artefacts de bords
        img_c=np.copy(myimg)
        img_c[img_c>img_mean]=img_mean
        #print("img mean", img_mean)
        
    k=0
    s=[]
    
    # scorie test zone differente resolu avec coupe demi disque bord droit et bord gauche
    ze1=ze 
    ze2=ze 


    for i in range(y1+ze1,y2-ze2):
        li=np.copy(img_c[i,:-5])
        #myli=np.copy(img_c[i,:-5])
        #myli=np.copy(img_c[i,:-5])
        
        
        #method detect_bord same as flat median
        offset=0
        b=np.percentile(li,97)
        bb=b*0.7 #retour à 0.7 sinon accroche sur zones trop noires
        
        if cfg.LowDyn :
            #guillaume
            bb=b*0.9 # faible dynamique, ne pas trop clamper
            #bb=65535
         
        
        #bb=b
        #print("seuil edge : ", b," ",bb)

        li[li>bb]=bb
        li=gaussian_filter1d(li, 2)
        #li[li<4000]=30
        #li_med=median_filter(li,size=50)
        li_filter=gaussian_filter1d(li, 11)
        li_gr=np.gradient(li_filter)
        #li_gr=np.gradient(li_med)
        
        
        x1li=li_gr.argmax()
        x2li=li_gr.argmin()

        
        if 2==1 :
            if i in range(y1+ze1+3, y1+ze1+5) :
            #if x1 <2500 :
                plt.plot(li)
                plt.title('Profil ligne '+str(i))
                plt.show()
                #plt.plot(li_med)
                #plt.title('Median Profil ligne '+str(i))
                #plt.show()
                plt.plot(li_gr)
                plt.title('Gradient Profil ligne '+str(i))
                plt.show()
        


        
        #x_argsort=li_gr.argsort()
        
        if x1li==0 or x2li==0 :
            pass
        else:
            s=np.array([x1li,x2li])
            
            if s.size !=0 and (s[-1]-s[0])> (x2-x1)/2:
                c_x1=s[0]+offset
                c_x2=s[-1]-offset
                bord_gauche.append(c_x1)
                bord_gaucheY.append(i)
                bord_droit.append(c_x2)
                bord_droitY.append(i)
                k=k+1
   
    bords=[bord_gauche, bord_droit]
    bordsY=[bord_gaucheY, bord_droitY] 
    
    
    if debug :
        plt.imshow(myimg)
        # plot edges on image as red dots
        a1=bords[0]
        b1=bordsY[0]
        a2=bords[1]
        b2=bordsY[1]
        plt.title("bord 0 red - bord 1 yellow")
        plt.scatter(a1,b1,s=0.1, marker='.', edgecolors=('red'))
        plt.scatter(a2,b2,s=0.1, marker='.', edgecolors=('yellow'))
        plt.show()

    
    # elimine les points le long des bords haut et bas si disk pas entier
    # si on divise par continuum on n'exclue pas les bords de crop
    # si on filtre trop on elimine des points sur un disue entier
    for i in range(0,2) :
        exd=np.copy(bords[i]) # bord
        #eY=np.copy(bordsY[i])
        gr_ex=abs(np.gradient(exd))
        
        #smooth=gaussian_filter1d(gr_ex, 21)
        #d=gr_ex-smooth

        g=[x for x in gr_ex if x > 0]
        #g=[x for x in d if (x > 0 and x <5) ]
        th=np.mean(g)
        
        if debug1 :
            print("grmean ", np.mean(g))
            plt.plot(gr_ex)
            plt.show()
            #plt.plot(d)
            #plt.title('gardient sans continuum')
            plt.show()
    
        # filtrage
        kk=1
        for k in range(0,len(gr_ex)-1) :   
            #if abs ((bords[i][kk]-bords[i][kk-1])/(bordsY[i][kk]-bordsY[i][kk-1])) > th :
            # ajoute filtrage ou un point bord droit est inférieur au mileu (cas protus)
            if abs(gr_ex[k]) > th or bords[i][kk]<=abs(x1-100) or bords[i][kk]>=x2+100 or bords[i][kk] - (i*milieu) <=0 :
            #if abs(d[k]) > th :
                #print("kk ",kk)
                del bords[i][kk]
                del bordsY[i][kk]
                kk=kk-1
            kk=kk+1
            
        
    if debug :
        plt.imshow(myimg)
        # plot edges on image as red dots
        a=bords[0]+bords[1]
        b=bordsY[0]+bordsY[1]
        plt.title('filtre gradient')
        plt.scatter(a,b,s=0.1, marker='.', edgecolors=('red'))
        plt.show()
        
    for s in range (0,2) :
        # divise profil des bords par son filtre gaussien et elimine les points 
        # au dessus de 3 pixels
        for i in range(0,2) :
    
            #s = gaussian_filter1d(bords[i], 11)
            #sav = savgol_filter(bords[i], 301, 2)
            
            # Test entre 5 et 6 
            p = np.polyfit(bordsY[i][1:-1],bords[i][1:-1],6)
            #p = np.polyfit(bordsY[i][1:-1],bords[i][1:-1],5)
            fit=[]
            for y in bordsY[i] :
                fitv = p[0]*y**6+p[1]*y**5+p[2]*y**4+p[3]*y**3+p[4]*y**2+p[5]*y+p[6]
                #fitv = p[0]*y**5+p[1]*y**4+p[2]*y**3+p[3]*y**2+p[4]*y**1+p[5]
                fit.append(fitv)
            #print('Coef poly ',p)
            fp = bords[i]-np.array(fit)
            #f = bords[i]-s
            #fsav = bords[i]-sav
            

            
            clip=3
        
            if debug1 :
                plt.scatter(bordsY[i], bords[i], s=0.1,marker='.')
                #plt.show()
                #plt.plot(s)
                #plt.plot(sav)
                plt.scatter(bordsY[i],np.array(fit), s=0.1,marker='.')
                plt.show()
                #plt.plot(f)
                #plt.plot(fsav)
                plt.plot(fp)
                plt.hlines(clip, 0, len(bords[i]), color="red")
                plt.ylim((-20,20))
                plt.show()
            
            # filtrage
            kk = 1
            # attention a direction bords droit ou gauche
            for k in range(0,len(fp)-1) :   
                if i==0 :
                    if (fp[k]) < -clip:
                        #print("kk ",kk)
                        del bords[i][kk]
                        del bordsY[i][kk]
                        kk=kk-1
                    #else:
                        #bords[i][kk]=fit[k]
                    kk=kk+1
                else:
                    if (fp[k]) > clip :
                        #print("kk ",kk)
                        del bords[i][kk]
                        del bordsY[i][kk]
                        kk=kk-1
                    #else:
                        #bords[i][kk]=fit[k]
                        
                    kk=kk+1
    
    # avant fit polynomial
   
    if debug :
        plt.imshow(myimg)
        a1=bords[0]
        b1=bordsY[0]
        a2=bords[1]
        b2=bordsY[1]
        plt.title("bord 0 red - bord 1 yellow - avant poly")
        plt.scatter(a1,b1,s=0.1, marker='.', edgecolors=('red'))
        plt.scatter(a2,b2,s=0.1, marker='.', edgecolors=('yellow'))
        plt.show()
    
    if not cfg.LowDyn : # echec du fit polynomial en faible dynamique
    #if 1==1 : # echec du fit polynomial en faible dynamique
        polyB=[]
        polyY=[]
        pB=[]
        pY=[]               
        for i in range(0,2)  :
            # Test entre 5 et 6 
            p = np.polyfit(bordsY[i][1:-1],bords[i][1:-1],6)
            #p = np.polyfit(bordsY[i][1:-1],bords[i][1:-1],5)
    
            for y in range(bordsY[i][5],bordsY[i][-5]) :
                fitv = p[0]*y**6+p[1]*y**5+p[2]*y**4+p[3]*y**3+p[4]*y**2+p[5]*y+p[6]
                #fitv = p[0]*y**5+p[1]*y**4+p[2]*y**3+p[3]*y**2+p[4]*y**1+p[5]
                if fitv>=0 :
                    pB.append(fitv)
                    pY.append(y)
            #print('Coef poly ',p)
            polyB.append(pB)
            polyY.append(pY)
            bords[i]=polyB[i]
            bordsY[i]=polyY[i]
       
    # recombine bords droit et gauche
    edgeX=bords[0]+bords[1]
    edgeY=bordsY[0]+bordsY[1]

    
    X = np.array(list(zip(edgeX, edgeY)), dtype='float')  
   
   
    if debug :
        plt.imshow(myimg)
        # plot edges on image as red dots
        np_m=np.asarray(X)
        xm,ym=np_m.T
        plt.title('filtre gradient et outliers continuum et fit polynomial')
        plt.scatter(xm,ym,s=0.1, marker='.', edgecolors=('red'))
        plt.show()

    return X



def fit_ellipse (myimg,X,disp_log):
    """
    @software{ben_hammel_2020_3723294,
    author       = {Ben Hammel and Nick Sullivan-Molina},
    title        = {bdhammel/least-squares-ellipse-fitting: v2.0.0},
    month        = mar,
    year         = 2020,
    publisher    = {Zenodo},
    version      = {v2.0.0},
    doi          = {10.5281/zenodo.3723294},
    url          = {https://doi.org/10.5281/zenodo.3723294}
    }
    """
    
    debug_graphics=False
    disp_log=False
        
    EllipseFit=[]
    reg = el.LsqEllipse().fit(X)
    center, width, height, phi = reg.as_parameters()
    EllipseFit=[center,width,height,phi]
    #EllipseFit=[center,height,width,phi]
    #section=((baryY-center[1])/center[1])
    XE=reg.return_fit(n_points=2000)
    
    
    if disp_log :
        print("Paramètres ellipse ............")
        print(f'center: {center[0]:.3f}, {center[1]:.3f}')
        print(f'width: {width:.3f}')
        print(f'height: {height:.3f}')
        print(f'phi_rad: {phi:.3f}')
        #print(f'phi: {np.rad2deg(phi):.3f}')

    if debug_graphics:
        plt.imshow(myimg)
        # plot edges on image as red dots
        np_m=np.asarray(X)
        xm,ym=np_m.T
        plt.scatter(xm,ym,s=0.1, marker='.', edgecolors=('red'))
        # plot ellipse in blue
        try:
            ellipse = Ellipse(
                xy=center, width=2*width, height=2*height, angle=np.rad2deg(phi),
                edgecolor='b', fc='None', lw=1, label='Fit', zorder=2)
    
            ax=plt.gca()
            #ax.set_ylim[0,2000]
            #plt.xlim [0,2000]
            ax.add_patch(ellipse)

        except:
            pass
       
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

def auto_crop_img (cam_height, h,w, frame, cercle0, debug_crop, param):
    
    debug_crop=False
    
    try :
        crop_force_hauteur = int(param[2])
        crop_force_largeur = int(param[3])
    except :
        crop_force_hauteur = 0
        crop_force_largeur = 0

    ih=cam_height
    # asym_h = min(cercle0[1], h-cercle0[1]) modif 31 dec 23 cause echec disque peu masqué
    asym_h = min(cercle0[1], ih-cercle0[1])
    diam_sol = 2 *cercle0[2]
    
    if crop_force_hauteur != 0 :
        crop_he = crop_force_hauteur
    else :
        #crop_he = ih+100 # pour accomoder angle de tilt
        crop_he=ih
    
    # il faut changer les coordonnées du centre de cercle0
    centre_hor=cercle0[0]
    centre_vert=cercle0[1]
    
    if asym_h <0  or asym_h <= cercle0[2]+20:
        #print("on ne centre pas en hauteur")
        if crop_force_largeur != 0 :
            crop_wi = crop_force_largeur
            print("autocrop forced")
        else :
            # largeur image multiple de ih
            # version 5.0 etait à 50
            if diam_sol+100 >= 2*ih :
                print("on prend largeur image a 3*ih", 3*ih)
                crop_wi = ih*3
            else  :
                if diam_sol +100 >=ih :
                    print("on prend largeur image a 2*ih",2*ih)
                    crop_wi = ih*2
                else :
                    #print("on garde image carrée")
                    crop_wi = crop_he

        # translation
        d_hor = cercle0[0]-crop_wi//2
        d_vert = 0
        centre_hor = crop_wi//2
        
    else :
        crop_wi = crop_he
        if crop_force_hauteur != 0 :
            crop_he = crop_force_hauteur
        if crop_force_largeur != 0 :
            crop_wi= crop_force_largeur
            
        #print('on centre et on crop')
        
        # translation
        d_hor = cercle0[0]-crop_wi//2
        d_vert = cercle0[1]-crop_he//2
        centre_hor = crop_wi//2
        centre_vert = crop_he//2


    if d_hor < 0: # doit decaler crop_img 
        dch_left=-d_hor
        dh_left=0
    else:
        dch_left=0
        dh_left=d_hor
        
    if d_vert <0 :
        dcv_top=-d_vert
        dv_top=0
    else:
        dcv_top=0
        dv_top=d_vert
    """
    if w-crop_wi-d_hor < 0 : # doit faire du padding a droite
        dch_droite = -d_hor+w
        dh_droite=w
    else:
        dch_droite=crop_wi
        dh_droite=d_hor+crop_wi
    """
    if w-crop_wi+dch_left < 0 : # doit faire du padding
        if d_hor>0 : 
            dch_droite=dch_left+w-d_hor # modif 13 jan 24 padding a droite
        else:
            dch_droite=dch_left+w # garde comme avant modif ds autres cas
        dh_droite=w

    else:
    
        if d_hor <0 :
            dch_droite=crop_wi
            #dv_bas=-d_vert+crop_he
            #dv_bas=dv_top+crop_he
            dh_droite=crop_wi-dch_left
        else :
            if crop_wi+dh_left> w :
                dch_droite=w-dh_left
                dh_droite= w
            else :
                dch_droite=crop_wi
                dh_droite=crop_wi+dh_left
    
    if debug_crop :
        if debug_crop:
            print("cercle :", cercle0)
            print("hauteur cam",cam_height)
            print("hauteur image", h)
            print("asym_h", asym_h)
            print("diam_sol", diam_sol)
            print(" h_img - h_cam", h-ih)
            print('d_hor', d_hor)
            print('d_vert', d_vert)
            print(crop_he,crop_wi)
            
    #if h-crop_he-d_vert < 0 : # doit faire du padding  en bas
    if h-crop_he+dcv_top < 0 : # doit faire du padding  en bas
        if crop_he+dv_top > h :
            if d_vert <0 :
                dcv_bas=h+dcv_top
                dv_bas=h
            else :
                dcv_bas=h-dv_top
                dv_bas=h
        else :
            dcv_bas=dcv_top+h
            dv_bas=h
    else:
        if d_vert == 0 :
            # image plus grande donc on va la centrer
            d_vert =(crop_he-h)//2+d_vert
            dv_top=-d_vert
            centre_vert=cercle0[1]-dv_top
            dv_bas=-d_vert+crop_he
            dcv_bas=crop_he
            
            
        else :
            if d_vert <0 :
                dcv_bas=crop_he
                #dv_bas=-d_vert+crop_he
                #dv_bas=dv_top+crop_he
                dv_bas=crop_he-dcv_top
            else :
                if crop_he+dv_top> h :
                    dcv_bas=h-dv_top
                    dv_bas= h
                else :
                    dcv_bas=crop_he
                    dv_bas=crop_he+dv_top
     
    if debug_crop:
        print('hor crop',dch_left, dch_droite)
        print('hor frame', dh_left, dh_droite)
        print('vert crop',dcv_top, dcv_bas)
        print('vert frame', dv_top, dv_bas)
    
    try :
        crop_img=np.full((crop_he, crop_wi),300, dtype='uint16')
        crop_img[dcv_top:dcv_bas,dch_left:dch_droite]=frame[dv_top:dv_bas,dh_left:dh_droite]
    except:
        cercleC=cercle0
        crop_he=0
        
        
    if debug_crop:
        plt.imshow(frame)
        plt.show()
       
        plt.imshow(crop_img)
        plt.show()
    
    #print('xcc, ycc center and radius ', centre_hor, centre_vert, cercle0[2] )
    print('crop image (h,w)', crop_img.shape)
        
    #cv2.imwrite(basefich+img_suff[k]+'_crop.png',crop_img)
    cercleC=[centre_hor, centre_vert, cercle0[2],cercle0[2]]

    return cercleC, crop_he, crop_wi, crop_img

def translate_img (img_mean, poly):
    # calcul des ecarts entre min et fit polynome
    fit=[]
    ecart=[]
    LineRecal = 1
    
    a=poly[0]
    b=poly[1]
    c=poly[2] # constante a y=0
    
    ih, iw = img_mean.shape
    img_mean_redresse = np.copy (img_mean)
    
    for y in range(0,ih):
        x=a*y**2+b*y+c
        ecart.append((x)-c)
        
    # ensuite il faut decaler les lignes en fonction de ecart
    for y in range(0,ih):
        myline= img_mean[y:y+1,:][0]
        # on interpole
        f=interp1d(np.arange(0,iw)-ecart[y],myline,kind='linear',fill_value="extrapolate")
        
        interp_line = f(np.arange(0,iw))
        img_mean_redresse[y:y+1,:] = interp_line

    
    return img_mean_redresse

def bin_to_spectre (img, y1, y2):
    # get the array through file path 
    
    # strategy to bin between y1 and y2
    # limit bin to small section of 20 pixels to avoid line blur
    # line is curved to vertical sum would blur the line
    
    pbin= ((y2-y1)//2) +1
    array_tobin= img[pbin-20:pbin+21,:]
    pro= np.sum(array_tobin,axis=0)

    return pro
    
    
    


