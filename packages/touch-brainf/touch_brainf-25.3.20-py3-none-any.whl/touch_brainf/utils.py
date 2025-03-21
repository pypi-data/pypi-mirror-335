import os
import random

def file_error():
    what_to_print = random.randint(1, 10)

    if what_to_print != 4:
        print("Please import a .bf file")
    else:
        print("IMPORT A BRAN FLAKES FILE BOIIII 🗿🗿🗿🔥🔥🔥")

    exit()

def get_code_from_file(filename: str) -> str:

    if os.path.splitext(filename)[1] == ".bf": 
        with open(filename, "r", encoding="utf8") as brainf_code: # utf8 is used to prevent any errors
            global code # we use the global code variable

            code = brainf_code.read()
            return code
    else:
        file_error() # if the file isnt a .bf file, throw the file error
        return None

    