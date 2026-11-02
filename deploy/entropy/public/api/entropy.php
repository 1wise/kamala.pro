<?php
// Timestamp: 2026-10-29
// Version: 1.10.0
// Author and Credits: https://www.alawise.es/1-s
// Sample one fixed camera per request; never accept a visitor-supplied URL.
declare(strict_types=1);
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, max-age=0');
header('X-Content-Type-Options: nosniff');
// The portable tool reads only this public sample. No cookies, keys or
// request bodies are needed; wildcard CORS also supports a local file origin.
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, OPTIONS');
if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'OPTIONS') {
    http_response_code(204);
    exit;
}
if (($_SERVER['REQUEST_METHOD'] ?? 'GET') !== 'GET') {
    http_response_code(405);
    header('Allow: GET, OPTIONS');
    echo json_encode(['error' => 'Use GET.']);
    exit;
}
$clv_cam = $_GET['src'] ?? 'auto';
if (!is_string($clv_cam) || !in_array($clv_cam, ['auto', 'cam1', 'cam2', 'cam3', 'cam4'], true)) {
    http_response_code(400);
    echo json_encode(['error' => 'Unknown source.']);
    exit;
}
// Bound aggregate camera traffic to one acquisition per second across this pool.
$sys_fil = @fopen(sys_get_temp_dir() . '/kamala-entropy.lock', 'c+');
if (!$sys_fil || !flock($sys_fil, LOCK_EX | LOCK_NB)) {
    http_response_code(503);
    echo json_encode(['error' => 'Sampler busy.']);
    exit;
}
$sys_ts = microtime(true);
if ($sys_ts - (float)stream_get_contents($sys_fil) < 1.0) {
    http_response_code(429);
    header('Retry-After: 1');
    echo json_encode(['error' => 'Sampler cooling down.']);
    exit;
}
ftruncate($sys_fil, 0);
rewind($sys_fil);
fwrite($sys_fil, (string)$sys_ts);
fflush($sys_fil);
$clv_cam = $clv_cam === 'auto' ? 'cam' . random_int(1, 4) : $clv_cam;
$dat_mst = '';
$est_cam = false;
if (function_exists('curl_init')) {
    $sys_cnl = curl_init('https://kam.2to1.me/stream/' . $clv_cam);
    curl_setopt_array($sys_cnl, [
        CURLOPT_CONNECTTIMEOUT_MS => 900,
        CURLOPT_TIMEOUT_MS => 2000,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_USERAGENT => 'Kamala-Entropy/1.10.0',
        CURLOPT_WRITEFUNCTION => static function ($sys_cnl, string $dat_par) use (&$dat_mst): int {
            $dat_mst .= substr($dat_par, 0, 131072 - strlen($dat_mst));
            // Stop an endless MJPEG connection once its bounded sample is full.
            return strlen($dat_mst) >= 131072 ? 0 : strlen($dat_par);
        },
    ]);
    curl_exec($sys_cnl);
    $txt_val = strtolower((string)curl_getinfo($sys_cnl, CURLINFO_CONTENT_TYPE));
    $sys_idx = strpos($dat_mst, "\xff\xd8\xff");
    $est_cam = curl_getinfo($sys_cnl, CURLINFO_HTTP_CODE) === 200
        && (str_starts_with($txt_val, 'multipart/x-mixed-replace') || str_starts_with($txt_val, 'image/jpeg'))
        && $sys_idx !== false && strlen($dat_mst) - $sys_idx >= 1024;
    $dat_mst = $est_cam ? substr($dat_mst, (int)$sys_idx) : '';
    curl_close($sys_cnl);
}
// Hashing conditions bytes; it does not establish a physical entropy rate.
$dat_azr = hash('sha512', "Kamala-v1.7\0" . random_bytes(64) . $dat_mst);
echo json_encode([
    'hex' => $dat_azr,
    'source' => $est_cam ? $clv_cam : null,
    'sample_bytes' => strlen($dat_mst),
    'sampled_at' => gmdate('c'),
    'mode' => $est_cam ? 'stream+system' : 'system-only',
]);
flock($sys_fil, LOCK_UN);
fclose($sys_fil);
