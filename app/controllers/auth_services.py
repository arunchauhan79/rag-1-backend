from schema import UserOutput, LoginRequest
from core import BadRequestException, verify_password,create_access_token,UnauthorizedException, DatabaseQueryException
from pymongo.asynchronous.database import AsyncDatabase
from datetime import datetime, timezone, timedelta




async def authenticateUser(login: LoginRequest, db: AsyncDatabase) -> dict:
    try:
        if not login.username or not login.password:
            raise BadRequestException("Username and password are required")

        user = await db.users.find_one({"username": login.username})
        if not user:
            raise UnauthorizedException("User not found")
      
        if not verify_password(login.password, user["password"]):
            raise UnauthorizedException("Invalid password")

        
        # Create JWT Token
        payload = {
            "id": str(user["_id"]),
            "organizationId": str(user.get("organizationId", "")),
            "role": user.get("role"),
            "exp": datetime.now(timezone.utc) + timedelta(days=1)
        }
        token = create_access_token(payload)
        # Clean user response
        # user.pop("password", None)

        return {
            "user": UserOutput.model_validate({**user, "id": str(user["_id"])}),
            "token": token
        }

    except Exception as e:
        raise DatabaseQueryException(f"Error authenticating user: {e}")