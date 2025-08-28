from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, status
from pydantic import UUID4
from workout_api.centro_treinamento.schemas import CentroTreinamentoIn, CentroTreinamentoOut
from workout_api.centro_treinamento.models import CentroTreinamentoModel
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
    summary='Criar um novo Centro de treinamento',
    status_code=status.HTTP_201_CREATED,
    response_model=CentroTreinamentoOut,
)
async def post(
    db_session: DatabaseDependency, 
    centro_treinamento_in: CentroTreinamentoIn = Body(...)
) -> CentroTreinamentoOut:
    try:
        centro_treinamento_out = CentroTreinamentoOut(id=uuid4(), **centro_treinamento_in.model_dump())
        centro_treinamento_model = CentroTreinamentoModel(**centro_treinamento_out.model_dump())
    
        db_session.add(centro_treinamento_model)
        await db_session.commit()
    except IntegrityError as e:
        await ExceptionMessages.handle_exception(e, db_session, 'Nome', centro_treinamento_in.nome)

    return centro_treinamento_out

@exceptions()
@router.get(
    '/{limit}&{offset}', 
    summary='Consultar todos os centros de treinamento',
    status_code=status.HTTP_200_OK,
    response_model=Page[CentroTreinamentoOut],
)
async def query(db_session: DatabaseDependency) -> Page[CentroTreinamentoOut]:
    query = select(CentroTreinamentoModel)
    return await paginate(db_session, query)

@exceptions()
@router.get(
    '/{id}', 
    summary='Consulta um centro de treinamento pelo id',
    status_code=status.HTTP_200_OK,
    response_model=CentroTreinamentoOut,
)
async def get(id: UUID4, db_session: DatabaseDependency) -> CentroTreinamentoOut:
    centro_treinamento_out: CentroTreinamentoOut = (
        await db_session.execute(select(CentroTreinamentoModel).filter_by(id=id))
    ).scalars().first()

    if not centro_treinamento_out:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Centro de treinamento não encontrado no id: {id}'
        )
    
    return centro_treinamento_out