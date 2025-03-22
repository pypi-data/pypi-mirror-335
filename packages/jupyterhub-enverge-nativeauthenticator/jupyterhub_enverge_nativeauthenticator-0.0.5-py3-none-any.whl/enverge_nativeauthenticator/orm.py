"""
ORM models for the Enverge NativeAuthenticator extension.

This module defines database models used to track authorization email status
for users of the JupyterHub NativeAuthenticator.
"""

from jupyterhub.orm import Base
from nativeauthenticator.orm import UserInfo
from sqlalchemy import Boolean, Column, Integer, ForeignKey
from sqlalchemy.orm import Session
from typing import Optional


class AuthorizationEmail(Base):
    """
    Tracks authorization notification emails sent to users after approval in NativeAuthenticator.
    
    Extends NativeAuthenticator to record when authorization emails have been sent.
    """

    __tablename__ = "authorization_emails"
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to the original UserInfo.id from nativeauthenticator
    user_info_id = Column(Integer, ForeignKey('users_info.id', ondelete='CASCADE'), nullable=False)
    
    # Boolean field to track if the authorization email was sent
    email_sent = Column(Boolean, default=False)
    
    @classmethod
    def find_by_user_id(cls, db: Session, user_id: int) -> Optional["AuthorizationEmail"]:
        """
        Find an authorization email record by user_id.
        
        Returns None if no record was found.
        """
        return db.query(cls).filter(cls.user_info_id == user_id).first()
    
    @classmethod
    def find_by_username(cls, db: Session, username: str) -> Optional["AuthorizationEmail"]:
        """
        Find an authorization email record by username.
        
        This method first finds the UserInfo record by username,
        then looks up the corresponding AuthorizationEmail record.
        
        Returns None if no record was found.
        """
        user_info = db.query(UserInfo).filter(UserInfo.username == username).first()
        if not user_info:
            return None
        return cls.find_by_user_id(db, user_info.id)
    
    @classmethod
    def mark_email_sent(cls, db: Session, username: str) -> Optional["AuthorizationEmail"]:
        """
        Mark that an authorization email has been sent for a user.
        
        If a record doesn't exist for this user, one will be created.
        Returns the authorization email record or None if the user doesn't exist.
        """
        user_info = db.query(UserInfo).filter(UserInfo.username == username).first()
        if not user_info:
            return None
            
        record = cls.find_by_user_id(db, user_info.id)
        if not record:
            record = cls(user_info_id=user_info.id, email_sent=True)
            db.add(record)
        else:
            record.email_sent = True
        db.commit()
        return record
    
    @classmethod
    def is_email_sent(cls, db: Session, username: str) -> bool:
        """
        Check if an authorization email has been sent for a user.
        
        Returns True if an email has been sent, False otherwise.
        """
        record = cls.find_by_username(db, username)
        return record is not None and record.email_sent
