from playwright.sync_api import Page, expect


class AuditoriaPage:
    """
    Page Object para a navegação pelo menu principal após o login.

    Padrões suportados:
      - Menu de navegação horizontal/vertical com links de texto
      - Menu suspenso (dropdown) com item "Auditoria"
      - Sidebar com item de menu

    Ajuste os seletores caso o sistema use outro padrão de navegação.
    """

    def __init__(self, page: Page) -> None:
        self._page = page

        # Menu principal "Auditoria" — tenta variações de texto e role
        self._menu_auditoria = (
            page.get_by_role("link", name="Auditoria")
            .or_(page.get_by_role("menuitem", name="Auditoria"))
            .or_(page.get_by_text("Auditoria", exact=True).first)
        )

        # Submenu "Lista de Auditorias"
        self._menu_lista_auditorias = (
            page.get_by_role("link", name="Lista de Auditorias")
            .or_(page.get_by_role("menuitem", name="Lista de Auditorias"))
            .or_(page.get_by_text("Lista de Auditorias", exact=True).first)
        )

    def acessar_auditoria(self) -> None:
        expect(self._menu_auditoria).to_be_visible()
        self._menu_auditoria.click()

    def acessar_lista_de_auditorias(self) -> None:
        expect(self._menu_lista_auditorias).to_be_visible()
        self._menu_lista_auditorias.click()
