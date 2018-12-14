# bme590final [![Build Status](https://travis-ci.org/EricaSkerrett/bme590final.svg?branch=master)](https://travis-ci.org/EricaSkerrett/bme590final)
Final Project for BME 590: Medical Device Software Design.

## Project Server
The server (final.py) for the processor is running on **vcm-7311.vm.duke.edu:5000**. The client that the image processing graphical user interface calls on (saved in client.py) makes GET and POST requests to this server.

### Running the Server Locally
To run the server **locally, without the VCM**, open final.py and comment out the last line of code:
`app.run(host="0.0.0.0")`
and uncomment the following code to use instead:
`app.run(host="127.0.0.1")`

Then, open client.py and comment out line 4: 
`api_host = "http://vcm-7311.vm.duke.edu:5000"`
and uncomment the following code to use instead:
`api_host = "http://127.0.0.1:5000"`

Then the user will be able to run final.py as a local server.

## Using the Image Processor Interface
To run the Image Processor, fork this repository and ensure that you have saved **final.py, client.py, gui.py, and the repository images** to your local machine. Then run gui.py locally. This will bring up the interface for the processor.

The first window in the processor asks for the user to either create a new user ID or to sign in as a return user. The user ID must be **a valid email address** that will serve as the method of identification for all image entries saved into the image processor database. Any return user must already exist in the database, or an error message will pop up.

The next window allows the user to upload images (either individually or stored in a .zip file). They will then be allowed to select from all the images they just uploaded in order to view the selected image and choose which type of processing they wish to perform on that image. Note that the user must click on the image in order to select it, if the user does not click on the image an error message will pop up.

The interface will allow users to upload and view both JPG and PNG files and process these images within the interface.

The user is allowed to choose from "Histogram Equalization", "Contrast Stretching", "Log Compression", and "Reverse Video" as the forms of processing to perform on their selected image. After viewing the processing performed on the image, the user is given the option of downloading this image as either a JPG, PNG, or TIFF file to their local device.

**Note: currently the processor does not support Histogram Equalization or Reverse Video processing for PNG images. To perform these processing types, upload the image as a JPG file.**

Other information stored in the database that is displayed to the user while viewing a processed image includes user metrics (the number of images uploaded, the number of images processed, the number of times each processing type was performed by the user, and the time the last processing instance took to perform), the size of the image uploaded, and the timestamp of the upload time for the image. The database also stores for internal use, but does not display, information such as the original image format and the processed image timestamp.

After processing/downloading an image, the user also has the ability to view histograms for the original and processed image, which are accessible by clicking the histograms button in the processed image viewing screen. Clicking on this button will also save the histogram locally under hist.jpeg. Then, the user can return to the upload images window to process a new image.

To watch a demo of the processor in action, see Processor_Demo.mp4 within this repository!
