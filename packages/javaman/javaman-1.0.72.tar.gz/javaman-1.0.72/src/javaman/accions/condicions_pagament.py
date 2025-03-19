from javaman import JManCon


class CondicionsPagament:
    __slots__ = '_con'

    _url_get_condicions = '/condicions_pagament'
    _url_get_formes_pagament = '/formes_pagament'

    def __init__(self, con: JManCon):
        self._con = con

    def get_condicions_pagament(self):
        req = self._con.get(url=self._url_get_condicions)
        return req.json()

    def get_formes_pagament(self):
        req = self._con.get(url=self._url_get_formes_pagament)
        return req.json()
