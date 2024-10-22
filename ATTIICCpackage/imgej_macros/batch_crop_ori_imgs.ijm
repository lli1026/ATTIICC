// Directory containing the images and ROIs
// inputDir = "/Users/lieli/Documents/PROJECTS/test_1a/data/";
// outputBaseDir = "/Users/lieli/Documents/PROJECTS/test_1a/cropped_ori/";
// roiDir = "/Users/lieli/Documents/PROJECTS/test_1a/data/ROIs/";


fileList = getFileList(inputDir);

// Function to construct the ROI file name based on the image file name
function getROIFileName(imageName) {
    // Remove the last character from the image name
    baseName = substring(imageName, 0, lengthOf(imageName) - 1);
    return baseName + "3_rois.zip";
}

// Function to get the image title without extension
function getTitleWithoutExtension(title) {
    dotIndex = lastIndexOf(title, ".");
    if (dotIndex > 0) {
        return substring(title, 0, dotIndex);
    } else {
        return title;
    }
}

// Loop through all subfolders from f00d0 to f32d2
for (n = 0; n <= 32; n++) {
    // Format the folder names manually
    if (n < 10) {
        folderPrefix = "f0" + n; // "f00", "f01", ..., "f09"
    } else {
        folderPrefix = "f" + n;  // "f10", "f11", ..., "f32"
    }
    
    blueSubFolder = folderPrefix + "d0/";
    greenSubFolder = folderPrefix + "d1/";
    redSubFolder = folderPrefix + "d2/";


    // Process blueFiles in blueSubFolder
    blueFiles = getFileList(inputDir + blueSubFolder);
    print("Processing blueFolder: " + blueSubFolder);
    for (imgIndex = 0; imgIndex < blueFiles.length; imgIndex++) {
        processImage(blueFiles[imgIndex], blueSubFolder);
    }

    // Process greenFiles in greenSubFolder
    greenFiles = getFileList(inputDir + greenSubFolder);
    print("Processing greenFolder: " + greenSubFolder);
    for (imgIndex = 0; imgIndex < greenFiles.length; imgIndex++) {
        processImage(greenFiles[imgIndex], greenSubFolder);
    }

    // Process redFiles in redSubFolder
    redFiles = getFileList(inputDir + redSubFolder);
    print("Processing redFolder: " + redSubFolder);
    for (imgIndex = 0; imgIndex < redFiles.length; imgIndex++) {
        processImage(redFiles[imgIndex], redSubFolder);
    }
    
}

// Function to process an image
function processImage(fileName, subFolder) {
    imagePath = inputDir + subFolder + fileName;
    print("Attempting to open image at: " + imagePath);

    // Check if the file exists before attempting to open it
    if (!File.exists(imagePath)) {
        print("Error: File not found - " + imagePath);
        return; // Skip the file if it doesn't exist
    }

    // Open the current image
    open(imagePath);

    // Get the image title (name without extension)
    title = getTitle();
    imageTitle = getTitleWithoutExtension(title);

    // Get the corresponding ROI file name
    roiFileName = getROIFileName(imageTitle);
    print(roiFileName);

    // Get the ROI Manager instance
    roiManager("reset"); // Clear any existing ROIs
    roiManager("Open", roiDir + roiFileName); // Load the ROIs from the constructed .zip file name

    // Get the number of ROIs
    count = roiManager("count");

    // Create the corresponding output subfolder for this set of images
    outputDir = outputBaseDir + subFolder;
    print("Output directory: " + outputDir); // Debugging line to print the directory

    if (!File.exists(outputDir)) {
        File.makeDirectory(outputDir); // Create the output subfolder if it doesn't exist
        print("Created directory: " + outputDir); // Print when the directory is created
    }

    // Loop through all the ROIs for the current image
    for (i = 0; i < count; i++) {
        // Select the ROI at index i
        roiManager("Select", i);

        // Get the name of the ROI at index i
        roiName = RoiManager.getName(i);
        
        // Duplicate the selected ROI area and title the duplicate with the ROI name
        run("Duplicate...", "title=" + imageTitle + "_" + roiName);
        
        // Split the roiName by "_"
		roiParts = split(roiName, "_");

		// Get the last two parts from the roiName
		roiLastTwoParts = roiParts[lengthOf(roiParts)-2] + "_" + roiParts[lengthOf(roiParts)-1];

		// Construct the new image title by concatenating imageTitle and last two parts of roiName
		newImageTitle = imageTitle + "_" + roiLastTwoParts;

		// Save the image with the new title
		saveAs("PNG", outputDir + newImageTitle + ".png");

        // Close the duplicated image
        close();
    }

    // Close the original image
    close();
}
