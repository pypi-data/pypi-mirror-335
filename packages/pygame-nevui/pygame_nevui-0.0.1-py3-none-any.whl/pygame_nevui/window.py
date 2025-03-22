from .utils import *
import sys
import pygame

_context_to_draw = None

class Window:
    @staticmethod
    def cropToRatio(width:int, height:int, ratio, default=(0, 0)):
        """
        Crop dimensions to a specified ratio.

        Arguments:
        width -- original width
        height -- original height
        ratio -- tuple containing the desired ratio (width, height)
        default -- tuple of default values to return if dimensions already match the ratio

        Returns:
        A tuple (new width:int, new height:int) to crop to the specified ratio.
        """
        rx, ry = ratio
        aspect_ratio = width / height
        if aspect_ratio == rx / ry: return default
        if aspect_ratio > rx / ry:
            crop_width = width - (height * rx / ry)
            return crop_width, default[1]
        else:
            crop_height = height - (width * ry / rx)
            return default[0], crop_height
        
    def __init__(self, size, minsize=(10, 10), title="pygame window", resizable=True, ratio: list[int, int] = None):
        """
        Initialize a Window object.

        size: (width, height) tuple of the window size
        minsize: (width, height) tuple of the minimum window size (NOTE: not implemented yet)
        title: the title of the window
        resizable: if True, the window is resizable (NOTE: buggy and unstable, use at your own risk)
        ratio: a (width, height) tuple of the desired aspect ratio of the window (NOTE: also very buggy)

        The window is created with the given size and title, and is set to be
        resizable if resizable is True. If a ratio is given, the window is
        resized to fit the given aspect ratio if the original size does not
        match the ratio.
        """
        self._original_size = size
        self.size = np.array(size)
        self.minsize = np.array(minsize)
        
        if resizable: flags = pygame.RESIZABLE 
        else: flags = 0
        self.surface = pygame.display.set_mode(size, flags=flags)
        self._title = title
        pygame.display.set_caption(self._title)
        
        self._ratio = ratio
        self._clock = pygame.time.Clock()
        
        self._events: list[Event] = []
        self.last_events = []
        
        self._offset = [0, 0]
        self._crop_width_offset = 0
        self._crop_height_offset = 0
        
        self._selected_context_menu = None
    @property
    def offset(self):
        return self._offset
    @property
    def title(self):
        return self._title
    @title.setter
    def title(self, text:str):
        self._title = text
        pygame.display.set_caption(self._title)
    @property
    def ratio(self):
        return self._ratio
    @ratio.setter
    def ratio(self, ratio:list[int, int]):
        self._ratio = ratio
    @property
    def original_size(self):
        return self._original_size
    def add_event(self,event:Event):
        self._events.append(event)
    def _event_cycle(self,type:int,*args, **kwargs):
        for event in self._events:
            if event.type == type:
                event(*args, **kwargs)
    def update(self,events,fps=60):
        self.last_events = events
        mouse.update()
        time.update()
        for item in keyboards_list:
            item.update()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.VIDEORESIZE:
                self.size = (event.w,event.h)
                if not self._ratio: self._crop_width_offset, self._crop_height_offset = self.cropToRatio(self.size[0], self.size[1], (self._original_size[0], self._original_size[1]))
                else: self._crop_width_offset, self._crop_height_offset = self.cropToRatio(self.size[0], self.size[1], self._ratio)
                self._offset = [self._crop_width_offset // 2,self._crop_height_offset // 2]
                self.surface = pygame.display.set_mode(self.size, pygame.RESIZABLE)

                self._event_cycle(Event.RESIZE,[self.size[0]-self._crop_width_offset,self.size[1]-self._crop_height_offset])
            if mouse.right_up:
                print("right up")
                if self._selected_context_menu:
                   self._selected_context_menu._open_context(mouse.pos)
            if mouse.any_down or mouse.any_fdown:
                if self._selected_context_menu:
                    if not self._selected_context_menu.get_rect().collidepoint(mouse.pos):
                        self._selected_context_menu._close_context()
                    
        self._clock.tick(fps)
        self._event_cycle(Event.UPDATE)
    @property
    def rel(self):
        return [(self.size[0]-self._crop_width_offset)/self._original_size[0],(self.size[1]-self._crop_height_offset)/self._original_size[1]]