import pygame
import copy

from .color import Color_Type, Color

class Flow:
    NOFLOW = 0
    FLOW = 1
    

class Gradient:
    # Константы направлений остаются без изменений
    TO_RIGHT = 'to right'
    TO_LEFT = 'to left'
    TO_TOP = 'to top'
    TO_BOTTOM = 'to bottom'
    TO_TOP_RIGHT = 'to top right'
    TO_TOP_LEFT = 'to top left'
    TO_BOTTOM_RIGHT = 'to bottom right'
    TO_BOTTOM_LEFT = 'to bottom left'

    CENTER = 'center'
    TOP_CENTER = 'top center'
    TOP_LEFT = 'top left'
    TOP_RIGHT = 'top right'
    BOTTOM_CENTER = 'bottom center'
    BOTTOM_LEFT = 'bottom left'
    BOTTOM_RIGHT = 'bottom right'

    def __init__(self, colors, type='linear', direction=TO_RIGHT, transparency=None):
        self.colors = self._validate_colors(colors)
        self.type = type
        self.direction = direction
        self._validate_type_direction()
        self.transparency = transparency

    def _validate_type_direction(self):
        
        linear_directions = [
            Gradient.TO_RIGHT, Gradient.TO_LEFT, Gradient.TO_TOP, Gradient.TO_BOTTOM,
            Gradient.TO_TOP_RIGHT, Gradient.TO_TOP_LEFT, Gradient.TO_BOTTOM_RIGHT, Gradient.TO_BOTTOM_LEFT
        ]
        radial_directions = [
            Gradient.CENTER, Gradient.TOP_CENTER, Gradient.TOP_LEFT, Gradient.TOP_RIGHT,
            Gradient.BOTTOM_CENTER, Gradient.BOTTOM_LEFT, Gradient.BOTTOM_RIGHT
        ]
        if self.type not in ['linear', 'radial']:
            raise ValueError(f"Gradient type '{self.type}' is not supported. Choose 'linear' or 'radial'.")
        if self.type == 'linear':
            if self.direction not in linear_directions and not (isinstance(self.direction, str) and self.direction.endswith('deg')):
                raise ValueError(f"Linear gradient direction '{self.direction}' is not supported.")
        elif self.type == 'radial':
            if self.direction not in radial_directions:
                raise ValueError(f"Radial gradient direction '{self.direction}' is not supported.")

    def with_transparency(self, transparency):
        return Gradient(self.colors, self.type, self.direction, transparency)

    def apply_gradient(self, surface):
        if self.type == 'linear':
            surface = self._apply_linear_gradient(surface)
        elif self.type == 'radial':
            surface = self._apply_radial_gradient(surface)
        if self.transparency:
            surface.set_alpha(self.transparency)
        return surface

    def _apply_linear_gradient(self, surface):
        """Применяет линейный градиент к поверхности с предвычислением цветов."""
        width, height = surface.get_size()
        width, height = surface.get_size()
        if len(self.colors) < 2:
            raise ValueError("Градиент должен содержать как минимум два цвета.")

        if len(self.colors) == 2:
            # Оптимизация для двух цветов
            start_color, end_color = self.colors
            steps = 256
            precomputed_colors = [
                self._interpolate_color(start_color, end_color, i / (steps - 1))
                for i in range(steps)
            ]

            def get_progress(x, y):
                if self.direction == Gradient.TO_RIGHT:
                    return x / (width - 1) if width > 1 else 0
                elif self.direction == Gradient.TO_LEFT:
                    return 1 - (x / (width - 1)) if width > 1 else 0
                elif self.direction == Gradient.TO_BOTTOM:
                    return y / (height - 1) if height > 1 else 0
                elif self.direction == Gradient.TO_TOP:
                    return 1 - (y / (height - 1)) if height > 1 else 0
                # Другие направления аналогично

            for x in range(width):
                for y in range(height):
                    progress = get_progress(x, y)
                    index = int(progress * (steps - 1))
                    color = precomputed_colors[index]
                    surface.set_at((x, y), color)
        else:

            # Задаём количество шагов для предвычисления (256 — хороший баланс скорости и качества)
            steps = 256
            precomputed_colors = []
            
            # Предвычисляем цвета для всех шагов
            for i in range(steps):
                progress = i / (steps - 1)  # Прогресс от 0 до 1
                color = self._get_color_at_progress(progress)
                precomputed_colors.append(color)

        # Функция для вычисления прогресса пикселя в зависимости от направления
        def get_progress(x, y):
            if self.direction == Gradient.TO_RIGHT:
                return x / (width - 1) if width > 1 else 0
            elif self.direction == Gradient.TO_LEFT:
                return 1 - (x / (width - 1)) if width > 1 else 0
            elif self.direction == Gradient.TO_BOTTOM:
                return y / (height - 1) if height > 1 else 0
            elif self.direction == Gradient.TO_TOP:
                return 1 - (y / (height - 1)) if height > 1 else 0
            elif self.direction == Gradient.TO_BOTTOM_RIGHT:
                diag_length = ((width - 1)**2 + (height - 1)**2)**0.5
                if diag_length == 0:
                    return 0
                proj = (x * (width - 1) + y * (height - 1)) / diag_length
                return proj / diag_length
            elif self.direction == Gradient.TO_TOP_LEFT:
                diag_length = ((width - 1)**2 + (height - 1)**2)**0.5
                if diag_length == 0:
                    return 0
                proj = ((width - 1 - x) * (width - 1) + (height - 1 - y) * (height - 1)) / diag_length
                return proj / diag_length
            elif self.direction == Gradient.TO_BOTTOM_LEFT:
                diag_length = ((width - 1)**2 + (height - 1)**2)**0.5
                if diag_length == 0:
                    return 0
                proj = ((width - 1 - x) * (width - 1) + y * (height - 1)) / diag_length
                return proj / diag_length
            elif self.direction == Gradient.TO_TOP_RIGHT:
                diag_length = ((width - 1)**2 + (height - 1)**2)**0.5
                if diag_length == 0:
                    return 0
                proj = (x * (width - 1) + (height - 1 - y) * (height - 1)) / diag_length
                return proj / diag_length
            else:
                raise ValueError(f"Неподдерживаемое направление градиента: {self.direction}")

        # Заполняем поверхность предвычисленными цветами
        for x in range(width):
            for y in range(height):
                progress = get_progress(x, y)
                # Выбираем индекс цвета из предвычисленного массива
                index = int(progress * (steps - 1))
                color = precomputed_colors[index]
                surface.set_at((x, y), color)
        
        return surface

    def _get_color_at_progress(self, progress):
        """Возвращает интерполированный цвет для заданного прогресса через все цвета градиента."""
        if len(self.colors) == 1:
            return self.colors[0]
        
        num_segments = len(self.colors) - 1
        segment = progress * num_segments
        index = int(segment)
        
        # Если прогресс на границе или за ней, возвращаем последний цвет
        if index >= num_segments:
            return self.colors[-1]
        
        # Интерполируем между двумя соседними цветами
        local_progress = segment - index
        color1 = self.colors[index]
        color2 = self.colors[index + 1]
        return self._interpolate_color(color1, color2, local_progress)

    def _get_radial_center(self, width, height):
        """Определяет координаты центра градиента в зависимости от направления."""
        if self.direction == Gradient.CENTER:
            return (width // 2, height // 2)
        elif self.direction == Gradient.TOP_CENTER:
            return (width // 2, 0)
        elif self.direction == Gradient.TOP_LEFT:
            return (0, 0)
        elif self.direction == Gradient.TOP_RIGHT:
            return (width - 1, 0)
        elif self.direction == Gradient.BOTTOM_CENTER:
            return (width // 2, height - 1)
        elif self.direction == Gradient.BOTTOM_LEFT:
            return (0, height - 1)
        elif self.direction == Gradient.BOTTOM_RIGHT:
            return (width - 1, height - 1)
        else:
            raise ValueError(f"Unsupported radial direction: {self.direction}")

    def _apply_radial_gradient(self, surface):
        """Применяет радиальный градиент с использованием минимального набора цветов."""
        # Определяем количество шагов для "минимального варианта" градиента
        steps = 256
        # Создаем список цветов заранее
        colors = [self._get_color_at_progress(i / (steps - 1)) for i in range(steps)]
        
        width, height = surface.get_size()
        # Определяем центр в зависимости от направления
        center_x, center_y = self._get_radial_center(width, height)
        # Вычисляем максимальное расстояние до углов для точного масштабирования
        corners = [(0, 0), (width - 1, 0), (width - 1, height - 1), (0, height - 1)]
        max_radius = max(((center_x - cx)**2 + (center_y - cy)**2)**0.5 for cx, cy in corners)
        
        # Обработка вырожденного случая
        if max_radius == 0:
            surface.fill(self.colors[0])
            return surface

        # Применяем градиент к каждому пикселю, используя предвычисленные цвета
        for x in range(width):
            for y in range(height):
                distance = ((x - center_x)**2 + (y - center_y)**2)**0.5
                progress = min(distance / max_radius, 1.0)  # Ограничиваем прогресс до 1.0
                index = int(progress * (steps - 1))
                color = colors[index]
                surface.set_at((x, y), color)
        return surface
    def _validate_colors(self, colors):
        if not isinstance(colors, (list, tuple)):
            raise ValueError("Цвета градиента должны быть списком или кортежем.")

        validated_colors = []
        for color in colors:
            if isinstance(color, str):
                # Преобразуем строку в верхний регистр и получаем кортеж из Color
                color_tuple = getattr(Color, color.upper(), None)
                if color_tuple and isinstance(color_tuple, tuple) and len(color_tuple) == 3:
                    validated_colors.append(color_tuple)
                else:
                    raise ValueError(f"Неподдерживаемое название цвета: '{color}'. Используйте кортеж RGB или имя цвета из класса Color.")
            elif isinstance(color, (tuple, list)) and len(color) == 3 and all(isinstance(c, int) and 0 <= c <= 255 for c in color):
                # Если это кортеж или список из трёх чисел в диапазоне 0-255
                validated_colors.append(tuple(color))
            else:
                raise ValueError("Каждый цвет должен быть кортежем из 3 целых чисел (RGB) или допустимым названием цвета.")

        return validated_colors
    def _interpolate_color(self, color1, color2, progress):
        """Линейная интерполяция между двумя цветами."""
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        r = int(r1 + (r2 - r1) * progress)
        g = int(g1 + (g2 - g1) * progress)
        b = int(b1 + (b2 - b1) * progress)
        return (r, g, b)

    def invert(self, new_direction=None):
        # Оставляем без изменений
        if new_direction is None:
            if self.type == 'linear':
                if isinstance(self.direction, str) and self.direction.endswith('deg'):
                    try:
                        angle = int(self.direction[:-3])
                    except ValueError:
                        raise ValueError("Некорректный формат угла.")
                    new_angle = (angle + 180) % 360
                    new_direction = f"{new_angle}deg"
                else:
                    mapping = {
                        Gradient.TO_RIGHT: Gradient.TO_LEFT,
                        Gradient.TO_LEFT: Gradient.TO_RIGHT,
                        Gradient.TO_TOP: Gradient.TO_BOTTOM,
                        Gradient.TO_BOTTOM: Gradient.TO_TOP,
                        Gradient.TO_TOP_RIGHT: Gradient.TO_BOTTOM_LEFT,
                        Gradient.TO_BOTTOM_LEFT: Gradient.TO_TOP_RIGHT,
                        Gradient.TO_TOP_LEFT: Gradient.TO_BOTTOM_RIGHT,
                        Gradient.TO_BOTTOM_RIGHT: Gradient.TO_TOP_LEFT
                    }
                    new_direction = mapping.get(self.direction)
                    if new_direction is None:
                        raise ValueError(f"Не поддерживается инвертирование направления: {self.direction}")
            elif self.type == 'radial':
                mapping = {
                    Gradient.CENTER: Gradient.CENTER,
                    Gradient.TOP_CENTER: Gradient.BOTTOM_CENTER,
                    Gradient.BOTTOM_CENTER: Gradient.TOP_CENTER,
                    Gradient.TOP_LEFT: Gradient.BOTTOM_RIGHT,
                    Gradient.BOTTOM_RIGHT: Gradient.TOP_LEFT,
                    Gradient.TOP_RIGHT: Gradient.BOTTOM_LEFT,
                    Gradient.BOTTOM_LEFT: Gradient.TOP_RIGHT
                }
                new_direction = mapping.get(self.direction)
                if new_direction is None:
                    raise ValueError(f"Не поддерживается инвертирование направления: {self.direction}")
        return Gradient(self.colors, self.type, new_direction)
class Style:
    def __init__(self,hover_style=None,**kwargs):
        """
        __init__(self,**kwargs)

        Initializing a new Style object

        Supported properties:

        - bgcolor: color of the widget's background. Should be a tuple of 3 integers or a gradient object.
        - fontcolor: color of the widget's text. Should be a tuple of 3 integers.
        - bordercolor: color of the widget's border. Should be a tuple of 3 integers or a gradient object.
        - borderwidth: width of the widget's border. Should be an integer.
        - borderradius: radius of the widget's corners. Should be an integer.
        - fontname: name of the font. Should be a string.
        - fontsize: size of the font. Should be an integer.

        Raises ValueError if the property value is incorrect.

        :param kwargs: keyword arguments containing style properties
        :return: None
        """

        self.type = type

        self.bgcolor = (120,120,120)
        self.borderwidth = 1
        self.bordercolor = (0,0,0)
        self.borderradius = 0
        self._kwargs_for_copy = kwargs
        self.fontname = "Arial"
        self.fontsize = 20
        self.fontcolor=(50,50,50)
        self.secondarycolor = (130,30,30)
        self._kwargs_getter(**kwargs)
        self._hover = hover_style
        self.text_align_x = Align.CENTER
        self.text_align_y = Align.CENTER
        self.transparency = None
        self.bgimage = None
        self.parent = None
        self.flow = 0
    def copy(self):
        return copy.copy(self._kwargs_for_copy)
    def _kwargs_getter(self,object="default",**kwargs):
        if object == "default":
            object = self
        for name,value in kwargs.items():
            if name=="bgcolor":
                if isinstance(value, Gradient):
                    self.bgcolor = value
                elif value == Color_Type.TRANSPARENT:
                    self.bgcolor = value
                elif isinstance(value, (tuple, list)) and len(value) == 3 and all(isinstance(c, int) for c in value) or isinstance(value, (tuple, list)) and len(value) == 4 and all(isinstance(c, int) for c in value):
                    self.bgcolor = tuple(value)
                elif isinstance(value, str):
                    color_tuple = getattr(Color, value.upper(), None)
                    if color_tuple:
                        self.bgcolor = color_tuple
                    else:
                        raise ValueError(f"Invalid color name '{value}' for bgcolor. Use RGB tuple, Gradient object, 'TRANSPARENT', or a valid color name from Color class.")
                else:
                    raise ValueError("bgcolor must be a tuple of 3/4 integers (RGB/A), a Gradient object, 'TRANSPARENT', or a color name string.")

            if name=="fontcolor":
                if isinstance(value, (tuple, list)) and len(value) == 3 and all(isinstance(c, int) for c in value):
                    self.fontcolor = tuple(value)
                elif isinstance(value, str):
                    color_tuple = getattr(Color, value.upper(), None)
                    if color_tuple:
                        self.fontcolor = color_tuple
                    else:
                        raise ValueError(f"Invalid color name '{value}' for fontcolor. Use RGB tuple or a valid color name from Color class.")
                else:
                    raise ValueError("fontcolor must be a tuple of 3 integers (RGB) or a color name string.")

            if name=="bordercolor":
                if isinstance(value, Gradient):
                    self.bordercolor = value
                elif value == Color_Type.TRANSPARENT:
                    self.bordercolor = value
                elif isinstance(value, (tuple, list)) and len(value) == 3 and all(isinstance(c, int) for c in value):
                    self.bordercolor = tuple(value)
                elif isinstance(value, str):
                    color_tuple = getattr(Color, value.upper(), None)
                    if color_tuple:
                        self.bordercolor = color_tuple
                    else:
                        raise ValueError(f"Invalid color name '{value}' for bordercolor. Use RGB tuple, Gradient object, 'TRANSPARENT', or a valid color name from Color class.")
                else:
                    raise ValueError("bordercolor must be a tuple of 3 integers (RGB), a Gradient object, 'TRANSPARENT', or a color name string.")

            if name=="secondarycolor":
                if isinstance(value, (tuple, list)) and len(value) == 3 and all(isinstance(c, int) for c in value):
                    self.secondarycolor = tuple(value)
                else:
                    raise ValueError("secondarycolor must be a tuple of 3 integers (RGB).")

            if name=="borderwidth":
                if isinstance(value,int):
                    self.borderwidth = value
                else:
                    raise ValueError("borderwidth needed to be NUMBER.")
            if name=="borderradius":
                if isinstance(value,int):
                    self.borderradius = value
                else:
                    raise ValueError("borderradius needed to be NUMBER.")
            if name =="fontname":
                if isinstance(value,str):
                    self.fontname = value
                else:
                    raise ValueError("fontname needed to be STRING.")
            if name == "fontsize":
                if isinstance(value,int):
                    self.fontsize = value
                else:
                    raise ValueError("fontsize needed to be NUMBER.")
            if name == "text_align_x":
                if isinstance(value,int):
                    self.text_align_x = value
                else:
                    raise ValueError("text_align_x needed to be NUMBER.")
            if name == "text_align_y":
                if isinstance(value,int):
                    self.text_align_y = value
                else:
                    raise ValueError("text_align_y needed to be NUMBER.")
            if name == "transparency":
                if isinstance(value,int):
                    if value >= 0 and value <= 255:
                        self.transparency = value
                    else:
                        raise ValueError("transpency needed to be NUMBER between 0 and 255.")
                else:
                    raise ValueError("transpency needed to be NUMBER.")
            if name == "bgimage":
                if isinstance(value,str):
                    self.bgimage = value
                else:
                    raise ValueError("bgimage needed to be STRING.")
            if name == "flow":
                if isinstance(value,int):
                    self.flow = value
                else:
                    raise ValueError("flow needed to be NUMBER.")
    @property
    def hover(self):
        return self._hover
    @hover.setter
    def hover(self,value):
        self._hover = value
    def __call__(self,hover_style=None,**kwargs):
        style = copy.copy(self)
        style._kwargs_getter(**kwargs)
        style._hover = hover_style
        return style

class Align():
    CENTER = 101010
    LEFT = 111111
    RIGHT = 121212
    TOP = 123122
    BOTTOM = 233121
    
class Theme:
    DEFAULT = Style()
    FIRE = Style(bgcolor=Color.ORANGERED, fontcolor=Color.YELLOW, bordercolor=Color.RED)
    CRIMSON = Style(bgcolor=Color.MAROON, fontcolor=Color.WHITE, bordercolor=Color.RED) 
    ROSE = Style(bgcolor=Color.MISTYROSE, fontcolor=Color.MAROON, bordercolor=Color.PINK)
    DARK = Style(bgcolor=Color.DARKGRAY, fontcolor=Color.LIGHTGRAY, bordercolor=Color.LIGHTGRAY)
    LIGHT = Style(bgcolor=Color.LIGHTGRAY, fontcolor=Color.DARKGRAY, bordercolor=Color.DARKGRAY)
    CUSTOM = Style(bgcolor=Color.BEIGE, fontcolor=Color.MAROON, bordercolor=Color.MAROON)
    PASTEL = Style(bgcolor=Color.LAVENDERBLUSH, fontcolor=Color.PURPLE, bordercolor=Color.PINK)
    VIBRANT = Style(bgcolor=Color.CYAN, fontcolor=Color.MAGENTA, bordercolor=Color.YELLOW)
    NATURE = Style(bgcolor=Color.PALEGREEN, fontcolor=Color.BROWN, bordercolor=Color.OLIVE)
    RETRO = Style(bgcolor=Color.LIGHTYELLOW, fontcolor=Color.BLUE, bordercolor=Color.RED)
    MINIMALIST = Style(bgcolor=Color.WHITE, fontcolor=Color.BLACK, bordercolor=Color.SILVER, borderradius=50)
    FUTURISTIC = Style(bgcolor=Color.NAVY, fontcolor=Color.AQUA, bordercolor=Color.LIME)
    WARM = Style(bgcolor=Color.PEACHPUFF, fontcolor=Color.CHOCOLATE, bordercolor=Color.ORANGE)
    COOL = Style(bgcolor=Color.LAVENDER, fontcolor=Color.TEAL, bordercolor=Color.SILVERGRAY)
    MONOCHROME = Style(bgcolor=Color.LIGHTBLACK, fontcolor=Color.SILVER, bordercolor=Color.GRAY)
    GOLD = Style(bgcolor=Color.LIGHTYELLOW, fontcolor=Color.MAROON, bordercolor=Color.GOLD)
    DEEPBLUE = Style(bgcolor=Color.NAVY, fontcolor=Color.LIGHTGRAY, bordercolor=Color.BLUE)
    FORESTGREEN = Style(bgcolor=Color.OLIVE, fontcolor=Color.LIGHTYELLOW, bordercolor=Color.GREEN)
    SUNSETORANGE = Style(bgcolor=Color.ORANGERED, fontcolor=Color.LIGHTYELLOW, bordercolor=Color.ORANGE)
class xTheme():
    PASTEL_RAINBOW = Style(bgcolor=(240, 224, 255), fontcolor=(132, 112, 255), bordercolor=(255, 192, 203))
    NEON = Style(bgcolor=(0, 0, 0), fontcolor=(255, 0, 255), bordercolor=(0, 255, 255))
    OCEAN_BLUE = Style(bgcolor=(240, 248, 255), fontcolor=(0, 70, 120), bordercolor=(70, 130, 180)) 
    GRAYSCALE = Style(bgcolor=(220, 220, 220), fontcolor=(80, 80, 80), bordercolor=(150, 150, 150))
    SPRING = Style(bgcolor=(245, 255, 245), fontcolor=(0, 100, 0), bordercolor=(144, 238, 144)) 
    AUTUMN = Style(bgcolor=(253, 245, 230), fontcolor=(160, 82, 45), bordercolor=(255, 140, 0)) 
    WINTER = Style(bgcolor=(248, 248, 255), fontcolor=(70, 130, 180), bordercolor=(176, 196, 222)) 
    CYBERPUNK = Style(
        bgcolor=Gradient(colors=[(20, 20, 20), (50, 0, 60)],type='linear',direction=Gradient.TO_BOTTOM),
        fontcolor=(255, 0, 100),
        bordercolor=(0, 255, 200),
        borderradius=10,
        borderwidth=1,
        fontsize=22
    )
    MATERIAL_LIGHT = Style(
        bgcolor=(250, 250, 250),  
        fontcolor=(33, 33, 33),   
        bordercolor=(200, 200, 200), 
        borderradius=4,
        borderwidth=1,
        fontsize=20
    )
    
    MATERIAL_DARK = Style(
        bgcolor=(18, 18, 18),      
        fontcolor=(255, 255, 255),
        bordercolor=(60, 60, 60), 
        borderradius=4,
        borderwidth=1,
        fontsize=20
    )
    SUNSET = Style(
        bgcolor=Gradient(colors=[(255, 94, 77), (255, 195, 113)], type='linear', direction=Gradient.TO_BOTTOM),
        fontcolor=(255, 255, 255),
        bordercolor=(200, 100, 50),
        borderradius=10,
        borderwidth=2,
        fontsize=22
    )
    TROPICAL = Style(
        bgcolor=Gradient(colors=[(64, 224, 208), (32, 178, 170)], type='linear', direction=Gradient.TO_RIGHT),
        fontcolor=(10, 10, 10),
        bordercolor=(0, 128, 128),
        borderradius=5,
        borderwidth=2,
        fontsize=20
    )
    MYSTIC = Style(
        bgcolor=Gradient(colors=[(72, 61, 139), (123, 104, 238)], type='linear', direction=Gradient.TO_BOTTOM),
        fontcolor=(230, 230, 250),
        bordercolor=(75, 0, 130),
        borderradius=8,
        borderwidth=2,
        fontsize=21
    )
    VINTAGE = Style(
        bgcolor=Gradient(colors=[(222, 184, 135), (210, 180, 140)], type='linear', direction=Gradient.TO_RIGHT),
        fontcolor=(101, 67, 33),
        bordercolor=(160, 82, 45),
        borderradius=12,
        borderwidth=3,
        fontsize=20
    )
    AURORA = Style(
        bgcolor=Gradient(colors=[(0, 255, 255), (255, 0, 255), (0, 0, 139)], type='radial', direction=Gradient.CENTER),
        fontcolor=(255, 255, 255),
        bordercolor=(138, 43, 226),
        borderradius=15,
        borderwidth=3,
        fontsize=23
    )
    GALACTIC = Style(
        bgcolor=Gradient(colors=[(10, 10, 30), (30, 30, 60)], type='linear', direction=Gradient.TO_RIGHT),
        fontcolor=(57, 255, 20),
        bordercolor=(57, 100, 20),
        borderradius=8,
        borderwidth=1,
        fontsize=20
    )
    ELEGANT = Style(
        bgcolor=Gradient(colors=[(245, 245, 245), (220, 220, 220)], type='linear', direction=Gradient.TO_BOTTOM),
        fontcolor=(0, 0, 0),
        bordercolor=(211, 211, 211),
        borderradius=20,
        borderwidth=1,
        fontsize=22
    )
    DREAMY = Style(
        bgcolor=Gradient(colors=[(255, 182, 193), (255, 240, 245)], type='linear', direction=Gradient.TO_TOP),
        fontcolor=(199, 21, 133),
        bordercolor=(255, 105, 180),
        borderradius=15,
        borderwidth=2,
        fontsize=21
    )
    RED = Style(
        bgcolor=Gradient(
            colors=[(230, 50, 50), (255, 120, 80)], 
            type='linear',
            direction=Gradient.TO_BOTTOM
        ),
        fontcolor=(255, 255, 255),     
        bordercolor=(220, 20, 60),      
        borderradius=10,               
        borderwidth=2,
        fontsize=22
    )