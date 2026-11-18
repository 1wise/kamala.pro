# Camera 3.5.9 → collector 3.6.0 → browser

Timestamp: 2026-11-16 | Version: 3.6.0
Author & Credits: https://www.alawise.es/1-s

The multipart JPEG header remains X-1wise-Pendulum. A complete new sample has
13 pipe-separated groups. The collector also accepts the previous nine-group
3D and 2D formats. Missing wind fields are unknown, never zero wind.

| Group | Payload | Units |
| --- | --- | --- |
| 1 | source timestamp | Unix seconds |
| 2 | x,y,apparent radius | pixels |
| 3 | anchor x,y,radius | pixels |
| 4 | dx,dy,dz | mm |
| 5 | vx,vy,vz | mm/s |
| 6 | 3D displacement | mm |
| 7 | geometric fit | integer percent |
| 8 | source bell alarm | 0/1; already wind-gated |
| 9 | source event counter | integer |
| 10 | smoothed pan-handle tilt | degrees |
| 11 | harmonic dissociation DH | 0–1, rounded to 2 decimals |
| 12 | source turbulence flag | 0/1 |
| 13 | wind factor | 0–2.5, rounded to 2 decimals |

The JSON envelope is version 3. Each sample/history item has a wind object
with tilt_deg, dissociation, turbulence, factor, suppression_active and
threshold_xy_mm. Legacy items have wind:null. Event records keep their wind
context; no extra bird events are inferred from the wind channel.

The reference source compares raw DH against 0.45. It computes the wind factor
as clamp(DH / 0.45, 0, 2.5). During turbulence, its effective XY threshold is
15 × (1 + 2.5 × factor) mm, and the bell alarm is suppressed even above that
threshold. Outside turbulence the source threshold is 15 mm.

The browser's 3D reference and XZ circle are visual references, not the source
XY decision boundary. With the new protocol the source flag, rather than 3D
amplitude, determines the alarm state. DH is an optical motion/dissociation
indicator; neither DH nor the factor is a calibrated wind speed in m/s.

DH and factor are rounded on the wire. DH=0.45 can coexist with either source
turbulence flag. The collector must not recompute that flag from the rounded
number. threshold_xy_mm is an estimate derived from the transmitted factor:
its rounding alone can differ from the source threshold by about 0.19 mm.
No claim is made that the windchime establishes the physical cause of motion.

All values are validated before publication. NaN/Infinity, invalid vectors,
invalid wind ranges and a simultaneous turbulence flag and bell alarm are
rejected. All-zero startup sentinels remain waiting. JPEG lengths are honored
so payload bytes cannot be mistaken for multipart headers.

## Optical references and pressure hypothesis

The first marker tracks the ladle's reflective handle. The second reference
belongs to the wok: the current code tracks its cavity center and estimates
tilt from its handle direction. DH combines loss of motion coherence with
variation in the ladle-to-wok horizontal offset. The capture algorithm and
the transmitted schema are unchanged by this clarification.

An association with turbulent airflow or low atmospheric pressure is an
observation hypothesis to compare with independent measurements. No pressure
value is measured or transmitted; pressure requires an independent barometer
record. Raw positions of the two windchime markers are not included in the
13-group header, which carries tilt and the derived DH/factor/flag instead.
