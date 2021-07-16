from flask import current_app as app
import numpy as np
import cv2 as cv
import os
import uuid

from collections import defaultdict

# ? ---
CONF_THRESHHOLD = 0.4
NMS_THRESHHOLD = 0.4
global coco_names

with open('coco.names', 'r') as f:
    coco_names = [cname.strip() for cname in f.readlines()]

net = cv.dnn.readNet('yolov4.weights', 'yolov4.cfg')
net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)

model = cv.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)


def object_detect(path, ext, filter_only=[], filter_without=[]):
    class_names = coco_names[:]
    class_ids = list(range(len(class_names)))
    
    # TODO background for font
    # filters
    if filter_only:
        print(f"filtering only: {filter_only}")
        class_ids = list(filter(lambda i: class_names[i] in filter_only, range(len(class_names))))
    if filter_without:
        print(f"filtering without: {filter_without}")
        class_ids = list(filter(lambda i: class_names[i] not in filter_without, range(len(class_names))))

    img = cv.imread(path)

    # classes, scores,
    classes, scores, boxes = model.detect(img, CONF_THRESHHOLD, NMS_THRESHHOLD)
    # colors = np.random.uniform(0, 255, size=(len(classes), 3))
    colors = np.random.uniform(125, 255, size=(len(classes), 3))

    i = 0
    # d = {person: 1, cat: 2}

    class_counts = defaultdict(lambda: 0)
    for (class_id, score, box) in zip(classes, scores, boxes):
        if class_id[0] not in class_ids:
            continue

        color = colors[i]
        # d[classname] += 1
        class_name = class_names[class_id[0]]
        class_counts[class_name] += 1

        label = f'{class_name}: {round(float(score*100), 2)}'
        # person: 98%


        cv.rectangle(img, box, color, 3) # for box
        # res = cv.putText(img, label, (box[0], box[1]-10), cv.FONT_HERSHEY_COMPLEX, 0.5, color, 2)

        # set text
        img = cv.putText(img, label, (box[0]+5, box[1]+20), cv.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 2)
        i += 1

    class_counts = dict(class_counts)
    print(f"class counts: {class_counts}")
    print(f"total: {i}")

    filename = str(uuid.uuid4().hex) + "." + ext
    path = os.path.join(app.config["OUTPUT_PATH"], filename)
    cv.imwrite(path, img)

    # return dictionary_count, total, path, distance_dictionary
    return path, i, class_counts
