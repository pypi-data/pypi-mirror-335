from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
# Will need to import Profile or define it in this file

class User(BaseModel):
    username: str
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    score: Optional[int] = None
    age: Optional[int] = None = Field(ge=2, default=15)
    isActive: Optional[bool] = None = Field(default=True)
    createdAt: Optional[datetime] = None
    tags: Optional[List[str]] = None
    profile: Optional[Profile] = None

    class Config:
        orm_mode = True