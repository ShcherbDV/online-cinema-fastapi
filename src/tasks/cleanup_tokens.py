from datetime import datetime, timezone

from celery_app import celery_app

from database.models.accounts import (
    ActivationTokenModel,
    PasswordResetTokenModel,
    RefreshTokenModel,
)
from database.session_sync import SessionLocal
from sqlalchemy import delete


@celery_app.task(name="tasks.cleanup_tokens.cleanup_expired_tokens")
def cleanup_expired_tokens():
    db = SessionLocal()

    try:
        now = datetime.now(timezone.utc)

        db.execute(delete(ActivationTokenModel)).where(ActivationTokenModel.expires_at < now)

        db.execute(delete(PasswordResetTokenModel)).where(
            PasswordResetTokenModel.expires_at < now
        )

        db.execute(delete(RefreshTokenModel)).where(RefreshTokenModel.expires_at < now)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
