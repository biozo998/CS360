from selenium.webdriver.common.by import By

RELATORIOS = {
    "projetos": {
        "url": "https://www.psofficeapp.com.br/csintegra/core/relatorios/manager.do?_sctx=2084849296480591325&controller=com.mcfox.core.controller.ReportController&state=SingleReport&rel_id=T_bel__Projetos_-_Gerente_2&relSearch=&Find_params=controller%253Dcom.mcfox.core.controller.ReportController%2526_sctx%253D2084849296480591325%2526state%253DList&Find_encoding=u",
        "acoes": [
            {"type": "select", "selector": (By.NAME, "isqltipo"), "value": "csv"},
            {"type": "click", "selector": (By.ID, "button_Execute")}
        ]
    }
}