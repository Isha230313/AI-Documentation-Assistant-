from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.core.security import create_access_token, verify_password
from api.deps import get_current_user, require_admin
from api.schemas.auth import RegisterRequest, TokenResponse, UserResponse
from api.users_store import create_user, get_user, list_users

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()):
    """Standard OAuth2 password flow. Returns a JWT bearer token."""
    user = get_user(form.username)
    if not user or not verify_password(form.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user["is_active"]:
        raise HTTPException(status_code=400, detail="Inactive user.")

    token = create_access_token({"sub": user["username"]})
    return TokenResponse(access_token=token)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    body: RegisterRequest,
    _admin: dict = Depends(require_admin),   # only admins can create users
):
    """Create a new user. Admin-only."""
    try:
        user = create_user(body.username, body.password)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return UserResponse(**user)


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return UserResponse(**current_user)


@router.get("/users", response_model=list[UserResponse])
def users(_admin: dict = Depends(require_admin)):
    """List all users. Admin-only."""
    return [UserResponse(**u) for u in list_users()]
