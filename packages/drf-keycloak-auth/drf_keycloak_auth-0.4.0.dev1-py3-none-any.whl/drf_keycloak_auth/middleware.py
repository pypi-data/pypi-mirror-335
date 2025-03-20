from django.shortcuts import redirect
from django.http import JsonResponse
from drf_keycloak_auth.authentication import KeycloakMultiAuthentication
from drf_keycloak_auth.keycloak import get_keycloak_openid
from keycloak.exceptions import KeycloakAuthenticationError

import logging

log = logging.getLogger("middleware")


class AuthSessionMiddleware:
    """Django Middleware for additional Standard Flow (Auth Code Flow) authentication."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = KeycloakMultiAuthentication()
        auth.keycloak_openid = get_keycloak_openid(host=request.get_host())

        if "text/html" in request.headers.get("Accept", "").lower():
            base_url = f"{request.scheme}://{request.get_host()}"
            code = request.GET.get("code")

            if not code:
                return redirect(auth.keycloak_openid.auth_url(redirect_uri=base_url))

            try:
                token_response = auth.keycloak_openid.token(
                    grant_type="authorization_code", code=code, redirect_uri=base_url
                )

                # Extract access token from response
                access_token = token_response["access_token"]
                log.debug("Successfully obtained access token")

                user, decoded_token = auth.authenticate_credentials(
                    access_token
                )
                auth.post_auth_operations(user, decoded_token, request)
                request.user = user  # Attach user to request

            except KeycloakAuthenticationError as e:
                log.error(f"Keycloak auth error: {str(e)}")
                return JsonResponse({"error": "Token exchange failed"}, status=401)
            except Exception as e:
                log.error(f"General error: {str(e)}")
                return JsonResponse({"error": "Authentication failed"}, status=500)

        return self.get_response(request)
