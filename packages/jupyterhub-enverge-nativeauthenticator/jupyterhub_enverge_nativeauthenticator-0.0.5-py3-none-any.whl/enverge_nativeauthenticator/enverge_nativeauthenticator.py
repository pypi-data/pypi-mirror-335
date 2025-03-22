"""
Enverge extension for JupyterHub's NativeAuthenticator.

This module extends the NativeAuthenticator to add email notification
capabilities when users are authorized.
"""

from typing import List, Tuple, Type

from nativeauthenticator.nativeauthenticator import NativeAuthenticator
from nativeauthenticator.handlers import (
    LoginHandler,
    SignUpHandler,
    DiscardHandler,
    AuthorizationAreaHandler,
    EmailAuthorizationHandler,
    ChangePasswordHandler,
    ChangePasswordAdminHandler,
)
from .handlers import ToggleAuthorizationHandler
from traitlets import Unicode


class EnvergeNativeAuthenticator(NativeAuthenticator):
    """
    Extended NativeAuthenticator with email notification capabilities.
    
    This authenticator adds the ability to send notification emails
    to users when they are authorized in the system.
    """

    sendgrid_api_key = Unicode(
        None,
        config=True,
        help="SendGrid API key for sending emails"
    )

    email_sender = Unicode(
        "no-reply@example.com",
        config=True,
        help="Email address to use as sender for outgoing emails"
    )
    
    sendgrid_template_id_authorization_email = Unicode(
        "d-XXX",
        config=True,
        help="SendGrid template ID for authorization emails"
    )
    
    def get_handlers(self, app) -> List[Tuple[str, Type]]:
        """
        Return the handlers that should be used for this authenticator.
        
        Overrides the parent method to use our custom ToggleAuthorizationHandler
        for the /authorize/[username] endpoint.
        """
        native_handlers = [
            (r"/login", LoginHandler),
            (r"/signup", SignUpHandler),
            (r"/discard/([^/]*)", DiscardHandler),
            (r"/authorize", AuthorizationAreaHandler),
            (r"/authorize/([^/]*)", ToggleAuthorizationHandler),
            # the following /confirm/ must be like in generate_approval_url()
            (r"/confirm/([^/]*)", EmailAuthorizationHandler),
            (r"/change-password", ChangePasswordHandler),
            (r"/change-password/([^/]+)", ChangePasswordAdminHandler),
        ]
        return native_handlers
