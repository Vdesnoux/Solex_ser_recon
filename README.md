# Solex Ser Recon - Core Module

![](https://img.shields.io/badge/Python-3.8-green "Python 3.8")

Ce dépôt contient le core du processus de recontruction du disque solaire à partir des fichiers d'acquisitions .SER dans le cadre d'utilisation du Sol'Ex.

Plus d'informations sur le projet Sol'Ex ici : [http://www.astrosurf.com/solex/](http://www.astrosurf.com/solex/)

L'objectif est de maintenir le core en tant que module **sans interface utilisateur**. Le fichier Inti_ser_recon.py contient une GUI pour les tests durant les développement, attention ce n'est pas la version utilisateur finale. Les développements du module Core, inti_recon.py doivent être indépendants de la GUI.


### Récupérer le code pour execution

Vous pouvez utiliser le code de ce dépôt sur votre machine personnelle :

- En récupérant le code en téléchargeant le package entier via le bouton **Code**
![](https://docs.github.com/assets/images/help/repository/code-button.png)


- En utilisant git via HTTPS ou en SSH. Cliquez sur "Clone with HTTPS/SSH" puis dans votre CMD Window ou terminal linux/macos

`git clone https://github.com/Vdesnoux/Solex_ser_recon.git`

![](https://docs.github.com/assets/images/help/repository/https-url-clone.png)


### Contribuer au dépôt

Si vous souhaitez contribuer au dépôt, consulter le document **CONTRIBUTING.md** présent sur le dépôt.


## Installation (développeurs)


### Python
Version recommandée : Python 3.8


### Environnement virtuel (optionnel)

Installation
`pip install virtualenv`

Creation de l'environnement
`virtualenv venv`

Activation de l'environnement
`source venv/bin/activate`



### Requirements

La liste des dépendances se trouve dans le fichier requirements.txt

- opencv_python==4.4.0.46
- numpy==1.19.2
- astropy==4.2
- PySimpleGUI==4.38.0
- lsq-ellipse==2.0.1

Pour une installation automatique taper :

 `pip install -r requirements.txt` 


## Lancement & Utilisation

- Dans le fenetre de pysimpleGUI entrer le nom du fichier ser à traiter

- Angle de tilt: si a zero calcul automatique, si valeur differente de zero le calcul utilisera cette valeur

 - Ratio SY/SX: si a zero calcul automatique, si valeur differente de zero le calcul utilisera cette valeur

- Cocher la case pour afficher un disque noir sur l'image png dont les seuils permettent de faire ressortir les protuberances

- Cocher la case pour ne sauvegarder en fits que les deux images finales _recon.fits et _clahe.fits

- Shift: decalage en pixels par rapport au minimum de la raie pour reconstruire sur une autre longueur d'onde
exemple: decalage de n pixels pour reconstruire le continuum


- Lors de l'affichae final des 4 images - appuyer sur "enter" pour sortir ou laisser faire la temporisation d'une minute

- Si plusieurs fichiers ser sont selectionnés, la temporisation est reduite a 10 ms :

    Les fichiers suivants sont stockés dans le repertoire du fichier ser
    - xx_mean.fits: image moyenne de toutes les trames de la video ser du spectre
    - xx_img.fits: image brute monochromatique
    - xx_corr.fits: image corrigée des lignes aberrantes
    - xx_circle.fits: image circularisée
    - xx_flat.fits: image corrigée du flat
    - xx_recon.fits: image finale, corrigée du slant
    - xx_clahe.fits: image finale, traitement par Contrast Local Adapative Histogram Enhancement (CLAHE)

