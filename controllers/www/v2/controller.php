<?php

include("include/config.php");

 $js_name=$_GET["js_name"];

 if (isset($js_name)) {
   $url = "http://localhost:5000/joystick/".$js_name;
   $handle = fopen($url, "r");
 }

 # Get current joystick
 $url = "http://localhost:5000/joystick/current";
 $fh = fopen($url, "r");
 $current = stream_get_contents($fh);
 echo "<h3>Current joystick: $current</h3>";

 # Get list of possible joysticks
 $url = "http://localhost:5000/joystick";
 $fh = fopen($url, "r");
 $joysticks = explode(PHP_EOL, stream_get_contents($fh));
 foreach ($joysticks as $stick) {
   echo "<a href='?js_name=$stick'>$stick</a><br />";
 }

?>
