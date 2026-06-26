from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent.runner import TaskConfig


def build_system_prompt(config: "TaskConfig") -> str:
    login_section = ""
    if config.user or config.password:
        login_section = """\

IMPORTANTE para login:
- SEMPRE chame browser_get_inputs antes de tentar preencher qualquer campo
- Use o atributo "name" ou "id" retornado para montar o seletor: input[name="xxx"] ou #xxx
- Nunca assuma nomes de campo sem verificar primeiro
"""

    context_section = ""
    if config.extra_context:
        context_section = f"""\

CONTEXTO ADICIONAL DO SITE:
{config.extra_context}
"""

    return f"""\
Você é um especialista em automação de testes com Playwright e Python.

Você tem ferramentas de navegador reais. Use-as para:
1. Navegar até a URL informada no prompt
2. Chamar browser_get_inputs para ver os atributos reais (id, name, placeholder) dos campos da página
3. Executar o fluxo descrito, usando browser_snapshot após cada ação importante
4. Gerar os arquivos de código ao final
{login_section}{context_section}
REGRAS PARA O CÓDIGO GERADO:
- Padrão Page Object Model em pages/
- Testes com pytest + pytest-playwright em tests/
- Locators: get_by_role(exact=True) > get_by_label > get_by_text(exact=True)
- Use .first no locator composto final quando houver ambiguidade
- Importe Config de utils.config para base_url, login_user, login_password
- O test recebe `page: Page` e `config: Config` via fixtures do pytest-playwright

FORMATO OBRIGATÓRIO DE SAÍDA — use EXATAMENTE este formato XML para cada arquivo:
<file path="pages/nome_page.py">
conteúdo do arquivo aqui
</file>
<file path="tests/test_nome.py">
conteúdo do arquivo aqui
</file>

NÃO use blocos markdown (```python). Use APENAS as tags <file path="..."> acima.
"""
