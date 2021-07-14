# -*- coding: utf-8 -*-
"""
@author: valerie desnoux
with improvements by Andrew Smith

------------------------------------------------------------------------

modif seuil dans section flat sur NewImg pour eviter de clamper à background 1000
mise en commentaire d'un ajout d'une detection des bords du disque solaire et d'un ajustement ce cercle apres
la circularisation en calculant le rayon a partir de la hauteur du disque
------------------------------------------------------------------------

-----------------------------------------------------------------------------
calcul sur une image des ecarts simples entre min de la raie
et une ligne de reference
-----------------------------------------------------------------------------
"""

from solex_util import *
from ser_read_video import *

def make_header(rdr):        
    # initialisation d'une entete fits (etait utilisé pour sauver les trames individuelles
    hdr= fits.Header()
    hdr['SIMPLE']='T'
    hdr['BITPIX']=32
    hdr['NAXIS']=2
    hdr['NAXIS1'] = rdr.iw
    hdr['NAXIS2'] = rdr.ih
    hdr['BZERO']=0
    hdr['BSCALE']=1
    hdr['BIN1']=1
    hdr['BIN2']=1
    hdr['EXPTIME']=0
    return hdr

def solex_proc(serfile, options):
    clearlog()
    plt.gray()              #palette de gris si utilise matplotlib pour visu debug
    flag_display = options['flag_display']
    
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
    # first compute mean image
    # rdr is the ser_reader object
    mean_img, rdr = compute_mean(serfile)
    hdr = make_header(rdr)
    ih = rdr.ih
    iw = rdr.iw
    
    WorkDir=os.path.dirname(serfile)+"/"
    os.chdir(WorkDir)
    base=os.path.basename(serfile)
    basefich=os.path.splitext(base)[0]

    """
    ----------------------------------------------------------------------------
    Calcul polynome ecart sur une image au centre de la sequence
    ----------------------------------------------------------------------------
    """

    
    savefich=basefich+'_mean'

    if options['save_fit']:
        SaveHdu=fits.PrimaryHDU(mean_img,header=hdr)
        SaveHdu.writeto(savefich+'.fit',overwrite=True)
    #affiche image moyenne
    if flag_display:
        cv2.namedWindow('Ser mean', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Ser mean', iw, ih)
        cv2.moveWindow('Ser mean', 100, 0)
        cv2.imshow ('Ser mean', mean_img)
        if cv2.waitKey(2000) == 27:                     # exit if Escape is hit
            cv2.destroyAllWindows()
            sys.exit()
        
        cv2.destroyAllWindows()
    
    y1,y2=detect_bord(mean_img, axis=1, offset=5)
    logme('Vertical limits y1, y2 : '+str(y1)+' '+str(y2))
    
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
        line_h=mean_img[i,:]
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
    #ecart=[]
    for y in range(0,ih):
        x=a*y**2+b*y+c
        deci=x-int(x)
        fit.append([int(x)-LineRecal,deci,y])
        #ecart.append([x-LineRecal,y])
    
    logme('Coeff A0, A1, A12 :  '+str(a)+'  '+str(b)+'  '+str(c))
    
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

    
    
    Disk, ih, iw, FrameCount = read_video_improved(serfile, fit, LineRecal, options)

    hdr['NAXIS1']=iw # note: slightly dodgy, new width
   
    #sauve fichier disque reconstruit
    if options['save_fit']:
        DiskHDU=fits.PrimaryHDU(Disk,header=hdr)
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
    
    #sauvegarde le fits
    if options['save_fit']:
        DiskHDU=fits.PrimaryHDU(img,header=hdr)
        DiskHDU.writeto(basefich+'_corr.fit', overwrite='True')
     
    
    """
    ------------------------------------------------------------
    calcul de la geometrie si on voit les bords du soleil
    sinon on applique un facteur x=0.5
    ------------------------------------------------------------
    """
    
    NewImg, newiw, flag_nobords, cercle =circularise(img,iw,ih,options)
    
    # sauve l'image circularisée
    frame=np.array(NewImg, dtype='uint16')
    if options['save_fit']:
        hdr['NAXIS1']=newiw # note: slightly dodgy, new width again
        DiskHDU=fits.PrimaryHDU(frame,header=hdr)
        DiskHDU.writeto(basefich+'_circle.fit',overwrite='True')
    
    """
    on fit un cercle !!!
   
    
    CercleFit=detect_fit_cercle (frame,y1,y2)
    print(CercleFit)
    
   
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
    if options['save_fit']:
        DiskHDU=fits.PrimaryHDU(frame,header=hdr)
        DiskHDU.writeto(basefich+'_flat.fit',overwrite='True')
   
    """
    -----------------------------------------------------------------------
    correction de distorsion slant disque
    -----------------------------------------------------------------------
    """
    img=frame
    if flag_nobords==False:
        # correction de slant uniquement si on voit les limbes droit/gauche
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
            if 'slant_fix' in options:
                TanAlpha = math.tan((options['slant_fix']))
                AlphaDeg = math.degrees(options['slant_fix'])
            logme('Slant angle : '+"{:+.2f} degrees".format(AlphaDeg))
            
            
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
                f=interp1d(ycalc,x,kind='linear',fill_value=(BackGround,BackGround),bounds_error=False)
                xcalc=f(y)
                NewLine=xcalc
                NewImg[:,i]=NewLine
            NewImg[NewImg<=0]=0  #modif du 19/05/2021 etait a 1000
            img=NewImg
    # refait un calcul de mise a l'echelle
    # le slant peut avoir legerement modifié la forme
    # mais en fait pas vraiment... donc on met en commentaire
    # img, newiw=circularise(img,newiw, ih,ratio_fixe)

    
    # sauvegarde en fits de l'image finale
    frame=np.array(img, dtype='uint16')
    if options['save_fit']:
        DiskHDU=fits.PrimaryHDU(frame,header=hdr)
        DiskHDU.writeto(basefich+'_recon.fit', overwrite='True')
    
    with  open(basefich+'_log.txt', "w") as logfile:
        logfile.writelines(mylog)
    
    return frame, hdr, cercle
    


