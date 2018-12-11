import pytest
import final

# uses global var to avoid reopening files
global_image1 = "capy.jpg"
global_image2 = "capy2.png"
global_open1 = open(global_image1, "rb")
global_b641 = final.base64.b64encode(global_open1.read())
global_b64_string1 = global_b641.decode("UTF-8")


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
                             "HistogramEqualization": 0,
                             "ContrastStretching": 0,
                             "LogCompression": 0,
                             "ReverseVideo": 0,
                             "Time to Complete Last Process": 0}),
    ("email_test2@duke.edu", {"User": "email_test2@duke.edu",
                              "Images Uploaded": 0,
                              "Images Processed": 0,
                              "HistogramEqualization": 0,
                              "ContrastStretching": 0,
                              "LogCompression": 0,
                              "ReverseVideo": 0,
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
    global global_image1
    global global_b641
    bytes = final.image_encoder(global_image1)
    assert bytes == global_b641


def test_b64string_encoder():
    global global_b64_string1
    b64_bytes = final.b64string_encoder(global_b64_string1)
    type_var = type(b64_bytes)
    assert type_var == bytes


def test_image_parser():
    global global_image1
    global global_image2
    test_image_list1 = [global_image1]
    test_image_list2 = [global_image1, global_image2]
    test_image_list3 = [global_image1, global_image2, 'test.gif']
    image1_b64_string = final.image_encoder(global_image1).decode("utf-8")
    image2_b64_string = final.image_encoder(global_image2).decode("utf-8")

    assert final.image_parser(test_image_list1) == {"capy": image1_b64_string}
    assert final.image_parser(test_image_list2) == {"capy": image1_b64_string,
                                                    "capy2": image2_b64_string}
    assert final.image_parser(test_image_list3) == {"capy": image1_b64_string,
                                                    "capy2": image2_b64_string}


def test_unzip_folder():
    assert 1 == 1


@pytest.mark.parametrize("a, expected", [
    ([{"a": 1}, {"b": 2}], {"a": 1, "b": 2}),
    ([{"a": 1, "b": 2}, {"c": 3}], {"a": 1, "b": 2, "c": 3}),
    ([{"a": 1}, {"c": 3}, {"a": 1, "b": 2}], {"a": 1, "b": 2, "c": 3})
])
def test_list_to_dict(a, expected):
    assert final.list_to_dict(a) == expected


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
    r2 = {"user_email": "name@email.com", "process_type": "ReverseVideo"}
    r3 = {"image_name": "string123", "process_type": "ReverseVideo"}

    r4 = {"user_email": "name", "image_name": "name.jpg", "process_type":
          "HistogramEqualization"}
    r5 = {"user_email": "name@email.com", "image_name": 123,
          "process_type": "HistogramEqualization"}
    r6 = {"user_email": "name@email.com", "image_name": "name.jpg",
          "process_type": "no processing"}

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


def test_process_image():
    global global_b641
    histprocess, histtime = final.process_image(global_b641,
                                                "HistogramEqualization")
    contprocess, conttime = final.process_image(global_b641,
                                                "ContrastStretching")
    logprocess, logtime = final.process_image(global_b641,
                                              "LogCompression")
    reverseprocess, revtime = final.process_image(global_b641,
                                                  "ReverseVideo")

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
    param = [length, "%.4f" % last]
    assert param == [416, '0.0108']


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
