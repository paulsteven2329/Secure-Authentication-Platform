from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, require_role
from app.models.user import User

router = APIRouter()

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/admin", dependencies=[Depends(require_role(["admin"]))])
def admin_route(current_user: User = Depends(get_current_user)):
    return {"msg": "Welcome admin!"}