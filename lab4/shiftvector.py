import random
import numpy as np
import cv2

class ShiftVector:
    def __init__(self, pathList, blockSize, step, windowSize):
        self.BLOCK_SIZE = [int(blockSize), int(blockSize)]
        self.STEP_SIZE = int(step)
        self.WINDOW_SIZE = int(windowSize)

        self.t_1 = cv2.imread(pathList[0], 0)
        self.t = cv2.imread(pathList[1], 0)

        cv2.imshow("1 Frame", self.t_1)
        cv2.imshow("2 Frame", self.t)
        cv2.waitKey(0)

        self.t_rec = self.t_1.copy()
        self.t_vec = self.t_1.copy()
        self.t_rec2 = self.t_1.copy()
        self.t_vec.fill(255)
        self.t_rec.fill(0)
        self.t_rec2.fill(0)

    @staticmethod
    def get_ssd(first_block, second_block):
        diff = np.sum(cv2.absdiff(first_block, second_block) ** 2)
        return diff

    @staticmethod
    def get_sad(first_block, second_block):
        diff = np.sum(cv2.absdiff(first_block, second_block))
        return diff

    @staticmethod
    def sliding_block(image, block_size, step):
        """
        Функция разбиения исходного изображения на блоки
        :param image: Исходное изображение
        :param block_size: Размер блока [NxL]
        :param step: Шаг блока
        :return: Нарезанные блоки (yield)
        """
        for x_coord in range(0, image.shape[0], step):
            if x_coord + block_size[0] > image.shape[0]:
                x_coord = image.shape[0] - block_size[0]
            for y_coord in range(0, image.shape[1], step):
                if y_coord + block_size[1] > image.shape[1]:
                    y_coord = image.shape[1] - block_size[1]
                yield (x_coord, y_coord, image[x_coord:x_coord + block_size[0], y_coord:y_coord + block_size[1]])

    @staticmethod
    def replace_block(a, b, block_size, x_coord, y_coord):
        """
        Вставка найденного блока в изображение для восстонавления
        :param a: Восстанавливаемое изображение
        :param b: Блок для замены 
        :param c: Акк
        :param block_size: Размер блока [NxL]
        :param x_coord: Начало заменяемого блока на оси х
        :param y_coord: Начало заменяемого блока на оси y
        """
        a[x_coord:x_coord + block_size[0], y_coord:y_coord + block_size[1]] = b[0:block_size[0], 0:block_size[1]]

    @staticmethod
    def search_window(image, x_coord, y_coord, size):
        """
        Окно поиска блока
        :param image: Изображение, в котором осуществляется поиск
        :param x_coord: Центр окна по оси X
        :param y_coord: Центр окна по оси Y
        :param size: Размер окна
        :return: Возвращает координаты окна (x, y) и само окно (пиксели)
        """
        if x_coord - size < 0:
            x_begin = 0
            x_end = x_coord + size
        elif x_coord + size > image.shape[0]:
            x_begin = x_coord - size
            x_end = image.shape[0]
        else:
            x_begin = x_coord - size
            x_end = x_coord + size

        if y_coord - size < 0:
            y_begin = 0
            y_end = y_coord + size
        elif y_coord + size > image.shape[1]:
            y_begin = y_coord - size
            y_end = image.shape[1]
        else:
            y_begin = y_coord - size
            y_end = y_coord + size

        return x_begin, y_begin, image[x_begin:x_end, y_begin:y_end]

    def find_vectors(self):
        for (x_block, y_block, im_block) in self.sliding_block(self.t_1, self.BLOCK_SIZE, self.STEP_SIZE):
            sad = 99999
            to_x = 0
            to_y = 0
            im_w = None
            flag = False
            (x_start, y_start, im_window) = self.search_window(self.t, x_block, y_block, self.WINDOW_SIZE)
            new_SAD = self.get_sad(im_block, self.t[x_block:x_block + self.BLOCK_SIZE[0], y_block:y_block + self.BLOCK_SIZE[1]])
            if new_SAD < 10:
                sad = new_SAD
                to_x = x_block
                to_y = y_block
                im_w = self.t[x_block: x_block + self.BLOCK_SIZE[0], y_block: y_block + self.BLOCK_SIZE[1]]
                self.replace_block(self.t_rec, im_w, self.BLOCK_SIZE, x_block, y_block)
                cv2.line(self.t_vec, (to_y, to_x), (y_block, x_block), (random.randint(0, 256)), 1, 8, 0)
                continue

            for x_window in range(0, im_window.shape[0] - self.BLOCK_SIZE[0] + 1):
                if flag is True:
                    flag = False
                    break
                for y_window in range(0, im_window.shape[1] - self.BLOCK_SIZE[1] + 1):
                    new_SAD = self.get_sad(im_block,
                                      im_window[x_window:x_window + self.BLOCK_SIZE[0], y_window:y_window + self.BLOCK_SIZE[1]])
                    if sad > new_SAD:
                        sad = new_SAD
                        to_x = x_start + x_window
                        to_y = y_start + y_window
                        im_w = im_window[x_window: x_window + self.BLOCK_SIZE[0], y_window: y_window + self.BLOCK_SIZE[1]]
                        if sad < 10:
                            self.replace_block(self.t_rec, im_w, self.BLOCK_SIZE, x_block, y_block)
                            cv2.line(self.t_vec, (to_y, to_x), (y_block, x_block), (random.randint(0, 256)), 1, 8, 0)
                            flag = True
                            break

            self.replace_block(self.t_rec, im_w, self.BLOCK_SIZE, x_block, y_block)
            cv2.line(self.t_vec, (to_y, to_x), (y_block, x_block), (random.randint(0, 256)), 1, 8, 0)

        cv2.imshow("Restored 1 frame", self.t_rec)
        cv2.imshow("Shift vectors", self.t_vec)