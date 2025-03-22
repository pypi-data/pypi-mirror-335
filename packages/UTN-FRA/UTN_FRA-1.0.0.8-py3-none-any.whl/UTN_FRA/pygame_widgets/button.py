# Copyright (C) 2025 <UTN FRA>
#
# Author: Facundo Falcone <f.falcone@sistemas-utnfra.com.ar>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pygame as pg
from .widget import Widget

class Button(Widget):
    
    def __init__(self, x, y, text, screen, font_path: str, color: tuple = (255,0,0), font_size = 25, on_click = None, on_click_param = None):
        super().__init__(x, y, text, screen, font_size)
        self.font = pg.font.Font(font_path, self.font_size)
        self.image = self.font.render(self.text, True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.on_click = on_click
        self.on_click_param = on_click_param 
    
    def button_pressed(self):
        """
        This function checks if a button is pressed at the mouse position and triggers a delay before
        executing a specified action.
        """
        mouse_pos = pg.mouse.get_pos()
        
        if self.rect.collidepoint(mouse_pos):
            if pg.mouse.get_pressed()[0] == 1:
                pg.time.delay(300)
                self.on_click(self.on_click_param)
    
    def draw(self):
        super().draw()
    
    def update(self):
        """
        The `update` function in Python calls the `draw` and `button_pressed` methods.
        """
        self.draw()
        self.button_pressed()