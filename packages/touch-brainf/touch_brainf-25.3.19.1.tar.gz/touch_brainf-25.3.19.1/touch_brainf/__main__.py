import sys
import os
import random

import touch_brainf

# welcome to the __main__ file!
# hopefully i didnt add too many comments to this...

#this fuction below will print different statements depending on if the number is or is not 4

def main():

    try: # set the file name to the argument provided
        filename = str(sys.argv[1])
    except IndexError:
        touch_brainf.file_error() # if theres no file, throw the file error

    code = touch_brainf.get_code_from_file(filename)

    # code = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.[>+<-]>-."


    runner = touch_brainf.Runner(code) # initialize a Runner object with your code

    runner.run() # run

if __name__ == "__main__": # if the function is called with `python -m touch_brainf then this will work`
    main()