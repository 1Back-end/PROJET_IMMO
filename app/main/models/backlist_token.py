from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import Column, Integer, DateTime, String, event
from sqlalchemy.sql import func
from app.main.models.db.base_class import Base


@dataclass
class BlacklistToken(Base):
    """
    Represents a token that has been blacklisted.

    Attributes:
        uuid (int): The unique identifier for the blacklisted token.
        token (str): The actual token value that has been blacklisted.
        date_added (datetime): The date and time when the token was added to the blacklist.
        date_modified (datetime): The date and time when the token was last modified.
    """
    __tablename__ = 'blacklist_tokens'

    uuid = Column(String, primary_key=True, unique=True)  # Unique ID for the blacklist token
    token = Column(String(500), unique=False, nullable=False)  # The blacklisted token

    date_added: datetime = Column(DateTime, default=func.now())  # Date when token was added
    date_modified: datetime = Column(DateTime, default=func.now(), onupdate=func.now())  # Date when token was last modified

    def __repr__(self):
        """ Returns a string representation of the BlacklistToken instance. """
        return '<BlacklistToken: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(db, auth_token):
        """
        Check if the provided authorization token is blacklisted.

        Args:
            db: The database session.
            auth_token (str): The authorization token to check.

        Returns:
            bool: True if the token is blacklisted, otherwise False.
        """
        res = db.query(BlacklistToken).filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False


@event.listens_for(BlacklistToken, 'before_insert')
def update_created_modified_on_create_listener(mapper, connection, target):
    """
    Event listener that runs before a record is inserted, setting the creation and modified timestamps.

    Args:
        mapper: The SQLAlchemy mapper.
        connection: The database connection.
        target: The target instance being inserted.
    """
    target.date_added = datetime.now()
    target.date_modified = datetime.now()


@event.listens_for(BlacklistToken, 'before_update')
def update_modified_on_update_listener(mapper, connection, target):
    """
    Event listener that runs before a record is updated, setting the modified timestamp.

    Args:
        mapper: The SQLAlchemy mapper.
        connection: The database connection.
        target: The target instance being updated.
    """
    target.date_modified = datetime.now()
