<?php
// Timestamp: 2026-10-28
// Version: 1.0.0
// Author and Credits: https://www.alawise.es/1-s
declare(strict_types=1);

require_once '/var/www/kamala.pro/private/send/send.php';
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
ini_set('session.use_strict_mode', '1');
session_name('kamala_contact');
session_set_cookie_params(['httponly' => true, 'secure' => true, 'samesite' => 'Strict', 'path' => '/contact/']);
session_start();

try {
    if ($_SERVER['REQUEST_METHOD'] === 'GET') {
        $_SESSION['csrf'] ??= bin2hex(random_bytes(32));
        $_SESSION['started'] ??= time();
        echo json_encode(['csrf' => $_SESSION['csrf']], JSON_THROW_ON_ERROR);
        exit;
    }
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        header('Allow: GET, POST');
        http_response_code(405);
        echo '{"ok":false,"message":"Method not allowed."}';
        exit;
    }
    if (!is_string($_POST['csrf'] ?? null) || !isset($_SESSION['csrf']) ||
        !hash_equals($_SESSION['csrf'], $_POST['csrf'])) {
        throw new InvalidArgumentException('Reload the page and try again.', 403);
    }
    if (!is_string($_POST['website'] ?? '') || ($_POST['website'] ?? '') !== '' ||
        time() - ($_SESSION['started'] ?? time()) < 2) {
        throw new InvalidArgumentException('Please wait a moment and try again.', 400);
    }
    foreach (['name' => 100, 'email' => 254, 'message' => 12000] as $clv_lim => $lim_env) {
        if (!is_string($_POST[$clv_lim] ?? null) || trim($_POST[$clv_lim]) === '' || strlen($_POST[$clv_lim]) > $lim_env) {
            throw new InvalidArgumentException('Please check the form fields.', 400);
        }
    }
    if (preg_match('/[\r\n]/', $_POST['name']) || preg_match('/[\r\n]/', $_POST['email']) ||
        !filter_var($_POST['email'], FILTER_VALIDATE_EMAIL)) {
        throw new InvalidArgumentException('Please enter a valid name and email address.', 400);
    }
    $cfg_apl = env_cfg();
    env_cor([
        'channel' => 'contact',
        'to' => [$cfg_apl['contact_to']],
        'reply_to' => trim($_POST['email']),
        'subject' => 'Kamala inquiry',
        'text' => "Name: " . trim($_POST['name']) . "\nEmail: " . trim($_POST['email']) . "\n\n" . trim($_POST['message']),
    ]);
    unset($_SESSION['csrf'], $_SESSION['started']);
    echo '{"ok":true,"message":"Message accepted for delivery. Thank you."}';
} catch (Throwable $err_env) {
    if ($err_env instanceof InvalidArgumentException) {
        http_response_code(in_array($err_env->getCode(), [400, 403], true) ? $err_env->getCode() : 400);
        echo json_encode(['ok' => false, 'message' => $err_env->getMessage()]);
    } else {
        http_response_code($err_env->getCode() === 429 ? 429 : 503);
        error_log('Kamala contact mail failed: ' . get_class($err_env) . ' code=' . $err_env->getCode());
        echo '{"ok":false,"message":"Email could not be submitted. Please try again later."}';
    }
}
