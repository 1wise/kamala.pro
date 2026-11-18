# Péndulo y windchime · actualización del capturador

Timestamp: 2026-11-16 | Version: 3.6.0
Author & Credits: https://www.alawise.es/1-s

El Site incorpora el panel, la gráfica DH y el CSV. Para recibir los cuatro
campos nuevos también debe actualizarse el capturador JSON en Excalibur. El
emisor de cámara 3.5.9 ya instalado se conserva: no ejecutar la referencia de
cámara incluida salvo como parte de una intervención independiente.

Tras extraer el ZIP, comprobar sin instalar:

    python3 install.py --root /var/www/kamala.pro/html
    python3 tests/test_protocol.py
    python3 tests/test_wind.py

Instalar con copia de seguridad y recargar el servicio:

    sudo python3 install.py --root /var/www/kamala.pro/html --install
    sudo systemctl restart kamala-pendulum.service

El instalador conserva la URL de origen existente y no modifica el contador
ni el algoritmo del emisor. Los archivos anteriores quedan en la ruta de
copia de seguridad que muestra el instalador. La actualización del capturador
publica JSON version 3, compatible con muestras antiguas sin datos de viento.

Para leer el JSON desde el dominio del Site, incorporar las cabeceras de
sites-telemetry-cors.conf en las ubicaciones JSON existentes, validar con
nginx -t y recargar Nginx. Las cabeceras no arrancan la cámara ni el capturador.
El emisor usa el indicador óptico para suprimir alarmas durante turbulencia;
no transmite una velocidad del viento calibrada en m/s.

El CSV conserva XYZ y añade inclinación, DH, turbulencia, factor, umbral XY
estimado y supresión. Los campos de viento quedan vacíos con emisores antiguos.
