from flask import current_app as app
import numpy as np
import cv2 as cv
import os
import uuid
from scipy.spatial import distance as dist

from collections import defaultdict
from itertools import combinations

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


def object_detect(path, ext, filter_only=[], filter_without=[], crop_objects=False):
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
    for_crop = img.copy()
    (H, W) = img.shape[:2]
    results = []
    # classes, scores,
    classes, scores, boxes = model.detect(img, CONF_THRESHHOLD, NMS_THRESHHOLD)
    # colors = np.random.uniform(0, 255, size=(len(classes), 3))
    colors = np.random.uniform(125, 255, size=(len(classes), 3))

    i = 0
    # d = {person: 1, cat: 2}
    coords = []
    centroids = []
    instance_names = []
    cropped_images = []

    # create directory for the objects output 
    random_name = str(uuid.uuid4().hex) 
    output_path = os.path.join(app.config["OUTPUT_PATH"], random_name)
    os.mkdir(output_path)
    class_counts = defaultdict(lambda: 0)
    for (class_id, score, box) in zip(classes, scores, boxes):
        if class_id[0] not in class_ids:
            continue

        color = colors[i]
        # d[classname] += 1
        class_name = class_names[class_id[0]]
        class_counts[class_name] += 1
        instance_name = f"{class_name}{class_counts[class_name]}"
        instance_names.append(instance_name)
        # person: 98%
        # ! rectangle area
        (x, y) = (box[0], box[1])
        (w, h) = (box[2], box[3])
        top_left, top_right = ((x, y), (x+w, y))
        bot_left, bot_right = ((x, y+h), (x+w, y+h))
        centroid = (x + (w//2), y + (h//2))
        print("top", top_left, top_right)
        print("bot", bot_left, bot_right)
        print("centroid", centroid)
        # centroids.append((centroid))
        coords.append((top_left, top_right, bot_left, bot_right))
        centroids.append(centroid)

        cv.rectangle(img, box, color, 3) # for box

        # cropping image
        
        cropped_path = os.path.join(output_path, instance_name + f".{ext}")
        cropped = for_crop[y:y+h, x:x+w]
        cv.imwrite(cropped_path, cropped)

        # res = cv.putText(img, label, (box[0], box[1]-10), cv.FONT_HERSHEY_COMPLEX, 0.5, color, 2)

        # set text
        # label = f'{class_name}: {round(float(score*100), 2)}'
        label = f'{instance_name}: {round(float(score*100), 2)}'
        print(class_name, f"x:{x}, y:{y}, w:{w}, h{h}")
        img = cv.putText(img, label, (box[0]+5, box[1]+20), cv.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 2)
        # img = cv.putText(img, label, centroid, cv.FONT_HERSHEY_COMPLEX, 0.5, (0,0,0), 2)
        img = cv.circle(img, centroid, 5, color, 3)
        i += 1

    distances = []
    if i > 1:
        for centroid_a, centroid_b in list(combinations(centroids, 2)):
            print("centroid a", centroid_a)
            print("centroid b", centroid_b)

        # distance table 
        distances = list(np.around( dist.cdist(centroids, centroids, metric="euclidean"), decimals=2 ))
        print(distances)

    class_counts = dict(class_counts)
    print(f"class counts: {class_counts}")
    print(f"total: {i}")

    filename = f"output.{ext}"
    path = os.path.join(output_path, filename)
    cv.imwrite(path, img)

    # return dictionary_count, total, path, distance
    return random_name, filename, i, class_counts, distances, instance_names
