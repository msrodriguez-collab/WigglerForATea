import time

from servo import Servo


class CupArm:
    def __init__(self, shoulder_pin, arm_pin, gripper_pin):
        self.shoulder = Servo(shoulder_pin)
        self.arm = Servo(arm_pin)
        self.gripper = Servo(gripper_pin)

        self.shoulder_angle = 90
        self.arm_angle = 90
        self.gripper_angle = 90

        self.set_joint_angles(shoulder=90, arm=90, gripper=90)

    def set_joint_angles(self, shoulder=None, arm=None, gripper=None):
        if shoulder is not None:
            self.shoulder_angle = shoulder
        if arm is not None:
            self.arm_angle = arm
        if gripper is not None:
            self.gripper_angle = gripper

        self.shoulder.set_pos(self.shoulder_angle)
        self.arm.set_pos(self.arm_angle)
        self.gripper.set_pos(self.gripper_angle)

    def move_slowly(self, shoulder=None, arm=None, gripper=None, step=1, delay=0.05):
        targets = {
            "shoulder": self.shoulder_angle if shoulder is None else shoulder,
            "arm": self.arm_angle if arm is None else arm,
            "gripper": self.gripper_angle if gripper is None else gripper,
        }

        for name, target in targets.items():
            current = getattr(self, f"{name}_angle")
            if current == target:
                continue

            direction = 1 if target > current else -1
            for angle in range(current, target + direction, direction * step):
                setattr(self, f"{name}_angle", angle)
                getattr(self, name).set_pos(angle)
                time.sleep(delay)

        self.shoulder_angle = targets["shoulder"]
        self.arm_angle = targets["arm"]
        self.gripper_angle = targets["gripper"]

    def open_gripper(self):
        self.gripper.set_pos(30)
        self.gripper_angle = 30

    def close_gripper(self):
        self.gripper.set_pos(120)
        self.gripper_angle = 120

    def reset(self):
        self.set_joint_angles(shoulder=90, arm=90, gripper=90)

    def cleanup(self):
        self.shoulder.stop()
        self.arm.stop()
        self.gripper.stop()


if __name__ == "__main__":
    # These are hardware PWM channels, not software GPIO PWM channels.
    cup_arm = CupArm(2, 3, 4)
    cup_arm.move_slowly(shoulder=40, arm=120, gripper=30, step=2, delay=0.05)
    cup_arm.open_gripper()
    cup_arm.close_gripper()
    cup_arm.reset()
    cup_arm.cleanup()