<?php
// Timestamp: 2026-10-28
// Version: 1.0.0
// Author and Credits: https://www.alawise.es/1-s
declare(strict_types=1);

namespace PHPMailer\PHPMailer {
    // Offline transport double: no network, shell, or real email is used.
    #[\AllowDynamicProperties]
    class PHPMailer {
        public static array $dat_env = [];
        public array $dat_dst = [];
        public array $dat_adj = [];
        public function __construct(bool $txt_val = true) {}
        public function __call(string $txt_val, array $dat_itm) {
            if ($txt_val === 'addAddress') $this->dat_dst[] = $dat_itm[0];
            if ($txt_val === 'addAttachment') $this->dat_adj[] = $dat_itm[0];
            if ($txt_val === 'setFrom') $this->from_addr = $dat_itm[0];
            if ($txt_val === 'addReplyTo') $this->reply_to = $dat_itm[0];
            if ($txt_val === 'send') self::$dat_env[] = clone $this;
            return true;
        }
    }
}

namespace {
    $sys_rad = sys_get_temp_dir() . '/kamala-send-' . bin2hex(random_bytes(6));
    mkdir($sys_rad, 0700);
    mkdir($sys_rad . '/consultas', 0700);
    copy(__DIR__ . '/../private/send.php', $sys_rad . '/send.php');
    $cfg_apl = require __DIR__ . '/../private/config.example.php';
    $cfg_apl['autoload'] = $sys_rad . '/autoload.php';
    $cfg_apl['smtp_pass'] = 'offline-fixture';
    $cfg_apl['contact_to'] = 'team@example.org';
    $cfg_apl['state_file'] = $sys_rad . '/rate.json';
    $cfg_apl['per_ip_hour'] = 2;
    $cfg_apl['total_hour'] = 3;
    file_put_contents($cfg_apl['autoload'], '<?php');
    file_put_contents($sys_rad . '/config.php', '<?php return ' . var_export($cfg_apl, true) . ';');
    require $sys_rad . '/send.php';
    $_SERVER['REMOTE_ADDR'] = '192.0.2.1';
    $dat_env = ['channel' => 'contact', 'to' => ['team@example.org'], 'reply_to' => 'visitor@example.net', 'subject' => 'Inquiry', 'text' => 'Hello'];

    try {
        env_cor($dat_env);
        if (\PHPMailer\PHPMailer\PHPMailer::$dat_env[0]->from_addr !== 'kamala@1wise.es' ||
            \PHPMailer\PHPMailer\PHPMailer::$dat_env[0]->reply_to !== 'visitor@example.net') {
            throw new \RuntimeException('Fixed sender / Reply-To test failed.');
        }
        foreach ([
            ['to' => ['other@example.org']],
            ['to' => ["victim@example.org\r\nBcc: injected@example.org"]],
            ['subject' => "Hello\nBcc: injected@example.org"],
            ['reply_to' => 'invalid'],
            ['text' => []],
            ['channel' => 'unknown'],
        ] as $dat_itm) {
            try {
                env_cor(array_replace($dat_env, $dat_itm));
                throw new \RuntimeException('Unsafe message was accepted.');
            } catch (\InvalidArgumentException $err_env) {}
        }
        env_cor($dat_env);
        try {
            env_cor($dat_env);
            throw new \LogicException('Per-peer limit failed.');
        } catch (\RuntimeException $err_env) {
            if ($err_env->getCode() !== 429) throw $err_env;
        }
        $_SERVER['REMOTE_ADDR'] = '192.0.2.2';
        env_cor($dat_env);
        $_SERVER['REMOTE_ADDR'] = '192.0.2.3';
        try {
            env_cor($dat_env);
            throw new \LogicException('Global limit failed.');
        } catch (\RuntimeException $err_env) {
            if ($err_env->getCode() !== 429) throw $err_env;
        }

        file_put_contents($cfg_apl['state_file'], '');
        file_put_contents($sys_rad . '/consultas/chart.png', base64_decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aX1sAAAAASUVORK5CYII='));
        $txt_val = file_get_contents(__DIR__ . '/../public/bior/sense_mail.php');
        file_put_contents($sys_rad . '/sense_mail.php', str_replace('/var/www/kamala.pro/private/send/send.php', $sys_rad . '/send.php', $txt_val));
        require $sys_rad . '/sense_mail.php';
        ob_start();
        if (sense_mail('reader@example.org', '<script>unsafe</script>', '', 'Chart', '<p>Legacy text</p>', 'chart.png') !== true) {
            throw new \RuntimeException('Legacy chart adapter failed.');
        }
        if (sense_mail('reader@example.org', '', '', 'Chart', '', '../config.php') !== false) {
            throw new \RuntimeException('Path traversal was accepted.');
        }
        ob_end_clean();
        $dat_itm = end(\PHPMailer\PHPMailer\PHPMailer::$dat_env);
        if (count($dat_itm->dat_adj) !== 1 || str_contains($dat_itm->Body, '<script>')) {
            throw new \RuntimeException('Chart attachment / HTML escaping failed.');
        }
        echo "PASS: sender, Reply-To, destination lock, header injection, input types, quotas, PNG adapter, path containment and HTML escaping. No email sent.\n";
    } finally {
        foreach (glob($sys_rad . '/consultas/*') as $pth_fil) unlink($pth_fil);
        rmdir($sys_rad . '/consultas');
        foreach (glob($sys_rad . '/*') as $pth_fil) unlink($pth_fil);
        rmdir($sys_rad);
    }
}
