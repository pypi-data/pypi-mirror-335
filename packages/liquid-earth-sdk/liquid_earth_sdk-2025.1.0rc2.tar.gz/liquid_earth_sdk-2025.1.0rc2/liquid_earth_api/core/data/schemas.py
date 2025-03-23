from dataclasses import dataclass


@dataclass
class AddDataPostData:
    spaceId: str
    ownerId: str
    dataType: str
    fileName: str
    
    
@dataclass
class AddNewSpacePostData:
    spaceName: str
    
    
@dataclass
class DeleteSpacePostData:
    spaceId: str