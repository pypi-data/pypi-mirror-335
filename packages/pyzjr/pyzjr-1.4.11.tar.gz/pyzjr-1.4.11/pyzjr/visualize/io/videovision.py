"""
Copyright (c) 2023, Auorui.
All rights reserved.
"""
import os
import cv2
import sys
import logging
import imageio
import numpy as np

import pyzjr.Z as Z
from pyzjr.visualize.io.imvision import StackedImagesV1

class VideoCap():
    """
    Customized Python video reading class
    Examples:
    ```
        Vcap = VideoCap(mode=0)
        while True:
            img = Vcap.read()
            Vcap.show("ss", img)
    ```
    """
    def __init__(self, mode=0, width=640, height=480, light=150):
        self.cap = cv2.VideoCapture(mode)
        self.cap.set(3, width)
        self.cap.set(4, height)
        self.cap.set(10, light)
        self.start_number = 0

    def read(self, flip=None):
        """
        :param flip: -1: Horizontal and vertical directions,
                      0: along the y-axis, vertical,
                      1: along the x-axis, horizontal
        """
        _, img = self.cap.read()
        if flip is not None:
            assert flip in [-1, 0, 1], f"VideoCap: The 'flip' parameter must be -1, 0, or 1."
            img = cv2.flip(img, flip)
        return img

    def free(self):
        """
        Release camera
        """
        self.cap.release()
        cv2.destroyAllWindows()

    def show(self, winname, src, base_name: str = './result.png', end_k=27,
             save_k=ord('s'), delay_t=1, extend_num=3):
        """
        Window display. Press 's' to save, 'Esc' to end
        """
        image_path, ext = os.path.splitext(base_name)
        os.makedirs(os.path.dirname(base_name), exist_ok=True)
        if src is not None:
            cv2.imshow(winname, src)
            k = cv2.waitKey(delay_t) & 0xFF
            if k == end_k:
                self.free()
                sys.exit(0)
            elif k == save_k:
                self.start_number += 1
                file_number = str(self.start_number).zfill(extend_num)
                file_path = f"{image_path}_{file_number}{ext}"
                print(f"{self.start_number}  Image saved to {file_path}")
                cv2.imwrite(file_path, src)


def Mp4toGif(mp4, name='result.gif', fps=10, start=None, end=None):
    """Convert MP4 files to GIF animations"""
    cap = cv2.VideoCapture(mp4)
    all_images = []
    frame_count = 0
    while True:
        ret, img = cap.read()
        if ret is False:
            break
        if start is not None and frame_count < start:
            frame_count += 1
            continue
        if end is not None and frame_count >= end:
            break
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        all_images.append(img)
        frame_count += 1

    duration = int(1000 / fps)  # 将帧率转换为每帧之间的延迟时间（毫秒）
    imageio.mimsave(name, all_images, duration=duration)
    print("Conversion completed！")



class FindColor():
    def __init__(self, trackBar=False, name="Bars"):
        self.trackBar = trackBar
        self.name = name
        if self.trackBar:
            self.initTrackbars()

    def empty(self, a):
        pass

    def initTrackbars(self):
        """
        :return:初始化轨迹栏
        """
        cv2.namedWindow(self.name)
        cv2.resizeWindow(self.name, 640, 240)
        cv2.createTrackbar("Hue Min", self.name, 0, 179, self.empty)
        cv2.createTrackbar("Hue Max", self.name, 179, 179, self.empty)
        cv2.createTrackbar("Sat Min", self.name, 0, 255, self.empty)
        cv2.createTrackbar("Sat Max", self.name, 255, 255, self.empty)
        cv2.createTrackbar("Val Min", self.name, 0, 255, self.empty)
        cv2.createTrackbar("Val Max", self.name, 255, 255, self.empty)

    def getTrackbarValues(self):
        """
        Gets the trackbar values in runtime
        :return: hsv values from the trackbar window
        """
        hmin = cv2.getTrackbarPos("Hue Min", self.name)
        smin = cv2.getTrackbarPos("Sat Min", self.name)
        vmin = cv2.getTrackbarPos("Val Min", self.name)
        hmax = cv2.getTrackbarPos("Hue Max", self.name)
        smax = cv2.getTrackbarPos("Sat Max", self.name)
        vmax = cv2.getTrackbarPos("Val Max", self.name)
        HsvVals = [[hmin, smin, vmin], [hmax, smax, vmax]]

        return HsvVals

    def protect_region(self, mask, threshold=None):
        """
        * 用于保护掩膜图的部分区域
        :param mask: 掩膜图
        :param threshold: 如果为None,则为不保护，如果是长为4的列表，则进行特定区域的保护
        :return: 返回进行保护区域的掩膜图

        example:    [0, img.shape[1], 0, img.shape[0]]为全保护状态，
                    x_start可以保护大于x的部分
                    x_end可以保护小于x的部分
                    y_start可以保护图像下方的部分
                    y_end可以保护图像上方的部分
        """
        if threshold == None:
            return mask
        else:
            x_start, x_end, y_start, y_end = threshold[:4]
            mask[y_start:y_end, x_start:x_end] = 0
            return mask

    def MaskZone(self, img, HsvVals):
        """
        * 生成掩膜图以及融合图像
        :param img: 输入图像
        :param HsvVals: 可以通过getTrackbarValues获得,也可调取Z.HSV的值
        :return: 返回融合图、掩膜图、HSV图
        """
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower = np.array(HsvVals[0])
        upper = np.array(HsvVals[1])
        mask = cv2.inRange(imgHSV, lower, upper)
        imgResult = cv2.bitwise_and(img, img, mask=mask)
        return imgResult, mask

    def update(self, img, myColor=None):
        """
        :param img: 需要在其中找到颜色的图像
        :param myColor: hsv上下限列表
        :return: mask带有检测到颜色的白色区域的roi图像
                 imgColor彩色图像仅显示检测到的区域
        """
        imgColor = [],
        mask = []
        if self.trackBar:
            myColor = self.getTrackbarValues()

        if isinstance(myColor, str):
            myColor = self.getColorHSV(myColor)

        if myColor is not None:
            imgColor, mask = self.MaskZone(img, myColor)
        return imgColor, mask

    def getColorHSV(self, myColor):
        if myColor == 'red':
            output = [[146, 141, 77], [179, 255, 255]]
        elif myColor == 'green':
            output = [[44, 79, 111], [79, 255, 255]]
        elif myColor == 'blue':
            output = [[103, 68, 130], [128, 255, 255]]
        else:
            output = None
            logging.warning("Color Not Defined")
            logging.warning("Available colors: red, green, blue ")

        return output

def DetectImageColor(img, ConsoleOut=True, threshold=None, scale=1.0):
    """
    * 轨迹栏检测图片,此函数仅仅作为使用示例
    :param img: 图片
    :param name: 轨迹栏名
    :param ConsoleOut: 用于是否控制台打印HsvVals的值
    :param threshold: 阈值，用于保护图片的区域
    :param scale: 规模大小
    :return:
    """
    ColF = FindColor(True, "DetectImg")
    while True:
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        HsvVals = ColF.getTrackbarValues()
        if ConsoleOut:
            print(HsvVals)
        imgResult, mask = ColF.update(img,HsvVals)
        pro_mask = ColF.protect_region(mask, threshold)
        imgStack = StackedImagesV1(scale, ([img, imgHSV],[pro_mask,imgResult]))
        cv2.imshow("Stacked Images", imgStack)
        k = cv2.waitKey(1)
        if k == 27:
            break

def DetectVideoColor(mode=0, myColor=None, scale=1.0):
    """
    * 轨迹栏检测摄像头,此函数仅仅作为使用示例
    :param mode: 检测模式,默认本地摄像头,可传入video路径
    :param myColor: getColorHSV返回的一些测好的Hsv值
    :param scale: 规模大小
    """
    if myColor:
        Cf = False
    else:
        Cf = True
    Vcap = VideoCap(mode=mode)
    ColF = FindColor(Cf, "DetectVideo")
    while True:
        img = Vcap.read()
        imgColor, mask = ColF.update(img, myColor)
        stackedimg = StackedImagesV1(scale, [img, imgColor])
        Vcap.show("DetectVideo", stackedimg)

if __name__=="__main__":
    DetectVideoColor(myColor="red")
    imagePath = r"D:\PythonProject\pyzjr\pyzjr\test.png"
    img = cv2.imread(imagePath)
    DetectImageColor(img)

    # Vcap = VideoCap(mode=0)
    # while True:
    #     img = Vcap.read()
    #     Vcap.show("ss", img)