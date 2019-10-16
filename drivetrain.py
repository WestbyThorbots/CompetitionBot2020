import seamonsters as sea 
import rev
from gear import DriveGear
import math

def initDrivetrain():
    superDrive = sea.SuperHolonomicDrive()

    # 3 motors per wheel but wheels cannot have the same position so 
    # add a small amount to it to make it work
    _makeWheel(superDrive, 1, 2, 3, rev.MotorType.kBrushless, 1, 0)
    _makeWheel(superDrive, 4, 5, 6, rev.MotorType.kBrushless, -1, 0)
    sea.setSimulatedDrivetrain(superDrive)
    return superDrive

def _makeWheel(superDrive, sparkMaxNum1, sparkMaxNum2, sparkMaxNum3, motorType, xPos, yPos):
    sparkMax1 = rev.CANSparkMax(sparkMaxNum1, motorType)
    sparkMax2 = rev.CANSparkMax(sparkMaxNum2, motorType)
    sparkMax3 = rev.CANSparkMax(sparkMaxNum3, motorType)
    for sparkMax in [sparkMax1, sparkMax2, sparkMax3]:
        sparkMax.restoreFactoryDefaults()
        sparkMax.setIdleMode(rev.IdleMode.kBrake)

    # encoderCountsPerFoot:
    # 1 count per encoder revolution
    # 1 : 1 gear ratio
    # 1 * 1 = 1 counts per wheel rotation
    # Wheel diameter: 4 in.
    # Wheel circumference: 4 * pi / 12 = 1.04720 ft
    # 1 / 1.04720 = 0.95493 counts per foot

    # maxVoltageVelocity = 5 ft per second * 60 seconds = 300 rpm
    angledWheel = sea.AngledWheel(sparkMax1, xPos, yPos, math.radians(90), 0.95493, 300)
    angledWheel.addMotor(sparkMax2)
    angledWheel.addMotor(sparkMax3)

    superDrive.addWheel(angledWheel)

# drive gears 
# TODO: update the pids based on speed and adjust move/turn scales
# slow gear is set to max because the shifting gearbox slows it down

slowVoltageGear = DriveGear("Slow Voltage", rev.ControlType.kVoltage, gearRatio=4, moveScale=250)
mediumVoltageGear = DriveGear("Medium Voltage", rev.ControlType.kVoltage, gearRatio=1, moveScale=150)
fastVoltageGear = DriveGear("Fast Voltage", rev.ControlType.kVoltage, gearRatio=1, moveScale=250)

slowVelocityGear = DriveGear("Slow Velocity", rev.ControlType.kVelocity,
    gearRatio=4, moveScale=14, p=0.000067, i=0.0000015, d=0.00035, f=0.0)
mediumVelocityGear = DriveGear("Medium Velocity", rev.ControlType.kVelocity,
    gearRatio=1, moveScale=8, p=0.000067, i=0.0000015, d=0.00035, f=0.0)
fastVelocityGear = DriveGear("Fast Velocity", rev.ControlType.kVelocity,
    gearRatio=1, moveScale=14, p=0.000067, i=0.0000015, d=0.00035, f=0.0)

slowPositionGear = DriveGear("Slow Position", rev.ControlType.kPosition,
    gearRatio=4, moveScale=14, p=0.5, i=0.0, d=3.0, f=0.0)
mediumPositionGear = DriveGear("Medium Position", rev.ControlType.kPosition,
    gearRatio=1, moveScale=8, p=0.5, i=0.0, d=3.0, f=0.0)
fastPositionGear = DriveGear("Fast Position", rev.ControlType.kPosition,
    gearRatio=1, moveScale=14, p=0.5, i=0.0, d=3.0, f=0.0)