"""Needed classes to implement the Factory interface."""

import json
import RemoteTypes as rt  # noqa: F401; pylint: disable=import-error
from remotetypes.remoteset import RemoteSet
import Ice

class Factory(rt.Factory):
    """Skeleton for the Factory implementation."""
    def __init__(self) -> None:
        # Diccionario para almacenar proxies, con clave como una tupla (name, category)
        self.objetosExistentes = {}

    def get(self, type, identifier=None, current=None):
        if type == rt.TypeName.RSet:
            # Crear una clave única para el objeto
            if identifier:
                identity = Ice.Identity(name=identifier, category="")
            else:
                identity = None

            # Revisar si el objeto ya existe
            key = (identity.name if identity else None, identity.category if identity else None)
            if key in self.objetosExistentes:
                return self.objetosExistentes[key]

            # Crear un nuevo objeto y agregarlo al adaptador
            rset = RemoteSet()
            if identity:
                proxy = current.adapter.add(rset, identity)
            else:
                proxy = current.adapter.addWithUUID(rset)
                identity = proxy.ice_getIdentity()
                key = (identity.name, identity.category)

            # Guardar el proxy en el diccionario
            rsetproxy = rt.RSetPrx.checkedCast(proxy)
            self.objetosExistentes[key] = rsetproxy

            return rsetproxy
        else:
            raise rt.UnknownType(type)