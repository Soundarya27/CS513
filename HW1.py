import argparse, os
import cv2
import numpy as np
import sys
from os import listdir
from os.path import isfile, join


def setup_parser():
    help_text = {
      'dir_name': 'Please specify the directory where sample images are stored',
      'image_count': 'Please specify the number of images'
    }

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir_name', type=dir_path, help=help_text['dir_name'], required=True)
    parser.add_argument('--image_count', type=int, help=help_text['image_count'], required=True)
    return parser.parse_args()

def dir_path(dirName):
    if os.path.isdir(dirName):
       return dirName
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{dirName} is not a valid path")

def calMeanImg(dirctory, imageNum):
    listImages = []
    for n in range(imageNum):
        img = listdir(dirctory)[n]
        imgDir = join(dirctory, img)
        if isfile(imgDir):
            listImages.append(imgDir)

    print("Directory loaded.")

    meanImg =  np.zeros((2032, 2032), np.uint8)


    print("Calculating the mean gradient image of %s images..."% imageNum)

    for n in listImages :
        currentImg = cv2.imread(n)
        currentImg = gradient(currentImg)
        meanImg = meanImg + (currentImg / imageNum)
        del currentImg
    print("Mean image created.")

    return meanImg

def showWin(image, windowName, res = (800, 800)):
    if sys.platform == "darwin":
        cv2.imshow(windowName, cv2.resize(image, res))
        print("Press any key to quit.")
        cv2.waitKey(2000)
        cv2.destroyAllWindows()
    else:
        cv2.imshow(windowName, cv2.resize(image, res))
        print("Press any key to quit.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
   

def save(image, outputName):
    cv2.imwrite(outputName, image)

def cvt2Gray(image):
    imageBW = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return imageBW

def sobel(image):
    sobel64F = cv2.Sobel(image, cv2.CV_64F, 1, 1, ksize = 5)
    sobel = np.absolute(sobel64F)
    return sobel

def smooth(image):
    smooth = cv2.GaussianBlur(image,(3,3),0)
    return smooth

def gradient(image):
    grayImg = cvt2Gray(image)
    smoothImg = smooth(grayImg)

    sobelImg = sobel(smoothImg)
    return sobelImg

def createMask(image):
    kernel = np.ones((5, 5),np.uint8)
    dilated = cv2.dilate( image, kernel, iterations = 4)
    mask = cv2.erode(dilated,kernel,iterations = 4)

    _, mask = cv2.threshold( mask, 10, 255,cv2.THRESH_BINARY)
    print( "Mask Image created.")
    return mask

def main(setup_parser):
    meanImg = calMeanImg(setup_parser.dir_name, setup_parser.image_count)
    save(meanImg, "meanImg.jpg")
    mask = createMask(meanImg)
    showWin(mask, "mask")
    save(mask, "mask.jpg")

if __name__ == '__main__':
    main(setup_parser())
