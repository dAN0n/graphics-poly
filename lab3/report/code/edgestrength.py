#!/usr/bin/env python

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from math import sqrt

class EdgeStrength:
    """
    Class for edge strengthening on greyscale image

    :ivar    inImg:    Loaded image, converted to greyscale
    :vartype inImg:    numpy
    :ivar    height:   Height of image
    :vartype height:   int
    :ivar    width:    Width of image
    :vartype width:    int
    :ivar    origImg:  Backup of original greyscale image
    :vartype origImg:  numpy
    """
    def __init__(self, inImg):
        # Load image
        self.inImg = cv.imread(inImg)
        # Rows
        self.height = self.inImg.shape[0]
        # Columns
        self.width = self.inImg.shape[1]
        # RGB to Greyscale image
        if len(self.inImg.shape) == 3: self.toGreyscale()
        # Greyscale image backup
        self.origImg = self.inImg

    def toGreyscale(self):
        """
        Converting RGB image to greyscale
        """
        # Get color arrays
        red   = self.inImg[...,2]
        green = self.inImg[...,1]
        blue  = self.inImg[...,0]
        
        # Fill array with shades of grey
        outImg = np.zeros((self.height, self.width))
        outImg[...] = 0.299 * red + 0.587 * green + 0.114 * blue
        
        # Round result shades
        outImg = np.round(outImg)
        
        # Update image
        self.inImg = outImg 

    def _expandImage(self, img = None):
        """
        Creating a border around of image with values of nearest pixels

        :return: Image with border around it
        :rtype:  numpy
        """
        if img is None:
            img = self.inImg
        height = img.shape[0]
        width  = img.shape[1]
        expImg = np.zeros((height + 2, width + 2))

        # Fill center of image with original image
        expImg[1:-1,1:-1] = img
        # Fill borders of expanded image with borders of original image
        # (except angular pixels)
        expImg[1:-1,0] = img[...,0]
        expImg[1:-1,-1] = img[...,-1]
        expImg[0,1:-1] = img[0,...]
        expImg[-1,1:-1] = img[-1,...]
        # Fill angular pixels
        expImg[0,0] = img[0,0]
        expImg[0,-1] = img[0,-1]
        expImg[-1,0] = img[-1,0]
        expImg[-1,-1] = img[-1,-1]

        return expImg

    def gaussSmoothing(self):
        """
        Gauss smoothing operator with 3x3 square
        """
        # Expand image with border around it
        expImg = self._expandImage()

        self.inImg = (expImg[0:-2,0:-2] + 2*expImg[0:-2,1:-1] + expImg[0:-2,2:] + 
            2*expImg[1:-1,0:-2] + 4*expImg[1:-1,1:-1] + 2*expImg[1:-1,2:] + 
            expImg[2:,0:-2] + 2*expImg[2:,1:-1] + expImg[2:,2:]) / 16

    def gaussSmoothingTwice(self):
        """
        Gauss smoothing operator with 5x5 square
        """
        # Expand image with border around it
        expImg = self._expandImage(self._expandImage())

        self.inImg = (expImg[0:-4,0:-4] + 2*expImg[0:-4,1:-3] + 4*expImg[0:-4,2:-2] + 2*expImg[0:-4,3:-1] + expImg[0:-4,4:] +
            2*expImg[1:-3,0:-4] + 4*expImg[1:-3,1:-3] + 8*expImg[1:-3,2:-2] + 4*expImg[1:-3,3:-1] + 2*expImg[1:-3,4:] +
            4*expImg[2:-2,0:-4] + 8*expImg[2:-2,1:-3] + 16*expImg[2:-2,2:-2] + 8*expImg[2:-2,3:-1] + 4*expImg[2:-2,4:] +
            2*expImg[3:-1,0:-4] + 4*expImg[3:-1,1:-3] + 8*expImg[3:-1,2:-2] + 4*expImg[3:-1,3:-1] + 2*expImg[3:-1,4:] +
            expImg[4:,0:-4] + 2*expImg[4:,1:-3] + 4*expImg[4:,2:-2] + 2*expImg[4:,3:-1] + expImg[4:,4:]) / 100

    def laplacianEdges(self, coef):
        """
        Use Laplacian operator to find edges of image and lower Laplacian shade range to 0 - coef

        :param coef: Maximum value of Laplacian shades
        :type  coef: float
        """
        self._laplacian()
        self._lsLaplacian(coef)

    def _laplacian(self):
        """
        Getting second-order derivative approximations with using of Laplacian operator
        """
        # Expand image with border around it
        expImg = self._expandImage()

        self.inImg = - expImg[0:-2,0:-2] - expImg[0:-2,1:-1] - expImg[0:-2,2:] - expImg[1:-1,0:-2] + 8*expImg[1:-1,1:-1] - expImg[1:-1,2:] - expImg[2:,0:-2] - expImg[2:,1:-1] - expImg[2:,2:]

    # def _lsLaplacian(self, coef = np.finfo(np.float64).max / 32786):
    def _lsLaplacian(self, coef = 1024):
        """
        Lower Laplacian shade range to 0 - coef

        :param coef: Maximum value of Laplacian shades
        :type  coef: float
        """
        self.inImg[self.inImg < 0] = 0
        self._linearStretching(coef)
        self.inImg[...] += 1

    def _linearStretching(self, coef):
        """
        Performing linear stretching on greyscale image
        """
        # Get bounds of shades
        a = np.amin(self.inImg)
        b = np.amax(self.inImg)
        # print(b)

        # Set bounds of new shades
        c = 0
        d = coef

        # Linear stretching
        resImg = np.zeros((self.height, self.width))
        resImg[...] = (self.inImg[...] - a) * ((d - c) / (b - a)) + c

        # Update image
        self.inImg = resImg

    def strengtheningEdges(self):
        """
        Strengthening edges on greyscale image
        """
        self.inImg[...] = self.inImg[...] * self.origImg[...]

    def saveImage(self, path):
        """
        Saving image to file

        :param path: Save path
        :type  path: str
        """
        cv.imwrite(path, self.inImg)

    def restoreImage(self):
        """
        Restoring original greyscale image and shade map from backup
        """
        self.inImg = self.origImg