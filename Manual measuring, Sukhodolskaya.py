import numpy as np,cv2,os,copy,math,ctypes

badtriviafractionworkaroundvar=False
Latency=300
user32=ctypes.windll.user32;user32.SetProcessDPIAware()
Width,Height=user32.GetSystemMetrics(0), user32.GetSystemMetrics(1); print Width,type(Width),Height,type(Height)
Pressed=None

def addressfix(address):
    if address[0] and address[len(address)-1] in ('\'','\"'):
        fixedaddress=address[1:len(address)-1]
    else:
        fixedaddress=address
    '''for i in range(len(address)):#redundant?
        if address[i]=='\\':
            fixedaddress=fixedaddress[:i]+'/'+fixedaddress[i+1:]'''
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
        global order,prevX,prevY,table,errorcounter,radius,color,tableRow,erasingsample,img
        if event==cv2.EVENT_LBUTTONDBLCLK and order<14:
            order+=1
            signline=['A','B','V','G','D','E']
            print 'LM_#'+str(order),y,x
            if order<=14:
                tableRow.append(float(y));tableRow.append(float(x))
            if order<=2:
                color=(255,127,0)
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
                    cv2.putText(img,('scale'+errorcounter*'*'),(x,y),cv2.FONT_HERSHEY_DUPLEX,0.5,(255,127,0),1)
            elif order%2==0 and 2<order<15:
                cv2.circle(img,(x,y),2,color,1)
                cv2.putText(img,(str(signline[int((order-3)/2)])+errorcounter*'*'),(x,y),cv2.FONT_HERSHEY_DUPLEX,0.5,(0,120,240),1)
        elif event==cv2.EVENT_RBUTTONDBLCLK:
            if order<=2 or len(tableRow)<=5:
                print 'No measuring to discard for the current beetle'
            else:
                toerase=len(tableRow)-2
                patch=erasingsample[int(tableRow[toerase])-14:int(tableRow[toerase])+3,int(tableRow[toerase+1])-3:int(tableRow[toerase+1])+14+errorcounter*8]#; patch=np.zeros((17,17,3),'uint8')
                img[int(tableRow[toerase])-14:int(tableRow[toerase])+3,int(tableRow[toerase+1])-3:int(tableRow[toerase+1])+14+errorcounter*8]=patch#; print img.shape,len(tableRow),a; cv2.rectangle(img,(int(tableRow[a+1])-3,int(tableRow[a])-14),(int(tableRow[a+1])+14,int(tableRow[a])+3),(0,255,0),3)
                order-=1; tableRow=tableRow[0:len(tableRow)-2]; toerase=None
                print 'Most recent landmark #'+str(order+1)+' is discarded'

def trim(event,x,y,flags,param):
    global t,l,b,r,imgdsc,warnVar,Pressed
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
    if sy<Height*0.95 and sx<Width*0.95:
        Downscaled=demonstrate
    else:
        dsx,dsy=sx/(Width*0.95),sy/(Height*0.95)
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

#def removedenotations(R,C, ,pic,cleanpic):

table=[['PhName','SP1R','SP1C','SP2R','SP2C',
        'AAR','AAC','APR','APC',
        'BLR','BLC','BRR','BRC',
        'VAR','VAC','VPR','VPC',
        'GLR','GLC','GRR','GRC',
        'DAR','DAC','DPR','DPC',
        'ELR','ELC','ERR','ERC','Sex\n']]
trimmingActionKeys=[ord('c'),ord('r'),ord('e'),ord('p')]
measureActionKeys=[ord('s'),ord('q'),ord('v'),ord('p'),ord('t')]

while True:
    try:
        directory=u''+addressfix(r''+raw_input('Folder with your images:'))
        photos=[a for a in os.listdir(directory.encode('utf-8')) if ftype(a)==True]
        break
    except Exception as WindowsError:
        print 'Wrong folder directory, repeat input.'

global breakingvar;breakingvar=False;Photonum=0

while True:
    Pressed=None
    if breakingvar==True or Photonum>=len(photos):
        break
    photopath=directory+'/'+photos[Photonum]
    img=cv2.imread(photopath,1);print photopath
    t,l,b,r=None,None,None,None
    imgdsc=downscale(img)

    cv2.imshow(photos[Photonum], imgdsc)
    cv2.setMouseCallback(photos[Photonum],trim)
    Copied_imgdsc=copy.deepcopy(imgdsc)
    while True:
        cv2.imshow(photos[Photonum], imgdsc)
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
    l1=int(l*imgreso[1]/dscimgres[1])
    r1=int(r*imgreso[1]/dscimgres[1])
    t1=int(t*imgreso[0]/dscimgres[0])
    b1=int(b*imgreso[0]/dscimgres[0])
    img=img[l1:r1,t1:b1]
    img=downscale(img)
    erasingsample=copy.deepcopy(img)
    print 'Trimmed image shape is',img.shape

    errorcounter,order,tableRow=0,0,[photos[Photonum]]
    cv2.namedWindow(photos[Photonum])
    cv2.setMouseCallback(photos[Photonum],measurePoints)
    while True:
        cv2.imshow(photos[Photonum],img)
        Pressed=cv2.waitKey(Latency)
        if Pressed in measureActionKeys:
            if Pressed==ord('q'):
                errorcounter=0
                Photonum+=1
                Pressed=None
                break
            elif Pressed==ord('t'):
                Pressed=None
                break
            elif Pressed==ord('v'):
                if order>=2:
                    for a in range(5,len(tableRow),2):
                        patch=erasingsample[int(tableRow[a])-14:int(tableRow[a])+3,int(tableRow[a+1])-3:int(tableRow[a+1])+14+errorcounter*8]
                        img[int(tableRow[a])-14:int(tableRow[a])+3,int(tableRow[a+1])-3:int(tableRow[a+1])+14+errorcounter*8]=patch
                    WSS=copy.deepcopy(tableRow[0:5])
                    for line in table:
                        if WSS[0] and WSS[1] and WSS[2] and WSS[3] and WSS[4] in line:
                            for b in range(5,len(line)-1,2):
                                patch=erasingsample[int(line[b])-14:int(line[b])+3,int(line[b+1])-3:int(line[b+1])+14+errorcounter*8]
                                img[int(line[b])-14:int(line[b])+3,int(line[b+1])-3:int(line[b+1])+14+errorcounter*8]=patch
                    table=[line for line in table if WSS[0] and WSS[1] and WSS[2] and WSS[3] and WSS[4] not in line]
                    errorcounter+=1; order=0; tableRow=tableRow[:1]
                    print 'Scale and the associated beetles\' measures are reset'
                elif order==1:
                    errorcounter+=1; order=0; tableRow=tableRow[:1]
                    print 'Scale is reset'
                elif order==0:
                    print 'No scale is yet set'
                Pressed=None
            elif Pressed==ord('s'):
                if order<14:
                    print 'Measurng is unfinished'
                else:
                    sex=raw_input('beetle\'s sex:')
                    tableRow.append(sex+'\n');table.append(tableRow);writedown(table,directory)#safe&ugly
                    order=2
                    tableRow=tableRow[:5]
                    print 'Proceed to the next beetle'
                    Pressed=None
            elif Pressed==ord('p'):
                breakingvar=True
                break
    writedown(table,directory)
    cv2.destroyAllWindows()
cv2.destroyAllWindows()
#quit()
