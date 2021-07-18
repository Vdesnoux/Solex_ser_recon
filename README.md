# Solex_ser_recon
Reonstruction disque solaire à partir de fichiers ser spectroheliographie

Fichier de lancement: Inti_ser_recon
Appel le module Inti_recon

Dans le fenetre de pysimpleGUI entrer le nom du fichier ser à traiter

Suppression de "Cocher la case "display" pour un affichage de la reconstruction en live"

Angle de tilt: si a zero calcul automatique, si valeur differente de zero le calcul utilisera cette valeur

Ratio SY/SX: si a zero calcul automatique, si valeur differente de zero le calcul utilisera cette valeur

Cocher la case pour afficher un disque noir sur l'image png dont les seuils permettent de faire ressortir les protuberances

Cocher la case pour ne sauvegarder en fits que les deux images finales _recon.fits et _clahe.fits

Shift: decalage en pixels par rapport au minimum de la raie pour reconstruire sur une autre longueur d'onde
exemple: decalage de n pixels pour reconstruire le continuum

Suppression de "Si affichage live, à la fin de la reconstruction appuyer sur "enter" pour coninuer les traitements"

A la fin, 4 images sont affichées - appuyer sur "enter" pour sortir ou laisser faire la temporisation d'une minute

Si plusieurs fichiers ser sont selectionnés, la temporisation est reduite a 10 ms

Les fichiers suivants sont stockés dans le repertoire du fichier ser
- xx_mean.fits: image moyenne de toutes les trames de la video ser du spectre
- xx_img.fits: image brute monochromatique
- xx_corr.fits: image corrigée des lignes aberrantes
- xx_circle.fits: image circularisée
- xx_flat.fits: image corrigée du flat
- xx_recon.fits: image finale, corrigée du slant
- xx_clahe.fits: image finale, traitement par Contrast Local Adapative Histogram Enhancement (CLAHE)

