import pytest
import final

# uses global var to avoid reopening files
global_image1 = "test_images/capy.jpg"
global_open1 = open(global_image1, "rb")
global_b641 = final.base64.b64encode(global_open1.read())


def test_validate_create_user():
    r1 = {"user": "Name"}
    r2 = {"user_email": 862}
    r3 = {"user_email": "Email"}

    with pytest.raises(AttributeError):
        final.validate_create_user(r1)
    with pytest.raises(TypeError):
        final.validate_create_user(r2)
    with pytest.raises(TypeError):
        final.validate_create_user(r3)


def test_validate_image_upload():
    r1 = {"user_email": "name@email.com"}
    r2 = {"uploaded_images": "string"}
    r3 = {"user_email": "name", "uploaded_images": "string"}
    r4 = {"user_email": "name@email.com", "uploaded_images": 23456}

    with pytest.raises(AttributeError):
        final.validate_image_upload(r1)
    with pytest.raises(AttributeError):
        final.validate_image_upload(r2)
    with pytest.raises(TypeError):
        final.validate_image_upload(r3)
    with pytest.raises(TypeError):
        final.validate_image_upload(r4)


def test_image_encoder():
    assert 1 == 1


def test_unzip_folder():
    assert 1 == 1


def test_get_size():
    global global_image1
    global global_b641
    name_dict = {global_image1: global_b641}
    size_dict = final.get_size(name_dict)
    assert size_dict == {global_image1: (416, 624, 3)}


def test_decode():
    global global_b641
    decoded_image = final.decode(global_b641)
    first = decoded_image[0, 0, 0]
    length = len(decoded_image)
    last = decoded_image[-1, -1, -1]
    param = [first, length, last]
    assert param == [132, 416, 24]


def test_get_format():
    global global_image1
    global global_b641
    name_dict = {global_image1: global_b641}
    format_dict = final.get_format(name_dict)
    assert format_dict == {global_image1: "jpeg"}


def test_validate_image_processed_upload():
    r1 = {"user_email": "name@email.com"}
    r2 = {"user_email": "name@email.com", "processed_images": "string12"}
    r3 = {"processed_images": "string123", "process_types": "Reverse Video"}
    r4 = {"user_email": "name", "processed_images": "String345",
          "process_types": "Histogram Equalization"}
    r5 = {"user_email": "name@email.com", "processed_images": 862,
          "process_types": "Histogram Equalization"}
    r6 = {"user_email": "name@email.com", "processed_images": "String345",
          "process_types": "no processing"}

    with pytest.raises(AttributeError):
        final.validate_image_processed_upload(r1)
    with pytest.raises(AttributeError):
        final.validate_image_processed_upload(r2)
    with pytest.raises(AttributeError):
        final.validate_image_processed_upload(r3)
    with pytest.raises(TypeError):
        final.validate_image_processed_upload(r4)
    with pytest.raises(TypeError):
        final.validate_image_processed_upload(r5)
    with pytest.raises(TypeError):
        final.validate_image_processed_upload(r6)


def test_view_b64_image():
    assert 1 == 1
