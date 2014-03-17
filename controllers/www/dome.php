<html>
 <head>
  <title>R2 Unit: Web control system - Dome</title>
  <link href="r2d2.css" rel="stylesheet" type="text/css">
 </head>

<?php

 $panels = array("PP1", "PP2", "PP4", "PP5", "PP6", "P1", "P2", "P3", "P4", "P7");

 $servo_name=$_GET["servo_name"];
 $value=$_GET["value"];

 if (isset($servo_name)) {
   system('echo DOME,'.$servo_name.','.$value.' > /tmp/r2_commands.pipe &');
 }

?>

 <body>
<div id="container">
 <div id="header">
  R2 Unit: Web control system - Dome
 </div>
 <div id="diagram">
  <img width=400 border=0 src="Dome.jpg">
 </div>
 <div id="menu">
  <table border=1>
   <tr>
    <th>Panel</th>
    <th colspan=2>Control</th>
   </tr>
  <?

    foreach ($panels as $panel) {
      echo "<tr>\n";
      echo " <td>$panel</td>\n";
      echo " <td><a href=\"http://r2d2/dome.php?servo_name=$panel&value=0.9\">Open</a></td>\n";
      echo " <td><a href=\"http://r2d2/dome.php?servo_name=$panel&value=0\">Close</a></td>\n";
      echo "</tr>\n";
    }
  ?>
 </div>
 <div id="footer">
 </div> 
</div>

 </body>
</html>

