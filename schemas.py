"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Wallpaper marketplace schemas

class ResolutionLinks(BaseModel):
    mobile: Optional[HttpUrl] = Field(None, description="Direct URL for mobile resolution (e.g., 1080x2400)")
    desktop: Optional[HttpUrl] = Field(None, description="Direct URL for desktop/4K resolution (e.g., 3840x2160)")

class Wallpaper(BaseModel):
    """
    Wallpapers collection schema
    Collection name: "wallpaper"
    """
    title: str = Field(..., description="Wallpaper title")
    anime: str = Field(..., description="Anime name or series")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    thumbnail_url: HttpUrl = Field(..., description="Preview/thumbnail image URL")
    image_urls: ResolutionLinks = Field(..., description="Download URLs by device type")
    is_premium: bool = Field(False, description="Whether this wallpaper requires purchase")
    price: float = Field(0.0, ge=0, description="Price in USD if premium")
    author: Optional[str] = Field(None, description="Artist/Uploader name")
    color_palette: List[str] = Field(default_factory=list, description="Dominant colors (hex)")
    aspect_ratio: Optional[str] = Field(None, description="e.g., 16:9, 21:9, 9:16")
    downloads: int = Field(0, ge=0, description="Download count")
