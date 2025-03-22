import numpy as np
import cv2
import os
from scipy import ndimage

# package1 image segmentation based on color
# package2 video segmentation based on color
# package3 similarates contour
# package4 2d orientation
# package5 feature tracking
# package6 3d rotation
#package7 3d orientation



# package1
def image_segmentation(path):
    # try this on greater pixel camera , greater or equal to mobile camera ,, greater the pixel better will it recognised colour
    try:
        os.makedirs("coloured_classified_images")
    except:
        pass
    img=cv2.imread(path)
    hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

    #red colour = 0-7,164-180
    mask1=cv2.inRange(hsv,np.array([0,50,50],np.uint8),np.array([7,255,255],np.uint8))
    mask2=cv2.inRange(hsv,np.array([164,50,50],np.uint8),np.array([180,255,255],np.uint8))
    mask=cv2.bitwise_or(mask1,mask2)
    imgo=cv2.bitwise_and(img,img,mask=mask)
    cv2.imwrite(r"coloured_classified_images\red.jpg",imgo)
    #orange = 8-17
    mask=cv2.inRange(hsv,np.array([8,50,50],np.uint8),np.array([17,255,255],np.uint8))
    imgo=cv2.bitwise_and(img,img,mask=mask)
    cv2.imwrite(r"coloured_classified_images\orange.jpg",imgo)
    #yellow = 18-31
    mask=cv2.inRange(hsv,np.array([18,50,50],np.uint8),np.array([31,255,255],np.uint8))
    imgo=cv2.bitwise_and(img,img,mask=mask)
    cv2.imwrite(r"coloured_classified_images\yellow.jpg",imgo)
    #green = 32-81
    mask=cv2.inRange(hsv,np.array([32,50,50],np.uint8),np.array([81,255,255],np.uint8))
    imgo=cv2.bitwise_and(img,img,mask=mask)
    cv2.imwrite(r"coloured_classified_images\green.jpg",imgo)
    #sky_blue=82-104
    mask=cv2.inRange(hsv,np.array([82,50,50],np.uint8),np.array([104,255,255],np.uint8))
    imgo=cv2.bitwise_and(img,img,mask=mask)
    cv2.imwrite(r"coloured_classified_images\skyblue.jpg",imgo)
    #blue=105-134
    mask=cv2.inRange(hsv,np.array([105,50,50],np.uint8),np.array([134,255,255],np.uint8))
    imgo=cv2.bitwise_and(img,img,mask=mask)
    cv2.imwrite(r"coloured_classified_images\blue.jpg",imgo)
    #violet=135-144
    mask=cv2.inRange(hsv,np.array([135,50,50],np.uint8),np.array([144,255,255],np.uint8))
    imgo=cv2.bitwise_and(img,img,mask=mask)
    cv2.imwrite(r"coloured_classified_images\violet.jpg",imgo)
    #purple=145-152
    mask=cv2.inRange(hsv,np.array([145,50,50],np.uint8),np.array([152,255,255],np.uint8))
    imgo=cv2.bitwise_and(img,img,mask=mask)
    cv2.imwrite(r"coloured_classified_images\purple.jpg",imgo)
    #pink=153-163
    mask=cv2.inRange(hsv,np.array([153,50,50],np.uint8),np.array([163,255,255],np.uint8))
    imgo=cv2.bitwise_and(img,img,mask=mask)
    cv2.imwrite(r"coloured_classified_images\pink.jpg",imgo)

def video_segmentation(path):
    cap=cv2.VideoCapture(path)
    try:
        os.makedirs("coloured_classified_video")
    except:
        pass
    fw=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fh=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps=int(cap.get(cv2.CAP_PROP_FPS))
    outblue=cv2.VideoWriter(r"coloured_classified_video\blue.mp4",cv2.VideoWriter_fourcc(*'mp4v'),fps,(fw,fh))
    outgreen=cv2.VideoWriter(r"coloured_classified_video\green.mp4",cv2.VideoWriter_fourcc(*'mp4v'),fps,(fw,fh))
    outorange=cv2.VideoWriter(r"coloured_classified_video\orange.mp4",cv2.VideoWriter_fourcc(*'mp4v'),fps,(fw,fh))
    outpink=cv2.VideoWriter(r"coloured_classified_video\pink.mp4",cv2.VideoWriter_fourcc(*'mp4v'),fps,(fw,fh))
    outpurple=cv2.VideoWriter(r"coloured_classified_video\purple.mp4",cv2.VideoWriter_fourcc(*'mp4v'),fps,(fw,fh))
    outred=cv2.VideoWriter(r"coloured_classified_video\red.mp4",cv2.VideoWriter_fourcc(*'mp4v'),fps,(fw,fh))
    outskyblue=cv2.VideoWriter(r"coloured_classified_video\skyblue.mp4",cv2.VideoWriter_fourcc(*'mp4v'),fps,(fw,fh))
    outviolet=cv2.VideoWriter(r"coloured_classified_video\violet.mp4",cv2.VideoWriter_fourcc(*'mp4v'),fps,(fw,fh))
    outyellow=cv2.VideoWriter(r"coloured_classified_video\yellow.mp4",cv2.VideoWriter_fourcc(*'mp4v'),fps,(fw,fh))
    while cap.isOpened():
        ret,frame=cap.read()
        if not ret:
            break
        img=frame
        hsv=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

        #red colour = 0-7,164-180
        mask1=cv2.inRange(hsv,np.array([0,50,50],np.uint8),np.array([7,255,255],np.uint8))
        mask2=cv2.inRange(hsv,np.array([164,50,50],np.uint8),np.array([180,255,255],np.uint8))
        mask=cv2.bitwise_or(mask1,mask2)
        imgo=cv2.bitwise_and(img,img,mask=mask)
        outred.write(imgo)
        #orange = 8-17
        mask=cv2.inRange(hsv,np.array([8,50,50],np.uint8),np.array([17,255,255],np.uint8))
        imgo=cv2.bitwise_and(img,img,mask=mask)
        outorange.write(imgo)
        #yellow = 18-31
        mask=cv2.inRange(hsv,np.array([18,50,50],np.uint8),np.array([31,255,255],np.uint8))
        imgo=cv2.bitwise_and(img,img,mask=mask)
        outyellow.write(imgo)
        #green = 32-81
        mask=cv2.inRange(hsv,np.array([32,50,50],np.uint8),np.array([81,255,255],np.uint8))
        imgo=cv2.bitwise_and(img,img,mask=mask)
        outgreen.write(imgo)
        #sky_blue=82-104
        mask=cv2.inRange(hsv,np.array([82,50,50],np.uint8),np.array([104,255,255],np.uint8))
        imgo=cv2.bitwise_and(img,img,mask=mask)
        outskyblue.write(imgo)
        #blue=105-134
        mask=cv2.inRange(hsv,np.array([105,50,50],np.uint8),np.array([134,255,255],np.uint8))
        imgo=cv2.bitwise_and(img,img,mask=mask)
        outblue.write(imgo)
        #violet=135-144
        mask=cv2.inRange(hsv,np.array([135,50,50],np.uint8),np.array([144,255,255],np.uint8))
        imgo=cv2.bitwise_and(img,img,mask=mask)
        outviolet.write(imgo)
        #purple=145-152
        mask=cv2.inRange(hsv,np.array([145,50,50],np.uint8),np.array([152,255,255],np.uint8))
        imgo=cv2.bitwise_and(img,img,mask=mask)
        outpurple.write(imgo)
        #pink=153-163
        mask=cv2.inRange(hsv,np.array([153,50,50],np.uint8),np.array([163,255,255],np.uint8))
        imgo=cv2.bitwise_and(img,img,mask=mask)
        outpink.write(imgo)
    cap.release()
    outpink.release()
    outblue.release()
    outgreen.release()
    outpurple.release()
    outorange.release()
    outred.release()
    outskyblue.release()
    outviolet.release()
    outyellow.release()

def contour_similarates(path1,path2,contour1index,contour2index):
    def cnt_magnify(cnt1,cnt2):
        #print(cnt1.shape,cnt2.shape)
        magnification_factor=cv2.contourArea(cnt2)/cv2.contourArea(cnt1)
        return magnification_factor
    def resize_cnt(cnt1,magnification_factor):    
        a=cnt1
        #print(a[:,1])
        x_multiply_factor,y_multiply_factor=magnification_factor,magnification_factor
        #print("escape1",a[:,0],"escape2")
        #metrix_x=np.array(a[:,0]*x_multiply_factor+xs)
        metrix_x=np.int64(a[:,0]*x_multiply_factor-(np.mean(a[:,0]*x_multiply_factor)-np.mean(a[:,0])))
        #metrix_y=np.array(a[:,1]*y_multiply_factor+ys)
        metrix_y=np.int64(a[:,1]*y_multiply_factor-(np.mean(a[:,1]*y_multiply_factor)-np.mean(a[:,1])))
        metrix=np.dstack([metrix_x,metrix_y])
        metrix=np.unique(metrix[0],axis=0)
        return metrix
    def similaratity(cnt2,metrix):
        a=metrix
        b=cnt2
        dif=np.array([])
        for i in range(0,len(a)):
            k=np.argmin(np.abs((b-a[i])[:,0])+np.abs((b-a[i])[:,1]))
            #print(k)
            dif=np.append(dif,np.sum(abs(b[k]-a[i])))
            #print(b[k]-a[i],b[k],a[i],k)
        if(len(dif)!=1):
            return np.sum(dif)/len(metrix)
        else:
            return dif/len(metrix)
    def image_read(img1,cnt2,magnification_factor):
        img1=cv2.GaussianBlur(img1,(5,5),0)
        img1=cv2.Canny(img1,50,150)
        img1=cv2.morphologyEx(img1,cv2.MORPH_CLOSE,(5,5))
        cnt1,_=cv2.findContours(img1,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        cnt1=cnt1[contour1index].reshape((-1,2))
        length=np.mean(cnt2,0)-np.mean(cnt1,0)
        cnt1=cnt1+np.mean(cnt2,0)-np.mean(cnt1,0)
        #print(cnt1,cnt1.reshape((-1,2)))
        mtrix=resize_cnt(cnt1,magnification_factor)
        similarity_index=similaratity(cnt2,mtrix)
        #print( magnification_factor,length,similarity_index)
        return magnification_factor,length,similarity_index   
    #__________________________________
    img0=cv2.imread(path1)
    '''cv2.imshow("testing",img0)
    cv2.waitKey(0)'''
    img0=cv2.GaussianBlur(img0,(5,5),0)
    img0=cv2.Canny(img0,50,150)
    img0=cv2.morphologyEx(img0,cv2.MORPH_CLOSE,(5,5))
    cnt1,_=cv2.findContours(img0,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    img2=cv2.imread(path2)
    img2=cv2.GaussianBlur(img2,(5,5),0)
    img2=cv2.Canny(img2,50,150)
    img2=cv2.morphologyEx(img2,cv2.MORPH_CLOSE,(5,5))
    cnt2,_=cv2.findContours(img2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    #print(len(cnt2),len(cnt1))
    cnt2=cnt2[contour2index]
    cnt1=cnt1[contour1index]
    magnification_factor_noted=cnt_magnify(cnt1,cnt2)
    if magnification_factor_noted>=1:
        pass
    else:
        path3=path1
        path1=path2
        path2=path3
    #________________________________
    img0=cv2.imread(path1)
    '''cv2.imshow("testing",img0)
    cv2.waitKey(0)'''
    img0=cv2.GaussianBlur(img0,(5,5),0)
    img0=cv2.Canny(img0,50,150)
    img0=cv2.morphologyEx(img0,cv2.MORPH_CLOSE,(5,5))
    cnt1,_=cv2.findContours(img0,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    img2=cv2.imread(path2)
    img2=cv2.GaussianBlur(img2,(5,5),0)
    img2=cv2.Canny(img2,50,150)
    img2=cv2.morphologyEx(img2,cv2.MORPH_CLOSE,(5,5))
    cnt2,_=cv2.findContours(img2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    cnt2=cnt2[contour2index]
    rcnt2=cnt2
    cnt1=cnt1[contour1index]
    rcnt1=cnt1
    try:
        magnification_factor=cnt_magnify(cnt1,cnt2)
    except:
        magnification_factor=1
    cnt2=cnt2.reshape((-1,2))
    mf,lengthr,sim=image_read(img0,cnt2,magnification_factor)
    return mf,lengthr,sim,rcnt1,rcnt2
def angle_turn_segment(path1,path2,contour1index,contour2index):
    def cnt_magnify(cnt1,cnt2):
        #print(cnt1.shape,cnt2.shape)
        magnification_factor=cv2.contourArea(cnt2)/cv2.contourArea(cnt1)
        return magnification_factor
    def resize_cnt(cnt1,magnification_factor):    
        a=cnt1
        #print(a[:,1])
        x_multiply_factor,y_multiply_factor=magnification_factor,magnification_factor
        #print("escape1",a[:,0],"escape2")
        #metrix_x=np.array(a[:,0]*x_multiply_factor+xs)
        metrix_x=np.int64(a[:,0]*x_multiply_factor-(np.mean(a[:,0]*x_multiply_factor)-np.mean(a[:,0])))
        #metrix_y=np.array(a[:,1]*y_multiply_factor+ys)
        metrix_y=np.int64(a[:,1]*y_multiply_factor-(np.mean(a[:,1]*y_multiply_factor)-np.mean(a[:,1])))
        metrix=np.dstack([metrix_x,metrix_y])
        metrix=np.unique(metrix[0],axis=0)
        return metrix
    def similaratity(cnt2,metrix):
        a=metrix
        b=cnt2
        dif=np.array([])
        for i in range(0,len(a)):
            k=np.argmin(np.abs((b-a[i])[:,0])+np.abs((b-a[i])[:,1]))
            #print(k)
            dif=np.append(dif,np.sum(abs(b[k]-a[i])))
            #print(b[k]-a[i],b[k],a[i],k)
        if(len(dif)!=1):
            return np.sum(dif)/len(metrix)
        else:
            return dif/len(metrix)
    def img_resize(cnt1,tita1):
        array=ndimage.rotate(cnt1,tita1,reshape=True)
        return array
    def image_read(img1,cnt2,magnification_factor):
        img1=cv2.GaussianBlur(img1,(5,5),0)
        img1=cv2.Canny(img1,50,150)
        img1=cv2.morphologyEx(img1,cv2.MORPH_CLOSE,(5,5))
        cnt1,_=cv2.findContours(img1,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        cnt1=cnt1[contour1index].reshape((-1,2))
        length=np.mean(cnt2,0)-np.mean(cnt1,0)
        cnt1=cnt1+np.mean(cnt2,0)-np.mean(cnt1,0)
        #print(cnt1,cnt1.reshape((-1,2)))
        mtrix=resize_cnt(cnt1,magnification_factor)
        similarity_index=similaratity(cnt2,mtrix)
        #print( magnification_factor,length,similarity_index)
        return magnification_factor,length,similarity_index   
    #__________________________________
    img0=cv2.imread(path1)
    '''cv2.imshow("testing",img0)
    cv2.waitKey(0)'''
    img0=cv2.GaussianBlur(img0,(5,5),0)
    img0=cv2.Canny(img0,50,150)
    img0=cv2.morphologyEx(img0,cv2.MORPH_CLOSE,(5,5))
    cnt1,_=cv2.findContours(img0,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    img2=cv2.imread(path2)
    img2=cv2.GaussianBlur(img2,(5,5),0)
    img2=cv2.Canny(img2,50,150)
    img2=cv2.morphologyEx(img2,cv2.MORPH_CLOSE,(5,5))
    cnt2,_=cv2.findContours(img2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    cnt2=cnt2[contour2index]
    cnt2r=cnt2
    cnt1=cnt1[contour1index]
    cnt1r=cnt1
    magnification_factor_noted=cnt_magnify(cnt1,cnt2)
    if magnification_factor_noted>=1:
        pass
    else:
        path3=path1
        path1=path2
        path2=path3
    #________________________________
    selecting=[]
    for i in range(0,360,10):
        img0=cv2.imread(path1)
        img0=img_resize(img0,i)
        #print(i)
        '''cv2.imshow("testing",img0)
        cv2.waitKey(0)'''
        img0=cv2.GaussianBlur(img0,(5,5),0)
        img0=cv2.Canny(img0,50,150)
        img0=cv2.morphologyEx(img0,cv2.MORPH_CLOSE,(5,5))
        cnt1,_=cv2.findContours(img0,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        img2=cv2.imread(path2)
        img2=cv2.GaussianBlur(img2,(5,5),0)
        img2=cv2.Canny(img2,50,150)
        img2=cv2.morphologyEx(img2,cv2.MORPH_CLOSE,(5,5))
        cnt2,_=cv2.findContours(img2,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
        cnt2=cnt2[contour2index]
        cnt1=cnt1[contour1index]
        try:
            magnification_factor=cnt_magnify(cnt1,cnt2)
        except:
            magnification_factor=1
        cnt2=cnt2.reshape((-1,2))
        selecting.append(image_read(img0,cnt2,magnification_factor)[-1])
        
        #print(image_read(img0,cnt2,magnification_factor))
    selecting=np.array(selecting)
    selecting_angle=range(0,360,10)[np.argmin(selecting)]
    rotation_angle=selecting_angle
    return rotation_angle,cnt1r,cnt2r
    '''for i in range(0,360,15):
        print(resize(img1,i))'''
def contourfeature_tracking(path,morphology_kernal_size_int,canny_min,canny_max,minimum_contour_area_threshold,contour_index_to_be_tracked,distanceshift):
    def feature_and_contour_tracking(path,morphology_kernal_size_int,canny_min,canny_max,minimum_contour_area_threshold,contour_index_to_be_tracked,distanceshift):
        def matching_features(frame1_cnt,frame2_cnt,feature_location,feature_index,feature_area,feature_track,l,issac,contour_track,distanceshift):
            contour_dummy=np.zeros(int(issac))
            contour_dummy=list(contour_dummy)
            #step1: area match and centroid location difference
            #1st area    #2nd distance
            global dummyindex3
            dummy=np.zeros_like(feature_location)
            dummy2=np.zeros_like(feature_area)
            tony=False
            for m in range(0,len(frame2_cnt)):
                indexes=[]
                if cv2.contourArea(frame2_cnt[m])!=0:
                    try:
                        index=(abs(1-feature_area/cv2.contourArea(frame2_cnt[m])))*(np.sum(abs(feature_location-np.mean(frame2_cnt[m],0)),1))
                        #print(np.min(index[np.argwhere(index!=0)]))
                        index=np.argmin(index)
                        indexes.append(index)
                        #print(index)
                        if np.sum(abs(feature_location[index]-np.mean(frame2_cnt[m],0)))<distanceshift:
                            feature_location[index]=np.mean(frame2_cnt[m],0)
                            dummy[index]=np.mean(frame2_cnt[m],0)
                            dummy2[index]=cv2.contourArea(frame2_cnt[m])
                            contour_dummy[index]=frame2_cnt[m]
                            feature_area[index]=cv2.contourArea(frame2_cnt[m])
                            if index==contour_index_to_be_tracked:
                                dummyindex3=m
                                tony=True
                        elif np.sum(abs(feature_location[index]-np.mean(frame2_cnt[m],0)))>2*distanceshift:
                            index3=np.intersect1d(np.argwhere(feature_location[:,0]==0),np.argwhere(feature_location[:,1]==0))[0]
                            feature_location[index3]=np.mean(frame2_cnt[m],0)
                            dummy[index3]=np.mean(frame2_cnt[m],0)
                            dummy2[index3]=cv2.contourArea(frame2_cnt[m])
                            contour_dummy[index3]=frame2_cnt[m]
                            feature_area[index3]=cv2.contourArea(frame2_cnt[m])
                            if index3==contour_index_to_be_tracked:
                                dummyindex3=m
                                tony=True
                    except:
                        pass
                        #print(np.min(index[np.argwhere(index!=0)]))
            #3rd reindexing of feature index
            #4th update feature location & area
            feature_track.append(dummy)
            contour_track.append(contour_dummy)
            #print(dummyindex3)
            if tony==True:
                return dummy,feature_track,dummyindex3,tony,feature_location,contour_track
            else:
                return dummy,feature_track,0,tony,feature_location,contour_track
        cap=cv2.VideoCapture(path)
        feature_location=np.array([])
        feature_index=np.array([])
        feature_area=np.array([])
        index_length=np.array([])
        f=open('featuretracking','w')
        feature_track=[]
        contour_track=[]
        t=0
        i=0
        j=0
        apple=0
        l=0
        tony=False
        while True:
            ret,frame=cap.read()
            if not ret:
                if i==1:
                    break
                else:
                    cap=cv2.VideoCapture(path)
                    ret,frame=cap.read()
                    frameheight,framewidth,framechannels=frame.shape
                    i=1
            stml=np.zeros_like(frame)
            stml2=np.zeros_like(frame)
            frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            
            frame=cv2.Canny(frame,10,70)
            blurred=cv2.GaussianBlur(frame,(7,7),0)
            img2=cv2.Canny(blurred,canny_min,canny_max)
            kernel=np.ones((morphology_kernal_size_int,morphology_kernal_size_int),np.uint8)
            frame=cv2.morphologyEx(img2,cv2.MORPH_CLOSE,kernel)
            '''    
            
            cnt_img2,_=cv2.findContours(img2,cv2.RETR_LIST , cv2.CHAIN_APPROX_NONE)'''
            cnt,_=cv2.findContours(frame,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(stml,cnt,-1,(255,255,255),2)
            frame2=frame.copy()
            frame1=cv2.Canny(frame,0,30)
            
            cnt2=[]
            for sm in range(0,len(cnt)):
                if cv2.contourArea(cnt[sm])>minimum_contour_area_threshold:
                    cnt2.append(cnt[sm])
            if i==1:
                if j==0:
                    print('number of contours under conditions',np.max(index_length))
                    feature_index=np.arange(0,np.max(index_length))
                    issac=np.max(index_length)
                    #print(feature_index[:5],feature_index[-5:])
                    for k in range(0,len(cnt2)):
                        #print("noting",len(cnt2))
                        feature_location=np.append(feature_location,np.mean(cnt2[k],0))
                        feature_area=np.append(feature_area,cv2.contourArea(cnt2[k]))
                    feature_area=np.append(feature_area,np.zeros((int(np.max(index_length)-len(cnt2)))))
                    #print(feature_location,np.max(index_length)-len(cnt2))
                    feature_location=np.append(feature_location,np.zeros((2*int(np.max(index_length)-len(cnt2)))))
                    feature_location=feature_location.reshape(-1,2)
                    relative_shiftmin,relative_shiftmax=np.min(np.subtract(index_length[1:],index_length[:-1])),np.max(np.subtract(index_length[1:],index_length[:-1]))
                    j=j+1
                    #print(feature_area)
                #print(feature_location)
                #print(len(cnt2))
                feature_tracking,feature_track,dummyindex3,tony,feature_location,contour_track=matching_features(cnt1,cnt2,feature_location,feature_index,feature_area,feature_track,l,issac,contour_track,distanceshift)
                f.write(f'{feature_location}')
                l=1
                if apple==0:
                    color=[]
                    apple=apple+1
                    for n in range(0,len(feature_tracking)):
                        a=np.random.randint(0,255)
                        b=np.random.randint(0,255)
                        c=np.random.randint(0,255)
                        color.append([a,b,c])
                    #print('noting',feature_location,approximate_feature_track)

                for stmml in range(0,len(feature_tracking)):
                    
                    
                    stml=cv2.circle(stml,(int(feature_tracking[stmml][0]),int(feature_tracking[stmml][1])),10,color[stmml],-1)
                if tony==True:
                    cv2.drawContours(stml2,cnt2,dummyindex3,(0,0,255),-1)
            cnt1=cnt2
            if i==0:
                index_length=np.append(index_length,len(cnt2))
            #stlm=cv2.line(stml,(0,0),(182,97),(0,0,255),5)
            cv2.imshow('om',stml)
            cv2.imshow('om2',stml2)
            cv2.imshow('ok',frame)
            cv2.waitKey(1)
        cv2.destroyAllWindows()
        cap.release()
        f.close()
        return feature_track,contour_track,framewidth,frameheight
    ft,ct,framewidth,frameheight=feature_and_contour_tracking(path,morphology_kernal_size_int,canny_min,canny_max,minimum_contour_area_threshold,contour_index_to_be_tracked,distanceshift)
    contour_track=ct
    len(contour_track)
    for i in range(0,len(contour_track)):
        try:
            image=np.zeros((frameheight,framewidth,3),np.uint8)
            cv2.drawContours(image,contour_track[i][contour_index_to_be_tracked],-1,(255,0,255),5)
            cv2.imshow('image',image)
            cv2.waitKey(1)
        except:
            pass
    cv2.destroyAllWindows()
    return contour_track



#packing 6 3d rotation



def rotation3d(path,morphology_kernal_size_int,canny_min,canny_max,minimum_contour_area_threshold,contour_index_to_be_tracked,max_pixel_shift):
    def feature_and_contour_tracking(path,morphology_kernal_size_int,canny_min,canny_max,minimum_contour_area_threshold,contour_index_to_be_tracked,max_pixel_shift):
        def matching_features(frame1_cnt,frame2_cnt,feature_location,feature_index,feature_area,feature_track,l,issac,contour_track,max_pixel_shift):
            contour_dummy=np.zeros(int(issac))
            contour_dummy=list(contour_dummy)
            #step1: area match and centroid location difference
            #1st area    #2nd distance
            global dummyindex3
            dummy=np.zeros_like(feature_location)
            dummy2=np.zeros_like(feature_area)
            tony=False
            for m in range(0,len(frame2_cnt)):
                indexes=[]
                if cv2.contourArea(frame2_cnt[m])!=0:
                    try:
                        index=(abs(1-feature_area/cv2.contourArea(frame2_cnt[m])))*(np.sum(abs(feature_location-np.mean(frame2_cnt[m],0)),1))
                        #print(np.min(index[np.argwhere(index!=0)]))
                        index=np.argmin(index)
                        indexes.append(index)
                        #print(index)
                        if np.sum(abs(feature_location[index]-np.mean(frame2_cnt[m],0)))<max_pixel_shift:
                            feature_location[index]=np.mean(frame2_cnt[m],0)
                            dummy[index]=np.mean(frame2_cnt[m],0)
                            dummy2[index]=cv2.contourArea(frame2_cnt[m])
                            contour_dummy[index]=frame2_cnt[m]
                            feature_area[index]=cv2.contourArea(frame2_cnt[m])
                            if index==contour_index_to_be_tracked:
                                dummyindex3=m
                                tony=True
                        elif np.sum(abs(feature_location[index]-np.mean(frame2_cnt[m],0)))>2*max_pixel_shift:
                            index3=np.intersect1d(np.argwhere(feature_location[:,0]==0),np.argwhere(feature_location[:,1]==0))[0]
                            feature_location[index3]=np.mean(frame2_cnt[m],0)
                            dummy[index3]=np.mean(frame2_cnt[m],0)
                            dummy2[index3]=cv2.contourArea(frame2_cnt[m])
                            contour_dummy[index3]=frame2_cnt[m]
                            feature_area[index3]=cv2.contourArea(frame2_cnt[m])
                            if index3==contour_index_to_be_tracked:
                                dummyindex3=m
                                tony=True
                    except:
                        pass
                        #print(np.min(index[np.argwhere(index!=0)]))
            #3rd reindexing of feature index
            #4th update feature location & area
            feature_track.append(dummy)
            contour_track.append(contour_dummy)
            #print(dummyindex3)
            if tony==True:
                return dummy,feature_track,dummyindex3,tony,feature_location,contour_track
            else:
                return dummy,feature_track,0,tony,feature_location,contour_track
        cap=cv2.VideoCapture(path)
        feature_location=np.array([])
        feature_index=np.array([])
        feature_area=np.array([])
        index_length=np.array([])
        f=open('featuretrack','w')
        feature_track=[]
        contour_track=[]
        t=0
        i=0
        j=0
        apple=0
        l=0
        tony=False
        while True:
            ret,frame=cap.read()
            if not ret:
                if i==1:
                    break
                else:
                    cap=cv2.VideoCapture(path)
                    ret,frame=cap.read()
                    image_height,image_width,image_channel=frame.shape
                    i=1
            stml=np.zeros_like(frame)
            stml2=np.zeros_like(frame)
            frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            
            frame=cv2.Canny(frame,10,70)
            blurred=cv2.GaussianBlur(frame,(7,7),0)
            img2=cv2.Canny(blurred,canny_min,canny_max)
            kernel=np.ones((morphology_kernal_size_int,morphology_kernal_size_int),np.uint8)
            frame=cv2.morphologyEx(img2,cv2.MORPH_CLOSE,kernel)
            '''    
            
            cnt_img2,_=cv2.findContours(img2,cv2.RETR_LIST , cv2.CHAIN_APPROX_NONE)'''
            cnt,_=cv2.findContours(frame,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(stml,cnt,-1,(255,255,255),2)
            frame2=frame.copy()
            frame1=cv2.Canny(frame,0,30)
            
            cnt2=[]
            for sm in range(0,len(cnt)):
                if cv2.contourArea(cnt[sm])>minimum_contour_area_threshold:
                    cnt2.append(cnt[sm])
            if i==1:
                if j==0:
                    print(np.max(index_length))
                    feature_index=np.arange(0,np.max(index_length))
                    issac=np.max(index_length)
                    #print(feature_index[:5],feature_index[-5:])
                    for k in range(0,len(cnt2)):
                        #print("noting",len(cnt2))
                        feature_location=np.append(feature_location,np.mean(cnt2[k],0))
                        feature_area=np.append(feature_area,cv2.contourArea(cnt2[k]))
                    feature_area=np.append(feature_area,np.zeros((int(np.max(index_length)-len(cnt2)))))
                    #print(feature_location,np.max(index_length)-len(cnt2))
                    feature_location=np.append(feature_location,np.zeros((2*int(np.max(index_length)-len(cnt2)))))
                    feature_location=feature_location.reshape(-1,2)
                    relative_shiftmin,relative_shiftmax=np.min(np.subtract(index_length[1:],index_length[:-1])),np.max(np.subtract(index_length[1:],index_length[:-1]))
                    j=j+1
                    #print(feature_area)
                #print(feature_location)
                #print(len(cnt2))
                feature_tracking,feature_track,dummyindex3,tony,feature_location,contour_track=matching_features(cnt1,cnt2,feature_location,feature_index,feature_area,feature_track,l,issac,contour_track,max_pixel_shift)
                f.write(f'{feature_location}')
                l=1
                if apple==0:
                    color=[]
                    apple=apple+1
                    for n in range(0,len(feature_tracking)):
                        a=np.random.randint(0,255)
                        b=np.random.randint(0,255)
                        c=np.random.randint(0,255)
                        color.append([a,b,c])
                    #print('noting',feature_location,approximate_feature_track)

                for stmml in range(0,len(feature_tracking)):
                    
                    
                    stml=cv2.circle(stml,(int(feature_tracking[stmml][0]),int(feature_tracking[stmml][1])),10,color[stmml],-1)
                if tony==True:
                    cv2.drawContours(stml2,cnt2,dummyindex3,(0,0,255),-1)
            cnt1=cnt2
            if i==0:
                index_length=np.append(index_length,len(cnt2))
            #stlm=cv2.line(stml,(0,0),(182,97),(0,0,255),5)
            cv2.imshow('om',stml)
            cv2.imshow('om2',stml2)
            cv2.imshow('ok',frame)
            cv2.waitKey(1)
        cv2.destroyAllWindows()
        cap.release()
        f.close()
        return feature_track,contour_track,image_height,image_width
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    #complete algorithm works from here
    #path1="C:\Users\vinay\Desktop\practice python\finding axis of rotation and amount of rotation\blue21.mp4"
    #path2="C:\Users\vinay\Desktop\sound\additional feature in robot\colours_algorithms\translation_rotation_features\blue21.mp4"
    #path3="C:\Users\vinay\Desktop\practice python\finding axis of rotation and amount of rotation\blue212.mp4"
    
    ft,ct,h,w=feature_and_contour_tracking(path,morphology_kernal_size_int,canny_min,canny_max,minimum_contour_area_threshold,contour_index_to_be_tracked,max_pixel_shift)
    contour_index_to_be_tracked
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    contour_track=ct
    len(contour_track)
    #draw contours

    # distinguish contour having maximum area
    def draw_contour(contour_index_to_be_tracked):
        for i in range(0,len(contour_track)):
            try:
                image=np.zeros((h,w,3),np.uint8)
                cv2.drawContours(image,contour_track[i][contour_index_to_be_tracked],-1,(255,0,255),5)
                cv2.imshow('image',image)
                cv2.waitKey(1)
            except:
                pass
        cv2.destroyAllWindows()
    draw_contour(contour_index_to_be_tracked)
    area=[]    
    for i in range(0,len(contour_track)):
        dummy=[]
        for j in range(0,len(contour_track[0])):
            try:
                dummy.append(cv2.contourArea(contour_track[i][j]))
                
            except:
                dummy.append(0)
        area.append(dummy)

    #################################################################################
    #step2
    #1st for perfect rotation
    #axis of rotation
    contour_excluded=np.argsort(np.sum(np.array(area),0))[-1]
    ft=np.array(ft)
    #ft[np.argwhere(ft[:,0]==[0,0])]
    ft[np.intersect1d(np.argwhere(ft[:,0][:,0]!=0) , np.argwhere(ft[:,0][:,1]!=0))][:,1]
    if 0!=contour_excluded:
        index=0
    else:
        index=len(contour_track[0])-1
    x,y=np.sum(ft[np.intersect1d(np.argwhere(ft[:,index][:,0]!=0) , np.argwhere(ft[:,index][:,1]!=0))][:,index][1:]-ft[np.intersect1d(np.argwhere(ft[:,index][:,0]!=0) ,np.argwhere(ft[:,index][:,1]!=0))][:,index][:-1],0)
    # y-axis==0 -x -ve x (-90,0) +ve x (0,90)
    #0 for y axis , 90 for x axis,angle of axis is orientation of axis of rotation , this is angle relative to x_axis and y_axis
    print(np.arctan(y/x)*180/np.pi)
    axis=int(np.arctan(y/x)*180/np.pi)
    print('axis of rotation angle relative to y_axis ',axis)
    if axis==0:
        print('perfect','y-axis')
        msc=0
    elif axis==90 or axis==-90:
        print('perfect','x-axis')
        msc=1
    elif 45>axis>-45:
        print('approximate axis=0','/','in case of perfect rotation exact axis=',axis)
        msc=0
    elif 90>axis>45 or -90<axis<-45:
        print('approximate axis=90','/','in case of perfect rotation exact axis=',axis)
        msc=1
    # we are working for axis with only 0 or 180 degree
    ########################################################################
    #step3
    #finding amount of rotation
    #selecting contours according to frame
    zeroornotcontours=np.array(area)
    total_frame=np.arange(0,len(zeroornotcontours))
    frame=np.array([])
    for i in range(0,len(zeroornotcontours[0])):
        first=np.min(np.argwhere(zeroornotcontours[:,i]!=0))
        last=np.max(np.argwhere(zeroornotcontours[:,i]!=0))
        print(first,last)
        frame=np.append(frame,np.array([first,last]))
    frame=np.array(np.reshape(frame,(-1,2)),np.uint64)
    indexes=list(np.argsort(frame[:,0]))
    indexes.remove(contour_excluded)
    #for doing this we need contours and centre
    #finding maximum lmax and wmax value for each contours and centres
    wmax=[]
    hmax=[]
    for j in indexes:
        wma=[]
        hma=[]
        for i in range(0,len(ft)):
            if ft[i][j][0]!=0 and ft[i][j][1]!=0:
                #print(ft[i][j])
                try:
                    wmax_wmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])
                    hmax_hmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])
                    #print(min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]),np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]))
                    #print(hmax_hmin)
                    wma.append(wmax_wmin)
                    hma.append(hmax_hmin)
                except:
                    #print(False)
                    pass
        wmax.append(max(wma))
        hmax.append(max(hma))
    #max(frame[indexes][0,:]),max(frame[indexes][:,1]),indexes,frame

    ###############################################
    #step3
    #finding amount of rotation
    #selecting contours according to frame
    zeroornotcontours=np.array(area)
    total_frame=np.arange(0,len(zeroornotcontours))
    frame=np.array([])
    for i in range(0,len(zeroornotcontours[0])):
        first=np.min(np.argwhere(zeroornotcontours[:,i]!=0))
        last=np.max(np.argwhere(zeroornotcontours[:,i]!=0))
        print(first,last)
        frame=np.append(frame,np.array([first,last]))
    frame=np.array(np.reshape(frame,(-1,2)),np.uint64)
    indexes=list(np.argsort(frame[:,0]))
    indexes.remove(contour_excluded)
    #for doing this we need contours and centre
    #finding maximum lmax and wmax value for each contours and centres
    wmax=[]
    hmax=[]
    for j in indexes:
        wma=[]
        hma=[]
        for i in range(0,len(ft)):
            if ft[i][j][0]!=0 and ft[i][j][1]!=0:
                #print(ft[i][j])
                try:
                    wmax_wmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])
                    hmax_hmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])
                    #print(min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]),np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]))
                    #print(hmax_hmin)
                    wma.append(wmax_wmin)
                    hma.append(hmax_hmin)
                except:
                    #print(False)
                    pass
        wmax.append(max(wma))
        hmax.append(max(hma))
    #max(frame[indexes][0,:]),max(frame[indexes][:,1]),indexes,frame
    ##################################################################
    #step4
    rotation_contour_time=[]
    print('msc',msc)
    if msc==0:
        k=0
        for j in indexes:   
            cap=cv2.VideoCapture(path)
            tracker=[]
            for i in range(0,len(ft)):
                ret,img=cap.read()
                if ft[i][j][0]!=0 and ft[i][j][1]!=0:
                    #print(ft[i][j])
                    try:
                        wmax_wmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])
                        hmax_hmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])
                        #print(min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]),np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]))
                        #print(90-90*wmax_wmin*hmax[k]/wmax[k]/hmax_hmin)                
                        cv2.drawContours(img,contour_track[i][j],-1,(0,255,255),4)
                        cv2.putText(img,f"{90-90*wmax_wmin*hmax[k]/wmax[k]/hmax_hmin}",(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,255),2,cv2.LINE_AA)
                        tracker.append([j,90-90*wmax_wmin*hmax[k]/wmax[k]/hmax_hmin])
                    except:
                        print(False)
                        try:
                            tracker.append(tracker[-1])
                        except:
                            tracker.append([j,np.nan])
                        pass
                else:
                    try:
                        tracker.append(tracker[-1])
                    except:
                        tracker.append([j,np.nan])
                cv2.waitKey(1)
                cv2.imshow('frame',img)
            k=k+1
            rotation_contour_time.append(tracker)
        max(frame[indexes][0,:]),max(frame[indexes][:,1]),indexes,frame
    elif msc==1:
        k=0
        for j in indexes:   
            cap=cv2.VideoCapture(path)
            tracker=[]
            for i in range(0,len(ft)):
                ret,img=cap.read()
                if ft[i][j][0]!=0 and ft[i][j][1]!=0:
                    #print(ft[i][j])
                    try:
                        wmax_wmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])
                        hmax_hmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])
                        #print(min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]),np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]))
                        #print(90-90*wmax_wmin*hmax[k]/wmax[k]/hmax_hmin)                
                        cv2.drawContours(img,contour_track[i][j],-1,(0,255,255),4)
                        cv2.putText(img,f"{90-90*hmax_hmin*wmax[k]/hmax[k]/wmax_wmin}",(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,255),2,cv2.LINE_AA)
                        tracker.append([j,90-90*hmax_hmin*wmax[k]/hmax[k]/wmax_wmin])
                    except:
                        try:
                            tracker.append(tracker[-1])
                        except:
                            tracker.append([j,np.nan])
                        print(False)
                        pass
                else:
                    try:
                        tracker.append(tracker[-1])
                    except:
                        tracker.append([j,np.nan])
                cv2.waitKey(1)
                cv2.imshow('frame',img)
            k=k+1
            rotation_contour_time.append(tracker)
        max(frame[indexes][0,:]),max(frame[indexes][:,1]),indexes,frame
    cv2.destroyAllWindows()
    cap.release()
    return axis,rotation_contour_time,contour_track

#packing 7 3d orientation
def orientation3d(path,morphology_kernal_size_int,canny_min,canny_max,minimum_contour_area_threshold,contour_index_to_be_tracked,max_pixel_shift):
    def feature_and_contour_tracking(path,morphology_kernal_size_int,canny_min,canny_max,minimum_contour_area_threshold,contour_index_to_be_tracked,max_pixel_shift):
        def matching_features(frame1_cnt,frame2_cnt,feature_location,feature_index,feature_area,feature_track,l,issac,contour_track,max_pixel_shift):
            contour_dummy=np.zeros(int(issac))
            contour_dummy=list(contour_dummy)
            #step1: area match and centroid location difference
            #1st area    #2nd distance
            global dummyindex3
            dummy=np.zeros_like(feature_location)
            dummy2=np.zeros_like(feature_area)
            tony=False
            for m in range(0,len(frame2_cnt)):
                indexes=[]
                if cv2.contourArea(frame2_cnt[m])!=0:
                    try:
                        index=(abs(1-feature_area/cv2.contourArea(frame2_cnt[m])))*(np.sum(abs(feature_location-np.mean(frame2_cnt[m],0)),1))
                        #print(np.min(index[np.argwhere(index!=0)]))
                        index=np.argmin(index)
                        indexes.append(index)
                        #print(index)
                        if np.sum(abs(feature_location[index]-np.mean(frame2_cnt[m],0)))<max_pixel_shift:
                            feature_location[index]=np.mean(frame2_cnt[m],0)
                            dummy[index]=np.mean(frame2_cnt[m],0)
                            dummy2[index]=cv2.contourArea(frame2_cnt[m])
                            contour_dummy[index]=frame2_cnt[m]
                            feature_area[index]=cv2.contourArea(frame2_cnt[m])
                            if index==contour_index_to_be_tracked:
                                dummyindex3=m
                                tony=True
                        elif np.sum(abs(feature_location[index]-np.mean(frame2_cnt[m],0)))>2*max_pixel_shift:
                            index3=np.intersect1d(np.argwhere(feature_location[:,0]==0),np.argwhere(feature_location[:,1]==0))[0]
                            feature_location[index3]=np.mean(frame2_cnt[m],0)
                            dummy[index3]=np.mean(frame2_cnt[m],0)
                            dummy2[index3]=cv2.contourArea(frame2_cnt[m])
                            contour_dummy[index3]=frame2_cnt[m]
                            feature_area[index3]=cv2.contourArea(frame2_cnt[m])
                            if index3==contour_index_to_be_tracked:
                                dummyindex3=m
                                tony=True
                    except:
                        pass
                        #print(np.min(index[np.argwhere(index!=0)]))
            #3rd reindexing of feature index
            #4th update feature location & area
            feature_track.append(dummy)
            contour_track.append(contour_dummy)
            #print(dummyindex3)
            if tony==True:
                return dummy,feature_track,dummyindex3,tony,feature_location,contour_track
            else:
                return dummy,feature_track,0,tony,feature_location,contour_track
        cap=cv2.VideoCapture(path)
        feature_location=np.array([])
        feature_index=np.array([])
        feature_area=np.array([])
        index_length=np.array([])
        f=open('featuretrack','w')
        feature_track=[]
        contour_track=[]
        t=0
        i=0
        j=0
        apple=0
        l=0
        tony=False
        while True:
            ret,frame=cap.read()
            if not ret:
                if i==1:
                    break
                else:
                    cap=cv2.VideoCapture(path)
                    ret,frame=cap.read()
                    image_height,image_width,image_channel=frame.shape
                    i=1
            stml=np.zeros_like(frame)
            stml2=np.zeros_like(frame)
            frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
            
            frame=cv2.Canny(frame,10,70)
            blurred=cv2.GaussianBlur(frame,(7,7),0)
            img2=cv2.Canny(blurred,canny_min,canny_max)
            kernel=np.ones((morphology_kernal_size_int,morphology_kernal_size_int),np.uint8)
            frame=cv2.morphologyEx(img2,cv2.MORPH_CLOSE,kernel)
            '''    
            
            cnt_img2,_=cv2.findContours(img2,cv2.RETR_LIST , cv2.CHAIN_APPROX_NONE)'''
            cnt,_=cv2.findContours(frame,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            cv2.drawContours(stml,cnt,-1,(255,255,255),2)
            frame2=frame.copy()
            frame1=cv2.Canny(frame,0,30)
            
            cnt2=[]
            for sm in range(0,len(cnt)):
                if cv2.contourArea(cnt[sm])>minimum_contour_area_threshold:
                    cnt2.append(cnt[sm])
            if i==1:
                if j==0:
                    print(np.max(index_length))
                    feature_index=np.arange(0,np.max(index_length))
                    issac=np.max(index_length)
                    #print(feature_index[:5],feature_index[-5:])
                    for k in range(0,len(cnt2)):
                        #print("noting",len(cnt2))
                        feature_location=np.append(feature_location,np.mean(cnt2[k],0))
                        feature_area=np.append(feature_area,cv2.contourArea(cnt2[k]))
                    feature_area=np.append(feature_area,np.zeros((int(np.max(index_length)-len(cnt2)))))
                    #print(feature_location,np.max(index_length)-len(cnt2))
                    feature_location=np.append(feature_location,np.zeros((2*int(np.max(index_length)-len(cnt2)))))
                    feature_location=feature_location.reshape(-1,2)
                    relative_shiftmin,relative_shiftmax=np.min(np.subtract(index_length[1:],index_length[:-1])),np.max(np.subtract(index_length[1:],index_length[:-1]))
                    j=j+1
                    #print(feature_area)
                #print(feature_location)
                #print(len(cnt2))
                feature_tracking,feature_track,dummyindex3,tony,feature_location,contour_track=matching_features(cnt1,cnt2,feature_location,feature_index,feature_area,feature_track,l,issac,contour_track,max_pixel_shift)
                f.write(f'{feature_location}')
                l=1
                if apple==0:
                    color=[]
                    apple=apple+1
                    for n in range(0,len(feature_tracking)):
                        a=np.random.randint(0,255)
                        b=np.random.randint(0,255)
                        c=np.random.randint(0,255)
                        color.append([a,b,c])
                    #print('noting',feature_location,approximate_feature_track)

                for stmml in range(0,len(feature_tracking)):
                    
                    
                    stml=cv2.circle(stml,(int(feature_tracking[stmml][0]),int(feature_tracking[stmml][1])),10,color[stmml],-1)
                if tony==True:
                    cv2.drawContours(stml2,cnt2,dummyindex3,(0,0,255),-1)
            cnt1=cnt2
            if i==0:
                index_length=np.append(index_length,len(cnt2))
            #stlm=cv2.line(stml,(0,0),(182,97),(0,0,255),5)
            cv2.imshow('om',stml)
            cv2.imshow('om2',stml2)
            cv2.imshow('ok',frame)
            cv2.waitKey(1)
        cv2.destroyAllWindows()
        cap.release()
        f.close()
        return feature_track,contour_track,image_height,image_width
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    #complete algorithm works from here
    #path1="C:\Users\vinay\Desktop\practice python\finding axis of rotation and amount of rotation\blue21.mp4"
    #path2="C:\Users\vinay\Desktop\sound\additional feature in robot\colours_algorithms\translation_rotation_features\blue21.mp4"
    #path3="C:\Users\vinay\Desktop\practice python\finding axis of rotation and amount of rotation\blue212.mp4"
    ft,ct,h,w=feature_and_contour_tracking(path,morphology_kernal_size_int,canny_min,canny_max,minimum_contour_area_threshold,contour_index_to_be_tracked,max_pixel_shift)
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    ###############################################################################################################################
    contour_track=ct
    len(contour_track)
    #draw contours

    # distinguish contour having maximum area
    def draw_contour(contour_index_to_be_tracked):
        for i in range(0,len(contour_track)):
            try:
                image=np.zeros((h,w,3),np.uint8)
                cv2.drawContours(image,contour_track[i][contour_index_to_be_tracked],-1,(255,0,255),5)
                cv2.imshow('image',image)
                cv2.waitKey(1)
            except:
                pass
        cv2.destroyAllWindows()
    draw_contour(contour_index_to_be_tracked)
    area=[]    
    for i in range(0,len(contour_track)):
        dummy=[]
        for j in range(0,len(contour_track[0])):
            try:
                dummy.append(cv2.contourArea(contour_track[i][j]))
                
            except:
                dummy.append(0)
        area.append(dummy)

    #################################################################################
    #step2
    #1st for perfect rotation
    #axis of rotation
    contour_excluded=np.argsort(np.sum(np.array(area),0))[-1]
    ft=np.array(ft)
    #ft[np.argwhere(ft[:,0]==[0,0])]
    ft[np.intersect1d(np.argwhere(ft[:,0][:,0]!=0) , np.argwhere(ft[:,0][:,1]!=0))][:,1]
    if 0!=contour_excluded:
        index=0
    else:
        index=len(contour_track[0])-1
    x,y=np.sum(ft[np.intersect1d(np.argwhere(ft[:,index][:,0]!=0) , np.argwhere(ft[:,index][:,1]!=0))][:,index][1:]-ft[np.intersect1d(np.argwhere(ft[:,index][:,0]!=0) ,np.argwhere(ft[:,index][:,1]!=0))][:,index][:-1],0)
    # y-axis==0 -x -ve x (-90,0) +ve x (0,90)
    #0 for y axis , 90 for x axis,angle of axis is orientation of axis of rotation , this is angle relative to x_axis and y_axis
    print(np.arctan(y/x)*180/np.pi)
    axis=int(np.arctan(y/x)*180/np.pi)
    print('axis of rotation angle relative to y_axis ',axis)
    if axis==0:
        print('perfect','y-axis')
        msc=0
    elif axis==90 or axis==-90:
        print('perfect','x-axis')
        msc=1
    elif 45>axis>-45:
        print('approximate axis=0','/','in case of perfect rotation exact axis=',axis)
        msc=0
    elif 90>axis>45 or -90<axis<-45:
        print('approximate axis=90','/','in case of perfect rotation exact axis=',axis)
        msc=1
    # we are working for axis with only 0 or 180 degree
    ########################################################################
    #step3
    #finding amount of rotation
    #selecting contours according to frame
    zeroornotcontours=np.array(area)
    total_frame=np.arange(0,len(zeroornotcontours))
    frame=np.array([])
    for i in range(0,len(zeroornotcontours[0])):
        first=np.min(np.argwhere(zeroornotcontours[:,i]!=0))
        last=np.max(np.argwhere(zeroornotcontours[:,i]!=0))
        print(first,last)
        frame=np.append(frame,np.array([first,last]))
    frame=np.array(np.reshape(frame,(-1,2)),np.uint64)
    indexes=list(np.argsort(frame[:,0]))
    indexes.remove(contour_excluded)
    #for doing this we need contours and centre
    #finding maximum lmax and wmax value for each contours and centres
    wmax=[]
    hmax=[]
    for j in indexes:
        wma=[]
        hma=[]
        for i in range(0,len(ft)):
            if ft[i][j][0]!=0 and ft[i][j][1]!=0:
                #print(ft[i][j])
                try:
                    wmax_wmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])
                    hmax_hmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])
                    #print(min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]),np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]))
                    #print(hmax_hmin)
                    wma.append(wmax_wmin)
                    hma.append(hmax_hmin)
                except:
                    #print(False)
                    pass
        wmax.append(max(wma))
        hmax.append(max(hma))
    #max(frame[indexes][0,:]),max(frame[indexes][:,1]),indexes,frame

    ###############################################
    #step3
    #finding amount of rotation
    #selecting contours according to frame
    zeroornotcontours=np.array(area)
    total_frame=np.arange(0,len(zeroornotcontours))
    frame=np.array([])
    for i in range(0,len(zeroornotcontours[0])):
        first=np.min(np.argwhere(zeroornotcontours[:,i]!=0))
        last=np.max(np.argwhere(zeroornotcontours[:,i]!=0))
        print(first,last)
        frame=np.append(frame,np.array([first,last]))
    frame=np.array(np.reshape(frame,(-1,2)),np.uint64)
    indexes=list(np.argsort(frame[:,0]))
    indexes.remove(contour_excluded)
    #for doing this we need contours and centre
    #finding maximum lmax and wmax value for each contours and centres
    wmax=[]
    hmax=[]
    ratioh_w=[]
    ratiow_h=[]
    for j in indexes:
        ratio_hw=[]
        ratio_wh=[]
        wma=[]
        hma=[]
        for i in range(0,len(ft)):
            if ft[i][j][0]!=0 and ft[i][j][1]!=0:
                #print(ft[i][j])
                try:
                    wmax_wmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])
                    hmax_hmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])
                    #print(min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]),np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]))
                    #print(hmax_hmin)
                    wma.append(wmax_wmin)
                    hma.append(hmax_hmin)
                    ratio_wh.append(wmax_wmin/hmax_hmin)
                    ratio_hw.append(hmax_hmin/wmax_wmin)
                except:
                    #print(False)
                    pass
        wmax.append(max(wma))
        hmax.append(max(hma))
        ratiow_h.append(min(ratio_wh))
        ratioh_w.append(min(ratio_hw))
    #max(frame[indexes][0,:]),max(frame[indexes][:,1]),indexes,frame
    ##################################################################
    #step4

    print('msc',msc)
    rotation_contour_time=[]
    if msc==0:
        k=0
        for j in indexes:   
            cap=cv2.VideoCapture(path)
            tracker=[]
            for i in range(0,len(ft)):
                ret,img=cap.read()
                if ft[i][j][0]!=0 and ft[i][j][1]!=0:
                    #print(ft[i][j])
                    try:
                        wmax_wmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])
                        hmax_hmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])
                        #print(min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]),np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]))
                        #print(90-90*wmax_wmin*hmax[k]/wmax[k]/hmax_hmin)                
                        cv2.drawContours(img,contour_track[i][j],-1,(0,255,255),4)
                        cv2.putText(img,f"{90-90*(wmax_wmin/hmax_hmin)*ratioh_w[k]}",(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,255),2,cv2.LINE_AA)
                        tracker.append([j,90-90*(wmax_wmin/hmax_hmin)*ratioh_w[k]])
                    except:
                        print(False)
                        try:
                            tracker.append(tracker[-1])
                        except:
                            tracker.append([j,np.nan])
                        pass
                else:
                    try:
                        tracker.append(tracker[-1])
                    except:
                        tracker.append([j,np.nan])
                cv2.waitKey(100)
                cv2.imshow('frame',img)
            k=k+1
            rotation_contour_time.append(tracker)
        max(frame[indexes][0,:]),max(frame[indexes][:,1]),indexes,frame
    elif msc==1:
        k=0
        for j in indexes:   
            cap=cv2.VideoCapture(path)
            tracker=[]
            for i in range(0,len(ft)):
                ret,img=cap.read()
                if ft[i][j][0]!=0 and ft[i][j][1]!=0:
                    #print(ft[i][j])
                    try:
                        wmax_wmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,1].flatten()==int(ft[i][j][1]))][:,:,0])
                        hmax_hmin=np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])-min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1])
                        #print(min(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]),np.max(contour_track[i][j].reshape(-1,2)[np.argwhere(contour_track[i][j][:,:,0].flatten()==int(ft[i][j][0]))][:,:,1]))
                        #print(90-90*wmax_wmin*hmax[k]/wmax[k]/hmax_hmin)                
                        cv2.drawContours(img,contour_track[i][j],-1,(0,255,255),4)
                        cv2.putText(img,f"{90-90*(hmax_hmin/wmax_wmin)*ratiow_h[k]}",(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(255,0,255),2,cv2.LINE_AA)
                        tracker.append([j,90-90*(hmax_hmin/wmax_wmin)*ratiow_h[k]])
                    except:
                        print(False)
                        try:
                            tracker.append(tracker[-1])
                        except:
                            tracker.append([j,np.nan])
                        pass
                else:
                    try:
                        tracker.append(tracker[-1])
                    except:
                        tracker.append([j,np.nan])
                
                cv2.waitKey(100)
                cv2.imshow('frame',img)
            k=k+1
            rotation_contour_time.append(tracker)
        max(frame[indexes][0,:]),max(frame[indexes][:,1]),indexes,frame
    cv2.destroyAllWindows()
    cap.release()
    return axis,indexes,rotation_contour_time,contour_track