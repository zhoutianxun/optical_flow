import LucasKanade as LK

lk_obj = LK.LucasKanadeObj()

# Load video
path = input("Please enter the name of your file, ensure that file is placed in same folder as this script: ")
if lk_obj.load_video(path):
    
	# Let user choose points to track
    lk_obj.display_first_frame()
    
    while True:
        try:
            n = input("Roughly how many objects are present in the frame? Enter an integer: ")
            n = int(n)
            lk_obj.get_corners(maxCorners=2*n) 
            lk_obj.display_corners(round(max(lk_obj.first_frame.shape[0]/n, lk_obj.first_frame.shape[1]/n)))

            if input("Enter y to proceed if the points you wish to track are marked out; Enter any other keys to choose number of objects again> ") in ['y' or 'Y']:
                break 
        except ValueError:
            print("Please try again, enter an integer")

    lk_obj.user_choose_corners()
    
    print("press esc to quit")
    lk_obj.run()



