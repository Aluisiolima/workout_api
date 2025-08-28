from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from workout_api.categorias.schemas import CategoriaIn, CategoriaOut
from workout_api.categorias.models import CategoriaModel
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate

from workout_api.contrib.dependencies import DatabaseDependency
from workout_api.contrib.exceptions import ExceptionMessages, exceptions
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@exceptions()
@router.post(
    '/', 
    summary='Criar uma nova Categoria',
    status_code=status.HTTP_201_CREATED,
    response_model=CategoriaOut,
)
async def post(
    db_session: DatabaseDependency, 
    categoria_in: CategoriaIn = Body(...)
) -> CategoriaOut:
    try:
        categoria_out = CategoriaOut(id=uuid4(), **categoria_in.model_dump())
        categoria_model = CategoriaModel(**categoria_out.model_dump())

        db_session.add(categoria_model)
        await db_session.commit()
    except IntegrityError as e:
        await ExceptionMessages.handle_exception(e, db_session, 'Nome', categoria_in.nome)


    return categoria_out
    

@exceptions()
@router.get(
    '/{limit}&{offset}', 
    summary='Consultar todas as Categorias',
    status_code=status.HTTP_200_OK,
    response_model=Page[CategoriaOut],
)
async def query(db_session: DatabaseDependency) -> Page[CategoriaOut]:
    query = select(CategoriaModel)
    return await paginate(db_session, query)

@exceptions()
@router.get(
    '/{id}', 
    summary='Consulta uma Categoria pelo id',
    status_code=status.HTTP_200_OK,
    response_model=CategoriaOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> CategoriaOut:
    categoria: CategoriaOut = (
        await db_session.execute(select(CategoriaModel).filter_by(id=id))
    ).scalars().first()

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Categoria não encontrada no id: {id}'
        )
    
    return categoria