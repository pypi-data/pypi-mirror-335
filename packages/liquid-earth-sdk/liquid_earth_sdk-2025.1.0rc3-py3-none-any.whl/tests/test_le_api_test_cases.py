import os
import pytest
from dotenv import load_dotenv
from liquid_earth_sdk.core.data.schemas import AddDataPostData, AddNewSpacePostData, DeleteSpacePostData
from liquid_earth_sdk.api import le_api, _utils_api
from liquid_earth_sdk.core.output import AvailableProject
from liquid_earth_sdk.modules.rest_client import rest_interface

load_dotenv()


@pytest.mark.core
class TestLEApiBase:
    """Base test class with common setup"""

    @classmethod
    def setup_class(cls):
        cls.user_token = os.environ.get("LIQUID_EARTH_API_TOKEN")
        cls.space_name = "[TEMP] Test python api"

    def _get_test_project(self, space_name: str) -> AddDataPostData:
        all_projects = le_api.get_available_projects(
            token=self.user_token
        )
        found_project = _utils_api.find_space_item(all_projects, space_name)
        post_data = AddDataPostData(
            spaceId=found_project["SpaceId"],
            ownerId=found_project["OwnerId"],
            dataType="static_mesh",
            fileName="test"
        )
        return post_data


class TestLEApiCore(TestLEApiBase):

    def test_get_available_projects(self):
        available_projects: list[AvailableProject] = le_api.get_available_projects(
            token=self.user_token
        )
        assert len(available_projects) > 0

    def test_new_space_get_link_delete_space(self):
        space = (AddNewSpacePostData(spaceName=self.space_name))
        response = rest_interface.post_create_space(space, self.user_token)
        assert response is not None

        # ! Here we are not uploading the binary that would be the normal process

        all_projects = le_api.get_available_projects(
            token=self.user_token
        )
        found_project: AvailableProject = _utils_api.find_space_item(all_projects, self.space_name)
        post_data = AddDataPostData(
            spaceId=found_project.SpaceId,
            ownerId=found_project.OwnerId,
            dataType="static_mesh",
            fileName="test"
        )
        deep_link = le_api.get_deep_link(
            post_data=post_data,
            token=self.user_token
        )
        assert deep_link is not None

        response = le_api.delete_space(
            delete_space_post_data=DeleteSpacePostData(spaceId=post_data.spaceId),
            token=self.user_token
        )

        assert response is not None
