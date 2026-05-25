from pydantic import BaseModel , Field


class BreifInp_(BaseModel):
    animal_type: str = Field(... , description="For the animal type")
    brief_explanation : str = Field(... , description="Few Decription about the animal")

