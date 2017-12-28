#!/usr/bin/env python

from edgestrength import EdgeStrength
import os, sys

# Create output directory
dirname = "out"
if not os.path.exists(dirname): os.mkdir(dirname)

# Load image
if len(sys.argv) > 1:
	img = EdgeStrength(sys.argv[1])
else:
	img = EdgeStrength("test.jpg")

imgName  = [dirname + "/{}.png".format(i) for i in ["1_grey", "2_lap", "3_gauss3", "4_lap3", "5_res3", "6_gauss5", "7_lap5", "8_res5"]]

# Save greyscale image
img.saveImage(imgName[0])

# Laplacian without smoothing
img._laplacian()
img._lsLaplacian()
img.saveImage(imgName[1])
img.restoreImage()

# Gauss smoothing 3x3
img.gaussSmoothing()
img.saveImage(imgName[2])

# Laplacian with smoothing 3x3
img._laplacian()
img._lsLaplacian()
img.saveImage(imgName[3])

# Result with 3x3
img._lsLaplacian(0.7)
img.strengtheningEdges()
img.saveImage(imgName[4])
img.restoreImage()

# Gauss smoothing 5x5
img.gaussSmoothingTwice()
img.saveImage(imgName[5])

# Laplacian with smoothing 5x5
img._laplacian()
img._lsLaplacian()
img.saveImage(imgName[6])

# Result with 5x5
img._lsLaplacian(0.7)
img.strengtheningEdges()
img.saveImage(imgName[7])