import getpass
import warnings
import os
import re
import io
import uuid

import pyautogui
import pytesseract
from datetime import datetime, timedelta
from pywinauto.application import Application
from pypdf import PdfReader
from PIL import Image, ImageEnhance
from pywinauto.keyboard import send_keys
from pywinauto.mouse import double_click
import win32clipboard
from pywinauto_recorder.player import set_combobox
from rich.console import Console
from worker_automate_hub.api.ahead_service import save_xml_to_downloads
from worker_automate_hub.api.client import (
    get_config_by_name,
    get_status_nf_emsys,
    send_file,
)
from worker_automate_hub.models.dto.rpa_historico_request_dto import (
    RpaHistoricoStatusEnum,
    RpaRetornoProcessoDTO,
    RpaTagDTO,
    RpaTagEnum,
)
from worker_automate_hub.models.dto.rpa_processo_entrada_dto import (
    RpaProcessoEntradaDTO,
)
from worker_automate_hub.utils.logger import logger
from worker_automate_hub.utils.util import (
    e_ultimo_dia_util,
    delete_xml,
    ocr_warnings,
    ocr_by_class,
    nf_busca_nf_saida,
    pessoas_ativa_cliente_fornecedor,
    nf_devolucao_liquidar_cupom,
    gerenciador_nf_header,
    cadastro_pre_venda_header,
    incluir_registro,
    is_window_open,
    is_window_open_by_class,
    kill_all_emsys,
    login_emsys,
    ocr_title,
    select_documento_type,
    set_variable,
    type_text_into_field,
    worker_sleep,
    post_partner,
    get_text_display_window,
)

pyautogui.PAUSE = 0.5
pyautogui.FAILSAFE = False
console = Console()


async def devolucao_ctf(task: RpaProcessoEntradaDTO) -> RpaRetornoProcessoDTO:
    """
    Processo que relazia entrada de notas no ERP EMSys(Linx).

    """
    try:
        #DEFINIR CONSTANTE DEFAULT PARA O ASSETS 
        ASSETS_PATH = "assets"
        # Get config from BOF
        config = await get_config_by_name("login_emsys")
        try:
            aliquota_icms = await get_config_by_name("Aliquota_ICMS")
            conconfig_aliquota_icms = aliquota_icms.conConfiguracao.get("aliquotas")
        except Exception as e:
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Não foi possivel recuperar o valor da configuração de Aliquota, erro: {e}.",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )
        console.print(task)

        # Seta config entrada na var nota para melhor entendimento
        nota = task.configEntrada

        #Definindo Variaveis com Escopo global
        numero_cupom_fiscal = nota.get("numCupomNotaFiscal")
        cod_empresa = nota.get("codigoEmpresa")
        cod_cliente_correto = nota.get("codClienteCorreto")
        cod_cliente_incorreto = nota.get("codClienteIncorreto")
        steps = ""
        numero_nota_fiscal = ""
        valor_nota_fiscal = ""
        item_arla = False
        cidade_cliente = ""
        data_hoje = datetime.today().strftime('%d/%m/%Y')
        multiplicador_timeout = int(float(task.sistemas[0].timeout))
        set_variable("timeout_multiplicador", multiplicador_timeout)

        #VERIFICANDO ENTRADA 
        historico_id = task.historico_id
        if historico_id:
            console.print("Historico ID recuperado com sucesso...\n")
        else:
            console.print("Não foi possivel recuperar o histórico do ID, não sendo possivel enviar os arquivo gerados como retorno...\n")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno="Não foi possivel recuperar o histórico do ID, não sendo possivel enviar os arquivo gerados como retorno",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            ) 

        # Fecha a instancia do emsys - caso esteja aberta
        await kill_all_emsys()

        #Validar se é o ultimo dia 
        if await e_ultimo_dia_util():
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno="Não será possivel processar devido a regra - 'Não deve ser processado nenhuma devolução no último dia útil do mês vigente'",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
        )

        #Realizando o login
        app = Application(backend="win32").start("C:\\Rezende\\EMSys3\\EMSys3.exe")
        warnings.filterwarnings("ignore",category=UserWarning,message="32-bit application should be automated using 32-bit Python")
        console.print("\nEMSys iniciando...", style="bold green")
        return_login = await login_emsys(config.conConfiguracao, app, task)
        if return_login.sucesso == True:
            console.print("Processo de login realizado com sucesso... \n")
        else:
            logger.info(f"\nError Message: {return_login.retorno}")
            console.print(f"\nError Message: {return_login.retorno}", style="bold red")
            return return_login


        #HABILITAR CLIENTE E FORNECEDOR PARA COD INCORRETO
        console.print("Seguindo com o processo de habilitar Cliente e Fornecedor para andamento do processo.. \n")
        type_text_into_field("Pessoas", app["TFrmMenuPrincipal"]["Edit"], True, "50")
        pyautogui.press("enter")
        send_keys("{DOWN " + ("2") + "}")
        pyautogui.press("enter")
        
        await worker_sleep(2)
        console.print("Verificando se o cliente esta ativo como Cliente e como Fornecedor... \n")
        ativar_cliente_fornecedor = await pessoas_ativa_cliente_fornecedor(cod_cliente_incorreto, True, True)
        if ativar_cliente_fornecedor.sucesso == True:
            steps += 'ETAPA 01 - CLIENTE E FORNECEDOR - ATIVADOS COM SUCESSO'
            console.log(ativar_cliente_fornecedor.retorno, style="bold green")
        else:
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=ativar_cliente_fornecedor.retorno,
                status=RpaHistoricoStatusEnum.Falha, 
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )
        
        #REALIZAR PROCESSO DE NOTA FISCAL DE SAIDA 
        type_text_into_field("Nota Fiscal de Saida", app["TFrmMenuPrincipal"]["Edit"], True, "50")
        pyautogui.press("enter")
        await worker_sleep(2)
        pyautogui.press('down')
        pyautogui.press("enter")
        console.print(f"\nPesquisa: 'Nota Fiscal de Saída' realizada com sucesso",style="bold green")
        await worker_sleep(6)

        busca_nf_saida = await nf_busca_nf_saida(numero_cupom_fiscal)
        if busca_nf_saida.sucesso == True:
            console.log(busca_nf_saida.retorno, style="bold green")
        else:
            retorno = f"{busca_nf_saida.retorno} \nEtapas Executadas:\n{steps}"
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=retorno,
                status=RpaHistoricoStatusEnum.Falha, 
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        
        #VERIFICANDO A EXISTENCIA DE WARNINGS 
        console.print("Verificando a existência de Warning... \n")
        warning_pop_up = await is_window_open("Warning")
        if warning_pop_up["IsOpened"] == True:
            console.print("possui Pop-up de Warning, analisando... \n")
            ocr_pop_warning = await ocr_warnings(numero_cupom_fiscal)
            if ocr_pop_warning.sucesso == True:
                retorno = f"POP UP Warning não mapeado para seguimento do processo, mensagem: {ocr_pop_warning.retorno} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                )
            else:
                retorno = f"{ocr_pop_warning.retorno} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )
        else:
            console.print("Não possui pop de Warning...\n")
        

        #VERIFICANDO SE O BOTÃO IR PARA A NOTA FATURA
        console.print("Verificando o status do Botão [Ir para Nota Fatura]...\n")
        try:
            btn_ir_para_nota = pyautogui.locateOnScreen(ASSETS_PATH + "\\notas_saida\\ir_para_nota_a_fatura_esmaecido.png", confidence=0.8)
            if btn_ir_para_nota:
                console.print("Botão 'Ir para nota de faturar' inativo, seguindo com o processo...\n")
                app = Application().connect(class_name="TFrmNotaFiscalSaida", timeout=60)
                main_window = app["TFrmNotaFiscalSaida"]
                main_window.set_focus()
                main_window.close()
            else:
                retorno = f"Botão [Ir para nota de faturar] está ativo, impossibilitando realizar a devolução \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                )     
        except Exception as e:
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"Não foi possivel verificar o botão [Ir para nota de faturar], erro: {e}",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        
        #ETAPA 14 A 18
        #STEP 2 - EMISSAO DA NOTA 
        type_text_into_field("Nota Fiscal de Entrada", app["TFrmMenuPrincipal"]["Edit"], True, "50")
        pyautogui.press("enter")
        await worker_sleep(2)
        pyautogui.press("enter")
        console.print(f"\nPesquisa: 'Nota Fiscal de Entrada' realizada com sucesso",style="bold green",
        )

        # Procura campo documento
        console.print("Navegando pela Janela de Nota Fiscal de Entrada...\n")
        document_type = await select_documento_type("NFe - NOTA FISCAL ELETRONICA PROPRIA - DANFE SERIE 077")
        if document_type.sucesso == True:
            console.log(document_type.retorno, style="bold green")
        else:
            retorno = f"{document_type.retorno} \nEtapas Executadas:\n{steps}"
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=retorno,
                status=RpaHistoricoStatusEnum.Falha, 
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        await worker_sleep(4)

        app = Application().connect(class_name="TFrmNotaFiscalEntrada", timeout=60)
        main_window = app["TFrmNotaFiscalEntrada"]

        main_window.set_focus()
        await worker_sleep(3)

        console.print("Controles encontrados na janela 'Nota Fiscal de Entrada, navegando entre eles...\n")
        panel_TNotebook = main_window.child_window(class_name="TNotebook", found_index=0)
        panel_TPage = panel_TNotebook.child_window(class_name="TPage", found_index=0)
        panel_TPageControl = panel_TPage.child_window(class_name="TPageControl", found_index=0)
        panel_TTabSheet = panel_TPageControl.child_window(class_name="TTabSheet", found_index=0)

        #SELECIONANDO O TIPO NOTA
        console.print("SELECIONANDO O TIPO NOTA...\n")
        panel_tipo_nota = panel_TPageControl.child_window(class_name="TDBIGroupBox", found_index=1)
        radio_nota_devolucao = panel_tipo_nota.child_window(class_name="TDBIRadioButton", found_index=1)
        radio_nota_devolucao.click()
        await worker_sleep(1)

        #INSERINDO A ENTRADA E EMISSÃO 
        console.print("INSERINDO A ENTRADA E EMISSÃO ...\n")
        field_entrada = main_window.child_window(class_name="TDBIEditDate", found_index=1)
        field_emissao = main_window.child_window(class_name="TDBIEditDate", found_index=2)
        field_entrada.set_edit_text(data_hoje)
        await worker_sleep(1)
        field_emissao.set_edit_text(data_hoje)
        await worker_sleep(1)

        #INSERINDO CODIGO DO FORNECEDOR
        console.print("INSERINDO CODIGO DO FORNECEDOR ...\n")
        field_fornecedor = main_window.child_window(class_name="TDBIEditCode", found_index=0)
        field_fornecedor.click()
        field_fornecedor.set_edit_text(cod_cliente_incorreto)
        field_fornecedor.click()
        pyautogui.press("tab")
        await worker_sleep(2)

        #SELECIONAO A NOP 
        console.print("SELECIONAO A NOP...\n")
        select_box_nop_select = main_window.child_window(class_name="TDBIComboBox", found_index=0)
        select_box_nop_select.click()

        itens_to_select = select_box_nop_select.texts()
        nop_to_be_select = ''

        for item in itens_to_select:
            if '1662' in item and (('c/fi' in item.lower() or 'c /fi' in item.lower())):
                nop_to_be_select = item
                break

        if nop_to_be_select != '':
            set_combobox("||List", nop_to_be_select)
        else:
            retorno = f"Não foi possivel encontrar a nop \nEtapas Executadas:\n{steps}"
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=retorno,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
            )




        try:
            pesquisar_icon = pyautogui.locateOnScreen(ASSETS_PATH + "\\emsys\\selecionar_venda.png", confidence=0.8)
            pyautogui.click(pesquisar_icon)
            await worker_sleep(5)
        except Exception as e:
            retorno = f"Não foi possivel clicar no botão Selecionar Venda, erro: {e} \nEtapas Executadas:\n{steps}"
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=retorno,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )
        
        await worker_sleep(2)
        pesquisar_venda_devolucao = await is_window_open_by_class("TFrmPesquisarVendaDevolucao", "TFrmPesquisarVendaDevolucao")
        if pesquisar_venda_devolucao["IsOpened"] == True:
            app = Application().connect(class_name="TFrmPesquisarVendaDevolucao", timeout=60)
            main_window = app["TFrmPesquisarVendaDevolucao"]
            main_window.set_focus()

            panel_filtro = main_window.child_window(class_name="TGroupBox", found_index=0)
            #INSERINDO O NUMERO VENDA
            console.print("INSERINDO O NUMERO VENDA...\n")
            field_num_venda = panel_filtro.child_window(class_name="TDBIEditString", found_index=0)
            field_num_venda.set_edit_text(numero_cupom_fiscal)
            await worker_sleep(1)

            #INSERINDO O CODIGO DO CLIENTE
            console.print("INSERINDO O CODIGO DO CLIENTE...\n")
            field_cliente = panel_filtro.child_window(class_name="TDBIEditCode", found_index=0)
            field_cliente.set_edit_text(cod_cliente_incorreto)
            await worker_sleep(1)
            field_cliente.click()
            await worker_sleep(1)
            pyautogui.press('tab')
            await worker_sleep(3)

            try:
                pesquisar_icon = pyautogui.locateOnScreen(ASSETS_PATH + "\\notas_saida\\icon_pesquisa_nota_saida.png", confidence=0.8)
                pyautogui.click(pesquisar_icon)
                await worker_sleep(5)
            except Exception as e:
                retorno = f"Não foi possivel clicar na Lupa para buscar a nota fiscal, erro: {e} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )
        
            i = 0
            max_attempts = 17

            while i < max_attempts:
                i += 1
                console.print("Verificando se a nota foi encontrada...\n")
                try:
                    main_window.set_focus()
                    no_data_full_path = "assets\\entrada_notas\\no_data_display.png"
                    img_no_data = pyautogui.locateCenterOnScreen(no_data_full_path, confidence=0.6)
                    if img_no_data:
                        console.print("'No data display' ainda aparente. Tentando novamente...")
                        await worker_sleep(10)
                except pyautogui.ImageNotFoundException:
                    console.print("'No data display' não encontrado na tela!")
                    break

                except Exception as e:
                    console.print(f"Ocorreu um erro: {e}")
                
            
            await worker_sleep(5)
            # VERIFICANDO A EXISTENCIA DE ERRO
            erro_pop_up = await is_window_open_by_class("TMessageForm","TMessageForm")
            if erro_pop_up["IsOpened"] == True:
                retorno = f"Nota não encontrada no EMsys na tela de Pesquisa Vendas para Devolução \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                )

            main_window.set_focus()
            try:
                selecionar_todos_itens = pyautogui.locateOnScreen(ASSETS_PATH + "\\emsys\\selecinar_todos_itens_quadro_azul.png", confidence=0.8)
                pyautogui.click(selecionar_todos_itens)
                await worker_sleep(5)
            except Exception as e:
                retorno = f"Não foi possivel clicar em selecionar todos os itens na tela de Pesquisar Vendas para Devolução, erro: {e} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )

            try:
                pesquisar_icon = pyautogui.locateOnScreen(ASSETS_PATH + "\\emsys\\inserir.png", confidence=0.8)
                pyautogui.click(pesquisar_icon)
                await worker_sleep(5)
            except Exception as e:
                retorno = f"Não foi possivel clicar em Inserir para selecionar a nota fiscal, erro: {e} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )

            await worker_sleep(5)
            console.print("Navegando pela Janela de Nota Fiscal de Entrada...\n")
            app = Application().connect(class_name="TFrmNotaFiscalEntrada")
            main_window = app["TFrmNotaFiscalEntrada"]

            main_window.set_focus()
            console.print("Acessando os itens da nota... \n")
            panel_TPage = main_window.child_window(class_name="TPage", title="Formulario")
            panel_TTabSheet = panel_TPage.child_window(class_name="TcxCustomInnerTreeView")
            panel_TTabSheet.wait("visible")
            panel_TTabSheet.click()
            send_keys("^({HOME})")
            await worker_sleep(1)
            send_keys("{DOWN " + ("5") + "}")

            # CONFIRMANDO SE A ABA DE ITENS FOI ACESSADA COM SUCESSO
            panel_TPage = main_window.child_window(class_name="TPage", title="Formulario")
            panel_TPage.wait("visible")
            panel_TTabSheet = panel_TPage.child_window(class_name="TTabSheet")
            title_n_serie = panel_TPage.child_window(title="N° Série")

            console.print("Verificando se os itens foram abertos com sucesso... \n")
            if not title_n_serie:
                retorno = f"Não foi possivel acessar a aba de 'Itens da nota \nEtapas Executadas:\n{steps}"
                console.print(f"Não foi possivel acessar a aba de 'Itens da nota...\n")
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )

            await worker_sleep(2)

            console.print("Acessando os itens indivualmente... \n")
            send_keys("{TAB 2}", pause=0.1)
            await worker_sleep(2)

            itens_nota = []

            index = 0
            last_line_item_emsys = 'x'
        
            try:
                while True:
                    await worker_sleep(2)
                    send_keys("^({HOME})")
                    await worker_sleep(1)
                    send_keys("{DOWN " + str(index) + "}", pause=0.1)
                    await worker_sleep(3)

                    with pyautogui.hold('ctrl'):
                        pyautogui.press('c')
                    await worker_sleep(1)
                    with pyautogui.hold('ctrl'):
                        pyautogui.press('c')

                    win32clipboard.OpenClipboard()
                    line_itens_emsys = win32clipboard.GetClipboardData().strip()
                    win32clipboard.CloseClipboard()
                    console.print(f"Linha atual copiada do Emsys: {line_itens_emsys}\nUltima Linha copiada: {last_line_item_emsys}")

                    if bool(line_itens_emsys):
                        if last_line_item_emsys == line_itens_emsys:
                            break
                        else:
                            last_line_item_emsys = line_itens_emsys

                    send_keys("+{F10}")
                    await worker_sleep(1)
                    send_keys("{DOWN 2}")
                    await worker_sleep(1)
                    send_keys("{ENTER}")
                    await worker_sleep(4)

                    app = Application().connect(title="Alteração de Item")
                    main_window = app["Alteração de Item"]
                    main_window.set_focus()

                    #RETRIVE ITENS NOTA 

                    tcx_page = main_window.child_window(class_name="TcxPageControl", found_index=0)
                    tab_sheet = tcx_page.child_window(class_name="TcxTabSheet", found_index=0)

                    quantidade_index = tab_sheet.child_window(class_name="TDBIEditNumber", found_index=42)
                    vl_unitario_index = tab_sheet.child_window(class_name="TCurrencyEdit", found_index=0)
                    vl_desconto_index = tab_sheet.child_window(class_name="TDBIEditNumber", found_index=41)

                    
                    quantidade = quantidade_index.window_text()
                    vl_unitario = vl_unitario_index.window_text()
                    vl_desconto = vl_desconto_index.window_text()

                    # ITERAGINDO COM O IPI
                    tpage_ipi = main_window.child_window(class_name="TPanel", found_index=0)

                    #RETRIVE COD E DESC ITEM 
                    cod_item_index = tpage_ipi.child_window(class_name="TDBIEditNumber", found_index=0)
                    cod_item = cod_item_index.window_text()

                    desc_item_index = tpage_ipi.child_window(class_name="TDBIEditString", found_index=1)
                    desc_item = desc_item_index.window_text()

                    itens_nota_dict = {
                        "codigo": cod_item,
                        "descricao": desc_item,
                        "quantidade": quantidade,
                        "valor_unitario": vl_unitario,
                        "desconto": vl_desconto
                    }
                    itens_nota.append(itens_nota_dict)


                    ipi = tpage_ipi.child_window(class_name="TDBIComboBox", found_index=2)
                    ipi_value = ipi.window_text()

                    console.print(f"Trabalhando com os itens, valor do IP {ipi_value}... \n")
                    if "IPI - ENTRADAS OUTROS" in ipi_value:
                        console.print(f"Iten selecionado com sucesso, clicando em Cancelar ...\n")
                        try:
                            btn_alterar = main_window.child_window(title="&Cancelar")
                            btn_alterar.click()
                        except:
                            btn_alterar = main_window.child_window(title="Cancelar")
                            btn_alterar.click()
                        await worker_sleep(3)
                    else:
                        console.print(f"Trabalhando com os itens, valor do IP em branco, selecionando IPI 0% ... \n")
                        ipi.click_input()
                        set_combobox("||List", "IPI - ENTRADAS OUTROS")

                        await worker_sleep(4)
                        tpage_ipi = main_window.child_window(class_name="TPanel", found_index=0)
                        ipi = tpage_ipi.child_window(class_name="TDBIComboBox", found_index=2)
                        ipi_value = ipi.window_text()

                        if "IPI - ENTRADAS OUTROS" in ipi_value:
                            console.print(f"Trabalhando com os itens, sucesso ao selecionar o valor do IPI ... \n")
                        else:
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=f"Erro ao selecionar o IPI de unidade nos itens, IPI: {ipi_value}",
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                            )

                        await worker_sleep(4)

                        console.print(f"Iten selecionado com sucesso, clicando em alterar ...\n")
                        try:
                            btn_alterar = main_window.child_window(title="&Alterar")
                            btn_alterar.click()
                        except:
                            btn_alterar = main_window.child_window(title="Alterar")
                            btn_alterar.click()
                        await worker_sleep(3)

                        confirm_pop_up = await is_window_open_by_class("TMessageForm","TMessageForm")
                        if confirm_pop_up["IsOpened"] == True:
                            app_confirm = Application().connect(
                            class_name="TMessageForm"
                            )
                            main_window_confirm = app_confirm["TMessageForm"]

                            btn_yes = main_window_confirm["&Yes"]
                            try:
                                btn_yes.click()
                                await worker_sleep(3)
                                console.print("O botão Yes foi clicado com sucesso.", style="green")
                                main_window.close()
                            except:
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=f"Não foi possivel clicar em Yes durante a alteração da tributação IPI",
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                                )
                    index = index+1
            except Exception as e:
                retorno = f"Erro ao trabalhar nas alterações dos itens, erro: {e} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )

            await worker_sleep(5)
            console.print("Navegando pela Janela de Nota Fiscal de Entrada - Acessando a Janela de Pagamento...\n")
            app = Application().connect(class_name="TFrmNotaFiscalEntrada")
            main_window = app["TFrmNotaFiscalEntrada"]

            main_window.set_focus()
            console.log("Seleciona Pagamento", style="bold yellow")
            try:
                pyautogui.click(623, 374)
                await worker_sleep(1)
                send_keys("{DOWN " + ("4") + "}")
            except Exception as e:
                panel_TPage = main_window.child_window(class_name="TPage", title="Formulario")
                panel_TTabSheet = panel_TPage.child_window(class_name="TcxCustomInnerTreeView")
                panel_TTabSheet.wait("visible")
                panel_TTabSheet.click()
                send_keys("{DOWN " + ("2") + "}")

            
            console.print(f"Adicionando pagamento... \n")
            try:
                panel_TPage = main_window.child_window(class_name="TPage", title="Formulario")
                panel_TTabSheet = panel_TPage.child_window(class_name="TPageControl")
                panel_TabPagamento = panel_TTabSheet.child_window(class_name="TTabSheet")
                panel_TabPagamentoCaixa = panel_TTabSheet.child_window(title="Pagamento Pelo Caixa")
                tipo_cobranca = panel_TabPagamentoCaixa.child_window(class_name="TDBIComboBox", found_index=0)

                console.print(f"Selecionando a Especie de Caixa... \n")
                tipo_cobranca.click()
                await worker_sleep(1)
                set_combobox("||List", "13 - DEVOLUCAO DE VENDA")

                await worker_sleep(2)

                console.print(f"Capturando o valor em Valores Restante... \n")
                tab_valores = panel_TabPagamento.child_window(title="Valores")
                valores_restantes = tab_valores.child_window(
                    class_name="TDBIEditNumber", found_index=1
                )
                valores_restantes_text = valores_restantes.window_text()
                valor_nota_fiscal = valores_restantes_text
                console.print(f"Valor capturado {valores_restantes_text}, inserindo no campo Valor em Pagamento pelo Caixa... \n")

                valor = panel_TabPagamentoCaixa.child_window(class_name="TDBIEditNumber", found_index=0)
                valor.set_edit_text(valores_restantes_text)
            except Exception as e:
                retorno = f"Não foi possivel realizar as atividades na aba de 'Pagamento', erro: {e} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )
            

            # Inclui registro
            console.print(f"Incluindo registro...\n")
            try:
                ASSETS_PATH = "assets"
                inserir_registro = pyautogui.locateOnScreen(ASSETS_PATH + "\\entrada_notas\\IncluirRegistro.png", confidence=0.8)
                pyautogui.click(inserir_registro)
            except Exception as e:
                console.print(
                    f"Não foi possivel incluir o registro utilizando reconhecimento de imagem, Error: {e}...\n tentando inserir via posição...\n"
                )
                await incluir_registro()
                

            await worker_sleep(5)
            console.print("Verificando a existencia de POP-UP de Itens que Ultrapassam a Variação Máxima de Custo ...\n")
            itens_variacao_maxima = await is_window_open_by_class("TFrmTelaSelecao", "TFrmTelaSelecao")
            if itens_variacao_maxima["IsOpened"] == True:
                app = Application().connect(class_name="TFrmTelaSelecao")
                main_window = app["TFrmTelaSelecao"]
                send_keys("%o")
            

            #VERIFICANDO SE A NOTA FOI INCLUIDA COM SUCESSO
            console.print("Verificando a se a Nota foi incluida com sucesso... \n")
            try:
                app = Application().connect(title="Information", timeout=180)
                main_window = app["Information"]
                main_window.set_focus()

                #EXTRAINDO O NUMERO DA NOTA 
                window_rect = main_window.rectangle()
                screenshot = pyautogui.screenshot(
                    region=(
                        window_rect.left,
                        window_rect.top,
                        window_rect.width(),
                        window_rect.height(),
                    )
                )
                username = getpass.getuser()
                short_uuid = str(uuid.uuid4()).replace('-', '')[:6]
                path_to_png = f"C:\\Users\\{username}\\Downloads\\aviso_popup_{short_uuid}.png"
                screenshot.save(path_to_png)
                console.print(f"Print salvo em {path_to_png}...\n")

                console.print(
                    f"Preparando a imagem para maior resolução e assertividade no OCR...\n"
                )
                image = Image.open(path_to_png)
                image = image.convert("L")
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(2.0)
                image.save(path_to_png)
                console.print(f"Imagem preparada com sucesso...\n")
                console.print(f"Realizando OCR...\n")
                captured_text = pytesseract.image_to_string(Image.open(path_to_png))
                console.print(f"Texto Full capturado {captured_text}...\n")
                os.remove(path_to_png)
                pattern = r"sequ[êe]ncia:\s*(\d+)"
                match = re.search(pattern, captured_text)

                if match:
                    numero_nota_fiscal = match.group(1)


                app = Application().connect(title="Information", timeout=180)
                main_window = app["Information"]
                main_window.set_focus()
                try:
                    btn_ok = main_window.child_window(class_name="TButton", found_index=0)
                    btn_ok.click()
                except Exception as e:
                    pyautogui.press('enter')
                finally:
                    pyautogui.press('enter')

                
                await worker_sleep(3)
                steps += 'ETAPA 02 - Nota fiscal de Entrada Incluida com sucesso'
            except Exception as e:
                    retorno = f"Não foi possivel obter a confirmação de Nota fiscal incluida com sucesso, erro {e} \nEtapas Executadas:\n{steps}"
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=retorno,
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )

        else:
            retorno = f"Não foi possivel abrir a tela de Pesquisar Venda para Devolução  \nEtapas Executadas:\n{steps}"
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=retorno,
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )

        app = Application().connect(class_name="TFrmNotaFiscalEntrada")
        main_window = app["TFrmNotaFiscalEntrada"]
        main_window.close()
        await worker_sleep(3)
        pyautogui.press('enter')
    
    
        #STEP 3 
        type_text_into_field("Gerenciador de Notas Fiscais", app["TFrmMenuPrincipal"]["Edit"], True, "50")
        pyautogui.press("enter")
        await worker_sleep(2)
        pyautogui.press("enter")
        await worker_sleep(5)
        console.print(f"\nPesquisa: 'Gerenciador de Notas Fiscais' realizada com sucesso",style="bold green")
        pesquisar_venda_devolucao = await is_window_open_by_class("TFrmGerenciadorNFe2", "TFrmGerenciadorNFe2")
        if pesquisar_venda_devolucao["IsOpened"] == True:
            console.print(f"\n'Gerenciador de Notas Fiscais'aberta com sucesso",style="bold green")
            selecionar_itens_gerenciador_nfe = await gerenciador_nf_header(data_hoje, cod_cliente_incorreto)
            if selecionar_itens_gerenciador_nfe.sucesso:
                console.print("PROCESSO EXECUTADO COM SUCESSO, SEGUINDO COM O PROCESSO PARA TRANSMITIR A NF-E...\n")
                app = Application().connect(class_name="TFrmGerenciadorNFe2", timeout=10)
                main_window = app["TFrmGerenciadorNFe2"]
                main_window.set_focus()

                console.print("Obtendo informacao da tela para o botao Transfimitir\n")
                tpanel_footer = main_window.child_window(class_name="TPanel", found_index=1)
                btn_transmitir = tpanel_footer.child_window(class_name="TBitBtn", found_index=5)
                btn_transmitir.click()
                console.print("Transmitir clicado com sucesso...\n")
                await worker_sleep(3)

                max_attempts = 10
                i = 0
                console.print("Aguardando pop de operacação concluida \n")
                while i < max_attempts:
                    try:
                        app = Application().connect(class_name="TFrmProcessamentoNFe2", timeout=10)
                        main_window = app["TFrmProcessamentoNFe2"]

                        await worker_sleep(5)
                        information_pop_up = await is_window_open_by_class("TMessageForm", "TMessageForm")
                        if information_pop_up["IsOpened"] == True:
                            msg_pop_up = await ocr_by_class(numero_nota_fiscal, "TMessageForm", "TMessageForm")
                            if msg_pop_up.sucesso:
                                if 'concl' in msg_pop_up.retorno.lower():
                                    try:
                                        information_operacao_concluida = main_window.child_window(class_name="TMessageForm")
                                        btn_ok = information_operacao_concluida.child_window(class_name="TButton")
                                        btn_ok.click()
                                        await worker_sleep(4)
                                    except:
                                        pyautogui.press('enter')
                                        await worker_sleep(4)
                                    finally:
                                        pyautogui.press('enter')
                                    break
                                else:
                                    retorno = f"Pop up nao mapeado para seguimento do robo {msg_pop_up} \nEtapas Executadas:\n{steps}"
                                    return RpaRetornoProcessoDTO(
                                        sucesso=False,
                                        retorno=retorno,
                                        status=RpaHistoricoStatusEnum.Falha,
                                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                                    )
                            else:
                                retorno = f"Não foi possivel realizar a confirmação do msg do OCR \nEtapas Executadas:\n{steps}"
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=retorno,
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                                )
                    except Exception as e:
                        pass


                    i += 1
                    await worker_sleep(10)
                

                if i == max_attempts:
                    console.print("Número máximo de tentativas atingido. Encerrando...")
                    retorno = f"Tempo esgotado e numero de tentativas atingido, não foi possivel obter o retorno de conclusão para transmissão na tela de Gerenciador NF-e \nEtapas Executadas:\n{steps}"
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=retorno,
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )
                

                console.print("Verificando se a nota foi transmitida com sucesso")
                app = Application().connect(class_name="TFrmProcessamentoNFe2", timeout=15)
                main_window = app["TFrmProcessamentoNFe2"]
                main_window.set_focus()

                tpanel_footer = main_window.child_window(class_name="TGroupBox", found_index=0)

                rect = tpanel_footer.rectangle()
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2

                pyautogui.moveTo(center_x, center_y)
                double_click(coords=(center_x, center_y))

                with pyautogui.hold('ctrl'):
                    pyautogui.press('c')
                await worker_sleep(1)
                with pyautogui.hold('ctrl'):
                    pyautogui.press('c')

                win32clipboard.OpenClipboard()
                pop_up_status = win32clipboard.GetClipboardData().strip()
                win32clipboard.CloseClipboard()
                console.print(f"Status copiado: {pop_up_status}")

                if "autorizado o uso da nf-e" in pop_up_status.lower():
                    console.print("Sucesso ao transmitir...\n")
                    main_window.close()
                else:
                    get_error_msg = await get_text_display_window(pop_up_status)
                    console.print(f"Mensagem Rejeição: {get_error_msg}")
                    retorno = f"Erro ao transmitir, mensagem de rejeição {get_error_msg} \nEtapas Executadas:\n{steps}"
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=retorno,
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                    )


                #PROCESSO DE IMPRESSÃO 
                console.print("Conectando a janela para seguir com o processo de impressão...\n")
                app = Application().connect(class_name="TFrmGerenciadorNFe2", timeout=60)
                main_window = app["TFrmGerenciadorNFe2"]
                main_window.set_focus()
                console.print("Obtendo informações do btn para imprimir...\n")
                tpanel_footer = main_window.child_window(class_name="TPanel", found_index=1)
                btn_imprimir_danfe = tpanel_footer.child_window(class_name="TBitBtn", found_index=0)
                btn_imprimir_danfe.click()
                await worker_sleep(5)

                console.print("Obtendo informações do btn selecionar PDF...\n")
                app = Application().connect(class_name="TFrmConfigurarTemplateDANF2", timeout=60)
                main_window = app["TFrmGerenciadorNFe2"]
                main_window.set_focus()
                console.print("Selecionando PDF...\n")
                btn_selecionar_pdf = main_window.child_window(class_name="TRadioButton", found_index=1)
                btn_selecionar_pdf.click()
                await worker_sleep(2)

                console.print("BTN Gerar ...\n")
                btn_gerar = main_window.child_window(class_name="TBitBtn", found_index=1)
                btn_gerar.click()
                console.print("BTN Gerar - Clicado com sucesso...\n")
                await worker_sleep(2)
                steps += 'ETAPA 03 - PROCESSO DE TRANSMITIR NF-e EXECUTADO COM SUCESSO '


                app = Application().connect(title="Salvar par arquivo")
                main_window = app["Salvar"]
                console.print("Tela 'Salvar' encontrada!")

                console.print("Interagindo com a tela 'Salvar'...\n")
                username = getpass.getuser()
                path_to_txt = f"C:\\Users\\{username}\\Downloads\\DEVOLUÇÃO PRAZO A FATURAR {numero_cupom_fiscal}"

                main_window.type_keys("%n")
                pyautogui.write(path_to_txt)
                await worker_sleep(1)
                main_window.type_keys("%l")
                console.print("Arquivo salvo com sucesso...\n")
                await worker_sleep(6)

                with open(f"{path_to_txt}.pdf", 'rb') as file:
                    file_bytes = io.BytesIO(file.read())

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                desArquivo = f"DEVOLUÇÃO PRAZO A FATURAR {numero_cupom_fiscal}.pdf"
                try:
                    await send_file(historico_id, desArquivo, "pdf", file_bytes, file_extension="pdf")
                    os.remove(path_to_txt)
                except Exception as e:
                    result = f"Arquivo DEVOLUÇÃO PRAZO A FATURAR gerado com sucesso, porém gerou erro ao realizar o envio para o backoffice {e} - Arquivo ainda salvo na dispositivo utilizado no diretório {path_to_txt}! \nEtapas Executadas:\n{steps}"
                    console.print(result, style="bold red")
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=result,
                        status=RpaHistoricoStatusEnum.Falha,
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )

                app = Application().connect(class_name="TFrmConfigurarTemplateDANF2", timeout=60)
                main_window = app["TFrmGerenciadorNFe2"]
                main_window.close()

                app = Application().connect(class_name="TFrmGerenciadorNFe2", timeout=60)
                main_window = app["TFrmGerenciadorNFe2"]
                main_window.close()


            else:
                retorno = f"{selecionar_itens_gerenciador_nfe} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha, 
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )
        else:
            retorno = f"Não foi possivel abrir a tela de Gerenciador de Notas Fiscais \nEtapas Executadas:\n{steps}"
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=retorno,
                status=RpaHistoricoStatusEnum.Falha, 
                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
            )


        #STEP 4 
        #PRE VENDA
        type_text_into_field("Cadastro Pré venda", app["TFrmMenuPrincipal"]["Edit"], True, "50")
        pyautogui.press("enter")
        await worker_sleep(2)
        pyautogui.press("enter")
        await worker_sleep(4)
        console.print(f"\nPesquisa: 'Cadastro Pré venda' realizada com sucesso",style="bold green")
        cadastro_pre_venda = await is_window_open_by_class("TFrmPreVenda", "TFrmPreVenda")
        if cadastro_pre_venda["IsOpened"] == True:
            preenchimento_header_pre_venda = await cadastro_pre_venda_header("5667 - VENDA DE COMB OU LUBRI - S/ ESTOQ E C/ FINANC", cod_cliente_correto, "A VISTA")
            if preenchimento_header_pre_venda.sucesso:
                try:
                    cidade_cliente = preenchimento_header_pre_venda.retorno
                    console.print(f"\nPreenchimento cabeçalho da pre venda preenchido com sucesso, seguindo com o processo.. ",style="bold green")
                    app = Application().connect(class_name="TFrmPreVenda", timeout=60)
                    main_window = app["TFrmPreVenda"]
                    main_window.set_focus()
                    
                    console.print("Navegando nos elementos...\n")
                    panel_TPage= main_window.child_window(class_name="TPage", found_index=0)
                    panel_menu_itens= main_window.child_window(class_name="TcxCustomInnerTreeView", found_index=0)

                    console.print("Acessando a janela de Itens...\n")
                    panel_menu_itens.click()
                    await worker_sleep(1)
                    pyautogui.press('home')
                    await worker_sleep(1)
                    pyautogui.press('down')
                    console.print(nota.get('itens'))
                    item_devolvido = ''


                    #FOR ITENS ENTRADA BACKOFFICE
                    for item in nota.get('itens'):
                        quantidade = item['novaQuantidade']
                        preco = item['novoPreco']
                        descricao = item['descricao']
                        quantidade = str(quantidade)
                        preco = str(preco)
                        #descricao = descricao.replace(".",",")
                        console.print(quantidade, preco, descricao)
                        item_devolvido = descricao

                        if 'arla' in descricao.lower():
                            item_arla = True

                        app = Application().connect(class_name="TFrmPreVenda", timeout=60)
                        main_window = app["TFrmPreVenda"]
                        main_window.set_focus()
                        
                        console.print("Itens acessado com sucesso, clicando em Incluir...\n")
                        panel_TGroup_Box= panel_TPage.child_window(class_name="TGroupBox", found_index=0)
                        btn_incluir = panel_TGroup_Box.child_window(class_name="TDBIBitBtn", found_index=4)
                        btn_incluir.click()
                        await worker_sleep(2)
                        console.print("Incluir clicado com sucesso...\n")

                        #VERIFICANDO A EXISTENCIA DE WARNINGS 
                        console.print("Verificando a existência de Warning... \n")
                        warning_pop_up = await is_window_open("Warning")
                        if warning_pop_up["IsOpened"] == True:
                            console.print("possui Pop-up de Warning, analisando... \n")
                            ocr_pop_warning = await ocr_warnings(numero_cupom_fiscal)
                            if ocr_pop_warning.sucesso == True:
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=f"POP UP Warning não mapeado para seguimento do processo, mensagem: {ocr_pop_warning.retorno}",
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                                )
                            else:
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=f"POP UP Warning não mapeado para seguimento do processo",
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                                )


                        i = 0
                        while i < 7:
                            try:
                                console.print("Clicando sobre a lupa para inserir o almoxarifado...\n")
                                app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=130)
                                main_window = app["TFrmIncluiItemPreVenda"]
                                main_window.set_focus()
                                panel_TGroup_Box= main_window.child_window(class_name="TPanel", found_index=2)
                                lupa_almoxarifaco = panel_TGroup_Box.child_window(class_name="TDBIBitBtn", found_index=1)
                                lupa_almoxarifaco.click()
                                console.print("Lupa clicado com sucesso inserindo a descrição do almoxarifado...\n")
                                await worker_sleep(2)

                                dialog_buscar = await is_window_open_by_class("TfrmDialogBuscaGeral", "TfrmDialogBuscaGeral")
                                if dialog_buscar["IsOpened"] == True:
                                    break
                                else:
                                    console.print("Não foi possivel abrir a janela de Busca Geral")
                                    i = i+1
                            except Exception as e:
                                console.print(f"Erro ao abrir a janela de Busca Geral: {e}")
                                i = i+1

                        
                        if i == 7:
                            retorno = f"Não foi possivel abrir a tela para buscar pelo item do produto na seleção do almoxarifado -  \nEtapas Executadas:\n{steps}"
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=retorno,
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                            )

                        app = Application().connect(class_name="TfrmDialogBuscaGeral", timeout=60)
                        main_window = app["TfrmDialogBuscaGeral"]
                        main_window.set_focus()

                        console.print("Buscando a mercadoria baseado na descrição...\n")
                        rect = main_window.rectangle()
                        center_x = (rect.left + rect.right) // 2
                        center_y = (rect.top + rect.bottom) // 2

                        #pyautogui.moveTo(center_x, center_y)
                        await worker_sleep(1)
                        pyautogui.click(center_x, center_y)
                        await worker_sleep(1)
                        send_keys("^({HOME})")

                        last_line = ''
                        while True:
                            with pyautogui.hold('ctrl'):
                                pyautogui.press('c')
                            await worker_sleep(1)
                            with pyautogui.hold('ctrl'):
                                pyautogui.press('c')

                            win32clipboard.OpenClipboard()
                            descricao_item = win32clipboard.GetClipboardData().strip()
                            win32clipboard.CloseClipboard()

                            if last_line == descricao_item:
                                retorno = f"Todos os itens percorridos e não foi possivel encontrar a descrição condizente a {descricao} \nEtapas Executadas:\n{steps}"
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=retorno,
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                                )
                            else:
                                if descricao.lower() in descricao_item.lower():
                                    break
                                else:
                                    last_line = descricao_item
                                    pyautogui.press('down')


                        main_window.set_focus()
                        send_keys("%o")
                        await worker_sleep(3)
                        console.print("Processo finalizado com sucesso, seguindo com a seleção da natureza...\n")

                        app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                        main_window = app["TFrmIncluiItemPreVenda"]
                        main_window.set_focus()
                        panel_TGroup_Box= main_window.child_window(class_name="TPanel", found_index=2)
                        natureza_oper_select = panel_TGroup_Box.child_window(class_name="TDBIComboBox", found_index=0)
                        natureza_oper_select.click()
                        await worker_sleep(1)
                        set_combobox("||List", "5667 - VENDA DE COMB OU LUBRI - S/ ESTOQ E C/ FINANC")
                        await worker_sleep(1)
                        console.print("Natureza da operação selecionado com sucesso, preenchendo os itens...\n")

                        #INSERINDO A QUANTIDADE
                        main_window.set_focus()
                        panel_TPage_Control= main_window.child_window(class_name="TcxPageControl", found_index=0)
                        panel_tabSheet = panel_TPage_Control.child_window(class_name="TcxTabSheet", found_index=0)

                        field_quantidade = panel_tabSheet.child_window(class_name="TDBIEditNumber", found_index=8)
                        console.print("Inserindo a quantidade de Itens...\n")
                        field_quantidade.click()
                        await worker_sleep(1)
                        pyautogui.press('del')
                        await worker_sleep(1)
                        pyautogui.press('backspace')
                        await worker_sleep(1)
                        pyautogui.write(quantidade)
                        #field_quantidade.set_edit_text(quantidade)
                        await worker_sleep(1)
                        pyautogui.press('tab')
                        await worker_sleep(2)

                        #INSERINDO O VALOR INDIVIDUAL DO ITEM
                        console.print("Inserindo o valor indivual do Item...\n")
                        btn_valor_unitario = panel_tabSheet.child_window(class_name="TDBIBitBtn", found_index=0)
                        btn_valor_unitario.click()
                        await worker_sleep(2)

                        app = Application().connect(class_name="TFrmInputBoxNumero", timeout=60)
                        main_window = app["TFrmInputBoxNumero"]
                        main_window.set_focus()

                        field_valor = main_window.child_window(class_name="TDBIEditNumber", found_index=0)
                        field_valor.click()
                        await worker_sleep(1)
                        for _ in range(10):
                            pyautogui.press("del")
                            pyautogui.press("backspace")
                        pyautogui.write(preco)
                        #field_valor.set_edit_text(preco)
                        await worker_sleep(2)

                        main_window.set_focus()
                        send_keys("%o")
                        await worker_sleep(2)
                        console.print("Valor inserido com sucesso...\n")

                        app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                        main_window = app["TFrmIncluiItemPreVenda"]
                        main_window.set_focus()
                        send_keys("%i")
                        await worker_sleep(2)
                        main_window.close()


                    #FOR OUTROS ITENS NOTA
                    for item in itens_nota:

                        quantidade = item['quantidade']
                        preco = item['valor_unitario']
                        descricao = item['descricao']
                        item_cod = item['codigo']
                        #descricao = descricao.replace(".",",")
                        console.print(quantidade, preco, descricao)

                        if descricao not in item_devolvido:
                            if 'arla' in descricao.lower():
                                item_arla = True

                            app = Application().connect(class_name="TFrmPreVenda", timeout=60)
                            main_window = app["TFrmPreVenda"]
                            main_window.set_focus()
                            
                            console.print("Itens acessado com sucesso, clicando em Incluir...\n")
                            panel_TGroup_Box= panel_TPage.child_window(class_name="TGroupBox", found_index=0)
                            btn_incluir = panel_TGroup_Box.child_window(class_name="TDBIBitBtn", found_index=4)
                            btn_incluir.click()
                            await worker_sleep(2)
                            console.print("Incluir clicado com sucesso...\n")

                            #VERIFICANDO A EXISTENCIA DE WARNINGS 
                            console.print("Verificando a existência de Warning... \n")
                            warning_pop_up = await is_window_open("Warning")
                            if warning_pop_up["IsOpened"] == True:
                                console.print("possui Pop-up de Warning, analisando... \n")
                                ocr_pop_warning = await ocr_warnings(numero_cupom_fiscal)
                                if ocr_pop_warning.sucesso == True:
                                    return RpaRetornoProcessoDTO(
                                        sucesso=False,
                                        retorno=f"POP UP Warning não mapeado para seguimento do processo, mensagem: {ocr_pop_warning.retorno}",
                                        status=RpaHistoricoStatusEnum.Falha,
                                        tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                                    )
                                else:
                                    return RpaRetornoProcessoDTO(
                                        sucesso=False,
                                        retorno=f"POP UP Warning não mapeado para seguimento do processo",
                                        status=RpaHistoricoStatusEnum.Falha,
                                        tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                                    )


                            main_window.set_focus()
                            send_keys("%o")
                            await worker_sleep(3)
                            console.print("Processo finalizado com sucesso, seguindo com a seleção da natureza...\n")

                            app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                            main_window = app["TFrmIncluiItemPreVenda"]
                            main_window.set_focus()
                            panel_TGroup_Box= main_window.child_window(class_name="TPanel", found_index=2)
                            almoxarificado_index = panel_TGroup_Box.child_window(class_name="TDBIEditNumber", found_index=1)
                            cod_almoxarificado = int(cod_empresa)+50
                            almoxarificado_index.click()
                            await worker_sleep(1)
                            pyautogui.write(str(cod_almoxarificado))
                            pyautogui.press('tab')
                            await worker_sleep(1)

                            cod_item_index = panel_TGroup_Box.child_window(class_name="TDBIEditNumber", found_index=0)
                            cod_item_index.click()
                            await worker_sleep(1)
                            pyautogui.write(str(item_cod))
                            pyautogui.press('tab')
                            await worker_sleep(1)


                            natureza_oper_select = panel_TGroup_Box.child_window(class_name="TDBIComboBox", found_index=0)
                            nop_selected = natureza_oper_select.window_text()
                            nop_selected_value = nop_selected[:4]

                            itens_to_select = natureza_oper_select.texts()
                            nop_to_be_select = ''

                            for item in itens_to_select:
                                if nop_selected_value in item and (('c/' in item.lower() or 'c /' in item.lower()) and ('s/' in item.lower() or 's /' in item.lower())):
                                    nop_to_be_select = item
                                    break

                            natureza_oper_select.click()
                            await worker_sleep(1)

                            if 'gasolina' in descricao.lower() or 'diesel' in descricao.lower() or 'gnv' in descricao.lower() or 'etanol' in descricao.lower():
                                set_combobox("||List", "5667 - VENDA DE COMB OU LUBRI - S/ ESTOQ E C/ FINANC")
                            else:
                                if nop_to_be_select != '':
                                    set_combobox("||List", nop_to_be_select)
                                else:
                                    retorno = f"Não foi possivel encontrar a nop para o item, nop original {nop_selected} \nEtapas Executadas:\n{steps}"
                                    return RpaRetornoProcessoDTO(
                                        sucesso=False,
                                        retorno=retorno,
                                        status=RpaHistoricoStatusEnum.Falha,
                                        tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                                    )
                                set_combobox("||List", "5405 - VENDA DE MERCADORIA ST S/ ESTOQUE C/FINANC")
                            await worker_sleep(1)
                            console.print("Natureza da operação selecionado com sucesso, preenchendo os itens...\n")

                            #INSERINDO A QUANTIDADE
                            main_window.set_focus()
                            panel_TPage_Control= main_window.child_window(class_name="TcxPageControl", found_index=0)
                            panel_tabSheet = panel_TPage_Control.child_window(class_name="TcxTabSheet", found_index=0)

                            field_quantidade = panel_tabSheet.child_window(class_name="TDBIEditNumber", found_index=8)
                            console.print("Inserindo a quantidade de Itens...\n")
                            field_quantidade.click()
                            await worker_sleep(1)
                            pyautogui.press('del')
                            await worker_sleep(1)
                            pyautogui.press('backspace')
                            await worker_sleep(1)
                            pyautogui.write(quantidade)
                            #field_quantidade.set_edit_text(quantidade)
                            await worker_sleep(1)
                            pyautogui.press('tab')
                            await worker_sleep(2)

                            app = Application().connect(class_name="TFrmIncluiItemPreVenda", timeout=60)
                            main_window = app["TFrmIncluiItemPreVenda"]
                            main_window.set_focus()
                            send_keys("%i")
                            await worker_sleep(2)
                            main_window.close()
                        else:
                            console.print(f"Item ja incluso no step anterior...\n")


                    app = Application().connect(class_name="TFrmPreVenda", timeout=60)
                    main_window = app["TFrmPreVenda"]
                    main_window.set_focus()
                    
                    console.print("Navegando nos elementos...\n")
                    panel_TPage= main_window.child_window(class_name="TPage", found_index=0)
                    panel_menu_itens= main_window.child_window(class_name="TcxCustomInnerTreeView", found_index=0)

                    console.print("Acessando a janela de Caixa...\n")
                    panel_menu_itens.click()
                    await worker_sleep(1)
                    pyautogui.press('home')
                    await worker_sleep(1)
                    send_keys("{DOWN " + ("3") + "}")

                    console.print("Capturando o valor total da Pre Venda...\n")
                    main_window.set_focus()
                    tnotebook_panel = main_window.child_window(class_name="TNotebook", found_index=0)
                    tpage_panel = tnotebook_panel.child_window(class_name="Tpage", found_index=0)
                    group_box = tpage_panel.child_window(class_name="TDBIGroupBox", found_index=0)
                    valor_pre_venda_index = group_box.child_window(class_name="TDBIEditNumber", found_index=4)
                    vl_pre_venda = valor_pre_venda_index.window_text()
                    console.print(f"Valor capturado {vl_pre_venda}")

                    console.print("Iniciando o prceosso de registrar o valor no Caixa...\n")
                    main_window.set_focus()
                    recebimento_caixa_index = tnotebook_panel.child_window(title="Recebimento Pelo Caixa")
                    selecionar_especie = recebimento_caixa_index.child_window(class_name="TDBIComboBox", found_index=0)
                    selecionar_especie.click()
                    await worker_sleep(2)
                    set_combobox("||List", "13 - DEVOLUCAO DE VENDA")
                    await worker_sleep(1)
                    valor_index = recebimento_caixa_index.child_window(class_name="TDBIEditNumber", found_index=0)
                    valor_index.set_edit_text(vl_pre_venda)
                    await worker_sleep(2)

                    console.print("Clicando em incluir registro...\n")
                    btn_incluir_registro = recebimento_caixa_index.child_window(class_name="TDBIBitBtn", found_index=3)
                    btn_incluir_registro.click()
                    

                    #CONFIRMANDO NA TELA DE PRE VENDA
                    try:
                        console.print("CLICANDO EM CONFIRMAR... \n")
                        app = Application().connect(class_name="TFrmPreVenda", timeout=60)
                        main_window = app["TFrmPreVenda"]
                        main_window.set_focus()

                        panel_Tnotebook = main_window.child_window(class_name="TNotebook", found_index=0)
                        panel_Tnotebook = panel_Tnotebook.child_window(class_name="TPage", found_index=0)
                        btn_confirmar = panel_Tnotebook.child_window(class_name="TBitBtn", found_index=11)
                        btn_confirmar.click()
                        console.print("CONFIRMAR CLICADO COM SUCESSO... \n")
                        await worker_sleep(3)
                    except Exception as e:
                        retorno = f"Não foi possivel clicar em Confirma na tela de Pre Venda \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=retorno,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )


                    # Inclui registro
                    console.print(f"Incluindo registro...\n")
                    try:
                        ASSETS_PATH = "assets"
                        inserir_registro = pyautogui.locateOnScreen(ASSETS_PATH + "\\entrada_notas\\IncluirRegistro.png", confidence=0.8)
                        pyautogui.click(inserir_registro)
                    except Exception as e:
                        console.print(
                            f"Não foi possivel incluir o registro utilizando reconhecimento de imagem, Error: {e}...\n tentando inserir via posição...\n"
                        )
                        await incluir_registro()

                    await worker_sleep(8)
                    #VERIFICANDO A EXISTENCIA DE WARNINGS 
                    console.print("Verificando a existência de Warning... \n")
                    warning_pop_up = await is_window_open("Warning")
                    if warning_pop_up["IsOpened"] == True:
                        console.print("possui Pop-up de Warning, analisando... \n")
                        ocr_pop_warning = await ocr_warnings(numero_cupom_fiscal)
                        if ocr_pop_warning.sucesso == True:
                            retorno = f"POP UP Warning não mapeado para seguimento do processo, mensagem: {ocr_pop_warning.retorno} \nEtapas Executadas:\n{steps}"
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=retorno,
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                            )
                        else:
                            retorno = f"POP UP Warning não mapeado para seguimento do processo \nEtapas Executadas:\n{steps}"
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=retorno,
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                            )
                    
                    #VERIFICANDO SE A PRÉ VENDA FOI INCLUIDA COM SUCESSO
                    console.print("VERIFICANDO SE A PRÉ VENDA FOI INCLUIDA COM SUCESSO... \n")
                    information_pop_up = await is_window_open("Informação")
                    if information_pop_up["IsOpened"] == True:
                        msg_pop_up = await ocr_title(numero_nota_fiscal, "Informação")
                        console.print(f'retorno:{msg_pop_up.sucesso}')
                        console.print(f'retorno:{msg_pop_up}')
                        if msg_pop_up.sucesso == True:
                            msg_retorno = msg_pop_up.retorno
                            console.print(msg_retorno)
                            if 'venda' in msg_retorno.lower():
                                try:
                                    information_operacao_concluida = main_window.child_window(title="Informação")
                                    btn_ok = information_operacao_concluida.child_window(class_name="TButton")
                                    btn_ok.click()
                                    await worker_sleep(4)
                                except:
                                    pyautogui.press('enter')
                                    await worker_sleep(4)
                            else:
                                retorno = f"Pop up nao mapeado para seguimento do robo {msg_pop_up.retorno} \nEtapas Executadas:\n{steps}"
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=retorno,
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                                )
                        else:
                            retorno = f"Não foi possivel realizar a confirmação do msg do OCR \nEtapas Executadas:\n{steps}"
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=retorno,
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                            )
                    else:
                        retorno = f"Janela de confirmação de pre venda incluida nao encontrada \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=retorno,
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                            )
                    

                    steps += 'ETAPA 04 - PRE VENDA INCLUIDA COM SUCESSO'
                    #CONFIRMANDO POP UP DE PRÉ VENDA - PESQUISAR PRE VENDA
                    try:
                        console.print("CONFIRMANDO POP UP DE PRÉ VENDA - PESQUISAR PRE VENDA... \n")
                        app = Application().connect(class_name="TFrmPreVenda", timeout=10)
                        main_window = app["Confirm"]
                        main_window.set_focus()

                        btn_yes = main_window.child_window(class_name="TButton", found_index=1)
                        btn_yes.click()
                        await worker_sleep(3)
                    except Exception as e:
                        retorno = f"Pop Up de Confirm  (Deseja pesquisar a Pré Venda ?) não encontrado \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=retorno,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )


                    #CONFIRMANDO NA TELA DE PRE VENDA
                    try:
                        console.print("CLICANDO EM CONFIRMAR... \n")
                        app = Application().connect(class_name="TFrmPreVenda", timeout=60)
                        main_window = app["TFrmPreVenda"]
                        main_window.set_focus()

                        panel_Tnotebook = main_window.child_window(class_name="TNotebook", found_index=0)
                        panel_Tnotebook = panel_Tnotebook.child_window(class_name="TPage", found_index=0)
                        btn_confirmar = panel_Tnotebook.child_window(class_name="TBitBtn", found_index=11)
                        btn_confirmar.click()
                        console.print("CONFIRMAR CLICADO COM SUCESSO... \n")
                        await worker_sleep(3)
                    except Exception as e:
                        retorno = f"Não foi possivel clicar em Confirma na tela de Pre Venda \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=retorno,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )


                    #CONFIRMANDO NA TELA DE PRE VENDA
                    try:
                        console.print("CONFIRMANDO POP UP DE Deseja realmente confirmar esta PRÉ VENDA ... \n")
                        app = Application().connect(class_name="TFrmPreVenda", timeout=10)
                        main_window = app["Confirm"]
                        main_window.set_focus()

                        btn_yes = main_window.child_window(class_name="TButton", found_index=1)
                        btn_yes.click()
                        await worker_sleep(3)
                        pyautogui.press('enter')
                    except Exception as e:
                        retorno = f"Não foi possivel clicar para confirmar a janela 'Deseja realmente confirmar esta pre-venda' \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=retorno,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )

                    
                    #FATURAR
                    try:
                        console.print("FATURAR... \n")
                        app = Application().connect(class_name="TFrmPreVenda", timeout=10)
                        main_window = app["TFrmPreVenda"]
                        main_window.set_focus()

                        panel_Tnotebook = main_window.child_window(class_name="TNotebook", found_index=0)
                        panel_Tnotebook = panel_Tnotebook.child_window(class_name="TPage", found_index=0)
                        btn_faturar = panel_Tnotebook.child_window(class_name="TBitBtn", found_index=7)
                        btn_faturar.click()
                        console.print("BOTAO FATURAR CLICADO COM SUCESSO... \n")
                        await worker_sleep(5)
                    except Exception as e:
                        retorno = f"Não foi possivel clicar em Faturar na tela de pre venda, erro: {e} \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=retorno,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )
                    

                    warning_pop = await is_window_open_by_class("TFrmPreVenda", "Warning")
                    if warning_pop["IsOpened"] == True:
                        warning_ocr = await ocr_by_class(numero_cupom_fiscal, "TFrmPreVenda", "Warning")
                        if warning_ocr.sucesso == True:
                            msg_warning = warning_ocr.retorno
                            if 'permiss' in msg_warning:
                                retorno = f"Cliente sem permissão para realizar a emissão da nota fiscal, por favor verificar o cadastro \nEtapas Executadas:\n{steps}"
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=retorno,
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                                )
                            else:
                                retorno = f"Pop não mapeado para seguindo do processo {msg_warning} \nEtapas Executadas:\n{steps}"
                                return RpaRetornoProcessoDTO(
                                    sucesso=False,
                                    retorno=retorno,
                                    status=RpaHistoricoStatusEnum.Falha,
                                    tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
                                )
                        else:
                            retorno = f"Não foi possivel extrair a mensagem do warning \nEtapas Executadas:\n{steps}"
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=retorno,
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                            )
                   

                    information_pop_up = await is_window_open("Information")
                    if information_pop_up["IsOpened"] == True:
                        app = Application().connect(title="Information", timeout=30)
                        main_window = app["Information"]
                        main_window.set_focus()
                        btn_ok = main_window.child_window(class_name="TButton", found_index=0)
                        btn_ok.click()


                    await worker_sleep(15)
                    #FATURAMENTO PRÉ-VENDA
                    try:
                        console.print("FATURAMENTO PRÉ-VENDA... \n")
                        app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=60)
                        main_window = app["TFrmDadosFaturamentoPreVenda"]
                        main_window.set_focus()
                    except Exception as e:
                        retorno = f"Não foi encontrada a Janela Faturamento de Pré Venda \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=result,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )
                    

                    #VERIFICANDO SE POSSUI POP UP WARNING
                    console.print("Verificando a presença de Warning... \n")
                    warning_boo = False
                    try:
                        try:
                            app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=10)
                            main_window = app["Warning"]
                            main_window.set_focus()
                        except:
                            console.print('Except')
                            app = Application().connect(class_name="Warning", timeout=10)
                            main_window = app["Warning"]
                            main_window.set_focus()
                        console.print("Possui Warning... \n")
                        btn_ok = main_window.child_window(class_name="TButton", found_index=0)
                        btn_ok.click()
                        await worker_sleep(3)
                        warning_boo = True
                    except:
                        console.print("Não Possui Warning... \n")
                        

                    #ALTERANDO TRIBUTO DOS ITENS 
                    if warning_boo:
                        try:
                            console.print('Acessando a tela de Itens')
                            app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=60)
                            main_window = app["TFrmDadosFaturamentoPreVenda"]
                            main_window.set_focus()
                            send_keys("%i")
                            await worker_sleep(2)
                            send_keys("%g")
                            await worker_sleep(2)
                            

                            console.print("Conectando para realizar a alteração da tributação do produto... \n")
                            app = Application().connect(class_name="TFrmDadosTributacaoProdutoPreVenda", timeout=60)
                            main_window = app["TFrmDadosTributacaoProdutoPreVenda"]

                            tpanel_dados_tributacao = main_window.child_window(class_name="TPanel", found_index=1)
                            tributacao_icms_select = tpanel_dados_tributacao.child_window(class_name="TDBIComboBox", found_index=4)


                            if not item_arla:
                                console.print("Não é item Arla ajustando tributacao... \n")
                                tributacao_icms_select.click()
                                await worker_sleep(1)
                                set_combobox("||List", "061 - 061- MONOFASICO")
                            else:
                                console.print("Item Arla buscando pela aliquota do estado... \n")
                                aliquota = None
                                for item in conconfig_aliquota_icms:
                                    if cidade_cliente in item["estado"]:
                                        aliquota = item["aliquota"]
                                        break

                                if aliquota:
                                    console.print(f"A alíquota para o estado {cidade_cliente} é: {aliquota}")
                                    tributacao_icms_select.click()
                                    await worker_sleep(1)
                                    tributacao = f"000 - 000- ICMS - {aliquota}%"
                                    set_combobox("||List", tributacao)
                                else:
                                    retorno = f"Estado {cidade_cliente} não encontrado \nEtapas Executadas:\n{steps}"
                                    return RpaRetornoProcessoDTO(
                                        sucesso=False,
                                        retorno=retorno,
                                        status=RpaHistoricoStatusEnum.Falha,
                                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                                    )
                            main_window.set_focus()
                            send_keys("%o")
                        except Exception as e:
                            retorno = f"Não foi possivel corrigir a tributação do itens na Janela Faturamento de Pré Venda, erro {e} \nEtapas Executadas:\n{steps}"
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=result,
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                            )
                            


                    #SELECIONANDO O TIPO DE DOCUMENTO 
                    console.print("Processo de ajustar aliquota realizado com sucesso, adicionando a mensagem... \n")
                    try:
                        console.print("Conectando a janela de pre venda... \n")
                        app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=60)
                        main_window = app["TFrmDadosFaturamentoPreVenda"]
                        main_window.set_focus()
                        send_keys("%p")
                        await worker_sleep(2)

                        panel_TPage= main_window.child_window(class_name="TPageControl", found_index=0)
                        panel_Ttabsheet= panel_TPage.child_window(class_name="TTabSheet", found_index=0)
                        modelo_select = panel_Ttabsheet.child_window(class_name="TDBIComboBox", found_index=1)
                        modelo_select.click()
                        await worker_sleep(1)
                        set_combobox("||List", "NFe - NOTA FISCAL ELETRONICA PROPRIA - DANFE SERIE 077")
                        await worker_sleep(1)
                    except Exception as e:
                        retorno = f"Não foi possivel selecionar o modelo do documento {e}' \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=retorno,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )


                    console.print("Processo de ajustar aliquota realizado com sucesso, adicionando a mensagem... \n")
                    try:
                        console.print("Conectando a janela de pre venda... \n")
                        app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=60)
                        main_window = app["TFrmDadosFaturamentoPreVenda"]
                        main_window.set_focus()
                        send_keys("%m")
                        await worker_sleep(2)

                        mensagem_tab = pyautogui.locateOnScreen(ASSETS_PATH + "\\notas_saida\\icon_mensagem.png", confidence=0.7)
                        if mensagem_tab:
                            pyautogui.click(mensagem_tab)
                            await worker_sleep(4)
                        else:
                            retorno = f"Não foi possivel localizar o campo 'Mensagem' \nEtapas Executadas:\n{steps}"
                            return RpaRetornoProcessoDTO(
                                sucesso=False,
                                retorno=retorno,
                                status=RpaHistoricoStatusEnum.Falha,
                                tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                            )


                        panel_tab_sheet = main_window.child_window(class_name="TcxTabSheet", found_index=0)
                        field_observacao = panel_tab_sheet.child_window(class_name="TDBIMemo", found_index=0)
                        console.print(f"Mensagem a ser adicionada\n")
                        text_campo_observacao = f"Nome do Motorista: {nota.get("nomeMotorista")} - Placa: {nota.get("placaClienteCorreto")} - Quilometragem do Veículo: {nota.get("quilometragemVeiculo")}"
                        console.print(f"{text_campo_observacao}\n")
                        field_observacao.click()
                        await worker_sleep(2)
                        pyautogui.write(text_campo_observacao)
                        await worker_sleep(2)

                        console.print(f"Mensagem adicionada com sucesso, filizando o processo\n")
                        main_window.set_focus()
                        try:
                            app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=60)
                            main_window = app["TFrmDadosFaturamentoPreVenda"]
                            main_window.set_focus()
                            btn_ok = main_window.child_window(class_name="TBitBtn", found_index=1)
                            btn_ok.click()
                        except:
                            btn_ok = main_window.child_window(title="&Ok")
                            btn_ok.click()
                            
                        await worker_sleep(5)
                        try:
                            app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=10)
                            main_window = app["Confirm"]
                            main_window.set_focus()
                        except:
                            console.print('Except')
                            app = Application().connect(class_name="TMessageForm", timeout=10)
                            main_window = app["TMessageForm"]
                            main_window.set_focus()

                        btn_yes = main_window.child_window(class_name="TButton", found_index=1)
                        btn_yes.click()
                        await worker_sleep(5)

                        try:
                            app = Application().connect(class_name="TFrmDadosFaturamentoPreVenda", timeout=10)
                            main_window = app["TMessageForm"]
                        except:
                            console.print('Except')
                            app = Application().connect(class_name="TMessageForm", timeout=10)
                            main_window = app["TMessageForm"]
                        main_window.set_focus()
                        send_keys("%i")
                        await worker_sleep(15)
                    except Exception as e:
                        retorno = f"Não foi possivel adicionar a 'Mensagem' na tela de Faturamento de pre venda, erro {e} \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=retorno,
                            status=RpaHistoricoStatusEnum.Falha, tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )
                    

                    try:
                        app = Application().connect(class_name="TFrmAguarde", timeout=60)
                        main_window = app["TppPrintDialog"]
                        tpanel_btn_ok = main_window.child_window(class_name="TPanel", found_index=1)
                        btn_ok_print_screen = tpanel_btn_ok.child_window(class_name="TButton", found_index=1)
                        btn_ok_print_screen.click()
                        await worker_sleep(3)
                    except Exception as e:
                        retorno = f"Não foi encontrada a para a impressão da nova venda \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=result,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )


                    console.print(f"NAVEGANDO NA TELA DE SALVAR RELATORIO\n")
                    #INSERINDO O DIRETORIO E SALVANDO O ARQUIVO
                    try:
                        app = Application().connect(title="Salvar Saída de Impressão como")
                        main_window = app["Dialog"]
                        console.print("Tela 'Salvar' encontrada!")

                        console.print("Interagindo com a tela 'Salvar'...\n")
                        username = getpass.getuser()
                        path_to_txt = f"C:\\Users\\{username}\\Downloads\\NOVA VENDA {numero_cupom_fiscal}"

                        main_window.type_keys("%n")
                        pyautogui.write(path_to_txt)
                        await worker_sleep(1)
                        main_window.type_keys("%l")
                        console.print("Arquivo salvo com sucesso...\n")
                        await worker_sleep(8)
                    except Exception as e:
                        retorno = f"Não foi salvar o arquivo com a nova venda, erro {e} \nEtapas Executadas:\n{steps}"
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=result,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )

                    with open(f"{path_to_txt}.pdf", 'rb') as file:
                        file_bytes = io.BytesIO(file.read())

                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    desArquivo = f"NOVA VENDA {numero_cupom_fiscal}.pdf"
                    try:
                        await send_file(historico_id, desArquivo, "pdf", file_bytes, file_extension="pdf")
                        os.remove(f"{path_to_txt}.pdf")
                    except Exception as e:
                        result = f"Arquivo NOVA VENDA gerado com sucesso, porém gerou erro ao realizar o envio para o backoffice {e} - Arquivo ainda salvo na dispositivo utilizado no diretório {path_to_txt} !"
                        console.print(result, style="bold red")
                        return RpaRetornoProcessoDTO(
                            sucesso=False,
                            retorno=result,
                            status=RpaHistoricoStatusEnum.Falha,
                            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )

                    information_pop_up = await is_window_open("Information")
                    if information_pop_up["IsOpened"] == True:
                        app = Application().connect(title="Information", timeout=30)
                        main_window = app["Information"]
                        main_window.set_focus()
                        btn_ok = main_window.child_window(class_name="TButton", found_index=0)
                        btn_ok.click()


                    try:
                        app = Application().connect(class_name="TFrmProcessamentoFEe2", timeout=10)
                        main_window = app["TFrmProcessamentoFEe2"]
                        main_window.close()
                    except Exception as e:
                        console.print("Janela TFrmDadosFaturamentoPreVenda ja fechada")


                    await worker_sleep(5)
                    is_confirm_pop_up = False
                    try:
                        app = Application().connect(class_name="TFrmGerenciadorNFe2", timeout=10)
                        main_window = app["Confirm"]
                        is_confirm_pop_up = True
                    except:
                        pass


                    if is_confirm_pop_up == True:
                        msg_text = await ocr_by_class(numero_cupom_fiscal,"TFrmGerenciadorNFe2", "Confirm")
                        if 'imprimir' in msg_text.retorno.lower():
                            app = Application().connect(class_name="TFrmGerenciadorNFe2", timeout=10)
                            main_window = app["Confirm"]
                            main_window.set_focus()
                            send_keys("%n")
                    

                    try:
                        app = Application().connect(class_name="TFrmProcessamentoFEe2", timeout=10)
                        main_window = app["TFrmProcessamentoFEe2"]
                        main_window.close()
                    except Exception as e:
                        console.print("Janela TFrmDadosFaturamentoPreVenda ja fechada")

                    try:
                        app = Application().connect(class_name="TFrmPreVenda", timeout=10)
                        main_window = app["TFrmPreVenda"]
                        main_window.close()
                    except Exception as e:
                        console.print("Janela Pre venda ja fechada")
                except Exception as e:
                    retorno = f"Não foi possivel concluir o processo de pré venda {e} \nEtapas Executadas:\n{steps}"
                    return RpaRetornoProcessoDTO(
                        sucesso=False,
                        retorno=retorno,
                        status=RpaHistoricoStatusEnum.Falha, 
                        tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                    )
            else:
                retorno = f"{preenchimento_header_pre_venda.retorno} \nEtapas Executadas:\n{steps}"
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Falha, 
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                        )


        #GERAR RELATORIO FINAL 
        type_text_into_field("Rel. Boletim Caixa", app["TFrmMenuPrincipal"]["Edit"], True, "50")
        pyautogui.press("enter")
        await worker_sleep(2)
        pyautogui.press("enter")
        await worker_sleep(5)

        
        app = Application().connect(class_name="TFrmRelBoletimCaixa", timeout=60)
        main_window = app["TFrmRelBoletimCaixa"]

        tgroup_box = main_window.child_window(class_name="TGroupBox", found_index=0)
        
        dt_inicio = tgroup_box.child_window(class_name="TDBIEditDate", found_index=0)
        dt_inicio.set_edit_text(data_hoje)
        dt_final = main_window.child_window(class_name="TDBIEditDate", found_index=1)
        dt_final.set_edit_text(data_hoje)

        #SELECIONANDO A ESPECIE
        select_especie = main_window.child_window(class_name="TDBIComboBox", found_index=0)
        select_especie.click()
        set_combobox("||List", "13 - DEVOLUCAO DE VENDA")
        send_keys("%g")

        #CLICANDO NO ICONE DE IMPRIMIR 
        await worker_sleep(10)
        screen_width, screen_height = pyautogui.size()
        x = 10
        y = screen_height - 280 - (96 * 2) / .254
        pyautogui.click(x,y)

        
        #INTERAGINDO COM A TELA DE PRINT
        console.print("Interagindo com a tela 'PRINT'...\n")
        app = Application().connect(class_name="TppPrintDialog", timeout=20)
        main_window = app["TppPrintDialog"]
        tpanel_btn_ok = main_window.child_window(class_name="TPanel", found_index=1)
        btn_ok_print_screen = tpanel_btn_ok.child_window(class_name="TButton", found_index=1)
        btn_ok_print_screen.click()
        await worker_sleep(5)
        
        
        #INSERINDO O DIRETORIO E SALVANDO O ARQUIVO
        app = Application().connect(title="Salvar Saída de Impressão como")
        main_window = app["Dialog"]
        console.print("Tela 'Salvar' encontrada!")

        console.print("Interagindo com a tela 'Salvar'...\n")
        username = getpass.getuser()
        path_to_txt = f"C:\\Users\\{username}\\Downloads\\CAIXA 13 DEVOLUCAO {numero_cupom_fiscal}"

        main_window.type_keys("%n")
        pyautogui.write(path_to_txt)
        await worker_sleep(1)
        main_window.type_keys("%l")
        console.print("Arquivo salvo com sucesso...\n")
        await worker_sleep(10)
        
        txt = ""
        with open(f"{path_to_txt}.pdf", "rb") as f:
            reader = PdfReader(f)
            for p in reader.pages:
                txt += p.extract_text()
        
        console.print(f"Texto extraido {txt}...\n")
        v = re.findall(r'\b\d{1,3},\d{2}\b(?!\s*\d+\.\d+\.\d+)',txt)

        ultimo_valor = v[-1]
        penultimo_valor = v[-2]

        if ultimo_valor == penultimo_valor:
            console.print("Valores no relatorio corretamente gerados...\n")
            with open(f"{path_to_txt}.pdf", 'rb') as file:
                file_bytes = io.BytesIO(file.read())

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            desArquivo = f"CAIXA 13 DEVOLUCAO {numero_cupom_fiscal}.pdf"
            try:
                await send_file(historico_id, desArquivo, "pdf", file_bytes, file_extension="pdf")
                os.remove(f"{path_to_txt}.pdf")
                retorno = f"Processo de devolução executado com sucesso \nEtapas Executadas:\n{steps}"

                try:
                    url_retorno = nota.get("urlRetorno")
                    identificador = nota.get("identificador")

                    if url_retorno and identificador:
                        await post_partner(url_retorno, identificador, numero_nota_fiscal, valor_nota_fiscal)
                    else:
                        console.print("Não foi possivel obter o valor de urlRetorno/identificador")
                except:
                    console.print(f"Erro ao obter os dados ou enviar a requisição: {e}")
                
                return RpaRetornoProcessoDTO(
                    sucesso=True,
                    retorno=retorno,
                    status=RpaHistoricoStatusEnum.Sucesso)
            except Exception as e:
                result = f"Arquivo CAIXA 13 DEVOLUÇÃO gerado com sucesso, porém gerou erro ao realizar o envio para o backoffice {e} - Arquivo ainda salvo na dispositivo utilizado no diretório {path_to_txt} !"
                console.print(result, style="bold red")
                return RpaRetornoProcessoDTO(
                    sucesso=False,
                    retorno=result,
                    status=RpaHistoricoStatusEnum.Falha,
                    tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
                )
        else:
            os.remove(f"{path_to_txt}.pdf")
            return RpaRetornoProcessoDTO(
                sucesso=False,
                retorno=f"O valor de entrada {penultimo_valor} não esta batendo com o valor de saída {ultimo_valor}, por favor verificar. \nEtapas Executadas:\n{steps}",
                status=RpaHistoricoStatusEnum.Falha,
                tags=[RpaTagDTO(descricao=RpaTagEnum.Negocio)]
            )
        
    except Exception as ex:
        retorno = f"Erro Processo Devolução Prazo a Faturar: {str(ex)} \nEtapas Executadas:\n{steps}"
        logger.error(retorno)
        console.print(retorno, style="bold red")
        return RpaRetornoProcessoDTO(
            sucesso=False,
            retorno=retorno,
            status=RpaHistoricoStatusEnum.Falha,
            tags=[RpaTagDTO(descricao=RpaTagEnum.Tecnico)]
        )
