from solex_util import *

import skimage
import skimage.feature
import sys

import math
import numpy as np
import matplotlib.pyplot as plt

from skimage import data
from skimage import transform
from skimage import filters

import cv2

import scipy
from ellipse import LsqEllipse
from matplotlib.patches import Ellipse

NUM_REG = 6 #6 # include biggest NUM_REG regions in fit


filename = 'D:/SHG examples/16_33_15/16_33_15_corr.png' #sys.argv[1]
filename = 'D:/SHG examples/13_06_21/Test_161540_diskHC.png' #sys.argv[1]



def dofit(X):
    X1 = X[:, 0]
    X2 = X[:, 1]
    reg = LsqEllipse().fit(X)
    center, width, height, phi = reg.as_parameters()
    return center, width, height, phi, reg.return_fit(n_points=100)


def two_step(X):
    center, width, height, phi, _ = dofit(X)
    mat = np.array([np.array([np.cos(phi), np.sin(phi)])/width, np.array([-np.sin(phi), np.cos(phi)])/height])
    Xr = mat @ (X - np.array(center)).T
    X1r = Xr[0, :]
    X2r = Xr[1, :]   
    values = np.linalg.norm(Xr, axis = 0) - 1
    #print(np.mean(values), np.std(values), max(values), min(values))
    anomaly_threshold = max(values)
    X = X[values > -max(values)]
    center, width, height, phi, ellipse_points = dofit(X)
    mat = np.array([np.array([np.cos(phi), np.sin(phi)])/width, np.array([-np.sin(phi), np.cos(phi)])/height])
    Xr = mat @ (X - np.array(center)).T
    X1r = Xr[0, :]
    X2r = Xr[1, :]    
    values = np.linalg.norm(Xr, axis = 0) - 1
    #print(np.mean(values), np.std(values), max(values), min(values))
    ratio = width / height
    return mat@np.array(center), height, phi, ratio, X, ellipse_points

def correct_image(image, phi, ratio):
    logme('Y/X ratio : ' + "{:.3f}".format(ratio))
    logme('Tilt angle : ' + "{:.3f}".format(math.degrees(phi)) + " degrees")
    mat = np.array([[np.cos(phi), np.sin(phi)], [-np.sin(phi), np.cos(phi)]]) @ np.array([[1/ratio, 0], [0, 1]])
    mat3 = np.zeros((3, 3))
    mat3[:2, :2] = mat
    mat3[2, 2] = 1
    corners = np.array([[0,0], [0, image.shape[0]], [image.shape[1], 0], [image.shape[1], image.shape[0]]])
    new_corners = (np.linalg.inv(mat) @ corners.T).T # use inverse because we represent mat3 as inverse of transform
    new_h = np.max(new_corners[:, 1]) - np.min(new_corners[:, 1])
    new_w = np.max(new_corners[:, 0]) - np.min(new_corners[:, 0])
    mat3 = mat3 @ np.array([[1, 0, np.min(new_corners[:, 0])], [0, 1, np.min(new_corners[:, 1])], [0,   0,    1]]) # apply translation to prevent clipping
    my_transform = transform.ProjectiveTransform(matrix=mat3)
    corrected_img = transform.warp(image, my_transform, output_shape = (np.ceil(new_h),np.ceil(new_w)), cval  = image[0, 0])
    corrected_img = (2**16*corrected_img).astype(np.uint16) # note : 16-bit output
    return corrected_img



def ellipse_to_circle(image, options, sigma = 20):
    if sigma <= 0:
        logme('ERROR: could not find any edges')
        return image, (-1, -1, -1)
    
    image = image / 65536 # assume 16 bit
    low_threshold = np.median(cv2.blur(image, ksize=(5, 5))) / 10 #float(sys.argv[3])
    high_threshold = low_threshold*1.5#float(sys.argv[4])
    print('using thresholds:', low_threshold, high_threshold)
    edges = skimage.feature.canny(
        image=image,
        sigma=sigma,
        low_threshold=low_threshold,
        high_threshold=high_threshold,
    )
    if options['flag_display'] and 0:
        plt.imshow(edges)
        plt.title('remember to close this window by pressing the "X"', color = 'red')
        plt.show()
    
    labelled, nf = scipy.ndimage.measurements.label(edges, structure  = [[1,1,1], [1,1,1],[1,1,1]])
    if nf == 0:
        return ellipse_to_circle(image * 65536, options, sigma = sigma - 5) # try again with less blur, hope it will work
    region_sizes = [-1] + [np.sum(labelled == i) for i in range(1, nf+1)]
    filt = np.zeros(edges.shape)
    for label in sorted(region_sizes, reverse = True)[:min(nf, NUM_REG)]:
        filt[labelled == region_sizes.index(label)] = 1
        
    X = np.argwhere(filt) # find the non-zero pixels
    x_min, y_min, x_max, y_max = np.min(X[:, 0]), np.min(X[:, 1]), np.max(X[:, 0]), np.max(X[:, 1])
    dx = x_max - x_min
    dy = y_max - y_min
    crop = 0.025

    mask = np.zeros(filt.shape)
    mask[int(x_min+dx*crop):int(x_max-dx*crop), int(y_min+dy*crop):int(y_max-dy*crop)] = 1
    filt *= mask
    X = np.argwhere(filt) # find the non-zero pixels again

    x_min, y_min, x_max, y_max = np.min(X[:, 0]), np.min(X[:, 1]), np.max(X[:, 0]), np.max(X[:, 1])
            
    X = np.array(X, dtype='float')
    center, height, phi, ratio, X_f, ellipse_points = two_step(X)
    fix_img = correct_image(image, phi, ratio)

    if options['flag_display']:
        fig, ax = plt.subplots(ncols=2, nrows = 2)

        ax[0][0].imshow(image, cmap=plt.cm.gray)
        ax[0][0].set_title('uncorrected image', fontsize = 11)
        raw = np.argwhere(edges)
        ax[0][1].plot(raw[:, 1], image.shape[0] - raw[:, 0], 'ro', label = 'edge detection')
        ax[0][1].set_xlim([0, image.shape[1]])
        ax[0][1].set_ylim([0, image.shape[0]])
        ax[0][1].legend()
        ax[1][1].plot(X_f[:, 1], image.shape[0] - X_f[:, 0], 'ro', label = 'filtered edges')
        ax[1][1].plot(ellipse_points[:, 1], image.shape[0] - ellipse_points[:, 0], color='b', label = 'ellipse fit')
        ax[1][1].set_xlim([0, image.shape[1]])
        ax[1][1].set_ylim([0, image.shape[0]])
        ax[1][1].legend()
        ax[1][0].imshow(fix_img, cmap=plt.cm.gray)
        ax[1][0].set_title('geometrically corrected image', fontsize=11)
        
        ax[0][1].set_title('remember to close this window \n by pressing the "X"', color = 'red')
        plt.show()

    
    circle = (center[0], center[1], height) # radius == height
    return fix_img, circle
