from .game_object import Component
from .vmath_mini import Vector2d, Angle

class Transform(Component):
    pos: Vector2d
    rotation: Angle

    def __init__(self, pos: Vector2d = Vector2d(0, 0), rotation: Angle|float = 0) -> None:
        self.pos = pos
        if not isinstance(rotation, Angle):
            self.rotation = Angle(rotation)
        else:
            self.rotation = rotation

    def move(self, delta: Vector2d):
        self.pos += delta
        if self.game_object.parent is not None:
            self.game_object.parent.need_draw_set_true()
    
    def rotate(self, delta: Angle):
        self.rotation += delta
    
    def set_pos(self, pos: Vector2d):
        self.pos = pos
    
    def set_rotation(self, rotation: Angle):
        self.rotation = rotation

    def __str__(self):
        return f"Transform: {self.pos}, {self.rotation}"