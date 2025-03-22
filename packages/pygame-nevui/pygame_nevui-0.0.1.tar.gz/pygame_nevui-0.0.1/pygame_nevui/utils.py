import pygame
import time as tt
import numpy as np
class RoundedSurface():
    @staticmethod
    def create(surface:pygame.SurfaceType, radius:int):
        """
        Создает копию surface с закругленными углами.

        Args:
            surface: Исходный Surface.
            radius: Радиус закругления углов.

        Returns:
            Surface с закругленными углами.
        """
        rect = surface.get_rect()
        a_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        a_surf.fill((0, 0, 0, 0))
        pygame.draw.rect(a_surf, (255, 255, 255, 255), rect, border_radius=radius)
        new = surface.copy()
        new.blit(a_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        return new
class Mouse:
    STILL= 0
    FDOWN= 1
    DOWN = 2
    UP= 3
    def __init__(self):
        self._pos = (0,0)
        
        self._left = 0
        self._right = 0
        self._center = 0
        
        self._left_up = False
        self._right_up = False
        self._center_up = False
        
        self._left_fdown = False
        self._right_fdown = False
        self._center_fdown = False
        
        self._left_down = False
        self._right_down = False
        self._center_down = False
        
        self._left_still = False
        self._right_still = False
        self._center_still = False
    
    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self,value):
        self._pos = value
    
    @property
    def left(self):
        return self._left
    @left.setter
    def left(self,value):
        self._left = value
    
    @property
    def right(self):
        return self._right
    @right.setter
    def right(self,value):
        self._right = value
    
    @property
    def center(self):
        return self._center
    @center.setter
    def center(self,value):
        self._center = value
    
    @property
    def left_up(self):
        return self._left_up
    @left_up.setter
    def left_up(self,value):
        self._left_up = value
    
    @property
    def left_fdown(self):
        return self._left_fdown
    @left_fdown.setter
    def left_fdown(self,value):
        self._left_fdown = value
    
    @property
    def left_down(self):
        return self._left_down
    @left_down.setter
    def left_down(self,value):
        self._left_down = value
    
    @property
    def left_still(self):
        return self._left_still
    @left_still.setter
    def left_still(self,value):
        self._left_still = value
    
    @property
    def right_up(self):
        return self._right_up
    @right_up.setter
    def right_up(self,value):
        self._right_up = value
    
    @property
    def right_fdown(self):
        return self._right_fdown
    @right_fdown.setter
    def right_fdown(self,value):
        self._right_fdown = value
    
    @property
    def right_down(self):
        return self._right_down
    @right_down.setter
    def right_down(self,value):
        self._right_down = value
    
    @property
    def right_still(self):
        return self._right_still
    @right_still.setter
    def right_still(self,value):
        self._right_still = value
    
    @property
    def center_up(self):
        return self._center_up
    @center_up.setter
    def center_up(self,value):
        self._center_up = value
    
    @property
    def center_fdown(self):
        return self._center_fdown
    @center_fdown.setter
    def center_fdown(self,value):
        self._center_fdown = value
    
    @property
    def center_down(self):
        return self._center_down
    @center_down.setter
    def center_down(self,value):
        self._center_down = value
    
    @property
    def center_still(self):
        return self._center_still
    @center_still.setter
    def center_still(self,value):
        self._center_still = value
    
    @property
    def any_down(self):
        return self.left_down or self.right_down or self.center_down
    @property
    def any_fdown(self):
        return self.left_fdown or self.right_fdown or self.center_fdown
    @property
    def any_up(self):
        return self.left_up or self.right_up or self.center_up
    
    def updateKeys(self,is_clicked,key):
        State = key
        if is_clicked:
            if State == self.FDOWN:
                State = self.DOWN
            if State != self.DOWN:
                State = self.FDOWN
        else:
            if State == self.DOWN:
                State = self.UP
            else:
                State = self.STILL
        return State
    def set_states(self,state):
        up = False
        fd = False
        dw = False
        st = False
        if state == self.STILL:
            st = True
        elif state == self.FDOWN:
            fd = True
        elif state == self.DOWN:
            dw = True
        elif state == self.UP:
            up = True
        return up,fd,dw,st
    def update(self):
        self.pos = pygame.mouse.get_pos()
        keys = pygame.mouse.get_pressed()
        self.left = self.updateKeys(keys[0],self.left)
        self.left_up,self.left_fdown,self.left_down,self.left_still = self.set_states(self.left)
        self.right = self.updateKeys(keys[2],self.right)
        self.right_up,self.right_fdown,self.right_down,self.right_still = self.set_states(self.right)
        self.center = self.updateKeys(keys[1],self.center)
        self.center_up,self.center_fdown,self.center_down,self.center_still = self.set_states(self.center)

class Time():
    def __init__(self):
        """
        Initializes the Time object with default delta time, frames per second (fps),
        and timestamps for time calculations.

        Attributes:
            delta_time/dt (float): The time difference between the current and last frame.
            fps (int): Frames per second, calculated based on delta time.
            now (float): The current timestamp.
            after (float): The timestamp of the previous frame.
        """
        self._delta_time = np.float16(1.0)
        self._fps = np.int16()
        self._now = tt.time()
        self._after = tt.time()
    @property
    def delta_time(self):
        return float(self._delta_time)
    @property
    def dt(self):
        return float(self._delta_time)
    @property
    def fps(self):
        return int(self._fps)
    def _calculate_delta_time(self):
        self._now = tt.time()
        self._delta_time = np.float16((self._now - self._after))
        self._after = self._now
    def _calculate_fps(self):
        try:
            self._fps = np.int16(int(1 / (self.delta_time)))
        except:
            self._fps = 0
    def update(self):
        self._calculate_delta_time()
        self._calculate_fps()

class Key:
    STILL= 0
    FDOWN= 1
    DOWN = 2
    UP= 3
    def __init__(self,key):
        self.key_value = key
        self.up = False
        self.fdown = False
        self.down = False
        self.still = False
        self.state = 0
    def updateKeys(self, is_clicked, key_state):
        if is_clicked:
            if key_state == self.STILL or key_state == self.UP:
                return self.FDOWN
            return self.DOWN
        else:
            if key_state == self.DOWN or key_state == self.FDOWN:
                return self.UP
            return self.STILL
    def set_states(self,state):
        up = False
        fd = False
        dw = False
        st = False
        if state == self.STILL:
            st = True
        elif state == self.FDOWN:
            fd = True
        elif state == self.DOWN:
            dw = True
        elif state == self.UP:
            up = True
        return up,fd,dw,st
    def update(self,keys):
        self.state = self.updateKeys(keys[self.key_value],self.state)
        self.up,self.fdown,self.down,self.still = self.set_states(self.state)
        

class Keyboard:
    def __init__(self,keys:list[Key]=[],function_on_click=None):
        self.keys = keys
        self.fun = function_on_click
        self.pg_keys = pygame.key.get_pressed()
        keyboards_list.append(self)
    def is_pressed(self):
        for key in self.keys:
            if key.state > 0: return True
        return False
    def is_up(self):
        for key in self.keys:
            if key.state == 3: return True
        return False
    def is_fdown(self):
        for key in self.keys:
            if key.state == 1: return True
        return False

    def update(self):
        self.pg_keys = pygame.key.get_pressed()
        for key in self.keys:
            key.update(self.pg_keys)

time = Time()
mouse = Mouse()

keyboards_list = []

class Event:
    DRAW = 0
    UPDATE = 1
    RESIZE = 2
    RENDER = 3
    def __init__(self,type,function,*args, **kwargs):
        """
        Initializes an Event object with a type, function, and optional arguments.

        Parameters:
        type (int): The type of event, indicating the kind of operation.
        function (callable): The function to be executed when the event is triggered.
        *args: Variable length argument list to be passed to the function.
        **kwargs: Arbitrary keyword arguments to be passed to the function.
        """
        self.type = type
        
        self._function = function
        self._args = args
        self._kwargs = kwargs
    def __call__(self,*args, **kwargs):
        if args: self._args = args
        if kwargs: self._kwargs = kwargs
        self._function(*self._args, **self._kwargs)

class InputType():
    NUMBERS = "0123456789"
    LETTERS_ENG = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
    LETTERS_RUS = "йцукенгшщзхъфывапролджэячсмитьбюЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ"
    BASIC_SYMBOLS = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

    LETTERS_UKR = "ієїґа-яІЄЇҐ"+LETTERS_RUS
    LETTERS_BEL = "абвгдеёжзійклмнопрстуўфхцчшыьэюяАБВГДЕЁЖЗІЙКЛМНОПРСТУЎФХЦЧШЫЬЭЮЯ"
    LETTERS_GER = "äöüÄÖÜß" + LETTERS_ENG
    LETTERS_FR = "àâçéèêëîïôûüÿÀÂÇÉÈÊËÎÏÔÛÜŸæœÆŒ" + LETTERS_ENG
    LETTERS_ES = "áéíóúüñÁÉÍÓÚÜÑ" + LETTERS_ENG
    LETTERS_IT = "àèéìòóùÀÈÉÌÒÓÙ" + LETTERS_ENG
    LETTERS_PL = "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ" + LETTERS_ENG
    LETTERS_PT = "àáâãçéêíóôõúüÀÁÂÃÇÉÊÍÓÔÕÚÜ" + LETTERS_ENG
    LETTERS_GR = "αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
    LETTERS_AR = "ءآأؤإئابةتثجحخدذرزسشصضطظعغفقكلمنهوي"
    LETTERS_JP = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
    LETTERS_CN = "的一是不了人我在有他这为之大来以个中上们"

    WHITESPACE = " \t\n\r\f\v"
    SEPARATORS_COMMON = ",.;:?!"
    SEPARATORS_BRACKETS = "()[]{}"
    SEPARATORS_QUOTES = "\"'`«»"

    MATH_SYMBOLS_BASIC = "+-*/="
    MATH_SYMBOLS_ADVANCED = "><≤≥≠≈±√∑∫"
    MATH_SYMBOLS_CURRENCY = "€£¥₽$"
    MATH_SYMBOLS_GREEK = "πΩΣΔΘΛΞΦΨΓ"

    URL_SYMBOLS = "-._~:/?#[]@!$&'()*+,;=%abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    EMAIL_SYMBOLS = "-._%+-@abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

    HEX_DIGITS = "0123456789abcdefABCDEF"

    PUNCTUATION_MARKS = ",.;:?!—…"
    DASHES = "-—‒–"
    APOSTROPHE = "'"

    CONTROL_CHARS = "".join(chr(i) for i in range(32))

    MARKDOWN_SYMBOLS = "*_`~>#+![]()="
    COMBINATIONS = ":-) :-( :D :P <3"
    SPECIAL_SYMBOLS = "©®™°№§"

    ALL_LETTERS = (LETTERS_ENG + LETTERS_RUS + LETTERS_UKR + LETTERS_BEL + LETTERS_GER + 
                   LETTERS_FR + LETTERS_ES + LETTERS_IT + LETTERS_PL + LETTERS_PT + 
                   LETTERS_GR + LETTERS_AR + LETTERS_JP + LETTERS_CN)
    ALL_SYMBOLS = (BASIC_SYMBOLS + SEPARATORS_COMMON + SEPARATORS_BRACKETS + SEPARATORS_QUOTES + 
                   MATH_SYMBOLS_BASIC + MATH_SYMBOLS_ADVANCED + MATH_SYMBOLS_CURRENCY + 
                   PUNCTUATION_MARKS + DASHES + APOSTROPHE + MARKDOWN_SYMBOLS + SPECIAL_SYMBOLS + 
                   MATH_SYMBOLS_GREEK)

class Input_Type(InputType):
    #Old naming
    pass

class Locale:
    """
    Manages text localization for different languages.

    The `Locale` class provides a mechanism for storing and retrieving
    text strings in various languages. It allows you to add languages,
    select the current language, and retrieve string translations for the
    selected language.

    **Usage Example:**

    ```python
    locale = Locale(["en", "ru"]) # Initialize with support for English and Russian
    locale.select_lang("en")     # Select English language
    locale["hello"] = "Hello"    # Set translation for "hello" in English
    locale.select_lang("ru")     # Switch to Russian language
    locale["hello"] = "Привет"   # Set translation for "hello" in Russian

    print(locale["hello"])       # Output: Привет (Russian selected)
    locale.select_lang("en")     # Switch back to English
    print(locale["hello"])       # Output: Hello (English selected)
    print(locale["goodbye"])    # Output: <goodbye> (no translation, placeholder)
    ```
    """
    def __init__(self, languages:list):
        self.data = {"none":{}}
        for lang in languages:
            self.add_language(lang)
        self.selected_language = "none"
    def add_language(self,lang):
        self.data[lang] = {}
        self.select_lang(lang)
    def __setitem__(self, key, value):
        self.data[self.selected_language][key] = value
      
    def __getitem__(self, key):
        lang_data = self.data.get(self.selected_language) 
        if lang_data:
            value = lang_data.get(key)
            if value is not None: return value
            else:
                default_lang_data = self.data.get("none")
                if default_lang_data:
                    default_value = default_lang_data.get(key)
                    if default_value is not None: return default_value
                return f"<{key}>"  
        else: return f"<Language '{self.selected_language}' not found>" 

    def select_lang(self,lang:str):
        if self.data.get(lang,None):
            self.selected_language = lang
    def set_items(self, lang: str, items: list[list[str, str]]):
        """
        Sets multiple translations for a specified language.

        Adds or updates translations for a set of keys and values
        within the data dictionary for the language `lang`. Temporarily
        selects the language `lang` to perform the operations and then
        restores the previously selected language.

        Args:
            lang (str): The language code for which to set the translations.
            items (list[list[str, str]]): A list of key-value pairs, where
                                         each element of the list is a list
                                         of two strings: [key, translation].
        """
        if lang not in self.data: print(f"Warning: Language '{lang}' not found. Translations will not be set."); return

        old_selected_lang = self.selected_language
        self.select_lang(lang)
        lang_data = self.data[lang]
        for item in items:
            if len(item) == 2:
                key, value = item
                lang_data[key] = value
            else: print(f"Warning: Invalid item format in 'items' list: {item}. Expected [key, value].")
        self.select_lang(old_selected_lang)

def _check_for_int(value: any, name: str = "None", raise_error: bool = True, print_error: bool = True) -> int:
    try: return int(value)
    except Exception as e:
        error_text = f"{value} is not an integer. ({name})"
        if raise_error: raise ValueError(error_text)
        elif print_error: print(error_text)
    