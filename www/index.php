<html>

<div style="text-align:center; width:1024px; margin-left:auto; margin-right:auto;">
<img id="Image-Maps_6201308260908372" src="Dome-Panels.jpg" usemap="#Image-Maps_6201308260908372" border="0" width="1024" height="662" alt="" />
<map id="_Image-Maps_6201308260908372" name="Image-Maps_6201308260908372">
<area shape="poly" coords="181,268,166,334,182,394,239,357,242,301," href="http://192.168.5.197/?servo_name=pp5&value=0.9" alt="open pp5" title="open pp5"   />
<area shape="poly" coords="248,369,185,405,234,449,297,467,294,398," href="http://192.168.5.197/?servo_name=pp6&value=0.9" alt="" title=""   />
<area shape="poly" coords="307,398,308,466,366,450,414,404,358,369," href="http://192.168.5.197/?servo_name=PP1&value=0.9" alt="Open PP1" title="Open PP1"   />
<area shape="poly" coords="362,359,419,392,439,327,422,268,363,301," href="http://192.168.5.197/?servo_name=PP2&value=0.9" alt="Open PP2" title="Open PP2"   />
<area shape="rect" coords="1022,660,1024,662" href="http://www.image-maps.com/index.php?aff=mapped_users_6201308260908372" alt="Image Map" title="Image Map" />
</map>
<!-- Image map text links - Start - If you do not wish to have text links under your image map, you can move or delete this DIV -->
<div style="text-align:center; font-size:12px; font-family:verdana; margin-left:auto; margin-right:auto; width:1024px;">
	<a style="text-decoration:none; color:black; font-size:12px; font-family:verdana;" href="http://192.168.5.197/?servo_name=PP5&value=0.9" title="Open PP5">Open PP5</a>
 | 	<a style="text-decoration:none; color:black; font-size:12px; font-family:verdana;" href="http://192.168.5.197/?servo_name=PP6&value=0.9" title="Open PP6">Open PP6</a>
 | 	<a style="text-decoration:none; color:black; font-size:12px; font-family:verdana;" href="http://192.168.5.197/?servo_name=PP1&value=0.9" title="Open PP1">Open PP1</a>
 | 	<a style="text-decoration:none; color:black; font-size:12px; font-family:verdana;" href="http://192.168.5.197/?servo_name=PP2&value=0.9" title="Open PP2">Open PP2</a>
 | 	<a style="text-decoration:none; color:black; font-size:12px; font-family:verdana;" href="http://www.image-maps.com/index.php?aff=mapped_users_6201308260908372" title="Image Map">Image Map</a>
</div>
<!-- Image map text links - End - -->

</div>

<?php

$servo_name=$_GET["servo_name"];
$value=$_GET["value"];

if (isset($servo_name)) {
   system('echo '.$servo_name.','.$value.' > /tmp/r2_commands.pipe &');
}

?>


