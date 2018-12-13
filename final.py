from flask import Flask, jsonify, request
from pymodm import connect, MongoModel, fields
import time
from datetime import datetime, timedelta
import base64
import io
import matplotlib.image as mpimg
import matplotlib
from matplotlib import pyplot as plt
import zipfile
import skimage
from skimage import exposure, color
from skimage.viewer import ImageViewer
import imghdr
import scipy
import logging
import numpy as np
# matplotlib.use('TkAgg')


connect("mongodb://sputney13:sputney13@ds161901.mlab.com:61901/bme590final")
app = Flask(__name__)

logging.basicConfig(filename="final.log", filemode='w', level=logging.INFO)


class ImageDB(MongoModel):
    user_email = fields.EmailField(primary_key=True)
    uploaded_images = fields.ListField(field=fields.DictField())
    image_formats = fields.ListField(field=fields.DictField())
    upload_times = fields.ListField(field=fields.DateTimeField())
    image_size = fields.ListField(field=fields.DictField())
    processed_info = fields.ListField(field=fields.DictField())
    user_metrics = fields.DictField()


def validate_create_user(r):
    """ Validates user input for posts to /image/user

    Args:
        r: dictionary containing user_email key for posting to database

    Raises:
        AttributeError: when post does not contain proper key
        TypeError: when user_email key is not an email (does not have an @)

    """
    if "user_email" in r:
        if "@" not in r["user_email"]:
            logging.exception("TypeError: user_email is not an email string.")
            raise TypeError("user_email must be an email string.")
    else:
        logging.exception("AttributeError: post does not contain"
                          " user_email key.")
        raise AttributeError("Post must be dict with user_email key.")
    logging.info("Passed create user validation.")


def init_user_metrics(user_email):
    """ Creates the user_metrics dict for new user with all keys set to 0

    Args:
        user_email: the new user's email string (database id)

    Returns:
        user_metrics: a dictionary to hold the metrics for that user's
                      processes, with all keys initially set to 0

    """
    user_metrics = {"User": user_email,
                    "Images Uploaded": 0,
                    "Images Processed": 0,
                    "HistogramEqualization": 0,
                    "ContrastStretching": 0,
                    "LogCompression": 0,
                    "ReverseVideo": 0,
                    "Time to Complete Last Process": 0}
    logging.info("User metrics for " + user_email + " initialized.")
    return user_metrics


@app.route("/image/user", methods=["POST"])
def create_user():
    """ POSTS a new user's email and their initialized metrics to database

    Returns:
        200 status after posting has occurred

    """
    r = request.get_json()
    validate_create_user(r)
    user_metrics = init_user_metrics(r["user_email"])
    entry = ImageDB(r["user_email"], user_metrics=user_metrics)
    entry.save()
    logging.info("New user stored in database.")
    return "Created", 200


@app.route("/image/user/<user_email>", methods=["GET"])
def returning_user(user_email):
    """ GETS a returning image processor user (identified by email) from db

    Args:
        user_email: string containing returning user's email

    Returns:
         email: json containing user_email and error_message keys

    """
    for user in ImageDB.objects.raw({}):
        if user.user_email == user_email:
            email = {
                    "user_email": user_email,
                    "error_message": 'None'
                    }
            logging.info("Return user accessed.")
            break
        else:
            email = {"user_email": "Not in database",
                     "error_message": 'User not in database. Please enter'
                                      ' an email in the database or create'
                                      ' a new user.'}
            logging.exception("User not in the database.")
    return jsonify(email)


def validate_image_upload(r):
    """ Validates user inputs for posts to /image/upload

        Args:
            r: dictionary containing keys of image names and values
               of the base64 string encoded image

        Raises:
            TypeError: when the image names or the image strings are not
                       string types
            AttributeError: when the image name contains a / or .

        """
    for image_name in r.keys():
        if type(image_name) is not str:
            raise TypeError("Image name must be a string.")
        if '/' in image_name or '.' in image_name:
            raise AttributeError("Image name cannot contain . or /")
    for image_string in r.values():
        if type(image_string) is not str:
            raise TypeError("Image value must be a base64 string.")


def image_encoder(image):
    """ Encodes image into base64 type bytes

    Args:
        image: the name of the image to be encoded

    Returns:
         base_64_string: the base64 type bytes representing the image

    """
    with open(image, "rb") as image_file:
        base64_bytes = base64.b64encode(image_file.read())
    return base64_bytes


def image_parser(file_list):
    """ Parses, encodes, and finds formats for uploaded images

    Args:
        file_list: list containing strings of file names or
        zip folder of images to be encoded

    Returns:
        image_dict: dictionary of images and their encoded base64 string

    """
    image_dict = {}
    for file in file_list:
        if file.endswith('.zip'):
            image_names = unzip_folder(file)

            file_list.remove(file)
            file_list.append(image_names)
    for image in file_list:
        if type(image) is list:
            for contents in image:
                file_list.append(contents)
            file_list.remove(image)
    for image in file_list:
        if image.endswith('.jpg') or image.endswith('.png') or image\
                .endswith('.tiff'):
            base64_bytes = image_encoder(image)
            base64_string = base64_bytes.decode("UTF-8")
            image_only_list = image.split('/')
            image_only = image_only_list[-1]
            image_list = image_only.split('.')
            image_name = image_list[0]
            image_dict.update({image_name: base64_string})
        else:
            file_list.remove(image)
    return image_dict


def b64string_encoder(b64string):
    """ Encodes string base64 type into bytes base64 type

    Args:
        b64string: the string base64 of an image

    Returns:
         b64bytes: the bytes base64 type

    """
    b64bytes = b64string.encode("UTF-8")
    return b64bytes


def unzip_folder(zipped_folder):
    """ Reads items from a zipped folder and stores in list

    Args:
        zipped_folder: string containing name of .zip folder to be read

    Returns:
        file_list: list of items in .zip folder in style of
        "foldername/file.ext"

    """
    zf = zipfile.ZipFile(zipped_folder, 'r')
    name_list = zf.namelist()
    return name_list


def zip_images(image_list):  # for image downloads
    """ Adds 1 image at a time to a zipfile "downloaded_images.zip"
        for when the user selects multiple images.
        Pass zipped file through unzip_folder("downloaded_images.zip")
        to view.

    Args:
        image_list: list[] of images by "foldername/file.ext"
        that need to be zipped

    Returns:
         zf: closed zip file with appended image paths/names

    """
    zf = zipfile.ZipFile("downloaded_images.zip", "w")
    for image in image_list:
        zf.write(image)
    zf.close()
    return zf


@app.route("/image/upload/<user_email>", methods=["POST"])
def image_upload(user_email):
    """ POSTs user-uploaded image to database

    Posts user-uploaded image as an encoded base64 string as well as image
    upload time, format, and size to database under the user's email.
    Updates metrics for user based off number of images uploaded.

    Returns:
        200 status after the posting has occurred

    """
    r = request.get_json()
    validate_image_upload(r)
    image_dict = r
    image_size = get_size(image_dict)
    image_format = get_format(image_dict)
    upload_time = datetime.now()

    image = ImageDB.objects.raw({"_id": user_email}).first()
    image.uploaded_images.append(image_dict)
    image.upload_times.append(upload_time)
    image.image_size.append(image_size)
    image.image_formats.append(image_format)
    image.user_metrics["Images Uploaded"] += len(image_dict)
    image.save()
    return "Uploaded", 200


def list_to_dict(dict_images):
    """ Takes a list of dictionaries and sorts them into a single dict

    Args:
        dict_images: A list of dictionaries containing images

    Returns:
        uploaded_images: a dictionary containing all the keys and info
                         from the dict_images list
    """
    uploaded_images = {}
    for dicts in dict_images:
        for image in dicts.keys():
            uploaded_images.update({image: dicts[image]})
    return uploaded_images


@app.route("/image/upload/<user_email>", methods=["GET"])
def get_uploaded_images(user_email):
    """ Retrieves all uploaded images for specified user

    Args:
        user_email: email of user that has the desired uploaded images

    Returns:
        uploaded_images: dict containing all uploaded image keys
                         and strings

    """
    image = ImageDB.objects.raw({"_id": user_email}).first()
    uploads = image.uploaded_images
    uploaded_images = list_to_dict(uploads)
    return jsonify(uploaded_images)


@app.route("/image/upload_time/<user_email>", methods=["GET"])
def get_upload_time(user_email):
    """ Retrieves user's upload timestamps for all uploaded images

    Args:
        user_email: user's email ID

    Returns:
        upload_times: dict containing image_name as keys and upload_time
                      for image as its value

    """
    user_email = str(user_email)
    image = ImageDB.objects.raw({"_id": user_email}).first()
    upload_times = {}
    uploads = image.uploaded_images
    times = image.upload_times
    for i in range(len(uploads)):
        upload_time = times[i]
        for keys in uploads[i].keys():
            upload_times.update({keys: upload_time})
    return jsonify(upload_times)


@app.route("/image/upload_size/<user_email>", methods=["GET"])
def get_upload_sizes(user_email):
    """ Retrieves user's upload sizes for all uploaded images

    Args:
        user_email: user's email ID

    Returns:
         upload_sizes: json containing image_name as keys and
                       size of image as its value

    """
    user_email = str(user_email)
    image = ImageDB.objects.raw({"_id": user_email}).first()
    size_dicts = image.image_size
    upload_sizes = list_to_dict(size_dicts)
    return jsonify(upload_sizes)


def get_size(image_dict):
    """ Reads images from dictionary to find image size

    Args:
        image_dict: dictionary containing base64 values and image name keys

    Returns:
        size_dict: dictionary containing size values and image name keys
        Sizes are in tuples (H, W, D)

    """
    image_name = image_dict.keys()
    size_dict = {}
    for image in image_name:
        img_buf = decode(image_dict[image])
        i = skimage.io.imread(img_buf)
        size = i.shape
        size_dict.update({image: size})
    return size_dict


def decode(encoded_image):
    """ Takes an encoded image and decodes it for further processing

    Args:
        encoded_image: base64 string encoding list

    Returns:
        img_buf: buffered bytes object

    """
    img_bytes = base64.b64decode(encoded_image)
    img_buf = io.BytesIO(img_bytes)
    return img_buf


def get_format(image_dict):
    """ Opens images from dictionary to find image format

    Args:
        image_dict: dictionary containing base64 values and image name keys

    Returns:
        format_dict: dictionary containing image format values and
        image name keys. Formats are strings

    """
    image_name = image_dict.keys()
    format_dict = {}
    for image in image_name:
        image_buf = decode(image_dict[image])
        im_format = imghdr.what(image_buf)
        format_dict.update({image: im_format})
    return format_dict


def validate_image_processed_upload(r):
    """ Validates user inputs for posts to /image/processed/upload

    Args:
        r: dictionary containing user_email, image_name, image_string, and
           process_types keys

    Raises:
         AttributeError: when r does not contain required keys
         TypeError: when user_email is not a valid email,
                    when process_type is not a specified processing type,
                    when image_name is not a string

    """
    if all(k in r for k in ("user_email", "image_name", "process_type")):
        if "@" not in r["user_email"]:
            raise TypeError("user_email must be a valid email.")
        elif type(r["image_name"]) is not str:
            raise TypeError("image_name must be a string.")
        elif r["process_type"] != "HistogramEqualization"\
                and r["process_type"] != "ContrastStretching"\
                and r["process_type"] != "LogCompression" \
                and r["process_type"] != "ReverseVideo":
            raise TypeError("process_type must be one of the 4 specified.")
    else:
        raise AttributeError("Post must be dict with user_email, image_name, "
                             "and process_types keys.")


def process_image(image_string, process_type):
    """ Processes image string according to one of 4 processing types

    Args:
        image_string: encoded base64 string of image to be processed
        process_type: one of 4 supported processing types to be performed

    Returns:
        processed_image: array of processed image data
        process_time: seconds taken for processing to be completed

    """
    if process_type == "HistogramEqualization":
        processed_image, process_time = hist_equalization(image_string)
    elif process_type == "ContrastStretching":
        processed_image, process_time = cont_stretching(image_string)
    elif process_type == "LogCompression":
        processed_image, process_time = log_compression(image_string)
    elif process_type == "ReverseVideo":
        processed_image, process_time = reverse_video(image_string)
    else:
        processed_image = image_string
        process_time = 0
    return processed_image, process_time


@app.route("/image/processed/upload", methods=["POST"])
def image_processed_upload():
    """ POSTs images processed by specified processing type to database

    Posts processed image as a dictionary containing the encoded base64 string
    as well as image processing time, image processing type, and updated user
    metrics to the database under the user's email

    Returns:
        200 status after the posting has occurred

    """
    r = request.get_json()
    validate_image_processed_upload(r)
    image_name = r["image_name"]
    image_no_location = image_name.split('/')[-1]
    image_no_format = image_no_location.split('.')[0]
    process_type = r["process_type"]
    image = ImageDB.objects.raw({"_id": r["user_email"]}).first()
    image_string = image_encoder(image_name)

    processed_image, time_to_process = process_image(image_string,
                                                     process_type)
    processed_image_b64bytes = base64.b64encode(processed_image)
    processed_image = processed_image_b64bytes.decode("UTF-8")
    time_to_process = str(time_to_process)
    process_time = datetime.now()
    process_info = {image_no_format: processed_image,
                    "process_type": process_type,
                    "process_time": process_time}
    image.processed_info.append(process_info)
    image.user_metrics[process_type] += 1
    image.user_metrics["Images Processed"] += 1
    image.user_metrics["Time to Complete Last Process"] = time_to_process
    image.save()
    return "Uploaded", 200


@app.route("/image/processed/<user_email>/<image_name>/<process_type>",
           methods=["GET"])
def get_processed_image(user_email, image_name, process_type):
    """ Retrieves specified processed image's info for user

    Args:
        user_email: email of user that has the desired processed image
        image_name: name of image that was processed
        process_type: type of processing performed on the image

    Returns:
        processed_image: JSONified dict containing the image name as the
                         key for a string of the processed image array,
                         the image process_type, and image process_time

    """
    processed_image = {}
    image = ImageDB.objects.raw({"_id": user_email}).first()
    processed_info = image.processed_info
    for dicts in processed_info:
        images = dicts.keys()
        processing = dicts["process_type"]
        if (image_name in images) and (processing == process_type):
            processed_image = dicts
    return jsonify(processed_image)


@app.route("/image/metrics/<user_email>", methods=["GET"])
def get_user_metrics(user_email):
    """ Retrieves user_metrics dictionary for a specified user

    Args:
        user_email: email id for the image processing user

    Returns:
         user_metrics: dict containing information about the number of images
         uploaded, images processed and their types, and time of last
         processing for the user

    """
    image = ImageDB.objects.raw({"_id": user_email}).first()
    user_metrics = image.user_metrics
    return jsonify(user_metrics)


def hist_equalization(encoded_img):
    """ Takes a b64-encoded image and returns new image array after
    histogram equalization

    Args:
        encoded_img: base64 string encoding list

    Returns:
        eq_img: an array for the new image that underwent histogram
        equalization
        process_time: seconds taken to complete the processing

    """
    start_time = time.monotonic()
    img_buf = decode(encoded_img)
    img = skimage.io.imread(img_buf)
    gs_img = skimage.color.rgb2gray(img)
    eq_img = skimage.exposure.equalize_hist(gs_img)
    end_time = time.monotonic()
    process_time = timedelta(seconds=end_time - start_time)
    # viewer = ImageViewer(eq_img)
    # viewer.show()
    return eq_img, process_time


def cont_stretching(encoded_img):
    """ Takes a b64-encoded image and returns new image array after
    contrast stretching

    Args:
        encoded_img: base64 string encoding list

    Returns:
        constr_img: an array for the new image that underwent contrast
        stretching
        process_time: seconds taken to complete image processing

    """
    start_time = time.monotonic()
    img_buf = decode(encoded_img)
    img = skimage.io.imread(img_buf)
    contstr_img = exposure.rescale_intensity(img, out_range=(150, 200))
    end_time = time.monotonic()
    process_time = timedelta(seconds=end_time - start_time)
    # lowers the contrast
    return contstr_img, process_time


def log_compression(encoded_img):
    """ Takes a b64-encoded image and returns new image array after
    log compression

    Args:
        encoded_img: base64 string encoding list

    Returns:
        constr_img: an array for the new image that underwent contrast
        stretching
        process_time: seconds taken to complete image_processing

    """
    start_time = time.monotonic()
    img_buf = decode(encoded_img)
    img = skimage.io.imread(img_buf)
    logcomp_img = skimage.exposure.adjust_log(img, gain=0.5)
    end_time = time.monotonic()
    process_time = timedelta(seconds=end_time - start_time)
    return logcomp_img, process_time


def reverse_video(encoded_img):
    """ Takes a b64-encoded image and returns new image array after
      inverting image

      Args:
          encoded_img: base64 string encoding list

      Returns:
          inv_img: an array for the new image that underwent inversion
          process_time: seconds taken to complete image processing

      """
    start_time = time.monotonic()
    img_buf = decode(encoded_img)
    img = skimage.io.imread(img_buf)
    inv_img = skimage.util.invert(img)
    end_time = time.monotonic()
    process_time = timedelta(seconds=end_time - start_time)
    return inv_img, process_time


def make_hist(img_b64string):
    """ Takes a b64-encoded image and returns a b64 string of the image's
        histogram

      Args:
          img_b64string: base64 string encoded image

      Returns:
          hist_b64string: base64 string encoded image of histogram

      """

    img_buf = decode(img_b64string)
    img_array = skimage.io.imread(img_buf)
    vals = img_array.mean(axis=2).flatten()
    fig = plt.figure()
    b, bins, patches = plt.hist(vals, 255)
    lim1, lim2 = plt.xlim([0, 255])
    title = plt.title("Histogram")
    # plt.show()
    fig.savefig("hist.png", bbox_inches='tight', pad_inches=0)
    open_hist = open("hist.png", "rb")
    hist_array = skimage.io.imread(open_hist)
    hist_b64bytes = base64.b64encode(hist_array)
    hist_b64string = hist_b64bytes.decode("UTF-8")

    # print(hist_array)
    # viewer = ImageViewer(hist_array)
    # viewer.show()

    # my_stringIObytes = StringIO.StringIO()
    # plt.savefig(my_stringIObytes, format='png')
    # my_stringIObytes.seek(0)
    # my_base64_pngData = base64.b64encode(my_stringIObytes.read())
    # fig.add_subplot(111)
    # fig.canvas.draw()
    # width, height = fig.get_size_inches()*fig.get_dpi()
    # mplimage = np.fromstring(fig.canvas.tostring_rgb(), /
    #       dtype='uint8').reshape(height, width, 3)
    # hist_array = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
    # hist_array = hist_array.reshape(fig.canvas.get_width_height()/
    #       [::-1] + (3,))
    # plt.hist(img_array.ravel(), bin=256, histtype='step', color='black')
    # plt.show()
    # hist_array = np.array(fig.canvas.renderer._renderer)
    return hist_b64string


if __name__ == "__main__":
    app.run(host="127.0.0.1")
    # app.run(host="0.0.0.0")
