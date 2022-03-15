from instruments import *
import os

url = "https://www.comdinheiro.com.br/HistoricoIndicadoresFundos001.php?&cnpjs=29726133000121+28581166000168&data_ini=16112021&data_fim=07032022&indicadores=patrimonio~cotistas+beta_48m+valor_total+captacao+resgate+valor_cota&op01=tabela_h&num_casas=2&enviar_email=0&periodicidade=diaria&cabecalho_excel=modo2&transpor=0&asc_desc=desc&tipo_grafico=linha&relat_alias_automatico=cmd_alias_01"
ins = make_instrument(os.environ["COMDINHEIRO_USER"], os.environ["COMDINHEIRO_PASSWORD"], url)

# obter os parametros utilizados na query string da consulta em forma de dicionário
params = ins.get_params()
print(params)

# após alterar os parâmetros para a consulta desejada, .set_params insere os novos valores
ins.set_params(params)

ins.get_data()
print(ins.df.head())
