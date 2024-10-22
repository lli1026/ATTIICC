// Directory containing the images and ROIs


// use below when calling macros from python
//imageDirectory = getArgument();
//outputDirectory = getArgument();
//roiDirectory = getArgument();

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

// Loop through all subfolders from f00d3_png to f32d3_png
for (n = 0; n <= 32; n++) {
    // Format the folder names manually
    if (n < 10) {
        folderPrefix = "f0" + n; // "f00", "f01", ..., "f09"
    } else {
        folderPrefix = "f" + n;  // "f10", "f11", ..., "f32"
    }
    
    bfSubFolder = folderPrefix + "d3_png/";

    // Process bfFiles in bfSubFolder
    bfFiles = getFileList(inputDir + bfSubFolder);
    print("Processing bfFolder: " + bfSubFolder);
    for (imgIndex = 0; imgIndex < bfFiles.length; imgIndex++) {
        processImage(bfFiles[imgIndex], bfSubFolder);
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
        
        // Save the duplicated image using the image title and ROI name as part of the filename
        saveAs("PNG", outputDir +  roiName + ".png");

        // Close the duplicated image
        close();
    }

    // Close the original image
    close();
}

