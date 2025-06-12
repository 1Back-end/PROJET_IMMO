from typing import Generator, Optional

from fastapi import Depends, Query
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, BackgroundTasks

from app.main import schemas, models, crud
from app.main.core.i18n import __
from app.main.core.security import decode_access_token


def get_db(request: Request) -> Generator:
    return request.state.db


class TokenRequired(HTTPBearer):

    def __init__(self, token: Optional[str] = Query(None), roles=None, auto_error: bool = True,let_new_user: bool = False):
        if roles is None:
            roles = []
        self.roles = roles
        self.token = token,
        self.let_new_user = let_new_user
        super(TokenRequired, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        required_roles = self.roles
        credentials: HTTPAuthorizationCredentials = await super(TokenRequired, self).__call__(request)

        if not credentials and self.token:
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=self.token)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))
            token_data = decode_access_token(credentials.credentials)
            if not token_data:
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))

            if models.BlacklistToken.check_blacklist(db, credentials.credentials):
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))

            current_user = crud.user.get_by_uuid(db=db, uuid=token_data["sub"])
            if not current_user:
                raise HTTPException(status_code=403, detail=__("dependencies-token-invalid"))
            
            if current_user.is_new_user and not self.let_new_user:
                raise HTTPException(status_code=403, detail=__("first-time-login-require-change-password"))
            
            # Vérifie si le rôle de l'utilisateur fait partie des rôles autorisés
            if self.roles and current_user.role not in self.roles:
                raise HTTPException(status_code=403, detail="Insufficient permissions")

            """
            if required_roles:
                if current_user.role_uuid not in required_roles:
                    raise HTTPException(status_code=403, detail=__("dependencies-access-unauthorized"))
            """

            return current_user
        else:
            raise HTTPException(status_code=403, detail=__("dependencies-access-unauthorized"))
        db.close()



