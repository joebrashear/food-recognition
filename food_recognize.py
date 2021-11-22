"""
Recognize food: fruit, vegetable
"""

import io
import os
from datetime import datetime
import requests
import cv2
from google.cloud import vision_v1p3beta1 as vision

# Setup google authen client key
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_key.json'

# Source path content all images
SOURCE_PATH = "C:/Fruits/"

FOOD_TYPE = 'Fruit'  # 'Vegetable'

APP_ID = "f42907f5"
APP_KEY = "c2b17669b4b9b1eff72c964c28c0d4b1"


def load_food_name(food_type):
    """
    Load all known food type name.
    :param food_type: Fruit or Vegetable
    :return:
    """
    names = [line.rstrip('\n').lower() for line in open('dict/' + food_type + '.dict')]
    return names


def recognize_food(img_path, list_foods):
    start_time = datetime.now()

    # Read image with opencv
    img = cv2.imread(img_path)

    # Get image size
    height, width = img.shape[:2]

    # Scale image
    img = cv2.resize(img, (800, int((height * 800) / width)))

    # Save the image to temp file
    cv2.imwrite("output.jpg", img)

    # Create new img path for google vision
    img_path = "output.jpg"

    # Create google vision client
    client = vision.ImageAnnotatorClient()

    # Read image file
    with io.open(img_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.types.Image(content=content)

    # Recognize text
    response = client.label_detection(image=image)
    labels = response.label_annotations

    for label in labels:
        # if len(text.description) == 10:
        desc = label.description.lower()
        score = round(label.score, 2)
        print("label: ", desc, "  score: ", score)
        if (desc in list_foods):
            # score = round(label.score, 3)
            # print(desc, 'score: ', score)

            # Put text license plate number to image
            nutrition = requests.get("https://api.edamam.com/api/food-database/v2/parser?app_id=%s&app_key=%s&ingr=%s&nutrition-type=logging" %(APP_ID, APP_KEY, desc))
            print("status code", nutrition.status_code)
            nutrition_json = nutrition.json()
            if nutrition.status_code == 200:
                cv2.putText(img, str(nutrition_json["parsed"][0]["food"]["nutrients"]), (300, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 200), 2)
                cv2.imshow('Recognize & Draw', img)
                cv2.waitKey(0)

            # Get first fruit only
            break

    print('Total time: {}'.format(datetime.now() - start_time))

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    file = 'live.png'
    cv2.imwrite( file,frame)
    print('---------- Start FOOD Recognition --------')
    list_foods = load_food_name(FOOD_TYPE)
    print(list_foods)
    recognize_food(file, list_foods)
    # Display the resulting frame
    cv2.imshow('frame',frame)
    print('---------- End ----------')

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
print('---------- Start FOOD Recognition --------')
list_foods = load_food_name(FOOD_TYPE)
print(list_foods)
path = SOURCE_PATH + '1.jpg'
recognize_food(path, list_foods)
print('---------- End ----------')
