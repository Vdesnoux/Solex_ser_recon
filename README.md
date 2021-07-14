Solar disk reconstruction from spectroheliography SER files

Usage: Launch SHG_MAIN (double click)

In the pysimpleGUI window enter the name of the file to be processed
Check the "display" box for a live reconstruction display
Shift: offset in pixels from the minimum of the line to reconstruct on another wavelength
Y/X ratio: enter a specific Y/X ratio, or leave blank for auto-correction
Slant: enter a specific slant angle in degrees, or leave blank for auto-correction

If "save .fit" is checked, the following files are stored in the directory of the SER file:

- xx_mean.fit: average image of all the frames of the SER video of the spectral line
- xx_img.fit: monochromatic raw image
- xx_corr.fit: image corrected for outliers
- xx_circle.fit: circularized image
- xx_flat.fit: corrected image of the flat
- xx_recon.fit: final image, corrected for slant

If "Save CLAHE image only" is ticked then only the final image will be saved