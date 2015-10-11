<?

include("include/config.php");

?>
<html>
 <head>
  <title>R2 Unit: Web control system - Audio</title>
  <link href="r2d2.css" rel="stylesheet" type="text/css">
 </head>

 <body>
<div id="container">
 <div id="header">
  R2 Unit: Web control system - Audio
 </div>
 <div>
<?

$play = $_GET["play"];
$random = $_GET["random"];

if(isset($play)) {
   echo "Playing.... $play\n";
   $url = "http://localhost:5000/audio/".$play;
   $handle = fopen($url, "r");
}

if(isset($random)) {
   echo "Playing.... $play\n";
   $url = "http://localhost:5000/audio/random/".$random;
   $handle = fopen($url, "r");
}


$files = array_diff(scandir($sound_dir), array('..', '.'));
$num_files=sizeof($files);
$num_rows=$num_files/$num_cols;

echo "<table cols=11>\n";
echo "<tr>\n";
echo " <td><a href=\"?random=alarm\">Alarm</a></td>\n";
echo " <td><a href=\"?random=happy\">Happy</a></td>\n";
echo " <td><a href=\"?random=hum\">Hum</a></td>\n";
echo " <td><a href=\"?random=misc\">Misc</a></td>\n";
echo " <td><a href=\"?random=quote\">Quotes</a></td>\n";
echo " <td><a href=\"?random=razz\">Razz</a></td>\n";
echo " <td><a href=\"?random=sad\">Sad</a></td>\n";
echo " <td><a href=\"?random=sent\">Sent</a></td>\n";
echo " <td><a href=\"?random=ooh\">Oooh</a></td>\n";
echo " <td><a href=\"?random=proc\">Proc</a></td>\n";
echo " <td><a href=\"?random=whistle\">Whistle</a></td>\n";
echo "</tr>\n";
echo "</table>\n";

echo "<table cols=$num_cols>\n";

for ($i = 1 ; $i < $num_rows ; $i++) {
   $start_num = $i*$num_cols;
   echo "<tr>\n";
   echo " <td><a href=\"?play=".substr($files[$start_num], 0, -4)."\">".substr($files[$start_num], 0, -4)."</a></td>\n";
   echo " <td><a href=\"?play=".substr($files[$start_num+1], 0, -4)."\">".substr($files[$start_num+1], 0, -4)."</a></td>\n";
   echo " <td><a href=\"?play=".substr($files[$start_num+2], 0, -4)."\">".substr($files[$start_num+2], 0, -4)."</a></td>\n";
   echo " <td><a href=\"?play=".substr($files[$start_num+3], 0, -4)."\">".substr($files[$start_num+3], 0, -4)."</a></td>\n";
   echo " <td><a href=\"?play=".substr($files[$start_num+4], 0, -4)."\">".substr($files[$start_num+4], 0, -4)."</a></td>\n";
   echo " <td><a href=\"?play=".substr($files[$start_num+5], 0, -4)."\">".substr($files[$start_num+5], 0, -4)."</a></td>\n";
   echo "</td>\n";
} 

?>
  </table>

 </div>
 <div id="footer">
 </div> 
</div>

 </body>
</html>

