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



@tasks.get('/tarefas')
def listar():
    return tarefas

@tasks.post('/tarefas', status_code=status.HTTP_201_CREATED)
def adicionar(tarefa: Tarefa):
    nivel_tarefa = [1,3,5,8]
    prioridade_tarefa = [1,2,3]
    
    if tarefa.nivel not in nivel_tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f'ERRO:Para nível escolha 1, 3, 5 ou 8')
    
    if tarefa.prioridade not in prioridade_tarefa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"ERRO:Para Prioridade escolha 1, 2, ou 3")
    
    tarefa.id = len(tarefas)
    tarefas.append(tarefa)
    return 'Tarefa adicionada.'
        

    

@tasks.put('/tarefas/cancelar/{tarefa_id}', status_code=status.HTTP_204_NO_CONTENT)
def cancelar(tarefa_id: int):
    for tarefa in tarefas:
        if tarefa.id == tarefa_id:
            if tarefa.situacao == 'Cancelada':
                   raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail= f'A tarefa {tarefa_id} já está cancelada')
            else:
                tarefa.situacao = 'Cancelada'
                return
    
    

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
