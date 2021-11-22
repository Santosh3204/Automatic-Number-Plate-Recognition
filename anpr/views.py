from pathlib import Path
from django.shortcuts import render
import cv2
import pytesseract
import numpy as np
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\S.Santosh Kumar\AppData\Local\Tesseract-OCR\tesseract.exe'
# Create your views here.


# create html page to accept image
# send image to server
# extract number from image
# send original image, detected image, cropped image, number to html page

cascade= cv2.CascadeClassifier("anpr/haarcascade_russian_plate_number.xml")
states={"AN":"Andaman and Nicobar","AP":"Andhra Pradesh","AR":"Arunachal Pradesh",
        "AS":"Assam","BR":"Bihar","CH":"Chandigarh","DN":"Dadra and Nagar Haveli",
        "DD":"Daman and Diu","DL":"Delhi","GA":"Goa","GJ":"Gujarat",
        "HR":"Haryana","HP":"Himachal Pradesh","JK":"Jammu and Kashmir","KA":"Karnataka",
        "KL":"Kerala","LD":"Lakshadweep","MP":"Madhya Pradesh","MH":"Maharashtra",
        "MN":"Manipur","ML":"Meghalaya","MZ":"Mizoram","NL":"Nagaland","OD":"Odissa",
        "PY":"Pondicherry","PN":"Punjab","RJ":"Rajasthan","SK":"Sikkim","TN":"TamilNadu",
        "TR":"Tripura","UP":"Uttar Pradesh", "WB":"West Bengal","CG":"Chhattisgarh",
        "TS":"Telangana","JH":"Jharkhand","UK":"Uttarakhand"}


def home_page(request):
    return render(request, "recognize.html")


def recognize_number(request):
    if request.method=="POST":

        print(request.FILES["image"])
        img_name = request.FILES["image"]
        print("1. web page image - ", img_name, type(img_name))

        im=Image.open(img_name)
        print("2. opening image - ", im, type(im))

        
        im.save("media/uploaded_image.jpg")
        path="media/uploaded_image.jpg"
        
        img=cv2.imread(path)
        print("3. reading image from media files - ", img, type(img))
        
        # Converting into Gray
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #cv2.imwrite("media/upload_gray.jpg", gray)
        print("4. Converting into Gray - ", gray, type(gray))

        # Detecting plate
        nplate = cascade.detectMultiScale(gray, 1.1, 4)
        print("5. detect multi scale - ", nplate, type(nplate))

        no_img=cv2.imread("media/no_image.png")

        cv2.imwrite('media/result.jpg', no_img)
        cv2.imwrite('media/plate.jpg', no_img)

        read="NA"
        for (x,y,w,h) in nplate:
            # Crop a portion of plate
            a, b = (int(0.02*img.shape[0]), int(0.01*img.shape[1]))
            #a, b = (int(0.02*img.shape[0]), int(0.02*img.shape[1]))
            plate = img[y+a:y+h-a, x+b:x+w-b, :]
            #cv2.imwrite("media/cropped_plate.jpg", plate)
            # make image more darker to identify the LPR
            ## iMAGE PROCESSING

            kernel = np.ones((1, 1), np.uint8)
            print("6. converting array to ones - ", kernel, type(kernel))

            plate = cv2.dilate(plate, kernel, iterations=1)
            print("7. dilate array to ones - ", plate, type(plate))
            print("7.1", kernel)

            plate = cv2.erode(plate, kernel, iterations=1)
            print("8. erode array to ones - ", plate, type(plate))
            print("8.1", kernel)

            #cv2.imwrite("media/clarity_plate.jpg", plate)

            plate_gray = cv2.cvtColor(plate,cv2.COLOR_BGR2GRAY)
            #cv2.imwrite("media/plate_gray.jpg", plate_gray)
            print("9. gray plate - ", plate_gray, type(plate_gray))

            (thresh, plate) = cv2.threshold(plate_gray, 127, 255, cv2.THRESH_BINARY)
            print("10. threshold and plate - ", thresh, plate, type(thresh), type(plate))
            #cv2.imwrite("media/bw_plate.jpg", plate)
            # Feed Image to OCR engine
            read = pytesseract.image_to_string(plate)       # AP10AT3204
            read = ''.join(e for e in read if e.isalnum())
            print(read)
            stat = read[0:2]
            try:
                # Fetch the State information
                print('Car Belongs to',states[stat])
            except:
                print('State not recognised!!')
            print(read)
            #number plate box
            cv2.rectangle(img, (x,y), (x+w, y+h), (51,51,255), 2)
            #text box
            #cv2.rectangle(img, (x, y - 40), (x + w, y),(51,51,255) , -1)
            # text keeping in box
            #cv2.putText(img,read, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            #cv2.imshow('Plate',plate)
            # Save & display result image
            cv2.imwrite('media/plate.jpg', plate)

        #cv2.imshow("Result", img)
        cv2.imwrite('media/result.jpg',img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        data={
            "uploaded_image": "uploaded_image.jpg",
            "plate_image": "plate.jpg",
            "car_image": "result.jpg",
            "plate_number": read
        }

        return render(request, "recognize.html", data)


# Let's make a function call