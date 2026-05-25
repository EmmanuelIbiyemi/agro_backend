from pydantic import BaseModel , Field


class RegisterRequest(BaseModel):
    # farmer_id: str = Field(..., description="Unique identifier for the farmer")
    farm_name: str = Field(..., description="Name of the farm")
    farm_email: str = Field(..., description="Email address of the farm")
    farm_livestocks: int = Field(... , description = "Number of livestocks in the farm")
    password: str = Field(... , description= "Password")

class LoginRequest(BaseModel):
    farm_email: str = Field(... , description="Farm Email for the user to login")
    farm_password : str = Field(... , description="Farm Password For the farm")