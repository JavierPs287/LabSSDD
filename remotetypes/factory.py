"""Needed classes to implement the Factory interface."""

import RemoteTypes as rt  # noqa: F401; pylint: disable=import-error
from remotetypes.remoteset import RemoteSet 

class Factory(rt.Factory):
    """Implementación de la fábrica para crear objetos remotos."""
    def __init__(self) -> None:
        self

    def get(self, type, identifier=None, current=None):

        if type == rt.TypeName.RSet:
            rset = RemoteSet()
            proxy = current.adapter.addWithUUID(rset)
            rsetproxy = rt.RSetPrx.checkedCast(proxy)
            return rsetproxy
        else:
            raise rt.UnknownType(type)