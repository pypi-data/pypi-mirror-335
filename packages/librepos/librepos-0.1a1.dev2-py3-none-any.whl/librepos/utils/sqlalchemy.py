from librepos.extensions import db

from .helpers import timezone_aware_datetime


class TimestampMixin:
    created_date = db.Column(db.Date, default=lambda: timezone_aware_datetime().date())
    created_time = db.Column(db.Time, default=lambda: timezone_aware_datetime().time())
    updated_date = db.Column(
        db.Date,
        default=lambda: timezone_aware_datetime().date(),
        onupdate=lambda: timezone_aware_datetime().date(),
    )
    updated_time = db.Column(
        db.Time,
        default=lambda: timezone_aware_datetime().time(),
        onupdate=lambda: timezone_aware_datetime().time(),
    )


class CRUDMixin:
    """Mixin to add CRUD operations to Flask-SQLAlchemy models."""

    @classmethod
    def create(cls, **kwargs):
        """Create a new instance and add it to the database."""
        instance = cls(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    @classmethod
    def get_all(cls):
        """Get all records."""
        instance = db.session.query(cls).all()
        return instance

    @classmethod
    def update(cls, record_id, **kwargs):
        """Update a record by ID with provided fields."""
        instance = db.session.query(cls).filter_by(id=record_id).first()
        if not instance:
            return None
        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        db.session.commit()
        return instance

    @classmethod
    def delete(cls, record_id):
        """Delete a record by its ID."""
        instance = db.session.query(cls).filter_by(id=record_id).first()
        if not instance:
            return False
        db.session.delete(instance)
        db.session.commit()
        return True

    @classmethod
    def get_by_id(cls, record_id):
        """Get a record by its ID."""
        instance = db.session.query(cls).filter_by(id=record_id).first()
        return instance

    def save(self):
        """Save the current instance to the database."""
        db.session.add(self)
        db.session.commit()

    def delete_instance(self):
        """Delete the current instance from the database."""
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def update_instance():
        """Update the current instance"""
        return db.session.commit()
