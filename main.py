import cv2
import shutil
from datetime import datetime
from fileMethods import *
from pathlib import Path
from threading import Thread
from SelectCells import select_cells,cut_rectangles,combine_images
from AnalyseFluorescence import analyse_fluorescence

#TODO Limit the amount of characters that can be used to name analysis to prevent problems with limits on excel sheetspyin
#TODO Add way of selecting cut images from folder
#TODO Maybe add way of dividing large images into smaller ones to allow for easier analysis of larger images

'''
Program to calculate the nuclear localisation of a given tagged fluorescent protein
User provides on image of the nucleus (or other compartment) and another of a tagged protein
Program then determines the localised intensity of the protein, the localisation ratio and the percentage of the protein that is nuclear 
Developed by: Thomas Young at Lancaster University Leonie Unterholzner Lab 2023
'''


windowSize = (650,275)
mainWindowTab = [
                [sg.Button("Select File",key="nucleusImageSelectButton"),sg.Text("Select Nucleus Image",key="nucleusImageSelectText")],
                [sg.Button("Select File",key="proteinImageSelectButton"),sg.Text("Select Fluorescent Label Image",key="proteinImageSelectText")],
                [sg.Text("Fluorescent protein colour:"),sg.Combo(["Red","Green"],readonly=True,default_value="Red",key="fluorescenceSelection")],
                [sg.Button("Extract cells",key="extractCellsButton",disabled=True),sg.Button("Reuse previous coordinates",key="reuseCoordButton",disabled=True)],
                [sg.Button("Add Data to Existing File",key="existingFileButton"),sg.Text("",key="excelFileSelectionText")],
                [sg.Text("Image Analysis Experiment Name:"),sg.InputText("",key="experimentName")],
                [sg.Button("Analyse Images",key="analyseImagesButton",disabled=True)],]

advancedOptionsTab = [[sg.Text("Fluorescent Background \nthreshold value",justification="left"),
                       sg.Slider(range=(1,255),resolution=1,default_value=1,enable_events=True, orientation= "horizontal", key="thresholdSlider"),
                       sg.Button("Show Image",key="thresholdShowImageButton",disabled=True)],
                      [sg.Text("Nuclear Background\nthreshold value",justification="left"),
                       sg.Slider(range=(1,255),default_value=1,enable_events=True, orientation= "horizontal", key="nuclearThresholdSlider"),
                       sg.Button("Show Image",key="nuclearThresholdShowImageButton",disabled=True)]]

# Prevents problems if the help.txt is not found
try:
    helpText = open("howToText.txt","r")
    howToTab = [[sg.Multiline(helpText.read(), size=windowSize, horizontal_scroll=True, disabled=True)]]
except:
    helpText= "Help text not found"
    howToTab = [[sg.Text(helpText)]]

windowLayout = [[sg.TabGroup([[sg.Tab("Main Window",mainWindowTab)],[sg.Tab("Advanced Options",advancedOptionsTab)],[sg.Tab("How To Guide",howToTab)]])]]

selectionWindowLayout = [[sg.Button("Open Image")],
                         [sg.Text("Select cells by left clicking and dragging to draw a box around the cell\n"
                                  "To undo a selection press the Z key\n"
                                  "To reset all selections press the R key\n"
                                  "To finish selections and save them as images press the X key\n"
                                  "To close the window press the Q key"),],
                         ]

bannedCharacters = [r"\ ", "/", "?", "%", "*", ":", ";", "|", "<", ">", ",", "="]
numberList = ["1","2","3","4","5","6","7","8","9","0"]
window = sg.Window("Nuclear Localisation Analysis",windowLayout,resizable=True,size=windowSize)
nucleusImageSelected = False
proteinImageSelected = False
excelFile = None
cellsDictionary = {}

while True:
    event,values = window.read()

    if event == sg.WIN_CLOSED or event == 'Cancel':  # If user closes window or clicks cancel
        break


    if event == "nucleusImageSelectButton":
        #Selects the image of the nucleus (DAPI stained)
        # Path object ensures that uses correct /
        nucleusImage = getFile()
        if nucleusImage is not None:
            nucleusImage = Path(nucleusImage).__str__()
            if os.path.splitext(nucleusImage)[-1] == ".tif":
                window["nucleusImageSelectText"].update(f"Nucleus file selected: {getFileName(nucleusImage)}")
                print(f"Selected image: {getFileName(nucleusImage)}")
                nucleusImageSelected = True
            else:
                nucleusImage = None
                sg.popup("Selected image must be a .tif file")

    if event == "proteinImageSelectButton":
        #Selects the image of the protein to determine the localisation of
        # Path object ensures that uses correct /
        proteinImage = getFile()
        if proteinImage is not None:
            proteinImage = Path(proteinImage).__str__()
            if os.path.splitext(proteinImage)[-1] == ".tif":
                window["proteinImageSelectText"].update(f"Fluorescent labelled file selected: {getFileName(proteinImage)}")
                print(f"Selected image: {getFileName(proteinImage)}")
                folderName = f"{getFileName(proteinImage)}"
                proteinImageSelected = True
            else:
                proteinImage = None
                sg.popup("Selected image must be a .tif file")

    if (nucleusImageSelected is True) and (proteinImageSelected is True):
        #Ensures buttons can only be used if cell images have been selected
        window["extractCellsButton"].update(disabled=False)
        window["reuseCoordButton"].update(disabled=False)
        window["nuclearThresholdShowImageButton"].update(disabled = False)
        window["thresholdShowImageButton"].update(disabled=False)
        combineImage = combine_images(proteinImage,nucleusImage,values["fluorescenceSelection"])


    if event == "extractCellsButton":
        #Sets the colour to be used for the fluorescent label, only really relevant in displaying the image to the user
        fluorescenceColour = values["fluorescenceSelection"]
        cellSelectionWindow = sg.Window("Selection Window", selectionWindowLayout)
        while True:
            event, values = cellSelectionWindow.read()

            if event == sg.WIN_CLOSED or event == 'Cancel':  # If user closes window or clicks cancel
                try:
                    #When selection is done will loop through both folders of fluorescent and nuclear images adding
                    #them to a dictionary to link them together for analysis
                    fluorescentLabelFolderName = f"{folderName} Fluorescent Labelled Cells"
                    nucleusFolderName = f"{folderName} Nucleus Cells"
                    cellsDictionary = {}
                    for fluorescentFile,nucleusFile in zip(os.listdir(fluorescentLabelFolderName),os.listdir(nucleusFolderName)):
                        if not fluorescentFile.endswith(".txt"):
                            cellsDictionary[f"{fluorescentLabelFolderName}/{fluorescentFile}"] = f"{nucleusFolderName}/{nucleusFile}"
                    window["analyseImagesButton"].update(disabled=False)
                except:
                    sg.Print("Error in selecting cells")
                break
            if event == "Open Image":
                #Produces two folders of images one with the nuclei one with the fluorescent label
                selectThread = Thread(target=select_cells, args=(proteinImage,nucleusImage,folderName,fluorescenceColour))
                #Threading is used to prevent the other GUI elements from crashing
                selectThread.start()

    if event == "thresholdShowImageButton":
        #Thresholds the image by setting any values below the threshold value to 0
        fluorescentImage = cv2.imread(proteinImage, cv2.IMREAD_GRAYSCALE)
        ret,threshImage = cv2.threshold(fluorescentImage,values["thresholdSlider"],255,cv2.THRESH_BINARY)
        cv2.namedWindow("Threshold Image", cv2.WINDOW_NORMAL)
        cv2.imshow("Threshold Image",threshImage)

    if event == "nuclearThresholdShowImageButton":
        # Thresholds the image by setting any values below the threshold value to 0
        fluorescentImage = cv2.imread(nucleusImage, cv2.IMREAD_GRAYSCALE)
        ret, threshImage = cv2.threshold(fluorescentImage, values["nuclearThresholdSlider"], 255, cv2.THRESH_BINARY)
        cv2.namedWindow("Threshold Image", cv2.WINDOW_NORMAL)
        cv2.imshow("Threshold Image", threshImage)



    if event == "reuseCoordButton":

        coordinatesFile = Path(getFile()).__str__()
        #Converts list of coordinates to usable list
        coordinatesList = file_to_coord(coordinatesFile)
        fluorescentLabelFolderName = f"{folderName} Fluorescent Labelled Cells"
        nucleusFolderName = f"{folderName} Nucleus Cells"
        #If folders already exist with same name will delete them
        if os.path.isdir(fluorescentLabelFolderName):
            shutil.rmtree(fluorescentLabelFolderName)
        if os.path.isdir(nucleusFolderName):
            shutil.rmtree(nucleusFolderName)
        #Cuts rectangles from images using coordinates list
        image = cv2.imread(proteinImage)
        imageNucleus = cv2.imread(nucleusImage)
        cut_rectangles(proteinImage, image, coordinatesList, fluorescentLabelFolderName)
        cut_rectangles(nucleusImage, imageNucleus, coordinatesList, nucleusFolderName)
        cv2.destroyAllWindows()
        coordinatesList.clear()

        cellsDictionary = {}
        #Adds all cells to a dictionary for analysis
        for fluorescentFile, nucleusFile in zip(os.listdir(fluorescentLabelFolderName), os.listdir(nucleusFolderName)):
            if not fluorescentFile.endswith(".txt"):
                cellsDictionary[f"{fluorescentLabelFolderName}/{fluorescentFile}"] = f"{nucleusFolderName}/{nucleusFile}"

        window["analyseImagesButton"].update(disabled=False)

    if event == "existingFileButton":
        excelFile =  getFile()
        print(excelFile.split("."))
        if "xlsx" in excelFile.split("."):
            #Name needs to have file extension removed for pandas to save dataframe
            excelFile = excelFile.split("/")[-1].replace(".xlsx","")
            window["excelFileSelectionText"].update(f"Excel file selected: {excelFile} ")
        else:
            sg.popup("That is not an excel file")
            excelFile = None
        print(excelFile)

    if event == "analyseImagesButton":
        if len(cellsDictionary) < 1:
            sg.popup_error("No cells selected to be analysed!")
        else:
            #Generates name for experiment if one not given
            if values["experimentName"] == "":
                experimentName = f"{getFileName(proteinImage,'/')} Nuclear Localisation"
            else:
                experimentName = values["experimentName"]
            #If no excel file has been selected to add the data to will save as a separate excel file
            if excelFile is None:
                analyse_fluorescence(cellsDictionary,values["thresholdSlider"],values["nuclearThresholdSlider"],experimentName)
            else:
                try:
                    analyse_fluorescence(cellsDictionary,values["thresholdSlider"],values["nuclearThresholdSlider"],experimentName,excelFile)
                except:
                    analyse_fluorescence(cellsDictionary, values["thresholdSlider"],values["nuclearThresholdSlider"],experimentName)
                    print(f"Failed to add data to sheet, saved as {experimentName}")
        try:
            time = datetime.now()
            with open(f"{fluorescentFile} {time.strftime('%d.%m.%Y %H.%M.%S')} Settings Used.txt","a") as file:
                file.write(f"Fluorescence Threshold Value Used: {values['thresholdSlider']}\n"
                           f"Nuclear Threshold Value Used: {values['nuclearThresholdSlider']}\n"
                           f"")
        except:
            sg.Popup(f"Error in saving threshold values.txt values were:\n"
                     f"Fluorescent: {values['thresholdSlider']}\n"
                     f"Nuclear: {values['nuclearThresholdSlider']}")

