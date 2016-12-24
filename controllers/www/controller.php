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
  <a href="/index.php">R2 Unit: Web control system</a> - Select Controller
 </div>
 <div>
<?php

 $js_name=$_GET["js_name"];

 if (isset($js_name)) {
   $url = "http://localhost:5000/controller/ps3/".$js_name;
   $handle = fopen($url, "r");
 }


?>
<a href=?js_name=0>PS3 (js0)</a>
