from comdinheiro.instruments import *
from datetime import date
import os


hf = historico_fundos(os.environ["COMDINHEIRO_USER"], os.environ["COMDINHEIRO_PASSWORD"],
                      cnpjs="29.726.133/0001-21", variaveis="valor_cota quant_cotas",
                      data_ini=date(2021, 1, 1), data_fim=date(2021, 1, 31),
                      periodicidade="diaria", tabela="v", ordem_data="asc")
hf.get_data()
print(hf.df.head())
