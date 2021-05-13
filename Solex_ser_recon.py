# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 16:38:55 2020

@author: valerie

Front end de traitements spectro helio de fichier ser
- interface pour selectionner un ou plusieurs fichiers
- appel au module solex_recon qui traite la sequence et genere les fichiers fits
- propose avec openCV un affichage de l'image resultat

"""
import numpy as np
import cv2
import os
import sys
import Solex_recon as sol
from astropy.io import fits

#import time
import PySimpleGUI as sg

def UI_SerBrowse (WorkDir):
    """
    Parameters
    ----------
    WorkDir : TYPE string
        repertoire par defaut à l'ouverture de la boite de dialogue

    Returns 
    -------
    Filenames : TYPE string
        liste des fichiers selectionnés, avec leur extension et le chemin complet
    Shift : Type string
        Ecart en pixel demandé pour reconstruire le disque 
        sur une longeur d'onde en relatif par rapport au centre de la raie    
    """
    sg.theme('Dark2')
    sg.theme_button_color(('white', '#500000'))
    
    layout = [
    [sg.Text('Nom du fichier', size=(15, 1)), sg.InputText(default_text='',size=(40,1),key='-FILE-'),
     sg.FilesBrowse('Open',file_types=(("SER Files", "*.ser"),),initial_folder=WorkDir)],
    [sg.Checkbox('Affiche reconstruction', default=False, key='-DISP-')],
    [sg.Text('Decalage pixel',size=(15,1)),sg.Input(default_text='0',size=(8,1),key='-DX-',enable_events=True)],  
    [sg.Button('Ok'), sg.Cancel()]
    ] 
    
    window = sg.Window('Processing', layout, finalize=True)
    window['-FILE-'].update(WorkDir) 
    window.BringToFront()
    
    while True:
        event, values = window.read()
        if event==sg.WIN_CLOSED or event=='Cancel': 
            break
        
        if event=='Ok':
            break

    window.close()
               
    FileNames=values['-FILE-']
    Shift=values['-DX-']
    flag_display=values['-DISP-']
    
    return FileNames, Shift, flag_display

# recupere les parametres utilisateurs enregistrés lors de la session
# precedente dans un fichier txt "pysolex.ini" qui va etre placé ici en dur
# dans repertoire c:/py/ pour l'instant

try:
    with open('c:/py/pysolex.ini', "r") as f1:
        
        param_init = f1.readlines()
        WorkDir=param_init[0]
except:
    pass

# Recupere paramatres de la boite de dialogue
#
# serfiles: liste des noms de fichier ser avec repertoire et extension
# shift: ecart en pixel par rapport au centre de la raie

serfiles, Shift, flag_display=UI_SerBrowse(WorkDir)
serfiles=serfiles.split(';')

#pour gerer la tempo des affichages des images resultats dans cv2.waitKey
if len(serfiles)==1:
    tempo=0
else:
    tempo=1
# boucle sur la liste des fichers
for serfile in serfiles:
    print (serfile)
    
    if serfile=='':
        sys.exit()
    
    WorkDir=os.path.dirname(serfile)+"/"
    os.chdir(WorkDir)
    base=os.path.basename(serfile)
    basefich=os.path.splitext(base)[0]
    
    # met a jour le repertoire si on a changé dans le fichier ini
    try:
        with open('c:/py/pysolex.ini', "w") as f1:
            f1.writelines(WorkDir)
    except:
        pass
    
    # ouverture du fichier ser
    try:
        f=open(serfile, "rb")
    except:
        print('erreur ouverture fichier : ',serfile)
        
    # lecture entete ficier ser
    b=np.fromfile(serfile, dtype='int8',count=14)
    FileID=b.tobytes().decode()
    offset=14
    
    LuID=np.fromfile(serfile, dtype=np.uint32, count=1, offset=offset)
    offset=offset+4
    
    ColorID=np.fromfile(serfile, dtype='uint32', count=1, offset=offset)
    offset=offset+4
    
    little_Endian=np.fromfile(serfile, dtype='uint32', count=1,offset=offset)
    offset=offset+4
    
    Width=np.fromfile(serfile, dtype='uint32', count=1,offset=offset)
    Width=Width[0]
    print('Width :', Width)
    offset=offset+4
    
    Height=np.fromfile(serfile, dtype='uint32', count=1,offset=offset)
    Height=Height[0]
    print('Height :',Height)
    offset=offset+4
    
    PixelDepthPerPlane=np.fromfile(serfile, dtype='uint32', count=1,offset=offset)
    PixelDepthPerPlane=PixelDepthPerPlane[0]
    offset=offset+4
    
    FrameCount=np.fromfile(serfile, dtype='uint32', count=1,offset=offset)
    FrameCount=FrameCount[0]
    print('Nb de frame :',FrameCount)
    offset=offset+4
    
    b=np.fromfile(serfile, dtype='int8',count=40,offset=offset)
    Observer=b.tobytes().decode()
    print ('Observer :',Observer)
    offset=offset+40
    
    b=np.fromfile(serfile, dtype='int8',count=40,offset=offset)
    Instrument=b.tobytes().decode()
    print ('Instrument :',Instrument)
    offset=offset+40
    
    b=np.fromfile(serfile, dtype='int8',count=40,offset=offset)
    Telescope=b.tobytes().decode()
    print ('Telescope :', Telescope)
    print(' ')
    offset=offset+40
    
    DTime=np.fromfile(serfile, dtype='int64', count=1,offset=offset)
    DTime=DTime[0]
    offset=offset+8
    DTimeUTC=np.fromfile(serfile, dtype='int64', count=1,offset=offset)
    DTimeUTC=DTimeUTC[0]
    
    
    #cv2.namedWindow('Ser', cv2.WINDOW_NORMAL)
    #cv2.resizeWindow('Ser', Width, Height)
    #cv2.moveWindow('Ser', 100, 0)
    
    ok_flag=True              # Flag pour sortir de la boucle de lexture avec exit
    count=Width*Height        # Nombre d'octet d'une trame
    FrameIndex=1              # Index de trame
    offset=178                # Offset de l'entete fichier ser

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
    
        num=np.fromfile(serfile, dtype='uint16',count=count, offset=offset)
        num=np.reshape(num,(Height,Width))
        if flag_rotate:
            num=np.rot90(num)
        
        #ajoute les trames pour creer une image haut snr pour extraire
        #les parametres d'extraction de la colonne du centre de la raie et la
        #corriger des distorsions
        mydata=np.add(num,mydata)
        
        #increment la trame et l'offset pour lire trame suivant du fichier .ser
        FrameIndex=FrameIndex+1
        offset=178+FrameIndex*count*2
    
    f.close()
    
    # calcul de l'image moyenne
    myimg=mydata/(FrameIndex-1)             # Moyenne
    myimg=np.array(myimg, dtype='uint16')   # Passe en entier 16 bits
    AxeY= hdr['NAXIS2']                     # Hauteur de l'image
    AxeX= hdr['NAXIS1']                     # Largeur de l'image
    myimg=np.reshape(myimg, (AxeY, AxeX))   # Forme tableau X,Y de l'image moyenne
    savefich=basefich+'_mean'               # Nom du fichier de l'image moyenne
    
    # sauve en fits l'image moyenne avec suffixe _mean
    SaveHdu=fits.PrimaryHDU(myimg,header=hdr)
    SaveHdu.writeto(savefich+'.fit',overwrite=True)
    
    #debug
    #t1=float(time.time())
    #print('image mean saved',t1-t0)
    
    #affiche image moyenne
    cv2.namedWindow('Ser', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Ser', AxeX, AxeY)
    cv2.moveWindow('Ser', 100, 0)
    cv2.imshow ('Ser', myimg)
    if cv2.waitKey(2000) == 27:                     # exit if Escape is hit
           cv2.destroyAllWindows()
           sys.exit()
    
    cv2.destroyAllWindows()
    
    # appel au module d'extraction, reconstruction et correction
    #
    # basefich: nom du fichier ser sans extension et sans repertoire
    # dx: decalage en pixel par rapport au centre de la raie 
    try:
        Shift=int(Shift)
    except:
        Shift=0
    
    frame, header, cercle=sol.solex_proc(serfile,Shift,flag_display)
    
    base=os.path.basename(serfile)
    basefich=os.path.splitext(base)[0]
   
    ih=frame.shape[0]
    newiw=frame.shape[1]
    
    
    # gere reduction image png
    if ih>600:
        sc=0.5
        
    # gere reduction image png
    if ih>2000:
        sc=0.3

        
    cv2.namedWindow('sun0', cv2.WINDOW_NORMAL)
    cv2.moveWindow('sun0', -10, 0)
    cv2.resizeWindow('sun0', (int(newiw*sc), int(ih*sc)))
    cv2.imshow('sun0',frame)
    
    
    cv2.namedWindow('sun', cv2.WINDOW_NORMAL)
    cv2.moveWindow('sun', 0, 0)
    cv2.resizeWindow('sun', (int(newiw*sc), int(ih*sc)))
    
    cv2.namedWindow('sun2', cv2.WINDOW_NORMAL)
    cv2.moveWindow('sun2', 200, 0)
    cv2.resizeWindow('sun2', (int(newiw*sc), int(ih*sc)))
    
    cv2.namedWindow('sun3', cv2.WINDOW_NORMAL)
    cv2.moveWindow('sun3', 400, 0)
    cv2.resizeWindow('sun3', (int(newiw*sc), int(ih*sc)))

    cv2.namedWindow('clahe', cv2.WINDOW_NORMAL)
    cv2.moveWindow('clahe', 600, 0)
    cv2.resizeWindow('clahe',(int(newiw*sc), int(ih*sc)))
    
    # create a CLAHE object (Arguments are optional)
    #clahe = cv2.createCLAHE(clipLimit=0.8, tileGridSize=(5,5))
    clahe = cv2.createCLAHE(clipLimit=0.8, tileGridSize=(2,2))
    cl1 = clahe.apply(frame)
    
    
    frame1=np.copy(frame)
    Seuil_bas=np.percentile(frame1, 25)
    Seuil_haut=np.max(frame1)
    frame1[frame1>Seuil_haut]=65000
    #print('seuil bas', Seuil_bas)
    #print('seuil haut', Seuil_haut)
    fc=(frame1-Seuil_bas)* (65000/(Seuil_haut-Seuil_bas))
    fc[fc<0]=0
    frame_contrasted=np.array(fc, dtype='uint16')
    cv2.imshow('sun',frame_contrasted)
    #cv2.waitKey(0)
    
    frame1=np.copy(frame)
    Seuil_haut=np.max(frame1)
    Seuil_bas=(Seuil_haut*0.5)
    #print('seuil bas HC', Seuil_bas)
    #print('seuil haut HC', Seuil_haut)
    frame1[frame1>Seuil_haut]=65000
    fc2=(frame1-Seuil_bas)* (65000/(Seuil_haut-Seuil_bas))
    fc2[fc2<0]=0
    frame_contrasted2=np.array(fc2, dtype='uint16')
    cv2.imshow('sun2',frame_contrasted2)
    #cv2.waitKey(0)
    
    frame1=np.copy(frame)
    Seuil_haut=np.max(frame1)*0.6
    Seuil_bas=0
    
    #print('seuil bas protu', Seuil_bas)
    #print('seuil haut protu', Seuil_haut)
    frame1[frame1>Seuil_haut]=65000
    fc2=(frame1-Seuil_bas)* (65000/(Seuil_haut-Seuil_bas))
    fc2[fc2<0]=0
    x0=cercle[0]
    y0=cercle[1]-1
    r=int(cercle[2]*0.5)+1
    frame_contrasted3=np.array(fc2, dtype='uint16')
    frame_contrasted3=cv2.circle(frame_contrasted3, (x0,y0),r,80,-1)
    cv2.imshow('sun3',frame_contrasted3)
    #cv2.waitKey(0)
    
    Seuil_bas=np.percentile(cl1, 25)
    Seuil_haut=np.max(cl1)*1.05
    cc=(cl1-Seuil_bas)*(65000/(Seuil_haut-Seuil_bas))
    cc[cc<0]=0
    cc=np.array(cc, dtype='uint16')
    cv2.imshow('clahe',cc)
    cv2.waitKey(tempo)  #affiche 15s et continue

    #sauvegarde en png pour appliquer une colormap par autre script
    cv2.imwrite(basefich+'_disk.png',frame_contrasted)
    #sauvegarde en png pour appliquer une colormap par autre script
    cv2.imwrite(basefich+'_diskHC.png',frame_contrasted2)
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
    cv2.moveWindow('color',int(newiw*sc), 0)
    cv2.imshow('color',imC)
    cv2.waitKey(5000)
    cv2.imwrite(basefich+'_color.png',imC)
    """
    
    #sauvegarde le fits
    frame=np.array(cl1, dtype='uint16')
    DiskHDU=fits.PrimaryHDU(frame,header)
    DiskHDU.writeto(basefich+'_clahe.fit', overwrite='True')

    cv2.destroyAllWindows()

