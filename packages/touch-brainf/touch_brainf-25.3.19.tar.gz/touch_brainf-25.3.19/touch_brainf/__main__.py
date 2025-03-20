import sys
import os
import random

import touch_brainf

# welcome to the __main__ file!
# hopefully i didnt add too many comments to this...

#this fuction below will print different statements depending on if the number is or is not 4
def file_error():
    what_to_print = random.randint(1, 10)

    if what_to_print != 4:
        print("Please import a .bf file")
    else:
        print("IMPORT A BRAN FLAKES FILE BOIIII 🗿🗿🗿🔥🔥🔥")

    exit()

def main():

    try: # set the file name to the argument provided
        filename = str(sys.argv[1])
    except IndexError:
        file_error() # if theres no file, throw the file error

    if os.path.splitext(filename)[1] == ".bf": 
        with open(filename, "r", encoding="utf8") as brainf_code: # utf8 is used to prevent any errors
            global code # we use the global code variable

            code = brainf_code.read()  
    else:
        file_error() # if the file isnt a .bf file, throw the file error

    # code = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.[>+<-]>-."


    runner = touch_brainf.Runner(code) # initialize a Runner object with your code

    runner.run() # run

if __name__ == "__main__": # if the function is called with `python -m touch_brainf then this will work`
    main()