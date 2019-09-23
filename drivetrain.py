import seamonsters as sea 
import rev
from gear import DriveGear
import math

def initDrivetrain():
    superDrive = sea.SuperHolonomicDrive()
    _makeWheel(superDrive, 1, rev.MotorType.kBrushless, -1, 0)
    _makeWheel(superDrive, 2, rev.MotorType.kBrushless, 1, 0)
    sea.setSimulatedDrivetrain(superDrive)
    return superDrive

def _makeWheel(superDrive, sparkMaxNum, motorType, xPos, yPos):
    sparkMax = rev.CANSparkMax(sparkMaxNum, motorType)
    sparkMax.restoreFactoryDefaults()
    sparkMax.setIdleMode(rev.IdleMode.kBrake)

    angledWheel = sea.AngledWheel(sparkMax, xPos, yPos, math.radians(90), 1, 16)

    superDrive.addWheel(angledWheel)

# drive gears 
# TODO: update the pids based on speed and adjust move/turn scales
# also, add pids velocity once Nathan figures them out

slowVoltageGear = DriveGear("Slow Voltage", rev.ControlType.kVoltage,
    moveScale=4, turnScale=math.radians(90))
mediumVoltageGear = DriveGear("Medium Voltage", rev.ControlType.kVoltage,
    moveScale=8, turnScale=math.radians(180))
fastVoltageGear = DriveGear("Fast Voltage", rev.ControlType.kVoltage,
    moveScale=14, turnScale=math.radians(270))

slowVelocityGear = DriveGear("Slow Velocity", rev.ControlType.kVoltage,
    moveScale=4, turnScale=math.radians(90),
    p=0.0, i=0.0, d=0.0, f=0.0)
mediumVelocityGear = DriveGear("Medium Velocity", rev.ControlType.kVoltage,
    moveScale=8, turnScale=math.radians(180),
    p=0.0, i=0.0, d=0.0, f=0.0)
fastVelocityGear = DriveGear("Fast Velocity", rev.ControlType.kVoltage,
    moveScale=14, turnScale=math.radians(270),
    p=0.0, i=0.0, d=0.0, f=0.0)

slowPositionGear = DriveGear("Slow Position", rev.ControlType.kPosition,
    moveScale=4, turnScale=math.radians(90),
    p=0.5, i=0.0, d=3.0, f=0.0)
mediumPositionGear = DriveGear("Medium Position", rev.ControlType.kPosition,
    moveScale=8, turnScale=math.radians(180),
    p=0.5, i=0.0, d=3.0, f=0.0)
fastPositionGear = DriveGear("Fast Position", rev.ControlType.kPosition,
    moveScale=14, turnScale=math.radians(270),
    p=0.5, i=0.0, d=3.0, f=0.0)