import random
import numpy as np
import cv2

class ObjectRectangle:
    def __init__(self, path, time):
        self.ix, self.iy = -1, -1
        self.drawing = False
        video = cv2.VideoCapture(path)
        video.set(0, time)

        success, self.img = video.read()
        self.drawImg = self.img + 0

        self.coord = [-1, -1, -1, -1]

    def showFrame(self):
        cv2.namedWindow('1st Frame')
        cv2.setMouseCallback('1st Frame', self.draw)

        while(1):
            cv2.imshow('1st Frame', self.drawImg)
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                cv2.destroyAllWindows()
                break

    def draw(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawImg = self.img + 0
            self.drawing = True
            self.ix = x
            self.iy = y

        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            cv2.rectangle(self.drawImg,(self.ix,self.iy),(x,y),(0,0,255), 2)
            self.coord = [self.ix, self.iy, x, y]

    @staticmethod
    def toGreyscale(img):
        """
        Converting RGB image to greyscale
        """
        # Get color arrays
        red   = img[...,2]
        green = img[...,1]
        blue  = img[...,0]
        
        # Fill array with shades of grey
        outImg = np.zeros((img.shape[0], img.shape[1]))
        outImg[...] = 0.299 * red + 0.587 * green + 0.114 * blue
        
        # Round result shades
        outImg = np.round(outImg)
        
        # Update image
        return outImg

    def getCoordinates(self):
        return self.coord


class Tracker:
    def __init__(self, path, time, frameCount, coord):
        self.imgList = list()
        self.imgCoordList = list()
        self.imgCoordList.append(coord)
        self.fix_coord()

        video = cv2.VideoCapture(path)
        video.set(0, time)
        count = 0
        success = True

        while success and count < frameCount:
            success, image = video.read()
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            self.imgList.append(image)
            if count > 0:
                self.imgCoordList.append(None)
            count += 1

    @staticmethod
    def get_ssd(first_block, second_block):
        diff = np.sum(cv2.absdiff(first_block, second_block) ** 2)
        return diff

    @staticmethod
    def get_sad(first_block, second_block):
        diff = np.sum(cv2.absdiff(first_block, second_block))
        return diff

    @staticmethod
    def search_window(image, x_coord, y_coord, x_size, y_size):
        """
        Окно поиска блока
        :param image: Изображение, в котором осуществляется поиск
        :param x_coord: Центр окна по оси X
        :param y_coord: Центр окна по оси Y
        :param size: Размер окна
        :return: Возвращает координаты окна (x, y) и само окно (пиксели)
        """
        if x_coord - x_size < 0:
            x_begin = 0
            x_end = x_coord + x_size
        elif x_coord + x_size > image.shape[1]:
            x_begin = x_coord - x_size
            x_end = image.shape[1]
        else:
            x_begin = x_coord - x_size
            x_end = x_coord + x_size

        if y_coord - y_size < 0:
            y_begin = 0
            y_end = y_coord + y_size
        elif y_coord + y_size > image.shape[0]:
            y_begin = y_coord - y_size
            y_end = image.shape[0]
        else:
            y_begin = y_coord - y_size
            y_end = y_coord + y_size

        return x_begin, y_begin, image[y_begin:y_end, x_begin:x_end]

    def fix_coord(self):
        if self.imgCoordList[0][2] < self.imgCoordList[0][0]:
            self.imgCoordList[0][0], self.imgCoordList[0][2] = self.imgCoordList[0][2], self.imgCoordList[0][0]
        if self.imgCoordList[0][3] < self.imgCoordList[0][1]:
            self.imgCoordList[0][1], self.imgCoordList[0][3] = self.imgCoordList[0][3], self.imgCoordList[0][1]

    @staticmethod
    def getShadeMap(img):
        """
        Creating map with the amount of each shade

        :return: Shade map
        :rtype:  numpy
        """
        return np.bincount(img.astype(int).flat, minlength=256)

    def histogramIntersection(self, oldImage, newImage):
        oldShade = self.getShadeMap(oldImage)
        newShade = self.getShadeMap(newImage)

        maxShade = np.sum(oldShade[0:])
        minimum = np.minimum(oldShade, newShade)
        sumShade = np.sum(minimum[0:])

        intersection = sumShade / maxShade
        return True if intersection >= 0.5 else False

    @staticmethod
    def block_center(coord):
        x_coord = round((coord[0] + coord[2]) / 2)
        y_coord = round((coord[1] + coord[3]) / 2)
        return x_coord, y_coord

    @staticmethod
    def block_size(coord):
        x_size = coord[2] - coord[0]
        y_size = coord[3] - coord[1]
        return [x_size, y_size]


    @staticmethod
    def get_image_block(coord, image):
        x_size = coord[2] - coord[0]
        y_size = coord[3] - coord[1]
        return image[coord[1]:coord[1] + y_size, coord[0]:coord[0] + x_size]

    def find_object(self):
        for index, _ in enumerate(self.imgList):
            if index == len(self.imgList) - 1:
                break

            sad = 999999
            to_x = 0
            to_y = 0
            im_w = None
            flag = False

            print(index)

            blockSize = self.block_size(self.imgCoordList[index])
            im_block = self.get_image_block(self.imgCoordList[index], self.imgList[index])
            (x_center, y_center) = self.block_center(self.imgCoordList[index])
            x_coord = self.imgCoordList[index][0]
            y_coord = self.imgCoordList[index][1]

            (x_start, y_start, im_window) = self.search_window(self.imgList[index + 1], x_center, y_center, blockSize[0], blockSize[1])
            new_SAD = self.get_sad(im_block, self.imgList[index + 1][y_coord:y_coord + blockSize[1], x_coord:x_coord + blockSize[0]])
            if new_SAD < 5000:
                if self.histogramIntersection(im_block, self.imgList[index + 1][y_coord:y_coord + blockSize[1], x_coord:x_coord + blockSize[0]]):
                    self.imgCoordList[index + 1] = self.imgCoordList[index]
                else:
                    break
                continue

            best_x = -1
            best_y = -1

            for x_window in range(0, im_window.shape[1] - blockSize[0] + 1):
                for y_window in range(0, im_window.shape[0] - blockSize[1] + 1):
                    new_SAD = self.get_sad(im_block,
                                      im_window[y_window:y_window + blockSize[1], x_window:x_window + blockSize[0]])
                    if sad > new_SAD:
                        sad = new_SAD
                        best_x = x_start + x_window
                        best_y = y_start + y_window

            if best_x >= 0 and best_y >= 0:
                coord = [best_x,
                         best_y,
                         best_x + blockSize[0],
                         best_y + blockSize[1]]

                check = True
                for item in coord:
                    if item < 0:
                        check = False
                if check and self.histogramIntersection(im_block, self.imgList[index + 1][best_y:best_y + blockSize[1], best_x:best_x + blockSize[0]]):
                    self.imgCoordList[index + 1] = coord
                else:
                    break
            else:
                break

    def draw_frames(self):
        for i, v in enumerate(self.imgList):
            if self.imgCoordList[i] is not None:
                image = v
                cv2.rectangle(image,(self.imgCoordList[i][0],self.imgCoordList[i][1]),(self.imgCoordList[i][2],self.imgCoordList[i][3]),(0,0,255), 2)
                cv2.imshow('{} Frame'.format(i + 1), image)
            else:
                cv2.imshow('{} Frame'.format(i + 1), v)
                break
        cv2.waitKey(0)