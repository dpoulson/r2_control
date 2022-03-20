<?php
include("include/config.php");

?>
<div id="content">
    <h3 class="current">Start shutdown procedure</h3>
    <div class="shutdown">
        <a href="/index.php">Shutdown</a>
    </div>
</div>
<?php

echo "<div class='message'>Shutting down&hellip;</div>";

$url = "http://localhost:5000/shutdown/now";
$fh = fopen($url, "r");

?>
