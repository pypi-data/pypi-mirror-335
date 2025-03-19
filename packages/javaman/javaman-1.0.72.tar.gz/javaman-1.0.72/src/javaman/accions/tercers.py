from javaman.connexio import JManCon


class Tercers:
    __slots__ = '_con'

    _url_get_tercers = '/tercer'
    _url_get_tercers_parametres = '/tercer/{id_tercer}/parametres'
    _url_get_tercers_anotacions = '/tercer/{id_tercer}/anotacions'
    _url_get_tercers_bancs = '/tercers_bancs'
    _url_get_tercer_banc = '/tercers_bancs/{tercer_banc_id}'

    def __init__(self, con: JManCon):
        self._con = con

    def get_tercer(self, p_tercer: int):
        req = self._con.get(url=self._url_get_tercers+'/'+str(p_tercer))
        return req.json()

    def get_tercer_by_nif(self, p_nif: str):
        req = self._con.get(url=self._url_get_tercers+'?nif='+p_nif)
        return req.json()

    def get_tercer_parametres(self, p_tercer: int):
        req = self._con.get(url=Tercers._url_get_tercers_parametres.format(id_tercer=p_tercer))
        return req.json()

    def get_tercer_anotacions(self, p_tercer: int):
        req = self._con.get(url=Tercers._url_get_tercers_anotacions.format(id_tercer=p_tercer))
        return req.json()

    def get_tercers_bancs_by_id(self, p_tercer_banc_id: int):
        req = self._con.get(url=Tercers._url_get_tercer_banc.format(tercer_banc_id=p_tercer_banc_id))
        return req.json()

    def get_tercers_bancs_by_tercer_id(self, p_tercer_id: int):
        req = self._con.get(url=Tercers._url_get_tercers_bancs+'?tercer_id='+str(p_tercer_id))
        return req.json()
