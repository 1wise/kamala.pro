<!-- Timestamp: 2026-10-30 | Version: 2.0.1 | Author and Credits: https://www.alawise.es/1-s -->
<!-- Sanitized Drive reference; not installed by the V2 overlay. -->
<html>
<head>
    <title>Combinador de estudios</title>
    <meta name="Biorritmos Compositor" content="width=device-width, height=device-height, charset=utf-8">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />
    <link href="./stylesheet.css" rel="stylesheet" type="text/css">
 <script>
    function pasteClipboard(event) {
    // Check if the event is a double-click
    if (event.detail === 2) {
      // Get the clipboard content
      navigator.clipboard.readText()
        .then(text => {
          // Paste the clipboard content into the input field
          event.target.value = text;
        })
        .catch(err => {
          console.error('Failed to read clipboard contents: ', err);
        });
    }
  }
 </script>
</head>
<body>
    &nbsp;&nbsp;&nbsp;<b><u>Combinador de estudios</u></b><br><br>
    <form method="get" class="bior-form" enctype="multipart/form-data">
    <a><label type="text" style="font-size:14pt; ">DD-MM-YYYY-Para-DD-MM-YYYY.png</label></a><br>
    <a><input type="text" name="emdat1" ondblclick="pasteClipboard(event)" style="height:40px; font-size:22px; width:310px; font-family:caladea" maxlength="32" placeholder="Doble click para pegar"></a><br><br>
    <a><labe type="text" style="font-size:14pt; ">DD-MM-YYYY-Para-DD-MM-YYYY.png</label></a><br>
    <a><input type="text" name="emdat2" ondblclick="pasteClipboard(event)" style="height:40px; font-size:22px; width:310px; font-family:caladea" maxlength="32" placeholder="Doble click para pegar"></a><br><br>
    <a><label style="font-size:16pt; font-family:caladea;">Nombre de fichero, acabar con .png</label></a><br>
    <a><input type="text" style="height:40px; font-size:22pt; width:310px;" maxlength="254" name="emComb"></a><br><br>
    <a><input type="submit" type="text" style="font-size:22pt; height:45px; width:310px;" name="submit" value="Combinar Imagenes"></a>
    </form>
<?php
global $emUsr, $remMsg, $emAsu, $miMsg, $emDat, $nomImg, $smsNum, $somApi;
require_once './sense_mail.php';
require_once './sense_sms.php';
ob_start();
    // Biorhythm by 1wise.es
    // http://kamala.pro/biorritmos
        // http://1wise.es
    //
    // Last edit 25-08-2023 00:00
    //
    // Print a standard page header
    //
if(isset($_GET['emdat1']) && isset($_GET['emdat2']) && isset($_GET['emComb']) || isset($_POST['submit'])) {
   $somUsu = (getenv('KAMALA_SMS_USER') ?: '');
   $somPas = (getenv('KAMALA_SMS_PASSWORD') ?: '');
   $somApi = base64_encode("$somUsu:$somPas");
   $nowForm =  date(' d-m-y H:i:s ');
   $emIp = $_SERVER['REMOTE_ADDR'];
   $emdat1 = $_GET['emdat1'];
   $emdat2 = $_GET['emdat2'];
   $emComb = $_GET['emComb'];
   $nomImg = substr($emComb, 0, strpos($emComb, ".png")).".png";
   $dirImg = './consultas/';
   $dirNomImg = $dirImg . $nomImg;
   $remNom = $emComb;
   // Run ImageMagick to emComb the images
   exec("convert $dirImg$emdat1 $dirImg$emdat2 -composite $dirNomImg");

   // Display the result
   echo "<br>&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsp<b>Imagen Compuesta</b><br><br>";
   echo "<img id='laimagen' src='" . $dirImg . $nomImg . "' alt='" . $nomImg . "' />";

   if (strpos($remNom, "_") !== false ) {
     $emRem = strstr($remNom, '_', true);
   } else {
      $emRem = $remNom;
   }
   if (strpos($remNom, "_") !== false ) {
      $emRem = strstr($remNom, '_', true);
   } else {
      $emRem = $remNom;
   }
   $emUsr = '';
   if (preg_match('~_m_(.*?)_m_~', $emComb, $emUsch)) {
      $emUsr = $emUsch[1];
   }
   $smsNum = '';
   if (preg_match('~_pepitO_(.*?)_Grillo_~', $emComb, $smsNch)) {
      $smsNum = $smsNch[1];
   }
   $remMsg = '';
   if (preg_match('~_mSg_(.*?)_mSg_~', $emComb, $mstch)) {
      $remMsg = $mstch[1];
   }
   $emAsu =  ' Biorritmos https://kamala.pro/ - ' . $emdat1 . ' Combinado con ' . $emdat2;
   $miMsg = "<p>From - >>".$emIp." - ".$nowForm."<< - >>".$emRem."<< - >>".$remMsg."<< - Greetings ;)</p>";
   if ($emUsr !== '') {
      sense_mail($emUsr, $remMsg, $emDat, $emAsu, $miMsg, $nomImg);
   }
   if ($smsNum !== '' && $somApi !=='') {
      sense_sms($remMsg, $nomImg, $smsNum, $somApi);
   }
   // append log file
   $emIp = $_SERVER['REMOTE_ADDR'];
   $datLog  = ">".$emIp."<< - >>".$emdat1." - ".$emdat2." - ".$emComb." - ".date("d-m-Y H:i:s :)").PHP_EOL;
   file_put_contents('MaxMix.log', $datLog, FILE_APPEND);
}
exit();
ob_end_flush();
?>
</body>
</html>

