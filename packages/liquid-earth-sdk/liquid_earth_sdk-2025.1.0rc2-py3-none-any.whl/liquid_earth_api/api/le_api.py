from typing import Union, Optional
import subsurface
from . import _utils_api
from liquid_earth_api.core.data.schemas import AddDataPostData, AddNewSpacePostData, DeleteSpacePostData
from ..core.output import ServerResponse, AvailableProject
from ..modules.rest_client import rest_interface
from ..modules.blob_client import blob_interface

import os


def set_token(token: str):
    # Check that the first 3 characters are le-
    if token[:3] != 'le-':
        raise ValueError('The token is invalid. Generate a new token from the LiquidEarth WebApp')

    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(f'LIQUID_EARTH_TOKEN={token}\n')
    else:
        with open('.env', 'a') as f:
            f.write(f'LIQUID_EARTH_TOKEN={token}\n')


def upload_mesh_to_existing_space(space_name: str, data: subsurface.UnstructuredData, file_name: str,
                                  token: str, grab_link: bool = True) -> ServerResponse:

    # * Make sure file name does not contain .le
    if file_name.endswith('.le'):
        file_name = file_name[:-3]

    # * grab space
    available_projects: list[AvailableProject] = get_available_projects(token)

    # ? which type is actually returned here?a
    found_project:AvailableProject = _utils_api.find_space_item(
        all_projects=available_projects,
        space_name=space_name
    )

    link: Optional[str] = _upload_mesh_common(
        data=data,
        file_name=file_name,
        found_project=found_project,
        grab_link=grab_link,
        token=token
    )

    server_response = ServerResponse(
        deep_link=link,
        available_projects=available_projects,
        selected_project=found_project
    )

    return server_response


def upload_mesh_to_new_space(space_name: str, data: subsurface.UnstructuredData,
                             file_name: str, token: str, grab_link: bool = True) -> ServerResponse:
    post_data = AddNewSpacePostData(spaceName=space_name)
    new_project = rest_interface.post_create_space(post_data, token)
    available_project = AvailableProject(**new_project)
    
    link: Optional[str] = _upload_mesh_common(data, file_name, available_project, grab_link, token)
    server_response = ServerResponse(
        deep_link=link,
        available_projects=[available_project],
        selected_project=available_project
    )

    return server_response


def get_deep_link(post_data: AddDataPostData, token: str) -> str:
    return rest_interface.get_deep_link(post_data, token)


def get_available_projects(token: str):
    return rest_interface.get_available_projects(token)


def delete_space(delete_space_post_data: DeleteSpacePostData, token: str) -> dict:
    return rest_interface.delete_space(delete_space_post_data, token)


def _upload_mesh_common(data: "subsurface.UnstructuredData", file_name: str, found_project: AvailableProject,
                        grab_link: bool, token: str) -> Optional[str]:
    post_data: AddDataPostData = AddDataPostData(
        spaceId=found_project.SpaceId,
        ownerId=found_project.OwnerId,
        dataType="static_mesh",
        fileName=file_name
    )
    sas_dict: dict = rest_interface.post_add_data_to_space(post_data, token)
    if not sas_dict.get("sasForTestLe"):
        raise ValueError("Missing required SAS token in sas_dict")

    _ = blob_interface.push_unstructured_data(
        unstructured_data=data,
        sas=sas_dict["sasForTestLe"]
    )

    # * Grab link
    if grab_link:
        link = get_deep_link(post_data, token)
    else:
        link = None

    return link
