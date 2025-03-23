from liquid_earth_sdk.core.output import AvailableProject


def find_space_item(all_projects: list[AvailableProject], space_name: str):
    found_project = None
    for project in all_projects:
        if project.Name == space_name:
            found_project = project
    if found_project is None:
        raise ValueError("Space not found in LiquidEarth user. Make sure the space exists or create a new one")
    return found_project
