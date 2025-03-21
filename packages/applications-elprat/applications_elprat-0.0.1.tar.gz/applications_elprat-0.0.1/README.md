# Nomenclator Archetype

**Applications Archetype** es una librería para utilizar en el desarrollo de aplicaciones.

Proporciona clases de métodos reutilizables para proyectos futuros del ayuntamiento de l'Prat.

## Características

- Basado en los principios de Domain-Driven Design.
- Generación automática de CRUD utilizando comandos personalizados.
- Plantillas configurables con Jinja2 para adaptarse a diferentes necesidades.
- Integración con FastAPI para generación de rutas RESTful.
- Extensible para diferentes tipos de almacenamiento y lógica de negocio.

## Requisitos

- Python 3.9.20 o superior.
- Dependencias:
  - `click`
  - `jinja2`
  - `fastapi`
  - `SQLAlchemy`
  - `pytest` 
  - `virtualenv`
  - `jsonschema`

## Instalación

1. Clona el repositorio o descarga el código fuente.

```bash
git clone https://architectureBackend@dev.azure.com/architectureBackend/applications_archetype/_git/applications_archetype
cd applicationss_archetype
```

2. Verificamos que tenemos los paquetes necesarios para compilar la librería.

```bash
python -c "from setuptools import find_packages; print(find_packages())"
```

3. Compilar el código fuente de la biblioteca.

```bash
python -m build
```

4. Instala la librería utilizando `pip`.

```bash
  pip install .
```

5. Verificamos la versión de la library instalada.

```bash
pip show applications-elprat
```

> mostramos la versión de la libreía instalada.

6. Actualizar la versión actual de la librería instalada.

```bash
pip install --upgrade applications-elprat
```

> también puedes se utilizar la opción -U: `pip install -U applications-elprat`

7. Eliminar compilación de la librería generada.

```bash
rm -rf build/* dist/* *.egg-info src/*.egg-info
```

8. Generar una nueva versión de la librería.

> Antes de realizar el paso (3), además de modificar la implementación de la librería debemos incrementar el número de versión que se encuentra en los archivos `setup.py` y `pypropject.py`.
