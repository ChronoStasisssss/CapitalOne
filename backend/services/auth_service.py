from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from passlib.context import CryptContext
from models.user import User
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import os
import logging
from pydantic import BaseModel

# Security logging
logging.basicConfig(filename='auth.log', level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError("Invalid SECRET_KEY - must be at least 32 characters")

# Use RS256 for better security
ALGORITHM = os.getenv("ALGORITHM", "RS256") 
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "1"))

# Password policy
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Track failed attempts
failed_attempts: Dict[str, int] = {}

class TokenData(BaseModel):
    email: str
    scopes: list[str] = []
    device_id: Optional[str] = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with additional security checks"""
    if len(plain_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )
    return pwd_context.verify(plain_password, hashed_password)

def get_user(email: str) -> Optional[User]:
    """Get user from database with security logging"""
    # In production, replace with real DB call
    user_dict = fake_users_db.get(email)
    if user_dict:
        logger.info(f"User accessed: {email}")
        return User(**user_dict)
    logger.warning(f"Failed access attempt for unknown user: {email}")
    return None

def authenticate_user(email: str, password: str, request: Request) -> Optional[User]:
    """Authenticate user with security enhancements"""
    # Check failed attempts
    if failed_attempts.get(email, 0) >= 5:
        logger.warning(f"Account locked due to too many attempts: {email}")
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail="Account temporarily locked"
        )

    user = get_user(email)
    if not user or not verify_password(password, user.hashed_password):
        failed_attempts[email] = failed_attempts.get(email, 0) + 1
        logger.warning(f"Failed login attempt for: {email}")
        return None

    # Reset failed attempts on success
    failed_attempts.pop(email, None)
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token with enhanced security"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "bancoseguro.com",
        "aud": "bancoseguro-app"
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(email: str) -> str:
    """Create refresh token for long-term sessions"""
    return jwt.encode(
        {"sub": email, "type": "refresh"},
        SECRET_KEY,
        algorithm=ALGORITHM,
        expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    request: Request = None
) -> User:
    """Get current user with enhanced security checks"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "require_iss": True,
                "require_aud": True,
                "verify_iss": True,
                "verify_aud": True
            }
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        # Check token type if implementing refresh tokens
        if payload.get("type") == "refresh":
            raise HTTPException(
                status_code=403,
                detail="Refresh token cannot be used for authentication"
            )
            
    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise credentials_exception
    
    user = get_user(email)
    if user is None:
        raise credentials_exception
        
    # Log successful authentication
    logger.info(f"User authenticated: {email}")
    if request:
        logger.info(f"IP: {request.client.host}")
        
    return user
