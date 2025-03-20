class Gmath:
    def __init__(self):
        self.result = None
    
    def out(self, string=""):
        print(f"{string}{self.result}")
        return self
    
    def power(self, number, to):
        self.result = number ** to
        return self

    def rnd(self, number):
        self.result = round(number)
        return self
        
    def numroot(self, number, power):
        self.result = number ** (1/power)
        return self

    def PoL(self, invest, back, currency="$"):
        currency = str(currency)

        if (currency.isdigit()):
            raise ValueError("The currency cannot be a number.")

        if (len(currency) != 1):
            raise ValueError("The currency can only be up to 1 character and must be greater than 0.")

        if (invest == back):
            self.result = "NO PROFIT OR LOSS"
        elif (invest < back):
            money = back - invest
            self.result = f"PROFIT of {currency}{money}"
        else:
            money = invest - back
            self.result = f"LOSS of {currency}{money}"
        return self

    def area2(self, shape, x=0, y=0):
        shapes = ["circle", "square", "rectangle", "triangle", "parallelogram", "rhombus", "ellipse"]
        shape = shape.lower()
        if (shape not in shapes):
            raise ValueError(f"Invalid 2D shape '{shape}'.")
        else:
            if (shape == "circle"):
                self.result = 3.14159 * x ** 2
            elif (shape == "square"):
                self.result = x * x
            elif (shape == "rectangle"):
                self.result = x * y
            elif (shape == "triangle"):
                self.result = 1/2 * x * y
            elif (shape == "parallelogram"):
                self.result = x * y
            elif (shape == "rhombus"):
                self.result = 1/2 * x * y
            elif (shape == "ellipse"):
                self.result = 3.14159 * x * y
        return self

    def tsa3(self, shape, x=0, y=0, z=0):
        shape = shape.lower()
        shapes = ["cube", "cuboid", "cylinder", "sphere", "cone", "hemisphere"]
        if (shape not in shapes):
            raise ValueError(f"Invalid 3D shape '{shape}'.")
        else:
            if (shape == "cube"):
                self.result = 6 * x ** 2
            elif (shape == "cuboid"):
                self.result = 2 * (x * y + x * z + y * z)
            elif (shape == "sphere"):
                self.result = 4 * 3.14159 * x ** 2
            elif (shape == "cylinder"):
                self.result = 2 * 3.14159 * x * (x + y)
            elif (shape == "cone"):
                self.result = 3.14159 * x * (x + y)
            elif (shape == "hemisphere"):
                self.result = 3 * 3.14159 * x ** 2
        return self

    def perimeter2(self, shape, x=0, y=0):
        shapes = ["circle", "square", "rectangle", "triangle"]
        shape = shape.lower()
        if (shape not in shapes):
            raise ValueError(f"Invalid 2D shape '{shape}'.")
        else:
            if (shape == "circle"):
                self.result = 2 * 3.14159 * x
            elif (shape == "square"):
                self.result = 4 * x
            elif (shape == "rectangle"):
                self.result = 2 * (x + y)
            elif (shape == "triangle"):
                self.result = x + y + ((x**2 + y**2) ** 0.5)  # Assuming right triangle
        return self

    def vol3(self, shape, x=0, y=0, z=0):
        shapes = ["cube", "cuboid", "cylinder", "sphere", "cone", "hemisphere"]
        shape = shape.lower()
        if (shape not in shapes):
            raise ValueError(f"Invalid 3D shape '{shape}'.")
        else:
            if (shape == "cube"):
                self.result = x ** 3
            elif (shape == "cuboid"):
                self.result = x * y * z
            elif (shape == "sphere"):
                self.result = (4 / 3) * 3.14159 * x ** 3
            elif (shape == "cylinder"):
                self.result = 3.14159 * x ** 2 * y
            elif (shape == "cone"):
                self.result = (1 / 3) * 3.14159 * x ** 2 * y
            elif (shape == "hemisphere"):
                self.result = (2 / 3) * 3.14159 * x ** 3
        return self