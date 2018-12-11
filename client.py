import requests

# api_host = "http://127.0.0.1:5000"
api_host = "http://vcm-7311.vm.duke.edu:5000"


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


def post_uploaded_images(user_email, uploaded_images):
    """ Makes POST request to /image/upload

    Args:
        user_email: user email ID
        uploaded_images: list of image files desired to be uploaded (must
                         be of the format .jpg, .tiff, .png, or .zip)

    Returns:
         r: the status of the post request (200 if completed)

    """
    upload = {"user_email": user_email,
              "uploaded_images": uploaded_images}
    r = requests.post(api_host + '/image/upload', json=upload)
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


if __name__ == "__main__":
    post1 = post_create_user("sarah.putney@duke.edu")
    email = get_returning_user("sarah.putney@duke.edu")
    post2 = post_uploaded_images("sarah.putney@duke.edu",
                                 ["test_images/capy.jpg"])
    uploads = get_uploaded_images("sarah.putney@duke.edu")
    post3 = post_processed_image("sarah.putney@duke.edu",
                                 "test_images/capy.jpg",
                                 "Histogram Equalization")
    print(post1)
    print(email)
    print(post2)
    print(uploads)
    print(post3)
