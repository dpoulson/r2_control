<html>
 <head>
  <title>R2 Unit: Web control system</title>
 </head>

 <body>



<h1>R2 Unit: Web control system</h1>
<ul>
 <li><a href="dome.php">Dome control</a></li>
 <li><a href="body.php">Body control</a></li>
 <li><a href="scripts.php">Scripting</a></li>
 <li><a href="audio.php">Audio</a></li>
 <li>Debug</li>
 <li><a href="controller.php">Select Controller</a></li>
 <li><a href="shutdown.php">Shutdown</a></li>
</ul>

<pre>
<?php

$url = "http://localhost:5000/status";
$fh = fopen($url, "r");
echo stream_get_contents($fh);



?>
</pre>

</body>
</html>

