from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum

# Quote status enum
class QuoteStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    DECLINED = "declined"

# Quote item base
class QuoteItemBase(BaseModel):
    description: str
    details: Optional[str] = None
    quantity: float
    unit_price: float
    total_price: Optional[float] = None
    element_id: Optional[int] = None

# Quote item create
class QuoteItemCreate(QuoteItemBase):
    pass

# Quote item in DB
class QuoteItemInDB(QuoteItemBase):
    id: int
    quote_id: int

    class Config:
        orm_mode = True

# Quote base
class QuoteBase(BaseModel):
    title: str
    status: QuoteStatus = QuoteStatus.DRAFT
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    notes: Optional[str] = None
    tax_rate: float = 0.0
    discount_percentage: float = 0.0
    project_id: int

# Quote create
class QuoteCreate(QuoteBase):
    subtotal_amount: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    expiry_date: Optional[datetime] = None
    client_id: Optional[int] = None
    items: List[QuoteItemCreate]

# Quote update
class QuoteUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[QuoteStatus] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_phone: Optional[str] = None
    notes: Optional[str] = None
    tax_rate: Optional[float] = None
    discount_percentage: Optional[float] = None
    subtotal_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    discount_amount: Optional[float] = None
    total_amount: Optional[float] = None
    expiry_date: Optional[datetime] = None
    client_id: Optional[int] = None

# Quote in DB base
class QuoteInDBBase(QuoteBase):
    id: int
    subtotal_amount: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    created_at: datetime
    updated_at: datetime
    expiry_date: Optional[datetime] = None
    client_id: Optional[int] = None
    created_by: int

    class Config:
        orm_mode = True

# Quote response
class Quote(QuoteInDBBase):
    pass

# Quote with items
class QuoteWithItems(Quote):
    items: List[QuoteItemInDB] = []

# Quote activity
class QuoteActivity(BaseModel):
    id: int
    action: str
    notes: Optional[str] = None
    timestamp: datetime
    user_id: Optional[int] = None
    quote_id: int

    class Config:
        orm_mode = True

# Quote with items and activities
class QuoteDetail(QuoteWithItems):
    activities: List[QuoteActivity] = []

# Quote status update
class QuoteStatusUpdate(BaseModel):
    status: QuoteStatus

# Quote summary stats
class QuoteSummary(BaseModel):
    total_quotes: int
    by_status: dict
    total_value: float
    recent_quotes: List[Quote] = []