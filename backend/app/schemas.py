from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

class ProfileIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    education: str = ""
    experience: str = ""
    skills: list[str] = Field(default_factory=list)
    target_role: str = ""
    location: str = ""

class JobIn(BaseModel):
    title: str = Field(min_length=2, max_length=120)
    company: str = Field(min_length=2, max_length=120)
    location: str = "Remote"
    job_type: str = "Full-time"
    description: str = ""
    skills: list[str] = Field(default_factory=list)
    salary: str = "Not disclosed"

class CompanyIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    industry: str = "Technology"
    location: str = "India"
    website: str = ""
    description: str = ""
