from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

tasks = FastAPI()

class Tarefa(BaseModel):
    id: int
    descricao: str
    responsavel: str
    nivel: int
    prioridade: int
    situacao: str 

tarefas: list[Tarefa] = []

@tasks.get('/tarefas')
def listar():
    return tarefas

@tasks.post('/tarefas')
def adicionar(tarefa: Tarefa):
    tarefas.append(tarefa)
    return tarefas

@tasks.delete('/tarefas/{tarefa_id}', status_code=status.HTTP_204_NO_CONTENT)
def remover(tarefa_id: int):
    for tarefa_atual in tarefas:
        if tarefa_atual.id == tarefa_id:
            tarefas.remove(tarefa_atual)
            return
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tarefa não encontrada')

@tasks.get('/tarefas/{tarefas_id}')
def obter_tarefa(tarefa_id: int, response: Response):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            return tarefa

        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não há tarefa com id = {tarefa_id}')


@tasks.get('/tarefas/{tarefa.id}/situacao')
def listar_situacao(tarefa_situacao: str, response: Response):
    for tarefa in tarefas:
        if tarefa.situacao == tarefa_situacao:
            return tarefa
    
    
    
     