__author__ = "seamonsters"
import math
import wpilib
import inspect, os
import configparser
from pyfrc.physics import drivetrains
from pyfrc.physics.visionsim import VisionSim
import ctre
import robotpy_ext.common_drivers.navx
from networktables import NetworkTables

# make the NavX work with the physics simulator
def createAnalogGyro():
    return wpilib.AnalogGyro(0)
robotpy_ext.common_drivers.navx.AHRS.create_spi = createAnalogGyro

class SimulatedTalon:

    def __init__(self, port, reverse, maxVel):
        self.port = port
        self.inv = -1 if reverse else 1
        self.maxVel = maxVel
        self.lastPosition = 0

    def getSpeed(self, data):
        if self.port == None:
            return 0.0
        try:
            talonData = data['CAN'][self.port]
            controlMode = talonData['control_mode']
            if controlMode == ctre.ControlMode.PercentOutput:
                value = talonData['value']
                if value < -1:
                    value = -1.0
                if value > 1:
                    value = 1.0
                talonData['quad_position'] += int(value * self.maxVel / 5)
                talonData['quad_velocity'] = int(value * self.maxVel) # update encoder
                return value * self.inv
            elif controlMode == ctre.ControlMode.Position:
                targetPos = talonData['pid0_target']
                diff = targetPos - self.lastPosition
                self.lastPosition = targetPos
                talonData['quad_position'] = targetPos # update encoder
                talonData['quad_velocity'] = int(diff * 5)
                return diff / self.maxVel * 5 * self.inv
            elif controlMode == ctre.ControlMode.Velocity:
                targetVel = talonData['pid0_target']
                talonData['quad_position'] += int(targetVel / 5) # update encoder
                talonData['quad_velocity'] = int(targetVel)
                return targetVel / self.maxVel * self.inv
            else:
                return 0.0
        except KeyError:
            return 0.0

class PhysicsEngine:

    def __init__(self, physicsController):
        self.physicsController = physicsController

        # NavX simulation
        self.physicsController.add_analog_gyro_channel(0)

        config = configparser.ConfigParser()
        filename = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep + "sim" + os.sep + "drivetrain.ini"
        print("Reading robot data from", filename)
        config.read(filename)

        if 'talons' in config:
            talons = config['talons']
        else:
            talons = { }
        self.simulatedTalons = { }
        for key, value in talons.items():
            num = int(key[len('talon'):])
            maxVel = float(value)
            self.simulatedTalons[num] = SimulatedTalon(num, maxVel < 0, abs(maxVel))

        if 'drivetrain' in config:
            drivetrain = config['drivetrain']
        else:
            drivetrain = { }
        self.xLen = float(drivetrain.get('xlen', '2'))
        self.yLen = float(drivetrain.get('ylen', '3'))
        self.speed = float(drivetrain.get('speed', '12'))
        self.drivetrain = drivetrain.get('drivetrain', 'mecanum')
        self.flMotor = int(drivetrain.get('flmotor', '-1'))
        self.frMotor = int(drivetrain.get('frmotor', '-1'))
        self.blMotor = int(drivetrain.get('blmotor', '-1'))
        self.brMotor = int(drivetrain.get('brmotor', '-1'))

        if 'ds' in config:
            ds = config['ds']
        else:
            ds = { }
        location = int(ds.get('location', '1'))
        team = 1 if (ds.get('team', 'red').lower() == 'blue') else 0
        self.allianceStation = location - 1 + team * 3

        if 'field' in config:
            field = config['field']
        else:
            field = { }
        self.visionX = float(field.get('visionx', '0'))
        self.visionY = float(field.get('visiony', '0'))
        self.visionAngleStart = float(field.get('visionanglestart', '90'))
        self.visionAngleEnd = float(field.get('visionangleend', '270'))

    def initialize(self, hal_data):
        self.visionTable = NetworkTables.getTable('limelight')
        self.visionTable.putNumber('tv', 1)
        self.visionTable.putNumber('tx', 0)
        self.visionTable.putNumber('ty', 0)
        self.visionTable.putNumber('ts', 0)
        self.visionTable.putNumber('ta', 5)

        visionTarget = VisionSim.Target(self.visionX, self.visionY,
                                        self.visionAngleStart,
                                        self.visionAngleEnd)
        self.visionSim = VisionSim([visionTarget], 60, 2, 50)
        hal_data['alliance_station'] = self.allianceStation

    def update_sim(self, data, time, elapsed):
        talonSpeeds = {-1: 0} # -1 for default talon values
        for num, simTalon in self.simulatedTalons.items():
            talonSpeeds[num] = simTalon.getSpeed(data)

        fl = talonSpeeds[self.flMotor]
        fr = talonSpeeds[self.frMotor]
        bl = talonSpeeds[self.blMotor]
        br = talonSpeeds[self.brMotor]

        if self.drivetrain == "mecanum":
            vx, vy, vw = drivetrains.mecanum_drivetrain(bl, br, fl, fr,
                self.xLen, self.yLen, self.speed)
            self.physicsController.vector_drive(vx, vy, vw, elapsed)
        elif self.drivetrain == "four":
            speed, rot = drivetrains.four_motor_drivetrain(bl, br, fl, fr,
                self.xLen, self.speed)
            self.physicsController.drive(speed, rot, elapsed)
        elif self.drivetrain == "two":
            speed, rot = drivetrains.two_motor_drivetrain(fl, fr,
                self.xLen, self.speed)
            self.physicsController.drive(speed, rot, elapsed)

        # https://github.com/robotpy/robotpy-wpilib/issues/291
        data['analog_gyro'][0]['angle'] = math.degrees(self.physicsController.angle)

        x, y, angle = self.physicsController.get_position()
        visionData = self.visionSim.compute(time, x, y, angle)
        if visionData is not None:
            targetData = visionData[0]
            self.visionTable.putNumber('tv', targetData[0])
            if targetData[0] != 0:
                self.visionTable.putNumber('tx', targetData[2])
        else:
            # DOESN'T mean no vision. vision just doesn't always update
            pass
