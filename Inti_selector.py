# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 18:24:02 2021

@author: valer

Version O.1
- ajout de erase graphique pour eviter les supperpositions d'images
- bug click dans list - oubli de graph move
- adaptation au nouveau log de exp par sharpcap
"""

import numpy as np
#import matplotlib.pyplot as plt
#from astropy.io import fits
import PySimpleGUI as sg
import os, fnmatch
import io

#import cv2
import sys
import yaml
from PIL import Image
import time


global mydic_files
current_version = '        Inti Selector V0.1 by V.Desnoux'

def read_camsetting (fich):
    basefich=fich[1:9]+'.CameraSettings.txt'
    d = {}
    try:
        with open(basefich) as f:
            for line in f:
                try:
                    (key, val) = line.split('=')
                    d[key] = val[:-1]
                except:
                    pass
    except:
        print('file not found : ', basefich)
    
    return d

def get_gainexp (fich):
    # lexture fichier de camera setting 
    cam_dict=read_camsetting(fich)
    try:
        Gain=cam_dict['Gain']
        # convert in ms
        try:
            Exp=float(cam_dict['Exposure'])*1000
            Exp=str(float("{:.2f}".format(Exp)))+' ms'
        except:
            Exp=cam_dict['Exposure']
    except:
        Gain='error'
        Exp='error'
    cam_text=fich +'    Gain: '+Gain+' Exp: '+Exp
    return cam_text

def img_resize (nomfich,dim):
    image = Image.open(nomfich)
    image.thumbnail((dim, dim))
    bio = io.BytesIO()
    image.save(bio, format="PNG")
    out=bio.getvalue()
    #with io.BytesIO() as output:
        #image.save(output, format="PNG")
        #out = output.getvalue()
    return out



"""
------------------------------------------------------------------------------
------------------------------------------------------------------------------
INTI Selector starts here

Permet la comparaison d'images png pour selectioner la meilleure
- image de reference à droite
- image de comparaison à gauche
- boutons pour zoomer et se deplacer dans l'image
- sauve dans fichier _log.txt les noms des fichiers qu'on logge 
------------------------------------------------------------------------------
------------------------------------------------------------------------------
"""
# recupere les parametres utilisateurs enregistrés lors de la session
# precedente dans un fichier ini.yamp 

#my_ini=os.path.dirname(sys.argv[0])+'/inti.yaml'
my_ini=os.getcwd()+'/inti.yaml'
my_dictini={'directory':'', 'dec_doppler':3, 'dec_cont':15}
#print('myini de depart:', my_ini)

try:
    
    #print('mon repertoire : ', mydir_ini)
    with open(my_ini, "r") as f1:
        my_dictini = yaml.safe_load(f1)
    WorkDir=my_dictini['directory']
except:
    WorkDir=''

"""
------------------------------------------------------------------------------
GUI fenetre appli
------------------------------------------------------------------------------
"""

sg.theme('Dark2')
sg.theme_button_color(('white', '#500000'))

colonne0 =[
    [sg.Graph(canvas_size=(650,650),graph_bottom_left=(0, 0),graph_top_right=(650, 650),drag_submits=True, enable_events=True,key='-CROP0-')],
    [sg.Text('', size=(40,1),key='-NOM0-')]
    ]

colonne1= [
    [sg.Graph(canvas_size=(650,650),graph_bottom_left=(0, 0),graph_top_right=(650, 650),drag_submits=True, enable_events=True,key='-CROP1-')],
    [sg.Text('', size=(40,1),key='-NOM1-')]
    ]

colonne_mid=[
    [sg.Listbox(values='', select_mode='extended',size=(20,10), enable_events=True, key='-LIST-')],
    [sg.Text('',size=(15,3))],
    [sg.Text('',size=(15,3))],
    [sg.Button ("Zoom In", size=(10,1))],
    [sg.Button("Zoom Out", size=(10,1)),],
    [sg.Text('',size=(15,3))],
    [sg.Text('',size=(15,3))],
    [sg.Button ("Reset", size=(10,1))]
    ]
layout = [
    [sg.Text('Directory', size=(15, 1)), sg.InputText(default_text='',size=(100,1),enable_events=True,key='-FOLDER-'),
     sg.FolderBrowse('Open',initial_folder=WorkDir), 
     sg.Combo(['*_clahe.png','*_protus.png', '*_diskHC.png','*_raw.png'],default_value='*_clahe.png',enable_events=True,key='-PAT-'),
     sg.Text(current_version, size=(30, 1),text_color='Tan', font=("Arial", 8, "italic"))],
    [sg.Column(colonne0), sg.Column(colonne_mid,element_justification='center'),sg.Column(colonne1)],
    [sg.Button("Previous", size=(15,1)),sg.Button("Next", size=(15,1)),
     sg.Button ("Keep", size=(15,1)),sg.Button("Log", size=(15,1)),
     sg.Button ("Selected", size=(15,1)),
     sg.Button ("Post Process", size=(25,1), visible=False),
     sg.Button("Exit")]
    ]

window = sg.Window('INTI Selector', layout, finalize=True,location=(0,0), return_keyboard_events=True)
window['-FOLDER-'].update(WorkDir) 
window.BringToFront()

"""
----------------------------------------------------------------------------
Initialisation des variables
----------------------------------------------------------------------------
"""
i=0         # indice du nom de fichier dans la liste
mylog=[]    # liste qui contient les noms de fichiers que l'on log
nb_img=1000 #valeur max dans un repertoire

#coordonnées en haut à droite
x0=0
y0=650

#ecart position du graph
dx0=0
dy0=0

#dimension du canvas
dim0=650
dim=dim0

#ajoute ou retire 300 pixels pour resize image plus ou moins grande (zoom)
step_zoom=100

#deplacement du panning
step_move=100

# indice du fichier qui est dans l'emplacement de reference
indice_ref=0

# reference les zones images et la liste
graph0=window.Element("-CROP0-")
graph1=window.Element("-CROP1-")
sel_list=[]

#flag post_process
flag_postproc=False

if WorkDir !='':
    # on charge le premier fichier dans les deux fenetres
    os.chdir(WorkDir)
    pattern='*_clahe.png'
    mylog.append(pattern+'\n')
    clahe_files=fnmatch.filter(os.listdir(WorkDir), pattern)
    bio=img_resize(clahe_files[0],dim)
    combo = get_gainexp(clahe_files[0])
    window['-NOM0-'].update(combo)
    window['-NOM1-'].update(combo)
    
    graph0.DrawImage(data=bio, location=(x0,y0))
    graph1.DrawImage(data=bio, location=(x0,y0))
    nb_img=len(clahe_files)
    acq_files=[acq_files[:10]+'log.txt' for acq_files in clahe_files]

    # met a jour la listbox

    window.Element('-LIST-').update(values=clahe_files)
    
# pour la souris
dragging = False
start_point = end_point = prior_rect = None


"""
-----------------------------------------------------------------------------
Boucle events de la window
-----------------------------------------------------------------------------
"""
while True:
    event, values = window.read()
    

    
    if event=='-PAT-':
        i=0
        dx0=0
        dy0=0
        x0=0
        y0=650
        indice_ref=0
        dim=dim0
        pattern=values['-PAT-']
        mylog.append(pattern)
        graph0.erase()
        graph1.erase()
        sel_list=[]
        sel_indice=0
        clahe_files=fnmatch.filter(os.listdir(WorkDir), pattern)
        window.Element('-LIST-').update(values=clahe_files)
        bio=img_resize(clahe_files[0],dim)
        combo = get_gainexp(clahe_files[i])
        window['-NOM0-'].update(combo)
        window['-NOM1-'].update(combo)
        graph0.DrawImage(data=bio, location=(x0,y0))
        graph1.DrawImage(data=bio, location=(x0,y0))
        nb_img=len(clahe_files)

        
    if event=='Previous':
        if i>0:
            graph1.erase()
            i=i-1
            bio=img_resize(clahe_files[i],dim)
            combo = get_gainexp(clahe_files[i])
            window['-NOM1-'].update(combo)
            graph1.DrawImage(data=bio, location=(x0,y0))
            graph1.move(dx0,dy0)
        
    if event=='Next':
        if i<(nb_img-1):
            graph1.erase()
            i=i+1
            bio=img_resize(clahe_files[i],dim)
            combo = get_gainexp(clahe_files[i])
            window['-NOM1-'].update(combo)
            graph1.DrawImage(data=bio,location=(x0,y0))
            graph1.move(dx0,dy0)
    
    if event=="Keep":
        graph0.erase()
        bio=img_resize(clahe_files[i],dim)
        # lexture fichier de camera setting 
        combo = get_gainexp(clahe_files[i])
        window['-NOM0-'].update(combo)
        graph0.DrawImage(data=bio, location=(x0,y0))
        graph0.move(dx0,dy0)
        indice_ref=i
        # we log also
        combo = get_gainexp(clahe_files[i])
        mylog.append(combo +'\n')
        sel_list.append(i)
        window.Element('-LIST-').update(set_to_index=sel_list, scroll_to_index=i)
        
    if event=="Zoom In" or event=='MouseWheel:Up':
    
        if dim <=8000:
            graph1.erase()
            graph0.erase()
            dim=dim+step_zoom
            x0=x0-step_zoom/2
            y0=y0+step_zoom/2
            bio=img_resize(clahe_files[indice_ref],dim)
            graph0.DrawImage(data=bio, location=(x0,y0))
            graph0.move(dx0,dy0)
            bio=img_resize(clahe_files[i],dim)
            graph1.DrawImage(data=bio, location=(x0,y0))
            graph1.move(dx0,dy0)
        else:
            print ('image plus grande que 8000 pixels')
    
    if event=="Zoom Out" or event=='MouseWheel:Down':
        if dim >=(650+step_zoom):
            graph1.erase()
            graph0.erase()
            dim=dim-step_zoom
            if dim>=650:
                x0=x0+step_zoom/2
                y0=y0-step_zoom/2
            else:
                x0=0
                y0=650
                graph0.erase()
                graph1.erase()
            bio=img_resize(clahe_files[indice_ref],dim)
            graph0.DrawImage(data=bio, location=(x0,y0))
            graph0.move(dx0,dy0)
            bio=img_resize(clahe_files[i],dim)
            graph1.DrawImage(data=bio, location=(x0,y0))
            graph1.move(dx0,dy0)
        else:
            print ('image sera trop petite')
    
           
    
    if event=="-FOLDER-":
        WorkDir = values['-FOLDER-']
        os.chdir(WorkDir)
        pattern='*_clahe.png'
        clahe_files=fnmatch.filter(os.listdir(WorkDir), pattern)
        if len(clahe_files)!=0 :
            bio=img_resize(clahe_files[0],dim)
            combo = get_gainexp(clahe_files[0])
            window['-NOM0-'].update(combo)
            window['-NOM1-'].update(combo)
            graph0.DrawImage(data=bio, location=(x0,y0))
            graph1.DrawImage(data=bio, location=(x0,y0))
            nb_img=len(clahe_files)
            window.Element('-LIST-').update(values=clahe_files)
        else:
            print('no files found')
        
    if event=="Log":
        combo = get_gainexp(clahe_files[i])
        mylog.append(combo +'\n')
        sel_list.append(i)
        window.Element('-LIST-').update(set_to_index=sel_list, scroll_to_index=i)
        
    if event=="Selected" and len(sel_list)!=0:
        clahe_files=[clahe_files[k] for k in sel_list]
        window.Element('-LIST-').update(values=clahe_files)
        i=0
        indice_ref=0
        nb_img=len(clahe_files)
        sel_list=[]
        mylog.append("selection")
        graph0.erase()
        graph1.erase()
        bio=img_resize(clahe_files[0],dim)
        combo = get_gainexp(clahe_files[i])
        window['-NOM0-'].update(combo)
        window['-NOM1-'].update(combo)
        graph0.DrawImage(data=bio, location=(x0,y0))
        graph1.DrawImage(data=bio, location=(x0,y0))
        
    if event=="-LIST-" and len(values['-LIST-'])!=0 :

        i=clahe_files.index(values['-LIST-'][len(values['-LIST-'])-1])
        graph1.erase()
        bio=img_resize(clahe_files[i],dim)
        combo = get_gainexp(clahe_files[i])
        window['-NOM1-'].update(combo)
        graph1.DrawImage(data=bio, location=(x0,y0))
        graph1.move(dx0,dy0)

    if event==sg.WIN_CLOSED or event=='Exit': 
        break

    if event=="Reset":
        x0=0
        y0=650
        dim=dim0
        dx0=dy0=0
        graph0.erase()
        graph1.erase()
        bio=img_resize(clahe_files[i],dim)
        graph1.DrawImage(data=bio, location=(x0,y0))
        bio=img_resize(clahe_files[indice_ref],dim)
        graph0.DrawImage(data=bio, location=(x0,y0))
    
    if event=='-CROP1-' or event=='-CROP0-':
        if event=='-CROP1-':
            x,y=values['-CROP1-']
        if event=='-CROP0-':
            x,y=values['-CROP0-']
        if not dragging:
            start_point=(x,y)
            dragging =True
            Lastxy=x,y
        else:
            end_point=(x,y)
            
        delta_x, delta_y= x-Lastxy[0], y-Lastxy[1]
        graph1.move(delta_x, delta_y)
        graph0.move(delta_x, delta_y)
        Lastxy=x,y
        
    if event.endswith('+UP'):
        #print (event)
        try:
            dx0=dx0+(end_point[0]-start_point[0])
            dy0=dy0+(end_point[1]-start_point[1])
        except:
            pass
        start_point, end_point = None, None  # enable grabbing a new rect
        dragging = False
        
    if event=="Post Process":
        flag_postproc=True
        file_to_proc=clahe_files[indice_ref]
        print(file_to_proc)
        break


window.close()

"""
-----------------------------------------------------------------------------
Sortie de l'application
-----------------------------------------------------------------------------
"""
#print (my_ini)
# on sauve les noms de fichiers loggés
with  open(str(int(time.time()))+'_log.txt', "w") as logfile:
        logfile.writelines(mylog)

#met a jour le repertoire si on a changé dans le fichier ini.yaml
my_dictini['directory']=WorkDir
my_dictini['dec doppler']=3
my_dictini['dec cont']=15

try:
    
    with open(my_ini, "w") as f1:
        yaml.dump(my_dictini, f1, sort_keys=False)
except:
    print('erreur ecriture inti.yaml')

if flag_postproc==False :
    sys.exit()

sg.theme('Dark2')
sg.theme_button_color(('white', '#500000'))

colonne0 =[
    [sg.Graph(canvas_size=(650,650),graph_bottom_left=(0, 0),graph_top_right=(650, 650),drag_submits=True, enable_events=True,key='-IMG-')],
    [sg.Text('', size=(35,1),key='-TEXT-')]
    ]

colonne_droite=[
    [sg.Slider(orientation ='vertical',enable_events=True, key='-SLIDC-', range=(1,10)),sg.Slider(orientation ='vertical', enable_events=True, key='-SLIDB-',range=(1,10))],
    [sg.Text('',size=(15,3))],
    [sg.Button ("Reset", size=(10,1))]
    ]
layout = [
    [sg.Column(colonne0), sg.Column(colonne_droite,element_justification='center')],
    [sg.Button("Save"), sg.Button("Exit")]
    ]

window = sg.Window('INTI processor', layout, finalize=True,location=(0,0), return_keyboard_events=True)
window.BringToFront()

#initialisation diverses
graph=window.Element("-IMG-")
bio=img_resize(file_to_proc,dim)
combo = get_gainexp(file_to_proc)
window['-TEXT-'].update(combo)
graph.DrawImage(data=bio, location=(x0,y0))

#coordonnées en haut à droite
x0=0
y0=650

#ecart position du graph
dx0=0
dy0=0

#dimension du canvas
dim0=650
dim=dim0

#ajoute ou retire 300 pixels pour resize image plus ou moins grande (zoom)
step_zoom=100

#deplacement du panning
step_move=100

# pour la souris
dragging = False
start_point = end_point = prior_rect = None

"""
-----------------------------------------------------------------------------
Boucle events de la window
-----------------------------------------------------------------------------
"""
while True:
    event, values = window.read()
    
    
    if event=='MouseWheel:Up':
    
        if dim <=8000:
            dim=dim+step_zoom
            x0=x0-step_zoom/2
            y0=y0+step_zoom/2
            bio=img_resize(file_to_proc,dim)
            graph.DrawImage(data=bio, location=(x0,y0))
            graph.move(dx0,dy0)
            
        else:
            print ('image plus grande que 8000 pixels')
    
    if event=='MouseWheel:Down':
        if dim >=(650+step_zoom):
            dim=dim-step_zoom
            if dim>=650:
                x0=x0+step_zoom/2
                y0=y0-step_zoom/2
            else:
                x0=0
                y0=650
                graph.erase()
            bio=img_resize(file_to_proc,dim)
            graph.DrawImage(data=bio, location=(x0,y0))
            graph.move(dx0,dy0)
            
        else:
            print ('image sera trop petite')
            
    if event=='-IMG-':
        x,y=values['-IMG-']
        
        if not dragging:
            start_point=(x,y)
            dragging =True
            Lastxy=x,y
        else:
            end_point=(x,y)
            
        delta_x, delta_y= x-Lastxy[0], y-Lastxy[1]
        graph.move(delta_x, delta_y)
      
        Lastxy=x,y
        
    if event.endswith('+UP'):
        #print (event)
        try:
            dx0=dx0+(end_point[0]-start_point[0])
            dy0=dy0+(end_point[1]-start_point[1])
        except:
            pass
        start_point, end_point = None, None  # enable grabbing a new rect
        dragging = False
    
    if event=="Reset":
        x0=0
        y0=650
        dim=dim0
        dx0=dy0=0
        graph.erase()
        bio=img_resize(file_to_proc,dim)
        graph.DrawImage(data=bio, location=(x0,y0))

    if event=="Save":
        print ("on sauve la : ", WorkDir+"t"+file_to_proc)
    
    if event==sg.WIN_CLOSED or event=='Exit': 
        break
    
    if event=="-SLIDC-":
        print("event slider C")
        #read the image
        im = Image.open(file_to_proc)
        print(im.mode)
        im_array=np.array(im)
        print (im_array.shape, im_array.dtype)
        factor = 1.5 
        #im = ImageEnhance.Contrast(im).enhance(factor)
        im.thumbnail((dim, dim))
        bio = io.BytesIO()
        im.save(bio, format="PNG")
        out=bio.getvalue()
        graph.DrawImage(data=bio, location=(x0,y0))
        

    
    
    

    
window.close()
sys.exit()

