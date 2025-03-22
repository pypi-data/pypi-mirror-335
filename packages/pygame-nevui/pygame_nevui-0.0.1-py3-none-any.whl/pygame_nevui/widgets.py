import pygame
import numpy as np
import copy
import math
from PIL import Image
from .style import *
from .utils import *
from .color import *
from .animations import *

default_style = Theme.DEFAULT

class Widget:
    def __init__(self,size,style:Style,freedom=False):
        self.size = np.array(size,dtype=np.int32)
        self.first_update_fuctions = []
        self.style = style
        self.surface = pygame.Surface(size,flags=pygame.SRCALPHA|pygame.HWSURFACE | pygame.DOUBLEBUF)
        self.coordinates = np.array([0,0],dtype=np.float32)
        self.__is_render = True
        self.__is_active = True
        self._hovered = False
        self._anim_coordinates = [0,0]
        self._anim_coordinates_initial = [0,0]
        self._anim_coordinates_additional = [0,0]
        self._anim_opacity = None
        self._anim_opacity_value = None
        self._anim_rotation = 0
        self._anim_rotation_value = 0
        self._surface_copy_for_rotation = self.surface
        self._is_changed = True
        self._freedom = freedom
        self._text_baked = None
        self._text_surface = None
        self._text_rect = None
        
        self._resize_ratio = [1,1]
        self.animation_manager = AnimationManager()
        self._first_update = True
        
        self._events = []
        
        self.x = 0
        self.y = 0
        self.unrendered = False
    def add_event(self,event:Event):
        self._events.append(event)
    def add_on_first_update(self,fuction):
        self.first_update_fuctions.append(fuction)
    #______RENDER______________________________
    def enable_render(self):
        self.__is_render = True
        self._is_changed = True
        self.unrendered = True
    def disable_render(self):
        self.__is_render = False
        self._is_changed = True
    @property
    def render(self):
        return self.__is_render
    @render.getter
    def render(self):
        return self.__is_render
    @render.setter
    def render(self,value:bool):
        if value == True:
            self.unrendered = True
        self.__is_render = value
    #______ACTIVE______________________________
    def activate(self):
        self.__is_active = True
        self._is_changed = True
    def disactivate(self):
        self.__is_active = False
        self._is_changed = True
    @property
    def active(self):
        return self.__is_active
    @active.getter
    def active(self):
        return self.__is_active
    @active.setter
    def active(self,value:bool):
        self.__is_active = value
    #__________________________________________
    def _event_cycle(self,type:int,*args, **kwargs):
            for event in self._events:
                if event.type == type:
                    event(*args, **kwargs)
    def resize(self,_resize_ratio):
        self._is_changed = True
        self._resize_ratio = _resize_ratio
        self.surface = pygame.Surface([int(self.size[0]*self._resize_ratio[0]),int(self.size[1]*self._resize_ratio[1])],flags=pygame.SRCALPHA|pygame.HWSURFACE | pygame.DOUBLEBUF)
        self._event_cycle(Event.RESIZE)
    @property
    def style(self):
        if not self._hovered:
            return self._style
        if self._style._hover:return self._style._hover
        else: return self._style
        
    def _first_set_style(self,style:Style):
        self._style = copy.copy(style)
    @style.setter
    def style(self,style:Style):
        self._is_changed = True
        self._style = copy.copy(style)
        self.add_on_first_update(lambda:[self._first_set_style(style),print("JOPAA 2")])
        
    def draw(self):
        if not self.render:
            if self.unrendered:
                self.surface.fill((0,0,0,0))
            return
        self._event_cycle(Event.DRAW)
        #Color_Type().check_bg(self.style.bgcolor,if_transparent=lambda:self.surface.fill((0,0,0,0)),if_gradient=lambda:self.style.bgcolor(self.surface),if_value=lambda:self.surface.fill(self.style.bgcolor),bool=False)
        if self._is_changed:
            self.surface.fill((0,0,0,0))
            if self.animation_manager.anim_rotation:
                self.surface = pygame.transform.rotate(self.surface, -self.animation_manager.anim_rotation)
            if type(self) == Widget:
                self._is_changed = False
            if isinstance(self.style.bgcolor,Gradient):
                if self.style.transparency:
                    surf = pygame.Surface(self.surface.get_size(),flags=pygame.SRCALPHA)
                    self.style.bgcolor.with_transparency(self.style.transparency).apply_gradient(surf)
                    self.surface = self.surface.convert_alpha()
                    self.surface.blit(surf)
                else:
                    self.style.bgcolor.apply_gradient(self.surface)
            elif self.style.bgcolor ==Color_Type.TRANSPARENT:
                self.surface.fill((0,0,0,0))
            else:
                self.surface.fill(self.style.bgcolor,(0,0,int(self.size[0]*self._resize_ratio[0]),int(self.size[1]*self._resize_ratio[1])))
            if self.style.borderwidth > 0:
                if not self.style.bordercolor == Color_Type.TRANSPARENT:
                    surf = pygame.Surface(self.surface.get_size(),flags=pygame.SRCALPHA|pygame.HWSURFACE | pygame.DOUBLEBUF)
                    if self.style.transparency:
                        surf.set_alpha(self.style.transparency)
                    pygame.draw.rect(surf,self.style.bordercolor,[0,0,int(self.size[0]*self._resize_ratio[0]),int(self.size[1]*self._resize_ratio[1])],self.style.borderwidth,border_radius=int(self.style.borderradius))
                    self.surface.blit(surf,(0,0))
            if self.style.borderradius > 0:
                    self.surface = RoundedSurface.create(self.surface,int(self.style.borderradius))
            if type(self) == Widget:
                if self.animation_manager.anim_rotation:
                    self.surface = pygame.transform.rotate(self.surface, self.animation_manager.anim_rotation)
    def update(self,*args):
        self.animation_manager.update()
        if self.animation_manager.anim_position:
            self._anim_coordinates_initial = self.animation_manager.anim_position
            for i in range(2):self._anim_coordinates[i] = self._anim_coordinates_additional[i]+self._anim_coordinates_initial[i]
        if self.animation_manager.anim_opacity:
            self._anim_opacity_value = self.animation_manager.anim_opacity
        if self.animation_manager.anim_rotation:
            if self._anim_rotation_value != int(self.animation_manager.anim_rotation):
                center = pygame.Rect([int(self.coordinates[0]),int(self.coordinates[1])], self._surface_copy_for_rotation.get_size()).center
                self._anim_rotation_value = int(self.animation_manager.anim_rotation)
                self.surface = pygame.transform.rotate(self._surface_copy_for_rotation, self._anim_rotation_value)
                coordinates = list(self.surface.get_rect(center=center).topleft)
                for i in range(2):
                    self._anim_coordinates_additional[i] = coordinates[i]-self.coordinates[i]
                for i in range(2):self._anim_coordinates[i] = self._anim_coordinates_additional[i]+self._anim_coordinates_initial[i]
                self._is_changed = True
        if self._anim_opacity_value != self._anim_opacity:
            self._anim_opacity = self._anim_opacity_value
            self.surface.set_alpha(self._anim_opacity)
        if self._first_update:
            self._first_update = False
            for item in self.first_update_fuctions:
                item()
        self._event_cycle(Event.UPDATE)
        if mouse.left_fdown:
            self._check_for_collide_and_after()
    def bake_text(self,text,unlimited_y=False,words_indent=False,alignx=Align.CENTER,aligny=Align.CENTER,continuous=False):
        if continuous:
            self._bake_text_single_continuous(text)
            return
        if self.style.fontname == "Arial":
            renderFont = pygame.font.SysFont(self.style.fontname,int(self.style.fontsize*self._resize_ratio[1]))
        else:
            renderFont = pygame.font.Font(self.style.fontname,int(self.style.fontsize*self._resize_ratio[1]))
        is_popped  =False
        line_height = renderFont.size("a")[1]
        words = list(text)
        marg = ""
        if words_indent:
            words = text.strip().split()
            marg = " "
        lines = []
        current_line = ""
        ifnn = False
        for word in words:
            if word == '\n':
                ifnn = True
            try:
                w = word[0]+word[1]
                if w == '\ '.strip()+"n":
                    ifnn = True
            except:
                pass
            if ifnn:
                lines.append(current_line)
                current_line = ""
                test_line = ""
                text_size = 0
                ifnn = False
                continue
            test_line = current_line + word + marg
            text_size = renderFont.size(test_line)
            if text_size[0] > self.size[0]*self._resize_ratio[0]:
                lines.append(current_line)
                current_line = word + marg
            else:
                current_line = test_line
        lines.append(current_line)
        if not unlimited_y:
            while len(lines) * line_height > self.size[1] * self._resize_ratio[1]:
                lines.pop(-1)
                is_popped = True
        self._text_baked = "\n".join(lines)
        if is_popped:
            if not unlimited_y:
                self._text_baked = self._text_baked[:-3] + "..."
                justify_y = False
            else:
                justify_y = True
        else:
            justify_y = False

        self._text_surface = renderFont.render(self._text_baked, True, self.style.fontcolor)

        container_rect = self.surface.get_rect()
        text_rect = self._text_surface.get_rect()

        if alignx == Align.LEFT:
            text_rect.left = container_rect.left
        elif alignx == Align.CENTER:
            text_rect.centerx = container_rect.centerx
        elif alignx == Align.RIGHT:
            text_rect.right = container_rect.right

        if aligny == Align.TOP:
            text_rect.top = container_rect.top
        elif aligny == Align.CENTER:
            text_rect.centery = container_rect.centery
        elif aligny == Align.BOTTOM:
            text_rect.bottom = container_rect.bottom

        self._text_rect = text_rect
    def _bake_text_single_continuous(self, text):
        if self._style.fontname == "Arial":
            renderFont = pygame.font.SysFont(self._style.fontname,int(self._style.fontsize*self._resize_ratio[1]))
        else:
            renderFont = pygame.font.Font(self._style.fontname,int(self._style.fontsize*self._resize_ratio[1]))
        self.font_size = renderFont.size(text)
        self._text_surface = renderFont.render(self._entered_text, True, self.style.fontcolor)
        if not self.font_size[0]+10*self._resize_ratio[0] >= self.size[0]*self._resize_ratio[0]:
            self._text_rect = self._text_surface.get_rect(left=10*self._resize_ratio[0],centery=self.surface.get_height()/2)
        else:
            self._text_rect = self._text_surface.get_rect(right=self.surface.get_width()-10*self._resize_ratio[0],centery=self.surface.get_height()/2)
    def _check_for_collide_and_after(self):
        if pygame.Rect([self.master_coordinates[0],self.master_coordinates[1]],self.surface.get_size()).collidepoint(mouse.pos):
            self.hovered = True
        else:
            self.hovered = False
    def get_rect(self):
        return pygame.Rect(self.master_coordinates[0], self.master_coordinates[1], self.size[0]*self._resize_ratio[0], self.size[1]*self._resize_ratio[1])
class Empty_Widget(Widget):
    def __init__(self, size):
        super().__init__(size, default_style)
    def draw(self):
        pass
    
class Label(Widget):
    def __init__(self,size,text,style:Style,freedom=False,words_indent = False):
        text = str(text)
        super().__init__(size,Theme.DEFAULT,freedom)
        self._text = ""
        self.first_update_fuctions = []
        self._words_split = words_indent
        self.text = str(text)
        self.style = style
        
        self.bake_text(self._text,False,self._words_split,self.style.text_align_x,self.style.text_align_y)
        
    @property
    def hovered(self):
        return self._hovered
    @hovered.setter
    def hovered(self,value:bool):
        if self.hovered == value:
            return
        self._hovered = value
        self._is_changed = True
        self.bake_text(self._text,False,self._words_split,self.style.text_align_x,self.style.text_align_y)
    @property
    def text(self):
        return self.text
    @text.setter
    def text(self,text:str):
        self._is_changed = True
        self._text = text
        self.bake_text(text,False,self._words_split,self.style.text_align_x,self.style.text_align_y)
    def resize(self, _resize_ratio):
        self._is_changed = True
        super().resize(_resize_ratio)
        self.bake_text(self._text,False,self._words_split,self.style.text_align_x,self.style.text_align_y)
    def _first_set_style(self,style:Style):
        self._style = copy.copy(style)
    @property
    def style(self):
        if not self.hovered:
            return self._style
        if self._style._hover:return self._style._hover
        else: return self._style
    @style.setter
    def style(self,style:Style):
        self._is_changed = True
        self._style = copy.copy(style)
        self.add_on_first_update(lambda:self._first_set_style(style))
        if hasattr(self,'_text'):
            self.bake_text(self._text)
    def draw(self):
        super().draw()
        if not self.render:
            return
        if self._is_changed:
            self._is_changed = False
            self.surface.blit(self._text_surface, self._text_rect)
            if self.animation_manager.anim_rotation:
                    self.surface = pygame.transform.rotate(self.surface, self.animation_manager.anim_rotation)
        self._event_cycle(Event.RENDER)

class Button(Label):
    def __init__(self,fuction,text:str,size,style:Style=default_style,active:bool = True,throw_errors=False,freedom=False,words_indent=False):
        super().__init__(size,text,style,freedom,words_indent)
        ### Basic variables
        self.fuction = fuction
        self.active = active
        self._throw = throw_errors
        
    def update(self,*args):
        super().update(*args)
        if not self.active:
            return
        if self.hovered:
            if mouse.left_up:
                if self.fuction:
                    try:
                        self.fuction()
                    except Exception as e:
                        print(e)
                        if self._throw:
                            raise e
class CheckBox(Button):
    def __init__(self,on_change_fuction,state,size,style:Style,active:bool = True):
        super().__init__(lambda:on_change_fuction(state) if on_change_fuction else None,"",size,style)
        self._id = None
        self._check_box_group = None
        self.is_active = False
        self.state = state
        self.active = active
        self.count = 0
    def draw(self):
        super().draw()
        if not self.render:
            return
        if self.is_active:
            pygame.draw.rect(self.surface,(200,50,50),[0,0,self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]],border_radius=int(self._style.borderradius*(self._resize_ratio[0]+self._resize_ratio[1])/2))
        self._event_cycle(Event.RENDER)
        if self._is_changed:
            if self.animation_manager.anim_rotation:
                self.surface = pygame.transform.rotate(self.surface, self.animation_manager.anim_rotation)
    def _check_for_collide_and_after(self):
        if not self.active:
            return
        if pygame.Rect([self.master_coordinates[0],self.master_coordinates[1]],self.surface.get_size()).collidepoint(mouse.pos):
            if self.fuction:
                self.fuction()
                self.call_dot_group()
    def update(self,*args):
        super().update(*args)
        pass
    def connect_to_dot_group(self,dot_group,id):
        self._id = id
        self._check_box_group = dot_group
    def call_dot_group(self):
        self._check_box_group.active = self._id

class ImageWidget(Widget):
    def __init__(self,size,image,style:Style):
        super().__init__(size,style)
        self.image_orig = image
        self.image = self.image_orig
        self.resize([1,1])
    def resize(self, _resize_ratio):
        super().resize(_resize_ratio)
        self.image = pygame.transform.scale(self.image_orig,(self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]))
        
    def draw(self):
        super().draw()
        if not self.render:
            return
        self._event_cycle(Event.DRAW)
        self.surface.blit(self.image,[0,0])
        if self._style.borderradius > 0:
            self.surface = RoundedSurface.create(self.surface,int(self._style.borderradius))
        self._event_cycle(Event.RENDER)
        if self._is_changed:
            if self.animation_manager.anim_rotation:
                self.surface = pygame.transform.rotate(self.surface, self.animation_manager.anim_rotation)
class GifWidget(Widget):
    def __init__(self,size,gif_path=None,style:Style=default_style,frame_duration=100):
        """
        Инициализирует виджет для отображения GIF-анимации.

        Args:
            coordinates (list): Координаты виджета [x, y].
            surf (pygame.Surface): Поверхность, на которой будет отображаться виджет.
            size (list, optional): Размеры виджета [ширина, высота]. Defaults to [100, 100].
            borderradius (int, optional): Радиус скругления углов. Defaults to 0.
            gif_path (str, optional): Путь к GIF-файлу. Defaults to None.
            frame_duration (int, optional): Длительность одного кадра в миллисекундах. Defaults to 100.
        """
        super().__init__(size,style)
        self.gif_path = gif_path
        self.frames = []
        self.frame_index = 0
        self.frame_duration = frame_duration
        self.last_frame_time = 0
        self.original_size = size
        self._load_gif()
        #self.scale([1,1]) # сразу подгоняем кадры
        self.current_time = 0
        self.scaled_frames = None
        self.resize(self._resize_ratio)
    def _load_gif(self):
        """Загружает GIF-анимацию из файла."""
        if self.gif_path:
            try:
                gif = Image.open(self.gif_path)
                for i in range(gif.n_frames):
                    gif.seek(i)
                    frame_rgb = gif.convert('RGB')
                    frame_surface = pygame.image.frombuffer(frame_rgb.tobytes(), frame_rgb.size, 'RGB')
                    self.frames.append(frame_surface)
                
            except FileNotFoundError:
                print(f"Error: GIF file not found at {self.gif_path}")
            except Exception as e:
                print(f"Error loading GIF: {e}")

    def resize(self, _resize_ratio):
        super().resize(_resize_ratio)
        """Изменяет размер GIF-анимации.
        Args:
            _resize_ratio (list, optional): Коэффициент масштабирования [scale_x, scale_y]. Defaults to [1, 1].
        """
        if self.frames:
            self.scaled_frames = [pygame.transform.scale(frame,[self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]]) for frame in self.frames]


    def draw(self):
        """Отрисовывает текущий кадр GIF-анимации."""
        super().draw()
        if not self.render:
            return
        if not self.frames:
            return
        self.current_time += 1*time.delta_time*100
        if self.current_time > self.frame_duration:
             self.frame_index = (self.frame_index + 1) % len(self.frames)
             self.current_time = 0
        if self.scaled_frames:
            frame_to_draw = self.scaled_frames[self.frame_index] if hasattr(self,"scaled_frames") else self.frames[self.frame_index]
            frame_rect = frame_to_draw.get_rect(center=self.coordinates)
            self.surface.blit(frame_to_draw,(0,0))
        self._event_cycle(Event.RENDER)
        if self._is_changed:
            if self.animation_manager.anim_rotation:
                self.surface = pygame.transform.rotate(self.surface, self.animation_manager.anim_rotation)
        
class Input(Widget):
    def __init__(self, size, style,default:str="",placeholder:str="",blacklist=None,
                 whitelist=None,on_change_function=None,multiple = False,active=True,
                 allow_paste=True,words_indent=False,max_characters=None):
        super().__init__(size, style)
        self._entered_text = default
        self.selected = False
        self.blacklist = blacklist
        self.whitelist = whitelist
        self.placeholder = placeholder
        self._on_change_fun = on_change_function
        self.active = active
        self.iy = multiple
        self.paste = allow_paste
        self._wordssplit = words_indent
        self.max_characters = max_characters
        self._right_bake_text()
        
    def _right_bake_text(self):
        if len(self._entered_text) <= 0: 
            self.bake_text(self.placeholder,self.iy,self._wordssplit,continuous=not self.iy)
        else:
            self.bake_text(self._entered_text,self.iy,self._wordssplit,continuous=not self.iy)
    @property
    def style(self):
        return self._style
    @style.setter
    def style(self, style:Style):
        self._is_changed = True
        self._style = copy.copy(style)
        if hasattr(self,'_entered_text'):
            self.bake_text(self._entered_text)
    
    def update(self,events:list[pygame.event.Event]):
        super().update()
        if not self.active:
            return
        self.check_selected()
        #try:
        #    print(self.master_coordinates,mouse.pos)
        #except:
        #    pass
        if self.selected:
           # print("goida")
            for event in events:
                if event.type == pygame.KEYDOWN:
                    self._is_changed = True
                    if event.key == pygame.K_BACKSPACE:
                        self._entered_text = self._entered_text[:-1]
                        #print([len(self._entered_text)])
                        self._right_bake_text()
                        if self._on_change_fun:
                            self._on_change_fun(self._entered_text)
                    elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                        if self.paste:
                            try:
                                self._entered_text += pygame.scrap.get_text()
                                if self._on_change_fun:
                                    self._on_change_fun(self._entered_text)
                                self._right_bake_text()
                            except pygame.error:
                                pass
                    elif event.unicode:
                        unicode = event.unicode
                        if self.max_characters:
                            if len(self._entered_text) >= self.max_characters:
                                continue
                        if self.blacklist:
                            for i in range(len(self.blacklist)):
                                item = self.blacklist[i]
                                if item in unicode:
                                    unicode = unicode.replace(item,"")
                        if self.whitelist:
                            new_unicode = ""
                            for i in range(len(unicode)):
                                item = unicode[i]
                                if item in self.whitelist:
                                    new_unicode += item
                            unicode = new_unicode
                        self._entered_text += unicode
                        if unicode != "":
                            if self._on_change_fun:
                                self._on_change_fun(self._entered_text)
                        self._right_bake_text()
    def check_selected(self):
        #print(self.get_rect(),mouse.pos)
        if self.get_rect().collidepoint(mouse.pos) and mouse.left_fdown:
            self.selected = True
        elif not self.get_rect().collidepoint(mouse.pos) and mouse.left_fdown:
            self.selected = False
    @property
    def text(self):
        if self._entered_text=="":
            return self.placeholder
        return self._entered_text
        
    @text.setter
    def text(self,text:str):
        self._entered_text = text
        self.bake_text(self._entered_text,self.iy,self._wordssplit)
        self._right_bake_text()
    
    def draw(self):
        self._event_cycle(Event.DRAW)
        super().draw()
        if not self.render:
            return
        if self._is_changed:
            self.surface.blit(self._text_surface, self._text_rect if not self.iy else self._text_rect.topleft)
        self._event_cycle(Event.RENDER)
        if self._is_changed:
            if self.animation_manager.anim_rotation:
                self.surface = pygame.transform.rotate(self.surface, self.animation_manager.anim_rotation)
     
class MusicPlayer(Widget):
    def __init__(self, size, music_path, style: Style = default_style):
        super().__init__(size, style)
        pygame.mixer.init()
        self.music_path = music_path
        self.sound = pygame.mixer.Sound(music_path) 
        self.music_length = self.sound.get_length() * 1000 
        self.channel = None 
        self.start_time = 0 
        self.progress = 0
        self.side_button_size = self.size[1] / 4
        self.progress_bar_height = self.size[1] / 4
        self.cross_image = self.draw_cross()
        self.circle_image = self.draw_circle()
        self.button_image = self.circle_image
        self.button_rect = self.button_image.get_rect(center=(self.side_button_size / 2, self.side_button_size / 2))
        self.time_label = Label((size[0] - self.side_button_size * 2, 20),
                              f"{self.format_time(self.progress)}/{self.format_time(self.music_length)}",
                              style(fontsize=12, bordercolor=Color_Type.TRANSPARENT, bgcolor=Color_Type.TRANSPARENT))
        self.is_playing = False
        self.sinus_margin = 0

    def resize(self, _resize_ratio):
        super().resize(_resize_ratio)
        self.time_label.resize(_resize_ratio)
    def draw_sinusoid(self,size,frequency,margin):
        self.sinus_surf = pygame.Surface(size,pygame.SRCALPHA)
        self.sinus_surf.fill((0,0,0,0))
        for i in range(int(size[0])):
            y = abs(int(size[1] * math.sin(frequency * i+margin))) 
            y = size[1]-y
            print(y)
            pygame.draw.line(self.sinus_surf,(50,50,200),(i,size[1]),(i,y))
            
    def update(self, *args):
        super().update()
        if self.is_playing:
            self.sinus_margin+=1*time.delta_time
        if self.sinus_margin >= 100:
            self.sinus_margin = 0
        self.time_label.coordinates = [(self.size[0] / 2 - self.time_label.size[0] / 2) * self._resize_ratio[0],(self.size[1] - self.time_label.size[1]) * self._resize_ratio[1]]
        if mouse.left_fdown:
            if pygame.Rect([self.master_coordinates[0], self.master_coordinates[1]],[self.side_button_size, self.side_button_size]).collidepoint(mouse.pos):
                self.toggle_play()

        if self.is_playing:
            self.progress = pygame.time.get_ticks() - self.start_time
            if self.progress >= self.music_length:
                self.stop()
            self.time_label.text = f"{self.format_time(self.progress)}/{self.format_time(self.music_length)}"
            self.button_image = self.cross_image 
        else:
            self.button_image = self.circle_image
            if self.progress >= self.music_length:
                self.progress = 0

            self.time_label.text = f"{self.format_time(self.progress)}/{self.format_time(self.music_length)}"
    def format_time(self, milliseconds):
        total_seconds = milliseconds // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02}:{seconds:02}"
    def toggle_play(self):
        if self.is_playing:
            self.pause()
        else:
            self.play()
    def play(self):
            self.channel = self.sound.play(0)
            if self.channel is not None:
                self.start_time = self.progress 
                self.is_playing = True
            else:
                print("Error: Could not obtain a channel to play the sound. Jopa also")
    def pause(self):
        if self.is_playing:
            if self.channel:
                self.channel.pause()
            self.is_playing = False
    def stop(self):
        if self.channel:
            self.channel.stop()
        self.is_playing = False
        self.progress = 0
    def draw_cross(self):
        cross_surface = pygame.Surface((self.side_button_size, self.side_button_size), pygame.SRCALPHA)
        pygame.draw.line(cross_surface, (255, 255, 255), (5, 5), (self.side_button_size - 5, self.side_button_size - 5), 3)
        pygame.draw.line(cross_surface, (255, 255, 255), (self.side_button_size - 5, 5), (5, self.side_button_size - 5), 3)
        return cross_surface

    def draw_circle(self):
        circle_surface = pygame.Surface((self.side_button_size, self.side_button_size), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (255, 255, 255), (self.side_button_size // 2, self.side_button_size // 2),self.side_button_size // 2 - 5)
        return circle_surface

    def draw(self):
        super().draw()
        self.surface.blit(self.button_image, self.button_rect)
        progress_width = (self.size[0] / 1.2 * (self.progress / self.music_length)) * self._resize_ratio[0] if self.music_length > 0 else 0
        pygame.draw.rect(self.surface, (10, 10, 10),
                         ((self.size[0] - self.size[0] / 1.2) / 2 * self._resize_ratio[0],
                          (self.size[1] / 2 - self.progress_bar_height / 2) * self._resize_ratio[1],
                          self.size[0] / 1.2 * self._resize_ratio[0],
                          self.progress_bar_height * self._resize_ratio[1]), 0, self._style.borderradius)
        self.draw_sinusoid([progress_width,self.size[1]/17*self._resize_ratio[1]],0.15,self.sinus_margin)
        self.surface.blit(self.sinus_surf,((self.size[0] - self.size[0] / 1.2) / 2 * self._resize_ratio[0],(self.size[1] / 2 - self.sinus_surf.get_height()-self.progress_bar_height / 2) * self._resize_ratio[1]))
        pygame.draw.rect(self.surface, (50, 50, 200),
                         ((self.size[0] - self.size[0] / 1.2) / 2 * self._resize_ratio[0],
                          (self.size[1] / 2 - self.progress_bar_height / 2) * self._resize_ratio[1], progress_width,
                          self.progress_bar_height * self._resize_ratio[1]), 0, -1,0,0,self._style.borderradius,self._style.borderradius)

        self.time_label.draw()
        self.surface.blit(self.time_label.surface, self.time_label.coordinates)
        self._event_cycle(Event.RENDER)
        if self._is_changed:
            if self.animation_manager.anim_rotation:
                self.surface = pygame.transform.rotate(self.surface, self.animation_manager.anim_rotation)

class ProgressBar(Widget):
    def __init__(self, size,min_value,max_value,default_value,style: Style=default_style):
        super().__init__(size,style)
        self._min_value = min_value
        self._max_value = max_value
        self.value = default_value
        self.percentage_of_value = self.value
    @property
    def percentage(self):
        return self._percentage
    @percentage.setter
    def percentage(self,value):
        self._percentage = value
        self.value = self._min_value+(self._max_value-self._min_value)*self._percentage
    @percentage.setter
    def percentage_of_value(self,value):
        self._percentage = (value-self._min_value)/(self._max_value-self._min_value)
    @property
    def value(self):
        return self._current_value
    @value.setter
    def value(self,value):
        self._current_value = value
        self.percentage_of_value = value
    def draw(self):
        if not self.render: return
        super().draw()
        pygame.draw.rect(self.surface,self.style.secondarycolor,[1,1,int(self.size[0]*self.percentage*self._resize_ratio[0])-2,int(self.size[1]*self._resize_ratio[1])-2],0,border_radius=int(self.style.borderradius))
        if self._is_changed:
            if self.animation_manager.anim_rotation:
                self.surface = pygame.transform.rotate(self.surface, self.animation_manager.anim_rotation)
class SliderBar(Widget):
    def __init__(self, begin_val: int, end_val: int, size, style, step: int = 1, freedom=False,default=-999.999123):
        super().__init__(size, style, freedom)
        self.begin_val = begin_val 
        self.end_val = end_val      
        self.step = step          
        self.current_value = begin_val 
        self.is_dragging = False    
        self.slider_pos = 0         
        if default!= -999.999123:
            self.current_value = default
        self._update_slider_position()  

    def _update_slider_position(self):
        """Обновляет позицию ползунка на основе текущего значения"""
        range_val = self.end_val - self.begin_val
        if range_val == 0:
            self.slider_pos = 0
        else:
            self.slider_pos = (self.current_value - self.begin_val) / range_val * self.size[0]

    def _update_value_from_position(self):
        range_val = self.end_val - self.begin_val
        if range_val == 0:
            self.current_value = self.begin_val
        else:
            self.current_value = self.begin_val + (self.slider_pos / self.size[0]) * range_val
            self.current_value = round(self.current_value / self.step) * self.step
            self.current_value = max(self.begin_val, min(self.end_val, self.current_value))

    def update(self, *args):
        super().update(*args)
        if not self.active: return
        if mouse.left_down or mouse.left_fdown:
            if self.get_rect().collidepoint(mouse.pos): self.is_dragging = True
        else: self.is_dragging = False
        if self.is_dragging:
            relative_x = mouse.pos[0] - self.master_coordinates[0]
            self.slider_pos = max(0, min(self.size[0], relative_x))
            self._update_value_from_position()
            self._update_slider_position()

    def draw(self):
        if not self.render:return
        super().draw()
        pygame.draw.line(self.surface, self.style.bordercolor,(0, self.size[1] // 2), (self.size[0], self.size[1] // 2), 6)
        slider_rect = pygame.Rect(self.slider_pos - 5,(self.size[1]- self.size[1]/1.1)/2, 10, self.size[1]/1.1)
        pygame.draw.rect(self.surface, self.style.secondarycolor, slider_rect)
        self.bake_text(str(self.current_value), alignx='left', aligny='center')
        self.surface.blit(self._text_surface, self._text_rect)
        if self._is_changed:
            if self.animation_manager.anim_rotation:
                self.surface = pygame.transform.rotate(self.surface, self.animation_manager.anim_rotation)

class ElementSwitcher(Widget):
    def __init__(self, size, elements, style: Style = default_style,on_change_function=None):
        super().__init__(size, style)
        self.elements = elements
        self.current_index = 0
        self.button_padding = 10
        self.arrow_width = 10
        self.bake_text(self.current_element_text())
        self.on_change_function = on_change_function
    def current_element_text(self):
        if not self.elements: return ""
        return f"{self.elements[self.current_index]}"
    def next_element(self):
        self.current_index = (self.current_index + 1) % len(self.elements)
        self.bake_text(self.current_element_text())
        if self.on_change_function: self.on_change_function(self.current_element_text())
    def previous_element(self):
        self.current_index = (self.current_index - 1) % len(self.elements)
        self.bake_text(self.current_element_text())
        if self.on_change_function: self.on_change_function(self.current_element_text())
    def set_index(self,index:int):
        self.current_index = index
        self.bake_text(self.current_element_text())
        if self.on_change_function: self.on_change_function(self.current_element_text())
    @property
    def hovered(self):
        return self._hovered
    @hovered.setter
    def hovered(self,value:bool):
        if self.hovered == value:
            return
        self._hovered = value
        self.bake_text(self.current_element_text())

    def update(self, *args):
        super().update(*args)
        if not self.active:
            return
        if mouse.left_up and self.hovered:
            click_pos_relative = np.array(mouse.pos) - self.master_coordinates
            center_x = self.surface.get_width() / 2
            button_width = self._text_rect.width / 2 + self.button_padding + self.arrow_width * 2
            if click_pos_relative[0] < center_x - button_width / 2: self.previous_element()
            elif click_pos_relative[0] > center_x + button_width / 2: self.next_element()

    def draw(self):
        super().draw()
        if not self.render:
            return
        text_center_x = self.surface.get_width() / 2
        text_center_y = self.surface.get_height() / 2
        left_button_center_x = text_center_x - self._text_rect.width / 2 - self.button_padding - self.arrow_width
        right_button_center_x = text_center_x + self._text_rect.width / 2 + self.button_padding + self.arrow_width

        button_center_y = text_center_y
        arrow_color = self.style.fontcolor

        pygame.draw.polygon(self.surface, arrow_color, [
            (left_button_center_x - self.arrow_width, button_center_y),
            (left_button_center_x, button_center_y - self.arrow_width / 2),
            (left_button_center_x, button_center_y + self.arrow_width / 2)])
        pygame.draw.polygon(self.surface, arrow_color, [
            (right_button_center_x + self.arrow_width, button_center_y),
            (right_button_center_x, button_center_y - self.arrow_width / 2),
            (right_button_center_x, button_center_y + self.arrow_width / 2)])

        self.surface.blit(self._text_surface, self._text_rect)
        self._event_cycle(Event.RENDER)
        if self._is_changed:
            if self.animation_manager.anim_rotation:
                self.surface = pygame.transform.rotate(self.surface, self.animation_manager.anim_rotation)