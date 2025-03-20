# Nomenclator Archetype

**Nomenclator Archetype** es una librería para generar implementaciones CRUD y utilizar dependencias 
siguiendo los principios de la arquitectura **Domain-Driven Design (DDD)**.

Proporciona una estructura modular y reutilizable para proyectos futuros del ayuntamiento de l'Prat, 
incluyendo capas de Dominio, Repositorio, Servicio y Rutas.

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
  - `python-json-logger`
  - `pyjwt`

## Instalación

1. Clona el repositorio o descarga el código fuente.

```bash
git clone https://architectureBackend@dev.azure.com/architectureBackend/nomenclators_archetype/_git/nomenclators_archetype
cd nomenclators_archetype
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
pip show nomenclators-elprat
```

> mostramos la versión de la libreía instalada.

6. Actualizar la versión actual de la librería instalada.

```bash
pip install --upgrade nomenclators-elprat
```

> también puedes se utilizar la opción -U: `pip install -U nomenclators-elprat`

7. Eliminar compilación de la librería generada.

```bash
rm -rf build/* dist/* *.egg-info src/*.egg-info
```

8. Generar una nueva versión de la librería.

> Antes de realizar el paso (3), además de modificar la implementación de la librería debemos incrementar el número de versión que se encuentra en los archivos `setup.py` y `pypropject.py`.
