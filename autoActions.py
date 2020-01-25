import math, coordinates, drivetrain
from autoScheduler import Action
import seamonsters as sea

def driveToPoint(pathFollower, coord, speed):
    drivetrain.mediumVelocityGear.applyGear(pathFollower.drive)

    yield from sea.ensureTrue(
        pathFollower.driveToPointGenerator(coord.x, coord.y, 1, math.radians(10)), 25)

def createDriveToPointAction(pathFollower, coord, speed):
    return Action("Drive to " + coord.name,
        lambda: driveToPoint(pathFollower, coord, speed), coord)

def rotateInPlace(pathFollower, angle):
    coord = coordinates.FieldCoordinate("Rotated",
        pathFollower.robotX, pathFollower.robotY, angle)
    yield from driveToPoint(pathFollower, coord, 5)

def createRotateInPlaceAction(pathFollower, angle):
    return Action("Rotate to " + str(round(math.degrees(angle))),
        lambda: rotateInPlace(pathFollower, angle))

def waitOneSecond():
    yield from sea.wait(sea.ITERATIONS_PER_SECOND)

def endAuto(robot):
    yield
    robot.manualMode()

def createEndAction(robot):
    return Action("END", lambda: endAuto(robot))

def createGenericAutoActions(robot):
    return [
        createEndAction(robot),
        Action("Wait 1 sec", waitOneSecond)
    ]