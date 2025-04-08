from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    get_current_user,
    TokenData
)
from models.user import User
from datetime import timedelta
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    try:
        user = authenticate_user(
            form_data.username,
            form_data.password,
            request
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"}
            )

        access_token = create_access_token(
            {"sub": user.email},
            timedelta(minutes=15)
        )
        refresh_token = create_refresh_token(user.email)

        logger.info(f"Successful login: {user.email}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900  # 15 minutes
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.post("/refresh")
async def refresh_token(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    try:
        new_access_token = create_access_token(
            {"sub": current_user.email},
            timedelta(minutes=15)
        )
        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"Refresh token error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not refresh token"
        )

@router.get("/me")
async def read_users_me(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    # Return minimal user info for security
    return {
        "email": current_user.email[:2] + "*****@****",
        "name": current_user.name
    }

@router.post("/logout")
async def logout(request: Request):
    # In production, implement token blacklisting
    logger.info(f"User logged out: {request.client.host}")
    return {"message": "Successfully logged out"}
