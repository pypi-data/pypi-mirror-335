from javaman.connexio import JManCon


class Regularitzacions:
    __slots__ = '_con'

    _url_get_regularitzacio = "/regularitzacions/ex/{regularitzacio_id}"
    _url_post_regularitzacio = "/regularitzacions/ex"
    _url_delete_regularitzacio = "/regularitzacions/{regularitzacio_id}"

    def __init__(self, con: JManCon):
        self._con = con

    def get_regularitzacio(self, p_regularitzacio_id: int):
        tmp_url = Regularitzacions._url_get_regularitzacio.format(regularitzacio_id=p_regularitzacio_id)
        req = self._con.get(url=tmp_url)
        return req.json()

    def post_regularitzacio(self, p_data: dict):
        req = self._con.post(url=self._url_post_regularitzacio, data=p_data)
        return req.json()

    def delete_regularitzacio(self,  p_regularitzacio_id: int):
        req = self._con.delete(url=self._url_delete_regularitzacio.format(regularitzacio_id=p_regularitzacio_id))
        return req.json()
