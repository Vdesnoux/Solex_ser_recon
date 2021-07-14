Solar disk reconstruction from SHG (spectroheliography) SER files

Install the most recent version of Python from python.org. During Windows installation, check the box to update the PATH.

For Windows, double click the windows_setup file to install the needed Python libraries.

Usage: launch SHG_MAIN (by double clicking under Windows).

In the Python GUI window, enter the name of the SER file(s) to be processed. Batch processing is possible.

Check the "Show images" box for a live reconstruction display (and some additional live display windows afterwards). This modestly increases processing time.

If "Save .fit files" box is checked, the following files will be stored in the same directory as the SER file:

- xx_mean.fit: average image of all the frames in the SER video of the spectral line
- xx_img.fit: raw image reconstruction
- xx_corr.fit: image corrected for outliers
- xx_circle.fit: circularized image
- xx_flat.fit: corrected flat image
- xx_recon.fit: final image, corrected for slant
- xx_clahe.fit: final image, with Contrast Limited Adaptive Histogram Equalization

If "Save CLAHE image only" box is checked, then only the final PNG image with Contrast Limited Adaptive Histogram Equalization will be saved.

Y/X ratio: enter a specific Y/X ratio, if this is known. Leave blank for auto-correction.

Slant angle: enter a specific slant angle in degrees. If angle correction is unknown, try first with zero. Leave blank for auto-correction.

Pixel offset: offset in pixels from the minimum of the line to reconstruct the image on another wavelength.

