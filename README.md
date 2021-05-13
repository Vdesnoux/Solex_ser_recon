# Solex_ser_recon
Reonstruction disque solaire à partir de fichiers ser spectroheliographie

Fichier de lancement: Solex_ser_recon
Appel le module ser_recon

Dans le fenetre de pysimpleGUI entrer le nom du fichier ser à traiter
Cocher la case "display" pour un affichage de la reconstruction en live
Shift: decalage en pixels par rapport au minimum de la raie pour reconstruire sur une autre longueur d'onde
exemple: decalage de n pixels pour reconstruire le continuum

Si affichage live, à la fin de la reconstruction appuyer sur "enter" pour coninuer les traitements

A la fin, 4 images sont affichées - appuyer sur "enter" pour sortir

Les fichiers suivants sont stockés dans le repertoire du fichier ser
- xx_mean.fit: image moyenne de toutes les trames de la video ser du spectre
- xx_img.fit: image brute monochromatique
- xx_corr.fit: image corrigée des lignes abhérantes
- xx_circle.fit: image circularisée
- xx_flat.fit: image corrigée du flat
- xx_recon.fit: image finale, corrigée du slant

