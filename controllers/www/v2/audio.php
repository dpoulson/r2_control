<?php

include("include/config.php");

$play = $_GET["play"];
$random = $_GET["random"];
$vol = $_GET["vol"];

if(isset($vol)) {
   $url = "http://localhost:5000/audio/volume/".$vol;
   $handle = fopen($url, "r");
}
elseif(isset($play)) {
   echo "Playing.... $play\n";
   $url = "http://localhost:5000/audio/".$play;
   $handle = fopen($url, "r");
}
elseif(isset($random)) {
   echo "Playing.... $play\n";
   $url = "http://localhost:5000/audio/random/".$random;
   $handle = fopen($url, "r");
}

if(!isset($vol)) {
   $url = "http://localhost:5000/audio/volume";
   $fh = fopen($url, "r");
   $current_volume = (round(stream_get_contents($fh), 2))*100;

?>
<br />
<div class="slidecontainer">
  Vol: <input type="range" min="0" max="100" value="<?php echo $current_volume; ?>" class="slider" id="volume">
</div>
<script>
var slider = document.getElementById("volume");
var output = document.getElementById("current_volume");

// Update the current slider value (each time you drag the slider handle)
slider.oninput = function() {
    var request = new XMLHttpRequest();

    request.open('GET', 'http://<?php echo $_SERVER['SERVER_NAME']; ?>/v2/?page=audio&vol=' + this.value/100, true);
    request.send();
}
</script>
<?php
   $url = "http://localhost:5000/audio/list";
   $fh = fopen($url, "r");
   $files = str_getcsv(str_replace(" ", "", stream_get_contents($fh)), ",");
   sort($files);
   $num_files=sizeof($files);

   echo "<table id='table' cols=11>\n";
   echo "<tr>\n";
   echo " <td class=item><a href=\"?page=audio&random=alarm\">Alarm</a></td>\n";
   echo " <td><a href=\"?page=audio&random=happy\">Happy</a></td>\n";
   echo " <td><a href=\"?page=audio&random=hum\">Hum</a></td>\n";
   echo " <td><a href=\"?page=audio&random=misc\">Misc</a></td>\n";
   echo " <td><a href=\"?page=audio&random=quote\">Quotes</a></td>\n";
   echo " <td><a href=\"?page=audio&random=razz\">Razz</a></td>\n";
   echo " <td><a href=\"?page=audio&random=sad\">Sad</a></td>\n";
   echo " <td><a href=\"?page=audio&random=sent\">Sent</a></td>\n";
   echo " <td><a href=\"?page=audio&random=ooh\">Oooh</a></td>\n";
   echo " <td><a href=\"?page=audio&random=proc\">Proc</a></td>\n";
   echo " <td><a href=\"?page=audio&random=whistle\">Whistle</a></td>\n";
   echo " <td><a href=\"?page=audio&random=scream\">Scream</a></td>\n";
   echo "</tr>\n";
   echo "</table>\n";

echo "<div class=items>";
for ($i = 0 ; $i < $num_files ; $i++) {
   echo "<div class=item><a href=\"?page=audio&play=".$files[$i]."\">".$files[$i]."</a></div>";
}
echo "</div>";

}

?>


