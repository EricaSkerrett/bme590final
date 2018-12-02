from flask import Flask, jsonify, request
from pymodm import connect, MongoModel, fields
from datetime import datetime
import base64
import io
import matplotlib.image as mpimg
from matplotlib import pyplot as plt
import zipfile

connect("mongodb://sputney13:sputney13@ds161901.mlab.com:61901/bme590final")
app = Flask(__name__)


class Image(MongoModel):
    user_email = fields.EmailField(primary_key=True)
    uploaded_images = fields.ListField(field=fields.CharField())
    image_formats = fields.ListField(field=fields.CharField())
    upload_times = fields.ListField(field=fields.DateTimeField())
    image_size = fields.ListField()
    processed_images = fields.ListField(field=fields.CharField())
    process_types = fields.ListField(field=fields.CharField())
    process_times = fields.ListField(field=fields.DateTimeField())
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


@app.route("/image/user", methods=["POST"])
def create_user():
    """ POSTS a new image processor user (identified by email) to database

    Returns:
        200 status after posting has occurred

    """
    r = request.get_json()
    validate_create_user(r)
    entry = Image(r["user_email"])
    entry.save()
    return "Created", 200


def validate_image_upload(r):
    """ Validates user inputs for posts to /image/upload

        Args:
            r: dictionary containing user_email and uploaded_images keys

        Returns:
            AttributeError: when r does not contain the 2 required keys
            TypeError: when user_email is not an email/when uploaded_images
                       does not end in .jpg, .tiff, .png, or .zip

        """
    if all(k in r for k in ("user_email", "uploaded_images")):
        if "@" not in r["user_email"]:
            raise TypeError("user_email must be a valid email.")
        elif ".jpg" or ".png" or ".tiff" or ".zip" \
                not in r["uploaded_images"]:
            raise TypeError("Uploaded image must be JPG, PNG, or TIFF.")
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
    # we may need to pair each base64 string to the name of the original file
    # we may also want to split this into 2 functions depending on unit testing
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
    upload time, format, and size to database under the user's email

    Returns:
        200 status after the posting has occurred

    """
    r = request.get_json()
    validate_image_upload(r)
    image_dict = image_encoder(r["uploaded_images"])
    # image_size = call on a function to find image size
    # image_format = call on a function to extract image format
    upload_time = datetime.now()
    image = Image.objects.raw({"_id": r["user_email"]}).first()
    image.uploaded_images.append(image_dict)
    image.upload_times.append(upload_time)
    # image.image_size.append(image_size)
    # image.image_formats.append(image_format)
    image.save()
    return "Uploaded", 200


def validate_image_processed_upload(r):
    """ Validates user inputs for posts to to /image/processed/upload

    Args:
        r: dictionary containing user_email, processed_images, and
           process_types keys

    Returns:
         AttributeError: when r does not contain required keys
         TypeError: when user_email is not a valid email, when
                    processed_images is not a string, when process_types
                    is not a specified processing type

    """
    if all(k in r for k in ("user_email", "processed_images",
                            "process_types")):
        if "@" not in r["user_email"]:
            raise TypeError("user_email must be a valid email.")
        elif type(r["processed_images"]) is not str:
            raise TypeError("processed_images must be a base64 type string.")
        elif r["process_types"] is not "Histogram Equalization" or "\
        Contrast Stretching" or "Log Compression" or "Reverse Video":
            raise TypeError("process_types must be one of the 4 specified.")
    else:
        raise AttributeError("Post must be dict with user_email, "
                             "processed_images, and process_types keys.")


@app.route("/image/processed/upload", methods=["POST"])
def image_processed_upload():
    """ POSTs processed images to database

    Posts processed image (processed by GET request) as encoded base64 string
    as well as image processing time, image processing type, and updated user
    metrics to the database under the user's email

    Returns:
        200 status after the posting has occurred

    """
    r = request.get_json()
    validate_image_processed_upload(r)
    process_type = r["process_types"]
    process_time = datetime.now()
    image = Image.objects.raw({"_id": r["user_email"]}).first()
    image.processed_images.append(r["processed_images"])
    image.process_times.append(process_time)
    image.process_types.append(process_type)
    # update user_metrics dict (find process type key and add 1)
    image.save()
    return "Uploaded", 200


def view_b64_image(image_format, base64_string):
    """ Decodes and shows base64 strings as images

    Args:
        image_format: type of file image was before encoding
        base64_string: encoded string of base64 bytes

    Returns:
        Plot of decoded image

    """
    image_bytes = base64.b64decode(base64_string)
    image_buf = io.BytesIO(image_bytes)
    i = mpimg.imread(image_buf, format=image_format)
    plt.imshow(i, interpolation='nearest')
    plt.show()


@app.route("/image/upload/<user_email>", methods=["GET"])
def get_uploaded_images(user_email):
    """ Retrieves and shows all uploaded images for specified user

    Args:
        user_email: email of user that has the desired uploaded images

    Returns:
        Plots of the images the specified user has uploaded

    """
    image = Image.objects.raw({"_id": user_email}).first()
    uploaded_images = image.uploaded_images
    image_format = image.image_formats
    # note that this doesn't allow for viewing multiple images:
    # should allow for iteration through list of uploaded images
    # and image_formats so that all uploaded images can be viewed
    view_b64_image(image_format, uploaded_images)


if __name__ == "__main__":
    app.run(host="127.0.0.1")
