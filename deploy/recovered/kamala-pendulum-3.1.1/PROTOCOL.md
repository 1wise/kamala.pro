# Cabecera del péndulo 3D

Timestamp: 2026-11-07 · Version: 3.1.1
Author & Credits: https://www.alawise.es/1-s

Cada JPEG del MJPEG lleva la cabecera `X-1wise-Pendulum`:

```text
ts|x_px,y_px,r_px|ax_px,ay_px,ar_px|dx_mm,dy_mm,dz_mm|vx_mm_s,vy_mm_s,vz_mm_s|shift_3d_mm|fit_pct|alert|events
```

| Grupo | Significado | Unidad |
| --- | --- | --- |
| `ts` | Hora del fotograma | Unix, segundos |
| `x,y,r` | Centro y radio aparente del cascabel | px |
| `ax,ay,ar` | Referencia adaptativa | px |
| `dx,dy,dz` | Desplazamiento publicado | mm |
| `vx,vy,vz` | Velocidad publicada | mm/s |
| `shift_3d` | Amplitud XYZ publicada | mm |
| `fit_pct` | Puntuación geométrica | 0–100 |
| `alert` | Alarma decidida por el emisor | 0 / 1 |
| `events` | Contador del emisor | Entero |

`dz < 0` significa acercamiento a la lente; `dz > 0`, alejamiento.
El colector conserva los desplazamientos enviados: no los recalcula usando
la referencia, que el emisor actualiza después de calcularlos.

La cabecera sigue teniendo nueve grupos, pero cada vector pasa de dos a tres
componentes. La forma de los cuatro vectores permite distinguir el formato
3D del antiguo 2D; los formatos mixtos, valores no finitos y radios inválidos
se rechazan. La cabecera inicial completamente a cero significa espera.

El JSON público usa `version: 2`. En `sample` y `history` incorpora `mode`,
`r`, `ar`, `dz`, `vz`, `displacement`, `fit_pct`, `luminance` y
`tracking_valid`, además de las coordenadas y velocidades existentes.

- `mode: "3d-mm"`: desplazamientos en mm, velocidades en mm/s y
  `luminance: null`. `fit_pct <= 15` se trata conservadoramente como ajuste bajo.
- `mode: "2d-px"`: formato antiguo en píxeles, con `dz`, `vz`, `r`, `ar` y
  `fit_pct` en `null`. No se inventa una componente Z.
- `units` declara las unidades de posición, desplazamiento y velocidad.
- `limits.threshold` declara la referencia visual de amplitud.

La interfaz también admite snapshots anteriores `version: 1` durante la
actualización. Un cambio entre 2D y 3D inicia otra sesión, para evitar mezclar
píxeles con milímetros en una gráfica o exportación.

El CSV contiene 20 columnas e incluye unidades en los encabezados. Conserva
radios aparentes y coordenadas en px; las columnas de desplazamiento y
velocidad utilizan mm o px según la sesión. Los datos no disponibles quedan
vacíos. `source_threshold_active` conserva la alarma del emisor;
`tracker_event_count` conserva su contador.

En el emisor 3.1.0 adjunto, la alarma usa XY aunque la amplitud publicada sea
XYZ. La revisión opcional 3.1.1 cambia esa condición a XYZ. La interfaz mantiene
separados el estado del umbral visual y los eventos originales en ambos casos.
