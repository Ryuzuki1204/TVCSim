# modules

from vpython import *
from time import sleep
import matplotlib.pyplot as plt

# time step

dt = 0.1

# setpoint

setpoint = 6
setpoint_line = curve(vector(-10, setpoint, 0), vector(10, setpoint,
                      0), color=color.blue)

# rocket params

initial_velocity = 0
initial_height = -10
max_thrust = 15  # newtons
mass = 1  # kg
g = -9.8
min_pos = -10
# PID constants
# time period = 7
# Ku ~ 2
KP = 2/5
KI = 2/35
KD = 14/15

# Ziegler nicholson method:
# using the "no overshoot method" https://en.wikipedia.org/wiki/Ziegler%E2%80%93Nichols_method
# Ziegler–Nichols Tuning Rules for PID, Microstar Laboratories

# Tip: decreasing KI to 2/25 yields lesser overshoot, but later start
class Rocket:

    def __init__(self):
        self.body = cylinder(
            pos=vector(0, initial_height, 0),
            color=color.red,
            length=3.5,
            radius=0.3,
            axis=vector(0, 1, 0),
            opacity=0.6,
            make_trail = True
            )
        self.velocity = vector(0, initial_velocity, 9)
        self.acc = vector(0, 0, 0)
        self.trail = curve(color=color.white)

    def set_acc(self, thrust):
        self.acc = vector(0, g + thrust / mass, 0)

    def get_acc(self):
        return self.acc.y

    def set_vel(self):
        self.velocity += self.acc * dt

    def get_vel(self):
        return self.velocity.y

    def set_pos(self):
        self.body.pos.y += self.velocity.y * dt
        if(self.body.pos.y <= min_pos):
            self.body.pos.y = min_pos

    def get_pos(self):
        return self.body.pos.y


class PID:

    def __init__(
        self,
        KP,
        KI,
        KD,
        target
        ):
        self.kp = KP
        self.ki = KI
        self.kd = KD
        self.setpoint = target
        self.error = 0
        self.integral_error = 0
        self.derivative_error = 0
        self.error_last = 0
        self.kpe = 0
        self.kde = 0
        self.kie = 0
        self.computed_thrust = 0

    def output(self, pos):
        self.error = self.setpoint - pos
        self.integral_error += self.error * dt
        self.derivative_error = (self.error - self.error_last) / dt
        self.error_last = self.error

        self.kpe = self.kp * self.error
        self.kde = self.kd * self.derivative_error
        self.kie = self.ki * self.integral_error

        self.computed_thrust = self.kpe + self.kie + self.kde

        if self.computed_thrust >= max_thrust:
            self.computed_thrust = max_thrust
        elif self.computed_thrust <= 0:
            self.computed_thrust = 0
        else:
            pass

        return self.computed_thrust

    def get_kpe(self):
        return self.kpe

    def get_kde(self):
        return self.kde

    def get_kie(self):
        return self.kie


class Simulation:

    def __init__(self):
        self.rocket = Rocket()
        self.pid = PID(KP, KI, KD, setpoint)
        self.timestamps = []
        self.position = []
    def cycle(self):
        i = 0
        while i < 30:
            i += dt
            rate(50)
            thrust = self.pid.output(self.rocket.get_pos())
            self.position.append(self.rocket.get_pos())
            self.timestamps.append(i)
            self.rocket.set_acc(thrust)
            print(f"acc = {self.rocket.get_acc()}")
            self.rocket.set_vel()
            print(f"vel = {self.rocket.get_vel()}")
            self.rocket.set_pos()
            print(f"pos = {self.rocket.get_pos()}")
        plt.plot(self.timestamps, self.position)
        plt.show()

scene.autoscale = False


def main():
    sim = Simulation()
    sim.cycle()


main()
