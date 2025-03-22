import pygame
class ColorType:
    TRANSPARENT = 101
    class Gradient:
        """
        A class for creating a gradient surface.(Not working anymore)

        Attributes:
            start_color (tuple): The starting color of the gradient.
            end_color (tuple): The ending color of the gradient.
            direction (str): The direction of the gradient (HORIZONTAL or VERTICAL).
        """
        HORIZONTAL = "horizontal"
        VERTICAL = "vertical"

        def __init__(self, start_color: tuple = (0, 0, 0), end_color: tuple = (255, 255, 255), direction: str = HORIZONTAL):
            """
            Initializes a Gradient object.(DONT WORK ANYMORE)

            Args:
                start_color (tuple, optional): The starting color of the gradient. Defaults to (0, 0, 0).
                end_color (tuple, optional): The ending color of the gradient. Defaults to (255, 255, 255).
                direction (str, optional): The direction of the gradient (HORIZONTAL or VERTICAL). Defaults to HORIZONTAL.

            Raises:
                ValueError: If the direction is not HORIZONTAL or VERTICAL.
            """
            self.start_color = start_color
            self.end_color = end_color
            if direction not in (self.HORIZONTAL, self.VERTICAL):
                raise ValueError("Invalid direction. Use 'horizontal' or 'vertical'.")
            self.direction = direction
            raise Exception("Use SEPARATE Gradient class instead")
        def __call__(self, surface) -> pygame.Surface:
            return

class Color_Type(ColorType):
    #Old Naming
    pass

TRANSPARENT_COLOR = 101

def hex(hex_color:str):h=hex_color.lstrip("#");return (int(h[:2],16),int(h[2:4],16),int(h[4:6],16))if len(h)==6 else(int(h[0]*2,16),int(h[1]*2,16),int(h[2]*2,16))if len(h)==3 else None
class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    MAGENTA = (255, 0, 255)
    LIME = (0, 255, 0) 
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    GRAY = (128, 128, 128)
    PINK = (255, 192, 203)
    PURPLE = (128, 0, 128)
    ORANGE = (255, 165, 0)
    BROWN = (165, 42, 42)
    SILVER = (192, 192, 192)
    GOLD = (255, 215, 0)
    PALEGREEN = (152, 251, 152)
    NAVY = (0, 0, 128)
    MAROON = (128, 0, 0)
    OLIVE = (128, 128, 0)
    TEAL = (0, 128, 128)
    AQUA = (0, 255, 255)
    LAVENDER = (230, 230, 250)
    BEIGE = (245, 245, 220)
    IVORY = (255, 255, 240)
    LEMONCHIFFON = (255, 250, 205)
    LIGHTYELLOW = (255, 255, 224)
    LAVENDERBLUSH = (255, 240, 245)
    MISTYROSE = (255, 228, 225)
    ANTIQUEWHITE = (250, 235, 215)
    PAPAYAWHIP = (255, 239, 213)
    BLANCHEDALMOND = (255, 235, 205)
    BISQUE = (255, 228, 196)
    PEACHPUFF = (255, 218, 185)
    NAVAJOWHITE = (255, 222, 173)
    MOCCASIN = (255, 228, 181)
    CORAL = (255, 127, 80)
    TOMATO = (255, 99, 71)
    ORANGERED = (255, 69, 0)
    DARKORANGE = (255, 140, 0)
    CHOCOLATE = (210, 105, 30)
    SADDLEBROWN = (139, 69, 19)
    LIGHTGRAY = (211, 211, 211)
    SILVERGRAY = (192, 192, 192)
    DARKGRAY = (169, 169, 169)
    LIGHTBLACK = (105, 105, 105)
    ALICEBLUE = (240, 248, 255)
    AQUAMARINE = (127, 255, 212)
    AZURE = (240, 255, 255)
    CHARTREUSE = (127, 255, 0)
    CORNFLOWERBLUE = (100, 149, 237)
    CRIMSON = (220, 20, 60)
    DARKBLUE = (0, 0, 139)
    DARKCYAN = (0, 139, 139)
    DARKGOLDENROD = (184, 134, 11)
    DARKGREEN = (0, 100, 0)
    DARKKHAKI = (189, 183, 107)
    DARKMAGENTA = (139, 0, 139)
    DARKOLIVEGREEN = (85, 107, 47)
    DARKRED = (139, 0, 0)
    DARKSALMON = (233, 150, 122)
    DARKSEAGREEN = (143, 188, 143)
    DARKSLATEBLUE = (72, 61, 139)
    DARKSLATEGRAY = (47, 79, 79)
    DARKTURQUOISE = (0, 206, 209)
    DARKVIOLET = (148, 0, 211)
    DEEPPINK = (255, 20, 147)
    DEEPSKYBLUE = (0, 191, 255)
    DODGERBLUE = (30, 144, 255)
    FIREBRICK = (178, 34, 34)
    FLORALWHITE = (255, 250, 240)
    FORESTGREEN = (34, 139, 34)
    FUCHSIA = (255, 0, 255)
    GAINSBORO = (220, 220, 220)
    GHOSTWHITE = (248, 248, 255)
    GOLDENROD = (218, 165, 32)
    GREENYELLOW = (173, 255, 47)
    HONEYDEW = (240, 255, 240)
    HOTPINK = (255, 105, 180)
    INDIANRED = (205, 92, 92)
    INDIGO = (75, 0, 130)
    KHAKI = (240, 230, 140)
    LAWNGREEN = (124, 252, 0)
    LIGHTBLUE = (173, 216, 230)
    LIGHTCORAL = (240, 128, 128)
    LIGHTCYAN = (224, 255, 255)
    LIGHTGOLDENRODYELLOW = (250, 250, 210)
    LIGHTGREEN = (144, 238, 144)
    LIGHTPINK = (255, 182, 193)
    LIGHTSALMON = (255, 160, 122)
    LIGHTSEAGREEN = (32, 178, 170)
    LIGHTSKYBLUE = (135, 206, 250)
    LIGHTSLATEGRAY = (119, 136, 153)
    LIGHTSTEELBLUE = (176, 196, 222)
    LIMEGREEN = (50, 205, 50)
    LINEN = (250, 240, 230)
    MEDIUMAQUAMARINE = (102, 205, 170)
    MEDIUMBLUE = (0, 0, 205)
    MEDIUMORCHID = (186, 85, 211)
    MEDIUMPURPLE = (147, 112, 219)
    MEDIUMSEAGREEN = (60, 179, 113)
    MEDIUMSLATEBLUE = (123, 104, 238)
    MEDIUMSPRINGGREEN = (0, 250, 154)
    MEDIUMTURQUOISE = (72, 209, 204)
    MEDIUMVIOLETRED = (199, 21, 133)
    MIDNIGHTBLUE = (25, 25, 112)
    MINTCREAM = (245, 255, 250)
    OLDLACE = (253, 245, 230)
    OLIVEDRAB = (107, 142, 35)
    PALEGOLDENROD = (238, 232, 170)
    PALETURQUOISE = (175, 238, 238)
    PALEVIOLETRED = (219, 112, 147)
    PERU = (205, 133, 63)
    PLUM = (221, 160, 221)
    POWDERBLUE = (176, 224, 230)
    REBECCAPURPLE = (102, 51, 153)
    ROSYBROWN = (188, 143, 143)
    ROYALBLUE = (65, 105, 225)
    SALMON = (250, 128, 114)
    SANDYBROWN = (244, 164, 96)
    SEAGREEN = (46, 139, 87)
    SEASHELL = (255, 245, 238)
    SIENNA = (160, 82, 45)
    SKYBLUE = (135, 206, 235)
    SLATEBLUE = (106, 90, 205)
    SLATEGRAY = (112, 128, 144)
    SNOW = (255, 250, 250)
    SPRINGGREEN = (0, 255, 127)
    STEELBLUE = (70, 130, 180)
    TAN = (210, 180, 140)
    THISTLE = (216, 191, 216)
    TURQUOISE = (64, 224, 208)
    VIOLET = (238, 130, 238)
    WHEAT = (245, 222, 179)
    WHITESMOKE = (245, 245, 245)
    YELLOWGREEN = (154, 205, 50)
    UKRAINE = "POOP"