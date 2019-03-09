from govAPI_CH import GovAPI_CH
from govAPI_UK import GovAPI_UK

class GovAPIFactory:

    @classmethod
    def create_country_gov_api(cls, country_code,cfg):
        if country_code == "CH":
            return GovAPI_CH(cfg)
        if country_code == "UK":
            return GovAPI_UK(cfg)
        return None
