<?php
// Timestamp: 2026-10-28
// Version: 1.0.0
// Author and Credits: https://www.alawise.es/1-s

return [
    // Use smtp for OVH, or sendmail for an already configured local Postfix.
    'transport' => 'smtp',
    'smtp_host' => 'ssl0.ovh.net',
    'smtp_port' => 465,
    'smtp_tls' => 'ssl',
    'smtp_user' => 'kamala@1wise.es',
    'smtp_pass' => '',
    'from_addr' => 'kamala@1wise.es',
    'from_name' => 'Kamala',
    // Contact always sends to this server-controlled address.
    'contact_to' => '',
    // Preserve the legacy BCC only when this copy is still wanted.
    'bior_bcc' => 'henri@sirkia.es',
    'autoload' => __DIR__ . '/vendor/autoload.php',
    'state_file' => '/var/lib/php/kamala/send/rate.json',
    'per_ip_hour' => 5,
    'total_hour' => 100,
];
