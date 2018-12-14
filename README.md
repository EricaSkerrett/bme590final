# bme590final [![Build Status](https://travis-ci.org/EricaSkerrett/bme590final.svg?branch=master)](https://travis-ci.org/EricaSkerrett/bme590final)
Final Project for BME 590: Medical Device Software Design.

The server (final.py) for the processor is running on **vcm-7311.vm.duke.edu:5000**. The client that the image processing graphical user interface calls on (saved in client.py) makes GET and POST requests to this server.

(To run the server **locally without VCM**, go to the final.py and comment out last line of code:

`app.run(host="0.0.0.0")`

and use the following code instead:

`app.run(host="127.0.0.1")`

Then go to the client.py and comment out line 4: 

`api_host = "http://vcm-7311.vm.duke.edu:5000"`

and use the following code instead:

`api_host = "http://127.0.0.1:5000`

Then user will be able to run the final.py as local server instead.)

To access the Image Processor, save final.py, client.py, and gui.py to your local machine. Then run gui.py locally. This will bring up the interface for the processor.

The first window in the processor asks for the user to either create a new user ID or to sign in as a return user. The user ID must be **a valid email address** that will serve as the method of identification for all image entries saved into the image processor database. Any return user must already exist in the database, or an error message will pop up.

The next window allows the user to upload images (either individually or stored in a .zip file). They will then be allowed to select from all the images they just uploaded in order to view the selected image and choose which type of processing they wish to perform on that image. Note that the user must click on the image in order to select it, if the user does not click on the image an error message will pop up.

Note that the interface will allow users to upload and view both JPEG and PNG files. However, to view processed images WITHIN the interface, the user must upload a JPEG-format image.

The user is allowed to choose from "Histogram Equalization", "Contrast Stretching", "Log Compression", and "Reverse Video" as the forms of processing to perform on their selected image. After viewing the processing performed on the image, the user is given the option of downloading this image as either a JPG, PNG, or TIFF file to their local device. If the user initially uploaded a PNG type image, the downloaded image will allow the user to view the processing performed on the image.

Other information stored in the database that is accessible to the user are user metrics (the number of images uploaded, the number of images processed, the number of times each processing type was performed by the user, and the time the last processing instance took to perform), the size of each image uploaded, and timestamps for upload times for each processed image. The user metrics, image size, and upload timestamp will appear on the screen each time a newly processed image is viewed. The database also stores information such as the original image format and the processed image timestamp.

After processing/downloading an image, the user also has the ability to view histograms for the original and processed image, which are accessible by clicking the histograms button in the processed image viewing screen.
