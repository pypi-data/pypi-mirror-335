from javaman.connexio import JManCon


class Proveidors:
    __slots__ = '_con'

    _url_list_proveidors = '/proveidors/llista'
    _url_proveidors = '/proveidors'
    _url_get_proveidor = '/proveidors/{proveidor_id}'
    _url_put_proveidor = '/proveidors/{proveidor_id}'

    def __init__(self, con: JManCon):
        self._con = con

    def list_proveidors(self):
        res = self._con.get(url=self._url_list_proveidors)
        return res.json()

    def get_proveidor_by_nif(self, p_nif: str):
        res = self._con.get(url=self._url_proveidors+'?nif='+p_nif)
        return res.json()

    def get_proveidor(self, proveidor_id: int):
        res = self._con.get(url=self._url_get_proveidor.format(proveidor_id=str(proveidor_id)))
        return res.json()

    def post_proveidor(self, proveidor: dict):
        res = self._con.post(url=self._url_proveidors, data=proveidor)
        return res.json()

    def put_proveidor(self, proveidor_id: int, proveidor: dict):
        res = self._con.post(url=self._url_put_proveidor.format(proveidor_id=str(proveidor_id)), data=proveidor)
        return res.json()
