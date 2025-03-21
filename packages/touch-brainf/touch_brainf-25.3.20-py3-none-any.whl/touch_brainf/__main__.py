import sys
import os
import random
import argparse

import touch_brainf

# welcome to the __main__ file!
# hopefully i didnt add too many comments to this...

#this fuction below will print different statements depending on if the number is or is not 4

def main():

    version_path = os.path.join(touch_brainf.__path__[0], "data/version.txt")

    # playing with command parsing
    parser = argparse.ArgumentParser(prog="touch_brainf")
    parser.add_argument("filename", help="The file that you want to run", nargs=1)
    parser.add_argument("-v", "--version", action="version", version=open(version_path).read())
    args = parser.parse_args()

    filename = args.filename

    code = touch_brainf.get_code_from_file(filename)

    # code = "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++.[>+<-]>-."


    runner = touch_brainf.Runner(code) # initialize a Runner object with your code

    runner.run() # run

if __name__ == "__main__": # if the function is called with `python -m touch_brainf then this will work`
    main()