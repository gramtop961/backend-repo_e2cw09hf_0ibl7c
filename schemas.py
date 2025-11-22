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

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

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

# Real-estate analysis schema
class PropertyAnalysis(BaseModel):
    """
    Stores analysis results for an uploaded property package.
    Collection name: "propertyanalysis"
    """
    property_name: Optional[str] = Field(None, description="Property name or identifier")
    purchase_price: Optional[float] = Field(None, ge=0, description="Assumed purchase price")

    files: Dict[str, Any] = Field(default_factory=dict, description="Uploaded file metadata: name, size, type")

    # Key outputs derived from parsing
    units_total: Optional[int] = Field(None, ge=0)
    units_occupied: Optional[int] = Field(None, ge=0)
    occupancy_rate: Optional[float] = Field(None, ge=0, le=1)
    avg_rent: Optional[float] = Field(None, ge=0)

    t12_income: Optional[float] = Field(None, ge=0)
    t12_expense: Optional[float] = Field(None, ge=0)
    noi: Optional[float] = Field(None)
    cap_rate: Optional[float] = Field(None, ge=0)
    dscr: Optional[float] = Field(None, ge=0)

    om_price_hint: Optional[float] = Field(None, ge=0, description="Price parsed from OM if available")
    notes: Optional[str] = None

    status: str = Field("completed", description="Status of analysis")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!
