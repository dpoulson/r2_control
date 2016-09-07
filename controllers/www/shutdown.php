<?php

include("include/config.php");

?>
<html>
 <head>
  <title>R2 Unit: Web control system - Shutdown</title>
  <link href="r2d2.css" rel="stylesheet" type="text/css">
 </head>

 <body>
<div id="container">
 <div id="header">
  <a href="/index.php">R2 Unit: Web control system</a> - Shutdown
 </div>
 <div>
<?php

echo "Shutting down...";

$url = "http://localhost:5000/shutdown/now";
$fh = fopen($url, "r");

?>
