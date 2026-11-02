# Kamala V2 — registro de variables

## Incorporaciones 2.1.1 pendientes de sincronización externa

La hoja vars se ha consultado de nuevo. Se reutilizan sys_idx, dmn_vis,
dmn_itm, idx_job, dat_img, url_img y ob_mut. Se documentan los nuevos nombres:

| Nombre | Uso |
| --- | --- |
| dat_dad / idx_dad | Fixed six-face pip catalogue and unique inline SVG instance counter. |
| svg_dad / crt_dad | Render exact vector die faces and accessible DOM figures. |
| obs_img / est_rev | Observe the chart image lifecycle and suppress partial batch status. |
| dat_del / cnt_try | Bounded retry delays and image reload attempt count. |
| recarga / enlaza / desliga | Reload an existing chart image and attach/remove its lifecycle listeners. |
| btn_img / lnk_img | Explicit image-only retry control and direct image link. |

Timestamp: 2026-10-30 | Version: 2.0.0
Author and Credits: https://www.alawise.es/1-s

Se consultó la hoja vars antes de implementar. Se reutilizan los nombres existentes.
La revisión automática rechazó añadir las siguientes filas a la hoja externa por falta de autorización explícita para esa escritura. Quedan documentadas aquí para sincronización posterior.

| Nombre | Categoría | Función | Convención | Uso |
| --- | --- | --- | --- | --- |
| dat_gls | Aplicación | Catálogo completo de artes y variantes | Castellano abreviado | Kamala V2: editorial groups, provenance, lexical definitions and photo instructions. |
| dat_lex | Aplicación | Entradas del léxico | Castellano abreviado | Kamala V2: searchable lexical entries with English and Spanish equivalents. |
| dat_top | Aplicación | Temas de interpretación | Castellano abreviado | Kamala V2: allowlisted Potpourri topics and photo guidance. |
| dat_nom | Aplicación | Nombres y equivalencias | Castellano abreviado | Kamala V2: names and localized lexical equivalents. |
| dat_grp | Aplicación | Grupos del índice | Castellano abreviado | Kamala V2: alphabetical lexical groups. |
| dat_opt | Aplicación | Opciones documentadas | Castellano abreviado | Kamala V2: allowlisted SDK option names mapped to provider constants. |
| dat_val | Aplicación | Valor validado de opción | Castellano abreviado | Kamala V2: selected constant value after allowlist validation. |
| act_fin | Aplicación | Acción al finalizar | Castellano abreviado | Kamala V2: asynchronous completion callback. |
| fin_ast | Aplicación | Finalizar cálculo astrológico | Castellano abreviado | Kamala V2: release busy state for the current chart job. |
| act_lex | Aplicación | Actualizar filtro del léxico | Castellano abreviado | Kamala V2: apply term and observation-scale filters. |
| fmt_lex | Aplicación | Normalizar término del léxico | Castellano abreviado | Kamala V2: accent-insensitive search text. |
| clv_lex | Aplicación | Clave estable de término | Castellano abreviado | Kamala V2: ASCII fragment identifier for a named lexical entry. |
| crt_v2 | Aplicación | Crear páginas de versión dos | Castellano abreviado | Kamala V2: render arts, complete glossary and private photo form. |
| crt_gls_lst | Aplicación | Crear listado de artes | Castellano abreviado | Kamala V2: render linked arts filtered by primary or secondary scale. |
| crt_pot_lnk | Aplicación | Crear enlace a Potpourri | Castellano abreviado | Kamala V2: technique-specific photo instructions and submission link. |
| est_drw | Aplicación | Estado de tirada explícita | Castellano abreviado | Kamala V2: permit a chance draw only for explicit api_act=draw. |
| obj_img | Sistema | Imagen de origen decodificada | Latín abreviado | Kamala V2: bounded GD source image decoded from an uploaded photo. |
| obj_dst | Sistema | Imagen de destino normalizada | Latín abreviado | Kamala V2: metadata-free GD raster sent as a JPEG attachment. |
| pth_prv | Sistema | Ruta privada | Latín abreviado | Kamala V2: private mail helper directory outside the public root. |
| pth_bak | Sistema | Ruta de copia de seguridad | Latín técnico abreviado | Kamala V2: timestamped rollback directory for the installation overlay. |
| pth_ctc | Sistema | Ruta de contacto | Latín técnico abreviado | Kamala V2: installed contact document preserved by the migration. |
| pth_arc | Sistema | Ruta de archivo de respaldo | Latín abreviado | Kamala V2: archived prior file under the rollback directory. |
| cpy_fil | Sistema | Copiar archivo autorizado | Latín abreviado | Kamala V2: copy an overlay file after backing up the existing target. |
| act_inst | Aplicación | Aplicar instalación | Castellano abreviado | Kamala V2: install a reviewed static/PHP overlay while retaining active host configuration. |
| crt_mod | Sistema | Cargar módulo auxiliar | Latín abreviado | Kamala V2: import a local release helper from an exact file path. |
| cnt_ast | Aplicación | Cantidad de etiquetas AstroApp | Castellano abreviado | Kamala V2: number of eligible head tags configured without printing the access code. |
| act_tec | Aplicación | Actualizar guía de técnica | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| dat_img | Sistema | Datos de imagen de prueba | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| env_prb | Aplicación | Petición multipart de prueba | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| pth_dst_fil | Sistema | Ruta de archivo destino | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| pth_rel | Sistema | Ruta relativa | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| pth_ses | Sistema | Ruta de sesiones de prueba | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| pth_tmp | Sistema | Ruta temporal | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| qry_flt | Aplicación | Filtro de consulta | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| rsp_ctc | Aplicación | Respuesta preparando formulario | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| sys_con | Sistema | Conexión HTTP local | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| sys_prc | Sistema | Proceso de prueba | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| sys_prt | Sistema | Puerto efímero de prueba | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| txt_bnd | Sistema | Separador multipart de prueba | Abreviatura estable | Kamala V2: pending external registry synchronization. |
| tok_ses | Sistema | Token de sesión de prueba | Abreviatura estable | Kamala V2: pending external registry synchronization. |


## Incorporaciones 2.0.3 pendientes de sincronización externa

| Nombre | Categoría | Función | Convención | Uso |
| --- | --- | --- | --- | --- |
| dat_car | Aplicación | Catálogo de métodos de carta | Castellano abreviado | Chart-family defaults and allowed calculation conventions. |
| act_car | Aplicación | Actualizar método de carta | Castellano abreviado | Rebuild the matching controls and reset submission consent. |
| est_prv | Aplicación | Estado de actualización privada | Castellano abreviado | Installer flag; public-only packages leave private mail modules untouched. |

## Incorporaciones 2.0.5 pendientes de sincronización externa

| Nombre | Categoría | Función | Convención | Uso |
| --- | --- | --- | --- | --- |
| dat_fil | Aplicación | Datos de archivos de entrega | Castellano abreviado | Download names, byte counts and SHA-256 values for release bundles. |
| txt_tit | Aplicación | Título de descarga | Castellano abreviado | User-facing label for each downloadable bundle. |

## Incorporaciones 2.0.6 pendientes de sincronización externa

| Nombre | Categoría | Función | Convención | Uso |
| --- | --- | --- | --- | --- |
| dat_tar | Aplicación | Catálogo de imágenes del tarot | Castellano abreviado | Complete 78-card map with image paths and art directions. |
| dat_pos | Aplicación | Posiciones de palos | Castellano abreviado | Symmetric layouts for exact numeral-card pip counts. |
| dat_pip | Aplicación | Dibujos de palos | Abreviatura estable | Reusable ornamental SVG suit emblems. |
| dmn_dlg | Sistema | Diálogo de imagen | Latín abreviado | Native modal for inspecting a card at full size. |
| url_img | Sistema | URL de imagen | Abreviatura estable | Validated local card image URL. |

## Incorporaciones 2.1.0 pendientes de sincronización externa

La hoja vars se volvió a consultar. Se reutilizan sys_cnv, sys_ctx, dat_tel, est_pau,
pth_fil, sys_ts y los nombres existentes. Se mantiene la restricción previa de escritura externa.

**Contemplación y visualización**: `dat_flu`, `dat_dst`, `dat_pul`, `dat_pix`, `dat_mem`, `val_tel`, `act_tel`, `crt_demo`, `crt_cnp`, `pet_tel`, `act_mod`, `act_tam`, `crt_rad`, `crt_elip`, `crt_fnd`, `crt_cera`, `crt_llama`, `crt_cir`, `crt_nube`, `crt_bola`, `crt_vis`, `act_ani`, `act_pau`, `act_foc`, `fmt_flu`, `sys_neb`, `ctx_neb`, `fac_dpr`, `chr_ani`, `chr_sig`, `chr_neb`, `est_foc`, `est_vis`, `cfg_apl`, `url_art`.

**Barajas y composición**: `dat_esp`, `txt_pip`, `txt_def`, `txt_pap`, `clv_pal`, `clv_est`, `ang_rad`, `ang_deg`, `val_esc`, `cnt_off`, `cnt_par`, `cnt_top`, `cnt_bot`, `cnt_lat`, `cnt_ini`, `txt_id`, `est_fig`, `txt_ran`, `txt_pal`, `txt_col`, `dat_cpy`, `sys_mod`.

**Captador y despliegue**: `dat_fwl`, `dat_red`, `dat_ant`, `dat_arg`, `dat_lns`, `dat_buf`, `dat_msg`, `dat_usr`, `txt_ifc`, `txt_ses`, `txt_cur`, `txt_ult`, `txt_typ`, `txt_usr`, `txt_ser`, `txt_uni`, `cnt_del`, `cnt_gid`, `cnt_uid`, `cnt_rx`, `cnt_tx`, `cnt_rp`, `cnt_tp`, `sys_mnt`, `sys_ant`, `sys_del`, `sys_dir`, `sys_inf`, `sys_out`, `sys_prc`, `sys_sel`, `sys_try`, `sys_sig`, `sys_clv`, `sys_evt`, `sys_err`, `pth_sys`, `pth_tel`, `pth_env`, `est_dis`, `est_exc`, `est_fin`, `est_up`.

Los nombres dat_flu/dat_dst guardan valores suavizados y objetivos de la imagen; dat_pul guarda pulsos breves. val_tel valida la señal pública; act_tel deduplica avisos por sesión y contador. El captador separa datos de red (dat_red) y avisos de firewall (dat_fwl), con rutas y tiempos del sistema abreviados en latín.
