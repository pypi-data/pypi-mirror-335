from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from usageflow.core import UsageFlowClient
import time
from typing import Dict, Any, List, Optional
from starlette.routing import Match
class UsageFlowMiddleware(BaseHTTPMiddleware):
    """
    Middleware to track API usage with UsageFlow.

    This middleware integrates with FastAPI to track API requests and responses,
    providing detailed usage analytics and insights.

    :param app: The FastAPI application instance
    :param api_key: The UsageFlow API key
    :param whitelist_routes: List of routes to whitelist (skip tracking)
    :param tracklist_routes: List of routes to track only
    """
    def __init__(self, app: FastAPI, api_key: str, whitelist_routes: List[str] = None, tracklist_routes: List[str] = None):
        super().__init__(app)
        self.client = UsageFlowClient(api_key)
        self.whitelist_routes = whitelist_routes or []
        self.tracklist_routes = tracklist_routes or []

    async def dispatch(self, request: Request, call_next):
        """Middleware to execute logic before and after the request."""
        start_time = time.time()

        route_path = get_router_path(request)
        # Check if the request is in the whitelist (skip tracking)
        if route_path and any(route_path.startswith(pattern) for pattern in self.whitelist_routes):
            return await call_next(request)

        # Check if the request matches the tracklist (only track these)
        if self.tracklist_routes and not any(route_path.startswith(pattern) for pattern in self.tracklist_routes):
            return await call_next(request)

        # Extract metadata (Before Request)
        request_metadata = await self._before_request(request)

        if request_metadata.get("blocked"):
            return Response(content=request_metadata["error"], status_code=request_metadata["status_code"])

        # Process the request
        response = await call_next(request)

        # Post-processing (After Request)
        await self._after_request(request, response, start_time)

        return response

    async def _before_request(self, request: Request) -> Dict[str, Any]:
        """Handle logic before the request reaches the endpoint."""
        request.state.body_data = await self._get_request_body(request)

        metadata = {
            "method": request.method,
            "url": get_router_path(request),
            "rawUrl": str(request.url.path),
            "clientIP": request.client.host if request.client else None,
            "userAgent": request.headers.get("user-agent"),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "headers": {k: ("****" if "key" in k.lower() else v) for k, v in request.headers.items()},
            "queryParams": dict(request.query_params),
            "pathParams": dict(request.path_params),
            "body": request.state.body_data,
            "userId": self._extract_user_id(request),
        }

        request.state.metadata = metadata
        ledger_id = self._guess_ledger_id(request)

        # Allocate request
        success, result = self.client.allocate_request(ledger_id, metadata)
        if not success:
            return {
                "blocked": True,
                "error": result.get("message", "Request blocked"),
                "status_code": result.get("status_code", 500),
            }

        # Store event ID for after request processing
        request.state.event_id = result.get("eventId")
        request.state.ledger_id = ledger_id
        return {"blocked": False}

    async def _after_request(self, request: Request, response: Response, start_time: float):
        """Handle logic after the request has been processed."""
        if hasattr(request.state, "event_id") and request.state.event_id:
            duration = int((time.time() - start_time) * 1000)

            request.state.metadata.update({
                "responseStatusCode": response.status_code,
                "responseHeaders": dict(response.headers),
                "requestDuration": duration,
            })

            self.client.fulfill_request(request.state.ledger_id, request.state.event_id, request.state.metadata)

    async def _get_request_body(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract request body safely."""
        try:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                return await request.json()
            elif "application/x-www-form-urlencoded" in content_type:
                return dict(await request.form())
            elif "multipart/form-data" in content_type:
                return dict(await request.form())
            else:
                return (await request.body()).decode("utf-8")
        except Exception:
            return None

    def _extract_user_id(self, request: Request) -> str:
        """Extract user ID from JWT or headers."""
        token = self.client.extract_bearer_token(request.headers.get("Authorization"))
        if token:
            claims = self.client.decode_jwt_unverified(token)
            return claims.get("sub", "anonymous") if claims else "anonymous"
        return request.headers.get("X-User-ID", "anonymous")

    def _guess_ledger_id(self, request: Request) -> str:
        """Determine the ledger ID from request data."""
        method = request.method
        url = get_router_path(request)

        # Check configured identity field
        config = self.client.get_config()
        if config:
            field_name = config.get("identityFieldName")
            location = config.get("identityFieldLocation")

            if field_name and location:
                match location:
                    case "path_params":
                        if field_name in request.path_params:
                            return f"{method} {url} {self.client.transform_to_ledger_id(request.path_params[field_name])}"
                    case "query_params":
                        if field_name in request.query_params:
                            return f"{method} {url} {self.client.transform_to_ledger_id(request.query_params[field_name])}"
                    case "body":
                        if hasattr(request.state, "body_data") and field_name in request.state.body_data:
                            return f"{method} {url} {self.client.transform_to_ledger_id(request.state.body_data[field_name])}"
                    case "bearer_token":
                        token = self.client.extract_bearer_token(request.headers.get("Authorization"))
                        if token:
                            claims = self.client.decode_jwt_unverified(token)
                            if claims and field_name in claims:
                                return f"{method} {url} {self.client.transform_to_ledger_id(claims[field_name])}"

        return f"{method} {url}"

def get_router_path(request: Request) -> Optional[str]:
    current_path = None
    for route in request.app.routes:
        if route.matches(request.scope):
            match, _ = route.matches(request.scope)
            if match == Match.FULL:
                return route.path
            elif match == Match.PARTIAL and current_path is None:
                current_path = route.path

    return current_path

__version__ = "0.1.1"
__all__ = ["UsageFlowMiddleware"]
