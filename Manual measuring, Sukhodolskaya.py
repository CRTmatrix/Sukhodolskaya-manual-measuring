import cv2
import numpy as np
import os
import copy
import math

Width=1366
Height=768
Latency=300
badtriviafractionworkaroundvar=False

def addressfix(address):
    fixedaddress=address
    for i in range(len(address)):
        if address[i]=='\\':
            fixedaddress=fixedaddress[:i]+'/'+fixedaddress[i+1:]
    return fixedaddress

def ftype(name):
    ftypes=['.png','.jpg','.bmp','.jpeg','.tiff']
    for i in ftypes:
        if i.upper() in name and '.xml' not in name or i in name:
            return True

def badtriviafractionworkaround(text):
    if badtriviafractionworkaroundvar==True:
        comatext=''
        for a in text:
            if a !='.':
                comatext+=a
            else:
                comatext+=','
    else:
        comatext=text
    return comatext

def measurePoints(event,x,y,flags,param):
        global order,prevX,prevY,table,errorcounter,radius,color,tableRow
        if event==cv2.EVENT_LBUTTONDBLCLK and order<14:
            order+=1
            signline=['A','B','V','G','D','E']
            print 'LM_#'+str(order),y,x
            if order<=14:
                tableRow.append(float(y));tableRow.append(float(x))
            if order<=2:
                color=(255,90,90)
            elif 2<order<=6:
                color=(0,0,255)
            elif 6<order<=10:
                color=(0,255,0)
            elif 10<order<=14:
                color=(255,0,0)
            else:
                pass
            if order%2!=0 and order<15:
                cv2.circle(img,(x,y),2,color,1)
                if order==1:
                    prevX=x;prevY=y
            elif order==2:
                if x==prevX and y==prevY:
                    print 'Wrong scale input'
                    order=0
                else:
                    cv2.circle(img,(x,y),2,color,1)
                    cv2.putText(img,('scale'+errorcounter),(x,y),cv2.FONT_HERSHEY_DUPLEX,0.5,(255,127,127),1)
            elif order%2==0 and 2<order<15:
                cv2.circle(img,(x,y),2,color,1)
                cv2.putText(img,(str(signline[int((order-3)/2)])+errorcounter),(x,y),cv2.FONT_HERSHEY_DUPLEX,0.5,(0,120,240),1)
        elif event==cv2.EVENT_RBUTTONUP and order<14:
            if order<=2:
                print 'nothing to discard'
            else:
                order=2
                errorcounter+='*'
                tableRow=tableRow[:5]
                print 'Last beetle\'s measures are discarded'

def trim(event,x,y,flags,param):
    global t,l,b,r,imgdsc,Pressed,warnVar
    if event==cv2.EVENT_LBUTTONDBLCLK:
        t,l=x,y # CAREFUL WITH CARTESIANS HERE!
        print 'top-left',t,l
        imgdsc[:,t]=(0,0,255)
        imgdsc[l]=(0,0,255)
        warnVar=False
    elif event==cv2.EVENT_RBUTTONDBLCLK:
        b,r=x,y
        print 'bottom-right',b,r
        imgdsc[:,b]=(255,0,0)
        imgdsc[r]=(255,0,0)
        warnVar=False
    elif Pressed==ord('e'):
        print 'erased'
        t,l,b,r=None,None,None,None
        imgdsc=Copied_imgdsc
        Pressed=None
    if t!=None and l!=None and b!=None and r!=None and warnVar==False:
        if t>b or l>r:
            print 'Misconfused corners!'
            warnVar=True
        elif t==b or l==r:
            print 'No area selected!'
            warnVar=True

def downscale(demonstrate):
    reso=demonstrate.shape
    sy,sx=reso[0],reso[1]
    if sy<Height*0.97 and sx<Width*0.97:
        Downscaled=demonstrate
    else:
        dsx,dsy=sx/(Width*0.97),sy/(Height*0.97)
        global trimscale
        if dsx>dsy:
            trimscale=1/dsx
        else:
            trimscale=1/dsy
        Downscaled=cv2.resize(demonstrate,(0,0),fx=trimscale,fy=trimscale)
    return Downscaled

def writedown(table,directory):
    header='PhName\tScale\tA\tB\tV\tG\tD\tE\tSex\n'
    for a in table[1:]:
        hor,ver=[10,18,26],[5,13,21]
        for b in ver:
            if a[b]>a[b+2]:
                CB,RB=a[b+2],a[b+3]
                a[b+2],a[b+3]=a[b],a[b+1]
                a[b],a[b+1]=CB,RB
        for b in hor:
            if a[b]>a[b+2]:
                CB,RB=a[b+1],a[b+2]
                a[b+1],a[b+2]=a[b-1],a[b]
                a[b-1],a[b]=CB,RB
        header+=a[0]+'\t'
        rowScale=math.sqrt((a[1]-a[3])**2+(a[2]-a[4])**2);header+=str(rowScale)+'\t'
        for c in range(5,28,4):
            header+=str(10*math.sqrt((a[c+2]-a[c])**2+(a[c+3]-a[c+1])**2)/rowScale)+'\t'
        header+=a[29]
    
    stringTable=''
    for a in table:
        for b in range(len(a)):
            c=str(a[b]);stringTable+=c
            if '\n' not in c:
                stringTable+='\t'

    with open(directory+'/LM table.txt','w') as results1:
        results1.write(badtriviafractionworkaround(stringTable))
        results1.close()
    with open(directory+'/Measures table.txt','w') as results2:
        results2.write(badtriviafractionworkaround(header))
        results2.close()

table=[['PhName','SP1R','SP1C','SP2R','SP2C',
        'AAR','AAC','APR','APC',
        'BLR','BLC','BRR','BRC',
        'VAR','VAC','VPR','VPC',
        'GLR','GLC','GRR','GRC',
        'DAR','DAC','DPR','DPC',
        'ELR','ELC','ERR','ERC','Sex\n']]
trimmingActionKeys=[ord('c'),ord('r'),ord('e'),ord('p')]
measureActionKeys=[ord('s'),ord('q'),ord('v'),ord('p')]

while True:
    try:
        directory=addressfix(r''+raw_input('Folder with your images:'))
        photos=[a for a in os.listdir(directory) if ftype(a)==True]
        break
    except Exception as WindowsError:
        print 'Wrong folder directory, repeat input.'

global breakingvar;breakingvar=False

for photo in photos:
    if breakingvar==True:
        break
    photopath=directory+'/'+photo
    img=cv2.imread(photopath,1)
    t,l,b,r=None,None,None,None
    imgdsc=downscale(img)

    cv2.imshow(photo, imgdsc)
    cv2.setMouseCallback(photo,trim)
    Copied_imgdsc=copy.deepcopy(imgdsc)
    while True:
        cv2.imshow(photo, imgdsc)
        Pressed=cv2.waitKey(Latency)&0xFF
        if Pressed in trimmingActionKeys:
            if Pressed==ord('p'):
                breakingvar=True
                Pressed=None
                break
            elif Pressed==ord('r'):
                imgdsc=np.rot90(imgdsc,1)
                img=np.rot90(img,1)
                Pressed=None
            elif t<b and l<r and t!=None and l!=None and b!=None and r!=None:
                if Pressed==ord('c'):
                    Pressed=None
                    break
    cv2.destroyAllWindows()
    if breakingvar==True:
        break
    imgreso=img.shape
    dscimgres=imgdsc.shape
    l1=l*imgreso[1]/dscimgres[1]
    r1=r*imgreso[1]/dscimgres[1]
    t1=t*imgreso[0]/dscimgres[0]
    b1=b*imgreso[0]/dscimgres[0]
    l1,r1,t1,b1=int(l1),int(r1),int(t1),int(b1)
    img=img[l1:r1,t1:b1]
    img=downscale(img)
    print 'Trimmed image shape is',img.shape

    errorcounter,order,tableRow='',0,[photo]
    cv2.namedWindow(photo)
    cv2.resizeWindow(photo, img.shape[0],img.shape[1])
    cv2.setMouseCallback(photo,measurePoints)
    while True:
        cv2.imshow(photo,img)
        Pressed=cv2.waitKey(Latency)
        if Pressed in measureActionKeys:
            if Pressed==ord('q'):
                Pressed=None
                break
            elif Pressed==ord('v'):
                order=0
                addvalue=''
                errorcounter+='*'
                tableRow=tableRow[:1]
                print 'scale and the last one\'s measures reset'
                Pressed=None
            elif Pressed==ord('s'):
                if order<14:
                    print 'Unfinished measurng'
                else:
                    sex=raw_input('beetle\'s sex:')
                    tableRow.append(sex+'\n');table.append(tableRow)
                    order=2
                    tableRow=tableRow[:5]
                    errorcounter=''
                    print 'Proceed to the next beetle'
                    Pressed=None
            elif Pressed==ord('p'):
                breakingvar=True
                Pressed=None
                break
    cv2.destroyAllWindows()
cv2.destroyAllWindows()

writedown(table,directory)
#quit()
