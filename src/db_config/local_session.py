from starlette import status
from starlette.exceptions import HTTPException


class LocalSessionState:
    def __init__(self):
        self._session = None

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session):
        self._session = session


local_session_state = LocalSessionState()


async def get_local_session():
    if local_session_state.session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Local session not initialized")
    local_session = local_session_state.session

    async with local_session() as session:
        yield session
