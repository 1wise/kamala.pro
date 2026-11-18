# Zhouyi · notas breves y texto chino

Version 1.1.0 · Timestamp: 2026-11-07
Author & Credits: https://www.alawise.es/1-s

La versión 1.0.0 añadía un enlace externo. Esta actualización incorpora en la
propia página las sentencias de los 64 hexagramas del Zhouyi (周易), con el texto
chino clásico y una versión breve en inglés identificada como nota editorial
de Kamala. El idioma de la interfaz existente sigue siendo el inglés.

Las notas aparecen junto a los hexagramas principal y resultante al completar
las seis líneas. Si ambos coinciden, aparece una sola nota. Reset las oculta y
borra el contenido de la tirada anterior. También funciona con Cast all six lines.

Cada nota enlaza a su texto chino en Wikisource. El enlace al Chinese Text
Project permanece como lectura adicional. La atribución distingue el texto
clásico de la explicación editorial; los detalles constan en SOURCES.md.

## Instalación en Excalibur

Descomprimir fuera de la carpeta pública y entrar en el paquete:

```bash
unzip kamala-yijing-reference-1.1.0.zip
cd kamala-yijing-reference-1.1.0
python3 install.py
sudo python3 install.py --install
```

El primer comando de Python revisa todos los destinos sin modificarlos.
El instalador usa `/var/www/kamala.pro/html`. Para otra raíz, añadir
`--root /ruta/al/html` a ambos comandos de Python.

El instalador actualiza estas cuatro páginas conservando su contenido:

- `/apps/coins/`
- `/apps/yijing/`
- `/techniques/coins/`
- `/techniques/yijing/`

Añade `yijing-reference.mjs`, `yijing-readings.mjs` y `yijing-readings.css` a la
raíz pública. Las referencias a los archivos llevan `v=1.1.0` para cargar la
actualización. Guarda una copia de los archivos existentes en
`/var/backups/kamala-yijing-reference/` e imprime su ubicación al terminar.

Recargar `/apps/yijing/` y completar una tirada. Debajo de las figuras deben
aparecer **Zhouyi 周易 · Book of Changes**, el original chino y la nota breve.
Para una comprobación rápida, seleccionar **Browser only** y pulsar
**Cast all six lines**. Reset debe volver a ocultar las notas.

Este paquete se instala sobre la web existente. El daemon no necesita reinicio.

## Archivos y licencias

- `install.py`: instalación con validación previa, escritura atómica por archivo
  y copias de seguridad.
- `yijing-reference.mjs`: muestra las notas de los hexagramas ya calculados por
  la aplicación.
- `yijing-readings.mjs`: datos locales para los 64 hexagramas.
- `yijing-readings.css`: presentación adaptable a móvil.
- `SOURCES.md` y `SOURCES.json`: atribución, referencias y registro de fuentes.
- `LICENSE`: licencia GPL-3.0 del código.
- `LICENSE-DATA.txt`: licencia y atribución de los textos y notas.
- `SHA256SUMS`: comprobaciones de integridad del paquete.
