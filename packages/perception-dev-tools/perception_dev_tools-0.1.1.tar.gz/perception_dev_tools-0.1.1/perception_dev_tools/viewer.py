#! /bin/env python3
# viewer.py
import open3d as o3d
import fire
from pathlib import Path


def viewer(path:Path):
    mesh = mesh = o3d.io.read_triangle_mesh(path)
    mesh.compute_vertex_normals()
    o3d.visualization.draw_geometries([mesh])

if __name__ == "__main__":
    fire.Fire(viewer)