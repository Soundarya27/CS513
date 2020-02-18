import argparse
import cv2
import numpy as np
import sys
from os import listdir
from os.path import isfile, join

def setup_parser():
    help_text = {
      'dir_name': 'specify the directory where sample images are stored',
      'image_count': 'specify the number of images'
    }

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--dir_name', type=str, help=help_text['dir_name'], required=True)
    parser.add_argument('--image_count', type=int, help=help_text['image_count'], default='1')
    return parser.parse_args()

#def getDir():
#    if len(sys.argv) == 3:
#        dirctory = sys.argv[1]
#        imageNum = int(sys.argv[2])
#    else:
#        print("Please input the Image file directory and image number.")
#        sys.exit(1)

#    print("smear auto detect started.")
#    return dirctory, imageNum

def calMeanImg(dirctory, imageNum):
    images = []
    for i in range(imageNum):
        img = listdir(dirctory)[i]
        imgDir = join(dirctory, img)
        if isfile(imgDir):
            images.append(imgDir)

    print("Directory loaded.")

    meanImg =  np.zeros((2032, 2032), np.uint8)


    print("Calculating the mean gradient image of %s images..."% imageNum)

    for i in images :
        currentImg = cv2.imread(i, 0)
        # currentImg = gradient(currentImg)
        meanImg = meanImg + (currentImg / imageNum)
        del currentImg
    print("mean image created.")

    # mdieanImg = listdir(dirctory)[2 / imageNum]
    # medieanImgDir = join(dirctory, img)

    return meanImg

def showWin(image, windowName, res = (800, 800)):
    cv2.imshow(windowName, cv2.resize(image, res))
    print("Press any key to quit.")
    cv2.waitKey(10000)
    cv2.destroyAllWindows('image')
    #cv2.waitKey(1)

def save(image, outputName):
    cv2.imwrite(outputName, image)

def cvt2Gray(image):
    imageBW = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # showWin(image_bw, "gray")
    # print("grayscale Image created")
    return imageBW

def sobel(image):
    sobel64F = cv2.Sobel(image, cv2.CV_64F, 1, 1, ksize = 5)
    sobel = np.absolute(sobel64F)
    return sobel

def smooth(image):
    smooth = cv2.GaussianBlur(image,(3,3),0)
    # showWin(blur, "blur")
    return smooth

def gradient(image):
    grayImg = cvt2Gray(image)
    smoothImg = smooth(grayImg)

    sobelImg = sobel(smoothImg)
    # print("gradient image created.")
    return sobelImg

def createMask(image):
    # image = cv2.normalize( image, image, 0, 255, cv2.NORM_MINMAX)
    # cv2.imshow('NORMALimage',image)
    kernel = np.ones((5, 5),np.uint8)
    # opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations = 3)
    dilated = cv2.dilate( image, kernel, iterations = 2)
    mask = cv2.erode(dilated,kernel,iterations = 2)

    # mask = cv2.normalize( mask, mask, 0, 255, cv2.NORM_MINMAX)

    _, mask = cv2.threshold( mask, 100, 255,cv2.THRESH_BINARY)
    print( "Mask Image created.")
    return mask

def main(setup_parser):
#    dirctory, imageNum = getDir()
    meanImg = calMeanImg(setup_parser.dir_name, setup_parser.image_count)
    # print(meanImg.dtype())
    # cv2.normalize( meanImg, meanImg, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    save(meanImg, "meanImg.jpg")
    # showWin(meanImg, "meanImg")
    # gradientMeanImg = gradient(meanImg)
    # save(gradientMeanImg, "gradientMeanImg.jpg")
    # copyImg = meanImg.copy()
    # gradientImg = gradient(meanImg)
    # showWin(gradientImg, "gradientImg")
    meanImg = smooth(meanImg)

    mask = createMask(meanImg)
    showWin(mask, "mask")
    save(mask, "mask.jpg")



if __name__ == '__main__':
    main(setup_parser())
