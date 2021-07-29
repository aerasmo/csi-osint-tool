from flask import current_app as app
import numpy as np
import cv2 as cv
import os
import uuid
from scipy.spatial import distance as dist

from collections import defaultdict
from itertools import combinations

# csv
import csv

# ? ---
CONF_THRESHHOLD = 0.4
NMS_THRESHHOLD = 0.4
coco_names = []

# load coco names
with open('coco.names', 'r') as f:
    coco_names = [cname.strip() for cname in f.readlines()]

# model config
net = cv.dnn.readNet('yolov4.weights', 'yolov4.cfg')
net.setPreferableBackend(cv.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv.dnn.DNN_TARGET_CUDA)

model = cv.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)

font = cv.FONT_HERSHEY_COMPLEX

def writeCSV(path, data, filename):
    try: 
        os.mkdir(os.path.join(path, 'csv'))
    except FileExistsError:
        print("File already exists")

    with open(f'{path}/csv/{filename}.csv', 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        for row in data:
            csv_writer.writerow(row)
        # spamwriter.writerow(['Spam', 'Lovely Spam', 'Wonderful Spam'])

def draw_text(img, text,
          font=cv.FONT_HERSHEY_PLAIN,
          pos=(0, 0),
          font_scale=3,
          font_thickness=2,
          text_color=(255, 255, 255),
          text_color_bg=(0, 0, 0)
          ):

    x, y = pos
    text_size, _ = cv.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv.rectangle(img, pos, (x + text_w + 10, y + text_h + 5), text_color_bg, -1)
    img = cv.putText(img, text, (x, y + text_h + font_scale - 1), font, font_scale, text_color, font_thickness)
    return img


def max_image_res(w, h, max_res):
    max_ = max(w, h)
    coeff = max_res / max_
    w *= coeff
    h *= coeff
    return (round(w), round(h))


def object_detect(path, ext, filter_only=[], filter_without=[], show_distance=False, write_file=True):
    class_names = coco_names[:]
    class_ids = list(range(len(class_names)))
    
    # filters
    if filter_only:
        print(f"filtering only: {filter_only}")
        class_ids = list(filter(lambda i: class_names[i] in filter_only, range(len(class_names))))
    if filter_without:
        print(f"filtering without: {filter_without}")
        class_ids = list(filter(lambda i: class_names[i] not in filter_without, range(len(class_names))))

    img = cv.imread(path) # orig image
    height, width = img.shape[:2]
    img = cv.resize(img, max_image_res(width, height, 1280), interpolation = cv.INTER_CUBIC)

    for_crop = img.copy() # dup for cropping


    count_csv = [['class', 'count']]
    distance_csv = [['object1_name', 'object1_position', 'object2_name' , 'object2_position', 'distance']]
    coords = []
    centroids = []
    instance_names = []
    object_dict = {}
    class_counts = defaultdict(lambda: 0)

    random_name = str(uuid.uuid4().hex) # folder_dir
        # create directory for the objects output 
    if write_file:
        output_path = os.path.join(app.config["OUTPUT_PATH"], random_name)
        os.mkdir(output_path)
        img_path = os.path.join(output_path, 'objects')
        os.mkdir(img_path)


    # detect objects from the model
    classes, scores, boxes = model.detect(img, CONF_THRESHHOLD, NMS_THRESHHOLD)
    colors = np.random.uniform(60, 150, size=(len(classes), 3))

    i = 0
    for (class_id, score, box) in zip(classes, scores, boxes):
        if class_id[0] not in class_ids: # if this filtered
            continue

        # class counts and instance names
        class_name = class_names[class_id[0]]

        class_counts[class_name] += 1
        instance_name = f"{class_name}{class_counts[class_name]}"
        instance_names.append(instance_name)
        accuracy = float(score*100)
        # label = f'{class_name} {int(accuracy)}%'
        label = f'{instance_name} {int(accuracy)}%'
        

        # person: 98%
        # setting getting coords
        (x, y) = (box[0], box[1])
        (w, h) = (box[2], box[3])
        top_left, top_right = ((x, y), (x+w, y))
        bot_left, bot_right = ((x, y+h), (x+w, y+h))
        corners = (top_left, top_right, bot_left, bot_right)
        centroid = (x + (w//2), y + (h//2))
        # print("top", top_left, top_right)
        # print("bot", bot_left, bot_right)
        # print("centroid", centroid)
        coords.append(corners)
        centroids.append(centroid)
        object_dict[instance_name] = {'class': class_name, 'corner': corners, 'centroid': centroid, 'accuracy': accuracy}

        # set rectangle 
        color = colors[i]
        cv.rectangle(img, box, color, thickness=4) # for box

        if write_file:
            # cropping image
            class_path = os.path.join(img_path, class_name)
            try:
                os.mkdir(class_path)
            except FileExistsError:
                pass

            cropped_path = os.path.join(class_path, instance_name + f".{ext}")
            print(cropped_path)
            cropped = for_crop[y:y+h, x:x+w]
            cv.imwrite(cropped_path, cropped)

        # set text
        # print(f"{label} - {corners}")
        img = draw_text(img, label, pos=(box[0]+5, box[1]+5), text_color_bg=color)
        # img = cv.putText(img, label, (box[0]+5, box[1]+20), font, 0.5, (0,0,0), 2)
        i += 1

    
    # if more than 1 detection perform distance

    distances = []
    if i > 1: 
        for obj1, obj2 in list(combinations(object_dict, 2)):
            centroid_a = object_dict[obj1]['centroid']
            centroid_b = object_dict[obj2]['centroid']

            distance = ((centroid_a[0] - centroid_b[0]) ** 2 + (centroid_a[1] - centroid_b[1]) ** 2) ** 0.5
            distance_csv.append([obj1, centroid_a, obj2, centroid_b, distance])

            if show_distance: # show distance on image 
                distance = round(distance, 2)
                distance_x = (centroid_a[0] + centroid_b[0]) // 2
                distance_y = (centroid_a[1] + centroid_b[1]) // 2
                cv.circle(img, centroid_a, 5, (0, 0, 255), 10) # create circle at middle
                cv.circle(img, centroid_b, 5, (0, 0, 255), 10) # create circle at middle
                cv.line(img, centroid_a, centroid_b,(255,0,0),3)
                img = cv.putText(img, str(distance), (distance_x, distance_y), font, 1, (255,255,255), 2)
        # distance table 
        distances = list(np.around( dist.cdist(centroids, centroids, metric="euclidean"), decimals=2 ))
        # print(distances)

    class_counts = dict(class_counts)


    # append classes counts to csv
    filename = ""
    if write_file:
        # write csv
        for class_count in class_counts:
            count_csv.append([class_count, class_counts[class_count]])
        count_csv.append(['total', i])
        writeCSV(output_path, count_csv, 'count')
        writeCSV(output_path, distance_csv, 'distance')

        # write final output
        filename = f"output.jpg"
        path = os.path.join(output_path, filename)
        cv.imwrite(path, img)

    # return dictionary_count, total, path, distance
    return random_name, filename, i, class_counts, distances, instance_names, object_dict
