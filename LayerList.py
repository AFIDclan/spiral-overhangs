def parse(char, line):
    # Remove comments
    line = line.split(';')[0]
    if char in line:
        return float(line.split(char)[-1].split()[0])
    else:
        return None
        

class Line:
    def __init__(self, line):
        self.line = line

    @staticmethod
    def is_type(line):
        return False

    def render(self):
        return self.line


class Comment(Line):
    def __init__(self, line):
        super().__init__(line)

    @staticmethod
    def is_type(line):
        return line.startswith(';')

    def render(self):
        return self.line

class Acceleration(Line):
    # Acceleration keys:
    # P: - printing moves
    # R: - filament only moves
    # T: - travel moves (as of now T is ignored)
    # S: - default acceleration
    def __init__(self, line=""):
        super().__init__(line)
        self.p = parse('P', line)
        self.r = parse('R', line)
        self.t = parse('T', line)
        self.s = parse('S', line)


    @staticmethod
    def is_type(line):
        return line.startswith('M204') and ('P' in line or 'R' in line or 'T' in line or 'S' in line)

    def render(self):
        str = "M204"
        if self.p is not None:
            str += " P{}".format(self.p)
        if self.r is not None:
            str += " R{}".format(self.r)
        if self.t is not None:
            str += " T{}".format(self.t)
        if self.s is not None:
            str += " S{}".format(self.s)
        return str

class Position (Line):
    def __init__(self, line=""):
        super().__init__(line)
        self.x = parse('X', line)
        self.y = parse('Y', line)
        self.z = parse('Z', line)
        self.e = parse('E', line)

        if (self.e is None):
            self.e = 0.03762

    @staticmethod
    def is_type(line):
        return line.startswith('G1') and ('X' in line or 'Y' in line or 'Z' in line)

    def render(self):
        str = "G1"
        if self.x is not None:
            str += " X{}".format(self.x)
        if self.y is not None:
            str += " Y{}".format(self.y)
        if self.z is not None:
            str += " Z{}".format(self.z)
        if self.e is not None:
            str += " E{}".format(self.e)
        return str


class Unknown (Line):
    def __init__(self, line):
        super().__init__(line)

    @staticmethod
    def is_type(line):
        return True



class Layer:
    def __init__(self, lines=[]):
        self.lines = lines

    def get_positions(self):
        return [line for line in self.lines if isinstance(line, Position)]
        
    def render(self):
        return "\n".join([line.render() for line in self.lines])

    def add(self, line):
        self.lines.append(line)

    def add_terminator(self):

        # ;LAYER_CHANGE
        # ;Z:2
        # ;HEIGHT:0.2
        # ;BEFORE_LAYER_CHANGE
        # G92 E0.0
        # ;2

        # ;AFTER_LAYER_CHANGE
        self.lines.append(Comment("; stop printing object"))
        self.lines.append(Comment(";LAYER_CHANGE"))
        #self.lines.append(Comment(";Z:{}".format(0.2)))
        self.lines.append(Comment(";HEIGHT:0.2"))
        self.lines.append(Comment(";BEFORE_LAYER_CHANGE"))
        self.lines.append(Unknown("G92 E0.0"))
        self.lines.append(Comment(";AFTER_LAYER_CHANGE"))
        self.lines.append(Comment("; printing object"))

    @staticmethod
    def FromLines(in_lines):
        lines = []
        z=None
        for line in in_lines:
            if Position.is_type(line):
                p = Position(line)
                if p.z is not None:
                    z=p.z
                elif z is not None and p.z is None:
                    p.z = z
                lines.append(p)
            elif Acceleration.is_type(line):
                lines.append(Acceleration(line))
            elif Comment.is_type(line):
                lines.append(Comment(line))
            else:
                lines.append(Unknown(line))
        
        return Layer(lines)
        

class LayerList:
    def __init__(self, layers=[]):
        self.layers = layers


    def render(self):
        return "\n".join([layer.render() for layer in self.layers])

    @staticmethod
    def FromFile(gcode_file):
        layers = []
        with open(gcode_file, "r") as f:
            lines = f.readlines()
            layer_lines = []
            for line in lines:
                if line.startswith("; stop printing object"):
                    layer_lines.append(line.strip())
                    layers.append(Layer.FromLines(layer_lines))
                    layer_lines = []
                else:
                    layer_lines.append(line.strip())

        layers.append(Layer.FromLines(layer_lines))
        return LayerList(layers)