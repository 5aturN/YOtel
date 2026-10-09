"""HTTP layer for the initial room availability and booking API."""

import hmac
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from yaotel.config import Settings
from yaotel.db import create_database
from yaotel.schemas import BookingCreate, BookingRead, RoomRead
from yaotel.services import BookingConflict, BookingService, RoomNotFound


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build an app instance with isolated settings and database resources."""
    runtime_settings = settings or Settings.from_env()
    engine, session_factory = create_database(runtime_settings.database_url)
    app = FastAPI(
        title="ЯОтель API",
        version="0.2.0",
        description="Учебный API поиска доступных номеров и создания бронирований.",
    )
    app.state.settings = runtime_settings
    app.state.engine = engine
    app.state.session_factory = session_factory

    def get_session(request: Request):
        session: Session = request.app.state.session_factory()
        try:
            yield session
        finally:
            session.close()

    DbSession = Annotated[Session, Depends(get_session)]

    def require_api_key(
        request: Request,
        x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
    ) -> None:
        expected = request.app.state.settings.api_key
        if not expected:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="API access is not configured.",
            )
        if not x_api_key or not hmac.compare_digest(x_api_key, expected):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid API key.",
            )

    @app.get("/health", tags=["health"], summary="Check service health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get(
        "/api/rooms/availability",
        response_model=list[RoomRead],
        dependencies=[Depends(require_api_key)],
        tags=["rooms"],
        summary="Find rooms available for a stay",
    )
    def room_availability(
        check_in: Annotated[date, Query()],
        check_out: Annotated[date, Query()],
        guests: Annotated[int, Query(ge=1, le=10)],
        session: DbSession,
    ) -> list[RoomRead]:
        try:
            rooms = BookingService(session).available_rooms(check_in, check_out, guests)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return [RoomRead.model_validate(room) for room in rooms]

    @app.post(
        "/api/bookings",
        response_model=BookingRead,
        status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(require_api_key)],
        tags=["bookings"],
        summary="Create a pending room booking",
    )
    def create_booking(
        request: BookingCreate, session: DbSession
    ) -> BookingRead:
        try:
            booking = BookingService(session).create_booking(**request.model_dump())
        except RoomNotFound as exc:
            raise HTTPException(status_code=404, detail="Room not found.") from exc
        except BookingConflict as exc:
            raise HTTPException(
                status_code=409, detail="Room is not available for these dates."
            ) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return BookingRead.model_validate(booking)

    return app
