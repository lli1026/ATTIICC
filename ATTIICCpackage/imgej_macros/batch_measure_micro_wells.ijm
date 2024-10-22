// Set the base directories for original images and ROIs
inputDir = "/Users/lieli/Documents/PROJECTS/test_1a/data/f00d3_png/";
roiBaseDir = "/Users/lieli/Documents/PROJECTS/test_1a/data/ROIs/";
outputBaseDir = "/Users/lieli/Documents/PROJECTS/test_1a/data/measurement_micro_well/";

// Function to process each image and apply the ROIs
function processImage(imageFile) {
    // Set the directories
    originalPath = inputDir + imageFile;
    outputSubFolder = outputBaseDir;

    // Open the original image
    open(originalPath);
    originalImage = getImageID();
    
    // Create the corresponding ROI file name
    baseName = replace(imageFile, ".png", "");
    

    // Construct the ROI path
    roiFileName = baseName + "_rois.zip";
    roiPath = roiBaseDir + roiFileName;
    
    print(baseName);
    
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
        

        
        // Save the measurements to a CSV file in the appropriate subfolder
        csvPath = outputBaseDir + baseName + "_measurements.csv";
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
    

    // Process blueFiles in blueSubFolder
    files = getFileList(inputDir);
    print("Processing folder: " + inputDir);
    for (imgIndex = 0; imgIndex < files.length; imgIndex++) {
        processImage(files[imgIndex]);
    }

}
