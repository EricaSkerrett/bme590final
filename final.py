from flask import Flask, jsonify, request
from pymodm import connect, MongoModel, fields
from datetime import datetime
import base64
import io
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
import zipfile
import skimage
from skimage import exposure
from skimage.viewer import ImageViewer
import imghdr

connect("mongodb://sputney13:sputney13@ds161901.mlab.com:61901/bme590final")
app = Flask(__name__)


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

    Returns:
        AttributeError: when post does not contain proper key
        TypeError: when user_email key is not an email (does not have an @)

    """
    if "user_email" in r:
        if "@" not in r["user_email"]:
            raise TypeError("user_email must be an email string.")
    else:
        raise AttributeError("Post must be dict with user_email key.")


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
                    "Histogram Equalization": 0,
                    "Contrast Stretching": 0,
                    "Log Compression": 0,
                    "Reverse Video": 0,
                    "Time to Complete Last Process": 0}
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
            break
        else:
            email = {"user_email": "Not in database",
                     "error_message": 'User not in database. Please enter'
                                      ' an email in the database or create'
                                      ' a new user.'}
    return jsonify(email)


def validate_image_upload(r):
    """ Validates user inputs for posts to /image/upload

        Args:
            r: dictionary containing user_email and uploaded_images keys

        Returns:
            AttributeError: when r does not contain the 2 required keys
            TypeError: when user_email is not an email/when keys in
                       uploaded_images does not end in .jpg, .tiff,
                       .png, or .zip

        """
    if all(k in r for k in ("user_email", "uploaded_images")):
        if "@" not in r["user_email"]:
            raise TypeError("user_email must be a valid email.")
        elif r["uploaded_images"] is not None:
            for image in r["uploaded_images"]:
                if ".jpg" or ".png" or ".tiff" or ".zip" \
                 not in image:
                    raise TypeError("Uploaded image must be JPG,"
                                    " PNG, or TIFF.")
    else:
        raise AttributeError("Post must be dict with user_email and"
                             "uploaded_images keys.")


def image_encoder(file_list):
    """ Encodes user-uploaded images in a base64 string for saving to db

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
        with open(image, "rb") as image_file:
            base64_string = base64.b64encode(image_file.read())
            image_dict.update({image: base64_string})
    return image_dict


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


@app.route("/image/upload", methods=["POST"])
def image_upload():
    """ POSTs user-uploaded image to database

    Posts user-uploaded image as an encoded base64 string as well as image
    upload time, format, and size to database under the user's email.
    Updates metrics for user based off number of images uploaded.

    Returns:
        200 status after the posting has occurred

    """
    r = request.get_json()
    validate_image_upload(r)
    image_dict = image_encoder(r["uploaded_images"])
    image_size = get_size(image_dict)
    image_format = get_format(image_dict)
    upload_time = datetime.now()

    image = ImageDB.objects.raw({"_id": r["user_email"]}).first()
    image.uploaded_images.append(image_dict)
    image.upload_times.append(upload_time)
    image.image_size.append(image_size)
    image.image_formats.append(image_format)
    image.user_metrics["Images Uploaded"] += len(image_dict)
    image.save()
    return "Uploaded", 200


def get_size(image_dict):
    """ Reads images from dictionary to find image size

    Args:
        image_dict: dictionary containing base64 values and image name keys

    Returns:
        size_dict: dictionary containing size values and image name keys
        Sizes are in tuples (H, W, D)

    """
    image_name = image_dict.keys()
    for image in image_name:
        img_buf = decode(image_dict[image])
        i = skimage.io.imread(img_buf)
        size = i.shape
        image_dict[image] = size  # replaces base64 with size
    size_dict = image_dict
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
    for image in image_name:
        image_buf = decode(image_dict[image])
        im_format = imghdr.what(image_buf)
        image_dict[image] = im_format
    format_dict = image_dict
    return format_dict


def validate_image_processed_upload(r):
    """ Validates user inputs for posts to to /image/processed/upload

    Args:
        r: dictionary containing user_email, image_name, processed_images, and
           process_types keys

    Returns:
         AttributeError: when r does not contain required keys
         TypeError: when user_email is not a valid email, when
                    processed_image is not a string, when process_type
                    is not a specified processing type, when image_name is
                    not a string

    """
    if all(k in r for k in ("user_email", "image_name", "processed_image",
                            "process_type")):
        if "@" not in r["user_email"]:
            raise TypeError("user_email must be a valid email.")
        elif type(r["image_name"]) is not str:
            raise TypeError("image_name must be a string.")
        elif type(r["processed_image"]) is not str:
            raise TypeError("processed_image must be a base64 type string.")
        elif r["process_type"] is not "Histogram Equalization" or "\
        Contrast Stretching" or "Log Compression" or "Reverse Video":
            raise TypeError("process_type must be one of the 4 specified.")
    else:
        raise AttributeError("Post must be dict with user_email, image_name "
                             "processed_images, and process_types keys.")


@app.route("/image/processed/upload", methods=["POST"])
def image_processed_upload():
    """ POSTs processed images to database

    Posts processed image as a dictionary containing the encoded base64 string
    as well as image processing time, image processing type, and updated user
    metrics to the database under the user's email

    Returns:
        200 status after the posting has occurred

    """
    r = request.get_json()
    validate_image_processed_upload(r)
    image_name = r["image_name"]
    process_type = r["process_type"]
    process_time = datetime.now()
    process_info = {image_name: r["processed_image"],
                    "process_type": process_type,
                    "process_time": process_time}

    image = ImageDB.objects.raw({"_id": r["user_email"]}).first()
    image.processed_info.append(process_info)
    image.user_metrics[r["process_type"]] += 1
    image.user_metrics["Images Processed"] += 1
    image.save()
    return "Uploaded", 200


@app.route("/image/upload/<user_email>", methods=["GET"])
def get_uploaded_images(user_email):
    """ Retrieves all uploaded images for specified user

    Args:
        user_email: email of user that has the desired uploaded images

    Returns:
        uploaded_images: dict containing uploaded image keys and strings

    """
    image = ImageDB.objects.raw({"_id": user_email}).first()
    uploaded_images = image.uploaded_images
    return uploaded_images


def hist_equalization(encoded_img):
    """ Takes a b64-encoded image and returns new image array after
    histogram equalization

    Args:
        encoded_image: base64 string encoding list

    Returns:
        eq_img: an array for the new image that underwent histogram
        equalization

    """
    img_buf = decode(encoded_img)
    img = skimage.io.imread(img_buf)
    gs_img = skimage.color.rgb2gray(img)
    eq_img = skimage.exposure.equalize_hist(gs_img)
    viewer = ImageViewer(eq_img)
    viewer.show()
    return eq_img


def make_hist(img_array):
    plt.hist(img_array.ravel(), bin=256, histtype='step', color='black')
    plt.show()


if __name__ == "__main__":
    app.run(host="127.0.0.1")
