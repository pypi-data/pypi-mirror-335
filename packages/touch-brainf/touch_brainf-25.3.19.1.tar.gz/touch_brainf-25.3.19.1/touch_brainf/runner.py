from touch_brainf.errors import *

class Runner: # this class is really the interpreter, i didnt call it "Interpreter" so that stuff made more sense

    def __init__(self, code: str):
        self.code = code

    def interpret(self, code: str): # interpret the program
        mem = [0]
        memPos = 0

        i = 0 # everything below is just brainf code stuff
        while i < len(code):
            if code[i] == ">":
                memPos += 1
                if len(mem) <= memPos:
                    mem.append(0)
            if code[i] == "<":
                memPos -= 1
                if memPos < 0:
                    raise PointerNotInRangeError("Attempted to go to a negative memory position", i)
            if code[i] == "+":
                mem[memPos] += 1
                if mem[memPos] >= 256:
                    mem[memPos] = 0
            if code[i] == "-":
                mem[memPos] -= 1
                if mem[memPos] <= -1:
                    mem[memPos] = 255    
            if code[i] == ".":
                print(chr(mem[memPos]), end="")
            if code[i] == ",":
                ascii_to_numb = str(input("Input Requested (Only the first character will be accepted): "))
                mem[memPos] = ord(ascii_to_numb[0])
            if code[i] == "[":
                if mem[memPos] == 0:
                    opening_count = 0
                    i+=1

                    while i < len(code):
                        if code[i] == "]" and opening_count == 0:
                            break
                        elif code[i] == "[":
                            opening_count+=1
                        elif code[i] == "]":
                            opening_count-=1
                        i+=1

            if code[i] == "]":
                if mem[memPos] != 0:
                    closing_count = 0
                    i-=1

                    while i >= 0:
                        if code[i] == "[" and closing_count == 0:
                            break
                        elif code[i] == "]":
                            closing_count+=1
                        elif code[i] == "[":
                            closing_count-=1
                        i-=1
                
            i+=1 # iterate (or something)


    def run(self): # just a run function which is a wrapper for interpret
        self.interpret(self.code)


            


    