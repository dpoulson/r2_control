<?php

include("include/config.php");

function setTheme($theme) {
	file_put_contents('theme.txt', $theme);
	header("Location: http://$_SERVER[HTTP_HOST]");
	exit;
}
  if (isset($_GET['theme'])) {
	  $theme = $_GET['theme'];
	  setTheme($theme);
  }
?>

<h3 class="avail">Select your theme</h3>
<div class="items">
    <div class="item"><a href='?theme=blueprint'>Blueprint</a></div>
    <div class="item"><a href='?theme=galactic'>Galactic</a></div>
</div>


