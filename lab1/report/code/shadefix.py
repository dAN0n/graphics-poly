#!/usr/bin/env python

import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

class ShadeFix:
    """
    Class for performing linear stretching and histogram equalization on greyscale image

    :ivar    inImg:    Loaded image, converted to greyscale
    :vartype inImg:    numpy
    :ivar    height:   Height of image
    :vartype height:   int
    :ivar    width:    Width of image
    :vartype width:    int
    :ivar    origImg:  Backup of original greyscale image
    :vartype origImg:  numpy
    :ivar    shadeMap: Map with the amount of each shade
    :vartype shadeMap: numpy
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
        # Shade Map
        self.shadeMap = self.getShadeMap()

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

    def linearStretching(self):
        """
        Performing linear stretching on greyscale image
        """
        # Get bounds of histogram
        a = np.nonzero(self.shadeMap)[0][0]
        b = np.nonzero(self.shadeMap)[0][-1]

        # Linear stretching
        resImg = np.zeros((self.height, self.width))
        resImg[...] = (self.inImg[...] - a) * (255 / (b - a))

        # Fix out of range values
        resImg[resImg < 0] = 0
        resImg[resImg > 255] = 255
        resImg = np.round(resImg)

        # Update image and shade map
        self.inImg = resImg
        self.shadeMap = self.getShadeMap()

    def histogramEqualization(self):
        """
        Performing histogram equalization on greyscale image
        """
        # Create shades replace map and fill it
        shades = np.zeros(256)
        pixelCount = self.height * self.width
        for k in range(0, shades.size - 1):
            shades[k] = np.sum(self.shadeMap[0:k]) / pixelCount

        # Histogram stretching for the whole range
        shades[...] *= 255

        # Replace pixels according to shade map
        resImg = np.zeros((self.height, self.width))
        resImg[...] = shades[self.inImg[...].astype(int)]

        # Update image and shade map
        self.inImg = resImg
        self.shadeMap = self.getShadeMap()

    def makeHistogram(self, title, path):
        """
        Creating histogram of image and save to file

        :param title: Title of histogram
        :type  title: str
        :param path:  Save path
        :type  path:  str
        """
        # Create plot
        fig = plt.figure(figsize=(12.80, 7.20), dpi=100)
        plt.bar(np.arange(256), self.shadeMap, 1)
        plt.xlim(-1, 256)
        plt.title(title)
        
        # Save plot
        fig.savefig(path)

    def normalizeShadeMap(self):
        """
        Deleting about 5% of histogram pixels from corners
        """
        check, a, b = 0, 0, 255
        while check < 0.05 * self.width * self.height:
            # Cut from left side
            if self.shadeMap[a] <= self.shadeMap[b]:
                check += self.shadeMap[a]
                self.shadeMap[a] = 0
                a += 1
            # Cut from right side
            else:
                check += self.shadeMap[b]
                self.shadeMap[b] = 0
                b -=1

    def getShadeMap(self):
        """
        Creating map with the amount of each shade

        :return: Shade map
        :rtype:  numpy
        """
        return np.bincount(self.inImg.astype(int).flat, minlength=256)

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
        self.shadeMap = self.getShadeMap()