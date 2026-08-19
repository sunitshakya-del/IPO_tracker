from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Header
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")


# ============ AUTH MODELS ============
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    user_id: str = Field(default_factory=lambda: f"user_{uuid.uuid4().hex[:12]}")
    email: str
    name: str
    picture: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ============ AUTH HELPER FUNCTIONS ============
async def get_current_user(request: Request, authorization: Optional[str] = Header(None)) -> dict:
    """Extract user from session_token (cookie or Authorization header)"""
    session_token = None
    
    # Try cookie first
    session_token = request.cookies.get("session_token")
    
    # Fallback to Authorization header
    if not session_token and authorization:
        if authorization.startswith("Bearer "):
            session_token = authorization.replace("Bearer ", "")
        else:
            session_token = authorization
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find session
    session_doc = await db.user_sessions.find_one(
        {"session_token": session_token},
        {"_id": 0}
    )
    
    if not session_doc:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check expiry
    expires_at = session_doc["expires_at"]
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    user_doc = await db.users.find_one(
        {"user_id": session_doc["user_id"]},
        {"_id": 0}
    )
    
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user_doc


class DematAccount(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Added for user isolation
    account_name: str
    broker_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DematAccountCreate(BaseModel):
    account_name: str
    broker_name: str

class DematAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    broker_name: Optional[str] = None


class IPO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Added for user isolation
    ipo_name: str
    lot_size: int
    application_price: float
    allotment_quantity: int
    listing_price: float
    sell_price: Optional[float] = None
    demat_account_id: str
    application_date: str
    listing_date: str
    broker_charges: float = 0
    profit_loss: float = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class IPOCreate(BaseModel):
    ipo_name: str
    lot_size: int
    application_price: float
    allotment_quantity: int
    listing_price: float
    sell_price: float
    demat_account_id: str
    application_date: str
    listing_date: str
    broker_charges: Optional[float] = 0

class IPOUpdate(BaseModel):
    ipo_name: Optional[str] = None
    lot_size: Optional[int] = None
    application_price: Optional[float] = None
    allotment_quantity: Optional[int] = None
    listing_price: Optional[float] = None
    sell_price: Optional[float] = None
    demat_account_id: Optional[str] = None
    application_date: Optional[str] = None
    listing_date: Optional[str] = None
    broker_charges: Optional[float] = None


@api_router.get("/")
async def root():
    return {"message": "IPO P&L Tracker API"}


# ============ AUTH ENDPOINTS ============
@api_router.post("/auth/session")
async def create_session(request: Request, response: Response):
    """Exchange session_id for session_token"""
    try:
        body = await request.json()
        session_id = body.get("session_id")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id required")
        
        # Call Emergent Auth API
        async with httpx.AsyncClient() as client:
            auth_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            
            if auth_response.status_code != 200:
                raise HTTPException(status_code=401, detail="Invalid session_id")
            
            user_data = auth_response.json()
        
        # Check if user exists
        existing_user = await db.users.find_one(
            {"email": user_data["email"]},
            {"_id": 0}
        )
        
        if existing_user:
            user_id = existing_user["user_id"]
            # Update user data
            await db.users.update_one(
                {"user_id": user_id},
                {"$set": {
                    "name": user_data["name"],
                    "picture": user_data.get("picture")
                }}
            )
        else:
            # Create new user
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                picture=user_data.get("picture")
            )
            user_doc = user.model_dump()
            user_doc['created_at'] = user_doc['created_at'].isoformat()
            await db.users.insert_one(user_doc)
            user_id = user.user_id
        
        # Create session
        session_token = user_data["session_token"]
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        session = UserSession(
            user_id=user_id,
            session_token=session_token,
            expires_at=expires_at
        )
        
        session_doc = session.model_dump()
        session_doc['created_at'] = session_doc['created_at'].isoformat()
        session_doc['expires_at'] = session_doc['expires_at'].isoformat()
        
        # Delete old sessions for this user
        await db.user_sessions.delete_many({"user_id": user_id})
        
        # Insert new session
        await db.user_sessions.insert_one(session_doc)
        
        # Set httpOnly cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
            max_age=7*24*60*60  # 7 days
        )
        
        # Get full user data
        user_doc = await db.users.find_one(
            {"user_id": user_id},
            {"_id": 0}
        )
        
        return {"user": user_doc, "message": "Session created"}
        
    except Exception as e:
        logging.error(f"Session creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/auth/me")
async def get_me(request: Request, authorization: Optional[str] = Header(None)):
    """Get current user from session"""
    user = await get_current_user(request, authorization)
    return user


@api_router.post("/auth/logout")
async def logout(request: Request, response: Response, authorization: Optional[str] = Header(None)):
    """Logout user"""
    try:
        user = await get_current_user(request, authorization)
        
        # Delete session
        session_token = request.cookies.get("session_token")
        if session_token:
            await db.user_sessions.delete_one({"session_token": session_token})
        
        # Clear cookie
        response.delete_cookie(
            key="session_token",
            path="/",
            secure=True,
            httponly=True,
            samesite="none"
        )
        
        return {"message": "Logged out successfully"}
    except HTTPException:
        # Even if not authenticated, clear cookie
        response.delete_cookie(
            key="session_token",
            path="/",
            secure=True,
            httponly=True,
            samesite="none"
        )
        return {"message": "Logged out"}


@api_router.post("/accounts", response_model=DematAccount)
async def create_account(account: DematAccountCreate, request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    account_obj = DematAccount(**account.model_dump(), user_id=user["user_id"])
    doc = account_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.demat_accounts.insert_one(doc)
    return account_obj

@api_router.get("/accounts", response_model=List[DematAccount])
async def get_accounts(request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    accounts = await db.demat_accounts.find({"user_id": user["user_id"]}, {"_id": 0}).to_list(1000)
    for account in accounts:
        if isinstance(account.get('created_at'), str):
            account['created_at'] = datetime.fromisoformat(account['created_at'])
    return accounts

@api_router.put("/accounts/{account_id}", response_model=DematAccount)
async def update_account(account_id: str, account: DematAccountUpdate, request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    existing = await db.demat_accounts.find_one({"id": account_id, "user_id": user["user_id"]}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Account not found")
    
    update_data = {k: v for k, v in account.model_dump().items() if v is not None}
    if update_data:
        await db.demat_accounts.update_one({"id": account_id, "user_id": user["user_id"]}, {"$set": update_data})
    
    updated = await db.demat_accounts.find_one({"id": account_id, "user_id": user["user_id"]}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    return DematAccount(**updated)

@api_router.delete("/accounts/{account_id}")
async def delete_account(account_id: str, request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    result = await db.demat_accounts.delete_one({"id": account_id, "user_id": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted successfully"}


@api_router.post("/ipos", response_model=IPO)
async def create_ipo(ipo: IPOCreate, request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    ipo_dict = ipo.model_dump()
    ipo_dict['user_id'] = user["user_id"]
    broker_charges = ipo_dict.get('broker_charges', 0) or 0
    sell_price = ipo_dict.get('sell_price', ipo_dict['listing_price'])
    profit_loss = (sell_price - ipo_dict['application_price']) * ipo_dict['allotment_quantity'] - broker_charges
    ipo_dict['profit_loss'] = profit_loss
    ipo_dict['broker_charges'] = broker_charges
    ipo_dict['sell_price'] = sell_price
    
    ipo_obj = IPO(**ipo_dict)
    doc = ipo_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.ipos.insert_one(doc)
    return ipo_obj

@api_router.get("/ipos", response_model=List[IPO])
async def get_ipos(
    request: Request,
    authorization: Optional[str] = Header(None),
    demat_account_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    user = await get_current_user(request, authorization)
    query = {"user_id": user["user_id"]}
    if demat_account_id:
        query['demat_account_id'] = demat_account_id
    if start_date and end_date:
        query['listing_date'] = {"$gte": start_date, "$lte": end_date}
    
    ipos = await db.ipos.find(query, {"_id": 0}).to_list(1000)
    for ipo in ipos:
        if isinstance(ipo.get('created_at'), str):
            ipo['created_at'] = datetime.fromisoformat(ipo['created_at'])
        if 'sell_price' not in ipo or ipo.get('sell_price') is None:
            ipo['sell_price'] = ipo.get('listing_price')
    return ipos

@api_router.put("/ipos/{ipo_id}", response_model=IPO)
async def update_ipo(ipo_id: str, ipo: IPOUpdate, request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    existing = await db.ipos.find_one({"id": ipo_id, "user_id": user["user_id"]}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="IPO not found")
    
    update_data = {k: v for k, v in ipo.model_dump().items() if v is not None}
    
    if update_data:
        merged = {**existing, **update_data}
        broker_charges = merged.get('broker_charges', 0) or 0
        sell_price = merged.get('sell_price', merged.get('listing_price'))
        profit_loss = (sell_price - merged['application_price']) * merged['allotment_quantity'] - broker_charges
        update_data['profit_loss'] = profit_loss
        if 'broker_charges' in update_data:
            update_data['broker_charges'] = broker_charges
        if 'sell_price' in update_data:
            update_data['sell_price'] = sell_price
        await db.ipos.update_one({"id": ipo_id, "user_id": user["user_id"]}, {"$set": update_data})
    
    updated = await db.ipos.find_one({"id": ipo_id, "user_id": user["user_id"]}, {"_id": 0})
    if isinstance(updated.get('created_at'), str):
        updated['created_at'] = datetime.fromisoformat(updated['created_at'])
    return IPO(**updated)

@api_router.delete("/ipos/{ipo_id}")
async def delete_ipo(ipo_id: str, request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    result = await db.ipos.delete_one({"id": ipo_id, "user_id": user["user_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="IPO not found")
    return {"message": "IPO deleted successfully"}


@api_router.get("/dashboard/stats")
async def get_dashboard_stats(request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    ipos = await db.ipos.find({"user_id": user["user_id"]}, {"_id": 0}).to_list(1000)
    accounts = await db.demat_accounts.find({"user_id": user["user_id"]}, {"_id": 0}).to_list(1000)
    
    for ipo in ipos:
        if 'sell_price' not in ipo or ipo.get('sell_price') is None:
            ipo['sell_price'] = ipo.get('listing_price')
    
    total_invested = sum(ipo['application_price'] * ipo['allotment_quantity'] for ipo in ipos)
    total_returns = sum(ipo.get('sell_price', ipo['listing_price']) * ipo['allotment_quantity'] for ipo in ipos)
    total_pl = sum(ipo['profit_loss'] for ipo in ipos)
    active_ipos = len(ipos)
    win_count = sum(1 for ipo in ipos if ipo['profit_loss'] > 0)
    win_rate = (win_count / active_ipos * 100) if active_ipos > 0 else 0
    
    account_wise_pl = {}
    for ipo in ipos:
        acc_id = ipo['demat_account_id']
        if acc_id not in account_wise_pl:
            account_wise_pl[acc_id] = 0
        account_wise_pl[acc_id] += ipo['profit_loss']
    
    accounts_with_pl = []
    for account in accounts:
        acc_data = {**account}
        acc_data['total_pl'] = account_wise_pl.get(account['id'], 0)
        accounts_with_pl.append(acc_data)
    
    sorted_ipos = sorted(ipos, key=lambda x: x.get('listing_date', ''), reverse=True)
    
    return {
        "total_invested": round(total_invested, 2),
        "total_returns": round(total_returns, 2),
        "total_pl": round(total_pl, 2),
        "active_ipos": active_ipos,
        "win_rate": round(win_rate, 2),
        "accounts_with_pl": accounts_with_pl,
        "recent_ipos": sorted_ipos[:5]
    }


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()