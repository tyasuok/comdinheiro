# Comdinheiro API

Código para auxílio na interação com a api do comdinheiro

[Instalação](#instalação)

[Utilização](#utilização)

# Instalação

`pip install comdinheiro`

# Utilização
```python
from comdinheiro import *
url = "https://www.comdinheiro.com.br/HistoricoIndicadoresFundos001.php?&cnpjs=29726133000121+28581166000168&data_ini=16112021&data_fim=07032022&indicadores=patrimonio~cotistas+beta_48m+valor_total+captacao+resgate+valor_cota&op01=tabela_h&num_casas=2&enviar_email=0&periodicidade=diaria&cabecalho_excel=modo2&transpor=0&asc_desc=desc&tipo_grafico=linha&relat_alias_automatico=cmd_alias_01"
ins = make_instrument(usuario, senha, url)
ins.get_data()
print(ins.df.head())

```
|    | data       | patrimonio/cotistas29726133/000121kapitalo_k10_ficfi_mm   | beta48_meses29726133/000121kapitalo_k10_ficfi_mm   | valor_dos_ativos29726133/000121kapitalo_k10_ficfi_mm   | captacao_no_diar$29726133/000121kapitalo_k10_ficfi_mm   | resgate_no_diar$29726133/000121kapitalo_k10_ficfi_mm   | valor_da_cota29726133/000121kapitalo_k10_ficfi_mm   | patrimonio/cotistas28581166/000168vinland_macro_ficfi_mm   | beta48_meses28581166/000168vinland_macro_ficfi_mm   | valor_dos_ativos28581166/000168vinland_macro_ficfi_mm   | captacao_no_diar$28581166/000168vinland_macro_ficfi_mm   | resgate_no_diar$28581166/000168vinland_macro_ficfi_mm   | valor_da_cota28581166/000168vinland_macro_ficfi_mm   |
|---:|:-----------|:----------------------------------------------------------|:---------------------------------------------------|:-------------------------------------------------------|:--------------------------------------------------------|:-------------------------------------------------------|:----------------------------------------------------|:-----------------------------------------------------------|:----------------------------------------------------|:--------------------------------------------------------|:---------------------------------------------------------|:--------------------------------------------------------|:-----------------------------------------------------|
|  0 | 07/03/2022 | 314654,064463                                             | []                                                 | 1654596668,51                                          | 22533926,79                                             | 1016487,78                                             | 1,5555606                                           | 235930,815333                                              | []                                                  | 267947961,08                                            | 441772,22                                                | 134207,99                                               | 1,3683933                                            |
|  1 | 04/03/2022 | 311617,163185                                             | []                                                 | 1629380881,25                                          | 10951129,92                                             | 300846,77                                              | 1,5532464                                           | 236656,310492                                              | []                                                  | 266736243,47                                            | 1189300                                                  | 121449,97                                               | 1,3644215                                            |
|  2 | 03/03/2022 | 309298,024599                                             | []                                                 | 1633719325,84                                          | 9525157,75                                              | 30535139,18                                            | 1,5414114                                           | 237858,792813                                              | []                                                  | 267052516,4                                             | 64610,76                                                 | 10810                                                   | 1,367055                                             |
|  3 | 02/03/2022 | 314065,51323                                              | []                                                 | 1615898370,64                                          | 1387029,58                                              | 858397,74                                              | 1,5342904                                           | 239658,350155                                              | []                                                  | 265148872,81                                            | 1006239                                                  | 132682,58                                               | 1,3640137                                            |
|  4 | 25/02/2022 | 317297,11381                                              | []                                                 | 1626170136,95                                          | 14507714,4                                              | 341860,18                                              | 1,5430078                                           | 240792,535575                                              | []                                                  | 267264207,81                                            | 825205,93                                                | 330097,29                                               | 1,3725289                                            |

```python
# alterar parâmetros da consulta
arguments = ins.get_arguments()
print(arguments)
```
```yaml
{'asc_desc': 'desc',
 'cabecalho_excel': 'modo2',
 'cnpjs': '29726133000121+28581166000168',
 'data_fim': '07032022',
 'data_ini': '16112021',
 'enviar_email': '0',
 'indicadores': 'patrimonio~cotistas+beta_48m+valor_total+captacao+resgate+
valor_cota',
 'num_casas': '2',
 'op01': 'tabela_h',
 'periodicidade': 'diaria',
 'relat_alias_automatico': 'cmd_alias_01',
 'tipo_grafico': 'linha',
 'transpor': '0'}
```
```python
# alterando a data inicial para 01/01/2021
arguments["data_ini"] = "01112021"
ins.set_arguments(arguments) # informando à consulta os novos argumentos
ins.get_data() # realizando a consulta com os novos argumentos

# remover listas vazias (o formato devolvido pelo comdinheiro para valores nulos)
ins.df = ins.df.applymap(lambda x: np.nan if x == [] else x)
# trocar vírgulas por pontos e converter para float (vem como string)
ins.df[numeric_cols] = ins.df[numeric_cols].apply(lambda x: x.str.replace(",", ".").astype(float))
```
