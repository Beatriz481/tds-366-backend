from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

tasks = FastAPI()

origins = ['http://localhost:5501', 'http://127.0.0.5501']

tasks.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class Tarefa(BaseModel):
    id: int | None
    descricao: str
    responsavel: str | None
    nivel: int
    prioridade: int
    situacao: str = 'Nova'


tarefas: list[Tarefa] = []


@tasks.post('/tarefas', status_code=status.HTTP_201_CREATED)
def criar_tarefa(tarefa: Tarefa):
    niveis_validos = [1,3,5,8]
    prioridades_validas = [1,2,3]

    if tarefa.nivel not in niveis_validos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Nível inválido.Os níveis válidos são:1,3,5 ou 8.')
    
    if tarefa.prioridade not in prioridades_validas:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Prioridade inválida.As prioridades válidas são:1,2 ou 3.')

    tarefa.id = len(tarefas) + 1
    tarefas.append(tarefa)
    return {"mensagem": "Tarefa criada."}



@tasks.get('/tarefas')
def listar():
    return tarefas


@tasks.put('/tarefas/{tarefa_id}/resolvida', status_code=status.HTTP_204_NO_CONTENT)
def marcar_resolvida(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            if tarefa.situacao == 'Resolvida':
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='A tarefa com ID {tarefa_id} já está com situação Resolvida.')
            elif tarefa.situacao == 'Em andamento':
                tarefa.situacao = 'Resolvida'
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='A tarefa não está com situação Em andamento.')    


@tasks.put('/tarefas/{tarefa_id}/pendente', status_code=status.HTTP_204_NO_CONTENT)
def marcar_pendente(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            if tarefa.situacao == 'Pendente':
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='A tarefa com ID {tarefa_id} já está com situação Pendente.')
            elif tarefa.situacao == 'Nova' or tarefa.situacao == 'Em andamento':
                tarefa.situacao = 'Pendente'
                return
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='A tarefa não está em situação de Nova ou Em andamento')


@tasks.put('/tarefas/{tarefa_id}/em_andamento', status_code=status.HTTP_204_NO_CONTENT)
def marcar_em_andamento(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            if tarefa.situacao == 'Em andamento':
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'A tarefa de ID {tarefa_id} já está com situação pendente.')
            
            elif tarefa.situacao == 'Nova' or tarefa.situacao == 'Pendente':
                tarefa.situacao = 'Em andamento'
                return
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail='A tarefa não está com situação de nova ou pendente.')



@tasks.put('/tarefas/{tarefa_id}/cancelar', status_code=status.HTTP_204_NO_CONTENT)
def cancelar_tarefa(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            if tarefa.situacao == 'Cancelada':
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=f'A tarefa com ID {tarefa_id} já está cancelada.')
            else:
                tarefa.situacao = 'Cancelada'
                return            
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'A tarefa com ID {tarefa_id} não foi encontrada.')
    

@tasks.get('/tarefas/{tarefa_id}')
def detalhes_tarefa(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            return tarefa

        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não há tarefa com id = {tarefa_id}')


@tasks.get('/tarefas/filtro_situacao/')
def filtrar_situacao(situacao: str, start: int = 0, end: str = len(tarefas)+1):
    tarefas_filtradas: list[Tarefa] = []
    situacao = situacao.lower().strip()

    for tarefa in tarefas:
        if tarefa.situacao.lower().strip() == situacao:
            tarefas_filtradas.append(tarefa)

    if len(tarefas_filtradas) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f'Não há tarefas em Situação:{situacao}.')
    else:
        return tarefas_filtradas 
           

@tasks.get('/tarefas/filtro_nivel_prioridade/')
def filtrar_nivel_prioridade(nivel: int, prioridade: int, start: int = 0, end: int = len(tarefas)+1):
    if start >= end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="O valor de 'start' deve ser menor que o valor de 'end'.")
    
    tarefas_filtradas: list[Tarefa] = []
    for tarefa in tarefas:
        if tarefa.nivel == nivel and tarefa.prioridade == prioridade:
            tarefas_filtradas.append(tarefa)

    if len(tarefas_filtradas) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Não existe tarefa com nível {nivel} e prioridade {prioridade}.")
    
    else:
        return tarefas_filtradas
