import requests
from bs4 import BeautifulSoup
import re


class ServicioScraping:
    """Servicio de web scraping para recolección de datos de entrenamiento"""

    @staticmethod
    def buscar_web(consulta: str, max_resultados: int = 10) -> list:
        """
        Busca información en la web usando DuckDuckGo

        Args:
            consulta: Término de búsqueda
            max_resultados: Máximo de resultados a retornar

        Returns:
            Lista de diccionarios con resultados
        """
        resultados = []

        try:
            # Búsqueda con DuckDuckGo (no requiere API key)
            url = f"https://html.duckduckgo.com/html/?q={consulta}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }

            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")

            # Extraer resultados
            for resultado in soup.select(".result")[:max_resultados]:
                titulo = resultado.select_one(".result__title")
                snippet = resultado.select_one(".result__snippet")
                enlace = resultado.select_one("a.result__a")

                if titulo and enlace:
                    url_destino = enlace.get("href")
                    titulo_texto = titulo.get_text(strip=True)

                    # Navegar al link real para extraer contenido profundo
                    contenido_profundo = ServicioScraping.visitar_sitio(url_destino)

                    # Si falló la visita, usar el snippet como fallback
                    contenido_final = (
                        contenido_profundo
                        if contenido_profundo
                        else snippet.get_text(strip=True)
                    )

                    resultados.append(
                        {
                            "titulo": titulo_texto,
                            "url": url_destino,
                            "descripcion": (
                                snippet.get_text(strip=True) if snippet else ""
                            ),
                            "contenido": contenido_final,
                            "features": ServicioScraping.extraer_features(
                                contenido_final
                            ),
                        }
                    )

        except Exception as e:
            return [{"error": str(e)}]

        return resultados

    @staticmethod
    def visitar_sitio(url: str) -> str:
        """
        Navega a la URL y extrae el texto principal de los párrafos.
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            resp = requests.get(url, headers=headers, timeout=4)
            if resp.status_code == 200:
                s = BeautifulSoup(resp.text, "html.parser")
                # Extraer parrafos para tener texto real
                parrafos = s.find_all("p")
                texto_completo = "\n".join([p.get_text() for p in parrafos])

                # Limitar tamaño para no saturar BD
                return texto_completo[:5000] if texto_completo else None
        except:
            return None
        return None

    @staticmethod
    def extraer_features(texto: str) -> dict:
        """
        Extrae características numéricas del texto para ML

        Args:
            texto: Texto a analizar

        Returns:
            Diccionario con 10 features numéricas
        """
        palabras = texto.split()

        return {
            "longitud": len(texto),
            "palabras": len(palabras),
            "mayusculas": sum(1 for c in texto if c.isupper()),
            "numeros": sum(1 for c in texto if c.isdigit()),
            "puntuacion": sum(1 for c in texto if c in ".,;:!?"),
            "espacios": texto.count(" "),
            "lineas": texto.count("\n"),
            "densidad_palabras": len(palabras) / max(len(texto), 1),
            "promedio_longitud_palabra": sum(len(w) for w in palabras)
            / max(len(palabras), 1),
            "caracteres_especiales": len(re.findall(r"[^a-zA-Z0-9\s]", texto)),
        }
