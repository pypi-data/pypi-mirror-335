import cv2
import os
from time import time
from PIL import Image
import numpy as np
import PowerDB as pdb
def make_project(projectpath:str,messagable:bool=True):
    try:
        os.mkdir(f'{projectpath}\\data')
        os.mkdir(f'{projectpath}\\data\\classifiers')
        open(f'{projectpath}\\data\\haarcascade_frontalface_Default.xml','x')
        d = open(f'{os.path.dirname(os.path.abspath(__file__))}\\haarcascade_frontalface_Default.xml','r')
        data = d.read()
        d.close()
        f = open(f'{projectpath}\\data\\haarcascade_frontalface_Default.xml','w')
        f.write(data)
        f.close()
        pdb.create.makeDB(f'{projectpath}\\data\\userlist.pdb')
        pdb.create.makecontainer(f'{projectpath}\\data\\userlist.pdb')
    except (FileNotFoundError,FileExistsError,PermissionError,OSError):
        if messagable is True:
            print('ERROR, either in the matter of if a file exists or not , or about os and permiddions')
def add_user(projectpath:str,username:str,messagable:bool=True):
    names = set()
    try:
        z = pdb.container_data.readsectors(f'{projectpath}\\data\\userlist.pdb',0,pdb.container_data.numbersectors(f'{projectpath}\\data\\userlist.pdb',0,True))
    except FileNotFoundError:
        if messagable is True:
            print('database file does not exist')
        exit()
    for i in z:
        names.add(i)
    un = username
    if un == "None":
        if messagable is True:
            print("Error: Name cannot be 'None'")
    elif un in names:
        if messagable is True:
           print("Error: User already exists!")
    elif len(un) == 0:
        if messagable is True:
           print("Error: Name cannot be empty!")
    else:
        name = un
        names.add(name)
        for b in range(len(names)):
            pdb.container_data.insert(f'{projectpath}\\data\\userlist.pdb', list(names)[b], [0, b])
def capture_data(projectpath:str,username:str,cameraindex:int=0,windowed:bool=True, messagable:bool=True):
    path = f"{projectpath}/data/" + username
    num_of_images = 0
    try:
        detector = cv2.CascadeClassifier(f"{projectpath}/data/haarcascade_frontalface_default.xml")
    except:
        if messagable is True:
            print('cascade does not exist')
            exit()
    try:
        os.makedirs(path)
    except:
        if messagable is True:
           print('Directory Already Created')
    vid = cv2.VideoCapture(cameraindex)
    if messagable is True:
        print('capturing data is in action')
    while True:
        ret, img = vid.read()
        new_img = None
        grayimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face = detector.detectMultiScale(image=grayimg, scaleFactor=1.1, minNeighbors=5)
        for x, y, w, h in face:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 2)
            cv2.putText(img, "Face Detected", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255))
            cv2.putText(img, str(str(num_of_images) + " images captured"), (x, y + h + 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255))
            new_img = img[y:y + h, x:x + w]
        if windowed is True:
            cv2.imshow("Face Detection", img)
            key = cv2.waitKey(1) & 0xFF
        try:
            cv2.imwrite(str(path + "/" + str(num_of_images) + username + ".jpg"), new_img)
            num_of_images += 1
        except:

            pass
        if num_of_images > 300:  # take 300 frames
            break
    if windowed is True:
        cv2.destroyAllWindows()
def train_data(projectpath:str,username:str,messagable:bool=True):
        try:
            path = os.path.join(os.getcwd() + f"{projectpath}/data/" + username + "/")
            faces = []
            ids = []
            labels = []
            pictures = {}
            for root, dirs, files in os.walk(path):
                pictures = files
            for pic in pictures:
                imgpath = path + pic
                img = Image.open(imgpath).convert('L')
                imageNp = np.array(img, 'uint8')
                id = int(pic.split(username)[0])
                faces.append(imageNp)
                ids.append(id)
            ids = np.array(ids)
            clf = cv2.face.LBPHFaceRecognizer_create()
            clf.train(faces, ids)
            clf.write(f"{projectpath}/data/classifiers/" + username + "_classifier.xml")
        except FileNotFoundError:
            if messagable is True:
                print('path does not exist')
                exit()
def check_user(projectpath:str,username:str,cameraindex:int=0,timeout:int = 5,windowed:bool=True, messagable:bool=True):
    try:
        face_cascade = cv2.CascadeClassifier(f'{projectpath}/data/haarcascade_frontalface_default.xml')
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(f"{projectpath}/data/classifiers/{username}_classifier.xml")
        cap = cv2.VideoCapture(cameraindex)
        pred = False
        start_time = time()
        while True:
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:

                roi_gray = gray[y:y + h, x:x + w]

                id, confidence = recognizer.predict(roi_gray)
                confidence = 100 - int(confidence)
                if confidence > 50:
                    pred = True
                    text = 'Recognized: ' + username.upper()
                    font = cv2.FONT_HERSHEY_PLAIN
                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    frame = cv2.putText(frame, text, (x, y - 4), font, 1, (0, 255, 0), 1, cv2.LINE_AA)


                else:
                    pred = False
                    text = "Unknown Face"
                    font = cv2.FONT_HERSHEY_PLAIN
                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    frame = cv2.putText(frame, text, (x, y - 4), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
            if windowed is True:
                cv2.imshow("image", frame)
            elapsed_time = time() - start_time
            if elapsed_time >= timeout:
                if pred:
                    if messagable is True:
                       print('Congrats, You have already checked in')
                    return True
                else:
                    if messagable is True:
                       print('Alert, Please check in again')
                    return False

            if cv2.waitKey(20) & 0xFF == ord('q'):
                break
        cap.release()
        if windowed is True:
            cv2.destroyAllWindows()
    except FileNotFoundError:
        if messagable is True:
            print('either cascade or classifier is not found')
def remove_user(projectpath:str,username:str,messagable:bool=True):
    try:
        pdb.container_data.delete(f'{projectpath}\\data\\userlist.pdb',[0,pdb.container_data.readsectors(f'{projectpath}\\data\\userlist.pdb', 0,
                pdb.container_data.numbersectors(f'{projectpath}\\data\\userlist.pdb', 0, True)).index(username)])
    except (FileNotFoundError,ValueError):
        if messagable is True:
            print('ERROR!!, either username does not exist or database not found')
    try:
        os.remove(f'{projectpath}\\data\\classifiers\\{username}_classifier.xml')
    except (FileNotFoundError,OSError,PermissionError):
        if messagable is True:
            print('ERROR!!(one or more of those is/are the error: FileNotFoundError,OSError,PermissionError)')
    files = [f for f in os.listdir(f'{projectpath}\\data\\{username}') if os.path.isfile(os.path.join(f'{projectpath}\\data\\{username}', f))]
    try:
       for i in files:
          os.remove(f'{projectpath}\\data\\{username}\\{i}')
       os.rmdir(f'{projectpath}\\data\\{username}')
    except (FileNotFoundError, OSError, PermissionError):
        if messagable is True:
            print('ERROR!!(one or more of those is/are the error: FileNotFoundError,OSError,PermissionError)')
    if os.path.exists(f'{projectpath}\\data\\{username}') is False and os.path.exists(f'{projectpath}\\data\\classifiers\\{username}_classifier.xml') is False and username not in ' '.join([str(s) for s in pdb.container_data.readsectors(f'{projectpath}\\data\\userlist.pdb', 0,
                pdb.container_data.numbersectors(f'{projectpath}\\data\\userlist.pdb', 0, True))]):
        if messagable is True:
            print('all data about the user got removed')