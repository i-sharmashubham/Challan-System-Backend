from datetime import datetime
from Engine import CaptureImage,PreProcessing,PlateLocalization,CharacterRecognition
import os


for img in os.listdir('images/'):
    image = CaptureImage(os.path.join('images/', img))
    preProcessedImage = PreProcessing(image)
    plate = PlateLocalization(preProcessedImage,image)
    if plate is not None:
        isNumber,number = CharacterRecognition(plate)
        print(isNumber,number)