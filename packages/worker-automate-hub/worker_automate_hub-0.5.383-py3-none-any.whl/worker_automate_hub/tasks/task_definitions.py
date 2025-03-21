from worker_automate_hub.tasks.jobs.fidc_exportacao_docs_portal_b2b import exportacao_docs_portal_b2b
from worker_automate_hub.tasks.jobs.fidc_gerar_nosso_numero import gerar_nosso_numero
from worker_automate_hub.tasks.jobs.coleta_dje_process import coleta_dje_start_update
from worker_automate_hub.tasks.jobs.coleta_dje_process import (
    coleta_dje_start_update,
)
from worker_automate_hub.tasks.jobs.conexao_rdp import conexao_rdp
from worker_automate_hub.tasks.jobs.fechar_conexao_rdp import fechar_conexao_rdp
from worker_automate_hub.tasks.jobs.cte_manual import cte_manual
from worker_automate_hub.tasks.jobs.geracao_aprovacao_pedidos import geracao_aprovacao_pedidos_171, geracao_aprovacao_pedidos_34
from worker_automate_hub.tasks.jobs.notas_faturamento_sap import notas_faturamento_sap
from worker_automate_hub.tasks.jobs.descartes import descartes
from worker_automate_hub.tasks.jobs.ecac_estadual_main import (
    ecac_estadual_main,
)
from worker_automate_hub.tasks.jobs.ecac_federal import ecac_federal
from worker_automate_hub.tasks.jobs.entrada_de_notas_39 import entrada_de_notas_39
from worker_automate_hub.tasks.jobs.entrada_de_notas_207 import entrada_de_notas_207
from worker_automate_hub.tasks.jobs.entrada_de_notas_500 import entrada_de_notas_500
from worker_automate_hub.tasks.jobs.entrada_de_notas_9 import entrada_de_notas_9
from worker_automate_hub.tasks.jobs.entrada_de_notas_7139 import entrada_de_notas_7139
from worker_automate_hub.tasks.jobs.entrada_de_notas_36 import entrada_de_notas_36
from worker_automate_hub.tasks.jobs.fidc_remessa_cobranca_cnab240 import remessa_cobranca_cnab240
from worker_automate_hub.tasks.jobs.entrada_de_notas_9 import (
    entrada_de_notas_9,
)
from worker_automate_hub.tasks.jobs.entrada_de_notas_15 import (
    entrada_de_notas_15,
)
from worker_automate_hub.tasks.jobs.entrada_de_notas_16 import (
    entrada_de_notas_16,
)
from worker_automate_hub.tasks.jobs.entrada_de_notas_32 import (
    entrada_de_notas_32,
)
from worker_automate_hub.tasks.jobs.entrada_de_notas_33 import (
    entrada_de_notas_33,
)
from worker_automate_hub.tasks.jobs.entrada_de_notas_34 import (
    entrada_de_notas_34,
)
from worker_automate_hub.tasks.jobs.entrada_de_notas_39 import (
    entrada_de_notas_39,
)
from worker_automate_hub.tasks.jobs.entrada_de_notas_207 import (
    entrada_de_notas_207,
)
from worker_automate_hub.tasks.jobs.entrada_de_notas_500 import (
    entrada_de_notas_500,
)
from worker_automate_hub.tasks.jobs.entrada_de_notas_505 import (
    entrada_de_notas_505,
)
from worker_automate_hub.tasks.jobs.entrada_de_notas_7139 import (
    entrada_de_notas_7139,
)
from worker_automate_hub.tasks.jobs.despesas_cte import (
    despesas_cte
)
from worker_automate_hub.tasks.jobs.exemplo_processo import exemplo_processo
from worker_automate_hub.tasks.jobs.fidc_retorno_cobranca import retorno_cobranca
from worker_automate_hub.tasks.jobs.login_emsys import login_emsys
from worker_automate_hub.tasks.jobs.login_emsys_versao_especifica import login_emsys_versao_especifica
from worker_automate_hub.tasks.jobs.playground import playground
from worker_automate_hub.tasks.jobs.transferencias import transferencias
from worker_automate_hub.tasks.jobs.sped_fiscal import sped_fiscal
from worker_automate_hub.tasks.jobs.devolucao_prazo_a_faturar import devolucao_prazo_a_faturar
from worker_automate_hub.tasks.jobs.devolucao_ctf import devolucao_ctf
from worker_automate_hub.tasks.jobs.integracao_contabil import integracao_contabil

task_definitions = {
    "5b295021-8df7-40a1-a45e-fe7109ae3902": exemplo_processo,
    "a0788650-de48-454f-acbf-3537ead2d8ed": login_emsys,
    "7d319f61-5e12-425c-86ed-678f0d9e14bd": login_emsys_versao_especifica,
    "abcfa1ba-d580-465a-aefb-c15ac4514407": descartes,
    "2c8ee738-7447-4517-aee7-ce2c9d25cea9": transferencias,
    "855f9e0f-e972-4f52-bc1a-60d1fc244e79": conexao_rdp,
    "d36b0c83-9cc3-465f-ac80-934099a0e661": fechar_conexao_rdp,
    "457b8f50-4944-4107-8e1b-80cb9aedbd5d": notas_faturamento_sap,
    "81785803-0594-4bba-9aa0-7f220c200296": coleta_dje_start_update,
    "3907c8d4-d05b-4d92-b19a-2c4e934f1d78": ecac_estadual_main,
    "81d2d6e6-e9eb-414d-a939-d220476d2bab": ecac_federal,
    "bbab8ff5-3eff-4867-a4af-239273d896ee": entrada_de_notas_32,
    "9e5a1c05-9336-4b2d-814e-4d0e9f0057e1": entrada_de_notas_33,
    "08a112db-7683-417b-9a87-14ad0e1548da": entrada_de_notas_34,
    "1e354c95-f4e4-4e12-aaf6-4ef836cc741b": entrada_de_notas_36,
    "bf763394-918b-47be-bb36-7cddc81a8174": entrada_de_notas_39,
    "dafc0407-da8f-43a1-b97a-d27f966e122a": entrada_de_notas_207,
    "e1051c43-3495-4ca7-91d5-527fea2b5f79": entrada_de_notas_500,
    "d168e770-0c33-4e20-a7f9-977bf15542f3": entrada_de_notas_505,
    "8e61a6c6-aeb4-456d-9aa5-b83ab8be297d": entrada_de_notas_9,
    "1a53d689-3cfb-4ec0-a02c-b249224b12ac": entrada_de_notas_15,
    "811e8934-8227-4686-a030-df057c054f75": entrada_de_notas_16,
    "e19d48a4-850b-413e-81c3-808158711ea0": entrada_de_notas_7139,
    "a4154a69-a223-48c2-8ff6-535cd29ff2d4": playground,
    "8d45aa6b-e24c-464d-afba-9a3147b3f506": gerar_nosso_numero, #Banco do Brasil FIDC
    "29338b70-4ae6-4560-8aef-5d0d7095a527": gerar_nosso_numero, #Banco do Brasil S.A
    "0aa423c1-fc7f-4b7e-a2b2-a1012c09deae": remessa_cobranca_cnab240,
    "276d0c41-0b7c-4446-ae0b-dd5d782917cc": sped_fiscal,
    "5d8a529e-b323-453f-82a3-980184a16b52": devolucao_prazo_a_faturar,
    "19a8f0b4-f5bf-49e8-8bc2-4aeceeae95ec": retorno_cobranca, #Retorno de cobrança
    "2db72062-4d11-4f91-b053-f4800f46c410": retorno_cobranca,  #Retorno de cobrança extraordinaria
    "abf3725f-d9d9-4f48-a31d-b22efb422e08": despesas_cte,
    "cf25b3f3-b9f1-45b5-a8d2-8c087024afdc": devolucao_ctf,
    "f241dbd6-f4a7-4afb-822a-46a628cfc916": exportacao_docs_portal_b2b,
    "326a746e-06ec-44c0-84bb-3a2dd866353e": cte_manual,
    "c7a53083-a364-45e2-a1f7-acd439fe8632": integracao_contabil,
    "e1696b6b-9de4-4f22-a977-b191a39506a9": integracao_contabil,
    "0745818a-4760-4cbe-b6bc-073519ac2104": integracao_contabil,
    "044a5713-82bd-4758-aec4-3a502d526568": integracao_contabil,
    "f76dae1d-799b-4b23-b83f-f688e6528f2c": integracao_contabil,
    "d94efc2a-8589-4fd3-b545-01a431ebe51f": integracao_contabil,
    "c8527e90-c65b-4d68-b4cf-25008b678957": geracao_aprovacao_pedidos_34,
    "260380b7-a3e5-4c23-ab69-b428ee552830": geracao_aprovacao_pedidos_171
}


async def is_uuid_in_tasks(uuid_to_check):
    """
    Verifica se um UUID está presente nas definições de tarefas.

    :param uuid_to_check: O UUID a ser verificado.
    :return: True se o UUID estiver presente, False caso contrário.
    """
    return uuid_to_check in task_definitions.keys()
