import cv2
import pandas as pd
import PySimpleGUI as sg
from fileMethods import getFileName

def analyse_fluorescence(cellDictionary,fluorescentThreshold=25,nuclearThreshold=10,
                         fileName ="Nuc Localisation",excelFile=None):

    assert type(cellDictionary) == dict
    assert len(cellDictionary) >= 1
    debugSave = False
    analysing = True
    progress = 0
    windowLayout = [[sg.Text('Progress:')],
              [sg.ProgressBar(len(cellDictionary), orientation='h', size=(20, 20), key='-PROG-')],
              [sg.Button("Begin Analysis")]]
    window = sg.Window("Progress bar",windowLayout)
    #Window will initialise without running through cell dictionary loop, therefore need being analysis button,
    # which doesn't actually do anything specific but forces the cell dictionary loop to begin running
    while analysing:
        #Window.refresh() is called during some loops to prevent not responding windows error
        event,values = window.read()

        localisedFluorescence = {}
        dataList = []
        nameList = []
        for cell in cellDictionary:
            averageNuclearIntensity, nuclearIntensityRatio, percentageNuclear = 0,0,0
            nuclearLocations = []
            #Seperates the two images

            fluorescentImage = cv2.imread(cell,cv2.IMREAD_GRAYSCALE)
            nuclearImage = cv2.imread(cellDictionary[cell], cv2.IMREAD_GRAYSCALE)
            #Gets all pixel locations that correspond to a nucleus
            for x in range(0, nuclearImage.shape[0]):
                for y in range(0, nuclearImage.shape[1]):
                    window.refresh()
                    if nuclearImage[x,y] >= nuclearThreshold:
                        nuclearLocations.append((x,y))
            nuclearIntensities = []
            nonNuclearIntensities = []
            #Any fluorescent tagged locations within the nucleus
            for x in range(0,fluorescentImage.shape[0]):
                for y in range(0,fluorescentImage.shape[1]):
                    window.refresh()
                    if fluorescentImage[x,y] >= fluorescentThreshold:
                        if (x,y) in nuclearLocations:
                            nuclearIntensities.append(fluorescentImage[x,y])
                        else:
                            nonNuclearIntensities.append(fluorescentImage[x,y])
            if debugSave:
                fluorescentDebugImage = fluorescentImage.copy()
                nonfluorescentDebugImage = fluorescentImage.copy()
                for x in range(0, fluorescentDebugImage.shape[0]):
                    for y in range(0, fluorescentDebugImage.shape[1]):
                        if (x,y) not in nuclearLocations:
                            fluorescentDebugImage[x][y] = 0
                        else:
                            nonfluorescentDebugImage[x][y] = 0
                cv2.imwrite(f"NuclearDebug{cellDictionary[cell].split('/')[-1]}",fluorescentDebugImage)
                cv2.imwrite(f"NonNuclearDebug{cellDictionary[cell].split('/')[-1]}", nonfluorescentDebugImage)



            compareCellsText = f"{cellDictionary[cell].split('/')[-1]} and {cell.split('/')[-1]}"
            #If there are no nuclear intensities this means no fluorescence found in nucleus therefore is set to 0
            if nuclearIntensities == []:
                nuclearIntensities = [0]
            #If there are no non-nuclear intensities then it is all in the nucleus so nonNuclear intensities is set to 0
            if nonNuclearIntensities == []:
                nonNuclearIntensities = [0]
            #Tries to do all calculations, if there is an error then all values are set to "Error in calculations"
            try:
                #Average intensity just of values within the nucleus
                averageNuclearIntensity = round(sum(nuclearIntensities)/len(nuclearIntensities))
                #Average Intensity of values not in nucleus
                averageCytoplasmicIntensity = round(sum(nonNuclearIntensities)/len(nonNuclearIntensities))
                #Number higher than one indicates molecule is predominantly nuclear, less than means predominantly cytoplasmic
                nuclearIntensityRatio = round(averageNuclearIntensity/averageCytoplasmicIntensity,2)
                percentageNuclear = round((sum(nuclearIntensities)/(sum(nonNuclearIntensities)+sum(nuclearIntensities)))*100)
            except:
                averageNuclearIntensity,\
                nuclearIntensityRatio,\
                percentageNuclear = "Error in calculations","Error in calculations","Error in calculations"

            #Adds all data to a list
            dataList.append([averageNuclearIntensity,nuclearIntensityRatio,percentageNuclear])
            progress +=1
            window['-PROG-'].update(progress)
            sg.Print(f"{compareCellsText}",text_color="blue")
            sg.Print(f"Nuclear Size: {len(nuclearLocations)}\n"
                     f"Cytoplasmic Size: {len(nonNuclearIntensities)}")
            sg.Print(f"Average Nuclear intensity: {averageNuclearIntensity}\n"
                     f"Nuclear Intensity Ratio: {nuclearIntensityRatio}\n"
                     f"Percentage Nuclear: {percentageNuclear}\n")
            #Adds name of the image to a list
            nameList.append(cell.split("/")[-1])
            localisedFluorescence[cell] = (averageNuclearIntensity,nuclearIntensityRatio,percentageNuclear)

        df = pd.DataFrame(dataList, columns=["Average Nuclear Intensity", "Nuclear Intensity Ratio", "Nuclear Percentage"],
                          index=nameList)
        if excelFile is None:
            df.to_excel(f"{fileName}.xlsx", sheet_name=f"{fileName}")
            sg.popup(f"Analysis complete!\n"
                     f"Your file has been saved as {fileName}.xlsx", title="Analysis Status")
        else:

            with pd.ExcelWriter(f"{excelFile}.xlsx",engine="openpyxl",mode="a") as writer:
                df.to_excel(writer, sheet_name=f"{fileName}")

            sg.popup(f"Analysis complete\n"
                     f"Your data has been saved as sheet {fileName} in {excelFile}")
        print("Data added to excel")
        analysing = False

    return localisedFluorescence
