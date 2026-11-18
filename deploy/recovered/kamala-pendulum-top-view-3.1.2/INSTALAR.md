# Péndulo · vista superior XZ · 3.1.2

7 de noviembre de 2026 · Créditos: https://www.alawise.es/1-s

Actualización de la interfaz sobre el colector 3D 3.1.1 ya instalado. El panel
«Around the reference» representa el recorrido visto desde arriba:

| Elemento | Representación |
| --- | --- |
| Horizontal | Desplazamiento X, en mm |
| Vertical del dibujo | Desplazamiento Z, en mm |
| Parte superior | Z positivo: alejamiento de la cámara |
| Parte inferior | Z negativo: acercamiento a la cámara |
| Centro | Referencia de equilibrio, X = 0 y Z = 0 |
| Trayectoria | Muestras XZ con ajuste válido y una misma escala para ambos ejes |

Y se mantiene como componente vertical en las cifras y gráficas temporales.
La posición dibujada usa exclusivamente `dx` y `dz` del colector. Las coordenadas
de imagen `x`, `y`, `ax`, `ay` y los radios aparentes no determinan ese dibujo.
El panel muestra las coordenadas actuales X/Z en mm y la referencia (0,0) mm.

El círculo representa el radio de referencia en el plano XZ. La amplitud 3D
incluye también Y, por lo que puede superar su umbral aunque la proyección
XZ permanezca dentro del círculo. Si la telemetría es antigua y no incluye Z,
el panel espera datos 3D, sin sustituirlos por una trayectoria de píxeles.

## Instalar en Excalibur

Descomprimir fuera de la raíz pública y entrar en
`kamala-pendulum-top-view-3.1.2`:

```bash
python3 install.py
sudo python3 install.py --install
```

Para otra raíz web, añadir `--root /ruta/a/html` a ambas llamadas.

La primera llamada muestra el plan. El instalador actualiza los cinco archivos
web del instrumento, conserva el contenido exterior de las páginas y guarda
los archivos sustituidos bajo `/var/backups/kamala-pendulum-web/` con sus rutas
completas. Actualiza las referencias de caché a 3.1.2 y aplica `restorecon` si
está disponible.

Al terminar, recargar `/techniques/pendulum/` o
`/techniques/pendulum/live/`. No hace falta reiniciar el colector ni la cámara.

La actualización mantiene el JSON y el CSV del colector 3.1.1, con sus unidades
y las observaciones XYZ completas. El norte geográfico no se deduce de esta
proyección: los ejes corresponden al modelo de la cámara.
