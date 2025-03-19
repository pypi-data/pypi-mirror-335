from typing import TypeVar

DEBUG = False

class Component:
    game_object: "GameObject"

    def iteration(self):
        pass

    def draw(self):
        pass

    def __str__(self):
        return f""

T = TypeVar("T", bound=Component)

class GameObject:
    tags: list[str]
    components: list[Component]
    childs: list["GameObject"]
    parent: "GameObject"
    need_draw: bool
    need_blit: bool
    active: bool

    root: "GameObject" = None
    objs: list["GameObject"] = []
    group_tag_dict: dict[str, list["GameObject"]] = {}

    def __init__(self, tags: list[str] = []) -> None:
        self.components = []
        self.childs = []
        self.parent = None
        self.active = True
        self.need_draw = True
        self.need_blit = True
        GameObject.objs.append(self)
        if isinstance(tags, str):
            tag = tags
            self.tags = [tag]
            if not tag in GameObject.group_tag_dict.keys():
                GameObject.group_tag_dict[tag] = []
            GameObject.group_tag_dict[tag].append(self)
        else:
            self.tags = tags
            for tag in tags:
                if not tag in GameObject.group_tag_dict.keys():
                    GameObject.group_tag_dict[tag] = []
                GameObject.group_tag_dict[tag].append(self)

    @staticmethod
    def get_group_by_tag(tag: str) -> list["GameObject"]:
        if not tag in GameObject.group_tag_dict.keys():
            raise KeyError(f"There is no GameObject with \"{tag}\" tag")
        return GameObject.group_tag_dict[tag]

    def add_component(self, component: Component):
        self.components.append(component)
        component.game_object = self
        
    def add_child(self, child: "GameObject"):
        self.childs.append(child)
        child.parent = self

    def get_component(self, component_type: type[T]) -> T:
        for component in self.components:
            if isinstance(component, component_type):
                return component
        raise KeyError(f"{self} has no component \"{component_type}\"")

    def contains_component(self, component_type: type[T]) -> T:
        for component in self.components:
            if isinstance(component, component_type):
                return True
        return False

    def get_childs(self, tag: str) -> list["GameObject"]:
        result = []
        for child in self.childs:
            if tag in child.tags:
                result.append(child)
        return result

    def iteration(self):
        if not self.active:
            return
        for component in self.components:
            component.iteration()

    def draw(self):
        if not self.active or not self.need_draw:
            return
        for component in self.components:
            component.draw()

    def update(self):
        if not self.active:
            return
        for component in self.components:
            component.iteration()
            component.draw()

    def enable(self):
        self.active = True
        for child in self.childs:
            child.enable()

    def disable(self):
        self.active = False
        for child in self.childs:
            child.disable()

    def need_draw_set_true(self):
        self.need_draw = True
        self.need_blit = True
        if self.parent is not None:
            self.parent.need_draw_set_true()

    def destroy(self):
        for child in self.childs:
            child.destroy()
        GameObject.objs.remove(self)
        for tag in self.tags:
            GameObject.group_tag_dict[tag].remove(self)
        self.parent.childs.remove(self)

    @staticmethod
    def show_geneology_tree(g_obj: "GameObject|None" = None, depth: int = 1):
        if g_obj is None:
            g_obj = GameObject.root
        print("| " * (depth - 1) + "|-", g_obj)
        for child in g_obj.childs:
            GameObject.show_geneology_tree(child, depth + 1)

    def __str__(self):
        return f"GameObject: tags:{self.tags}, components: {self.components}, childs: {self.childs}"
