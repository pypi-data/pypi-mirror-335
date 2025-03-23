import os

import pytest
from dotenv import load_dotenv

from liquid_earth_sdk.api import le_api

load_dotenv()

user_token = os.environ.get("LIQUID_EARTH_API_TOKEN")

pytestmark = pytest.mark.core


def test_dxf_mesh_to_existing_space():
    import subsurface as ss
    from subsurface.modules.reader import dxf_file_to_unstruct_input
    import pandas

    path = os.environ.get("PATH_TO_DXF_DATA_PATH_SMALL")
    vertex, cells, cell_attr_int, cell_attr_map = dxf_file_to_unstruct_input(path)

    unstruct = ss.UnstructuredData.from_array(
        vertex,
        cells,
        cells_attr=pandas.DataFrame(cell_attr_int, columns=["Id"]),
        xarray_attributes={"cell_attr_map": cell_attr_map},
    )

    if False:
        ts = ss.TriSurf(mesh=unstruct)
        s = ss.visualization.to_pyvista_mesh(ts)
        ss.visualization.pv_plot([s], image_2d=False)

    if True:
        link = le_api.upload_mesh_to_existing_space(
            space_name="[TEMP] DXF From SDK",
            data=unstruct,
            file_name="dxf",
            token=user_token,
            grab_link=False
        )


def test_mx_mesh_to_existing_space():
    import subsurface as ss
    from subsurface.modules.reader.mesh.mx_reader import mx_to_unstruct_from_file
    unstruct: ss.UnstructuredData = mx_to_unstruct_from_file(os.getenv("PATH_TO_MX"))

    if False:
        ts = ss.TriSurf(mesh=unstruct)
        s = ss.visualization.to_pyvista_mesh(ts)
        ss.visualization.pv_plot([s], image_2d=True)

    link = le_api.upload_mesh_to_existing_space(
        space_name="[TEMP] MX From SDK",
        data=unstruct,
        file_name="mx_file",
        token=user_token
    )
