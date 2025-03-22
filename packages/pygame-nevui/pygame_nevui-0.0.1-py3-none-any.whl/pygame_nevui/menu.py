import pygame
import copy
from .style import *
from .utils import *
from .window import Window
from .animations import *
from .widgets import *
class Menu:
    def __init__(self,window:Window,size,style:Style=default_style): 
        self.window = window
        self.window_surface = None
        self.size = size
        self._coordinatesMW = [0,0]
        self.coordinates = [0,0]
        self.style = style
        self._changed = True
        self._global_changed = True
        self._resize_ratio = [1,1]
        self._update_surface()
        
        if not self.window:
            self.window_surface = self.window
            self.window = None
            return
        
        self.isrelativeplaced = False
        self.relx = None
        self.rely = None
        
        self.first_window_size = self.window.size
        self.first_size = size
        self.first_coordinates = [0,0]
        self.window.add_event(Event(Event.RESIZE,self.resize))
        
        
        self._layout = None
        self._enabled = True
        
        self._opened_menu = None
        if isinstance(self.style.bgcolor,Gradient):
            self.gradient_surf = pygame.Surface(self.size)
            self.style.bgcolor.apply_gradient(self.gradient_surf)
    @property
    def enabled(self) -> bool:
        return self._enabled
    @enabled.setter
    def enabled(self,value:bool):
        self._enabled = value
    @property
    def coordinatesMW(self) -> list[int,int]:
        return self._coordinatesMW
    @coordinatesMW.setter
    def coordinatesMW(self,coordinates:list[int,int]):
        self._coordinatesMW = [coordinates[0]*self._resize_ratio[0]+self.window._offset[0],coordinates[1]*self._resize_ratio[1]+self.window._offset[1]]
    def coordinatesMW_update(self):
        self.coordinatesMW = self.coordinates
    def open(self,menu,style:Style=None,*args):
        self._opened_menu = menu
        self._args_menus_to_draw = []
        for item in args: self._args_menus_to_draw.append(item)
        if style: self._opened_menu.apply_style_to_all(style)
        self._opened_menu._resize_with_ratio(self._resize_ratio)
    def close(self):
        self._opened_menu = None
    def _update_surface(self):
        if self.style.borderradius>0 or self.style.bgcolor==Color_Type.TRANSPARENT:self.surface = pygame.Surface([self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]],pygame.SRCALPHA|pygame.HWSURFACE | pygame.DOUBLEBUF)
        else: self.surface = pygame.Surface([self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]],pygame.HWSURFACE | pygame.DOUBLEBUF)
        if self.style.transparency: self.surface.set_alpha(self.style.transparency)
    def resize(self,size:list[int,int]):
        self._changed = True
        self._resize_ratio = [size[0]/self.first_window_size[0],size[1]/self.first_window_size[1]]
        self.coordinatesMW_update()
        self._update_surface()
        
        if self._layout:self._layout.resize(self._resize_ratio)
        if self.style.transparency:self.surface.set_alpha(self.style.transparency)
        print(self._resize_ratio)
    def _resize_with_ratio(self,ratio:list[int,int]):
        self._changed = True
        self._resize_ratio = ratio
        self.coordinatesMW_update()
        if self.style.transparency:self.surface.set_alpha(self.style.transparency)
        if self._layout:self._layout.resize(self._resize_ratio)
    @property
    def style(self) -> Style:
        return self._style
    @style.setter
    def style(self,style:Style):
        self._style = copy.copy(style)
    def apply_style_to_childs(self,style:Style):
        self._changed = True
        self.style = style
        if self._layout: self._layout.apply_style_to_childs(style)
    @property
    def layout(self):
        return self._layout
    @layout.setter
    def layout(self,layout):
        if layout._can_be_main_layout:
            layout.coordinates = (self.size[0]/2-layout.size[0]/2,self.size[1]/2-layout.size[1]/2)
            layout.connect_to_menu(self)
            self._layout = layout
        else: raise Exception("this Layout can't be main")
    def _set_layout_coordinates(self,layout):
        layout.coordinates = [self.size[0]/2-layout.size[0]/2,self.size[1]/2-layout.size[1]/2]
    def set_coordinates(self,x:int,y:int):
        self.coordinates = [x,y]
        self.coordinatesMW_update()
        
        self.isrelativeplaced = False
        self.relx = None
        self.rely = None
        
        self.first_coordinates = self.coordinates
    def set_coordinates_relative(self,relx:int,rely:int):
        self.coordinates = [(self.window.size[0]-self.window._crop_width_offset)/100*relx-self.size[0]/2,(self.window.size[1]-self.window._crop_height_offset)/100*rely-self.size[1]/2]
        self.coordinatesMW_update()
        self.isrelativeplaced = True
        self.relx = relx
        self.rely = rely
        self.first_coordinates = self.coordinates
    def draw(self):
        if not self.enabled: return
        rect_val = [self.coordinatesMW,self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]]
        if self._global_changed  or True:
            if isinstance(self.style.bgcolor,Gradient):
                if self._changed:
                    self.gradient_surf = pygame.Surface([self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]])
                    self.style.bgcolor.apply_gradient(self.gradient_surf)
                    print("generated Gradient")
                    self._changed = False
                    if self.style.transparency: self.surface.set_alpha(self.style.transparency)
                self.surface.blit(self.gradient_surf)
            elif self.style.bgcolor == Color_Type.TRANSPARENT: self.surface.fill((0,0,0,0))
            else: self.surface.fill(self._style.bgcolor)
        self._layout.draw()
        if self._style.borderwidth > 0:
            pygame.draw.rect(self.surface,self._style.bordercolor,[0,0,rect_val[1],rect_val[2]],int(self._style.borderwidth*(self._resize_ratio[0]+self._resize_ratio[1])/2) if int(self._style.borderwidth*(self._resize_ratio[0]+self._resize_ratio[1])/2)>0 else 1,border_radius=int(self._style.borderradius*(self._resize_ratio[0]+self._resize_ratio[1])/2))
        if self._style.borderradius > 0:
            self.surface = RoundedSurface.create(self.surface,int(self._style.borderradius*(self._resize_ratio[0]+self._resize_ratio[1])/2))
        self.window.surface.blit(self.surface,rect_val[0])
        #Opened Menu
        if self._opened_menu:
            for item in self._args_menus_to_draw: item.draw()
            self._opened_menu.draw()
    def update(self):
        if not self.enabled: return
        if self._opened_menu:
            self._opened_menu.update()
            return
        if self._layout: self._layout.update()
        self._global_changed = self.layout._is_changed
    def get_rect(self)->pygame.Rect:
        return pygame.Rect(self.coordinatesMW[0],self.coordinatesMW[1],self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1])

class DropDownMenu(Menu):
    def __init__(self, window:Window, size:list[int,int], style:Style=default_style,side:Align=Align.TOP,opened:bool=False,button_size:list[int,int]=None):
        super().__init__(window, size, style)
        self.side = side
        if not button_size:
            sz =[self.size[0]/3,self.size[0]/3]
        else:
            sz = button_size
        self.button = Button(self.toogle_self,"",sz,self.style)
        self.button.add_event(Event(Event.RENDER,lambda:self.draw_arrow(self.button.surface,self.style.bordercolor)))
        self.opened = opened
        self.transitioning = False
        self.animation_manager = AnimationManager()
        if self.side == Align.TOP:
            end = [self.coordinates[0],self.coordinates[1]-self.size[1]]
        elif self.side == Align.BOTTOM:
            end = [self.coordinates[0],self.coordinates[1]+self.size[1]]
        elif self.side == Align.LEFT:
            end = [self.coordinates[0]-self.size[0],self.coordinates[1]]
        elif self.side == Align.RIGHT:
            end = [self.coordinates[0]+self.size[0],self.coordinates[1]]
        self.end = end
        self.animation_speed = 1
    def draw_arrow(self, surface:pygame.Surface, color:list[int,int,int]|list[int,int,int,int], padding:int=1.1):
        bw = surface.get_width() / padding
        bh = surface.get_height() / padding

        mw = (surface.get_width() - bw) / 2
        mh = (surface.get_height() - bh) / 2
        
        if self.side == Align.TOP or self.side == Align.BOTTOM and self.opened and not self.transitioning:
            points = [(mw, mh), (bw // 2 + mw, bh + mh), (bw + mw, mh)]
        if self.side == Align.BOTTOM or self.side == Align.TOP and self.opened and not self.transitioning:
            points = [(mw, bh + mh), (bw // 2 + mw, mh), (bw + mw, bh + mh)]
        if self.side == Align.LEFT or self.side == Align.RIGHT and self.opened and not self.transitioning:
            points = [(mw, mh), (bw + mw, bh // 2 + mh), (mw, bh + mh)]
        if self.side == Align.RIGHT or self.side == Align.LEFT and self.opened and not self.transitioning:
            points = [(bw + mw, mh), (mw, bh // 2 + mh), (bw + mw, bh + mh)]
        pygame.draw.polygon(surface, color, points)
    def toogle_self(self):
        print("toogled")
        if self.transitioning: return
        self.animation_manager = AnimationManager()
        if self.opened:
            self.opened = False
            if self.side == Align.TOP:
                end = [self.coordinatesMW[0],self.coordinatesMW[1]-self.size[1]]
            elif self.side == Align.BOTTOM:
                end = [self.coordinatesMW[0],self.coordinatesMW[1]+self.size[1]]
            elif self.side == Align.LEFT:
                end = [self.coordinatesMW[0]-self.size[0],self.coordinatesMW[1]]
            elif self.side == Align.RIGHT:
                end = [self.coordinatesMW[0]+self.size[0],self.coordinatesMW[1]]
            self.end = end
            anim_transitioning = AnimationEaseInOut(0.5*self.animation_speed,self.coordinatesMW,end,AnimationType.POSITION)
            anim_opac = AnimationLinear(0.25*self.animation_speed,255,0,AnimationType.OPACITY)
            self.animation_manager.add_start_animation(anim_transitioning)
            self.animation_manager.add_start_animation(anim_opac)
            self.transitioning = True
        else:
            self.opened = True
            if self.side == Align.TOP:
                start = [self.coordinatesMW[0],self.coordinatesMW[1]-self.size[1]]
            elif self.side == Align.BOTTOM:
                start = [self.coordinatesMW[0],self.coordinatesMW[1]+self.size[1]]
            elif self.side == Align.LEFT:
                start = [self.coordinatesMW[0]-self.size[0],self.coordinatesMW[1]]
            elif self.side == Align.RIGHT:
                start = [self.coordinatesMW[0]+self.size[0],self.coordinatesMW[1]]
            anim_transitioning = AnimationEaseInOut(0.5*self.animation_speed,start,self.coordinatesMW,AnimationType.POSITION)
            anim_opac = AnimationLinear(0.5*self.animation_speed,0,255,AnimationType.OPACITY)
            self.animation_manager.add_start_animation(anim_transitioning)
            self.animation_manager.add_start_animation(anim_opac)
            self.transitioning = True
        self.animation_manager.update()
    def draw(self):
        customval = [0,0]
        if self.animation_manager.anim_opacity:
            self.surface.set_alpha(self.animation_manager.anim_opacity)
        if self.transitioning:
            customval = self.animation_manager.anim_position
            rect_val = [customval,self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]]
        elif self.opened:
            rect_val = [self.coordinatesMW,self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]]
        else:
            rect_val = [self.end,self.size[0]*self._resize_ratio[0],self.size[1]*self._resize_ratio[1]]
            self.button.draw()
            self.window.surface.blit(self.button.surface,self.button.coordinates)
            return
        self.surface.fill(self._style.bgcolor)
        self._layout.draw()
        if self._style.borderwidth > 0:
            pygame.draw.rect(self.surface,self._style.bordercolor,[0,0,rect_val[1],rect_val[2]],int(self._style.borderwidth*(self._resize_ratio[0]+self._resize_ratio[1])/2) if int(self._style.borderwidth*(self._resize_ratio[0]+self._resize_ratio[1])/2)>0 else 1,border_radius=int(self._style.borderradius*(self._resize_ratio[0]+self._resize_ratio[1])/2))
        if self._style.borderradius > 0:
            self.surface = RoundedSurface.create(self.surface,int(self._style.borderradius*(self._resize_ratio[0]+self._resize_ratio[1])/2))
        if rect_val[0]:
            self.window.surface.blit(self.surface,[int(rect_val[0][0]),int(rect_val[0][1])])
        self.button.draw()

        self.window.surface.blit(self.button.surface,self.button.coordinates)
    def update(self):
        self.animation_manager.update()
        if not self.animation_manager.start and self.transitioning:
            self.transitioning = False
        if self.transitioning:
            if self.animation_manager.anim_position:
                bcoords = self.animation_manager.anim_position
            else:
                bcoords = [-999,-999]
        elif self.opened:
            bcoords = self.coordinatesMW
        else:
            bcoords = self.end
        if self.side == Align.TOP:
            coords = [bcoords[0] + self.size[0] / 2-self.button.size[0]/2, bcoords[1] + self.size[1]]
        elif self.side == Align.BOTTOM:
            coords = [bcoords[0] + self.size[0] / 2-self.button.size[0]/2, bcoords[1]-self.button.size[1]]
        elif self.side == Align.LEFT:
            coords = [bcoords[0] + self.size[0], bcoords[1] + self.size[1] / 2-self.button.size[1]/2]
        elif self.side == Align.RIGHT:
            coords = [bcoords[0]-self.button.size[0], bcoords[1] + self.size[1] / 2-self.button.size[1]/2]
        self.button.coordinates = coords
        self.button.master_coordinates = self.button.coordinates
        self.button.update()
        if self.opened:
            super().update()
        
class ContextMenu(Menu):
    _opened_context = False
    def __init__(self, window, size, style = default_style):
        super().__init__(window, size, style)
        self._close_context()
    def _open_context(self,coordinates):
        self.set_coordinates(coordinates[0]-self.window._crop_width_offset,coordinates[1]-self.window._crop_width_offset)
        self._opened_context = True
    def apply(self):
        self.window._selected_context_menu = self
    def _close_context(self):
        self._opened_context = False
        self.set_coordinates(-self.size[0],-self.size[1])
    def draw(self):
        if self._opened_context: super().draw()
    def update(self):
        if self._opened_context: super().update()
class Group():
    def __init__(self,items=[]):
        self.items = items
        self._enabled = True
        self._opened_menu = None
        self._args_menus_to_draw = []
    def update(self):
        if not self._enabled:
            return
        if self._opened_menu:
            self._opened_menu.update()
            return
        for item in self.items:
            item.update()
    def draw(self):
        if not self._enabled:
            return
        for item in self.items:
            item.draw()
        if self._opened_menu:
            for item2 in self._args_menus_to_draw:
                item2.draw()
            self._opened_menu.draw()
    def step(self):
        if not self._enabled:
            return
        for item in self.items:
            item.update()
            item.draw()
    def enable(self):
        self._enabled = True
    def disable(self):
        self._enabled = False
    def toogle(self):
        self._enabled = not self._enabled
    def open(self,menu,style:Style=None,*args):
        self._opened_menu = menu
        self._args_menus_to_draw = []
        for item in args:
            self._args_menus_to_draw.append(item)
        if style:
            self._opened_menu.apply_style_to_all(style)
        self._opened_menu._resize_with_ratio(self._resize_ratio)
    def close(self):
        self._opened_menu = None