"""Needed classes to implement the Factory interface."""

import json
import Ice
import RemoteTypes as rt  # noqa: F401; pylint: disable=import-error
from remotetypes.remoteset import RemoteSet
import os


class Factory(rt.Factory):
    """Skeleton for the Factory implementation."""
    def __init__(self) -> None:
        # Diccionario para almacenar proxies, con clave como una tupla (name, category)
        self.objetosExistentes = {}
        self.objetosLocales = {}  # Aquí almacenaremos los objetos locales

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
                self.obtener_remoteset_desde_proxy(self.objetosExistentes[key], current)
                return self.objetosExistentes[key]

            # Crear un nuevo objeto y agregarlo al adaptador
            rset = RemoteSet()
            if current:
                if identity:
                    proxy = current.adapter.add(rset, identity)
                else:
                    proxy = current.adapter.addWithUUID(rset)
                    identity = proxy.ice_getIdentity()
                    key = (identity.name, identity.category)

                # Guardar el proxy en el diccionario
                rsetproxy = rt.RSetPrx.checkedCast(proxy)
                if not rsetproxy:
                    raise RuntimeError("Error al convertir el proxy a RSetPrx.")
                self.objetosExistentes[key] = rsetproxy
                self.objetosLocales[key] = rset  # Guardamos una copia local

                self.obtener_remoteset_desde_proxy(rsetproxy, current)

                return rsetproxy
            else:
                raise RuntimeError("No se puede agregar al adaptador: current es None")
        else:
            raise rt.UnknownType(type)

    def obtener_remoteset_desde_proxy(self, proxy, current):
        """Convertir el proxy al tipo específico RSetPrx."""
        if not proxy:
            raise TypeError("El proxy no es válido.")

        proxy = rt.RSetPrx.checkedCast(proxy)
        if not proxy:
            raise TypeError(f"El proxy no es de tipo RSetPrx: {type(proxy)}")

        # Obtener la identidad del proxy
        identity = proxy.ice_getIdentity()
        if not identity:
            raise ValueError("El proxy no tiene una identidad válida.")

        # Buscar el objeto en el adaptador
        objeto = current.adapter.find(identity)
        if not objeto:
            raise ValueError("No se encontró el objeto asociado al proxy.")

        # Verificar el tipo del objeto encontrado
        if isinstance(objeto, RemoteSet):
            return objeto
        else:
            raise ValueError("El objeto asociado no es de tipo RemoteSet.")

    def guardar_estado(self, archivo: str):
        """Guardar el estado de todos los RemoteSets en un archivo JSON."""
        estado = {}
        for key, rset in self.objetosLocales.items():
            try:
                # Guardamos los elementos de cada RemoteSet
                estado[str(key)] = list(rset._storage_)
            except Exception as e:
                print(f"Error al guardar el estado para {key}: {e}")

        # Guardar el estado en el archivo JSON
        with open(archivo, 'w') as f:
            json.dump(estado, f, indent=4)

        print(f"Estado guardado en {archivo}")


    def cargar_estado(self, archivo: str, current=None):
        """Cargar el estado de los RemoteSets desde un archivo JSON y restaurarlos en el adaptador."""
        try:
            with open(archivo, 'r') as f:
                estado = json.load(f)

            for key, elementos in estado.items():
                identity_name, identity_category = eval(key)  # Convertir la clave de nuevo a tupla

                # Crear el RemoteSet
                rset = RemoteSet()
                for item in elementos:
                    rset.add(item)

                # Crear la identidad para el RemoteSet
                identity = Ice.Identity(name=identity_name, category=identity_category)

                # Si current está disponible, agregarlo al adaptador
                if current:
                    proxy = current.adapter.add(rset, identity)

                    # Convertir el proxy al tipo adecuado y agregarlo a los diccionarios
                    rsetproxy = rt.RSetPrx.checkedCast(proxy)
                    if not rsetproxy:
                        raise RuntimeError("Error al convertir el proxy a RSetPrx.")
                    self.objetosExistentes[(identity_name, identity_category)] = rsetproxy
                    self.objetosLocales[(identity_name, identity_category)] = rset

                else:
                    # Si current no está disponible, crear un proxy sin identidad específica
                    proxy = current.adapter.addWithUUID(rset)

                    # Obtener la identidad generada del proxy
                    identity = proxy.ice_getIdentity()

                    # Convertir el proxy al tipo adecuado y agregarlo a los diccionarios
                    rsetproxy = rt.RSetPrx.checkedCast(proxy)
                    if not rsetproxy:
                        raise RuntimeError("Error al convertir el proxy a RSetPrx.")
                    self.objetosExistentes[(identity.name, identity.category)] = rsetproxy
                    self.objetosLocales[(identity.name, identity.category)] = rset

            # Eliminar el archivo después de cargar el estado
            os.remove(archivo)
            print(f"Estado cargado desde {archivo} y archivo eliminado.")
        
        except Exception as e:
            print(f"Error al cargar el estado desde {archivo}: {e}")

