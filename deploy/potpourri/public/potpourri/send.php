<?php
// Timestamp: 2026-10-30
// Version: 2.0.0
// Author and Credits: https://www.alawise.es/1-s
declare(strict_types=1);
require_once dirname(__DIR__, 2) . '/private/send/send.php';
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
ini_set('session.use_strict_mode', '1');
session_name('kamala_potpourri');
session_set_cookie_params(['httponly'=>true, 'secure'=>true, 'samesite'=>'Strict', 'path'=>'/potpourri/']);
session_start();
$dat_adj = [];
try {
    $cfg_apl = env_cfg();
    $dat_tec = json_decode(file_get_contents(__DIR__ . '/topics.json'), true, 64, JSON_THROW_ON_ERROR);
    if ($_SERVER['REQUEST_METHOD'] === 'GET') {
        $_SESSION['csrf'] ??= bin2hex(random_bytes(32));
        $_SESSION['started'] ??= time();
        echo json_encode(['csrf'=>$_SESSION['csrf'], 'ready'=>filter_var($cfg_apl['contact_to'] ?? '', FILTER_VALIDATE_EMAIL) !== false && function_exists('imagecreatefromstring') && is_file($cfg_apl['autoload'] ?? '')], JSON_THROW_ON_ERROR);
        exit;
    }
    if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
        header('Allow: GET, POST');
        http_response_code(405);
        echo '{"ok":false,"message":"Method not allowed."}';
        exit;
    }
    if (!is_string($_POST['csrf'] ?? null) || !isset($_SESSION['csrf']) || !hash_equals($_SESSION['csrf'], $_POST['csrf'])) {
        throw new InvalidArgumentException('Reload the page before sending.', 403);
    }
    if (($_POST['website'] ?? '') !== '' || time()-($_SESSION['started'] ?? time()) < 2 || ($_POST['consent'] ?? '') !== 'yes') {
        throw new InvalidArgumentException('Review consent and wait a moment before sending.', 400);
    }
    foreach (['name'=>100,'email'=>254,'message'=>10000,'art'=>120] as $clv_esc=>$lim_env) {
        if (!is_string($_POST[$clv_esc] ?? null) || trim($_POST[$clv_esc]) === '' || strlen($_POST[$clv_esc]) > $lim_env) throw new InvalidArgumentException('Please check the form fields.',400);
    }
    if (!isset($dat_tec[$_POST['art']]) || preg_match('/[\r\n]/',$_POST['name'].$_POST['email']) || !filter_var($_POST['email'],FILTER_VALIDATE_EMAIL)) {
        throw new InvalidArgumentException('Choose an art and a valid reply address.',400);
    }
    $dat_env = $_FILES['photos'] ?? null;
    if (!is_array($dat_env) || !is_array($dat_env['name'] ?? null) || count($dat_env['name']) < 1 || count($dat_env['name']) > 3) throw new InvalidArgumentException('Choose one to three photographs.',400);
    if (!function_exists('imagecreatefromstring') || !class_exists('finfo')) throw new RuntimeException('Photo processing is unavailable.');
    $cnt_tot = 0;
    foreach ($dat_env['name'] as $sys_idx=>$txt_val) {
        $pth_fil = $dat_env['tmp_name'][$sys_idx] ?? '';
        $cnt_tot += (int)($dat_env['size'][$sys_idx] ?? 0);
        if (($dat_env['error'][$sys_idx] ?? UPLOAD_ERR_NO_FILE) !== UPLOAD_ERR_OK || !is_uploaded_file($pth_fil) || ($dat_env['size'][$sys_idx] ?? 0)>5*1024*1024 || $cnt_tot>12*1024*1024) throw new InvalidArgumentException('Photo limits are 5 MB each and 12 MB total.',400);
        $txt_met = (new finfo(FILEINFO_MIME_TYPE))->file($pth_fil);
        $dat_lim = @getimagesize($pth_fil);
        if (!in_array($txt_met,['image/jpeg','image/png','image/webp'],true) || !$dat_lim || $dat_lim[0]*$dat_lim[1]>25000000 || $dat_lim[0]<1 || $dat_lim[1]<1) throw new InvalidArgumentException('Use a valid JPEG, PNG or WebP image up to 25 megapixels.',400);
        // Re-encoding removes location metadata and prevents sending arbitrary payloads.
        $obj_img = @imagecreatefromstring(file_get_contents($pth_fil));
        if (!$obj_img) throw new InvalidArgumentException('A photograph could not be decoded.',400);
        $fac_esc = min(1,2400/max($dat_lim[0],$dat_lim[1]));
        $obj_dst = imagecreatetruecolor(max(1,(int)round($dat_lim[0]*$fac_esc)),max(1,(int)round($dat_lim[1]*$fac_esc)));
        imagefill($obj_dst,0,0,imagecolorallocate($obj_dst,255,255,255));
        imagecopyresampled($obj_dst,$obj_img,0,0,0,0,imagesx($obj_dst),imagesy($obj_dst),$dat_lim[0],$dat_lim[1]);
        $pth_adj = tempnam(sys_get_temp_dir(),'kamala-photo-');
        if ($pth_adj === false) throw new RuntimeException('Temporary storage unavailable.');
        $dat_adj[] = $pth_adj;
        chmod($pth_adj,0600);
        if (!imagejpeg($obj_dst,$pth_adj,90)) throw new RuntimeException('Photo encoding failed.');
        imagedestroy($obj_img);imagedestroy($obj_dst);
    }
    env_cor([
        'channel'=>'potpourri', 'to'=>[$cfg_apl['contact_to']], 'reply_to'=>trim($_POST['email']),
        'subject'=>'Kamala Potpourri — '.$dat_tec[$_POST['art']]['title'],
        'text'=>"Private interpretation request\nName: ".trim($_POST['name'])."\nEmail: ".trim($_POST['email'])."\nArt: ".$dat_tec[$_POST['art']]['title']."\nConsent: personal interpretation and email reply\n\n".trim($_POST['message']),
        'attachments'=>$dat_adj,
    ]);
    unset($_SESSION['csrf'],$_SESSION['started']);
    echo '{"ok":true,"message":"Photos accepted for delivery. The interpretation will be answered by email."}';
} catch (Throwable $err_env) {
    $lim_env = $err_env instanceof InvalidArgumentException ? (in_array($err_env->getCode(),[400,403],true)?$err_env->getCode():400) : ($err_env->getCode()===429?429:503);
    http_response_code($lim_env);
    if (!($err_env instanceof InvalidArgumentException)) error_log('Kamala Potpourri failed: '.get_class($err_env).' code='.$err_env->getCode());
    echo json_encode(['ok'=>false,'message'=>$err_env instanceof InvalidArgumentException?$err_env->getMessage():'Photo submission is unavailable. Please try again later.']);
} finally {
    foreach ($dat_adj as $pth_adj) if (is_file($pth_adj)) unlink($pth_adj);
}
