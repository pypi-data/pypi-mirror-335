from doplcommunicator import Vector3, Quaternion, ControllerData

def test_controllerdata():
    # Setup
    enabled = True
    position = Vector3(1, 2, 3)
    rotation = Quaternion(0.1, 0.2, 0.3, 1)
    force = Vector3(0, 0, 1)
    targetForce = 1
    controllerData = ControllerData(enabled, position, rotation, force, targetForce)

    # Test
    assert controllerData.enabled == enabled
    assert controllerData.position == position
    assert controllerData.rotation == rotation
    assert controllerData.force == force
    assert controllerData.targetForce == targetForce