from typing import List

from fastapi import APIRouter, Body, Depends, FastAPI, HTTPException, Path
from pydantic import BaseModel

from src.application.interfaces import ComponentRepository
from src.application.use_cases import (
    ComponentDTO,
    add_value_to_component_use_case,
    create_component_use_case,
    delete_component_use_case,
    get_component_values_use_case,
)
from src.domain.exceptions import UnitMismatchError
from src.infrastructure.repositories.memory import MemoryComponentRepository


class AddValueRequest(BaseModel):
    values: List[int]


class UpdateResponse(BaseModel):
    updates: int


class ValueResponse(BaseModel):
    value: float
    unit: str


def get_component_router(repository: ComponentRepository) -> APIRouter:
    router = APIRouter(prefix="/components", tags=["components"])

    @router.post("/", response_model=dict, status_code=201)
    async def create_component(
        component_data: ComponentDTO = Body(...),
    ) -> dict:
        """
        Create a new component

        Creates a new component with the specified parameters and stores it in the repository.
        """
        try:
            component = create_component_use_case(
                component=component_data, repository=repository
            )
            return component.dump()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    @router.put("/{component_id}/values", response_model=UpdateResponse)
    async def add_values(
        component_id: int = Path(..., description="The ID of the component"),
        request: AddValueRequest = Body(...),
    ) -> UpdateResponse:
        """
        Add values to a component

        Adds new values to the specified component and returns the number of updates made.
        """
        try:
            updates = add_value_to_component_use_case(
                component_id=component_id, values=request.values, repository=repository
            )
            return UpdateResponse(updates=updates)
        except UnitMismatchError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(
                status_code=404, detail=f"Component not found: {str(e)}"
            )

    @router.get("/{component_id}/values", response_model=List[ValueResponse])
    async def get_component_values(
        component_id: int = Path(..., description="The ID of the component"),
    ) -> List[ValueResponse]:
        """
        Get component values

        Retrieves all values stored for the specified component.
        """
        try:
            values = get_component_values_use_case(
                component_id=component_id, repository=repository
            )
            return values
        except Exception as e:
            raise HTTPException(
                status_code=404, detail=f"Component not found: {str(e)}"
            )

    @router.delete("/{component_id}", response_model=dict, status_code=200)
    async def delete_component(
        component_id: int = Path(..., description="The ID of the component"),
    ) -> dict:
        """
        Delete a component

        Permanently removes the specified component from the repository.
        Returns the deleted component data.
        """
        try:
            component = delete_component_use_case(
                component_id=component_id, repository=repository
            )
            return component.dump()
        except Exception as e:
            raise HTTPException(
                status_code=404, detail=f"Component not found: {str(e)}"
            )

    return router


def get_app() -> FastAPI:
    app = FastAPI()
    app.include_router(get_component_router(repository=MemoryComponentRepository()))
    return app
