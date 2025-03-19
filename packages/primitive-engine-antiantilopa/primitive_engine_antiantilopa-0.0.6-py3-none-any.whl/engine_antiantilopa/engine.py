from .game_object import GameObject, DEBUG
from .surface import SurfaceComponent
from .camera import Camera
from .transform import Transform
from .vmath_mini import Vector2d
import pygame as pg

class Engine:

    def __init__(self, window_size: Vector2d|tuple[int, int] = Vector2d(0, 0)):
        if not isinstance(window_size, Vector2d):
            window_size = Vector2d.from_tuple(window_size)
        pg.init()
        pg.font.init()
        screen = GameObject("main_screen")
        screen.add_component(Transform(Vector2d(0, 0)))
        screen.add_component(SurfaceComponent(window_size))
        screen.get_component(SurfaceComponent).pg_surf = pg.display.set_mode(screen.get_component(SurfaceComponent).pg_surf.get_size())
        GameObject.root = screen
        screen.add_child(Camera)

    def run(self, fps = 20):
        run = True
        clock = pg.time.Clock()
        while run:
            clock.tick(fps)
            for event in pg.event.get(eventtype=pg.QUIT):
                if event.type == pg.QUIT:
                    run = False
            self.draw()
            self.iteration()
            pg.display.flip()
            for g_obj in GameObject.objs:
                for child in g_obj.childs:
                    if child.need_draw:
                        g_obj.get_component(SurfaceComponent).pg_surf.fill((0, 0, 0, 0))
                        break
            if DEBUG:
                print(f"fps = {clock.get_fps()}")


    def iteration(self):
        for g_obj in GameObject.objs:
            g_obj.iteration()

    def draw(self):
        for g_obj in GameObject.objs:
            g_obj.draw()
        window_size = GameObject.root.get_component(SurfaceComponent).size
        camera_pos = Camera.get_component(Transform).pos
        def blit(g_obj: GameObject, abs_pos: Vector2d):
            for child in g_obj.childs:
                if child.need_blit is False:
                    continue
                dist = (window_size + child.get_component(SurfaceComponent).size)
                if (abs_pos + child.get_component(Transform).pos - camera_pos + dist / 2).is_in_box(Vector2d(0, 0), dist):
                    blit(child, abs_pos + child.get_component(Transform).pos)
            if not (g_obj in GameObject.get_group_by_tag("Camera")):
                if g_obj.need_blit:
                    g_obj.get_component(SurfaceComponent).blit()
                    g_obj.need_blit = False
        blit(GameObject.root, Vector2d(0, 0))

        for g_obj in GameObject.objs:
            g_obj.need_draw = False

        Camera.get_component(SurfaceComponent).blit()
    
    def update(self):
        for g_obj in GameObject.objs:
            g_obj.update()
    
    @staticmethod
    def set_debug(value: bool):
        global DEBUG
        DEBUG = value