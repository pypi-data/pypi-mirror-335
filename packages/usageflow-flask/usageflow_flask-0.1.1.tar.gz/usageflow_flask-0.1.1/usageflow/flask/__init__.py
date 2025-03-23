from typing import List
from flask import Flask, request
from usageflow.core import UsageFlowClient
import time

class UsageFlowMiddleware:
    """
    Middleware to track API usage with UsageFlow.

    This middleware integrates with Flask to track API requests and responses,
    providing detailed usage analytics and insights.

    :param app: The Flask application instance
    :param api_key: The UsageFlow API key
    :param whitelist_routes: List of routes to whitelist (skip tracking)
    :param tracklist_routes: List of routes to track only
    """
    def __init__(self, app: Flask, api_key: str, whitelist_routes: List[str] = None, tracklist_routes: List[str] = None):
        self.app = app
        self.client = UsageFlowClient(api_key)
        self.whitelist_routes = whitelist_routes or []
        self.tracklist_routes = tracklist_routes or []
        self._init_middleware()

    def _init_middleware(self):
        """Initialize the middleware by registering before/after request handlers"""
        self.app.before_request(self._before_request)
        self.app.after_request(self._after_request)

    def _before_request(self):
        """Handle request before it reaches the view"""
        request.usageflow_start_time = time.time()
        
        route_path = request.path

        # Skip tracking for whitelisted routes
        if any(route_path.startswith(pattern) for pattern in self.whitelist_routes):
            return

        # Track only specific routes if tracklist is set
        if self.tracklist_routes and not any(route_path.startswith(pattern) for pattern in self.tracklist_routes):
            return

        # Prepare request metadata
        metadata = {
            "method": request.method,
            "url": request.url_rule.rule,
            "rawUrl": request.path,
            "clientIP": request.remote_addr,
            "userAgent": request.headers.get("user-agent"),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "headers": {k: ("****" if "key" in k.lower() else v) for k, v in request.headers.items()},
            "queryParams": dict(request.args),
            "pathParams": dict(request.view_args),
            "body": request.get_json(silent=True),
        }

        # Store metadata for later use
        request.usageflow_metadata = metadata

        # Get ledger ID and allocate request
        ledger_id = self._guess_ledger_id()
        success, result = self.client.allocate_request(ledger_id, metadata)
        
        if not success:
            error_message = result.get('message', 'Request fulfillment failed')
            status_code = result.get('status_code', 500)
            
            if status_code == 429:
                return {"error": "Rate limit exceeded"}, 429
            elif status_code == 403:
                return {"error": "Access forbidden"}, 403
            elif status_code == 401:
                return {"error": "Unauthorized access"}, 401
            else:
                return {"error": error_message}, status_code

        # Store event ID and ledger ID for later use
        request.usageflow_event_id = result.get('eventId') if result else None
        request.usageflow_ledger_id = ledger_id

    def _after_request(self, response):
        """Handle request after it has been processed by the view"""
        if hasattr(request, "usageflow_event_id") and request.usageflow_event_id:
            metadata = request.usageflow_metadata
            metadata.update({
                "responseStatusCode": response.status_code,
                "responseHeaders": dict(response.headers),
                "requestDuration": int((time.time() - request.usageflow_start_time) * 1000),
            })
            
            self.client.fulfill_request(
                request.usageflow_ledger_id,
                request.usageflow_event_id,
                metadata
            )

        return response

    def _extract_user_id(self) -> str:
        """Extract user ID from JWT or headers"""
        token = self.client.extract_bearer_token(request.headers.get("Authorization"))
        if token:
            claims = self.client.decode_jwt_unverified(token)
            return claims.get("sub", "anonymous") if claims else "anonymous"
        return request.headers.get("X-User-ID", "anonymous")

    def _guess_ledger_id(self) -> str:
        """Determine the ledger ID from the request"""
        method = request.method
        url = request.url_rule.rule

        # Check config for identity field configuration
        config = self.client.get_config()
        if config:
            field_name = config.get("identityFieldName")
            location = config.get("identityFieldLocation")

            if field_name and location:
                match location:
                    case "path_params":
                        # Get path parameters from the request
                        if request.view_args and field_name in request.view_args:
                            return method + " " + url + " " + self.client.transform_to_ledger_id(request.view_args[field_name])

                    case "query_params":
                        # Check query parameters
                        if request.args and field_name in request.args:
                            return method + " " + url + " " + self.client.transform_to_ledger_id(request.args[field_name])

                    case "body":
                        # Check request body
                        try:
                            body_data = request.get_json(silent=True) or {}
                            if body_data and field_name in body_data:
                                return method + " " + url + " " + self.client.transform_to_ledger_id(body_data[field_name])
                        except Exception:
                            pass

                    case "bearer_token":
                        # Extract from bearer token
                        auth_header = request.headers.get("Authorization")
                        if auth_header:
                            token = self.client.extract_bearer_token(auth_header)
                            if token:
                                claims = self.client.decode_jwt_unverified(token)
                                if claims and field_name in claims:
                                    return method + " " + url + " " + self.client.transform_to_ledger_id(claims[field_name])

        # Fallback to default ledgerId
        return f"{method} {url}"

__version__ = "0.1.1"
__all__ = ["UsageFlowMiddleware"] 