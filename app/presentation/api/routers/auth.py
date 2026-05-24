from fastapi import APIRouter, Depends, HTTPException, status
from app.presentation.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse
)
from app.application.services.auth_service import AuthService
from app.application.services.jwt_service import JWTService
from app.infrastructure.repositories.user_repository_sqlalchemy import UserRepositorySQLAlchemy
from app.infrastructure.security.bcrypt_hasher import BcryptHasher
from app.domain.exceptions import (
    UserAlreadyExistsException,
    InvalidCredentialsException,
    UserNotFoundException
)
from app.presentation.deps import get_auth_service, get_jwt_service

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Ejercicio 1: Registro de nuevo usuario
    
    - Valida email y contraseña
    - Hash seguro de contraseña con bcrypt
    - Retorna usuario creado con ID
    """
    try:
        user = await auth_service.register(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active
        )
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
    jwt_service: JWTService = Depends(get_jwt_service)
):
    """
    Ejercicio 1: Autenticación y generación de JWT
    
    - Valida credenciales
    - Genera token JWT con expiración de 24 horas
    """
    try:
        user = await auth_service.authenticate(
            email=request.email,
            password=request.password
        )
        token = jwt_service.create_token(user.id, user.email)
        return TokenResponse(
            access_token=token,
            user_id=user.id,
            email=user.email
        )
    except (UserNotFoundException, InvalidCredentialsException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"}
        )
