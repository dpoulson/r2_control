<?php

include("include/config.php");

$play = $_GET["play"];
$loop = $_GET["loop"];
$stop = $_GET["stop"];

if(!isset($loop)) {
   $loop = 0;
}

if(isset($stop)) {
   echo "Stopping... $stop<br />\n";
   $url = "http://localhost:5000/scripts/stop/".$stop;
   $handle = fopen($url, "r");
}


if(isset($play)) {
   echo "<p class='flexrow'>Playing&hellip; $play</p>\n";
   $url = "http://localhost:5000/scripts/".$play."/".$loop;
   $handle = fopen($url, "r");
}

$url = "http://localhost:5000/scripts/running";
$fh = fopen($url, "r");

$convert = explode("\n", stream_get_contents($fh));

for ($i=0;$i<count($convert);$i++)
{
    $data = str_getcsv($convert[$i]);
    if ($data != "")
       $running_list[$i] = $data[0];
}
if (sizeof($running_list) > 1) {
    echo "Running scripts: <br>";
    echo "<ul>\n";

    for ($x = 0 ; $x < sizeof($running_list) - 1; $x++) {
        list($id, $name) = explode(":", $running_list[$x]);
        echo " <li>Running: $name ($id) <a href=\"?page=scripts&stop=".$id."\">stop</a></li>";
    } 

    echo "</ul>\n";
}

$url = "http://localhost:5000/scripts/list";
$fh = fopen($url, "r");
$files = str_getcsv(str_replace(" ", "", stream_get_contents($fh)));
sort($files);
$num_files=sizeof($files);

echo "<div class=items>";
for ($i = 0 ; $i < $num_files ; $i++) {
   echo "<div class=item><a href=\"?page=scripts&play=".$files[$i]."\">".$files[$i]."</a></div>";
}
echo "</div>";


?>


