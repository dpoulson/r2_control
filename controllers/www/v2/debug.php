<?php

include("include/config.php");

$url = "http://localhost:5000/status";
$fh = fopen($url, "r");

$status = stream_get_contents($fh);

echo "<div>";
echo "<pre>";
echo $status;
echo "</pre>";
echo "</div>";


?>


