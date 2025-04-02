# xtekamx

Travel local agency at San Luis Potosi.

## Requisitos previos

Antes de comenzar, asegúrate de tener lo siguiente instalado en tu sistema:

1. **Python** (versión 3.8 o superior)
2. **pip** (el gestor de paquetes de Python)
3. **Git** (para clonar el repositorio)

## Instalación

Sigue estos pasos para instalar y ejecutar la aplicación localmente:

### 1. Instalar Python
1. Descarga Python desde su [sitio oficial](https://www.python.org/downloads/).
2. Durante la instalación, asegúrate de marcar la opción **"Add Python to PATH"**.
3. Verifica la instalación ejecutando en la terminal:
   ```bash
   python --version
   ```
   o
   ```bash
   python3 --version
   ```

### 2. Clonar el repositorio
Clona este repositorio en tu máquina local:
```bash
git clone https://github.com/matavaresr/xtekamx.git
cd xtekamx
```

### 3. Crear un entorno virtual
Crea un entorno virtual para aislar las dependencias del proyecto:
```bash
python -m venv env
```

Activa el entorno virtual:
- En Windows:
  ```bash
  .\env\Scripts\activate
  ```
- En macOS/Linux:
  ```bash
  source env/bin/activate
  ```

### 4. Instalar Django y otras dependencias
Instala Django y las dependencias del proyecto usando `pip`:
```bash
pip install -r requirements.txt
```

Si no existe un archivo `requirements.txt`, instala Django manualmente:
```bash
pip install django
```

### 5. Configurar la base de datos
Aplica las migraciones para configurar la base de datos:
```bash
python manage.py migrate
```

### 6. Ejecutar el servidor de desarrollo
Inicia el servidor de desarrollo de Django:
```bash
python manage.py runserver
```

Abre tu navegador y ve a [http://127.0.0.1:8000/](http://127.0.0.1:8000/) para ver la aplicación en funcionamiento.

## Estructura del proyecto

- **apps/**: Contiene las aplicaciones de Django.
- **templates/**: Archivos HTML para las vistas.
- **static/**: Archivos estáticos como CSS y JavaScript.
- **manage.py**: Archivo principal para ejecutar comandos de Django.

## Comandos útiles

- Crear un superusuario para acceder al panel de administración:
  ```bash
  python manage.py createsuperuser
  ```
- Aplicar nuevas migraciones:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```
- Salir del entorno virtual:
  ```bash
  deactivate
  ```

## Contribuir
Si deseas contribuir al proyecto, por favor abre un issue o envía un pull request.

## Licencia
Este proyecto está bajo la licencia [MIT](LICENSE).

## Disclaimer

Se recomienda utilizar **Visual Studio Code** como editor de código para trabajar en este proyecto. Visual Studio Code ofrece una experiencia de desarrollo optimizada con las siguientes ventajas:

- **Extensiones útiles**: Instala extensiones como *Python* y *Django* para facilitar el desarrollo.
- **Terminal integrada**: Ejecuta comandos directamente desde el editor.
- **Depuración**: Configura y depura tu aplicación de manera sencilla.

Puedes descargar Visual Studio Code desde su [sitio oficial](https://code.visualstudio.com/).
