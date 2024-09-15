from typing import List

from pydantic import BaseModel


class EntitiesDTO(BaseModel):
    """
    Represents the DTO, for entities, holding a dictionary with several elements.
    """

    person: List[str]
    object: List[str]
    animal: List[str]
    plant: List[str]
