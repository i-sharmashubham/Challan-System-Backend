from datetime import datetime
from Engine import CaptureImage,PreProcessing,PlateLocalization,CharacterRecognition, get_owner_data,createChallan
import threading
import os
import time

REG_FINE = 2000
INS_FINE = 1000
PUC_FINE = 500
PLACE = 'CHECKPOST No.32, Navi-Mumbai, 410001'

today = []

class ChallanSystem(threading.Thread):
    def __init__(self,source):
        threading.Thread.__init__(self)
        self.source = source

    def run(self):
        try:
            image = CaptureImage(self.source)
            preProcessedImage = PreProcessing(image)
            plate = PlateLocalization(preProcessedImage,image)
            if plate is not None:
                isNumber,number = CharacterRecognition(plate)
                if isNumber:
                    print('Plate Detected :',number)
                    if number in today:
                        print(number,': Already penalized today')
                    else :
                        print(number,': fetching owner data from RTO')
                        owner = get_owner_data(number)
                        if owner is None:
                            print(number,': data not avilable with RTO')
                        else:
                            print(number,': data fetched, calculating fine')
                            challan_data = {
                                'reg_no' : number,
                                'name' : owner.owner,
                                'phone' : owner.phone,
                                'email' : owner.email,
                                'date' : datetime.now(),
                                'place' : PLACE,
                                'insurance' : 0,
                                'puc' : 0,
                                'registration' : 0,
                                }
                            isFine = False
                            if owner.reg_valid_till < datetime.now().date():
                                isFine = True
                                challan_data['registration'] = REG_FINE
                            if owner.ins_valid_till < datetime.now().date():
                                isFine = True
                                challan_data['insurance'] = INS_FINE
                            if owner.puc_valid_till < datetime.now().date():
                                isFine = True
                                challan_data['puc'] = PUC_FINE
                            if isFine:
                                if createChallan(image, challan_data):
                                    print(number,': challan created')
                                    today.append(number)
                                else:
                                    print(number,': error in challan creation')
                            else:
                                print(number,': challan not created, everything valid') 
                    print(number,': Done')                           
                else:
                    print('Plate Not Detected')
            else:
                print('Plate Not Detected')
        except Exception as e:
            print('Error in processing data :',e)


for img in os.listdir('images/'):
    ChallanSystem(os.path.join('images/', '2.jpg')).start()
    break
print('Exiting')

if __name__ == '__main__':
    #Starting Challan System
    try:
        print('Starting Challan System : Main Thread')
        print('Press CTRL+C to Stop System')
        while True:
            # Passing each image in interval of 5 Sec
            for img in os.listdir('images/'):
                ChallanSystem(os.path.join('images/', img)).start()
                time.sleep(5)
    except KeyboardInterrupt:
        print('Interrupted by User!')

