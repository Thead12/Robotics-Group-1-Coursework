import math
import motors
import numpy as np

class SpringFollower:
    def __init__(self, speed=0.0, follow_distance=5.0, stopping_distance=2.0, v_max = 1.0, deadband=0.2):
        self.speed = speed
        self.motors = motors.MotorsYukon(mecanum=False)

        self.was_turning_right = True

        self.follow_distance = follow_distance
        self.stopping_distance = stopping_distance       
        self.v_max = v_max
        self.deadband = deadband  
        self.k = self.v_max / ((self.follow_distance - self.stopping_distance) ** 2)

        self.vel = np.array([0.0, 0.0])
        self._origin = np.array([0.0, 0.0])

    def update(self, human_detected, angle, distance):
        if not human_detected:
            self.speed = 0.3
            spinning_angle = math.radians(90) if self.was_turning_right else math.radians(-90)
            self.drive(spinning_angle)
            return
        else:
            self.speed = self.quadratic_speed(distance)
            self.drive(angle)
                
    def quadratic_speed(self, distance):
        if distance is None or math.isnan(distance):
            return 0.0

        if abs(distance - self.stopping_distance) <= self.deadband:
                return 0.0

        v = self.k * (distance - self.stopping_distance)**2
        return min(v, self.v_max)
    
    def drive(self, angle):
        # max angle is 90 degrees
        # at -90 and 90 degrees wheel multiplier should be 0 for corresponding side
        # as robot is turning theta decreases
        angle_clipped = angle
        np.clip(angle_clipped, 1, 1)
                
        turning = 0.5*np.cos(angle)
        turning_speed = turning*self.speed
        
        if angle_clipped > 0:
            self.motors.frontLeft(speed=self.speed)
            self.motors.backLeft(speed=self.speed)

            self.motors.frontRight(speed=turning_speed)
            self.motors.backRight(speed=turning_speed)

            return True

        elif angle_clipped < 0:            
            self.motors.frontLeft(speed=turning_speed)
            self.motors.backLeft(speed=turning_speed)

            self.motors.frontRight(speed=self.speed)
            self.motors.backRight(speed=self.speed)

        else:
            self.motors.frontLeft(speed=self.speed)
            self.motors.backLeft(speed=self.speed)

            self.motors.frontRight(speed=self.speed)
            self.motors.backRight(speed=self.speed)

            return False
    
    def stop(self):
        # turn of cameras and such
        self.motors.stop()