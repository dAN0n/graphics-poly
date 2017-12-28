#!/usr/bin/env python

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from math import sqrt

class EdgeFinder:
    """
    Class for edge detection on greyscale image

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

    def _expandImage(self):
        """
        Creating a border around of image with values of nearest pixels

        :return: Image with border around it
        :rtype:  numpy
        """
        expImg = np.zeros((self.height + 2, self.width + 2))
        # Fill center of image with original image
        expImg[1:-1,1:-1] = self.inImg
        # Fill borders of expanded image with borders of original image
        # (except angular pixels)
        expImg[1:-1,0] = self.inImg[...,0]
        expImg[1:-1,-1] = self.inImg[...,-1]
        expImg[0,1:-1] = self.inImg[0,...]
        expImg[-1,1:-1] = self.inImg[-1,...]
        # Fill angular pixels
        expImg[0,0] = self.inImg[0,0]
        expImg[0,-1] = self.inImg[0,-1]
        expImg[-1,0] = self.inImg[-1,0]
        expImg[-1,-1] = self.inImg[-1,-1]
        
        return expImg

    def findEdges(self, operator):
        """
        Create image with detected edges using Sobel, Prewitt or Roberts operator

        :param operator: Operator for edge detection ("sobel", "prewitt" or "roberts")
        :type  operator: str
        """
        # Create arrays for derivative approximations
        Gx = np.zeros((self.height, self.width))
        Gy = np.zeros((self.height, self.width))

        # Expand image with border around it
        expImg = self._expandImage()

        # Fill Gx and Gy
        if operator == "sobel":
            Gx, Gy = self._sobelEdges(expImg, Gx, Gy)
        elif operator == "prewitt":
            Gx, Gy = self._prewittEdges(expImg, Gx, Gy)
        elif operator == "roberts":
            Gx, Gy = self._robertsEdges(expImg, Gx, Gy)
        else:
            raise ValueError('Undefined operator: {}. Available operators: "sobel", "prewitt" or "roberts"'.format(type))
        
        # Create image with detected edges
        self._findG(Gx, Gy)

    @staticmethod
    def _sobelEdges(expImg, Gx, Gy):
        """
        Getting horizontal and vertical derivative approximations with using of Sobel operator

        :param expImg: Image expanded with borders 
        :type  expImg: numpy
        :param Gx:     Horizontal derivative approximation array/image
        :type  Gx:     numpy
        :param Gy:     Vertical derivative approximation array/image
        :type  Gy:     numpy
        :return:       Gx, Gy
        :rtype:        numpy, numpy
        """
        Gx[...] = expImg[0:-2,0:-2] - expImg[0:-2,2:] + 2*(expImg[1:-1,0:-2] - expImg[1:-1,2:]) + expImg[2:,0:-2] - expImg[2:,2:]
        Gy[...] = expImg[2:,0:-2] - expImg[0:-2,0:-2] + 2*(expImg[2:,1:-1] - expImg[0:-2,1:-1]) + expImg[2:,2:] - expImg[0:-2,2:]

        return Gx, Gy

    @staticmethod
    def _prewittEdges(expImg, Gx, Gy):
        """
        Getting horizontal and vertical derivative approximations with using of Prewitt operator

        :param expImg: Image expanded with borders 
        :type  expImg: numpy
        :param Gx:     Horizontal derivative approximation array/image
        :type  Gx:     numpy
        :param Gy:     Vertical derivative approximation array/image
        :type  Gy:     numpy
        :return:       Gx, Gy
        :rtype:        numpy, numpy
        """
        Gx[...] = expImg[0:-2,0:-2] - expImg[0:-2,2:] + expImg[1:-1,0:-2] - expImg[1:-1,2:] + expImg[2:,0:-2] - expImg[2:,2:]
        Gy[...] = expImg[2:,0:-2] - expImg[0:-2,0:-2] + expImg[2:,1:-1] - expImg[0:-2,1:-1] + expImg[2:,2:] - expImg[0:-2,2:]

        return Gx, Gy

    @staticmethod
    def _robertsEdges(expImg, Gx, Gy):
        """
        Getting horizontal and vertical derivative approximations with using of Roberts operator

        :param expImg: Image expanded with borders 
        :type  expImg: numpy
        :param Gx:     Horizontal derivative approximation array/image
        :type  Gx:     numpy
        :param Gy:     Vertical derivative approximation array/image
        :type  Gy:     numpy
        :return:       Gx, Gy
        :rtype:        numpy, numpy
        """
        Gx[...] = expImg[1:-1,1:-1] - expImg[2:,2:]
        Gy[...] = expImg[1:-1,2:] - expImg[2:,1:-1]

        return Gx, Gy

    def _findG(self, Gx, Gy):
        """
        Create result image using filled horizontal and vertical derivative approximations
        """
        # Get absolute values
        Gx = np.absolute(Gx)
        Gy = np.absolute(Gy)
        
        self.inImg = Gx + Gy

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