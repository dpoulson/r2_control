<html>

<?php

$servo_name=$_GET["servo_name"];
$value=$_GET["value"];

if (isset($servo_name)) {
   system('echo '.$servo_name.','.$value.' > /tmp/r2_commands.pipe');
}

$filename = "/home/pi/r2_control/servo.conf";

$lines = file($filename, FILE_IGNORE_NEW_LINES);

print "<center>\n";
print "<table width=600 border=1 align=center>\n";
print "<font size=+4>";

foreach ($lines as $line) {
    list($address, $channel, $name, $min, $max) = explode(",", $line);
    print "<tr style=\"height:40px\"><td><a href=\"?servo_name=".$name."&value=0.1\">10</a></td><td><a href=\"?servo_name=".$name."&value=0.25\">25</a></td><td><a href=\"?servo_name=".$name."&value=0.45\">45</a></td><td>".$name."</td><td><a href=\"?servo_name=".$name."&value=0.55\">55</a></td><td><a href=\"?servo_name=".$name."&value=0.75\">75</a></td><td><a href=\"?servo_name=".$name."&value=0.9\">90</a></td></tr>\n";
}

print "</table>\n";
print "</center>\n"

?>
