import requests

api_host = "http://127.0.0.1:5000"


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


if __name__ == "__main__":
    post1 = post_create_user("sarah.putney@duke.edu")
    email = get_returning_user("sarah.putney@duke.edu")
    print(post1)
    print(email)
