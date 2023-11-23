#manim -pql scene.py ThreeDLightSourcePosition
import manim
import numpy as np

class ThreeDLightSourcePosition(manim.ThreeDScene):
    def construct(self):
        axes = manim.ThreeDAxes()
        sphere = manim.Surface(
            lambda u, v: np.array([
                1.5 * np.cos(u) * np.cos(v),
                1.5 * np.cos(u) * np.sin(v),
                1.5 * np.sin(u)
            ]), v_range=[0, manim.TAU], u_range=[-manim.PI / 2, manim.PI / 2],
            checkerboard_colors=[manim.RED_D, manim.RED_E], resolution=(15, 32)
        )
        self.renderer.camera.light_source.move_to(3*manim.IN) # changes the source of the light
        self.set_camera_orientation(phi=75 * manim.DEGREES, theta=30 * manim.DEGREES)
        self.add(axes, sphere)


