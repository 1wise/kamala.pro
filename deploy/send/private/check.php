<?php
// Timestamp: 2026-10-28
// Version: 1.0.0
// Author and Credits: https://www.alawise.es/1-s
declare(strict_types=1);

if (PHP_SAPI !== 'cli') {
    http_response_code(404);
    exit;
}
require __DIR__ . '/send.php';
try {
    $cfg_apl = env_cfg();
    require $cfg_apl['autoload'];
    if (!class_exists(\PHPMailer\PHPMailer\PHPMailer::class)) {
        throw new RuntimeException('PHPMailer is unavailable.');
    }
    if (!filter_var($cfg_apl['from_addr'], FILTER_VALIDATE_EMAIL) ||
        !filter_var($cfg_apl['contact_to'], FILTER_VALIDATE_EMAIL)) {
        throw new RuntimeException('Configure from_addr and contact_to.');
    }
    if ($cfg_apl['transport'] === 'smtp' && $cfg_apl['smtp_pass'] === '') {
        throw new RuntimeException('Configure smtp_pass.');
    }
    if ($cfg_apl['transport'] === 'sendmail' && !is_executable('/usr/sbin/sendmail')) {
        throw new RuntimeException('Local sendmail transport is unavailable.');
    }
    if (!is_writable($cfg_apl['state_file'])) {
        throw new RuntimeException('Quota file is not writable by this account.');
    }
    echo "Configuration preflight passed. No message was sent.\n";
} catch (Throwable $err_env) {
    fwrite(STDERR, $err_env->getMessage() . "\n");
    exit(1);
}
