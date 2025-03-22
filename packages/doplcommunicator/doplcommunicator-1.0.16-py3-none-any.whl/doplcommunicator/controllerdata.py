from .vector3 import Vector3
from .quaternion import Quaternion

class ControllerData():
    def __init__(self, enabled: bool, position: Vector3, rotation: Quaternion, force: Vector3, targetForce: int):
        self.enabled = enabled
        self.position = position
        self.rotation = rotation
        self.force = force
        self.targetForce = targetForce

    @staticmethod
    def fromDict(controller_data):
        return ControllerData(
            controller_data["enabled"],
            Vector3.fromDict(controller_data["position"]),
            Quaternion.fromDict(controller_data["rotation"]),
            Vector3.fromDict(controller_data["force"]),
            controller_data["targetForce"])

    def toDict(self):
        return {
            "enabled": self.enabled,
            "position": self.position.toDict(),
            "rotation": self.rotation.toDict(),
            "force": self.force.toDict(),
            "targetForce": self.targetForce
        }

    def __eq__(self, other): 
        if not isinstance(other, ControllerData):
            # don't attempt to compare against unrelated types
            return NotImplemented
        
        return self.enabled == other.enabled and \
            self.position == other.position and \
            self.rotation == other.rotation and \
            self.targetForce == other.targetForce