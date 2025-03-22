import numpy as np
from doplcommunicator import DepthCameraData, PointCloudChunk


def test_depthcameradata():
    # Setup
    point_1 = [1, 2, 3, 0, 0, 0] # (x, y, z, r, g, b)
    point_2 = [4, 5, 6, .1, .4, .2] # (x, y, z, r, g, b)
    point_cloud = [point_1, point_2]
    chunk_id = 1
    chunk = PointCloudChunk(chunk_id, point_cloud)
    chunks = [chunk]
    depthCameraData = DepthCameraData(chunks)

    # Test
    assert depthCameraData.point_cloud_chunks == chunks
    assert np.all(depthCameraData.point_cloud_chunks[0].point_cloud_chunk == point_cloud)

def test_fromDict():
    # Setup
    point_1 = [1, 2, 3, 0, 0, 0] # (x, y, z, r, g, b)
    point_2 = [4, 5, 6, .1, .4, .2] # (x, y, z, r, g, b)
    point_cloud = [point_1, point_2]
    chunk_id = 1

    depth_camera_data = {
        "point_cloud_chunks": [{
            "chunk_id": chunk_id,
            "point_cloud_chunk": point_cloud,
        }],
    }
    depthCameraData = DepthCameraData.fromDict(depth_camera_data)

    # Test
    assert depthCameraData.point_cloud_chunks[0].chunk_id == chunk_id
    assert np.all(depthCameraData.point_cloud_chunks[0].point_cloud_chunk == point_cloud)

def test_toDict():
    # Setup
    point_1 = [1, 2, 3, 0, 0, 0] # (x, y, z, r, g, b)
    point_2 = [4, 5, 6, .1, .4, .2] # (x, y, z, r, g, b)
    point_cloud = [point_1, point_2]
    chunk_id = 1
    chunk = PointCloudChunk(chunk_id, point_cloud)
    chunks = [chunk]
    depthCameraData = DepthCameraData(chunks)
    depth_camera_dict = depthCameraData.toDict()

    # Test
    assert depth_camera_dict["point_cloud_chunks"][0]["chunk_id"] == chunk_id
    assert np.all(depth_camera_dict["point_cloud_chunks"][0]["point_cloud_chunk"] == point_cloud)
