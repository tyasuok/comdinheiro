import os
import re
import io
import copy
import json
import urllib
import zipfile
import warnings
import dateutil
import datetime
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class instrument:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.url = "https://www.comdinheiro.com.br/Clientes/API/EndPoint001.php"
        self.querystring = {"code":"import_data"}
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        self.login = f"username={self.username}&password={self.password}"

    def _encode(self, string):
        # quick ref: %26 = &
        # %3F = ?
        # %3D = =
        # %2F = /
        string = string.replace(" ", "%2B").replace("/", "%2F")
        return string
        # return urllib.parse.quote_plus(string)

    def get_data(self, fucked_json=False, tab=0, debug=False):
        if debug:
            print("Payload:", self.payload)
            print("getting data")
        # self.payload = self._encode(self.payload)
        # self.payload = urllib.parse.quote_plus(self.payload)
        # print(self.payload)

        response = requests.request("POST", self.url, data=self.payload, headers=self.headers, params=self.querystring)
        self.response = response
        if debug:
            print("data got got")
            print(response)
        self.jsn = response.json()
        # with open("test.txt", "w") as f:
        #     json.dump(self.jsn, f)
        # print(response.text)
        # with open("hahahahaha.json", "w") as f:
        #     json.dump(response.json(), f)
        self.make_df(fucked_json, tab)

    def make_df(self, fucked_json=1, tab=0):
        """
        fucked 1 = dentro da linha tem uma lista com dicionários
        fucked 2 = dentro da linha tem um dicionário
        """
        if fucked_json == 1:
            # corrige formato zuado do comdinheiro pra json
            # isso ocorre pra data_ini != data_fim no historico de fundos
            dfs_list = []

            for i in copy.deepcopy(self.jsn["resposta"][f"tab-p{tab}"]["linha"]):
                data = i.pop("data")
                temp_df = pd.DataFrame(i)
                temp_df["data"] = data
                dfs_list.append(temp_df)

            self.df = pd.concat(dfs_list)

        elif fucked_json == 2:
            cpy = copy.deepcopy(self.jsn["resposta"][f"tab-p{tab}"]["linha"])
            data = cpy.pop("data")
            self.df = pd.DataFrame(cpy)
            self.df["data"] = data

        elif type(self.jsn["resposta"][f"tab-p{tab}"]["linha"]) == dict:
            self.df = pd.DataFrame(self.jsn["resposta"][f"tab-p{tab}"]).transpose().reset_index(drop=True)

        elif len(self.jsn["resposta"][f"tab-p{tab}"]["linha"]) > 0:
            self.df = pd.DataFrame(self.jsn["resposta"][f"tab-p{tab}"]["linha"])

        else:
            print("AAAAAAAAAAAAAAAAAAHHHHHHHH PAYLOAD:", self.payload)

    def export(self, filename):
        self.df.to_csv(filename)
    
    def contains(self, column, word, inplace=False):
        word = re.compile(word, re.I)
        if inplace:
            self.df = self.df[self.df[column].str.contains(word)]

        return self.df[self.df[column].str.contains(word)]

class fund_screener(instrument):
    def __init__(self, username, password, variaveis, filtro, data_rr, data_cart, salve="", overwrite=0, cotas=7,  periodos=0):
        """
        cotas: 7 é todas, 2 é não cotas
        """
        # data_rr, último dia do mês q vc quer
        # data_cart, primeiro dia? do mês anterior, isso aqui vira só mês/ano então tnt faz, acho
        # formato=dd/mm/yyyy
        super().__init__(username, password)

# nome_gestor+like+Absolute+or%B9nome_gestor+like+Absoluto+or%B9nome_gestor+like+Ace%26Capital+or%B9nome_gestor+like+Adam+or+nome_gestor+like+Alaska+or%B9nome_gestor+like+Apex+or%B9nome_gestor+like+AZ%26Quest+or%B9nome_gestor+like+Bahia+or%B9nome_gestor+like+blueline+or%B9nome_gestor+like+Bogari+or+nome_gestor+like+BC+or+nome_gestor+like+Canvas+or%B9nome_gestor+like+Capstone+or%B9nome_gestor+like+Constancia+or%B9nome_gestor+like+Constellation+or%B9nome_gestor+like+Dynamo+or%B9nome_gestor+like+Equitas+or%B9cnpj_gestor+like+18.511.433~0001%BD77+or%B9cnpj_gestor+like+33.576.954~0001%BD04+or%B9cnpj_gestor+like+30.701.673~0001%BD30+or%B9nome_gestor+like+Gavea+or%B9nome_gestor+like+Genoa+or%B9nome_gestor+like+Giant%26Steps+or%B9nome_gestor+like+Zeitgeist+or%B9nome_gestor+like+Ibiuna+or%B9nome_gestor+like+Indie+or%B9nome_gestor+like+JGP+or%B9nome_gestor+like+Kadima+or%B9nome_gestor+like+Kapitalo+or%B9nome_gestor+like+Kinea+or%B9nome_gestor+like+Leblon+or%B9nome_gestor+like+Legacy+or%B9nome_gestor+like+Maua+or%B9nome_gestor+like+Moat+or%B9nome_gestor+like+MZK+or%B9nome_gestor+like+Navi+or%B9nome_gestor+like+Novus+or%B9nome_gestor+like+Nucleo+or%B9nome_gestor+like+Occam+or%B9nome_gestor+like+Oceana+or%B9nome_gestor+like+Pandhora+or%B9cnpj_gestor+like+27.957.477~0001%BD16+or%B9nome_gestor+like+SPX+or%B9nome_gestor+like+Squadra+or%B9nome_gestor+like+Tork+or%B9nome_gestor+like+Truxt+or%B9nome_gestor+like+Velt+or%B9cnpj_gestor+like+19.749.539~0001%BD76+or%B9nome_gestor+like+Vinland


        # maybe do the variables the old way
        encod = urllib.parse.quote_plus((f"?&relat=&data_rr={data_rr}&data_cart={data_cart}&"
        f"variaveis={urllib.parse.quote_plus(variaveis.replace(' ', '+'), safe='~')}"
        f"&agrupar=&gr_classe=FI&cl_cvm=todos&cl_anb=todos&admin=&gestor=&situacao=4"
        f"&cotas={cotas}&quali=7&exclu=7&forma=3&largura=960&truncar=200&casas=2&salve={salve}"
        f"&filtro={urllib.parse.quote_plus(filtro.replace('/', '~'), safe='~').replace('-', '%BD')}"
        f"&join=inner&overwrite={overwrite}&minha_variavel=&transpor=0&salve_obs=&relat_alias_automatico=cmd_alias_01&flag_tab_carteira=0"
        f"&periodos={periodos}&periodicidade=mensal&formato_data=1"))

        # dont encode the format
        self.payload = (self.login +
        "&URL=FundScreener001.php" +
        encod +
        "&format=json2")

    def new_payload(self, variaveis, filtro, data_rr):
        self.payload = (self.login +
        "&URL=FundScreener001.php%3F"
        "%26relat%3D%26data_rr%3D15%2F09%2F2020%26data_cart%3D01%2F08%2F2020"
        f"%26variaveis%3D{variaveis}"
        "%26agrupar%3D"
        "%26gr_classe%3Dtodos"
        "%26cl_cvm%3Dtodos"
        "%26cl_anb%3Dtodos"
        "%26admin%3D"
        "%26gestor%3D"
        "%26situacao%3D4"
        "%26cotas%3D7"
        "%26quali%3D7"
        "%26exclu%3D7"
        "%26forma%3D3"
        "%26largura%3D960"
        "%26truncar%3D200"
        "%26casas%3D2"
        "%26salve%3D"
        f"%26filtro%3D{filtro}"
        "%26join%3Dinner"
        "%26overwrite%3D0"
        "%26minha_variavel%3D"
        "%26transpor%3D0"
        "%26salve_obs%3D"
        "%26relat_alias_automatico%3Dcmd_alias_01"
        "%26flag_tab_carteira%3D0"
        "%26periodos%3D0"
        "%26periodicidade%3Dmensal"
        "%26formato_data%3D1&format=json2")

class historico_fundos(instrument):
    def __init__(self, username, password, cnpjs, variaveis, data_ini, data_fim, periodicidade="diaria", tabela="v", ordem_data="asc"):
        """
        tabela: v/h
        ordem_data: asc/desc
        periodicidade: diaria/mes
        """
        # formato data ddmmyyyy
        super().__init__(username, password)

        self.tabela = tabela
        self.payload = (self.login + 
            "&URL=HistoricoIndicadoresFundos001.php"
            f"%3Fcnpjs%3D{urllib.parse.quote_plus(cnpjs.replace(' ', '+').replace('/', '~'), safe='~')}"
            f"%26data_ini%3D{data_ini}%26data_fim%3D{data_fim}" +\
            urllib.parse.quote_plus(f"&indicadores={variaveis.replace(' ', '+')}", safe="~") +\
            f"%26op01%3Dtabela_{tabela}"
            f"%26num_casas%3D2%26enviar_email%3D0%26periodicidade%3D{periodicidade}%26cabecalho_excel%3Dmodo2%26transpor%3D0"
            f"%26asc_desc%3D{ordem_data}%26tipo_grafico%3Dlinha%26relat_alias_automatico%3Dcmd_alias_01%26"
            "&format=json2")

    def make_df(self, fucked_json=1, tab=0):
        if self.tabela == "h":
            self.df = pd.DataFrame().from_records(self.jsn["resposta"]["tab-p0"]["linha"])  
        else: # tabela == "v"
            super().make_df(fucked_json, tab)

class risk_corr(instrument):
    def __init__(self, username, password, tickers, data_ini, data_fim, periodicidade="diaria", matriz=0):
        """
        data_ini/data_fim: ddmmyyyy
        matriz: 0 - inteira; 1 - metade inferior; 2-metade superior
        """
        super().__init__(username, password)

        self.payload = (self.login + 
            "&URL=Risco001.php"
            f"%3Fticker%3D{urllib.parse.quote_plus(tickers.replace(' ', '+').replace('/', '~'), safe='~')}"
            f"%26data_ini%3D{data_ini}%26data_fim%3D{data_fim}"
            "%26retorno%3Ddiscreto%26num_casas%3D5%26design%3D2%26maxX%3D%26minX%3D%26maxY%3D%26minY%3D%26risco_grafico%3Danualizado%26opc_rr%3D%26desvpad_amostral%3D0%26exportar%3D%26retorno_periodo%3Danualizado%26check_tracking_error%3D0%26benchmark%3DCDI%26check_grafico_tracking%3D0%26moeda%3D"
            "%26matriz_exibir%3D{matriz}%26cabecalho_excel%3Dmodo2%26descricao%3D%26&format=json2")

class abrir_carteira2(instrument):
    def __init__(self, username, password):#, cnpjs, variaveis, data_ini, data_fim, periodicidade="diaria", tabela="v", ordem_data="asc"):
        """
        tabela: v/h
        ordem_data: asc/desc
        """
        # formato data ddmmyyyy
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
    def __init__(self, username, password, cnpjs, data_ini, data_fim):
        """
        data_ini/data_fim: ddmmyyyy
        """
        if type(data_ini) == datetime.date:
            data_ini = data_ini.strftime("%d%m%Y")
        if type(data_fim) == datetime.date:
            data_fim = data_fim.strftime("%d%m%Y")

        super().__init__(username, password)
        self.payload = (self.login +
            "&URL=HistoricoCotacao002.php"
            f"%3F%26x%3D{urllib.parse.quote_plus(cnpjs.replace(' ', '+').replace('/', '~'), safe='~')}%26"
            f"data_ini%3D{data_ini}%26data_fim%3D{data_fim}"
            "%26pagina%3D1%26d%3DMOEDA_ORIGINAL%26g%3D0%26m%3D0%26info_desejada%3Dnumero_indice%26retorno%3Ddiscreto%26tipo_data%3Ddu_br%26tipo_ajuste%3Dtodosajustes%26num_casas%3D2%26enviar_email%3D0%26ordem_legenda%3D1%26cabecalho_excel%3Dmodo1%26classes_ativos%3D9ur54ut49vj%26ordem_data%3D1%26rent_acum%3Drent_acum%26minY%3D%26maxY%3D%26deltaY%3D%26preco_nd_ant%3D0%26base_num_indice%3D100%26flag_num_indice%3D0%26eixo_x%3DData%26startX%3D0%26max_list_size%3D20%26line_width%3D2%26titulo_grafico%3D%26legenda_eixoy%3D%26tipo_grafico%3Dline&format=json2"
        )

    def get_data(self, **kwargs):
        super().get_data(**kwargs)
        self.df.index = self.df["data"]
        self.df = self.df.drop("data", axis=1)

class make_instrument(instrument):
    def __init__(self, username, password, url):
        super().__init__(username, password)
        self.prim_url = url
        self._params = None
        self._get_payload()

    def _get_payload(self):
        self.prim_url = re.sub("https?://|www|\.comdinheiro\.com\.br/", "", self.prim_url)
        self.payload = (self.login +
                        "&URL=" + urllib.parse.quote_plus(self.prim_url) +
                        "&format=json2"
                       )

    def get_params(self):
        if self._params is None:
            self._params = {i: j for i, j in zip(re.findall("&(.*?)=", self.prim_url),
                                                 re.findall("=(.*?)(?=&|$)", self.prim_url))}
        return self._params

    def set_params(self, params: dict):
        """
        changes the default parameters used when passing the primitive url
        params: dictionary containing key value pairs to set the parameters
        """
        # set self._params if None
        if self._params is None:
            self.get_params()

        # check if passed dict contains all params
        if len(set(self._params).intersection(params)) != len(self._params):
            print("Must pass dictionary containing all possible params\n"+
                  "(tip: use the dict returned by self.get_params())"
            )
            return 1
        else:
            # set params
            tmp = self.prim_url
            for key, value in params.items():
                tmp = re.sub(f"({key}=)(.*?)(&|$)", fr"\g<1>{value}\g<3>", tmp)

            # update the payload based on the new prim_url
            self.prim_utl = tmp
            self._get_payload()

def repl_num(df, col):
    # só é útil pra verificar isso da coluna ser string com ponto pra indicador de milhar
    if df[col].str.contains(".", regex=False).any():
        raise Exception("A string tem um ponto . isso vai zuar na hora de converter, provavelmente é por conta do separador de milhar")
    else:
        df[col] = df[col].str.replace(",", ".").astype(float)

def tracking_error(df, ibov, ddof=0):
    # expects the ibov column to be named "ibov"
    return df.pct_change().iloc[1:].sub(ibov.pct_change().iloc[1:]["ibov"], axis=0).std(ddof=ddof)

def drawdown(path, plot_name: list=[False, None], ibov=None, check_dates=False, **kwargs):
    """
    IMPORTANTE: o df e o ibov tem que ter os mesmos índices para realizar o .subtract corretamente
    path: pode ser ou um dataframe ou o path pro excel/csv
    plot_name: é uma lista [boolean, nome da coluna] o boolean é pra ter plot ou não
    ibov: passa um dataframe do ibov (se o ibov for uma coluna do df faz df[["ibov"]])
    check_dates: only used if ibov not None, makes sure ibov and each series start at the same date
    """
    df = path
    if type(path) == str:
        extension = os.path.splitext(path)[1]
        # maybe other cases other than csv and excel
        if extension == ".csv":
            df = pd.read_csv(path, index_col=0, parse_dates=True, **kwargs)
        else:
            df = pd.read_excel(path, index_col=0, **kwargs)

    df = df.pct_change().iloc[1:]
    # o df.sub() pro ibov vai aqui
    df.columns = df.columns.str.strip().str.replace("\n", "")

    if ibov is not None:
        if check_dates:
            cumulative = (df.apply(lambda x: 
                                      (x + 1).cumprod().sub(
                                      (ibov.loc[x.dropna().index[0]:, "ibov"].pct_change().iloc[1:] + 1)
                                      .cumprod(), axis=0
                                      )
                                  )
                         ) + 1
            tmp_cum = (df + 1).cumprod()
            tmp_ib = df.apply(lambda x: (ibov.loc[x.dropna().index[0]:, "ibov"].pct_change().iloc[1:] + 1).cumprod())
        else:
            cumulative = (df + 1).cumprod().sub((ibov.pct_change().iloc[1:]["ibov"] + 1).cumprod(), axis=0)
    else:
        if check_dates:
            warnings.warn("check dates doesn't do anything if ibov is None")
        cumulative = (df + 1).cumprod()

    peaks = cumulative.cummax()
    drawdown = (cumulative - peaks)/peaks

    max_drawdowns = pd.DataFrame()
    max_drawdowns["min"] = drawdown.min()
    max_drawdowns["idxmin"] = drawdown.idxmin()

    if plot_name[0]:
        if plot_name[1] is None:
            print(df.columns)
            plot_name[1]= input("Nome: ")
        fig, ax = plt.subplots()
        ax.plot(cumulative[plot_name[1]], label="Cumulative Returns")
        ax.plot(peaks[plot_name[1]], label="Peaks")

        # esse aqui plota o cumulativo do ibov teoricamente, refazer
        if ibov is not None:
            # ax.plot((1 + woj[all_dfs[plot_name[1]].dropna().iloc[0,].name:].pct_change()).cumprod(), label="ibov")
            ax.plot(tmp_ib[plot_name[1]], label="ibov")
            ax.plot(tmp_cum[plot_name[1]], label=plot_name[1] + "_no_sub")

        ax.scatter(drawdown[plot_name[1]].idxmin(),
                cumulative.loc[drawdown[plot_name[1]].idxmin()][plot_name[1]],
                s=100,
                marker="o",
                color="red",
                label="Max Drawdown",
                zorder=4
                )

        fig.figsize = (16, 9)
        ax.legend(bbox_to_anchor=(.5, -.15))
        fig.tight_layout()
        plt.show()

    return {"cumulative": cumulative,
            "peaks": peaks,
            "drawdown": drawdown,
            "max_drawdowns": max_drawdowns
    }

def beta(df, ibov_col="ibov", **kwargs):
    # verificar se não começa com na, se pá iloc da primeira linha e ver se tem algum na (.isna)
    # se possível usar o sklearn.LinearRegression msm, vira e mexe aqui dá algum prob
    if len(kwargs) > 0:
        df = df.loc[df.index[-1] + dateutil.relativedelta.relativedelta(**kwargs):, :]
    temp_df = df.apply(lambda x: x[x.dropna().index[0]:].cov(df[ibov_col][x.dropna().index[0]:], ddof=0) / df[ibov_col][x.dropna().index[0]:].var(ddof=0)\
                              if np.isnan(x.iloc[0]) else\
                                  x.cov(df[ibov_col], ddof=0) / df[ibov_col].var(ddof=0), axis=0)
    return temp_df.rename(lambda x: x+f"* {df[x].dropna().index[0].strftime('%Y-%m-%d')}" if np.isnan(df[x].iloc[0]) else x)

def fix_name(s):
    mm = re.compile("(:?Fundos? de Investimentos?|FI) Multimercados?", re.I)
    ac = re.compile("(:?Fundos? (:?de|em) Invest[ ]?iment[ ]?os?|FI) (:?de|em) A[CcÇç][OoÕõ]es?", re.I)
    ie = re.compile("Investimento (:?no|do) Exterior", re.I)
    fic = re.compile("(:?Fundos? de Invest[ ]?iment[ ]?os?|FI) em Cot[ ]?as", re.I)
    fiq = re.compile("(:?Fundos? de Investimentos?|FI) em Quotas", re.I)
    rf = re.compile("Renda Fixa", re.I)
    
    fi = re.compile("Fundos? de Investimento", re.I)
    # ac = re.compile("Fundo De Investimento Multimercados?", re.I)

    de = re.compile("(FI)(?P<cota>[CQ])( DE FI)(?P<tipo>[MA])?", re.I)

    s = re.sub(mm, "FIM", s)
    s = re.sub(ac, "FIA", s)
    s = re.sub(ie, "IE", s)
    s = re.sub(fic, "FIC", s)
    s = re.sub(fiq, "FIQ", s)
    s = re.sub(rf, "RF", s)
    s = re.sub(fi, "FI", s)
    s = re.sub(de, "FI\g<cota>FI\g<tipo>", s)
    return s

def valores_cotas(user, password, cnpjs, desde, dataanalise):
    variaveis = "valor_cota"
    hf = historico_fundos(user, password, cnpjs,
                             variaveis=variaveis,
                             data_ini=desde.strftime("%d%m%Y"),
                             data_fim=dataanalise.strftime("%d%m%Y"),
                             periodicidade="diaria",
                             tabela="h"
                             )
    hf.get_data()

    hf.df.index = pd.to_datetime(hf.df["data"], format="%d/%m/%Y")
    hf.df = hf.df.drop("data", axis=1)
    hf.df.columns = hf.df.columns.str[13:28]

    hf.df = hf.df.applymap(lambda x: np.nan if x == [] else x)
    hf.df = hf.df.apply(lambda x: x.str.replace(",", ".").astype(float)\
                            if x.dtype != "float64" else x)
    return hf.df

def indicadores(user, password, indicador, desde, dataanalise):
    """
    ANBIMA_IHFA
    IBOV
    CDI
    """
    hm = historico_multiplo(user, password, indicador,
                               desde.strftime("%d%m%Y"),
                               (dataanalise + dateutil.relativedelta.relativedelta(days=-1)).strftime("%d%m%Y")
        )
    hm.get_data(tab=1)
    hm.df.index = pd.to_datetime(hm.df.index, format="%d/%m/%Y")

    hm.df = hm.df.applymap(lambda x: np.nan if x == [] else x)
    hm.df = hm.df.applymap(lambda x: np.nan if x == "nd" else x)
    hm.df = hm.df.apply(lambda x: x.str.replace(",", ".").astype(float)\
                            if x.dtype != "float64" else x)
    return hm.df

if __name__=="__main__":
    pass
