import json
from pathlib import Path


class GestorJSON:
    def __init__(self, archivo):
        self.archivo = Path(archivo)
        self.archivo.parent.mkdir(parents=True, exist_ok=True)

        if not self.archivo.exists():
            self.guardar([])

    def leer(self):
        try:
            with self.archivo.open("r", encoding="utf-8") as archivo:
                datos = json.load(archivo)

            return datos if isinstance(datos, list) else []

        except (json.JSONDecodeError, OSError):
            return []

    def guardar(self, datos):
        try:
            self.archivo.parent.mkdir(parents=True, exist_ok=True)

            with self.archivo.open("w", encoding="utf-8") as archivo:
                json.dump(
                    datos,
                    archivo,
                    ensure_ascii=False,
                    indent=4
                )

            return True

        except (OSError, TypeError):
            return False
