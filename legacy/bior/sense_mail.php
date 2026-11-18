<?php
// Timestamp: 2026-10-28
// Version: 1.0.0
// Author and Credits: https://www.alawise.es/1-s

require_once '/var/www/kamala.pro/private/send/send.php';

// Keep the six positional arguments used by bior.php and compose.php.
function sense_mail($dat_dst, $txt_msj, $txt_val, $txt_asu, $txt_hom, $pth_fil)
{
    try {
        if (!is_string($pth_fil) || basename($pth_fil) !== $pth_fil ||
            !preg_match('/\A[^\/\\\\\x00]+\.png\z/i', $pth_fil)) {
            throw new InvalidArgumentException('Invalid chart filename.');
        }
        $sys_rad = realpath(__DIR__ . '/consultas');
        $pth_adj = realpath(__DIR__ . '/consultas/' . $pth_fil);
        if ($sys_rad === false || $pth_adj === false ||
            !str_starts_with($pth_adj, $sys_rad . DIRECTORY_SEPARATOR) ||
            !is_file($pth_adj) || filesize($pth_adj) > 2097152 ||
            (@getimagesize($pth_adj)[2] ?? null) !== IMAGETYPE_PNG) {
            throw new InvalidArgumentException('Chart unavailable or invalid.');
        }
        // Legacy caller HTML includes request fields. Escape it instead of trusting it.
        $txt_msj = trim(strip_tags((string) $txt_hom)) . "\n\n" . (string) $txt_msj;
        env_cor([
            'channel' => 'bior',
            'to' => array_values(array_unique(array_map('trim', explode(',', (string) $dat_dst)))),
            'subject' => trim((string) $txt_asu),
            'text' => $txt_msj,
            'html' => '<p>' . nl2br(htmlspecialchars($txt_msj, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')) . '</p><img src="cid:bior-chart" alt="Biorhythm chart">',
            'attachments' => [$pth_adj],
        ]);
        echo 'Message accepted for delivery.<br>';
        return true;
    } catch (Throwable $err_env) {
        // Avoid leaking SMTP details, recipient data, or credentials to the browser.
        error_log('Kamala bior mail failed: ' . get_class($err_env) . ' code=' . $err_env->getCode());
        echo 'Email could not be submitted. Please try again later.<br>';
        return false;
    }
}
