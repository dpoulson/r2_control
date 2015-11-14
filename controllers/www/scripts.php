<?

include("include/config.php");

?>
<html>
 <head>
  <title>R2 Unit: Web control system - Scripts</title>
  <link href="r2d2.css" rel="stylesheet" type="text/css">
 </head>

 <body>
<div id="container">
 <div id="header">
  <a href="/index.php">R2 Unit: Web control system</a> - Scripts
 </div>
 <div>
<?

$play = $_GET["play"];
$loop = $_GET["loop"];
$stop = $_GET["stop"];

if(!isset($loop)) {
   $loop = 0;
}

if(isset($stop)) {
   echo "Stopping... $stop<br />\n";
   $url = "http://localhost:5000/script/stop/".$stop;
   $handle = fopen($url, "r");
}


if(isset($play)) {
   echo "Playing.... $play<br />\n";
   $url = "http://localhost:5000/script/".$play."/".$loop;
   $handle = fopen($url, "r");
}

$url = "http://localhost:5000/script/running";
$fh = fopen($url, "r");

$convert = explode("\n", stream_get_contents($fh));

for ($i=0;$i<count($convert);$i++)
{
    $data = str_getcsv($convert[$i]);
    if ($data != "")
       $running_list[$i] = $data[0];
}

if (sizeof($running_list) > 1) {
    echo "Running scripts: <br />";
    echo "<ul>\n";

for ($x = 0 ; $x < sizeof($running_list) - 1; $x++) {
    list($id, $name) = split(":", $running_list[$x]);
    echo " <li>Running: $name ($id) <a href=\"?stop=".$id."\">stop</a></li>";
} 

    echo "</ul>\n";
}

$url = "http://localhost:5000/script/list";
$fh = fopen($url, "r");
$files = str_getcsv(str_replace(" ", "", stream_get_contents($fh)), ",");
sort($files);
$num_files=sizeof($files);
$num_rows=($num_files/$num_cols);



echo "<table cols=$num_cols>\n";

for ($i = 0 ; $i < $num_rows ; $i++) {
   $start_num = $i*$num_cols;
   echo "<tr>\n";
   echo " <td><a href=\"?play=".$files[$start_num]."\">".$files[$start_num]."</a> <a href=\"?play=".$files[$start_num]."&loop=1\">(loop)</a></td>\n";
   echo " <td><a href=\"?play=".$files[$start_num+1]."\">".$files[$start_num+1]."</a> <a href=\"?play=".$files[$start_num+1]."&loop=1\">(loop)</a></td>\n";
   echo " <td><a href=\"?play=".$files[$start_num+2]."\">".$files[$start_num+2]."</a> <a href=\"?play=".$files[$start_num+2]."&loop=1\">(loop)</a></td>\n";
   echo " <td><a href=\"?play=".$files[$start_num+3]."\">".$files[$start_num+3]."</a> <a href=\"?play=".$files[$start_num+3]."&loop=1\">(loop)</a></td>\n";
   echo " <td><a href=\"?play=".$files[$start_num+4]."\">".$files[$start_num+4]."</a> <a href=\"?play=".$files[$start_num+4]."&loop=1\">(loop)</a></td>\n";
   echo " <td><a href=\"?play=".$files[$start_num+5]."\">".$files[$start_num+5]."</a> <a href=\"?play=".$files[$start_num+5]."&loop=1\">(loop)</a></td>\n";
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

