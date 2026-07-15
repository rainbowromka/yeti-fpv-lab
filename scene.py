from grid_plane import GridPlane
from slope import Slope
from corridor import Corridor
from snowboard import Snowboard

class Scene:
    def __init__(self):
        self.xy_plane = GridPlane('xy', (0.7, 0.7, 0.7))
        self.xz_plane = GridPlane('xz', (0.5, 0.5, 0.5))
        self.yz_plane = GridPlane('yz', (0.3, 0.3, 0.3))
        self.slope = Slope()
        self.corridor = Corridor()
        self.snowboard = Snowboard()
        self.snowboard.start(self.corridor.center_line)

    def draw(self):
        self.xy_plane.draw()
        self.xz_plane.draw()
        self.yz_plane.draw()
        self.slope.draw()
        self.corridor.draw()
        self.snowboard.draw()

    def update(self, dt):
        self.snowboard.update(dt, self.corridor.center_line)

    def regenerate(self):
        self.corridor.generate()
        self.snowboard.start(self.corridor.center_line)