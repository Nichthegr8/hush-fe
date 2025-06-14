import os

def isFirstLaunch(fl_filename = "fl"):
    if not os.path.exists(fl_filename):
        open(fl_filename, "w+").close()
        return True
    return False