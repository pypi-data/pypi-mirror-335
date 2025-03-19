from .game_object import Component, GameObject, DEBUG
import pygame as pg
from .vmath_mini import Vector2d

from .transform import Transform

class SurfaceComponent(Component):
    pg_surf: pg.Surface
    size: Vector2d

    def __init__(self, size: Vector2d):
        self.size = size
        self.pg_surf = pg.Surface(size.as_tuple(), pg.SRCALPHA, 32)
        if DEBUG:
            self.pg_surf.set_alpha(128)

    def blit(self):
        if self.game_object == GameObject.root:
            return
        elif self.game_object.parent == GameObject.root:
            surf = self.game_object.parent.get_component(SurfaceComponent) 
            pos = self.game_object.get_component(Transform).pos - GameObject.get_group_by_tag("Camera")[0].get_component(Transform).pos
            pos += Vector2d.from_tuple(pg.display.get_surface().get_size())/2
        else:
            surf = self.game_object.parent.get_component(SurfaceComponent) 
            pos = self.game_object.get_component(Transform).pos + (self.game_object.parent.get_component(SurfaceComponent).size / 2)
        surf.pg_surf.blit(self.pg_surf, (pos - self.size / 2).as_tuple())


