"""
Recognize food: fruit, vegetable, grain, meat
"""

import io
import os
from datetime import datetime
import requests
import cv2
from google.cloud import vision_v1p3beta1 as vision
import webbrowser

# Setup google authen client key
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'client_key.json'

FOOD_TYPE = 'Food'  # 'Vegetable'

APP_ID = "f42907f5"
APP_KEY = "c2b17669b4b9b1eff72c964c28c0d4b1"


def load_food_name(food_type):
    """
    Load all known food type name.
    :param food_type: Fruit, Vegetable, Grain, Meat
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

    file = open("output.txt","r+")

    for label in labels:
        # if len(text.description) == 10:
        desc = label.description.lower()
        score = round(label.score, 2)
        print("label: ", desc, "  score: ", score)
        if (desc in list_foods):
            # score = round(label.score, 3)
            # print(desc, 'score: ', score)
            # put name of food
            # enerkcal - calories
            # Procnt - protein
            # chocdf - carbs
            # FAt - fat
            # FIBTG - fiber
            # add serving size too
            nutrition = requests.get("https://api.edamam.com/api/food-database/v2/parser?app_id=%s&app_key=%s&ingr=%s&nutrition-type=logging" %(APP_ID, APP_KEY, desc))
            nutrition_json = nutrition.json()
            # measure and weight
            print(str(nutrition_json))
            if nutrition.status_code == 200:
                food = nutrition_json["text"]
                calories = nutrition_json["parsed"][0]["food"]["nutrients"]["ENERC_KCAL"]
                protein = nutrition_json["parsed"][0]["food"]["nutrients"]["PROCNT"]
                fat = nutrition_json["parsed"][0]["food"]["nutrients"]["FAT"]
                carbs = nutrition_json["parsed"][0]["food"]["nutrients"]["CHOCDF"]
                fiber = nutrition_json["parsed"][0]["food"]["nutrients"]["FIBTG"]
                serving_size = nutrition_json["parsed"][0]["measure"]["weight"]

                str1 = "Food: " + str(food)
                str2 = "Serving Size: " + str(serving_size) + " " + "grams"
                str3 = "Calories: " + str(calories) + " kcal"
                str4 = "Carbs: " + str(carbs) + " grams"
                str5 = "Protein: " + str(protein) + " grams"
                str6 = "Fat: " + str(fat) + " grams"
                str7 = "Fiber: " + str(fiber) + " grams"
                for L in [str1, str2, str3, str4, str5, str6, str7]:
                    file.writelines(L)
                    file.write("\n")
                webbrowser.open("output.txt")

                #cv2.waitKey(0)
                print('Total time: {}'.format(datetime.now() - start_time))
            else:
                print("Error: Food not present in Database")
            return True
    print('Total time: {}'.format(datetime.now() - start_time))
    return False

import cv2
cap = cv2.VideoCapture()
# The device number might be 0 or 1 depending on the device and the webcam
cap.open(0, cv2.CAP_DSHOW)
list_foods = load_food_name(FOOD_TYPE)
while(True):
    ret, frame = cap.read()
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    file = 'live.png'
    cv2.imwrite( file,frame)
    find_food = recognize_food(file, list_foods)
    # Display the resulting frame
    if (find_food):
        break
cap.release()
cv2.destroyAllWindows()
