from flask import Flask, jsonify, request
from pymodm import connect, MongoModel, fields
from datetime import datetime
import base64
import io
import matplotlib.image as mpimg
from matplotlib import pyplot as plt

connect("mongodb://sputney13:sputney13@ds161901.mlab.com:61901/bme590final")
app = Flask(__name__)
app.run(host="127.0.0.1")


class Image(MongoModel):
    user_email = fields.EmailField(primary_key=True)
    uploaded_images = fields.ListField(field=fields.CharField())
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
    """ POSTS a new image processor user (identified by email)to database

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


def image_encoder(image_name):
    """ Encodes user-uploaded image in a base64 string for saving to db

    Args:
        image_name: string containing filename of image to be encoded

    Returns:
        base64_string: image encoded in a base64 string

    """
    # note right now this only works for a single file upload at a time
    # for .zip: write a function that unzips, use an if statement to call
    #           on that function if needed
    with open(image_name, "rb") as image_file:
        base64_string = base64.b64encode(image_file.read())
    return base64_string


@app.route("/image/upload", methods=["POST"])
def image_upload():
    """ POSTs user-uploaded image to database

    Posts user-uploaded image as an encoded base64 string as well as image
    upload time and image size to database under the user's email

    Returns:
        200 status after the posting has occurred

    """
    r = request.get_json()
    validate_image_upload(r)
    base64string = image_encoder(r["uploaded_images"])
    # image_size = call on a function to find image size here
    upload_time = datetime.now()
    image = Image.objects.raw({"_id": r["user_email"]}).first()
    image.uploaded_images.append(base64string)
    image.upload_times.append(upload_time)
    # image.image_size.append(image_size)
    image.save()
    return "Uploaded", 200


def validate_image_processed_upload(r):
    """ Validates user inputs for posts to to /image/processed/upload

    Args:
        r: dictionary containing user_email and processed_images keys

    Returns:
         AttributeError: when r does not contain required keys
         TypeError: when user_email is not a valid email, when
                    processed_images is not a string

    """
    if all(k in r for k in ("user_email", "processed_images")):
        if "@" not in r["user_email"]:
            raise TypeError("user_email must be a valid email.")
        elif type(r["processed_images"]) is not str:
            raise TypeError("processed_images must be a base64 type string.")
    else:
        raise AttributeError("Post must be dict with user_email and"
                             "processed_images keys.")


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
    # process_type = use information from GET request to determine
    process_time = datetime.now()
    image = Image.objects.raw({"_id": r["user_email"]}).first()
    image.processed_images.append(r["processed_images"])
    image.process_times.append(process_time)
    # image.process_types.append(process_type)
    # update user_metrics dict (find process type key and add 1)
    image.save()
    return "Uploaded", 200
