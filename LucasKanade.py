import numpy as np
from math import ceil
import cv2
import matplotlib.pyplot as plt

class LucasKanadeObj:
    def __init__(self, winsize=(11,11), maxLevel=2):
        """
        Lucas Kanade object 

        Parameters
        ----------
        winsize : tuple, optional
            window size for LK algorithm. The default is (15,15).
        maxLevel : TYPE, optional
            maximal pyramid level number for LK algorithm. The default is 2.
        maxCorners : TYPE, optional
            maximum number of corners generated for tracking. The default is 70.
        qualityLevel : TYPE, optional
            minimal accepted quality of image corners. The default is 0.3.
        minDistance : TYPE, optional
            minimum possible Euclidean distance between corners. The default is 0.3.
        blockSize : TYPE, optional
            average block size used for computing corner. The default is 8.

        """
        self.lk_params = dict( winSize  = winsize, maxLevel = maxLevel, criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.cap = None
        self.corners = None
        self.tracking_points = None
        self.first_frame = None
    
    def load_video(self, path):
        # loads video
        try:
            self.cap = cv2.VideoCapture(path)
            if self.cap.isOpened():
                print("Video loaded successfully")
                return True
            else:
                print("Video is not loaded successfully, please check path, program exits now...")
                return False
        except:
            print("Video is not loaded successfully, please check path, program exits now...")
            return False
    
    def display_first_frame(self):
        # Helper function to display first frame
        if type(self.first_frame) != list:
            ret, frame = self.cap.read()
            if ret:
                plt.imshow(frame, cmap='gray')
                plt.show(block=False)
        else:
            plt.imshow(self.first_frame, cmap='gray')
            plt.show(block=False)
        
    def get_corners(self, maxCorners=70, qualityLevel=0.3, minDistance=7, blockSize=7):
        # Take first frame and find corners in it
        self.corners = None
        self.feature_params = dict(maxCorners = maxCorners, qualityLevel = qualityLevel, minDistance = minDistance, blockSize = blockSize)
        ret, old_frame = self.cap.read()
        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
        self.corners = cv2.goodFeaturesToTrack(old_gray, mask = None, **self.feature_params)
        self.first_frame = old_frame
        
    def display_corners(self, feature_grid_size):
        """
        feature_grid_size : int
            divide the video frame into grids of feature_grid_size, only 1 feature will appear in each grid.
        """
        
        # Plot the first image, and annotate the points that were selected as good features for tracking
        plt.close()
        fig = plt.figure()
        fig.set_size_inches(15,20)
        plt.imshow(self.first_frame, cmap='gray')

        # Annotate points if there exist within n x n pixel grid
        grid = np.zeros((ceil(self.first_frame.shape[0]/feature_grid_size), 
                         ceil(self.first_frame.shape[1]//feature_grid_size)))
        counter = 0
        for point in self.corners:
            # check if another point has already been plotted in the same grid
            if grid[int(point[0,1]//feature_grid_size), int(point[0,0]//feature_grid_size)] == 0:
                plt.scatter(point[0,0], point[0,1], s=4, c='red')
                plt.annotate(counter, (point[0,0], point[0,1]), size=8, c='red')
                grid[int(point[0,1]//feature_grid_size), int(point[0,0]//feature_grid_size)] = 1.0
            counter += 1
        
        plt.show(block=False)

    def user_choose_corners(self):
        # Allow user to choose the points to follow
        self.tracking_points = None
        selections = input("Please key in the points you want to track, separated by comma (e.g. >> 3, 5,7 ): ")
        
        while True:
            try:
                selections = list(map(lambda x:int(x), selections.split(',')))
                '''
                if len(selections) < 2:
                    raise ValueError
                '''
                print(f"your selections is: {selections}")
                break
            except (NameError, ValueError, IndexError):
                selections = input("Input is invalid, please try again (e.g. >> 3, 5,7 ): ")
        
        self.tracking_points = self.corners[selections,:,:]
        
    def run(self):
        color = np.random.randint(0,255,(100,3))
        mask = np.zeros_like(self.first_frame)
        old_gray = cv2.cvtColor(self.first_frame, cv2.COLOR_BGR2GRAY)
        p0 = self.tracking_points.copy()

        while True:
            ret,frame = self.cap.read()
            if ret:
                frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            else:
                break
            
            # calculate optical flow
            p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, p0, None, **self.lk_params)
        
            # Select good points
            good_new = p1[st==1]
            good_old = p0[st==1]
        
            # draw the tracks
            for i,(new,old) in enumerate(zip(good_new,good_old)):
                a,b = new.ravel()
                c,d = old.ravel()
                mask = cv2.line(mask, (a,b),(c,d), color[i].tolist(), 2)
                frame = cv2.circle(frame,(a,b),5,color[i].tolist(),-1)
            img = cv2.add(frame,mask)
        
            cv2.imshow('frame',img)
        
            k = cv2.waitKey(30) & 0xff
            if k == 27:
                break
        
            # Now update the previous frame and previous points
            old_gray = frame_gray.copy()
            p0 = good_new.reshape(-1,1,2)
        
        cv2.destroyAllWindows()
        self.cap.release()
