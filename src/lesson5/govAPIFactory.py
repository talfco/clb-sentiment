from govAPI_CH import GovAPI_CH

class GovAPIFactory:

    @classmethod
    def create_country_gov_api(cls, country_code,cfg):
        if country_code == "CH":
            return GovAPI_CH(cfg)
        return None
