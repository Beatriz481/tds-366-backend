from fastapi import FastAPI, HTTPException, Response, status,Query
from pydantic import BaseModel

tasks = FastAPI()

class Tarefa(BaseModel):
    id: int | None
    descricao: str
    responsavel: str | None
    nivel: int
    prioridade: int
    situacao: str | None

tarefas: list[Tarefa] = []

situacao_tarefa = ['NOVA', 'EM ANDAMENTO', 'PENDENTE', 'RESOLVIDA', 'CANCELADA']

nivel_tarefa = [1,3,5,8]

prioridade_tarefa = [1,2,3]

prox_id = 1

@tasks.get('/tarefas')
def listar():
    return tarefas

@tasks.post('/tarefas', status_code=status.HTTP_201_CREATED)
def adicionar(tarefa: Tarefa):
    global prox_id
    tarefa.id = prox_id
    tarefa.situacao = situacao_tarefa[0]
    tarefas.append(tarefa)
    prox_id += 1
    return tarefas

@tasks.delete('/tarefas/{tarefa_id}', status_code=status.HTTP_204_NO_CONTENT)
def remover(tarefa_id: int):
    for tarefa_atual in tarefas:
        if tarefa_atual.id == tarefa_id:
            tarefas.remove(tarefa_atual)
            return ('Tarefa Removida.')
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Tarefa não encontrada')

@tasks.get('/tarefas/{tarefa_id}')
def obter_tarefa(tarefa_id: int, response: Response):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            return tarefa

        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Não há tarefa com id = {tarefa_id}')


@tasks.get('/tarefas')
def filtrar_tarefas(
    nivel: int = Query(None, enum= nivel_tarefa),
    situacao: str = Query(None, enum= situacao_tarefa),
    prioridade: int = Query(None, enum = prioridade_tarefa)):

    filtro_tarefas = tarefas

    if nivel:
        filtro_tarefas = [tarefa for tarefa in filtro_tarefas if tarefa.nivel == nivel]

    if situacao:
        filtro_tarefas = [tarefa for tarefa in filtro_tarefas if tarefa.situacao == situacao.upper()]

    if prioridade:
        filtro_tarefas = [tarefa for tarefa in filtro_tarefas if tarefa.prioridade == prioridade]
    
    return filtro_tarefas   


@tasks.put('/tarefas/{tarefa_id}')
def atualizar_situacao(tarefa_id: int, situacao: int | None, tarefa: Tarefa | None):
    for i , task in enumerate(tarefas):
        if task.id == tarefa_id:
            if tarefa is not None:
                tarefa.id = task.id
                tarefa.situacao = tarefa.situacao.upper()
                if tarefa.situacao not in situacao_tarefa:
                    raise HTTPException(400, detail='situação inválida')
                tarefas[i] = tarefa
            else:
                if situacao is None:
                    raise HTTPException(400, detail='situação não informada')
                situacao = situacao.upper()
                atual = situacao_tarefa.index(task.situacao)
                nova = situacao_tarefa.index(situacao)
                
                if atual >= 3 or nova < atual:
                    raise HTTPException(400, detail=f'Não é possivel atualizar o status da tarefa para {situacao}')
                task.situacao = situacao
            return task   
    raise HTTPException(404, detail='Tarefa não encontrada') 