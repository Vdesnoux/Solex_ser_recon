# -*- coding: utf-8 -*-
"""
Created on Sat Dec 23 18:33:24 2023

@author: valer
"""

import numpy as np
import matplotlib.pyplot as plt

import cv2
import math


def draw_stonyhurst (nomrep1, nomrep2,nomfich, fich_param, graph_param):
    plt.close()
    nomfich_full=nomrep1+nomfich
    img = cv2.imread(nomfich_full) 
    plt.axis('off')
    
    plt.imshow(img, cmap='gray')
    myday=fich_param['date']
    Pdisp=fich_param['PDisp']
    P=float(fich_param['P'])    # si P=0 alors INTI a calculer l'angle P avec routine locale dans PDisp
    if P!=0 :
        P=0                     # si P different de zéro INTI a tourner l'image donc le P devient nul   
    else:
        P=float(fich_param['PDisp'])
    P_rad=math.radians(P)
    B0=fich_param['B0']
    B0_rad=math.radians(B0)
    xc=fich_param['xcc']
    yc=fich_param['ycc']
    r=fich_param['radius']
    
    graduation_on=graph_param['gradu']
    opacity=graph_param['opacity']
    largeur_ligne=graph_param['lwidth']
    couleur_positive=graph_param['color']
    #couleur_negative=graph_param['color_inv'] 
    
    t=myday+"\n"
    t=t+"P : "+str(Pdisp)+"\nB0 : "+str(B0)
    plt.text(10,10,t,c="yellow", fontsize=3,verticalalignment='top')
    
    #draw circle
    angle = np.linspace( 0 , 2 * np.pi , 150 ) 
    radius = r
    x_cercle = xc+radius * np.cos( angle ) 
    y_cercle = yc+radius * np.sin( angle ) 
    plt.plot(x_cercle, y_cercle, color=couleur_positive, linewidth=largeur_ligne)
    
    
    B=np.linspace(-90, 90,39)
    B_rad=[ math.radians(a) for a in B]
    
    L=np.linspace(-180,180,37)
    L_rad=[ math.radians(a) for a in L]
    
    # L=0
    
    itemindex=0
    
    for ll in L_rad :
        X=np.array([r*math.cos(a)*math.sin(ll) for a in B_rad])
        Y=[r*math.cos(a)*math.cos(ll) for a in B_rad]
        Z=[r*math.sin(a) for a in B_rad]
        
        zz=[a*math.cos(B0_rad) for a in Z]
        yy=[a*math.sin(B0_rad) for a in Y]
        zz=np.array(zz)
        yy=np.array(yy)
        
        xp1= xc+(zz-yy)*math.sin(P_rad)
        xp2=np.array(X)*math.cos(P_rad)
        xp=np.array(xp1)+np.array(xp2)
        
        yp1= yc- (zz-yy)*math.cos(P_rad)
        yp2= np.array(X)*math.sin(P_rad)
        yp=np.array(yp1)+np.array(yp2)   
        
        t=((xp-xc)**2+(yp-yc)**2)
        tt=abs(t-r**2)
        itemindex=np.argmin(tt)
        
        
        if B0 >=0 : 
            xpp=xp[itemindex:]
            ypp=yp[itemindex:]
        else:
            xpp=xp[:itemindex]
            ypp=yp[:itemindex]
        
        if itemindex ==0 or itemindex==38:
            xpp=xp
            ypp=yp
            
        if (itemindex == (len(xp)-1) or itemindex==0 ) and abs(math.degrees(ll))>90:
            xpp=xp[0]
            ypp=yp[0]
            itemindex=1000
        
        #print(round(math.degrees(ll)), itemindex)
    
        #plt.plot(xpp,ypp,linestyle="-", color="red", linewidth=0.1, alpha=0.2)
        plt.plot(xpp,ypp,linestyle="-", color=couleur_positive, linewidth=largeur_ligne, alpha=opacity)
    
    # Trace les tropiques
    B=np.linspace(-90, 90,19)
    B_rad=[ math.radians(a) for a in B]
    
    L=np.linspace(-180,180,49)
    L_rad=[ math.radians(a) for a in L]
    
    for bb in B_rad :
        
        Z=np.array([r*math.sin(bb) for a in L_rad])
        X=np.array([r*math.sin(a)*math.cos(bb) for a in L_rad])
        Y=np.array([r*math.cos(a)*math.cos(bb) for a in L_rad])
        
        zz=np.array([a*math.cos(B0_rad) for a in Z])
        yy=np.array([a*math.sin(B0_rad) for a in Y])
       
        
        xp1=xc+(zz-yy)*math.sin(P_rad)
        xp2=np.array(X)*math.cos(P_rad)
        xp= np.array(xp1)+np.array(xp2)
        
        yp1=yc- (zz-yy)*math.cos(P_rad)
        yp2=np.array(X)*math.sin(P_rad)
        yp= np.array(yp1)+np.array(yp2)
        
        t=((xp-xc)**2+(yp-yc)**2)
        tt=abs(t-r**2)
    
        itemindex=np.argmin(tt)
        
    
        if itemindex > (len(xp)-1)/2 :
            itemindex=len(xp)-1-itemindex
            #print(xpp)
        
        if itemindex != 0 :
            xpp=xp[itemindex:-itemindex]
            ypp=yp[itemindex:-itemindex]
           
        else:
            xpp=xp
            ypp=yp
        #print(math.degrees(bb),itemindex)
        #plt.plot(xp,yp,linestyle="-", color="red", linewidth=0.2)
        plt.plot(xpp,ypp,linestyle="-", color=couleur_positive, linewidth=largeur_ligne, alpha=opacity)
        
        if graduation_on :
            if len(xpp)!=1 and abs(math.degrees(bb))!=90:
                lx1=[xpp[0], xpp[0]-20*math.cos(bb)]
                ly1=[ypp[0],ypp[0]-20*math.sin(bb)]
                plt.plot(lx1,ly1, color='white', linestyle='-', linewidth=0.2)
                plt.text(lx1[0]-50*math.cos(bb), ly1[0]-50*math.sin(bb), 
                         str(round(math.degrees(bb))), fontsize=3, color='yellow',
                         horizontalalignment='center', verticalalignment='center')
                lx2=[xpp[-1], xpp[-1]+20*math.cos(bb)]
                ly2=[ypp[-1],ypp[-1]-20*math.sin(bb)]
                plt.plot(lx2,ly2, color='white', linestyle='-', linewidth=0.2)
                plt.text(lx2[0]+50*math.cos(bb), ly2[0]-50*math.sin(bb), 
                         str(round(math.degrees(bb))), fontsize=3, color='yellow',
                         horizontalalignment='center', verticalalignment='center')
    
     
    nomfich_grid=nomrep2+nomfich.replace('disk','grid')
    plt.savefig(nomfich_grid, bbox_inches='tight',dpi=600)
    
    
    """
    sg.set_options(dpi_awareness=True, scaling=2)
    layout = [[sg.Canvas(size=size, key='-CANVAS-')]]

    window = sg.Window('Embedding Matplotlib', layout, finalize=True, element_justification='center', location=(100,100))
    fig_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)

    event, values = window.read()

    window.close()
    """
    
    if graph_param['disp'] :
        plt.show()
    
"""
---------------------------------------------------------------------------------------------
Program main pour stand alone
---------------------------------------------------------------------------------------------
"""
if __name__ == '__main__':
    
    
    nomrep1='xxx' # your png _disk directory
    
    nomrep2=nomrep1
    nom_fich="_xxx_disk.png" #your filename in the nomrep1 directory
    fich_param={}
    graph_param={}
    
    fich_param['date'] = "2022-06-19T11:33:34"  # the date of your observation in the fits format
    fich_param['P'] = 0                         # P angle value
    fich_param['B0'] = 2.85                     # B0 angle value
    fich_param['xcc'] = 1344                    # center x of the sun disk
    fich_param['ycc'] = 1147                    # center y of the sun disk
    fich_param['radius'] = 1117                 # radius of the sun disk
    fich_param['PDisp']= 2.85                   # P value displayed
    
    graph_param['gradu'] = True                 # Latitude angles graduations displayed
    graph_param['opacity'] = 0.5                # opacity to the grid
    graph_param['lwidth'] = 0.2                 # line width of the grid
    graph_param['color'] = 'yellow'             # color of the grid
    graph_param['color_inv'] = 'black'          # not used
    graph_param['disp']=False                   # enable matplotlib display otherwise only png saved
    
    draw_stonyhurst(nomrep1, nomrep2,nom_fich, fich_param, graph_param)







