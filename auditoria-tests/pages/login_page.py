from playwright.sync_api import Page, expect


class LoginPage:
    """
    Page Object para a tela de login.

    Seletores mapeados via Playwright MCP — ajuste os valores entre
    colchetes abaixo caso os IDs reais do sistema sejam diferentes.
    Use o MCP para inspecionar: npx @playwright/mcp@latest
    """

    # -----------------------------------------------------------------
    # Seletores — ajuste conforme inspeção real do sistema
    # -----------------------------------------------------------------
    # ASP.NET WebForms costuma gerar IDs como:
    #   ContentPlaceHolder1_txtUsuario  /  ctl00_txtUsuario  /  txtUsuario
    # Use o Playwright MCP ou DevTools (F12) para confirmar.
    _USERNAME_SELECTORS = [
        'input[id$="txtUsuario"]',
        'input[id$="txtLogin"]',
        'input[id$="txtUser"]',
        'input[name$="txtUsuario"]',
        'input[name$="txtLogin"]',
    ]
    _PASSWORD_SELECTORS = [
        'input[type="password"]',
        'input[id$="txtSenha"]',
        'input[id$="txtPassword"]',
    ]
    _SUBMIT_SELECTORS = [
        'input[type="submit"]',
        'button[type="submit"]',
        'input[id$="btnEntrar"]',
        'input[id$="btnLogin"]',
    ]

    def __init__(self, page: Page) -> None:
        self._page = page

        # Tenta seletores robustos por papel semântico primeiro
        self._username = page.get_by_role("textbox", name="Usuário") \
            .or_(page.get_by_label("Usuário")) \
            .or_(page.get_by_label("Login")) \
            .or_(page.locator(", ".join(self._USERNAME_SELECTORS)).first)

        self._password = page.get_by_role("textbox", name="Senha") \
            .or_(page.get_by_label("Senha")) \
            .or_(page.get_by_label("Password")) \
            .or_(page.locator(", ".join(self._PASSWORD_SELECTORS)).first)

        self._submit = page.get_by_role("button", name="Entrar") \
            .or_(page.get_by_role("button", name="Login")) \
            .or_(page.get_by_role("button", name="Acessar")) \
            .or_(page.locator(", ".join(self._SUBMIT_SELECTORS)).first)

    def open(self, url: str) -> None:
        self._page.goto(url)

    def should_be_visible(self) -> None:
        expect(self._username).to_be_visible()
        expect(self._password).to_be_visible()
        expect(self._submit).to_be_visible()

    def login(self, username: str, password: str) -> None:
        self._username.fill(username)
        self._password.fill(password)
        self._submit.click()
