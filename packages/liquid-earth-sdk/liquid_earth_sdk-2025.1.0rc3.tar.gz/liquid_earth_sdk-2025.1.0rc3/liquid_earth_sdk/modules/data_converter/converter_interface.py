import subsurface as ss
import gempy as gp


def gempy_to_subsurface(geomodel: gp.data.GeoModel) -> ss.UnstructuredData:
    meshes: ss.UnstructuredData = geomodel.solutions.raw_arrays.meshes_to_subsurface()
    return meshes
