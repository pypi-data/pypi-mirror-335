from dotenv import load_dotenv

load_dotenv()

from liquid_earth_api.api.le_api import (
    upload_mesh_to_existing_space,
    upload_mesh_to_new_space,
    get_available_projects,
    get_deep_link
)
