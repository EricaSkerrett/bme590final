# bme590final [![Build Status](https://travis-ci.org/EricaSkerrett/bme590final.svg?branch=master)](https://travis-ci.org/EricaSkerrett/bme590final)
Final Project for BME 590: Medical Device Software Design.

The server (final.py) is running on **http://vcm-7311.vm.duke.edu:5000**. The client that the image processing graphical user interface calls on (saved in client.py) makes GET and POST requests to this server.

To access the Image Processor, save final.py, client.py, and gui.py to your local machine. Then run gui.py locally. This will bring up the interface for the processor.

The first window in the processor asks for the user to either create a new user ID or to sign in as a return user. The user ID must be a valid email address that will serve as the method of identification for all image entries saved into the image processor database. Any return user must already exist in the database.

The next window allows the user to upload images (.jpg, .png, or .tiff type images, or images stored in a .zip). They will then be allowed to select from all the images they have ever uploaded to the database (including images from past uploads) in order to view the selected image and choose which type of processing they wish to perform on that image.

The user is allowed to choose from "Histogram Equalization", "Contrast Stretching", "Log Compression", and "Reverse Video" as the forms of processing to perform on their selected image. After viewing the processing performed on the image, the user is given the option of downloading this image as either a JPG, PNG, or TIFF file to their local device.

Other information stored in the database that is accessible to the user via the interface are user metrics (the number of images uploaded, the number of images processed, the number of times each processing type was performed by the user, and the time the last processing instance took to perform), the size of each image uploaded, the original format of each image uploaded, and timestamps for upload times and process times for each image.
