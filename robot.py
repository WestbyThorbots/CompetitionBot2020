import wpilib
import drivetrain
import seamonsters as sea 
import math

class CompetitionBot2020(sea.GeneratorBot):

    def robotInit(self):

        # joysticks
        self.joystick = wpilib.Joystick(0)
        self.buttonBoard = wpilib.Joystick(1)

        self.superDrive = drivetrain.initDrivetrain()

        # drive gears
        self.superDrive.gear = None
        self.driveGear = drivetrain.slowVoltageGear
        self.driveMode = "voltage"
        self.driveSpeed = "slow"
        self.driveGears = \
            {"voltage" : \
                {"slow" : drivetrain.slowVoltageGear, 
                "medium" : drivetrain.mediumVoltageGear, 
                "fast" : drivetrain.fastVoltageGear}, 
            "velocity" : \
                {"slow" : drivetrain.slowVelocityGear, 
                "medium" : drivetrain.mediumVelocityGear, 
                "fast" : drivetrain.fastVelocityGear},      
            "position" : \
                {"slow" : drivetrain.slowPositionGear, 
                "medium" : drivetrain.mediumPositionGear, 
                "fast" : drivetrain.fastPositionGear} 
            }

    def teleop(self):
        yield from sea.parallel(self.drive(), self.buttonControl())

    def drive(self):
        while True:

            if self.superDrive.gear != self.driveGear:
                self.driveGear.applyGear(self.superDrive)

            mag = sea.deadZone(self.joystick.getY()) 
            mag *= self.driveGear.moveScale # maximum feet per second
            turn = sea.deadZone(self.joystick.getX())
            turn *= self.driveGear.turnScale # maximum radians per second

            self.superDrive.drive(mag, math.pi/2, turn)

            yield

    def buttonControl(self):
        # clears events on buttons
        for button in range(1, 11):
            self.buttonBoard.getRawButtonPressed(button)

        while True:

            if self.buttonBoard.getRawButtonPressed(3):
                self.driveSpeed = "slow"
            elif self.buttonBoard.getRawButtonPressed(4):
                self.driveSpeed = "medium"
            elif self.buttonBoard.getRawButtonPressed(5):
                self.driveSpeed = "fast"

            if self.buttonBoard.getRawButtonPressed(2):
                self.toggleDriveMode()

            self.driveGear = self.driveGears[self.driveMode][self.driveSpeed]

            yield

    def toggleDriveMode(self):
        if self.driveMode == "voltage":
            self.driveMode = "velocity"
        elif self.driveMode == "velocity":
            self.driveMode = "position"
        else:
            self.driveMode = "voltage"

if __name__ == "__main__":
    wpilib.run(CompetitionBot2020)