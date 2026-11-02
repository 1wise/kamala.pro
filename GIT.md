# Kamala 2.1.1 — proyecto para Git

Timestamp: 2026-11-02 | Version: 2.1.1
Author and Credits: https://www.alawise.es/1-s

El ZIP Git contiene fuentes, recursos y páginas construidas. Omite .git,
credenciales y paquetes binarios de entregas anteriores. Descomprimir y entrar
en la carpeta kamala-pro.

| Ruta | Contenido |
| --- | --- |
| src/ | Plantillas, datos editoriales, módulos y las dos monedas en relieve |
| dist/ | Las 133 páginas públicas y recursos base; npm run build restaura las copias de imágenes originales |
| scripts/ | Construcción del sitio y del paquete de Excalibur |
| tests/ | Comprobaciones de páginas, aplicaciones e instalador |
| deploy/ | PHP de envío y entropía, ejemplos de configuración e instalador |
| legacy/bior/ | Copia de referencia de Drive, con credenciales retiradas |
| releases/ | Los scripts crean aquí los paquetes de instalación; su historial binario se omite del ZIP de fuentes |
| package.json y package-lock.json | Dependencias y versiones reproducibles |
| .openai/hosting.json | Identidad y configuración de publicación de Sites |

## Primera subida

Crear primero un repositorio vacío en el proveedor elegido. Desde la carpeta
descomprimida:

```bash
git init -b main
git add .
git commit -m "Kamala 2.1.1: dados con puntos y carga de imagen AstroApp"
```

Añadir la URL real del repositorio como remoto origin y subir la rama:

```bash
git remote add origin URL_DEL_REPOSITORIO
git push -u origin main
```

URL_DEL_REPOSITORIO es un marcador: sustituirlo por la URL HTTPS o SSH que
facilite el proveedor. Si se usa un clon ya existente, copiar los archivos allí
y conservar sus remotos y su historial.

## Reconstruir y preparar Excalibur

```bash
npm ci
npm run build
python3 tests/page-contracts.py
node tests/chance-variants.mjs
python3 tests/install-v2.py
python3 scripts/package-excalibur.py
python3 scripts/package-downloads.py
```

Se genera releases/kamala-pro-2.1.1-excalibur.zip. Descomprimir ese paquete
fuera de la carpeta pública del servidor y ejecutar:

```bash
sudo python3 tools/install_v2.py
```

La instalación conserva bior/, el formulario de contacto y la configuración
activa de correo y AstroApp. Véase deploy/site-update/INSTALAR.md.

El segundo script prepara dist/downloads/ para la publicación de Sites:
ZIP de Excalibur, ZIP de fuentes, sus sumas SHA-256 y una página de descarga.
Ese directorio generado se omite del propio ZIP de fuentes y del paquete de
Excalibur. El laboratorio portátil tiene el enlace estable assets/keys-lab.html.
Las imágenes originales se incluyen una sola vez en src/assets/. Ejecutar
npm ci y npm run build antes de desplegar el proyecto extraído; la construcción
recrea las copias de recursos bajo dist/assets/.

Los secretos se mantienen en Excalibur. .gitignore excluye las configuraciones
activas, archivos de claves privadas, registros, consultas generadas y
dependencias instaladas. Los ejemplos de configuración sí forman parte del
proyecto. La copia legacy/ procede de Drive y no certifica el estado actual
de los PHP del servidor.
