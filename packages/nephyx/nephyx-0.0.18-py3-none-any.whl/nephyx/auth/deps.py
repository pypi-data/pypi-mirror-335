from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets


def basic_auth(username: str = "admin", password: str = "admin"):
    def inner(
        credentials: HTTPBasicCredentials = Depends(HTTPBasic()),
    ) -> str:
        is_correct_username = secrets.compare_digest(credentials.username, username)
        is_correct_password = secrets.compare_digest(credentials.password, password)

        if not (is_correct_username and is_correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Basic"},
            )

        return credentials.username

    return inner
