<?php
// Timestamp: 2026-10-30
// Version: 2.0.0
// Author and Credits: https://www.alawise.es/1-s
declare(strict_types=1);

function env_cfg(): array
{
    $cfg_apl = require __DIR__ . '/config.php';
    if (!is_array($cfg_apl)) {
        throw new RuntimeException('Invalid private mail configuration.');
    }
    return $cfg_apl;
}

function env_lim(array $cfg_apl): void
{
    // Hash the direct peer rather than trusting user-supplied proxy headers.
    // The file lock also caps concurrent requests across PHP-FPM workers.
    $sys_fil = fopen($cfg_apl['state_file'], 'c+');
    if ($sys_fil === false || !flock($sys_fil, LOCK_EX)) {
        throw new RuntimeException('Mail quota storage is unavailable.');
    }
    try {
        $sys_ts = (int) floor(time() / 3600);
        $clv_lim = hash('sha256', $_SERVER['REMOTE_ADDR'] ?? 'local');
        $txt_val = stream_get_contents($sys_fil);
        $dat_lim = $txt_val === '' ? [] : json_decode($txt_val, true, 32, JSON_THROW_ON_ERROR);
        if (!is_array($dat_lim)) {
            throw new RuntimeException('Invalid mail quota storage.');
        }
        if (($dat_lim['hour'] ?? null) !== $sys_ts) {
            $dat_lim = ['hour' => $sys_ts, 'total' => 0, 'peers' => []];
        }
        if ($dat_lim['total'] >= $cfg_apl['total_hour'] ||
            ($dat_lim['peers'][$clv_lim] ?? 0) >= $cfg_apl['per_ip_hour']) {
            throw new RuntimeException('Mail quota exceeded.', 429);
        }
        ++$dat_lim['total'];
        $dat_lim['peers'][$clv_lim] = ($dat_lim['peers'][$clv_lim] ?? 0) + 1;
        $txt_val = json_encode($dat_lim, JSON_THROW_ON_ERROR);
        rewind($sys_fil);
        if (!ftruncate($sys_fil, 0) || fwrite($sys_fil, $txt_val) !== strlen($txt_val) || !fflush($sys_fil)) {
            throw new RuntimeException('Mail quota storage could not be saved.');
        }
    } finally {
        flock($sys_fil, LOCK_UN);
        fclose($sys_fil);
    }
}

function env_cor(array $dat_env): void
{
    $cfg_apl = env_cfg();
    if (!in_array($dat_env['channel'] ?? '', ['contact', 'bior', 'potpourri'], true)) {
        throw new InvalidArgumentException('Unknown message channel.');
    }
    if (!is_array($dat_env['to'] ?? null) || count($dat_env['to']) < 1 || count($dat_env['to']) > 5) {
        throw new InvalidArgumentException('Invalid recipient count.');
    }
    foreach ($dat_env['to'] as $dat_dst) {
        if (!is_string($dat_dst) || preg_match('/[\r\n]/', $dat_dst) || !filter_var($dat_dst, FILTER_VALIDATE_EMAIL)) {
            throw new InvalidArgumentException('Invalid recipient address.');
        }
    }
    if (in_array($dat_env['channel'], ['contact', 'potpourri'], true) && $dat_env['to'] !== [$cfg_apl['contact_to']]) {
        throw new InvalidArgumentException('Invalid contact destination.');
    }
    $txt_asu = $dat_env['subject'] ?? '';
    if (!is_string($txt_asu) || $txt_asu === '' || strlen($txt_asu) > 250 || preg_match('/[\r\n]/', $txt_asu)) {
        throw new InvalidArgumentException('Invalid message subject.');
    }
    if (!is_string($dat_env['text'] ?? null) || strlen($dat_env['text']) > 16000) {
        throw new InvalidArgumentException('Invalid message body.');
    }
    // Transport settings stay server-side. TLS certificate validation remains enabled.
    require_once $cfg_apl['autoload'];
    $obj_cor = new \PHPMailer\PHPMailer\PHPMailer(true);
    $obj_cor->CharSet = 'UTF-8';
    $obj_cor->SMTPDebug = 0;
    $obj_cor->Timeout = 15;
    if ($cfg_apl['transport'] === 'smtp') {
        if ($cfg_apl['smtp_pass'] === '' || !in_array($cfg_apl['smtp_tls'], ['ssl', 'tls'], true)) {
            throw new RuntimeException('SMTP credentials or TLS mode are not configured.');
        }
        $obj_cor->isSMTP();
        $obj_cor->Host = $cfg_apl['smtp_host'];
        $obj_cor->Port = (int) $cfg_apl['smtp_port'];
        $obj_cor->SMTPAuth = true;
        $obj_cor->Username = $cfg_apl['smtp_user'];
        $obj_cor->Password = $cfg_apl['smtp_pass'];
        $obj_cor->SMTPSecure = $cfg_apl['smtp_tls'];
    } elseif ($cfg_apl['transport'] === 'sendmail') {
        $obj_cor->isSendmail();
        $obj_cor->Sendmail = '/usr/sbin/sendmail';
    } else {
        throw new RuntimeException('Unsupported mail transport.');
    }
    $obj_cor->setFrom($cfg_apl['from_addr'], $cfg_apl['from_name']);
    foreach ($dat_env['to'] as $dat_dst) {
        $obj_cor->addAddress($dat_dst);
    }
    if (!empty($dat_env['reply_to'])) {
        if (preg_match('/[\r\n]/', $dat_env['reply_to']) || !filter_var($dat_env['reply_to'], FILTER_VALIDATE_EMAIL)) {
            throw new InvalidArgumentException('Invalid reply address.');
        }
        $obj_cor->addReplyTo($dat_env['reply_to']);
    }
    if ($dat_env['channel'] === 'bior' && $cfg_apl['bior_bcc'] !== '') {
        $obj_cor->addBCC($cfg_apl['bior_bcc']);
    }
    $obj_cor->Subject = $txt_asu;
    $obj_cor->isHTML(isset($dat_env['html']));
    $obj_cor->Body = $dat_env['html'] ?? $dat_env['text'];
    $obj_cor->AltBody = isset($dat_env['html']) ? $dat_env['text'] : '';
    foreach ($dat_env['attachments'] ?? [] as $pth_adj) {
        if ($dat_env['channel'] === 'potpourri') {
            $obj_cor->addAttachment($pth_adj, basename($pth_adj) . '.jpg', 'base64', 'image/jpeg');
        } else {
            $obj_cor->addAttachment($pth_adj);
            $obj_cor->addEmbeddedImage($pth_adj, 'bior-chart', basename($pth_adj));
        }
    }
    // Count attempts before opening SMTP, including transport failures.
    env_lim($cfg_apl);
    $obj_cor->send();
}
