from typing import Any, Generic, TypeVar

from ormar import Model as OrmarModel
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=OrmarModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Provides generic CRUD (Create, Read, Update, Delete) operations for a given model.

    This class provides basic database operations for a specified Ormar model,
    using Pydantic schemas for data validation.

    Parameters:
        model: A Ormar model class
        schema: A Pydantic model (schema) class

    Methods:
        get(id): Retrieve an instance by its ID.
        create(obj_in): Create a new instance from a schema.
        update(db_obj, obj_in): Update an existing instance.
    """

    def __init__(self, model: type[ModelType]):
        """
        Initializes the CRUD object with a model class.

        Args:
            model (Type[ModelType]): The Ormar model class to perform operations on.
        """
        self.model = model

    async def get(self, id: str | int) -> ModelType | None:
        """
        Retrieve a single instance by its ID.

        Args:
            id (str | int): The ID of the instance to retrieve.

        Returns:
            ModelType | None: The retrieved instance if found, otherwise None.
        """
        return await self.model.objects.filter(id=id).get_or_none()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new model instance based on schema data.

        Args:
            obj_in (CreateSchemaType): Schema containing the data for the new instance.

        Returns:
            ModelType: The newly created model instance.
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        return await db_obj.save()

    async def update(self, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]) -> ModelType:
        """
        Update an existing model instance.

        Args:
            db_obj (ModelType): The instance to be updated.
            obj_in (Union[UpdateSchemaType, dict]): Schema or dictionary with updated values.

        Returns:
            The updated model instance.
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        return await db_obj.update(**update_data)
