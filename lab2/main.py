#!/usr/bin/env python

from edgefinder import EdgeFinder
import os, sys

# Create output directory
dirname = "out"
if not os.path.exists(dirname): os.mkdir(dirname)

# Load image
if len(sys.argv) > 1:
	img = EdgeFinder(sys.argv[1])
else:
	img = EdgeFinder("test.jpg")

imgName  = [dirname + "/{}.png".format(i) for i in ["grey", "sobel", "prewitt", "roberts"]]

# Save greyscale image
img.saveImage(imgName[0])

# Use operators and save results to files
img.findEdges("sobel")
img.saveImage(imgName[1])

img.restoreImage()
img.findEdges("prewitt")
img.saveImage(imgName[2])

img.restoreImage()
img.findEdges("roberts")
img.saveImage(imgName[3])