import LucasKanade as LK

lk_obj = LK.LucasKanadeObj()

# Load video
path = input("Please enter the name of your file, ensure that file is placed in same folder as this script: ")
if lk_obj.load_video(path):

	lk_obj.get_corners()
	# Let user choose points to track
	lk_obj.user_choose_corners(50)

	print("press esc to quit")
	lk_obj.run()



