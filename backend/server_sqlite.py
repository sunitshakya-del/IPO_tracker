from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Header
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import aiosqlite
import json

# Database path - use user data directory in Electron mode
DB_PATH = os.environ.get('DB_PATH', '/app/backend/ipo_tracker.db')
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Global database connection
db_conn = None

# ============ DATABASE INITIALIZATION ============
async def init_db():
    """Initialize SQLite database with tables"""
    global db_conn
    db_conn = await aiosqlite.connect(DB_PATH)
    db_conn.row_factory = aiosqlite.Row
    
    # Create tables
    await db_conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            picture TEXT,
            created_at TEXT NOT NULL
        )
    ''')
    
    await db_conn.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            session_token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    await db_conn.execute('''
        CREATE TABLE IF NOT EXISTS demat_accounts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            account_name TEXT NOT NULL,
            broker_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    
    await db_conn.execute('''
        CREATE TABLE IF NOT EXISTS ipos (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            ipo_name TEXT NOT NULL,
            lot_size INTEGER NOT NULL,
            application_price REAL NOT NULL,
            allotment_quantity INTEGER NOT NULL,
            listing_price REAL NOT NULL,
            sell_price REAL,
            demat_account_id TEXT NOT NULL,
            application_date TEXT NOT NULL,
            listing_date TEXT NOT NULL,
            broker_charges REAL DEFAULT 0,
            profit_loss REAL DEFAULT 0,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (demat_account_id) REFERENCES demat_accounts (id)
        )
    ''')
    
    await db_conn.commit()
    logging.info(f"Database initialized at {DB_PATH}")

async def close_db():
    """Close database connection"""
    global db_conn
    if db_conn:
        await db_conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()

app = FastAPI(lifespan=lifespan)
api_router = APIRouter(prefix="/api")


# ============ AUTH MODELS ============
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    user_id: str = Field(default_factory=lambda: f"user_{uuid.uuid4().hex[:12]}")
    email: str
    name: str
    picture: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    user_id: str
    session_token: str
    expires_at: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


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
    async with db_conn.execute(
        "SELECT * FROM user_sessions WHERE session_token = ?",
        (session_token,)
    ) as cursor:
        session_row = await cursor.fetchone()
    
    if not session_row:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    session_doc = dict(session_row)
    
    # Check expiry
    expires_at = datetime.fromisoformat(session_doc["expires_at"])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    async with db_conn.execute(
        "SELECT * FROM users WHERE user_id = ?",
        (session_doc["user_id"],)
    ) as cursor:
        user_row = await cursor.fetchone()
    
    if not user_row:
        raise HTTPException(status_code=401, detail="User not found")
    
    return dict(user_row)


@api_router.get("/")
async def root():
    return {"message": "IPO P&L Tracker API (Desktop Edition)"}


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
        async with db_conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (user_data["email"],)
        ) as cursor:
            existing_user = await cursor.fetchone()
        
        if existing_user:
            user_id = existing_user["user_id"]
            # Update user data
            await db_conn.execute(
                "UPDATE users SET name = ?, picture = ? WHERE user_id = ?",
                (user_data["name"], user_data.get("picture"), user_id)
            )
            await db_conn.commit()
        else:
            # Create new user
            user = User(
                email=user_data["email"],
                name=user_data["name"],
                picture=user_data.get("picture")
            )
            await db_conn.execute(
                "INSERT INTO users (user_id, email, name, picture, created_at) VALUES (?, ?, ?, ?, ?)",
                (user.user_id, user.email, user.name, user.picture, user.created_at)
            )
            await db_conn.commit()
            user_id = user.user_id
        
        # Create session
        session_token = user_data["session_token"]
        expires_at = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
        created_at = datetime.now(timezone.utc).isoformat()
        
        # Delete old sessions for this user
        await db_conn.execute(
            "DELETE FROM user_sessions WHERE user_id = ?",
            (user_id,)
        )
        
        # Insert new session
        await db_conn.execute(
            "INSERT INTO user_sessions (user_id, session_token, expires_at, created_at) VALUES (?, ?, ?, ?)",
            (user_id, session_token, expires_at, created_at)
        )
        await db_conn.commit()
        
        # Set httpOnly cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            secure=True,
            samesite="none",
            path="/",
            max_age=7*24*60*60
        )
        
        # Get full user data
        async with db_conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        ) as cursor:
            user_row = await cursor.fetchone()
            user_doc = dict(user_row)
        
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
            await db_conn.execute(
                "DELETE FROM user_sessions WHERE session_token = ?",
                (session_token,)
            )
            await db_conn.commit()
        
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
        response.delete_cookie(
            key="session_token",
            path="/",
            secure=True,
            httponly=True,
            samesite="none"
        )
        return {"message": "Logged out"}


# ============ DEMAT ACCOUNT MODELS & ENDPOINTS ============
class DematAccount(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    account_name: str
    broker_name: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DematAccountCreate(BaseModel):
    account_name: str
    broker_name: str

class DematAccountUpdate(BaseModel):
    account_name: Optional[str] = None
    broker_name: Optional[str] = None


@api_router.post("/accounts", response_model=DematAccount)
async def create_account(account: DematAccountCreate, request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    account_obj = DematAccount(**account.model_dump(), user_id=user["user_id"])
    
    await db_conn.execute(
        "INSERT INTO demat_accounts (id, user_id, account_name, broker_name, created_at) VALUES (?, ?, ?, ?, ?)",
        (account_obj.id, account_obj.user_id, account_obj.account_name, account_obj.broker_name, account_obj.created_at)
    )
    await db_conn.commit()
    return account_obj

@api_router.get("/accounts", response_model=List[DematAccount])
async def get_accounts(request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    async with db_conn.execute(
        "SELECT * FROM demat_accounts WHERE user_id = ?",
        (user["user_id"],)
    ) as cursor:
        rows = await cursor.fetchall()
    return [dict(row) for row in rows]

@api_router.put("/accounts/{account_id}", response_model=DematAccount)
async def update_account(account_id: str, account: DematAccountUpdate, request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    
    async with db_conn.execute(
        "SELECT * FROM demat_accounts WHERE id = ? AND user_id = ?",
        (account_id, user["user_id"])
    ) as cursor:
        existing = await cursor.fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="Account not found")
    
    update_data = {k: v for k, v in account.model_dump().items() if v is not None}
    if update_data:
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        values = list(update_data.values()) + [account_id, user["user_id"]]
        await db_conn.execute(
            f"UPDATE demat_accounts SET {set_clause} WHERE id = ? AND user_id = ?",
            values
        )
        await db_conn.commit()
    
    async with db_conn.execute(
        "SELECT * FROM demat_accounts WHERE id = ? AND user_id = ?",
        (account_id, user["user_id"])
    ) as cursor:
        updated = await cursor.fetchone()
    
    return dict(updated)

@api_router.delete("/accounts/{account_id}")
async def delete_account(account_id: str, request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    cursor = await db_conn.execute(
        "DELETE FROM demat_accounts WHERE id = ? AND user_id = ?",
        (account_id, user["user_id"])
    )
    await db_conn.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account deleted successfully"}


# ============ IPO MODELS & ENDPOINTS ============
class IPO(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
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
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

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
    
    await db_conn.execute(
        """INSERT INTO ipos (id, user_id, ipo_name, lot_size, application_price, allotment_quantity,
           listing_price, sell_price, demat_account_id, application_date, listing_date,
           broker_charges, profit_loss, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (ipo_obj.id, ipo_obj.user_id, ipo_obj.ipo_name, ipo_obj.lot_size, ipo_obj.application_price,
         ipo_obj.allotment_quantity, ipo_obj.listing_price, ipo_obj.sell_price, ipo_obj.demat_account_id,
         ipo_obj.application_date, ipo_obj.listing_date, ipo_obj.broker_charges,
         ipo_obj.profit_loss, ipo_obj.created_at)
    )
    await db_conn.commit()
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
    query = "SELECT * FROM ipos WHERE user_id = ?"
    params = [user["user_id"]]
    
    if demat_account_id:
        query += " AND demat_account_id = ?"
        params.append(demat_account_id)
    if start_date and end_date:
        query += " AND listing_date >= ? AND listing_date <= ?"
        params.extend([start_date, end_date])
    
    async with db_conn.execute(query, params) as cursor:
        rows = await cursor.fetchall()
    
    ipos = [dict(row) for row in rows]
    # Backwards compatibility - set sell_price to listing_price if None
    for ipo in ipos:
        if ipo.get('sell_price') is None:
            ipo['sell_price'] = ipo.get('listing_price')
    return ipos

@api_router.put("/ipos/{ipo_id}", response_model=IPO)
async def update_ipo(ipo_id: str, ipo: IPOUpdate, request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    
    async with db_conn.execute(
        "SELECT * FROM ipos WHERE id = ? AND user_id = ?",
        (ipo_id, user["user_id"])
    ) as cursor:
        existing = await cursor.fetchone()
    
    if not existing:
        raise HTTPException(status_code=404, detail="IPO not found")
    
    existing_dict = dict(existing)
    update_data = {k: v for k, v in ipo.model_dump().items() if v is not None}
    
    if update_data:
        merged = {**existing_dict, **update_data}
        broker_charges = merged.get('broker_charges', 0) or 0
        sell_price = merged.get('sell_price', merged.get('listing_price'))
        profit_loss = (sell_price - merged['application_price']) * merged['allotment_quantity'] - broker_charges
        update_data['profit_loss'] = profit_loss
        
        set_clause = ", ".join([f"{k} = ?" for k in update_data.keys()])
        values = list(update_data.values()) + [ipo_id, user["user_id"]]
        await db_conn.execute(
            f"UPDATE ipos SET {set_clause} WHERE id = ? AND user_id = ?",
            values
        )
        await db_conn.commit()
    
    async with db_conn.execute(
        "SELECT * FROM ipos WHERE id = ? AND user_id = ?",
        (ipo_id, user["user_id"])
    ) as cursor:
        updated = await cursor.fetchone()
    
    return dict(updated)

@api_router.delete("/ipos/{ipo_id}")
async def delete_ipo(ipo_id: str, request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    cursor = await db_conn.execute(
        "DELETE FROM ipos WHERE id = ? AND user_id = ?",
        (ipo_id, user["user_id"])
    )
    await db_conn.commit()
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="IPO not found")
    return {"message": "IPO deleted successfully"}


# ============ DASHBOARD ENDPOINT ============
@api_router.get("/dashboard/stats")
async def get_dashboard_stats(request: Request, authorization: Optional[str] = Header(None)):
    user = await get_current_user(request, authorization)
    
    async with db_conn.execute(
        "SELECT * FROM ipos WHERE user_id = ?",
        (user["user_id"],)
    ) as cursor:
        ipo_rows = await cursor.fetchall()
    ipos = [dict(row) for row in ipo_rows]
    
    async with db_conn.execute(
        "SELECT * FROM demat_accounts WHERE user_id = ?",
        (user["user_id"],)
    ) as cursor:
        account_rows = await cursor.fetchall()
    accounts = [dict(row) for row in account_rows]
    
    for ipo in ipos:
        if ipo.get('sell_price') is None:
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
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
