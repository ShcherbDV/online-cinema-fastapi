from datetime import datetime, timezone

from celery import shared_task

from src.database.models.accounts import ActivationTokenModel, PasswordResetTokenModel, RefreshTokenModel
from src.database.session_sync import SessionLocal


@shared_task(name="src.tasks.cleanup_tokens.cleanup_expired_tokens")
def cleanup_expired_tokens():
    db = SessionLocal
    try:
        now = datetime.now(timezone.utc)

        db.execute(ActivationTokenModel).where(ActivationTokenModel.expires_at < now)

        db.execute(PasswordResetTokenModel).where(PasswordResetTokenModel.expires_at < now)

        db.execute(RefreshTokenModel).where(RefreshTokenModel.expires_at < now)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
