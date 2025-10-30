import numpy as np

class SpringFollower:
    def __init__(self, k=10.0, b=6.0, rest_length=0.5, dt=0.02):
        self.k = k
        self.b = b
        self.l0 = rest_length
        self.dt = dt

        self.pos = np.array([0.0, 0.0])
        self.vel = np.array([0.0, 0.0])

    def human_position(self, r, theta):
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        return np.array([x, y])

    def update(self, human_position):
        ph = self.human_position(human_position[0], human_position[1])
        diff = ph - self.pos
        dist = np.linalg.norm(diff)

        if dist > 1e-6:
            vel_spring = (self.k / self.b) * (1 - self.l0 / dist) * diff
        else:
            vel_spring = np.zeros(2)

        self.vel = vel_spring / self.b
        self.pos += self.vel * self.dt
        return self.vel
