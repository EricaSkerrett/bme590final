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


@pytest.mark.parametrize("a, expected", [
    ("test_user@gmail.com", {"User": "test_user@gmail.com",
                             "Images Uploaded": 0,
                             "Images Processed": 0,
                             "Histogram Equalization": 0,
                             "Contrast Stretching": 0,
                             "Log Compression": 0,
                             "Reverse Video": 0,
                             "Time to Complete Last Process": 0}),
    ("email_test2@duke.edu", {"User": "email_test2@duke.edu",
                              "Images Uploaded": 0,
                              "Images Processed": 0,
                              "Histogram Equalization": 0,
                              "Contrast Stretching": 0,
                              "Log Compression": 0,
                              "Reverse Video": 0,
                              "Time to Complete Last Process": 0})
])
def test_init_user_metrics(a, expected):
    assert final.init_user_metrics(a) == expected


def test_validate_image_upload():
    r1 = {"user_email": "name@email.com"}
    r2 = {"uploaded_images": ["image.jpg"]}
    r3 = {"user_email": "name", "uploaded_images": ["image.jpg"]}
    r4 = {"user_email": "name@email.com", "uploaded_images": ["image",
                                                              "image.png"]}

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
    image_buf = final.decode(global_b641)
    decoded_image = final.skimage.io.imread(image_buf)
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
    r2 = {"user_email": "name@email.com", "image_string": "string12"}
    r3 = {"image_string": "string123", "process_type": "Reverse Video"}

    r4 = {"user_email": "name", "image_name": "name.jpg", "image_string":
          "String345", "process_type": "Histogram Equalization"}
    r5 = {"user_email": "name@email.com", "image_name": 123,
          "image_string": "string123", "process_type":
          "Histogram Equalization"}
    r6 = {"user_email": "name@email.com", "image_name": "name.jpg",
          "image_string": 123, "process_type": "Histogram Equalization"}
    r7 = {"user_email": "name@email.com", "image_name": "name.jpg",
          "image_string": "String345", "process_type": "no processing"}

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
    with pytest.raises(TypeError):
        final.validate_image_processed_upload(r7)


def test_process_image():
    global global_b641
    histprocess, histtime = final.process_image(global_b641,
                                                "Histogram Equalization")
    contprocess, conttime = final.process_image(global_b641,
                                                "Contrast Stretching")
    logprocess, logtime = final.process_image(global_b641,
                                              "Log Compression")
    reverseprocess, revtime = final.process_image(global_b641,
                                                  "Reverse Video")

    oghist, oghisttime = final.hist_equalization(global_b641)
    ogcont, ogconttime = final.cont_stretching(global_b641)
    oglog, oglogtime = final.log_compression(global_b641)
    ogreverse, ogrevtime = final.reverse_video(global_b641)

    assert histprocess.all() == oghist.all()
    assert contprocess.all() == ogcont.all()
    assert logprocess.all() == oglog.all()
    assert reverseprocess.all() == ogreverse.all()
    assert final.process_image("test.jpg", "no process") == ("test.jpg", 0)


def test_hist_equalization():
    global global_b641
    eq_img = final.hist_equalization(global_b641)[0]
    length = len(eq_img)
    last = eq_img[-1][-1]
    param = [length, last]
    assert param == [416, 0.010774177428094655]


def test_cont_stretching():
    global global_b641
    constr_img = final.cont_stretching(global_b641)[0]
    length = len(constr_img)
    last = constr_img[-1, -1, -1]
    param = [length, last]
    assert param == [416, 154]


def test_log_compression():
    global global_b641
    comp_img = final.log_compression(global_b641)[0]
    length = len(comp_img)
    last = comp_img[-1, -1, -1]
    param = [length, last]
    assert param == [416, 16]


def test_reverse_video():
    global global_b641
    inv_img = final.reverse_video(global_b641)[0]
    length = len(inv_img)
    last = inv_img[-1, -1, -1]
    param = [length, last]
    assert param == [416, 231]
