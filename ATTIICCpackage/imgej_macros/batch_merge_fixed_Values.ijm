// To use this macro, edit the inputDir and outputDir and the subfolder numbers(each field has its own folder)

// Set the input and output directories directly
inputDir = "/home/lilly/Documents/PROJECTS/test_tumor_only/test_data_tumor_only/";
outputDir = "/home/lilly/Documents/PROJECTS/test_tumor_only/merged/";

// Set a fixed maximum brightness/contrast value
fixedBlueMaxBrightness = 281; // Adjust this value as needed
fixedGreenMaxBrightness = 351; // Adjust this value as needed
fixedRedMaxBrightness = 288; // Adjust this value as needed
fixedBlueMinBrightness = 118;   // This sets the minimum value, typically 0
fixedGreenMinBrightness = 146;   // This sets the minimum value, typically 0
fixedRedMinBrightness = 72;   // This sets the minimum value, typically 0

// Loop through all subfolders from f00 to f32
for (n = 0; n <= 1; n++) {
    // Format the folder names manually
    if (n < 10) {
        folderPrefix = "f0" + n; // "f00", "f01", ..., "f09"
    } else {
        folderPrefix = "f" + n;  // "f10", "f11", ..., "f32"
    }
    
    blueSubFolder =  folderPrefix + "d0/";
    greenSubFolder =  folderPrefix + "d1/";
    redSubFolder = folderPrefix + "d2/";
    print("blueSubFolder:"+blueSubFolder);
    // List files in the blue subfolder
    blueFiles = getFileList(inputDir + blueSubFolder);
    
    // Process each image set by their base names (p00 through p15)
    for (i = 0; i < blueFiles.length; i++) {
        blueFile = blueFiles[i];
        
        // Extract base name by removing "f00d0.TIF" (8 characters) from the end
        baseName = substring(blueFile, 0, lengthOf(blueFile) - 9);
		
        // Construct the corresponding green and red file names
        greenFile = baseName + folderPrefix + "d1.TIF";
        redFile = baseName + folderPrefix + "d2.TIF";
        
        // Create a folder for this `folderPrefix` if it doesn't exist
    	outputFolderPath = outputDir + folderPrefix + "/";
    	if (!File.exists(outputFolderPath)) {
        	File.makeDirectory(outputFolderPath);
        	print("Created directory: " + outputFolderPath);
    	}

        // Check if corresponding green and red files exist
        if (File.exists(inputDir + greenSubFolder + greenFile) && File.exists(inputDir + redSubFolder + redFile)) {
            
            // Open and process the blue image
            open(inputDir + blueSubFolder + blueFile);
            setMinAndMax(fixedBlueMinBrightness, fixedBlueMaxBrightness); // Apply fixed brightness/contrast
            blueImage = getTitle();
            
            // Open and process the green image
            open(inputDir + greenSubFolder + greenFile);
            setMinAndMax(fixedGreenMinBrightness, fixedGreenMaxBrightness); // Apply fixed brightness/contrast
            greenImage = getTitle();
            
            // Open and process the red image
            open(inputDir + redSubFolder + redFile);
            setMinAndMax(fixedRedMinBrightness, fixedRedMaxBrightness); // Apply fixed brightness/contrast
            redImage = getTitle();
            
            // Merge channels
            selectWindow(blueImage);
            run("Merge Channels...", "c3=" + blueImage + " c2=" + greenImage + " c1=" + redImage + " create");
            
            // Convert the merged image to RGB
            run("RGB Color");

            // Save the merged image
            saveAs("png", outputFolderPath + baseName + folderPrefix + ".png");
            close();
            
            // Close individual images
            close(blueImage);
            close(greenImage);
            close(redImage);
        
        } else {
            print("Corresponding files not found for " + baseName + " in folder " + folderPrefix + ". Skipping.");
        }
    }
}
