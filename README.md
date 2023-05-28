# Real Estate Finder

***Idiomas***
- **🇪🇸 - Español**
- [🇺🇸 - English](./README.en.md)
---

Este proyecto busca crear un buscador de propiedades con el objetivo de proporcionar a los usuarios una herramienta eficiente y fácil de usar para encontrar propiedades que se ajusten a sus necesidades y preferencias.

Con este buscador, los usuarios podrán realizar búsquedas personalizadas basadas en diferentes criterios, como ubicación, tipo de propiedad, precio, tamaño, y más.


## Tecnologías Utilizadas
- **Python** será el lenguaje principal de programación para desarrollar los microservicios del backend. Además, utilizaré los siguientes paquetes y bibliotecas: `unittest` para escribir y ejecutar pruebas, `mysql-connector-python` para la conexión a la base de datos MySQL, `Pydantic` para la validación de datos y `Uvicorn` para el servidor web ASGI.
- **Docker** para facilitar la creación y despliegue de los microservicios en un entorno aislado.


## Enfoque de Desarrollo
En este proyecto, seguiré una metodología de Desarrollo Dirigido por Pruebas (TDD). Esto implica que comenzaré creando pruebas unitarias que cubran diferentes aspectos de los microservicios, desde la conexión a la base de datos hasta la respuesta esperada de los endpoints. Utilizaré PEP8 como guía de estilo de codificación para mantener un código limpio y legible.

Además, tendré en cuenta las condiciones y la información que no se debe mostrar en los endpoints, asegurándome de implementar los métodos correspondientes para manejar estos casos.