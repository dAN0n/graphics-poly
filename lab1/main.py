#!/usr/bin/env python

from shadefix import ShadeFix
import os, sys

# Create output directory
dirname = "out"
if not os.path.exists(dirname): os.mkdir(dirname)

# Load image
if len(sys.argv) > 1:
	img = ShadeFix(sys.argv[1])
else:
	img = ShadeFix("test.jpg")

imgName  = [dirname + "/grey{}.png".format(i + 1) for i in range(3)]
histName = [dirname + "/hist{}.png".format(i + 1) for i in range(4)]

# Save greyscale image
img.saveImage(imgName[0])

# Save greyscale image histogram
img.makeHistogram("Histogram from greyscale image", histName[0])

# Save normalized histogram
img.normalizeShadeMap()
img.makeHistogram("Histogram after cutting range", histName[1])

# Save image and histogram after linear stretching
img.linearStretching()
img.saveImage(imgName[1])
img.makeHistogram("Histogram after linear stretching", histName[2])

# Restore original greyscale image
img.restoreImage()

# Save image and histogram after histogram equalization
img.histogramEqualization()
img.saveImage(imgName[2])
img.makeHistogram("Histogram after equalization", histName[3])