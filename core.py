from flask import current_app as app
from flask import send_file
import numpy as np
import cv2 as cv
import os
import uuid


def valid_ext(filename):
    ext = filename.rsplit(".", 1)[1]
    if ext.lower() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

def valid_size(size: int) -> bool:
    if size > app.config["ALLOWED_MAX_IMAGE_FILESIZE"]:
        return False
    return True

def object_detect(path, ext):
    # TODO file extension arg
    # TODO background for font
    conf_threshhold = 0.4
    nms_threshhold = 0.4

    class_names = []

    # read data
    with open('coco.names', 'r') as f:
        class_names = [cname.strip() for cname in f.readlines()]

    my_img = cv.imread(path)
    # my_img = cv.resize(my_img, (1280, 720))

    # ht, wt, _ = my_img.shape

    # ? 

    # net = cv.dnn.readNet('yolov4-p6.weights', 'yolov4-p6.cfg')
    net = cv.dnn.readNet('yolov4-tiny.weights', 'yolov4-tiny.cfg')
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
    net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)

    model = cv.dnn_DetectionModel(net)
    model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)

    # classes, scores,
    classes, scores, boxes = model.detect(my_img, conf_threshhold, nms_threshhold)
    # colors = np.random.uniform(0, 255, size=(len(classes), 3))
    colors = np.random.uniform(125, 255, size=(len(classes), 3))


    i = 0
    # d = {person: 1, cat: 2}
    for (class_id, score, box) in zip(classes, scores, boxes):
        color = colors[i]
        # d[classname] += 1
        label = f'{class_names[class_id[0]]}: {round(float(score*100), 2)}'
        # person: 98%
        cv.rectangle(my_img, box, color, 3) # for box
        # res = cv.putText(my_img, label, (box[0], box[1]-10), cv.FONT_HERSHEY_COMPLEX, 0.5, color, 2)
        res = cv.putText(my_img, label, (box[0]+5, box[1]+20), cv.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 2)
        i += 1

    filename = str(uuid.uuid4().hex) + "." + ext
    path = os.path.join(app.config["OUTPUT_PATH"], filename)
    cv.imwrite(path, res)

    # return dictionary_count, total, path, distance_dictionary
    return path
