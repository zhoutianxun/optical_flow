import cv2
import sys
import matplotlib.pyplot as plt
from random import randint

(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

trackerTypes = ['BOOSTING', 'MIL', 'KCF', 'GOTURN', 'CSRT']

def createTrackerByName(trackerType):
	# Create a tracker based on tracker name
	if trackerType == trackerTypes[0]:
		tracker = cv2.legacy.TrackerBoosting_create()
	elif trackerType == trackerTypes[1]:
		tracker = cv2.legacy.TrackerMIL_create()
	elif trackerType == trackerTypes[2]: 
		tracker = cv2.legacy.TrackerKCF_create()
	elif trackerType == trackerTypes[3]:
		tracker = cv2.legacy.TrackerGOTURN_create()
	elif trackerType == trackerTypes[4]:
		tracker = cv2.legacy.TrackerCSRT_create()
	else:
		tracker = None
		print('Incorrect tracker name')
		print('Available trackers are:')
		for t in trackerTypes:
			print(t)
	return tracker

def crossLine(point, endA, endB, direction):
	# Each of the argument is a tuple representing the coordinate
	# endA and endB defines the line. Point is the point to check if crosses
	# direction is either +1 or -1. +1 indicate point going above line
	y = point[1]
	x = point[0]
	m = (endA[1] - endB[1])/(endA[0] - endB[0])

	lineY = m * (x - endA[0]) + endA[1]
	return direction*y > direction*lineY

# Read video
path = input("Please enter name of file, ensure that file is in same folder: ")
video = cv2.VideoCapture(path)

# Exit if video not opened.
if not video.isOpened():
	print("Could not open video")
	sys.exit()

# Read first frame.
ok, frame = video.read()
if not ok:
	print('Cannot read video file')
	sys.exit()

## Select boxes
bboxes = []
colors = [] 
frame_copy = frame.copy()
# OpenCV's selectROI function doesn't work for selecting multiple objects in Python
# So we will call this function in a loop till we are done selecting all objects
while True:
	# draw bounding boxes over objects
	# selectROI's default behaviour is to draw box starting from the center
	# when fromCenter is set to false, you can draw box starting from top left corner
	bbox = cv2.selectROI('MultiTracker', frame_copy, showCrosshair=True)
	bboxes.append(bbox)
	colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))

	p1 = (int(bbox[0]), int(bbox[1]))
	p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
	cv2.rectangle(frame_copy, p1, p2, colors[-1], 2, 1)
	print("Press q to quit selecting boxes and start tracking")
	print("Press any other key to select next object")
	k = cv2.waitKey(0) & 0xFF
	if (k == 113):  # q is pressed
		break

# remove any abnormal box
bboxes = list(filter(lambda x: x != (0,0,0,0), bboxes))

print('Selected bounding boxes {}'.format(bboxes))

# Specify the tracker type
print(f"Select tracker type by index: {trackerTypes}")
i = int(input(">> "))
trackerType = trackerTypes[i]

# Create MultiTracker object
multiTracker = cv2.legacy.MultiTracker_create()

# Initialize MultiTracker 
for bbox in bboxes:
	multiTracker.add(createTrackerByName(trackerType), frame, bbox)

# Define crossing line
line = [(0, 368), (frame.shape[0], 368)] # change this to change line
atTopPrev = None
atBottomPrev = None
crossedToTop = 0
crossedToBottom = 0

while video.isOpened():
	success, frame = video.read()
	if not success:
		break

	# get updated location of objects in subsequent frames
	success, boxes = multiTracker.update(frame)

	# keep track of objects above and below line
	atTop = 0
	atBottom = 0

	# draw tracked objects
	for i, newbox in enumerate(boxes):
		p1 = (int(newbox[0]), int(newbox[1]))
		p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
		cv2.rectangle(frame, p1, p2, colors[i], 2, 1)

		center = ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2)
		if crossLine(center, line[0], line[1], -1):
			atTop += 1
		if crossLine(center, line[0], line[1], 1):
			atBottom += 1

	# Display number of crosses on frame
	cv2.line(frame, line[0], line[1], (0,255,255), 2)
	cv2.putText(frame, str(atTop) + " cells above line", (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
	cv2.putText(frame, str(atBottom) + " cells below line", (20,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
	
	if atTopPrev != None and atBottomPrev != None:
		crossedToTop += max(0, atTop - atTopPrev)
		crossedToBottom += max(0, atBottom - atBottomPrev)
		cv2.putText(frame, str(crossedToTop) + " crosses to top", (450,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)
		cv2.putText(frame, str(crossedToBottom) + " crosses to bottom", (450,50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2)	
	
	atTopPrev = atTop
	atBottomPrev = atBottom

	# show frame
	cv2.imshow('MultiTracker', frame)
	
	# quit on ESC button
	if cv2.waitKey(80) & 0xFF == 27:  # Esc pressed
		break