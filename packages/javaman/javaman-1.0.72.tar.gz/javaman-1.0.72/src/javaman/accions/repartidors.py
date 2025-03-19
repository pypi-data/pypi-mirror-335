from javaman.connexio import JManCon


class Repartidors:
    __slots__ = '_con'

    _url_get_repartiors = '/repartidors/ex'
    _url_get_repartior = '/repartidors/ex/{id_rep}'
    _url_get_repartior_zones = '/repartidors/{id_rep}/zones'
    _url_get_repartior_zona = '/repartidors/{id_rep}/zona'

    def __init__(self, con: JManCon):
        self._con = con

    def get_repartidors(self):
        req = self._con.get(url=Repartidors._url_get_repartiors)
        return req.json()

    def get_repartidor(self, p_repartidor: int):
        req = self._con.get(url=Repartidors._url_get_repartior.format(id_rep=p_repartidor))
        return req.json()

    def get_repartidor_zones(self, p_repartidor: int):
        tmp_url = Repartidors._url_get_repartior_zones.format(id_rep=p_repartidor)
        req = self._con.get(url=tmp_url)
        return req.json()

    def get_repartidor_zona_by_cp(self, p_repartidor: int, p_pais_codi: str, p_codi_postal: str):
        tmp_url = Repartidors._url_get_repartior_zona.format(id_rep=p_repartidor)
        tmp_url += "?pais_codi=" + p_pais_codi + "&cpostal=" + p_codi_postal
        req = self._con.get(url=tmp_url)
        return req.json()
