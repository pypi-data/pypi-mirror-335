import os

import time

import copy

import hashlib

import base64

import datetime

import tzdata

from typing import List, Dict

from zoneinfo import ZoneInfo


from enum import Enum

import requests

from nsj_gcf_utils.json_util import convert_to_dumps, json_loads, json_dumps

from nsj_rest_lib.dto.dto_base import DTOBase
from nsj_rest_lib.descriptor.dto_field import DTOField
from nsj_rest_lib.descriptor.dto_list_field import DTOListField

from nsj_integracao_api_client.infra.injector_factory import InjectorFactory


from nsj_integracao_api_client.infra.debug_utils import DebugUtils as _du

class Environment(Enum):
    LOCAL = "LOCAL"
    DEV = "DEV"
    QA = "QA"
    PROD = "PROD"

entidades_integracao: List[str] = [
    # --- apenas testes ---
    ## "persona.valestransportespersonalizadostrabalhadores"
    # --- Dimensoes ---
    'ns.gruposempresariais',
    'ns.empresas',
    'ns.estabelecimentos',
    'ns.configuracoes',
    'financas.bancos',
    'persona.faixas',
    'ns.obras',
    'persona.lotacoes',
    'ponto.regras',# ns.empresas
    'persona.sindicatos',
    'ns.feriados',
    'persona.instituicoes',
    'persona.eventos',
    'persona.tiposdocumentoscolaboradores',
    'persona.tiposhistoricos',
    'persona.tiposanexos',
    'persona.processos',
    'persona.ambientes',
    'persona.condicoesambientestrabalho',
    'persona.departamentos',
    'persona.funcoes',
    'persona.jornadas',
    'persona.horarios',
    'persona.horariosespeciais',
    'persona.cargos',
    'persona.niveiscargos',
    'persona.tiposfuncionarios',
    'persona.trabalhadores',
    'persona.dependentestrabalhadores',
    'persona.escalasfolgastrabalhadores',
    'persona.beneficios',
    'persona.concessionariasvts',
    'persona.tarifasconcessionariasvtstrabalhadores',
    'persona.configuracoesordemcalculomovimentos',
    'persona.configuracoesordemcalculomovimentosponto',
    'persona.historicos',
    'persona.medicos',
    'persona.rubricasponto',
    #'persona.rubricasapontamento',só na web???
    # Fatos
    'persona.compromissostrabalhadores',
    'persona.convocacoestrabalhadores',
    'persona.dispensavalestransportestrabalhadores',
    'persona.emprestimostrabalhadores',
    'persona.historicosadiantamentosavulsos',
    'persona.adiantamentosavulsos',
    'persona.membroscipa',
    'persona.reajustessindicatos',
    'persona.reajustestrabalhadores',
    'ponto.compensacoeslancamentos',
    'ponto.pagamentoslancamentos',
    'persona.admissoespreliminares',# --resolver fk solicitacoesadmissoes
    'persona.avisosferiastrabalhadores', # resolver kf solicitacoesferias
    'persona.pendenciaspagamentos',
    'persona.documentoscolaboradores',
    'persona.faltastrabalhadores', # resolver fk solicitacoesfaltas
    'persona.mudancastrabalhadores',
    'ponto.diascompensacoestrabalhadores',
    'persona.afastamentostrabalhadores',
    'ponto.atrasosentradascompensaveistrabalhadores',
    'ponto.saidasantecipadascompensaveistrabalhadores',
    'persona.beneficiostrabalhadores',
    'persona.movimentosponto',
    'persona.movimentos',
    #'persona.calculostrabalhadores' Não será reativada
]

TAMANHO_PAGINA: int = 100

# Flags trace
_E_SEND_DATA = False
_E_CHECK_INT = False

_entidades_particionadas_por_grupo = ['ns.empresas', 'ns.configuracoes']

_entidades_particionadas_por_empresa = [
    'ns.configuracoes',
    'persona.movimentosponto',
    'ns.estabelecimentos',
    'persona.trabalhadores',
    'persona.processos',
    'persona.jornadas',
    'persona.ambientes',
    'persona.funcoes',
    'persona.cargos',
    #'persona.beneficios',#'persona.lotacoes'Removido pois existem entidades dependentes que não são são particionadas (persona.beneficiostrabalhadores)
    'persona.configuracoesordemcalculomovimentos',
    'persona.configuracoesordemcalculomovimentosponto',
    'persona.membroscipa',
    'persona.movimentos',
    'persona.rubricasponto',
    'persona.condicoesambientestrabalho',
    'persona.tiposfuncionarios',
    'persona.horarios',
    'persona.admissoespreliminares',
    'persona.eventos',
    #'persona.lotacoes'Removido pois existem entidades dependentes que não são são particionadas (persona.beneficiostrabalhadores)
]

_entidades_particionadas_por_estabelecimento = [
    'ns.configuracoes',
    'ns.obras',
    'persona.movimentosponto',
    'persona.trabalhadores',
    'ns.configuracoes',
    'persona.processos',
    'persona.jornadas',
    'persona.ambientes',
    'persona.funcoes',
    'persona.cargos',
    #'persona.beneficios',#'persona.lotacoes'Removido pois existem entidades dependentes que não são são particionadas (persona.beneficiostrabalhadores)
    'persona.configuracoesordemcalculomovimentos',
    'persona.configuracoesordemcalculomovimentosponto',
    'persona.membroscipa',
    'persona.movimentos',
    'persona.rubricasponto',
    'persona.condicoesambientestrabalho',
    'persona.tiposfuncionarios',
    'persona.horarios',
    'persona.admissoespreliminares',
    'persona.eventos',
    #'persona.lotacoes' Removido pois existem entidades dependentes que não são são particionadas (persona.beneficiostrabalhadores)
]


AUTH_HEADER = 'X-API-Key'


def medir_tempo(alias=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            inicio = time.perf_counter()
            resultado = func(*args, **kwargs)
            fim = time.perf_counter()
            nome = alias if alias else func.__name__
            duracao = fim - inicio
            if duracao < 60:
                print(f"\033[94m{nome} executado em {duracao:.3f} segundos\033[0m")
            elif duracao < 3600:
                minutos = duracao // 60
                segundos = duracao % 60
                print(f"\033[94m{nome} executado em {minutos:.0f} minutos e {segundos:.3f} segundos\033[0m")
            else:
                horas = duracao // 3600
                minutos = (duracao % 3600) // 60
                segundos = duracao % 60
                print(f"\033[94m{nome} executado em {horas:.0f} horas, {minutos:.0f} minutos e {segundos:.3f} segundos\033[0m")
            return resultado
        return wrapper
    return decorator


class IntegradorService():

    _injector : InjectorFactory
    _api_key: str = None
    _tenant: int = None
    # Caso se deseje usar um tenant diferente do especificado no token
    _forced_tenant: int = None
    _dao_intg: 'IntegracaoDAO' = None
    _filtros_particionamento: list = None
    _env : Environment = Environment.PROD
    _save_point: dict = {
        #"persona.trabalhadores" : "11e32b78-f02c-46b4-81c0-a61447fffe41"
    }
    _ignored_fields : list = ["tenant", "lastupdate"]
    _tz_br: ZoneInfo

    def __init__(self, injector: InjectorFactory, log, env : Environment = Environment.PROD, forced_tenant : int = None):
        self._injector = injector
        self._log = log
        self._env = env
        self._forced_tenant = forced_tenant

        self._tz_br = ZoneInfo("America/Sao_Paulo")
        self._carregar_savepoint()

    def _carregar_savepoint(self):
        try:
            with open('savepoint.json', 'r') as f:
                self._save_point = json_loads(f.read())
                entidade_salva = list(self._save_point.keys())[0]
                self._log.mensagem(f"Savepoint carregado para : {entidade_salva }")
        except FileNotFoundError:
            self._save_point = {}

    def _trace_envio(self, filename, content):
        _du.conditional_trace(
            condition=_E_SEND_DATA,
            func=_du.save_to_file,
            filename=filename,
            content=content
        )

    def _trace_check(self, filename, content):
        _du.conditional_trace(
            condition=_E_CHECK_INT,
            func=_du.save_to_file,
            filename=filename,
            content=content
        )

    def _fields_to_load(self, dto_class) -> dict:

        fields = {}
        fields.setdefault("root", set(dto_class.fields_map.keys()))

        for _related_entity, _related_list_fields in dto_class.list_fields_map.items():
            fields["root"].add(_related_entity)
            fields.setdefault(_related_entity, set())
            _related_fields = _related_list_fields.dto_type.fields_map.keys()
            for _related_field in _related_fields:
                fields["root"].add(f"{_related_entity}.{_related_field}")
                fields[_related_entity].add(_related_field)

        return fields


    def _integracao_dao(self):
        if self._dao_intg is None:
            self._dao_intg = self._injector.integracao_dao()
        return self._dao_intg


    def _url_base(self) -> str:
        if self._env == Environment.LOCAL:
            return "http://localhost:5000/integracao-pessoas-api/66"
        elif self._env == Environment.DEV:
            return "https://api.nasajon.dev/integracao-pessoas-api/66"
            #return "http://localhost:5000/integracao-pessoas-api/66"
        elif self._env == Environment.QA:
            return "https://api.nasajon.qa/integracao-pessoas-api/66"
            #return "http://localhost:5000/integracao-pessoas-api/66"
        elif self._env == Environment.PROD:
            #return "http://localhost:5000/integracao-pessoas-api/66"
            return "https://api4.nasajon.app/integracao-pessoas-api/66"
        else:
            raise ValueError(f"Ambiente desconhecido: {self._env}")


    def _url_diretorio(self) -> str:
        if self._env == Environment.LOCAL:
            return "https://dir.nasajon.dev"
        elif self._env == Environment.DEV:
            return "https://dir.nasajon.dev"
        elif self._env == Environment.QA:
            return "https://dir.nasajon.qa"
        elif self._env == Environment.PROD:
            return "https://diretorio.nasajon.com.br"
        else:
            raise ValueError(f"Ambiente desconhecido: {self._env}")

    def _decode_token(self, token):
        data = token.split('.')[1]
        padding = '=' * (4 - len(data) % 4)
        str_token = base64.b64decode(data + padding).decode('utf-8')
        return  json_loads(str_token)


    @property
    def api_key(self):

        if self._api_key is None:
            self._api_key = self._integracao_dao().recuperar_token()

        return self._api_key


    @property
    def tenant(self):

        if self._forced_tenant is not None:
            return self._forced_tenant

        if self._tenant is None:
            decoded_token = self._decode_token(self.api_key)
            self._tenant = decoded_token["tenant_id"]

        return self._tenant

    def _tratar_resposta(self, response, dict_data):
        if response.status_code < 200 or response.status_code > 299:
            if 'application/json' in response.headers.get('Content-Type', ''):
                _json_response = response.json()
                if isinstance(_json_response, dict):
                    _message = _json_response['message'] if 'message' in _json_response else ''
                else:
                    _message = _json_response[0]['message'] if 'message' in _json_response[0] else ''
            else:
                _message = response.text
            raise Exception(f"""Erro ao enviar dados ao servidor:
            Endpoint: {response.url}
            Status: {response.status_code} - {response.reason}
            Mensagem: {_message}""", convert_to_dumps(dict_data))

    def _enviar_dados(self, dict_data, acao):
        """
        """
        self._trace_envio(f"trace/send_data_{acao}_{_du.time()}.json", json_dumps(dict_data))

        upsert = True #False if (acao in ["processos"] and self._env == Environment.PROD) else True

        s = requests.Session()
        s.headers.update({'Content-Type':'application/json', AUTH_HEADER: self.api_key})

        if upsert:
            response = s.put(f'{self._url_base()}/{acao}?upsert=true', json=convert_to_dumps(dict_data))

            if response.status_code == 413:
                for _item in dict_data:
                    response = s.put(f'{self._url_base()}/{acao}?upsert=true', json=convert_to_dumps(_item))
                    self._tratar_resposta(response, dict_data)
            else:
                self._tratar_resposta(response, dict_data)

        else:
            for _item in dict_data:
                response = s.post(f'{self._url_base()}/{acao}', json=convert_to_dumps(_item))
                if response.status_code < 200 or response.status_code > 299:
                    if 'application/json' in response.headers.get('Content-Type', '') and \
                    isinstance(response.json(), list) and 'message' in response.json()[0] and \
                    ('_bt_check_unique' in response.json()[0].get('message', '') or response.status_code == 409):
                        raise Exception(f"""Erro ao enviar dados ao servidor:
                        Endpoint: {response.url}
                        Status: {response.status_code} - {response.reason}
                        Mensagem: {response.text}""", convert_to_dumps(dict_data))


    def _apagar_dados(self, dict_data, acao):
        """
        """
        s = requests.Session()
        s.headers.update({'Content-Type':'application/json', AUTH_HEADER: self.api_key})
        response = s.delete(f'{self._url_base()}/{acao}?tenant={self.tenant}', json=convert_to_dumps(dict_data))

        if response.status_code < 200 or response.status_code > 299:
            if 'application/json' in response.headers.get('Content-Type', ''):
                _json_response = response.json()
                if isinstance(_json_response, dict):
                    _message = _json_response['message']if 'message' in _json_response else ''
                else:
                    _message = _json_response[0]['message'] if 'message' in _json_response[0] else ''

            else:
                _message = response.text
            raise Exception(f"""Erro ao apagar dados ao servidor:
            Endpoint: {response.url}
            Status: {response.status_code} - {response.reason}
            Mensagem: {_message}""")


    def _gerar_token_tenant(self, chave_ativacao: str) -> str:
        s = requests.Session()
        s.headers.update({
            'Content-Type':'application/x-www-form-urlencoded',
            'Accept':'application/json'
        })
        response = s.post(
            f'{self._url_diretorio()}/v2/api/gerar_token_ativacao_sincronia/',
            data={"codigo_ativacao": chave_ativacao})

        if response.status_code == 200:
            _json = response.json()
            if "apiKey" in _json:
                return _json["apiKey"]
            else:
                raise Exception(f'Retorno desconhecido:{_json}')

        if response.status_code < 200 or response.status_code > 299:
            if 'application/json' in response.headers.get('Content-Type', ''):
                _json_response = response.json()
                _message = _json_response['message'] if 'message' in _json_response else ''
            else:
                _message = response.text
            raise Exception(f"""Erro ao enviar dados ao servidor:
            Endpoint: {response.url}
            Status: {response.status_code} - {response.reason}
            Mensagem: {_message}""")


    def consultar_integridade_de(self, acao: str, filtros: dict, ultimo_id ,detalhar_diferencas: bool):

        filtros_str = None
        if filtros:
            filtros_str = ("&".join(
                [ f"{_chave}={filtros[_chave]}" for _chave in filtros.keys() ]
            ))

        s = requests.Session()
        s.headers.update({'Content-Type':'application/json', AUTH_HEADER: self.api_key})
        _url = (
            f'{self._url_base()}/{acao}/verificacao-integridade?tenant={self.tenant}&source={detalhar_diferencas}'
            f'{"&" + filtros_str if filtros_str else ""}'
            f'&limit={TAMANHO_PAGINA}'
            f'{"&after="+str(ultimo_id) if ultimo_id else ""}'
        )
        response = s.get(_url)
        response_content = response.json() if 'application/json' in response.headers.get('Content-Type', '') else response.text

        if response.status_code < 200 or response.status_code > 299:
            if isinstance(response_content, dict):
                _message = response_content.get('message', '')
            else:
                _message = response_content
            raise Exception(f"""Erro ao consultar a integridade no servidor:
            Endpoint: {response.url}
            Status: {response.status_code} - {response.reason}
            Mensagem: {_message}""")
        return response_content


    def _integracao_foi_configurada(self):
        return self._integracao_dao().integracao_configurada()


    def _validar_grupos_empresariais(self, grupos) -> List[Dict[str, str]]:

        grupos_cadastrados = self._integracao_dao().listar_grupos_empresariais(grupos)
        _cods = [grupo['codigo'] for grupo in grupos_cadastrados]
        _grupos_faltantes = [grupo for grupo in grupos if grupo not in _cods]
        assert len(_grupos_faltantes)==0, f"Grupo(s) '{','.join(_grupos_faltantes)}' não encontrado(s)."
        return grupos_cadastrados


    def executar_instalacao(self, chave_ativacao: str, grupos: List[str]):

        assert chave_ativacao, "Chave de ativação não pode ser vazia."
        self._log.mensagem(f"Executando instalação com a chave de ativação: {chave_ativacao}")

        assert not self._integracao_foi_configurada(), "Integração já instalada anteriormente."
        _token: str = self._gerar_token_tenant(chave_ativacao)
        _tenant = _token.split('.')[1]
        padding = '=' * (4 - len(_tenant) % 4)
        _tenant_str = base64.b64decode(_tenant + padding)
        decoded_token = json_loads(_tenant_str.decode('utf-8'))

        if grupos:
            grupos_cadastrados = self._validar_grupos_empresariais(grupos)
        else:
            grupos_cadastrados = self._integracao_dao().listar_grupos_empresariais()

        _ids  = [str(grupo['grupoempresarial']) for grupo in grupos_cadastrados]

        self._integracao_dao().registrar_grupos_empresariais(_ids)

        self._integracao_dao().registra_token_tenant(_token)

        self._log.mensagem(f"Instalação efetuada com sucesso para o tenant '{decoded_token['tenant_id']}'.")


    def ativar_grupos_empresariais(self, grupos: List[str]):

        assert self._integracao_foi_configurada(), "Integração não configurada!"
        assert grupos, "Grupos não podem ser vazios!"

        if grupos:
            grupos_cadastrados = self._validar_grupos_empresariais(grupos)
        else:
            grupos_cadastrados = self._integracao_dao().listar_grupos_empresariais()

        _ids  = [grupo['grupoempresarial'] for grupo in grupos_cadastrados]

        self._integracao_dao().registrar_grupos_empresariais(_ids)

        self._log.mensagem(f"Grupos empresariais ativados: '{','.join(grupos)}'.")


    def desativar_grupos_empresariais(self, grupos: List[str]):

        assert self._integracao_foi_configurada(), "Integração não configurada!"
        assert grupos, "Grupos não podem ser vazios!"

        grupos_cadastrados = self._validar_grupos_empresariais(grupos)

        _ids  = [grupo['grupoempresarial'] for grupo in grupos_cadastrados]

        self._integracao_dao().desativar_grupos_empresariais(_ids)

        self._log.mensagem(f"Grupos empresariais desativados: '{','.join(grupos)}'.")


    def _filtro_particionamento_de(self, entidade: str):

        if self._filtros_particionamento is None:
            _dados_part = self._integracao_dao().listar_dados_particionamento()

            self._filtros_particionamento = [
                {'grupoempresarial' : ",".join(list(map(lambda i: str(i["grupoempresarial"]), _dados_part)))},
                {'empresa' : ",".join(list(map(lambda i: str(i["empresa"]), _dados_part)))},
                {'estabelecimento' : ",".join(list(map(lambda i: str(i["estabelecimento"]), _dados_part)))}
            ]

        if entidade in _entidades_particionadas_por_grupo:
            return  self._filtros_particionamento[0]

        if entidade in _entidades_particionadas_por_empresa:
            return self._filtros_particionamento[1]

        if entidade in _entidades_particionadas_por_estabelecimento:
            return self._filtros_particionamento[2]


    def _dto_to_api(
        self,
        campos: Dict[str, List[str]],
        data: List[DTOBase]
    ) -> List[dict]:
        # Converte os objetos DTO para dicionários e adiciona o tenant
        transformed_data = []
        for dto in data:
            dto.tenant = self.tenant
            dto_dict = dto.convert_to_dict(campos)
            if "created_by" in dto_dict and not dto_dict["created_by"] is None:
                dto_dict["created_by"] = {"id": dto_dict["created_by"]}
            transformed_data.append(dto_dict)

        return transformed_data


    def _save_point_for(self, tabela: str):
        return self._save_point.get(tabela, None)

    def _do_save_point(self, tabela: str, chave):
        self._save_point[tabela] = chave
        with open('savepoint.json', 'w') as f:
            f.write(f'{{ "{tabela}": "{chave}" }} ' if chave else f'{{ "{tabela}": null }} ')

    def _save_point_clear(self):
        self._save_point.clear()
        if os.path.exists('savepoint.json'):
            os.remove('savepoint.json')


    @medir_tempo("Carga inicial")
    def executar_carga_inicial(self):

        assert self._integracao_foi_configurada(), "Integração não configurada!"

        _dao = self._integracao_dao()

        self._log.mensagem(f"Tenant: {self.tenant} .")
        self._log.mensagem(f"{len(entidades_integracao)} entidades para processar.")

        entidades_carga_inicial = copy.copy(entidades_integracao)
        if self._save_point:
            for entidade in entidades_integracao:
                if not entidade in self._save_point:
                    entidades_carga_inicial.remove(entidade)
                else:
                    break

        for entidade in entidades_carga_inicial:

            # if not entidade in ['persona.adiantamentosavulsos','persona.trabalhadores']:
            #     continue

            _idx = entidades_integracao.index(entidade) + 1
            self._log.mensagem(f"Efetuando carga {entidade}, {_idx} de {len(entidades_integracao)}.")
            _count = 0

            # Carregar dados paginados para integrar
            service = self._injector.service_for(entidade, True)
            fields = self._fields_to_load(service._dto_class)
            filters = self._filtro_particionamento_de(entidade)
            search_query = None

            pagina = 0
            self._log.mensagem(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extraindo dados para carga.")
            while True:
                current_after = self._save_point_for(entidade)
                _data = service.list(
                        current_after,
                        TAMANHO_PAGINA,
                        fields,
                        None,
                        filters,
                        search_query=search_query,
                    )

                _count = _count + len(_data)

                if len(_data)==0:
                    if current_after is None:
                        self._log.mensagem("Sem dados para transferir, indo adiante...")
                    else:
                        self._log.mensagem("Entidade integrada com sucesso.")
                    break

                self._log.mensagem(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {_count} registros...")

                dict_data = self._dto_to_api(fields, _data)

                self._log.mensagem(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Enviando dados para a api.")
                self._enviar_dados(dict_data, entidade.split('.')[1])

                # Aponta a leitura para a próxima página
                _last = _data[-1]
                self._do_save_point(entidade, getattr(_last, _last.pk_field))

            _dao.atualiza_ultima_integracao(entidade)
            self._save_point_clear()

        print("\033[92mCarga inicial finalizada com sucesso!\033[0m")


    @medir_tempo("Integração")
    def executar_integracao(self):

        assert self._integracao_foi_configurada(), "Integração não configurada!"

        self._log.mensagem(f"Tenant: {self.tenant} .")

        _dao = self._integracao_dao()

        entidades_pendentes = _dao.listar_entidades_pendentes_integracao()

        entidades_pendentes = {entidade: entidades_pendentes[entidade] for entidade in entidades_integracao if entidade in entidades_pendentes.keys()}

        self._log.mensagem(f"{len(entidades_pendentes)} entidades para processar." if entidades_pendentes else "Nenhuma entidade para processar.")
        _resumo = {}

        for entidade, data_ultima_integracao in entidades_pendentes.items():

            _idx = list(entidades_pendentes.keys()).index(entidade) + 1
            self._log.mensagem(f"Integrando {entidade}, {_idx} de {len(entidades_pendentes)}.")
            _count = 0

            # Carregar dados paginados para integrar
            service = self._injector.service_for(entidade, True)
            current_after = None
            fields = self._fields_to_load(service._dto_class) #tornar publico
            filters = self._filtro_particionamento_de(entidade)
            search_query = None
            _acao = entidade.split('.')[1]

            # Dados criados apos data_ultima_integracao
            # filtro_criacao = filters.copy() if filters else {}
            # filtro_criacao['created_at'] = data_ultima_integracao
            # while True:

            #     data = service.list(
            #             current_after,
            #             TAMANHO_PAGINA,
            #             fields,
            #             None,
            #             filtro_criacao,
            #             search_query=search_query,
            #         )

            #     if len(data)==0:
            #         self._log.mensagem("Sem dados para criar, indo adiante...")
            #         break

            #     # Convertendo para o formato de dicionário (permitindo omitir campos do DTO) e add tenant
            #     dict_data = self._dto_to_api(fields, data)

            #     # Mandar a bagatela por apis
            #     self._enviar_dados(dict_data, _acao)

            #     # Aponta a leitura para a próxima página
            #     _last = data[-1]
            #     current_after = getattr(_last, _last.pk_field)

            # Dados alterados apos data_ultima_integracao
            filtro_atualizacao = filters.copy() if filters else {}
            filtro_atualizacao['lastupdate'] = data_ultima_integracao
            while True:

                _data = service.list(
                        current_after,
                        TAMANHO_PAGINA,
                        fields,
                        None,
                        filtro_atualizacao,
                        search_query=search_query,
                    )

                _count = _count + len(_data)

                if len(_data)==0:
                    if current_after is None:
                        self._log.mensagem("Sem dados para atualizar, indo adiante...")
                    else:
                        self._log.mensagem("Entidade integrada com sucesso.")
                    break

                self._log.mensagem(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {_count} registros...")
                _resumo[entidade] = _count

                # Convertendo para o formato de dicionário (permitindo omitir campos do DTO) e add tenant
                dict_data = self._dto_to_api(fields, _data)

                # Mandar a bagatela por apis
                self._enviar_dados(dict_data, _acao)

                # Aponta a leitura para a próxima página
                _last = _data[-1]
                current_after = getattr(_last, _last.pk_field)

            # Dados excluidos apos data_ultima_integracao
            _coluna_id = service._dto_class.fields_map[service._dto_class.pk_field].entity_field
            para_apagar = _dao.listar_dados_exclusao(_coluna_id, entidade, data_ultima_integracao)
            if para_apagar:
                _resumo[entidade] = _resumo.get(entidade, 0) + len(para_apagar)
                self._apagar_dados(para_apagar, _acao)

            _dao.atualiza_ultima_integracao(entidade)

        print("\033[92mIntegração finalizada com sucesso!\033[0m")
        if _resumo:
            print(f"\033[92mResumo da integração:\033[0m {', '.join(f'{k}: {v}' for k, v in _resumo.items())}")


    def integrity_fields(self, dto) -> dict:
        fields = {"root": set()}

        for _field_name in sorted(dto.integrity_check_fields_map.keys()):

            if _field_name in self._ignored_fields:
                continue

            _field_obj = dto.integrity_check_fields_map[_field_name]

            if isinstance(_field_obj, DTOField):
                fields["root"].add(_field_name)
                continue

            if isinstance(_field_obj, DTOListField):
                fields["root"].add(_field_name)
                fields.setdefault(_field_name, set())

                for _related_field in sorted(_field_obj.dto_type.integrity_check_fields_map.keys()):
                    if not _related_field in self._ignored_fields:
                        fields["root"].add(f"{_field_name}.{_related_field}")
                        fields[_field_name].add(_related_field)

        return fields

    def tratar_campos_comparacao(self, dados: dict, campos_ignorados: list):

        keys_to_delete = []
        for chave, valor in dados.items():

            # Remove timezone para comparação
            if isinstance(valor, (datetime.datetime, datetime.date)):
                if valor.tzinfo is not None:
                    # print("-")
                    # print(valor.tzinfo)
                    # print(valor)
                    # print(valor.astimezone(self._tz_br).tzinfo)
                    # print(valor.astimezone(self._tz_br))
                    # print("-")
                    dados[chave] = valor.astimezone(self._tz_br).replace(microsecond=0, tzinfo=None)
                else:
                    dados[chave] = valor.replace(microsecond=0, tzinfo=None)

            # Ignora campos não úteis
            if chave in campos_ignorados:
                keys_to_delete.append(chave)

            # Aplica regras em sublistas
            if isinstance(valor, list):
                valor.sort(key=lambda x: x['id'])
                for item in valor:
                    self.tratar_campos_comparacao(item, campos_ignorados)

        for chave in keys_to_delete:
            del dados[chave]


    def converte_dados_para_hash(self, dto, integrity_fields):

        data = dto.convert_to_dict(integrity_fields)

        self.tratar_campos_comparacao(data, self._ignored_fields)

        concatenated_valors = ''.join(
            str(data[chave]) for chave in sorted(data.keys())
        )

        data['tenant'] = self.tenant

        return {
            'id': str(data[dto.pk_field]),
            'hash': hashlib.sha256(concatenated_valors.encode('utf-8')).hexdigest(),
            '_source': data,
            '_source_hash': concatenated_valors
        }


    def comparar_dados(self, dados_referencia, dados_comparacao):

        if dados_referencia['campos']['_'] != dados_comparacao['campos']['_']:
            print(f"\033[91mExistem diferenças entre os campos comparados:\r\n\r\nLocal: {dados_referencia['campos']['_']}\r\n\r\nWeb  : {dados_comparacao['campos']['_']}\033[0m")

        if dados_referencia['registros'] != dados_comparacao['registros']:
            print(f"\033[91mExistem diferenças nas quantidades de dados:\r\n\r\nLocal: {dados_referencia['registros']}\r\n\r\nWeb  : {dados_comparacao['registros']}\033[0m")

        # Índices para facilitar busca por ID
        idx_referencia = {item['id']: item for item in dados_referencia['dados']}
        idx_comparacao = {item['id']: item for item in dados_comparacao['dados']}

        # Inicializar listas de mudanças
        _criar = []
        _atualizar = []
        _excluir = []
        _diff = {}

        # Verificar itens nos dados de referência
        for item_id, item_ref in idx_referencia.items():
            if item_id not in idx_comparacao:
                # Criar se não existe nos dados de comparação
                _criar.append(item_ref['_source'])
            elif item_ref['hash'] != idx_comparacao[item_id]['hash']:
                # Atualizar se o hash é diferente
                _atualizar.append(item_ref['_source'])
                # Adiciona para exibir os dados puros se disponível
                if '_source' in idx_comparacao[item_id]:
                    _diff[item_ref['_source_hash']] = idx_comparacao[item_id]['_source']

        # Verificar itens nos dados de comparação
        for item_id in idx_comparacao.keys():
            if item_id not in idx_referencia:
                # Excluir se não existe em A
                _excluir.append(idx_comparacao[item_id]['id'])

        return _criar, _atualizar, _excluir, _diff

    @medir_tempo("Verificação de integridade")
    def executar_verificacao_integridade(
        self,
        parar_caso_diferencas : bool = False,
        detalhar_diferencas: bool = False,
        corrigir_auto: bool = False,
        tenant: int = 0
    ):

        assert self._integracao_foi_configurada(), "Integração não configurada!"

        self._log.mensagem(f"Tenant: {self.tenant} .")

        if corrigir_auto:
            assert self.tenant==tenant, "Tenant informado para correção não é igual ao configurado"

        self._log.mensagem(f"{len(entidades_integracao)} entidades para verificar integridade.")

        _diferencas = False
        _idx = 0
        for entidade in reversed(entidades_integracao):

            # if not entidade in ['persona.adiantamentosavulsos','persona.trabalhadores']:
            #     continue

            _idx += 1
            self._log.mensagem(f"Verificando integridade {entidade}, {_idx} de {len(entidades_integracao)}.")

            # Carregar dados paginados para integrar
            service = self._injector.service_for(entidade, False)

            _count = 0
            current_after = None
            fields = self._fields_to_load(service._dto_class)
            filters = self._filtro_particionamento_de(entidade)
            search_query = None
            _integrity_fields = self.integrity_fields(service._dto_class)
            _dados_locais = []

            self._log.mensagem(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Extraindo dados para comparação.")
            while True:

                _data = service.list(
                    current_after,
                    TAMANHO_PAGINA,
                    fields,
                    None,
                    filters,
                    search_query=search_query,
                )

                _count = _count + len(_data)

                if len(_data)==0:
                    break

                self._log.mensagem(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {_count} registros...")

                # Aponta a leitura para a próxima página
                _last = _data[-1]
                current_after = getattr(_last, _last.pk_field)

                # Convertendo para o formato de dicionário (permitindo omitir campos do DTO) e add tenant
                _cp_fields = copy.deepcopy(_integrity_fields)
                while _data:
                    dto = _data.pop(0)
                    _dados_locais.append(self.converte_dados_para_hash(dto, _cp_fields))


            _dados_locais = {
                'registros' : _count,
                'campos': {
                    "_": ",".join(sorted(_integrity_fields['root'])),
                },
                'dados': _dados_locais
            }

            self._log.mensagem(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Consultando dados da api.")


            # captura os dados de integridade da entidade
            _acao = entidade.split('.')[1]
            _dados = []
            _ultimo_id = None
            _count = 0
            while True:
                _dados_remotos = self.consultar_integridade_de(_acao, filters, _ultimo_id, detalhar_diferencas)

                _count = _count + len(_dados_remotos['dados'])

                if len(_dados_remotos['dados']) == 0:
                    break

                self._log.mensagem(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {_count} registros...")

                _dados = _dados + copy.copy(_dados_remotos['dados'])
                _ultimo_id = _dados[-1]['id']

            _dados_remotos['dados'] = _dados
            _dados_remotos['registros'] = _count

            self._log.mensagem(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Comparando dados.")

            # Compara os dados e obtem o que se deve fazer
            para_criar, para_atualizar, para_apagar, _diff = self.comparar_dados(_dados_locais, _dados_remotos)

            if para_criar:
                #print("\033[93mPara criar -> {len(para_criar)}\033[0m")
                print(f"\r\n\033[93mPara criar -> {len(para_criar)}\033[0m\r\n")
                if corrigir_auto:
                    print(f"\r\nCriando dados em {entidade}.\r\n")
                    self._enviar_dados(para_criar, _acao)

            if para_atualizar:
                print(f"\r\n\033[93mPara atualizar -> {len(para_atualizar)}\033[0m\r\n")
                if _diff:
                    _i : int = 0
                    for _chave, _valor in _diff.items():
                        _i  += 1
                        print(f"\r\n{_chave}<=>{_valor}\r\n")
                        self._trace_check(f"trace/integridade_{_acao}_{_i}_LOCAL.txt", _chave)
                        self._trace_check(f"trace/integridade_{_acao}_{_i}_REMOTE.txt", _valor)
                        #_du.save_to_file(f"trace/integridade_{_acao}_UPDATE.json", json_dumps(para_atualizar) )
                if corrigir_auto:
                    print(f"\r\nAtualizando dados em {entidade}.\r\n")
                    self._enviar_dados(para_atualizar, _acao)

            if para_apagar:
                print(f"\r\n\033[93mPara apagar -> {len(para_apagar)}\033[0m\r\n")
                if corrigir_auto:
                    print(f"\r\nRemovendo dados em {entidade}.\r\n")
                    self._apagar_dados(para_apagar, _acao)

            if not _diferencas:
                _diferencas = para_criar or para_atualizar or para_apagar

            if parar_caso_diferencas and (para_criar or para_atualizar or para_apagar) and not corrigir_auto:
                break

        if _diferencas:
            print("\033[93mOcorreram diferenças na checagem da integridade, verifique a saída.\033[0m")

        if not _diferencas:
            print("\033[92mVerificação finalizada sem diferenças!\033[0m")
