# Nuclear-Localisation
A program written for the PhD of Thomas Young. This program determines the relative nuclear localisation of fluorescently tagged proteins.
Work is lisenced under Creative Commons BY-NC 4.0  https://creativecommons.org/licenses/by-nc/4.0/ 

To use this program two images are required, a single channel image of the nucleus and a single channel image of a fluorescent tag
Requirements for the images:
    - They must be the same size
    - In focus images will provide more accurate analysis
    - Artificially modifying one image e.g increasing brightness, without changing the other may affect accuracy
    - The image MUST BE A .tif FILE this is because when the cells are extracted the individual images are saved as .tif images
      if a non-tif image is given at the start e.g .jpg then the conversion between the two imaging formats will change
      the intensity values in the image. This is especially a problem when using the thresholding values to remove background

To start use select file to select the image of the nucleus then again for the fluorescent image
Then choose the colour of the fluorescent label(red or green), this does not affect the localisation analysis but is used to merge the two images
when selecting the cells so that both the nucleus and the fluorescent label is visible

From here you have two options, extracting the cells from the image or reusing previous coordinates.
Extracting the cells will allow you to identify all the cells in your image
Reusing coordinates will use the previous selections from another extraction

Extracting the cells:

Select the "Extract cells" button and a window will be brought up showing your image and a pop up explaining how to select your cells
From the image shown click and drag around each individual cell to select it, you can use the "Z" key to undo a selection (This is only able to go back one selection)
To completely reset all selections press the "R" key
It is not a problem for the program if your selections overlap
Once happy that you have selected all of the cells in the image press the "X" key
This will extract all of your selection as individual images, one set for the nuclei and another for the fluorescent label
These images will be saved in their own folders in the same location as the program is running from
It is important that you do not add ANY files or change anything in these folders as it could cause the program to incorrectly pair the images.
If you need to use the images in the folders copy and paste them to use elsewhere

Reusing coordinates:

When you extract the cells from an image a .txt file will be saved in a folder called -your image name- Coordinates
This .txt file contains the coordinates needed to extract the same cells from an image again, this is useful for example
when you have two fluorescent tagged proteins and want to reuse the same cells
Note this of course only works on images that are the same, it is not intended to be used on different conditions
Select the reuse coordinates button and find the .txt file with the coordinates, this will then use the same coordinates
to extract the same cells from any images you have provided to the program

Thresholding Images:

Confocal images can contain a high amount of background intensity that may appear black to a person looking at it but the
computer would still count as a fluorescent pixel. To help with this in the "Advanced options" section there are two sliders
that allow the threshold value of the nucleus and fluorescent images to be set. Any pixels less intense than the value given
will not be included in analysis. The show image button can be used to get a preview of what the images will look like
with the threshold value. If the highlight pixels option is checked then any pixel that would be included in analysis
is set to maximum intensity, this can make it easier to identify background pixels (note that this is for display purposes
only, it does not change the intensity of images when analysed)

Analysing Images:

Now that the cells have been extracted either manually or by reusing coordinates, press the "Analyse Images" button,
If you want to give the spreadsheet with the data a custom name enter it in the "Image Analysis Experiment Name" text box.
If you wish to add the data from this analysis to an existing spreadsheet, use the "Add Data To Existing File" Button, this
will bring up a window that allows you to select an existing excel file, the data will be added in a new sheet.
If there is a problem in saving the data to that spreadsheet, could be caused by user still having the spreadsheet open
then the data will be save as a separate spreadsheet
The name of the sheet can be determined by giving a name in the "Image Analysis Experiment Name" text box
When the program is done analysing images it will save the results as an excel document in the same location the program is running in
If you provided a name then that will be used for the excel document, if not it will be named after your images

Additional Notes:

    - The localisation does not have to be to a nucleus, the program will determine the localisation of any two images
    - The colour of the images does not affect analysis as the images are analysed in black and white
    - If the program appears as not responding during analysis simply hit wait for program it should eventually complete
    - In Advanced options you can change the background thresholding values for the nucleus and fluorescent images, this
      prevents background pixels from being counted during analysis, use the show image buttons to preview what the image
      will look like.
    - Do not change or modify the .txt file containing the coordinates in any way this will prevent them from being able to be used
    - Do not add or change files in any of the folders containing extracted images, the program uses their order to pair
      up the right fluorescence with the correct nucleus
    - Give your experiment a unique name or the program may overwrite excel files with the same name
    - When selecting cells it is best to select as small an area as possible containing the cell, larger images will not
      affect analysis but will cause it to take longer
    - Explanations of the three parameters measured can be found in:
      Kelley JB, Paschal BM. Fluorescence-based quantification of nucleocytoplasmic transport.
      Methods. 2019 Mar 15;157:106-114.
      doi: 10.1016/j.ymeth.2018.11.002. Epub 2018 Nov 10. PMID: 30419335; PMCID: PMC7041306.
    - Use this program at your own risk no guarantees are made as to its accuracy
