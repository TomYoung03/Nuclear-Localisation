import cv2
import os
import shutil
import numpy
import random
import PySimpleGUI as sg
from fileMethods import getFileName

def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x,y)
        return x,y

def cut_rectangles(imagePath,image,rectList,folderName):
    if not os.path.exists(folderName):
        os.mkdir(f"{folderName}")
    for rect in rectList:
        print(rect)
        fileName = getFileName(imagePath,"\\").replace(".jpg","")
        fileName = fileName.replace(".tif","")
        if not os.path.isfile(f"{folderName}/{fileName} {rect}.tif"):
            try:
                cv2.imwrite(f"{folderName}/{fileName} {rect}.tif", image[rect[0][1]:rect[1][1], rect[0][0]:rect[1][0]])
            except:
               print(f"{folderName}/{fileName} {rect}.tif Failed to save")
        print(f"Saved file: {fileName} {rect}.tif")

def combine_images(image1,image2,colour):
    image = cv2.imread(image1)
    imageBlue, imageGreen, imageRed = cv2.split(image)
    nucleusImage = cv2.imread(image2)
    nucleusBlue, nucleusGreen, nucleusRed = cv2.split(nucleusImage)
    if colour == "Red":
        image = cv2.merge([nucleusBlue, numpy.zeros(imageGreen.shape, numpy.uint8), imageRed])
    if colour == "Green":
        image = cv2.merge([nucleusBlue, imageGreen, numpy.zeros(imageRed.shape, numpy.uint8)])
    return image


def select_cells(imagePath, nucleusImagePath, folderName="Selected Cells",fluorescenceColour = "Red"):
    global topLeftCorner, bottomRightCorner, rectangles,previousImage,undo

    def draw_rectangle(event, x, y, flags, *userdata):
        global topLeftCorner, bottomRightCorner, rectangles,previousImage,undo
        #Click down records first location, click up records second
        if event == cv2.EVENT_LBUTTONDOWN:
            topLeftCorner = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            bottomRightCorner = (x, y)
            #Creates a copy of the image before drawing the new rectangle to use when undoing
            previousImage = image.copy()
            #Adds rectangle to list and draws it on image
            rectangles.append((topLeftCorner, bottomRightCorner))
            undo = True
            #Draws rectangle with a random colour, values limited to avoid pure black rectangle
            cv2.rectangle(image, topLeftCorner, bottomRightCorner, (random.randint(50,230),random.randint(50,230),random.randint(50,230)), 5)
            cv2.imshow("Window", image)

    image = cv2.imread(imagePath)
    originalImage = image.copy()
    image = combine_images(imagePath,nucleusImagePath,fluorescenceColour)
    nucleusImage = cv2.imread(nucleusImagePath)
    resetImage = image.copy()
    #WINDOW_NORMAL flag allows window to be resized,note this can cause drawing of rectangles to look weird but actual data is still fine
    cv2.namedWindow("Window",cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Window", draw_rectangle)
    k = 0
    while True:
        # Display the image
        cv2.imshow("Window", image)
        k = cv2.waitKey(0)
        #If Q key is pressed close windows
        if k == 113:
            cv2.destroyAllWindows()
            rectangles.clear()
            image = resetImage.copy()
            break
        # If Z is pressed, clear the window, using the dummy image
        if k == 122 and undo:
            if previousImage is not None:
                # noinspection PyUnresolvedReferences
                image = previousImage.copy()
            print(rectangles)
            rectangles.pop()
            print(rectangles)
            #Seeting undo to false ensures that undo can only occur once otherwise constant pressing will delete rects from list
            undo = False
            cv2.imshow("Window", image)
        #If r is pressed then the image is reset all rectangles are removed
        if k == 114:
            image = resetImage.copy()
            rectangles.clear()
            cv2.imshow("Window", image)
        #If x is pressed it cuts rectangles and saves as separate images
        #Uses copy of original to avoid cut outs containing selection rectangle
        if k == 120:
            fluorescentLabelFolderName = f"{folderName} Fluorescent Labelled Cells"
            nucleusFolderName = f"{folderName} Nucleus Cells"
            if os.path.isdir(fluorescentLabelFolderName):
                shutil.rmtree(fluorescentLabelFolderName)
            if os.path.isdir(nucleusFolderName):
                shutil.rmtree(nucleusFolderName)
            if len(rectangles) >= 1:
                #Writes txt file of all coordinates
                coordinatesFolderName = f"{fluorescentLabelFolderName} Coordinates"
                if not os.path.isdir(coordinatesFolderName):
                    os.mkdir(coordinatesFolderName)
                with open(f"{coordinatesFolderName}/Cell Coordinates.txt","w+") as file:
                    for rect in rectangles:
                        file.write(f"{str(rect[0][0])}\n")
                        file.write(f"{str(rect[0][1])}\n")
                        file.write(f"{str(rect[1][0])}\n")
                        file.write(f"{str(rect[1][1])}\n")
                #Must use original image that has not been merged with nucleus for displaying
                cut_rectangles(imagePath,originalImage,rectangles,fluorescentLabelFolderName)
                cut_rectangles(nucleusImagePath,nucleusImage,rectangles,nucleusFolderName)


                cv2.destroyAllWindows()
                rectangles.clear()
                image = resetImage.copy()
                break
            else:
                print("Draw some rectangles!")
    #When window is closed will finish and return
    return True

topLeftCorner = []
bottomRightCorner = []
rectangles = []
previousImage = None
undo = True
