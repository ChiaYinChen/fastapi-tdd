"""Provides a generic base class for CRUD (Create, Read, Update, Delete) operations.

This module defines `CRUDBase`, a generic repository class that can be inherited
by specific model repositories to provide standard database interaction methods.
It uses type variables to allow for flexible model and schema definitions.

Type Variables:
    ModelType: Represents the Ormar model type.
    CreateSchemaType: Represents the Pydantic schema for creating instances.
    UpdateSchemaType: Represents the Pydantic schema for updating instances.
"""
from typing import Any, Generic, TypeVar

from ormar import Model as OrmarModel
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=OrmarModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic base class for CRUD operations on an Ormar model.

    This class provides common database operations (Create, Read, Update, Delete -
    though Delete is not explicitly implemented here) for a specified Ormar model
    type (`ModelType`), using Pydantic schemas (`CreateSchemaType`, `UpdateSchemaType`)
    for data input and validation.

    Type Args:
        ModelType: The Ormar model type.
        CreateSchemaType: The Pydantic schema type for creating new model instances.
        UpdateSchemaType: The Pydantic schema type for updating existing model instances.

    Attributes:
        model (type[ModelType]): The Ormar model class that this CRUD object operates on.
    """

    def __init__(self, model: type[ModelType]):
        """Initializes the CRUDBase with a specific Ormar model.

        Args:
            model (type[ModelType]): The Ormar model class to be managed by this repository.
        """
        self.model = model

    async def get(self, id: str | int) -> ModelType | None:
        """Retrieves a single model instance by its ID.

        Args:
            id (str | int): The ID of the instance to retrieve.

        Returns:
            ModelType | None: The retrieved model instance if found, otherwise None.
        """
        return await self.model.objects.filter(id=id).get_or_none()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Creates a new model instance from the provided schema data.

        Args:
            obj_in (CreateSchemaType): A Pydantic schema instance containing the data
                for the new model instance.

        Returns:
            ModelType: The newly created and saved model instance.
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        return await db_obj.save()

    async def update(self, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType:
        """Updates an existing model instance with data from a schema or dictionary.

        Args:
            db_obj (ModelType): The existing model instance to be updated.
            obj_in (UpdateSchemaType | dict[str, Any]): A Pydantic schema instance
                or a dictionary containing the data to update. If a schema is provided,
                fields that are not set (i.e., `None` and not explicitly passed)
                will be excluded from the update.

        Returns:
            ModelType: The updated and saved model instance.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        return await db_obj.update(**update_data)
