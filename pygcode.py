import re

#Probably useless, just a wrapper for an array?
class InstructionSet:
    # def __init__(self, instructions):
    #     self.instructions = instructions

    def parse(self, file):
        f = open(file, 'r')

        while True:
            line = f.readline().strip("\n")

            if line == "":
                break

            #Split on comment so we dont parse anyting in comments
            tokens = line.split(';')
            command = tokens[0]
            comment = "".join(tokens[1:None])

            if re.search("G\d", command) != None:
                flavor = 'G'
                idenifier = re.search("G\d+", command)[0]
                z = re.search("Z\d+\.\d+", command)[0] if re.search("Z\d+\.\d+", command) != None else ""
                x = re.search("X\d+\.\d+", command)[0] if re.search("X\d+\.\d+", command) != None else ""
                y = re.search("Y\d+\.\d+", command)[0] if re.search("Y\d+\.\d+", command) != None else ""
                e = re.search("E[\.]?\d+[\.]?\d+", command)[0] if re.search("E[\.]?\d+[\.]?\d+", command) != None else ""
                #f = re.search("F\d+\.\d+", command)[0] if re.search("F\d+\.\d+", command) != None else ""

                print(f"Parsed command {idenifier} {z} {x} {y} {e} ; {comment}")

            #Marlin commands are weird and we arent going to generate our own, so just pass it through
            elif re.search("M\d", command) != None:
                flavor = 'M'
                c = command.split('M')[1]
                print(f"Parsed command {flavor}{c} ; {comment}")
            else:
                print("Something else found")

            if not line:
                break

        f.close()



class GcodeCommand:
    def __init__(self, flavor, identifier, coordinates, feed, comment):
        self.flavor = flavor
        self.identifier = identifier
        self.coordinates = coordinates
        self.feed_rate = feed
        self.comment = comment


    

test = InstructionSet()

test.parse("./small_test_gcode.gcode")


#test_string = "G1 Z11.978 X102.334 Y105 E.03347"

#print(re.search("Z\d+\.\d+",test_string)[0])
