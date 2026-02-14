"""Auth routes — verify Supabase JWT and return user info."""

from fastapi import APIRouter, Header, HTTPException

from app.supabase_client import supabase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me")
async def get_current_user(authorization: str = Header(...)):
    """Return the current authenticated user from a Supabase JWT.

    Expects: Authorization: Bearer <access_token>
    """
    try:
        token = authorization.replace("Bearer ", "")
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        if not user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        return {
            "id": str(user.id),
            "email": user.email,
            "created_at": str(user.created_at) if user.created_at else None,
            "provider": user.app_metadata.get("provider", "email") if user.app_metadata else "email",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
