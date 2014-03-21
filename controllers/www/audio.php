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

if(isset($play)) {
   echo "Playing.... $play\n";
   exec("mpg123 $sound_dir/$play &");
}

$files = array_diff(scandir($sound_dir), array('..', '.'));
$num_files=sizeof($files);
$num_rows=$num_files/$num_cols;

echo "<table cols=$num_cols>\n";

for ($i = 1 ; $i < $num_rows ; $i++) {
   $start_num = $i*$num_cols;
   echo "<tr>\n";
   echo " <td><a href=\"?play=".$files[$start_num]."\">".substr($files[$start_num], 0, -4)."</a></td>\n";
   echo " <td><a href=\"?play=".$files[$start_num+1]."\">".substr($files[$start_num+1], 0, -4)."</a></td>\n";
   echo " <td><a href=\"?play=".$files[$start_num+2]."\">".substr($files[$start_num+2], 0, -4)."</a></td>\n";
   echo " <td><a href=\"?play=".$files[$start_num+3]."\">".substr($files[$start_num+3], 0, -4)."</a></td>\n";
   echo " <td><a href=\"?play=".$files[$start_num+4]."\">".substr($files[$start_num+4], 0, -4)."</a></td>\n";
   echo " <td><a href=\"?play=".$files[$start_num+5]."\">".substr($files[$start_num+5], 0, -4)."</a></td>\n";
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

