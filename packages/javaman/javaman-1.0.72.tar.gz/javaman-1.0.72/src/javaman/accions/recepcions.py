from javaman.connexio import JManCon


class Recepcions:
    __slots__ = '_con'

    _url_proveidors = '/recepcions/proveidors'
    _url_proveidor = '/recepcions/proveidors/{proveidor_id}'
    _url_proveidor_articles = '/recepcions/proveidors/{proveidor_id}/articles'
    _url_proveidor_comanda = '/recepcions/proveidors/{proveidor_id}/comandes_compra'
    _url_proveidor_comanda_art = '/recepcions/proveidors/{proveidor_id}/comandes_compra?article_atribut_id={article_atribut_id}'

    _url_post_recepcions = '/recepcions'
    _url_post_unitat_logistica = '/recepcions/{recepcio_id}/unitat_logistica'
    _url_post_unitat_logistica_mag = '/recepcions/{recepcio_id}/magatzem/{magatzem_id}/unitat_logistica'
    _url_post_unitat_logistica_mag_com = '/recepcions/{recepcio_id}/comanda/{comanda_compra_id}/magatzem/{magatzem_id}/unitat_logistica'
    _url_post_finalitzar = '/recepcions/{recepcio_id}/finalitzar'


    def __init__(self, con: JManCon):
        self._con = con

    def list_proveidors(self):
        res = self._con.get(url=self._url_proveidors)
        return res.json()

    def get_proveidor(self, proveidor_id: int):
        res = self._con.get(url=self._url_proveidor.format(proveidor_id=str(proveidor_id)))
        return res.json()

    def get_comandes_compra(self, proveidor_id: int, article_atribut_id: int = None):
        if article_atribut_id is None:
            res = self._con.get(url=self._url_proveidor_comanda.format(proveidor_id=str(proveidor_id)))
        else:
            res = self._con.get(url=self._url_proveidor_comanda_art.format(proveidor_id=str(proveidor_id), article_atribut_id=article_atribut_id))
        return res.json()

    def get_articles(self, proveidor_id: int):
        res = self._con.get(url=self._url_proveidor_articles.format(proveidor_id=str(proveidor_id)))
        return res.json()

    def post_recepcio(self, recepcio: dict):
        res = self._con.post(url=self._url_post_recepcions, data=recepcio)
        return res.json()

    def post_unitat_logistica(self, recepcio_id: int,  unitat_logistica: dict, magatzem_id: int = None, comanda_compra_id: int = None):
        if magatzem_id is None and comanda_compra_id is None:
            tmp_url = self._url_post_unitat_logistica.format(recepcio_id=recepcio_id)
        elif comanda_compra_id is None and magatzem_id is not None:
            tmp_url = self._url_post_unitat_logistica_mag.format(recepcio_id=recepcio_id, magatzem_id=magatzem_id)
        else:
            tmp_url = self._url_post_unitat_logistica_mag_com.format(recepcio_id=recepcio_id, magatzem_id=magatzem_id, comanda_compra_id=comanda_compra_id)

        res = self._con.post(url=tmp_url, data=unitat_logistica)
        return res.json()

    def post_finalitzar(self, recepcio_id: int, dades_albara: dict):
        res = self._con.post(url=self._url_post_finalitzar.format(recepcio_id=recepcio_id), data=dades_albara)
        return res.json()
