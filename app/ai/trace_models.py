# app/ai/trace_models.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class RetrievedItem(BaseModel):
    id: str
    title: str
    origin: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    tags: List[str] = []
    flavor_profiles: List[str] = []
    dietary_features: List[str] = []


class ParsedFilters(BaseModel):
    origin: Optional[str] = None
    category: Optional[str] = None
    flavor_profiles: Optional[List[str]] = None
    dietary_features: Optional[str] = None
    price_max: Optional[float] = None


class AIDebugTrace(BaseModel):
    user_message: str
    agent: str
    filters: ParsedFilters
    retrieved_items: List[RetrievedItem]
    llm_system_prompt: str
    llm_final_answer: str
    raw_filter_json: Dict[str, Any] = {}
    notes: Optional[str] = None