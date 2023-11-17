"""Module for handling notifications in the application.

This module provides functionality to trigger and manage notifications
for user accounts.
"""

import logging
from typing import Any, Dict, List, Union

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.models.account_models import Account
from app.database.connection import get_db

logging.basicConfig(level=logging.INFO)
BASE_URL = "/notifications"

router = APIRouter(prefix=BASE_URL, tags=["notifications"])


class NotificationManager:
    """ Notification manager class"""
    def _init_(self) -> None:
        """Initialize the NotificationManager."""
        self.notifications: List[Dict[str, Any]] = []

    def add_notification(
        self, account_id: str, notification_type: str, message: str
    ) -> None:
        """Add a notification to the manager.

        Args:
            account_id (str): The ID of the account.
            notification_type (str): The type of notification.
            message (str): The notification message.
        """
        notification = {
            "account_id": account_id,
            "type": notification_type,
            "message": message,
        }
        self.notifications.append(notification)

    def get_notifications(
        self, account_id: str
    ) -> List[Dict[str, Union[str, int]]]:
        """Get notifications for a specific account.

        Args:
            account_id (str): The ID of the account.

        Returns:
            List[Dict[str, Union[str, int]]]: List of notifications.
        """
        user_notifications = [
            n for n in self.notifications if n["account_id"] == account_id
        ]
        return user_notifications


notification_manager = NotificationManager()


def send_notification(
    account: Account, payload: Dict[str, Union[str, int]]
) -> None:
    """Send a notification for a specific account.

    Args:
        account (Account): The account to send the notification to.
        payload (Dict[str, Union[str, int]]): The payload containing \
        notification details.
    """
    if account:
        notification_type = payload.get("notification_type", "generic")
        message = payload.get("message", "No message")
        notification_manager.add_notification(
            account.id, notification_type, message
        )

@router.post("/trigger-notification/{account_id}")
async def trigger_notification(
    account_id: str,
    payload: Dict[str, Union[str, int]],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    """Trigger a notification for a specific account.

    Args:
        account_id (str): The ID of the account.
        payload (Dict[str, Union[str, int]]): The payload containing \
            notification details.
        background_tasks (BackgroundTasks): FastAPI background tasks.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: A response message.
    """
    account = db.query(Account).filter(Account.id == account_id).first()

    if account:
        background_tasks.add_task(send_notification, account, payload)
        return {"message": "Notification triggered successfully"}
    else:
        raise HTTPException(status_code=404, detail="Account not found")


@router.get("/get-notifications/{account_id}")
def get_notifications(
    account_id: str,
) -> Dict[str, Union[str, List[Dict[str, Any]]]]:
    """Get notifications for a specific account.

    Args:
        account_id (str): The ID of the account.

    Returns:
        Dict[str, Union[str, List[Dict[str, Any]]]]: Response \
            containing notifications.
    """
    notifications = notification_manager.get_notifications(account_id)
    return {"notifications": notifications}
