<?php

include("include/config.php");

$play = $_GET["play"];
$random = $_GET["random"];
$vol = $_GET["vol"];

$sound_groups = array("alarm", "happy",	"hum","misc", "quote", "razz", "sad", "sent", "ooh", "proc", "whist", "screa", "theme");

function startsWith($haystack, $needle) {
    // search backwards starting from haystack length characters from the end
    return $needle === ''
      || strrpos($haystack, $needle, -strlen($haystack)) !== false;
}

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

   echo "<div class=tab>\n";
   foreach ($sound_groups as $group) {
      echo "<button class=tablinks onclick=\"openTab(event, '$group')\">".ucfirst($group)."</button>";
   }
      echo "<button class=tablinks onclick=\"openTab(event, 'other')\">Other</button>";
      echo "<button class=tablinks onclick=\"openTab(event, 'random')\" id=defaultOpen>Random</button>";
   echo "</div>\n";


   foreach ($sound_groups as $group) {
      echo "<div id=$group class=tabcontent>\n";
      echo "<div class=items>";
      for ($i = 0 ; $i < $num_files ; $i++) {
         if (startsWith(strtolower($files[$i]), strtolower($group))) {
            echo "<div class=item><a href=\"?page=audio&play=".$files[$i]."\">".$files[$i]."</a></div>";
         }
      }
      echo "</div>";
      echo "</div>\n";
   }
   echo "<div id=other class=tabcontent>\n";
   echo "<div class=items>";
   for ($i = 0 ; $i < $num_files ; $i++) {
      $other = true;
      foreach ($sound_groups as $group) {
         if (startsWith(strtolower($files[$i]), strtolower($group))) { 
            $other = false;
         }
      }
      if ($other) {
         echo "<div class=item><a href=\"?page=audio&play=".$files[$i]."\">".$files[$i]."</a></div>";
      }
   }
   echo "</div>";
   echo "</div>\n";


   echo "<div id=random class=tabcontent>\n";
   echo "<div class=items>\n";
   echo " <div class=item><a href=\"?page=audio&random=alarm\">Alarm</a></div>\n";
   echo " <div class=item><a href=\"?page=audio&random=happy\">Happy</a></div>\n";
   echo " <div class=item><a href=\"?page=audio&random=hum\">Hum</a></div>\n";
   echo " <div class=item><a href=\"?page=audio&random=misc\">Misc</a></div>\n";
   echo " <div class=item><a href=\"?page=audio&random=quote\">Quotes</a></div>\n";
   echo " <div class=item><a href=\"?page=audio&random=razz\">Razz</a></div>\n";
   echo " <div class=item><a href=\"?page=audio&random=sad\">Sad</a></div>\n";
   echo " <div class=item><a href=\"?page=audio&random=sent\">Sent</a></div>\n";
   echo " <div class=item><a href=\"?page=audio&random=ooh\">Oooh</a></div>\n";
   echo " <div class=item><a href=\"?page=audio&random=proc\">Proc</a></div>\n";
   echo " <div class=item><a href=\"?page=audio&random=whistle\">Whistle</a></div>\n";
   echo " <div class=item><a href=\"?page=audio&random=scream\">Scream</a></div>\n";
   echo "</div>\n";
   echo "</div>\n";


}

?>

<script>
function openTab(evt, groupName) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(groupName).style.display = "block";
    evt.currentTarget.className += " active";
}
document.getElementById("defaultOpen").click();
</script>



