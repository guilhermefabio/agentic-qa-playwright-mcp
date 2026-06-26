from playwright.sync_api import Page, expect


class ListaAuditoriasPage:
    """
    Page Object para a tela de Lista de Auditorias.

    Após clicar em "Iniciar Auditoria", a validação verifica a abertura
    de um modal, formulário ou nova página. O método should_have_started_auditoria
    tenta múltiplos padrões — mantenha apenas o que corresponde ao sistema real.
    """

    def __init__(self, page: Page) -> None:
        self._page = page

        # Botão "Iniciar Auditoria" — tenta variações de texto e role
        self._btn_iniciar = (
            page.get_by_role("button", name="Iniciar Auditoria")
            .or_(page.get_by_role("link", name="Iniciar Auditoria"))
            .or_(page.get_by_text("Iniciar Auditoria", exact=True).first)
        )

        # ------------------------------------------------------------
        # Elementos que confirmam abertura da próxima tela/modal.
        # Ajuste para o que o sistema exibe após clicar em Iniciar Auditoria.
        # Exemplos comuns:
        #   - Modal com role="dialog"
        #   - Heading com título "Nova Auditoria" / "Iniciar Auditoria"
        #   - Formulário com campo de data ou descrição
        # ------------------------------------------------------------
        self._dialog_or_form = (
            page.get_by_role("dialog")
            .or_(page.get_by_role("heading", name="Nova Auditoria"))
            .or_(page.get_by_role("heading", name="Iniciar Auditoria"))
            .or_(page.locator("form").filter(has=page.get_by_role("button", name="Salvar")))
            .or_(page.locator("form").filter(has=page.get_by_role("button", name="Confirmar")))
            .or_(page.locator("form").filter(has=page.get_by_role("button", name="Iniciar")))
        )

    def should_be_visible(self) -> None:
        expect(self._btn_iniciar).to_be_visible()

    def iniciar_auditoria(self) -> None:
        expect(self._btn_iniciar).to_be_enabled()
        self._btn_iniciar.click()

    def should_have_started_auditoria(self) -> None:
        """
        Valida que o clique em 'Iniciar Auditoria' abriu a próxima tela.

        A assertiva usa `to_be_visible` com timeout de 10s para aguardar
        animações de abertura de modal ou carregamento de página.
        """
        expect(self._dialog_or_form).to_be_visible(timeout=10_000)
