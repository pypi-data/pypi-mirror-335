class Config:
    _api_key = None

    @classmethod
    def set_api_key(cls, apikey):
        cls._api_key = apikey

    @classmethod
    def get_api_key(cls):
        if cls._api_key is None:
            raise ValueError("API key is not set. Use client(apikey=...) to set it.")
        return cls._api_key

    @classmethod
    def get_link(cls):
        return "https://61rpkv4pr0.execute-api.ap-southeast-1.amazonaws.com/v1"


def client(apikey: str):
    Config.set_api_key(apikey)
