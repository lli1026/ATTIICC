// Set the base directories for original images and ROIs
//inputDir = "/Users/lieli/Documents/PROJECTS/test_1a/cropped_ori_bg/";
//roiBaseDir = "/Users/lieli/Documents/PROJECTS/test_1a/seg_cropped_ori_d3/";
//outputBaseDir = "/Users/lieli/Documents/PROJECTS/test_1a/measurements_using_seg_ori_d3/";

// Function to process each image and apply the ROIs
function processImage(imageFile, subFolder) {
    // Set the directories
    originalPath = inputDir + subFolder + imageFile;
    outputSubFolder = outputBaseDir + subFolder;

    // Open the original image
    open(originalPath);
    originalImage = getImageID();
    
    // Create the corresponding ROI file name
    baseName = replace(imageFile, "_bg.png", "");
    
    // Find the positions of the underscores
    underscorePositions = newArray();
    for (j = 0; j < lengthOf(baseName); j++) {
        if (substring(baseName, j, j + 1) == "_") {
            underscorePositions = Array.concat(underscorePositions, j);
        }
    }

    // Check if there are at least 3 underscores
    if (lengthOf(underscorePositions) >= 3) {
        // Position of the third underscore
        thirdUnderscorePos = underscorePositions[2];
    
        // Replace the last character before the third underscore with "3"
        newBaseName = substring(baseName, 0, thirdUnderscorePos - 1) +"3"+ substring(baseName, thirdUnderscorePos, lengthOf(baseName));
    } else {
        newBaseName = baseName; // If less than 3 underscores, keep the name as it is
    }

    // Adjust the ROI subfolder by removing the 'd0', 'd1', or 'd2' suffix from subFolder
    roiSubFolder = replace(subFolder, "d0/", "d3_png/");  // Replace 'd0/' with '/'
    roiSubFolder = replace(roiSubFolder, "d1/", "d3_png/");  // Replace 'd1/' with '/'
    roiSubFolder = replace(roiSubFolder, "d2/", "d3_png/");  // Replace 'd2/' with '/'

    // Construct the ROI path
    roiFileName = newBaseName + "_rois_rois.zip";
    roiPath = roiBaseDir + roiSubFolder + roiFileName;
    
    print(baseName);
    print(newBaseName);
    print(roiFileName);
    print(roiPath);  // Print the full path of the expected ROI file

    // Check if the ROI file exists
    if (File.exists(roiPath)) {
        print("ROI file found: " + roiPath);
        roiManager("Reset");
        roiManager("Open", roiPath);
        
        // Check if ROIs are loaded
        if (RoiManager.size == 0) {
            print("No ROIs found in file: " + roiPath);
            close();
            return;
        }
        
        // Apply the ROIs to the original image
        selectImage(originalImage);
        roiManager("Show All with labels");
        
        // Set measurements to include mean, centroid, and display labels
        run("Set Measurements...", "area shape mean centroid display redirect=None decimal=5");
        
        // Measure the intensity of the original image within the ROIs
        roiManager("Measure");
        
        // Create the output directory if it doesn't exist
        if (!File.exists(outputSubFolder)) {
            File.makeDirectory(outputSubFolder);
        }
        
        // Save the measurements to a CSV file in the appropriate subfolder
        csvPath = outputSubFolder + baseName + "_measurements.csv";
        saveAs("Results", csvPath);
        
        // Clear the results table and ROI Manager for the next iteration
        run("Clear Results");
        roiManager("Deselect");
        roiManager("Delete");
    } else {
        print("ROI file not found for image: " + imageFile);
    }
    
    // Close the original image
    close();
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
