import sys
from typing import List
import  argparse
from argparse import ArgumentError
import traceback

from nsj_integracao_api_client.infra.injector_factory import InjectorFactory

from nsj_integracao_api_client.service.integrador import IntegradorService, Environment


class ClientConsole:

    _modo_interativo : bool

    def __init__(self):
        self._modo_interativo = False

        self.parser = argparse.ArgumentParser(description="Cliente Console", exit_on_error=False)
        #parser = argparse.ArgumentParser(description="Cliente Console", add_help=False, epilog="...", exit_on_error=False)
        self.parser.add_argument("-e", "--entidades", help="Lista de entidades separadas por vírgulas")
        self.parser.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")
        self.parser.add_argument("-env", "--env", help="Se ambiente de DEV, QA, PROD", choices=[e for e in Environment], type=lambda x: Environment[x.upper()], default=Environment.PROD)
        self.parser.add_argument("-ft", "--forca_tenant", help="Permite executar o comando para um tenant diferente do instalado", type=int, default=None)

        self.subparsers = self.parser.add_subparsers(dest="command")
        # Subcomando padrão
        self.parser_recarga = self.subparsers.add_parser("integrar", help="Executa a integracao de dados enfileirados")
        self.parser_recarga.add_argument("-e", "--entidades", help="Lista de entidades separadas por vírgulas")
        self.parser_recarga.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")
        self.parser_recarga.add_argument("-env", "--env", help="Se ambiente de DEV, QA, PROD", choices=[e for e in Environment], type=lambda x: Environment[x.upper()], default=Environment.PROD)
        self.parser_recarga.add_argument("-ft", "--forca_tenant", help="Permite executar o comando para um tenant diferente do instalado", type=int, default=None)

        # Subcomando verificar integridade
        self.parser_integridade = self.subparsers.add_parser("verificar_integridade", help="Executa uma verificação de integridade, comparando os dados locais e remotos.")
        self.parser_integridade.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")
        self.parser_integridade.add_argument("-p", "--parar_caso_diferencas", help="Parar a checagem caso encontre diferenças", default=False, action="store_true")
        self.parser_integridade.add_argument("-d", "--detalhar", help="Detalhar as diferenças encontradas", default=False, action="store_true")
        self.parser_integridade.add_argument("-env", "--env", help="Se ambiente de DEV, QA, PROD", choices=[e for e in Environment], type=lambda x: Environment[x.upper()], default=Environment.PROD)
        self.parser_integridade.add_argument("-ft", "--forca_tenant", help="Permite executar o comando para um tenant diferente do instalado", type=int, default=None)

        # Grupo de argumentos para correção
        group_corrigir = self.parser_integridade.add_argument_group("correção", "Argumentos necessários para correção")
        group_corrigir.add_argument("-c", "--corrigir", help="Efetua a correção dos problemas encontrados", default=False, action="store_true")
        group_corrigir.add_argument("--tenant", help="ID do tenant", type=int)

        # Outros subcomandos...
        self.parser_instalar = self.subparsers.add_parser("instalar", help="Configura a integração para ser executada")
        self.parser_instalar.add_argument("chave_ativacao", help="Chave de ativação")
        self.parser_instalar.add_argument("-g", "--grupos", help="Lista de códigos de gruposempresariais separados por vírgulas")
        self.parser_instalar.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")
        self.parser_instalar.add_argument("-env", "--env", help="Se ambiente de DEV, QA, PROD", choices=[e for e in Environment], type=lambda x: Environment[x.upper()], default=Environment.PROD)

        self.parser_carga_inicial = self.subparsers.add_parser("carga_inicial", help="Executa a carga inicial")
        self.parser_carga_inicial.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")
        self.parser_carga_inicial.add_argument("-env", "--env", help="Se ambiente de DEV, QA, PROD", choices=[e for e in Environment], type=lambda x: Environment[x.upper()], default=Environment.PROD)
        self.parser_carga_inicial.add_argument("-ft", "--forca_tenant", help="Permite executar o comando para um tenant diferente do instalado", type=int, default=None)

        self.parser_add_grupos = self.subparsers.add_parser("ativar_grupos", help="executa a ativação de grupos empresariais na integração")
        self.parser_add_grupos.add_argument("-g", "--grupos", help="Lista de códigos de gruposempresariais separados por vírgulas")
        self.parser_add_grupos.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")

        self.parser_rem_grupos = self.subparsers.add_parser("desativar_grupos", help="executa a inativação de grupos empresariais na integração")
        self.parser_rem_grupos.add_argument("-g", "--grupos", help="Lista de códigos de gruposempresariais separados por vírgulas")
        self.parser_rem_grupos.add_argument("-t", "--traceback", help="Exibe o traceback em caso de erro", action="store_true")


    def mensagem(self, msg):
        print(msg)


    def get_integrador(self, injector, env : Environment,  forca_tenant: int = None) -> IntegradorService:

        return IntegradorService(injector, self, env, forca_tenant)


    def executar_instalacao(self, chave_ativacao: str, grupos: List[str], env: Environment):
        print("Executando processo de instalação da integração.")
        with InjectorFactory() as injector:
            self.get_integrador(injector, env).executar_instalacao(chave_ativacao, grupos)


    def ativar_grupos_empresariais(self, grupos: List[str], env: Environment):
        print(f"Ativando grupos empresariais: {grupos}")
        with InjectorFactory() as injector:
            self.get_integrador(injector, env).ativar_grupos_empresariais(grupos)


    def desativar_grupos_empresariais(self, grupos: List[str], env: Environment):
        print(f"Desativando grupos empresariais: {grupos}")
        with InjectorFactory() as injector:
            self.get_integrador(injector, env).desativar_grupos_empresariais(grupos)


    # Métodos associados aos comandos
    def executar_integracao(self, entidades: List[str], env: Environment, forca_tenant: int = None):
        with InjectorFactory() as injector:
            if entidades:
                print(f"Executando integração para as entidades: {entidades}")
                self.get_integrador(injector, env, forca_tenant).executar_integracao()
            else:
                print("Executando integração para todas as entidades.")
                self.get_integrador(injector, env, forca_tenant).executar_integracao()


    def executar_carga_inicial(self, env: Environment, forca_tenant: int = None):
        print("Executando carga inicial.")
        with InjectorFactory() as injector:
            self.get_integrador(injector, env, forca_tenant).executar_carga_inicial()


    def executar_verificacao_integridade(self, args):
        print("Executando verificação de integridade.")
        with InjectorFactory() as injector:
            self.get_integrador(injector, args.env, args.forca_tenant).executar_verificacao_integridade(
                args.parar_caso_diferencas,
                args.detalhar,
                args.corrigir,
                args.tenant
            )


    def modo_interativo(self):
        self._modo_interativo = True
        print("Modo interativo. Digite 'sair' para encerrar.")
        while True:
            try:
                entrada = input(">> ").strip()
                if entrada.lower() == 'sair':
                    print("Encerrando modo interativo.")
                    break
                if entrada:
                    args = self.parser.parse_args(entrada.split())
                    self.executar_comando(args)
            except SystemExit:
                continue
            except ArgumentError as e:
                print(f"\033[91mErro: {e}\033[0m")
            except Exception as e:
                print(f"\033[91mErro: {e}\033[0m")
                if '-t' in entrada.split():
                    traceback.print_exc()


    def executar_comando(self, args):
        if args.command == "integrar" or args.command is None:
            self.executar_integracao(entidades=args.entidades.split(",") if args.entidades else None, env=args.env, forca_tenant=args.forca_tenant)
        elif args.command == "instalar":
            self.executar_instalacao(args.chave_ativacao, args.grupos.split(",") if args.grupos else [], env=args.env)
        elif args.command == "ativar_grupos":
            self.ativar_grupos_empresariais(args.grupos.split(",") if args.grupos else None, env=args.env)
        elif args.command == "desativar_grupos":
            self.desativar_grupos_empresariais(args.grupos.split(",") if args.grupos else None, env=args.env)
        elif args.command == "carga_inicial":
            self.executar_carga_inicial(env=args.env, forca_tenant=args.forca_tenant)
        elif args.command == "verificar_integridade":
            if args.corrigir and not args.tenant:
                self.parser_integridade.error("tenant é obrigatório quando --corrigir é especificado")
            self.executar_verificacao_integridade(args)
        else:
            print('Comando desconhecido: "%s"', args.command)
            self.parser.print_help()


    # Configuração do parser de argumentos
    def main(self):
        args = self.parser.parse_args()

        if len(sys.argv) == 1:
            self.modo_interativo()
        else:
            self.executar_comando(args)


def run():
    client = ClientConsole()
    try:
        client.main()
    except ArgumentError:
        print(f"\033[91mErro: Argumentos inválidos: {sys.argv} \033[0m")
        exit(1)
    except Exception as e:
        print(f"\033[91mErro: {e}\033[0m")
        if '-t' in sys.argv:
            traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    run()
