<?php

include("include/config.php");

$js_name = $_GET["js_name"];
if (isset($js_name)) {
	$url = "http://localhost:5000/joystick/" . $js_name;
	$handle = fopen($url, "r");
}

# Get current joystick
$url = "http://localhost:5000/joystick/current";
$fh = fopen($url, "r");
$current = stream_get_contents($fh);
echo "<h3 class='current'>Current Controller $current</h3>";
echo "<div class=items>";
echo "<div class='current'>$current <img src='images/$current.png' alt='$current' width='40' height='40'></a></div>";
echo "</div>";

# Get list of possible joysticks
$url = "http://localhost:5000/joystick";
$fh = fopen($url, "r");
$joysticks = explode(PHP_EOL, stream_get_contents($fh));
echo "<h3 class='avail'>Available Controllers</h3>";
echo "<div class=items>";
foreach ($joysticks as $stick) {
	echo "<div class=item><a href='?js_name=$stick'>$stick <img src='images/$stick.png' alt='$stick' width='40px' height='40px'></a></div>";
}
echo "</div>";
