import requests

api_host = "http://127.0.0.1:5000"
# api_host = "http://vcm-7311.vm.duke.edu:5000"


def post_create_user(user_email):
    """ Makes new patient POST request to /image/user

    Args:
        user_email: email for new image processor user

    Returns:
         r: the status of the post request (200 if completed)

    """
    data = {
        "user_email": user_email
    }
    r = requests.post(api_host + '/image/user', json=data)
    return r


def get_returning_user(user_email):
    """ Makes GET request to image/user/<user_email>

    Args:
        user_email: string containing returning user's email

    Returns:
        email: json containing user_email if the user exists in the db
               and an error_message if the user is not in the db

    """
    website = api_host + '/image/user/' + user_email
    r = requests.get(website)
    email = r.json()
    return email


def post_uploaded_images(user_email, image_dict):
    """ Makes POST request to /image/upload/<user_email>

    Args:
        user_email: user email ID
        image_dict: dict with image names as keys and base64
                    strings as the corresponding values

    Returns:
         r: the status of the post request (200 if completed)

    """
    r = requests.post(api_host + '/image/upload/' + user_email,
                      json=image_dict)
    return r


def get_uploaded_images(user_email):
    """ Makes GET request to /image/upload/<user_email>

    Args:
        user_email: user email ID

    Returns:
         uploads: json containing image names as keys for the encoded
                  uploaded image b64 string

    """
    website = api_host + '/image/upload/' + user_email
    r = requests.get(website)
    uploads = r.json()
    return uploads


def get_upload_time(user_email):
    """ Makes GET request to /image/upload_time/<user_email>

    Args:
        user_email: user email ID

    Returns:
        upload_times: json containing image names as keys for the upload
                      times for those respective images

    """
    website = api_host + '/image/upload_time/' + user_email
    r = requests.get(website)
    upload_times = r.json()
    return upload_times


def get_upload_sizes(user_email):
    """ Makes GET request to /image/upload_size/<user_email>

    Args:
        user_email: user email ID

    Returns:
        upload_sizes: json containing image names as keys for the image
                      sizes for those respective images

    """
    website = api_host + '/image/upload_size/' + user_email
    r = requests.get(website)
    upload_sizes = r.json()
    return upload_sizes


def post_processed_image(user_email, image_name, process_type):
    """ Makes POST request to /image/processed/upload

    Args:
        user_email: user email ID
        image_name: name of image to be processed
        process_type: one of 4 specified processing types to perform on image

    Returns:
         r: status of the post (200 if completed)

    """
    process = {"user_email": user_email,
               "image_name": image_name,
               "process_type": process_type}
    r = requests.post(api_host + '/image/processed/upload', json=process)
    return r


def get_processed_image(user_email, image_name, process_type):
    """ Makes GET request to /image/processed/<user_email>/<image_name>/
        <process_type>

    Args:
        user_email: user email ID
        image_name: string, name of processed image to be retrieved
        process_type: string containing type of processing performed

    Returns:
        processed_image: dict containing image name key with a value of
                         a string-type array of the processed image data,
                         process_type key, and process_time key

    """
    website = api_host + '/image/processed/' + user_email + '/' + image_name\
        + '/' + process_type
    r = requests.get(website)
    processed_image = r.json()
    return processed_image


def get_user_metrics(user_email):
    """ Makes GET request to /image/metrics/<user_email>

    Args:
        user_email: user email ID

    Returns:
        user_metrics: dictionary containing relevant usage metrics for user

    """
    website = api_host + '/image/metrics/' + user_email
    r = requests.get(website)
    user_metrics = r.json()
    return user_metrics


if __name__ == "__main__":
    post_create_user("test3@duke.edu")
    upload_times = get_upload_time("test3@duke.edu")
    print(upload_times)
    upload_sizes = get_upload_sizes("test3@duke.edu")
    print(upload_sizes)
    post_processed_image("test3@duke.edu", "capy.jpg", "LogCompression")
    processed_image = get_processed_image("test3@duke.edu",
                                          "capy.jpg",
                                          "LogCompression")
    print(processed_image)
