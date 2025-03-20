from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from bayes.client.gear_client import Link


class DatasetVersion(BaseModel):
    id: Optional[str] = None
    version: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    size: Optional[float] = None
    deletedAt: Optional[datetime] = None
    semanticBindingName: Optional[str] = None
    createdAt: Optional[datetime] = None

    links: Optional[List[Link]] = []

    def deletedString(self):
        if self.deletedAt is not None:
            return "Deleted"
        else:
            return ""

    def get_link_value(self, link_name: str) -> Optional[str]:
        for link in self.links:
            if link.name == link_name:
                return link.value
        return None


class PublicDatasetVersions(BaseModel):
    data: List[DatasetVersion]

