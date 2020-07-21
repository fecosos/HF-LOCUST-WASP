"""
Created on Thu Mar 12 15:03 2020

This script contains the class that is in charge to control
everything related with the visual camera. 

Actions to be performed with the camera:
    1) Connect to the camera on the correct serial port (it may change)
    2) Set the camera settings 
    3) Take images and store them to be readable by the main program
    4) Save those images on the correct path 
    5) GPS coordinates are tagged directl on the image, not in the json file
    6) write all the image path and the name on the json file

To do so, we will work with the pygame library for controlling the camera and 
as well as with numpy and cv2 (the same as the other programs contained on that project)
"""

import os
import json
import numpy as np
import cv2
from time import sleep
from config import *


class VisualCameraInterface():

    def __init__(self, timestamp):

        # visual camera settings
        self.port = "/dev/video0"
        #2528, 1968
        self.camera_settings = dict(
            frame_width = 2528, 
            frame_height = 1968,
            exposure = 50,
            brightness = 40,
            contrast = 30,
            saturation = 20,
        )
        
        # variables we need to introduce from the main script
        self.timestamp = timestamp
        #self.path = path_visualimages

        # We initialize the array containing the data of the images
        self.visualimages = []

    def load_settings(self, cap):
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_settings['frame_width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_settings['frame_height'])
        cap.set(cv2.CAP_PROP_EXPOSURE, self.camera_settings['exposure'])
        cap.set(cv2.CAP_PROP_BRIGHTNESS, self.camera_settings['brightness'])
        cap.set(cv2.CAP_PROP_CONTRAST, self.camera_settings['contrast'])
        cap.set(cv2.CAP_PROP_SATURATION, self.camera_settings['saturation'])

    def take_image(self):    #function to take an image with the visual camera
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            time.sleep(1)
            self.take_image()

        self.load_settings(cap)
        ret, img = cap.read()
        cap.release()
        
        print('visual image ok')
        return img


    def edit_json(self, newvisualimage):
        # we try to write an existing json. If not existing, we create a new one
        try:
            with open('/home/pi/Desktop/HF-LOCUST-WASP/visual_images.json', 'r+') as f:
                data = []
                try:
                    data = json.load(f)
                except:
                    print("Empty json r+")

                data.append(newvisualimage)
                f.seek(0)
                json.dump(data, f)
                f.truncate()
                f.close()

        except:
            with open('/home/pi/Desktop/HF-LOCUST-WASP/visual_images.json', 'w') as f:
                data = []
                try:
                    data = json.load(f)
                except:
                    print("Empty json x")

                data.append(newvisualimage)
                f.seek(0)
                json.dump(data, f)
                f.truncate()
                f.close()

        print("done")


    def write_json(self, num_visual, path_visual):
        
        self.visualimages.append(
            {
                "image_id": num_visual,
                "image_path": path_visual,
            }
        )

        locust_images = {
            "id": self.timestamp,
            "results": self.visualimages
        }

        return locust_images

    def tag_image(self, img, coordinates, heading):
        # Th main purspose of that function is tag the image with the image coordinates over a white bckground
        
        # we will draw a white rectangle as background 
        rectangle_bgr = (255, 255, 255)

        text = str(coordinates)

        font = cv2.FONT_HERSHEY_SIMPLEX
        # org
        org = (50, 50)
        # fontScale
        fontScale = 0.8

        # Blue color in BGR
        color = (0, 0, 0)

        # Line thickness of 2 px
        thickness = 2

        # get the width and height of the text box
        (text_width, text_height) = cv2.getTextSize(text, font, fontScale=fontScale, thickness=1)[0]
            
        # set the text start position
        text_offset_x = int(50 + text_width/2)
        text_offset_y = int(img.shape[0] - (25 + text_height/2))

        # make the coords of the box with a small padding of two pixels
        box_coords = ((text_offset_x, int(text_offset_y + 4)), (int(text_offset_x + text_width + 4), int(text_offset_y - text_height - 4)))
        print('box coords 0:', box_coords[0])
        print('box coords 1:', box_coords[1])
        
        cv2.rectangle(img, box_coords[0], box_coords[1], rectangle_bgr, cv2.FILLED)

        # Using cv2.putText() method
        cv2.putText(img, text, (text_offset_x, text_offset_y), font, fontScale, color, thickness, cv2.LINE_AA)

        if typeOfMission is "periscope":

            heading = int(heading)

            # Line thickness of 5 px
            thickness = 5

            # get the width and height of the text box
            (text_width, text_height) = cv2.getTextSize(heading, font, fontScale=fontScale, thickness=1)[0]

            # set the text start position
            text_offset_x = int((img.shape[1]/2)-(text_width/2))
            text_offset_y = int(50 + text_height/2)

            # make the coords of the box with a small padding of two pixels
            box_coords = ((text_offset_x, text_offset_y + 10), (text_offset_x + text_width + 10, text_offset_y - text_height - 10))
            cv2.rectangle(img, box_coords[0], box_coords[1], rectangle_bgr, cv2.FILLED)

            # Using cv2.putText() method
            cv2.putText(img, heading, (text_offset_x, text_offset_y), font, fontScale, color, thickness, cv2.LINE_AA)


        return img

    def save_image(self, path_visual, img, num):
        name = str(path_visual) + '/' + str(num) + '.jpeg'
        cv2.imwrite(name, img)

    