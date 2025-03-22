"""
Handlers for the Enverge NativeAuthenticator extension.

This module provides HTTP request handlers that extend the functionality
of JupyterHub's NativeAuthenticator to support email notifications.
"""

import logging
import os
from typing import Optional, Dict, Any, Union

# Make SendGrid imports optional
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

from nativeauthenticator.handlers import LocalBase
from nativeauthenticator.orm import UserInfo
from .orm import AuthorizationEmail

try:
    from jupyterhub.scopes import needs_scope
    admin_users_scope = needs_scope("admin:users")
except ImportError:
    # Fallback for older JupyterHub versions
    from jupyterhub.utils import admin_only
    admin_users_scope = admin_only

logger = logging.getLogger(__name__)

# See SendGrid templates at https://mc.sendgrid.com/dynamic-templates

class ToggleAuthorizationHandler(LocalBase):
    """
    Handler for authorization status changes.
    
    Handles requests to authorize/[username] endpoints which toggle a user's
    authorization status and sends notification emails when users are authorized.
    """

    async def send_authorization_email(self, username: str, email: str) -> bool:
        """
        Send an authorization notification email to a newly authorized user.
        """
        if not email:
            logger.warning(f"No email address available for user {username}")
            return False
            
        if not SENDGRID_AVAILABLE:
            logger.error("SendGrid is not installed. Install with 'pip install sendgrid'")
            return False
            
        try:
            sendgrid_api_key = getattr(
                self.authenticator, 
                'sendgrid_api_key', 
                os.environ.get('SENDGRID_API_KEY')
            )
            
            if not sendgrid_api_key:
                logger.error("SendGrid API key not found in configuration or environment")
                return False
                
            # Get sender email with validation
            from_email = getattr(
                self.authenticator, 
                'email_sender', 
                os.environ.get('EMAIL_SENDER', 'noreply@example.com')
            )
            
            message = Mail(
                from_email=from_email,
                to_emails=email
            )
            
            template_id = getattr(
                self.authenticator,
                'sendgrid_template_id_authorization_email',
                "d-XXX"
            )
            
            if not template_id or template_id == "d-XXX":
                logger.error("SendGrid template ID not properly configured")
                return False
                
            message.template_id = template_id
            message.dynamic_template_data = {
                'name': username
            }
            
            sg = SendGridAPIClient(sendgrid_api_key)
            response = sg.send(message)
            
            if response.status_code >= 200 and response.status_code < 300:
                AuthorizationEmail.mark_email_sent(self.db, username)
                logger.info(f"Authorization email sent to {username} at {email}")
                return True
            else:
                logger.error(f"SendGrid API returned status code {response.status_code}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send authorization email to {username}: {str(e)}")
            return False

    @admin_users_scope
    async def get(self, slug: str) -> None:
        """
        Handle GET requests to toggle user authorization status.
        
        Args:
            slug: The username whose authorization status will be toggled
        """
        user = UserInfo.change_authorization(self.db, slug)
        
        if user.is_authorized:
            logger.info(f"User {slug} is now authorized")
            
            auth_email = AuthorizationEmail.find_by_username(self.db, slug)
            if auth_email:
                auth_email.email_sent = False
                self.db.commit()
            else:
                auth_email = AuthorizationEmail(user_info_id=user.id, email_sent=False)
                self.db.add(auth_email)
                self.db.commit()
            
            if user.email:
                await self.send_authorization_email(slug, user.email)
            else:
                logger.warning(f"No email available for user {slug}")
        else:
            logger.info(f"User {slug} is now unauthorized")
            
        self.redirect(self.hub.base_url + "authorize#" + slug)