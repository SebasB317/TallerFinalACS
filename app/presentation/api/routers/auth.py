from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.services.auth_service import AuthService
from app.application.services.jwt_service import JwtService
from app.domain.entities.user import User
from app.domain.exceptions import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.domain.value_objects.password import PlainPassword
from app.presentation.deps import get_auth_service, get_current_user, get_db, get_jwt_service, http_error_from_domain
from app.presentation.schemas.auth import LoginRequest, MeResponse, RegisterRequest, RegisterResponse, TokenResponse

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    body: RegisterRequest,
    db: Session = Depends(get_db),
    auth: AuthService = Depends(get_auth_service),
) -> RegisterResponse:
    try:
        PlainPassword(body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    try:
        user = auth.register(str(body.email), body.password)
        db.commit()
    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except EmailAlreadyRegisteredError as e:
        db.rollback()
        raise http_error_from_domain(e) from e
    except Exception:
        db.rollback()
        raise
    assert user.id is not None
    return RegisterResponse(user_id=user.id)


@router.post("/login", response_model=TokenResponse)
def login(
    body: LoginRequest,
    auth: AuthService = Depends(get_auth_service),
    jwt_service: JwtService = Depends(get_jwt_service),
) -> TokenResponse:
    try:
        PlainPassword(body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    try:
        user = auth.authenticate(str(body.email), body.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e
    except InvalidCredentialsError as e:
        raise http_error_from_domain(e) from e
    assert user.id is not None
    token = jwt_service.create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(current: User = Depends(get_current_user)) -> MeResponse:
    assert current.id is not None
    return MeResponse(user_id=current.id, email=current.email.value)