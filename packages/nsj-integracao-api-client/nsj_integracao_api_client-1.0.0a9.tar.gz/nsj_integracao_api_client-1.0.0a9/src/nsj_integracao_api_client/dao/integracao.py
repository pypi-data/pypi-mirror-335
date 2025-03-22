from typing import List
from datetime import datetime
from nsj_gcf_utils.db_adapter2 import DBAdapter2

class IntegracaoDAO:
    """
    Classe responsável pelas operacoees de CRUD ao banco de dados
    """
    _db: DBAdapter2

    def __init__(self, db: DBAdapter2 = None):
        self._db = db

    def listar_entidades_pendentes_integracao(self):
        sql = """SELECT
                entidade,
                coalesce(data_ultima_integracao, created_at) data_ultima_integracao
            FROM util.entidades_integracao
            """
        entidades = self._db.execute_query(sql)

        return { entidade['entidade'] :entidade['data_ultima_integracao'] for entidade in entidades }

    def listar_dados_exclusao(self, pk: str, entidade: str, data_ultima_integracao: datetime):
        sql = f"""SELECT
	        (oldvalue->>'{pk}')::uuid as id
        FROM ns.rastros
        WHERE
	        operacao= 'DELETE' AND
	        concat(schema,'.',tabela) = '{entidade}' AND
	        data >= :data
            """
        dados = self._db.execute_query(sql, data=data_ultima_integracao)

        return [ valor['id'] for valor in dados]


    def atualiza_ultima_integracao(self, entidade: str):
        sql = """INSERT INTO util.entidades_integracao(entidade, created_at)
        VALUES (:entidade, current_timestamp)
        ON CONFLICT (entidade) DO
        UPDATE
        SET
            data_ultima_integracao = current_timestamp
        WHERE
            excluded.entidade=:entidade_filtro"""
        self._db.execute(sql, entidade=entidade, entidade_filtro=entidade)


    def integracao_configurada(self) -> bool:
        sql = """SELECT
                count(*)
            FROM ns.configuracoes
            WHERE string_ini = 'API_TOKEN_SINCRONIA'"""
        count = self._db.execute_query_first_result(sql)

        return count["count"] > 0


    def recuperar_token(self) -> str:
        sql = """SELECT
                valor
            FROM ns.configuracoes
            WHERE string_ini = 'API_TOKEN_SINCRONIA'"""
        data = self._db.execute_query_first_result(sql)

        return data["valor"]


    def registra_token_tenant(self, token: str):
        sql = """INSERT INTO ns.configuracoes(valor, string_ini)
        VALUES (:valor, 'API_TOKEN_SINCRONIA');"""

        self._db.execute(sql, valor=token)


    def listar_grupos_empresariais(self, grupos: List[str] = None):
        sql = """SELECT
                grupoempresarial,
                codigo
            FROM ns.gruposempresariais"""

        if grupos:
            sql = sql + """
            WHERE codigo in :grupos"""

        grupos = self._db.execute_query(sql, grupos=tuple(grupos) if grupos else None)

        return grupos

    def registrar_grupos_empresariais(self, grupos_ids: List[str]):

        # Criar a consulta SQL com múltiplos valores
        values_placeholder = ", ".join(["(:id_{0})".format(i) for i in range(len(grupos_ids))])

        sql = f"""INSERT INTO util.grupos_empresariais_integracao(grupoempresarial)
        VALUES {values_placeholder}
        ON CONFLICT (grupoempresarial) DO UPDATE
        SET ativo = true;"""

        # Criar o dicionário de parâmetros
        params = {f"id_{i}": id_ for i, id_ in enumerate(grupos_ids)}

        rowcount, _ = self._db.execute(sql, **params)

        if rowcount!=len(grupos_ids):
            raise Exception(
                "Erro ao registrar grupos empresariais no banco de dados"
            )


    def desativar_grupos_empresariais(self, grupos_ids: List[str]):
        sql = """UPDATE util.grupos_empresariais_integracao
        SET ativo = false
        WHERE grupoempresarial in :grupos"""
        self._db.execute(sql, grupos=tuple(grupos_ids))


    def listar_dados_particionamento(self):
        sql = """SELECT
        gru.grupoempresarial,
        emp.empresa,
        est.estabelecimento
        FROM util.grupos_empresariais_integracao gei
        JOIN ns.gruposempresariais gru on ( gru.grupoempresarial =  gei.grupoempresarial )
        JOIN ns.empresas emp on ( emp.grupoempresarial = gru.grupoempresarial )
        JOIN ns.estabelecimentos est on (est.empresa = emp.empresa)
        WHERE gei.ativo"""

        return self._db.execute_query(sql)
