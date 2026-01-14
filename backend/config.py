from selenium.webdriver.common.by import By

RELATORIOS = {
    "projetos": {
        "url": "https://pso-csintegra.jexperts.cloud/csintegra/core/relatorios/manager.do",
        "acoes": [
            {"type": "select", "selector": (By.NAME, "isqltipo"), "value": "csv"},
            {"type": "click", "selector": (By.ID, "button_execute")}
        ]
    }
}