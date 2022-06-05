import os
import re
import io
import copy
import json
import urllib
import zipfile
import datetime
import requests
import pandas as pd
from typing import Union

class instrument:
    """
    parent class for any endpoint offered by comdinheiro
    """
    def __init__(self, username: str, password: str):
        """
        username: comdinheiro username
        password: comdinheiro password
        """
        self.username = username
        self.password = password

        self.url = "https://www.comdinheiro.com.br/Clientes/API/EndPoint001.php"
        self.querystring = {"code":"import_data"}
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.login = f"username={self.username}&password={self.password}"

    def _encode(self, string):
        """
        string: string to encode
        only encodes spaces ( ) and forward slashes (/)
        currently unused
        """
        string = string.replace(" ", "%2B").replace("/", "%2F")
        return string

    def get_data(self, json_format=False, tab=0, debug: bool=False):
        """
        creates self.response (requests.Response) and self.jsn (decoded json object)
        tab: select which tab contains the wanted information
        debug: bool
        """
        if debug:
            print("Payload:", self.payload)
            print("getting data")

        response = requests.request("POST", self.url, data=self.payload, headers=self.headers, params=self.querystring)
        self.response = response

        if debug:
            print("data got got")
            print(response)

        self.jsn = response.json()
        self.make_df(json_format, tab)

    def make_df(self, json_format=1, tab: int=0):
        """
        json_format 1 = linha contains a list of dictionaries
        json_format 2 = linha contains a dictionary
        """
        if json_format == 1:
            # corrige formato zuado do comdinheiro pra json
            # isso ocorre pra data_ini != data_fim no historico de fundos
            dfs_list = []

            for i in copy.deepcopy(self.jsn["resposta"][f"tab-p{tab}"]["linha"]):
                data = i.pop("data")
                temp_df = pd.DataFrame(i)
                temp_df["data"] = data
                dfs_list.append(temp_df)

            self.df = pd.concat(dfs_list)

        elif json_format == 2:
            cpy = copy.deepcopy(self.jsn["resposta"][f"tab-p{tab}"]["linha"])
            data = cpy.pop("data")
            self.df = pd.DataFrame(cpy)
            self.df["data"] = data

        elif type(self.jsn["resposta"][f"tab-p{tab}"]["linha"]) == dict:
            self.df = pd.DataFrame(self.jsn["resposta"][f"tab-p{tab}"]).transpose().reset_index(drop=True)

        elif len(self.jsn["resposta"][f"tab-p{tab}"]["linha"]) > 0:
            self.df = pd.DataFrame(self.jsn["resposta"][f"tab-p{tab}"]["linha"])

        else:
            raise(f"Error, couldn't convert to DataFrame\nPayload: {self.payload}")

    def _date_handler(self, dt: Union[datetime.date, datetime.datetime]) -> str:
        return dt.strftime(self.fmt)

class make_instrument(instrument):
    """
    generic instrument builder based on a provided url
    may be used for uncreated instrument classes
    may be used in place of existing instruments in order to not specify each parameter
    """
    def __init__(self, username: str, password: str, url: str):
        """
        url: full comdinheiro query url
        """
        super().__init__(username, password)
        self.prim_url = url
        self._arguments = None
        self._get_payload()

    def _get_payload(self):
        """
        generates payload
        """
        self.prim_url = re.sub("https?://|www|\.comdinheiro\.com\.br/", "", self.prim_url)
        self.payload = (self.login +
                        "&URL=" + urllib.parse.quote_plus(self.prim_url) +
                        "&format=json2"
                       )

    def get_arguments(self) -> dict:
        """
        returns dictionary with the instrument parameters
        """
        if self._arguments is None:
            self._arguments = {i: j for i, j in zip(re.findall("&(.*?)=", self.prim_url),
                                                 re.findall("=(.*?)(?=&|$)", self.prim_url))}
        return self._arguments

    def set_arguments(self, arguments: dict):
        """
        changes the default parameters used when passing the primitive url
        arguments: dictionary containing key value pairs to set the parameters
        """
        # set self._arguments if None
        if self._arguments is None:
            self.get_arguments()

        # check if passed dict contains all params
        if len(set(self._arguments).intersection(arguments)) != len(self._arguments):
            print("Must pass dictionary containing all possible params\n"+
                  "(tip: use the dict returned by self.get_arguments())"
            )
            return 1
        else:
            # set params
            tmp = self.prim_url
            for key, value in arguments.items():
                tmp = re.sub(f"({key}=)(.*?)(&|$)", fr"\g<1>{value}\g<3>", tmp)

            # update the payload based on the new prim_url
            self.prim_utl = tmp
            self._get_payload()
            return 0


class fund_screener(instrument):
    def __init__(self, username, password, variaveis,
                 filtro, data_rr: Union[datetime.date, datetime.datetime],
                 data_cart: Union[datetime.date, datetime.datetime], salve="",
                 overwrite=0, cotas=7,  periodos=0):
        """
        cotas: 7 é todas, 2 é não cotas
        """
        # data_rr, último dia do mês q vc quer
        # data_cart, primeiro dia? do mês anterior, isso aqui vira só mês/ano então tnt faz, acho
        # formato=dd/mm/yyyy
        super().__init__(username, password)

        self.fmt = "%d/%m/%Y"
        encod = urllib.parse.quote_plus((f"?&relat=&data_rr={self._date_handler(data_rr)}"
        f"&data_cart={self._date_handler(data_cart)}&"
        f"variaveis={urllib.parse.quote_plus(variaveis.replace(' ', '+'), safe='~')}"
        f"&agrupar=&gr_classe=FI&cl_cvm=todos&cl_anb=todos&admin=&gestor=&situacao=4"
        f"&cotas={cotas}&quali=7&exclu=7&forma=3&largura=960&truncar=200&casas=2&salve={salve}"
        f"&filtro={urllib.parse.quote_plus(filtro.replace('/', '~'), safe='~').replace('-', '%BD')}"
        f"&join=inner&overwrite={overwrite}&minha_variavel=&transpor=0&salve_obs=&relat_alias_automatico=cmd_alias_01&flag_tab_carteira=0"
        f"&periodos={periodos}&periodicidade=mensal&formato_data=1"))

        self.payload = (self.login +
        "&URL=FundScreener001.php" +
        encod +
        "&format=json2")

class historico_fundos(instrument):
    def __init__(self, username, password,
                 cnpjs, variaveis, data_ini: Union[datetime.date, datetime.datetime],
                 data_fim: Union[datetime.date, datetime.datetime],
                 periodicidade="diaria", tabela="v", ordem_data="asc"):
        """
        tabela: v/h
        ordem_data: asc/desc
        periodicidade: diaria/mes
        """
        super().__init__(username, password)

        self.fmt = "%d%m%Y"

        self.tabela = tabela
        print(urllib.parse.quote_plus(cnpjs.replace(' ', '+').replace('/', '~'), safe='~'))
        self.payload = (self.login + 
            "&URL=HistoricoIndicadoresFundos001.php"
            f"%3Fcnpjs%3D{urllib.parse.quote_plus(cnpjs.replace(' ', '+').replace('/', '~'), safe='~')}"
            f"%26data_ini%3D{self._date_handler(data_ini)}"
            f"%26data_fim%3D{self._date_handler(data_fim)}" +\
            urllib.parse.quote_plus(f"&indicadores={variaveis.replace(' ', '+')}", safe="~") +\
            f"%26op01%3Dtabela_{tabela}"
            f"%26num_casas%3D2%26enviar_email%3D0%26periodicidade%3D{periodicidade}%26cabecalho_excel%3Dmodo2%26transpor%3D0"
            f"%26asc_desc%3D{ordem_data}%26tipo_grafico%3Dlinha%26relat_alias_automatico%3Dcmd_alias_01%26"
            "&format=json2")

    def make_df(self, json_format=1, tab=0):
        if self.tabela == "h":
            self.df = pd.DataFrame().from_records(self.jsn["resposta"][f"tab-p{tab}"]["linha"])  
        else: # tabela == "v"
            super().make_df(json_format, tab)

class risk_corr(instrument):
    def __init__(self, username, password,
                 tickers, data_ini: Union[datetime.date, datetime.datetime],
                 data_fim: Union[datetime.date, datetime.datetime], periodicidade="diaria",
                 matriz=0):
        """
        data_ini/data_fim: ddmmyyyy
        matriz: 0 - inteira; 1 - metade inferior; 2-metade superior
        """
        super().__init__(username, password)

        self.fmt = "%d%m%Y"
        self.payload = (self.login + 
            "&URL=Risco001.php"
            f"%3Fticker%3D{urllib.parse.quote_plus(tickers.replace(' ', '+').replace('/', '~'), safe='~')}"
            f"%26data_ini%3D{self._date_handler(data_ini)}%26data_fim%3D{self._date_handler(data_fim)}"
            "%26retorno%3Ddiscreto%26num_casas%3D5%26design%3D2%26maxX%3D%26minX%3D%26maxY%3D%26minY%3D%26risco_grafico%3Danualizado%26opc_rr%3D%26desvpad_amostral%3D0%26exportar%3D%26retorno_periodo%3Danualizado%26check_tracking_error%3D0%26benchmark%3DCDI%26check_grafico_tracking%3D0%26moeda%3D"
            "%26matriz_exibir%3D{matriz}%26cabecalho_excel%3Dmodo2%26descricao%3D%26&format=json2")

class abrir_carteira2(instrument):
    def __init__(self, username, password):
        super().__init__(username, password)
        self.payload = (self.login +
            "&URL=CarteiraFundo002-25213366000170-20210201-setor-1-default-8-1---1-0-1-coluna-10%26format%3Djson2")

class quotistas1(instrument):
    def __init__(self, username, password, cnpj):
        """
        """
        super().__init__(username, password)
        self.payload = (self.login +
            f"&URL=FundoQuotistas001-{cnpj.replace('-', '').replace('.', '').replace('/', '')}-20210801-1-2-default&format=json2"
        )

class abrir_carteira9(instrument):
    def __init__(self, username, password, cnpj):
        """
        """
        super().__init__(username, password)
        self.payload = (self.login +
            f"&URL=CarteiraFundo009-{cnpj.replace('-', '').replace('.', '').replace('/', '')}-20210901-5-0-1-nunca-nunca-sempre&format=json2"
        )

class historico_multiplo(instrument):
    def __init__(self, username, password, cnpjs,
                 data_ini: Union[datetime.date, datetime.datetime],
                 data_fim: Union[datetime.date, datetime.datetime]):
        # if type(data_ini) == datetime.date:
        #     data_ini = data_ini.strftime("%d%m%Y")
        # if type(data_fim) == datetime.date:
        #     data_fim = data_fim.strftime("%d%m%Y")

        super().__init__(username, password)

        self.fmt = "%d%m%Y"
        self.payload = (self.login +
            "&URL=HistoricoCotacao002.php"
            f"%3F%26x%3D{urllib.parse.quote_plus(cnpjs.replace(' ', '+').replace('/', '~'), safe='~')}%26"
            f"data_ini%3D{self._date_handler(data_ini)}"
            f"%26data_fim%3D{self._date_handler(data_fim)}"
            "%26pagina%3D1%26d%3DMOEDA_ORIGINAL%26g%3D0%26m%3D0%26info_desejada%3Dnumero_indice%26retorno%3Ddiscreto%26tipo_data%3Ddu_br%26tipo_ajuste%3Dtodosajustes%26num_casas%3D2%26enviar_email%3D0%26ordem_legenda%3D1%26cabecalho_excel%3Dmodo1%26classes_ativos%3D9ur54ut49vj%26ordem_data%3D1%26rent_acum%3Drent_acum%26minY%3D%26maxY%3D%26deltaY%3D%26preco_nd_ant%3D0%26base_num_indice%3D100%26flag_num_indice%3D0%26eixo_x%3DData%26startX%3D0%26max_list_size%3D20%26line_width%3D2%26titulo_grafico%3D%26legenda_eixoy%3D%26tipo_grafico%3Dline&format=json2"
        )

    def get_data(self, **kwargs):
        super().get_data(**kwargs)
        self.df.index = self.df["data"]
        self.df = self.df.drop("data", axis=1)

if __name__=="__main__":
    pass
