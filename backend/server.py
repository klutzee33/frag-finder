from fastapi import FastAPI, APIRouter, HTTPException, Query
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import os
import json
import logging
import uuid
from datetime import datetime
import requests
import asyncio
from urllib.parse import quote
import re

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Fragrance Discounter Search Engine", version="1.0.0")
api_router = APIRouter(prefix="/api")

# Data models for Fragrance Search Engine
class Fragrance(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    brand: str
    gender: str  # "Men", "Women", "Unisex"
    type: str = "Eau de Parfum"  # EDP, EDT, Cologne, etc.
    size: str = "100ml"
    description: Optional[str] = None
    notes: Optional[List[str]] = []
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Discounter(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    website: str
    logo_url: Optional[str] = None
    description: Optional[str] = None
    active: bool = True

class FragrancePrice(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    fragrance_id: str
    discounter_id: str
    price: float
    currency: str = "USD"
    original_price: Optional[float] = None
    discount_percentage: Optional[int] = None
    availability: str = "In Stock"
    product_url: str
    last_updated: datetime = Field(default_factory=datetime.utcnow)

class SearchFilters(BaseModel):
    query: Optional[str] = None
    brand: Optional[str] = None
    gender: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    discounter: Optional[str] = None
    sort_by: str = "price_asc"  # price_asc, price_desc, name_asc, brand_asc
    limit: int = 20
    offset: int = 0

class SearchResult(BaseModel):
    fragrance: Fragrance
    prices: List[FragrancePrice]
    lowest_price: float
    highest_price: float
    discounter_count: int

class SearchResponse(BaseModel):
    results: List[SearchResult]
    total_count: int
    filters_applied: SearchFilters

# Sample data for demonstration
SAMPLE_DISCOUNTERS = [
    Discounter(
        id="1", 
        name="FragranceX", 
        website="https://www.fragrancex.com",
        description="Discount designer fragrances"
    ),
    Discounter(
        id="2", 
        name="FragranceNet", 
        website="https://www.fragrancenet.com",
        description="Authentic discounted perfumes"
    ),
    Discounter(
        id="3", 
        name="Jomashop", 
        website="https://www.jomashop.com",
        description="Luxury fragrances at discount prices"
    ),
    Discounter(
        id="4", 
        name="Perfume.com", 
        website="https://www.perfume.com",
        description="Designer and niche fragrances"
    )
]

SAMPLE_FRAGRANCES = [
    Fragrance(
        id="f1",
        name="Bleu de Chanel",
        brand="Chanel",
        gender="Men",
        type="Eau de Parfum",
        size="100ml",
        description="A woody aromatic fragrance with citrus and cedar notes",
        notes=["Grapefruit", "Lemon", "Mint", "Pink Pepper", "Ginger", "Nutmeg", "Cedar", "Sandalwood"],
        image_url="https://images.unsplash.com/photo-1541643600914-78b084683601?w=400"
    ),
    Fragrance(
        id="f2",
        name="Miss Dior",
        brand="Dior",
        gender="Women",
        type="Eau de Parfum",
        size="100ml",
        description="A floral fragrance with rose and patchouli",
        notes=["Blood Orange", "Mandarin", "Pink Pepper", "Rose", "Peony", "Iris", "Patchouli", "Rosewood"],
        image_url="https://images.unsplash.com/photo-1563170351-be82bc888aa4?w=400"
    ),
    Fragrance(
        id="f3",
        name="Sauvage",
        brand="Dior",
        gender="Men",
        type="Eau de Toilette",
        size="100ml",
        description="A fresh spicy fragrance inspired by wide-open spaces",
        notes=["Calabrian Bergamot", "Pepper", "Sichuan Pepper", "Lavender", "Pink Pepper", "Vetiver", "Cedar", "Labdanum"],
        image_url="https://images.unsplash.com/photo-1588405748880-12d1d2a59db9?w=400"
    ),
    Fragrance(
        id="f4",
        name="Black Opium",
        brand="Yves Saint Laurent",
        gender="Women",
        type="Eau de Parfum",
        size="90ml",
        description="An addictive gourmand fragrance with coffee and vanilla",
        notes=["Pink Pepper", "Orange Blossom", "Pear", "Coffee", "Jasmine", "Bitter Almond", "Licorice", "Vanilla", "Patchouli", "Cedar"],
        image_url="https://images.unsplash.com/photo-1594035910387-fea47794261f?w=400"
    ),
    Fragrance(
        id="f5",
        name="Acqua di Gio",
        brand="Giorgio Armani",
        gender="Men",
        type="Eau de Toilette",
        size="100ml",
        description="A fresh aquatic fragrance with marine notes",
        notes=["Lime", "Lemon", "Bergamot", "Jasmine", "Rose", "Rosemary", "Fruity Notes", "Musk", "Woody Notes", "Patchouli"],
        image_url="https://images.unsplash.com/photo-1585386959984-a4155224a1ad?w=400"
    ),
    Fragrance(
        id="f6",
        name="Coco Mademoiselle",
        brand="Chanel",
        gender="Women",
        type="Eau de Parfum",
        size="100ml",
        description="A fresh oriental fragrance with citrus and patchouli",
        notes=["Orange", "Mandarin Orange", "Orange Blossom", "Bergamot", "Rose", "Mimosa", "Jasmine", "Litchi", "Patchouli", "White Musk", "Vetiver", "Vanilla"],
        image_url="https://images.unsplash.com/photo-1595425970377-c9703cf48b6d?w=400"
    )
]

SAMPLE_PRICES = [
    # Bleu de Chanel prices
    FragrancePrice(id="p1", fragrance_id="f1", discounter_id="1", price=89.99, original_price=120.00, discount_percentage=25, product_url="https://fragrancex.com/bleu-chanel"),
    FragrancePrice(id="p2", fragrance_id="f1", discounter_id="2", price=92.50, original_price=120.00, discount_percentage=23, product_url="https://fragrancenet.com/bleu-chanel"),
    FragrancePrice(id="p3", fragrance_id="f1", discounter_id="3", price=95.00, original_price=120.00, discount_percentage=21, product_url="https://jomashop.com/bleu-chanel"),
    
    # Miss Dior prices
    FragrancePrice(id="p4", fragrance_id="f2", discounter_id="1", price=79.99, original_price=108.00, discount_percentage=26, product_url="https://fragrancex.com/miss-dior"),
    FragrancePrice(id="p5", fragrance_id="f2", discounter_id="2", price=82.00, original_price=108.00, discount_percentage=24, product_url="https://fragrancenet.com/miss-dior"),
    FragrancePrice(id="p6", fragrance_id="f2", discounter_id="4", price=85.50, original_price=108.00, discount_percentage=21, product_url="https://perfume.com/miss-dior"),
    
    # Sauvage prices
    FragrancePrice(id="p7", fragrance_id="f3", discounter_id="1", price=69.99, original_price=98.00, discount_percentage=29, product_url="https://fragrancex.com/sauvage"),
    FragrancePrice(id="p8", fragrance_id="f3", discounter_id="2", price=72.50, original_price=98.00, discount_percentage=26, product_url="https://fragrancenet.com/sauvage"),
    FragrancePrice(id="p9", fragrance_id="f3", discounter_id="3", price=74.99, original_price=98.00, discount_percentage=23, product_url="https://jomashop.com/sauvage"),
    
    # Black Opium prices
    FragrancePrice(id="p10", fragrance_id="f4", discounter_id="2", price=67.99, original_price=96.00, discount_percentage=29, product_url="https://fragrancenet.com/black-opium"),
    FragrancePrice(id="p11", fragrance_id="f4", discounter_id="3", price=71.00, original_price=96.00, discount_percentage=26, product_url="https://jomashop.com/black-opium"),
    FragrancePrice(id="p12", fragrance_id="f4", discounter_id="4", price=73.50, original_price=96.00, discount_percentage=23, product_url="https://perfume.com/black-opium"),
    
    # Acqua di Gio prices
    FragrancePrice(id="p13", fragrance_id="f5", discounter_id="1", price=54.99, original_price=76.00, discount_percentage=28, product_url="https://fragrancex.com/acqua-di-gio"),
    FragrancePrice(id="p14", fragrance_id="f5", discounter_id="2", price=57.50, original_price=76.00, discount_percentage=24, product_url="https://fragrancenet.com/acqua-di-gio"),
    
    # Coco Mademoiselle prices
    FragrancePrice(id="p15", fragrance_id="f6", discounter_id="1", price=94.99, original_price=132.00, discount_percentage=28, product_url="https://fragrancex.com/coco-mademoiselle"),
    FragrancePrice(id="p16", fragrance_id="f6", discounter_id="3", price=99.00, original_price=132.00, discount_percentage=25, product_url="https://jomashop.com/coco-mademoiselle"),
    FragrancePrice(id="p17", fragrance_id="f6", discounter_id="4", price=102.50, original_price=132.00, discount_percentage=22, product_url="https://perfume.com/coco-mademoiselle"),
]

def filter_fragrances(filters: SearchFilters) -> List[SearchResult]:
    """Filter and search fragrances based on criteria"""
    results = []
    
    for fragrance in SAMPLE_FRAGRANCES:
        # Text search in name, brand, or description
        if filters.query:
            query_lower = filters.query.lower()
            searchable_text = f"{fragrance.name} {fragrance.brand} {fragrance.description or ''}".lower()
            if query_lower not in searchable_text:
                continue
        
        # Brand filter
        if filters.brand and filters.brand.lower() != fragrance.brand.lower():
            continue
            
        # Gender filter
        if filters.gender and filters.gender.lower() != fragrance.gender.lower():
            continue
        
        # Get prices for this fragrance
        fragrance_prices = [p for p in SAMPLE_PRICES if p.fragrance_id == fragrance.id]
        
        # Apply discounter filter
        if filters.discounter:
            fragrance_prices = [p for p in fragrance_prices if p.discounter_id == filters.discounter]
        
        if not fragrance_prices:
            continue
            
        # Apply price filters
        min_price = min(p.price for p in fragrance_prices)
        max_price = max(p.price for p in fragrance_prices)
        
        if filters.min_price and max_price < filters.min_price:
            continue
        if filters.max_price and min_price > filters.max_price:
            continue
        
        results.append(SearchResult(
            fragrance=fragrance,
            prices=fragrance_prices,
            lowest_price=min_price,
            highest_price=max_price,
            discounter_count=len(fragrance_prices)
        ))
    
    # Sort results
    if filters.sort_by == "price_asc":
        results.sort(key=lambda x: x.lowest_price)
    elif filters.sort_by == "price_desc":
        results.sort(key=lambda x: x.lowest_price, reverse=True)
    elif filters.sort_by == "name_asc":
        results.sort(key=lambda x: x.fragrance.name)
    elif filters.sort_by == "brand_asc":
        results.sort(key=lambda x: x.fragrance.brand)
    
    # Apply pagination
    total_count = len(results)
    start_idx = filters.offset
    end_idx = start_idx + filters.limit
    results = results[start_idx:end_idx]
    
    return results, total_count

# API Routes
@api_router.get("/search", response_model=SearchResponse)
async def search_fragrances(
    query: Optional[str] = Query(None, description="Search term for fragrance name or brand"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    gender: Optional[str] = Query(None, description="Filter by gender (Men, Women, Unisex)"),
    min_price: Optional[float] = Query(None, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, description="Maximum price filter"),
    discounter: Optional[str] = Query(None, description="Filter by discounter ID"),
    sort_by: str = Query("price_asc", description="Sort by: price_asc, price_desc, name_asc, brand_asc"),
    limit: int = Query(20, description="Number of results per page"),
    offset: int = Query(0, description="Number of results to skip")
):
    """Search fragrances with filters"""
    filters = SearchFilters(
        query=query,
        brand=brand,
        gender=gender,
        min_price=min_price,
        max_price=max_price,
        discounter=discounter,
        sort_by=sort_by,
        limit=limit,
        offset=offset
    )
    
    results, total_count = filter_fragrances(filters)
    
    return SearchResponse(
        results=results,
        total_count=total_count,
        filters_applied=filters
    )

@api_router.get("/fragrances", response_model=List[Fragrance])
async def get_all_fragrances():
    """Get all available fragrances"""
    return SAMPLE_FRAGRANCES

@api_router.get("/fragrances/{fragrance_id}")
async def get_fragrance(fragrance_id: str):
    """Get specific fragrance with prices"""
    fragrance = next((f for f in SAMPLE_FRAGRANCES if f.id == fragrance_id), None)
    if not fragrance:
        raise HTTPException(status_code=404, detail="Fragrance not found")
    
    prices = [p for p in SAMPLE_PRICES if p.fragrance_id == fragrance_id]
    discounter_details = []
    
    for price in prices:
        discounter = next((d for d in SAMPLE_DISCOUNTERS if d.id == price.discounter_id), None)
        if discounter:
            discounter_details.append({
                "price_info": price,
                "discounter": discounter
            })
    
    return {
        "fragrance": fragrance,
        "price_comparison": discounter_details
    }

@api_router.get("/discounters", response_model=List[Discounter])
async def get_discounters():
    """Get all available discounters"""
    return SAMPLE_DISCOUNTERS

@api_router.get("/brands")
async def get_brands():
    """Get all available brands"""
    brands = list(set(f.brand for f in SAMPLE_FRAGRANCES))
    return sorted(brands)

@api_router.get("/popular")
async def get_popular_fragrances():
    """Get popular fragrances (based on number of discounters carrying them)"""
    fragrance_popularity = {}
    
    for price in SAMPLE_PRICES:
        if price.fragrance_id not in fragrance_popularity:
            fragrance_popularity[price.fragrance_id] = 0
        fragrance_popularity[price.fragrance_id] += 1
    
    # Sort by popularity
    popular_ids = sorted(fragrance_popularity.keys(), 
                        key=lambda x: fragrance_popularity[x], reverse=True)[:6]
    
    popular_fragrances = []
    for fragrance_id in popular_ids:
        fragrance = next((f for f in SAMPLE_FRAGRANCES if f.id == fragrance_id), None)
        if fragrance:
            prices = [p for p in SAMPLE_PRICES if p.fragrance_id == fragrance_id]
            min_price = min(p.price for p in prices) if prices else 0
            popular_fragrances.append({
                "fragrance": fragrance,
                "lowest_price": min_price,
                "discounter_count": len(prices)
            })
    
    return popular_fragrances

@api_router.get("/deals")
async def get_best_deals():
    """Get fragrances with the best discount percentages"""
    deals = []
    
    for fragrance in SAMPLE_FRAGRANCES:
        prices = [p for p in SAMPLE_PRICES if p.fragrance_id == fragrance.id]
        if prices:
            best_deal = max(prices, key=lambda p: p.discount_percentage or 0)
            deals.append({
                "fragrance": fragrance,
                "best_price": best_deal,
                "discounter": next((d for d in SAMPLE_DISCOUNTERS if d.id == best_deal.discounter_id), None)
            })
    
    # Sort by discount percentage
    deals.sort(key=lambda x: x["best_price"].discount_percentage or 0, reverse=True)
    
    return deals[:10]

# Health check
@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Fragrance Discounter Search Engine"}

# Include router
app.include_router(api_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)