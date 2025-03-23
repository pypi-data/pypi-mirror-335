import dataclasses
from typing import Optional
from pydantic import BaseModel


class AvailableProject(BaseModel):
    CreationDate: str
    DisplayedOwner: str
    Name: str
    OwnerId: str
    SpaceId: str


@dataclasses.dataclass
class ServerResponse:
    deep_link: str = None
    available_projects: Optional[list[AvailableProject]] = None
    selected_project: Optional[AvailableProject] = None
    
    
