from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError


class Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self, model) -> list:
        """Generic method to fetch all records from a given model."""
        records = self.session.query(model).all()
        return records

    def filter(self, model, **filters) -> list:
        """Generic method to filter records from a given model."""
        query = self.session.query(model)
        for key, value in filters.items():
            query = query.filter(getattr(model, key) == value)
        return query.all()

    def get(self, model, record_id) -> Any:
        """Get a single record by ID."""
        record = self.session.get(model, record_id)
        return record

    def commit(self):
        """Commit the current transaction."""
        self.session.commit()

    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()

    def add(self, model, **data) -> dict[str, Any]:
        """Insert a new row into the given model."""
        try:
            instance = model(**data)
            self.session.add(instance)
            self.commit()
            return instance
        except SQLAlchemyError as e:
            self.rollback()
            raise e

    def update(self, model, record_id, **data) -> Any:
        """Update an existing row by ID."""
        try:
            instance = self.get(model, record_id)
            if instance:
                for key, value in data.items():
                    setattr(instance, key, value)
                self.commit()
                return instance
            else:
                return None
        except SQLAlchemyError as e:
            self.rollback()
            raise e

    def delete(self, model, record_id) -> bool:
        """Delete a row by ID."""
        try:
            instance = self.get(model, record_id)
            if instance:
                self.session.delete(instance)
                self.commit()
                return True
            return False
        except SQLAlchemyError as e:
            self.rollback()
            raise e
