import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from pages.auditoria_page import AuditoriaPage
from pages.lista_auditorias_page import ListaAuditoriasPage
from utils.config import Config


@pytest.fixture(scope="session")
def config() -> Config:
    return Config()


def test_iniciar_auditoria(page: Page, config: Config) -> None:
    """
    Fluxo completo: login → Auditoria → Lista de Auditorias → Iniciar Auditoria.

    O teste para após validar que o clique em 'Iniciar Auditoria' abriu
    a próxima tela (modal, formulário ou nova página). Nenhum campo é
    preenchido e nada é salvo.
    """
    # --- Login ---
    login_page = LoginPage(page)
    login_page.open(config.base_url)
    login_page.should_be_visible()
    login_page.login(config.login_user, config.login_password)

    # --- Navegação: Auditoria → Lista de Auditorias ---
    auditoria_page = AuditoriaPage(page)
    auditoria_page.acessar_auditoria()
    auditoria_page.acessar_lista_de_auditorias()

    # --- Lista de Auditorias: verificar botão e clicar ---
    lista_page = ListaAuditoriasPage(page)
    lista_page.should_be_visible()
    lista_page.iniciar_auditoria()

    # --- Validação: próxima tela abriu ---
    lista_page.should_have_started_auditoria()

    # Teste encerrado aqui — nenhum campo preenchido, nada salvo.
