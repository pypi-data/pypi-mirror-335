import pytest
from subsurface import optional_requirements

from liquid_earth_sdk.api import le_api
from liquid_earth_sdk.core.data.schemas import DeleteSpacePostData
from liquid_earth_sdk.core.output import ServerResponse
from .test_le_api_test_cases import TestLEApiBase


class TestLEApiWithGempy(TestLEApiBase):
    """Tests that require GemPy"""
    _space_id: str = None
    
    @classmethod
    def setup_class(cls):
        super().setup_class()
        import gempy as gp
        from gempy.core.data.enumerators import ExampleModel
        cls.gempy_model = gp.generate_example_model(ExampleModel.ANTICLINE, compute_model=True)
        
     
    @classmethod
    def teardown_class(cls):
        """Deletes the created space after the tests"""
        if cls._space_id is not None:
            le_api.delete_space(
                delete_space_post_data=DeleteSpacePostData(spaceId=cls._space_id),
                token=cls.user_token
            )

    @pytest.mark.skip(reason="Run this explicitly")
    def test_upload_mesh_to_existing_space(self):
        ss = optional_requirements.require_subsurface()
        subsurface: ss.UnstructuredData = self.gempy_model.solutions.raw_arrays.meshes_to_subsurface()
        name = self.space_name
        token = self.user_token
        
        server_response: ServerResponse = le_api.upload_mesh_to_existing_space(
            space_name="[TEMP] Test python api",
            data=subsurface,
            file_name="anticline",
            token=token
        )
        assert server_response is not None

    def test_upload_mesh_to_new_space(self):
        server_response = le_api.upload_mesh_to_new_space(
            space_name="[TEMP] Test python api",
            data=self.gempy_model.solutions.raw_arrays.meshes_to_subsurface(),
            file_name="anticline",
            token=self.user_token
        )
        assert server_response is not None
        
        TestLEApiWithGempy._space_id = server_response.selected_project.SpaceId
