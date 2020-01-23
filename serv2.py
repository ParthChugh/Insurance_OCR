import fitz
import cv2 
import pytesseract
#pytesseract.pytesseract.tesseract_cmd = 'C:\\ML\\Tesseract-OCR\\tesseract.exe'
factor=5
from flask import *
import time
import os
import csv
base_path=os.getcwd()+'/static/'

app = Flask(__name__)

flag_insured=0
flag_producer=0
flag_insurer=[]
flag_contact_name=0
flag_contact_email=0
flag_date=0
flag_certificate=0
flag_commercial=0
flag_commercial_value=[]
flag_auto=0
flag_auto_value=[]
flag_worker=0
flag_worker_value=[]
flag_pollution=0
flag_pollution_value=[]

def Convert(docpath,pages,docname):
    doc = fitz.open(docpath)
    print("Pages : ",doc.pageCount)
    mat = fitz.Matrix(factor,factor)
    for i in range(0,doc.pageCount):    
        page = doc.loadPage(i)
        pix = page.getPixmap(matrix = mat)
        pix.writePNG(base_path+docname+".png")
        if((i+1)==pages):
            break

def Get_Text(img):
    return pytesseract.image_to_string(img).replace("\n",' ').upper()

def showimage(image):
    cv2.imshow('image',cv2.resize(image, (950, 740)))
    #cv2.imshow('image',image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def Get_N_Biggest_Coor(img,i):    
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(grey,180,255,cv2.THRESH_BINARY)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = sorted(contours, key = cv2.contourArea, reverse = True)[:20]    
    x,y,w,h = cv2.boundingRect(cnts[i])  
    #cv.rectangle(img,(x,y),(x+w,y+h),(255,0,255),2) # Marking rect       
    return [x,y,w,h]

def Get_All_Coor(img):
    cnt=[]
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(grey,180,255,cv2.THRESH_BINARY)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)    
    for i in contours:         
         if(cv2.contourArea(i)>1000):
             x,y,w,h = cv2.boundingRect(i)  
             cnt.append([x,y,w,h])                          
    return cnt

def Get_All_Big_Coor(img):
    cnt=[]
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(grey,180,255,cv2.THRESH_BINARY)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)    
    for i in contours:         
         if(cv2.contourArea(i)>10500):
             x,y,w,h = cv2.boundingRect(i)  
             cnt.append([x,y,w,h])                          
    return cnt

def Get_All_Sorted_Coor(img):
    grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret,thresh = cv2.threshold(grey,180,255,cv2.THRESH_BINARY)
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)    
    cnts = sorted(contours, key = cv2.contourArea, reverse = True)
    return cnts


@app.route('/')
def upload():
    return render_template("index.html")

@app.route('/success', methods = ['POST'])
def success():
    name=str(round(time.time()))
    f = request.files['file']
    f.save(base_path+name+f.filename)    
    Convert(base_path+name+f.filename,1,name)
    return render_template("image.html",name=name)

@app.route('/api1')
def api1():
    filename=request.args['file']
    imgfile=base_path+filename+".png"
    img = cv2.imread(imgfile)            
    x,y,w,h=Get_N_Biggest_Coor(img,2)      
    img=img[y:y+h, x:x+w]
    cv2.imwrite(base_path+filename+"_1.png",img) 
    return filename+"_1.png"

@app.route('/api2')
def api2():
    filename=request.args['file']
    imgfile=base_path+filename+".png"
    img = cv2.imread(imgfile)    
    x,y,w,h=Get_N_Biggest_Coor(img,3)          
    img=img[y:y+h, x:x+w]
    cv2.imwrite(base_path+filename+"_2.png",img)     
    return (filename+"_2.png")

@app.route('/api3')
def api3():
    filename=request.args['file']
    imgfile=base_path+filename+".png"
    img = cv2.imread(imgfile)
    x,y,w,h=Get_N_Biggest_Coor(img,1)          
    img=img[y:y+h, x:x+w]
    cv2.imwrite(base_path+filename+"_3.png",img)     
    return (filename+"_3.png")


@app.route('/api1text')
def api1text():
    result=""
    flag_insured=0
    flag_producer=0
    flag_insurer=[]
    flag_contact_name=0
    flag_contact_email=0
    flag_date=0
    print("GETTING TEXT")
    filename=request.args['file']
    imgfile=base_path+filename+".png"
    img = cv2.imread(imgfile)
    cnt=Get_All_Coor(img)  
    cnt=cnt[0:-2]        
    flag_insurer=[]
    for i in cnt:                
        x,y,w,h=i 
        #cv.rectangle(img,(x,y),(x+w,y+h),(255,0,255),2) # Marking rect               
        #showimage(img[y:y+h, x:x+w])           
        text=Get_Text(img[y:y+h, x:x+w])           
        if("INSURED" in text and "CERTIFICATE" not in text):            
            flag_insured=text.split("INSURED")[-1]            
        if("PRODUCER" in text and "CERTIFICATE" not in text):
            flag_producer=text.split("PRODUCER")[-1]            
        if("INSURER" in text and "CERTIFICATE" not in text):            
            flag_insurer.append(text) 
        if("@" in text):
            flag_contact_email=text.split(" ")[-1]
        if("NAME" in text):
            flag_contact_name=text.split("NAME")[-1].replace("?","")
        if("DATE" in text):
            flag_date=text.split("DATE")[-1]
        
    result+="INSURED : "+str(flag_insured)+"&#13"
    result+="PRODUCER : "+str(flag_producer)+"&#13"
    result+="EMAIL : "+str(flag_contact_email)+"&#13"
    result+="NAME : "+str(flag_contact_name)+"&#13"
    result+="DATE : "+str(flag_date)+"&#13"
    flag_insurer=flag_insurer[::-1]    
    for i in flag_insurer:
        result+=i.replace("INSURERA","INSURER A").replace("INSURERB","INSURER B").replace("INSURERC","INSURER C").replace("INSURERD","INSURER D").replace("INSURERE","INSURER E").replace("INSURERF","INSURER F")+"&#13"
    return result

@app.route('/api2text')
def api2text():
    filename=request.args['file']
    imgfile=base_path+filename+".png"
    img = cv2.imread(imgfile)
    x,y,w,h=Get_N_Biggest_Coor(img,2)          
    img=img[y:y+h, x:x+w]
    text=Get_Text(img)
    flag_certificate=text
    return "CERTIFICATE HOLDER : "+flag_certificate 

@app.route('/api3text')
def api3text():
    result=""
    flag_commercial=0
    flag_commercial_value=[]
    flag_auto=0
    flag_auto_value=[]
    flag_worker=0
    flag_worker_value=[]
    flag_pollution=0
    flag_pollution_value=[]
    flag_umbrella=0
    flag_umbrella_value=[]
    filename=request.args['file']
    imgfile=base_path+filename+".png"
    img = cv2.imread(imgfile)
    cnt=Get_All_Big_Coor(img) 
    cnt=cnt[::-1]      
    cnt=cnt[2:]
    cnt.sort(key = lambda x: x[0])
    cnt.sort(key = lambda x: x[1])    
    for i in cnt:                
        x,y,w,h=i 
        print(x,y,w,h)
        #cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255),2) # Marking rect               
        text=Get_Text(img[y:y+h, x:x+w])        
        if("COMMERCIAL GENERAL" in text or flag_commercial==1):            
            flag_commercial=1
            if("AUTOMOBILE LIABILITY" in text):
                flag_commercial=0
            if(flag_commercial==1):
                flag_commercial_value.append(text) 
        
        if("AUTOMOBILE LIABILITY" in text or flag_auto==1):     
            flag_auto=1
            if("UMBRELLA" in text):
                flag_auto=0
            if(flag_auto==1):
                flag_auto_value.append(text)

        if("UMBRELLA" in text or flag_umbrella==1):     
            flag_umbrella=1
            if("WORKERS COMPENSATION" in text):
                flag_umbrella=0
            if(flag_umbrella==1):
                flag_umbrella_value.append(text)

        if("WORKERS COMPENSATION" in text or flag_worker==1):     
            flag_worker=1
            if("POLLUTION" in text):
                flag_worker=0
            if(flag_worker==1):
                flag_worker_value.append(text)

        if("POLLUTION" in text or flag_pollution==1):     
            flag_pollution=1
            if("DESCRIPTION" in text):
                flag_pollution=0
            if(flag_pollution==1):
                flag_pollution_value.append(text)

    #print(flag_commercial_value[1:-1])      
    #print(flag_auto_value[1:-1])
    #print(flag_umbrella_value[2:-1])
    #print(flag_worker_value[1:-1])
    #print(flag_pollution_value[1:])

        #showimage(img)
    result+=("COMMERCIAL GENERAL LIABILITY &#13 ")
    flag_commercial_value=flag_commercial_value[1:-1]    
    for k in range(0,len(flag_commercial_value)):
        if(not str(flag_commercial_value[k])==""):
            result+=(str(flag_commercial_value[k]))
            result+=(" &#13 ")
    result+=(" &#13 ")       

    result+=("AUTOMOBILE LIABILITY &#13 ")
    flag_auto_value=flag_auto_value[1:-1]    
    for k in range(0,len(flag_auto_value)):
        if(not str(flag_auto_value[k])==""):
            result+=(str(flag_auto_value[k]))
            result+=(" &#13 ")
    result+=(" &#13 ")
    
    result+=("UMBRELLA LIABILITY &#13 ")
    flag_umbrella_value=flag_umbrella_value[2:-1]    
    for k in range(0,len(flag_umbrella_value)):
        if(not str(flag_umbrella_value[k])==""):
            result+=(str(flag_umbrella_value[k]))
            result+=(" &#13 ")
    result+=(" &#13 ")

    result+=("WORKERS COMPENSATION AND EMPLOYERS LIABILITY &#13 ")
    flag_worker_value=flag_worker_value[1:-1]    
    for k in range(0,len(flag_worker_value)):
        if(not str(flag_worker_value[k])==""):
            result+=(str(flag_worker_value[k]))
            result+=(" &#13 ")
    result+=(" &#13 ")

    result+=(" &#13 ")
    flag_pollution_value=flag_pollution_value[1:]    
    for k in range(0,len(flag_pollution_value)):
        if(not str(flag_pollution_value[k])==""):
            result+=(str(flag_pollution_value[k]))
            result+=(" &#13 ")
    result+=(" &#13 ")
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)


