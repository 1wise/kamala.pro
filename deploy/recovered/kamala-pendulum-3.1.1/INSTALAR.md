# Péndulo kam4 · compatibilidad 3D 3.1.1

7 de noviembre de 2026 · Créditos: https://www.alawise.es/1-s

Actualización para el emisor `stream-kam4.py` 3.1.0 adjuntado. Adapta el colector
de Excalibur y el instrumento integrado en las dos páginas del péndulo de
Kamala 2.3.0. El servicio de cristalización de cam5 conserva su configuración.

## Excalibur

Descomprimir fuera de la raíz pública y entrar en `kamala-pendulum-3.1.1`.
El colector usa únicamente la biblioteca estándar de Python 3; OpenCV sigue
ejecutándose en la Raspberry.

```bash
python3 install.py
sudo python3 install.py --install
sudo systemctl restart kamala-pendulum.service
```

La primera llamada muestra el plan. El instalador comprueba los destinos antes
de escribir, guarda los archivos sustituidos bajo
`/var/backups/kamala-pendulum/` con sus rutas completas y conserva
`/etc/sysconfig/kamala-pendulum`. Sustituye solo el instrumento y sus referencias
de CSS/JavaScript dentro de las páginas existentes; conserva el resto del texto,
menús, formularios y metadatos. Usa `--root /ruta/a/html` en ambas llamadas si la
raíz web es distinta.

Actualiza:

- `/usr/local/libexec/kamala/pendulum_feed.py`.
- `/etc/systemd/system/kamala-pendulum.service`.
- `pendulum.mjs`, `pendulum-core.mjs` y `pendulum.css` en la raíz web.
- El instrumento de `/techniques/pendulum/` y `/techniques/pendulum/live/`.

La unidad se recarga, pero el reinicio se realiza con el tercer comando.
Si el servicio no estaba habilitado, usar
`sudo systemctl enable --now kamala-pendulum.service`.

Comprobar:

```bash
sudo journalctl -u kamala-pendulum.service -n 20 --no-pager
curl -fsS https://www.kamala.pro/telemetry-pendulum/state.json | python3 -m json.tool
```

Con el emisor nuevo, el JSON debe tener `version: 2`, `sample.mode: "3d-mm"`,
`sample.dz`, `sample.vz`, `sample.fit_pct` y unidades `mm` / `mm/s`. Un
`sample: null` indica que aún no llegó una medición válida. La ruta de origen
sigue leyéndose del archivo de entorno existente; el valor inicial es
`http://10.42.0.41:8080/?out_fmt=stream`.

Abrir la página del péndulo y recargarla. El panel presenta amplitud 3D,
desplazamiento y velocidad XYZ, gráfica dedicada a Z, ajuste geométrico y CSV.
El diagrama de posición representa la proyección XY. Las coordenadas del centro
y los radios aparentes se mantienen en píxeles.

## Raspberry · corrección opcional 3.1.1

El lector admite directamente el emisor 3.1.0. Se incluye además una revisión
mínima del archivo adjunto, junto con el parche de las diferencias:

- La condición de alarma compara `des_3d_mm` con `umb_mrg_mm`; el 3.1.0 compara
  `des_2d_mm` y puede omitir movimientos solo en profundidad.
- La cola de JPEG queda limitada a 100 fotogramas, incluso sin clientes.
- El parámetro MIME `boundary` utiliza la forma estándar. El lector admite
  también la forma anterior con `--` inicial.
- El comentario sobre interpolación deja de presentar una precisión física
  como si estuviera validada.

Para revisar el parche desde una copia local del emisor 3.1.0:

```bash
patch --dry-run stream-kam4.py < raspberry/stream-kam4-3.1.1.patch
```

Para instalar la revisión en la Raspberry, desde la carpeta del paquete:

```bash
sudo cp -a --backup=numbered /opt/1wise/stream-kam4.py /opt/1wise/stream-kam4.py.before-3.1.1
sudo install -m 0755 raspberry/stream-kam4-3.1.1.py /opt/1wise/stream-kam4.py
sudo systemctl restart stream-kam4.service
```

La referencia y el contador del emisor se reinician al reiniciar ese servicio.
El colector inicia una sesión nueva si retrocede el contador, el timestamp
o cambia el protocolo. El parche conserva el seguimiento y la calibración del
archivo recibido; no constituye una validación experimental de la medida Z.

## Referencias de lectura

El archivo adjunto fija diámetro de 35 mm, distancia de referencia de 550 mm y
radio de referencia de 32 px. Calcula Z a partir del tamaño aparente y aplica
suavizado. La precisión real depende del enfoque, la detección del borde, la
calibración y el movimiento. Debe comprobarse con desplazamientos conocidos.

El ajuste geométrico es una puntuación del detector, no brillo ni una
probabilidad calibrada. Se conservan las muestras de ajuste bajo, marcadas como
no utilizables para las trazas. La pantalla distingue su umbral de amplitud del
contador recibido de la Raspberry, pues el emisor 3.1.0 todavía dispara por XY.

El colector conserva hasta 240 muestras y 20 eventos en el JSON, muestrea a
0,5 s y rota el diario privado a los 8 MiB. Sigue usando un único stream para
todos los visitantes. No requiere módulos científicos adicionales en Excalibur.
El intervalo de 2,5 s y el umbral de 15 mm provienen del emisor adjunto; si se
cambian allí, también habrá que ajustar sus referencias en el colector. La
opción `--threshold-mm` cambia únicamente la referencia visual del JSON.

`state.example.json` contiene datos sintéticos. No debe copiarse a la ruta de
telemetría pública como si fueran lecturas de producción.

## Verificación del paquete

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
node tests/test_core.mjs
```

Estas comprobaciones cubren el contrato de telemetría y la interfaz de datos.
La calibración óptica y el funcionamiento de OpenCV en la Raspberry requieren
una prueba con el equipo real.
