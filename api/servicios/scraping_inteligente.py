"""
Scraping Inteligente Dirigido por Contexto
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict


class ScrapingInteligente:
    """Scraping dirigido basado en contexto del equipo"""

    @staticmethod
    def buscar_por_equipo(categoria: int, tipo_mantenimiento: str) -> List[Dict]:
        """Busca información específica para tipo de equipo"""
        queries = ScrapingInteligente._generar_queries(categoria, tipo_mantenimiento)
        resultados = []

        for query in queries:
            datos = ScrapingInteligente._buscar_google(query)
            resultados.extend(datos)

        return resultados[:10]

    @staticmethod
    def _generar_queries(categoria: int, tipo: str) -> List[str]:
        """Genera queries inteligentes basadas en contexto"""
        categorias_map = {
            1: "bomba industrial",
            2: "motor electrico",
            3: "compresor",
            4: "generador",
            5: "transformador",
        }

        equipo = categorias_map.get(categoria, "equipo industrial")

        return [
            f"{equipo} {tipo} manual tecnico",
            f"{equipo} tiempo reparacion promedio",
            f"{equipo} mejores practicas mantenimiento",
            f"{equipo} troubleshooting guide",
        ]

    @staticmethod
    def _buscar_google(query: str) -> List[Dict]:
        """Busca en Google y extrae resultados"""
        try:
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": "Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                resultados = []

                for item in soup.find_all("div", class_="g")[:3]:
                    titulo = item.find("h3")
                    link = item.find("a")

                    if titulo and link:
                        resultados.append(
                            {
                                "titulo": titulo.text,
                                "url": link.get("href", ""),
                                "query": query,
                            }
                        )

                return resultados
        except:
            pass

        return []

    @staticmethod
    def guardar_conocimiento(datos: List[Dict], categoria: int):
        """Guarda en base de conocimiento"""
        from api.models import BaseConocimiento

        for dato in datos:
            BaseConocimiento.objects.get_or_create(
                fuente_url=dato["url"],
                defaults={
                    "titulo": dato["titulo"],
                    "contenido": dato.get("query", ""),
                    "relevancia_score": 0.7,
                },
            )


# Instancia global
scraping_inteligente = ScrapingInteligente()
