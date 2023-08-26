<?php

include("include/config.php");

$play = $_GET["play"];
$random = $_GET["random"];
$vol = $_GET["vol"];

$sound_groups = array("alarm", "happy", "hum", "misc", "quote", "razz", "sad", "sent", "ooh", "proc", "whist", "screa", "theme");
?>
<div class="audiowrapper">
<div class="leftsound">
    <p class='flexrow'>
		<?php

		function startsWith($haystack, $needle)
		{
			// search backwards starting from haystack length characters from the end
			return $needle === ''
					|| strrpos($haystack, $needle, -strlen($haystack)) !== false;
		}

		if (isset($vol)) {
			$url = "http://localhost:5000/volume/" . $vol;
			$handle = fopen($url, "r");
		} elseif (isset($play)) {
			echo "Playing&hellip; $play\n";
			$url = "http://localhost:5000/audio/" . $play;
			$handle = fopen($url, "r");
		} elseif (isset($random)) {
			echo "Playing&hellip; $play\n";
			$url = "http://localhost:5000/audio/random/" . $random;
			$handle = fopen($url, "r");
		}

		if (!isset($vol)) {
			$url = "http://localhost:5000/audio/volume";
			$fh = fopen($url, "r");
			$current_volume = (round(stream_get_contents($fh), 2)) * 100;

			$url = "http://localhost:5000/audio/list";
			$fh = fopen($url, "r");
			$files = str_getcsv(str_replace(" ", "", stream_get_contents($fh)), ",");
			sort($files);
			$num_files = sizeof($files);

			echo "</p>\n";
			echo "<div class=tab>\n";
			foreach ($sound_groups as $group) {
				echo "<button class=tablinks onclick=\"openTab(event, '$group')\">" . ucfirst($group) . "</button>";
			}
			echo "<button class=tablinks onclick=\"openTab(event, 'other')\">Other</button>";
			echo "<button class=tablinks onclick=\"openTab(event, 'random')\" id=defaultOpen>Random</button>";
			echo "</div>\n";


			foreach ($sound_groups as $group) {
				echo "<div id=$group class=tabcontent>\n";
				echo "<div class=items>";
				for ($i = 0; $i < $num_files; $i++) {
					if (startsWith(strtolower($files[$i]), strtolower($group))) {
						echo "<div class=item><a href=\"?page=audio&play=" . $files[$i] . "\">" . $files[$i] . "</a></div>";
					}
				}
				echo "</div>";
				echo "</div>\n";
			}
			echo "<div id=other class=tabcontent>\n";
			echo "<div class=audioitems>";
			for ($i = 0; $i < $num_files; $i++) {
				$other = true;
				foreach ($sound_groups as $group) {
					if (startsWith(strtolower($files[$i]), strtolower($group))) {
						$other = false;
					}
				}
				if ($other) {
					echo "<div class=audioitem><a href=\"?page=audio&play=" . $files[$i] . "\">" . $files[$i] . "</a></div>";
				}
			}
			echo "</div>";
			echo "</div>\n";
			echo "<div id=random class=tabcontent>\n";
			echo "<div class=audioitems>\n";
			echo "<a href=\"?page=audio&random=alarm\" class=audioitem>Alarm</a>\n";
			echo "<a href=\"?page=audio&random=happy\" class=audioitem>Happy</a>\n";
			echo "<a href=\"?page=audio&random=hum\" class=audioitem>Hum</a>\n";
			echo "<a href=\"?page=audio&random=misc\" class=audioitem>Misc</a>\n";
			echo "<a href=\"?page=audio&random=quote\" class=audioitem>Quotes</a>\n";
			echo "<a href=\"?page=audio&random=razz\" class=audioitem>Razz</a>\n";
			echo "<a href=\"?page=audio&random=sad\" class=audioitem>Sad</a>\n";
			echo "<a href=\"?page=audio&random=sent\" class=audioitem>Sent</a>\n";
			echo "<a href=\"?page=audio&random=ooh\" class=audioitem>Oooh</a>\n";
			echo "<a href=\"?page=audio&random=proc\" class=audioitem>Proc</a>\n";
			echo "<a href=\"?page=audio&random=whistle\" class=audioitem>Whistle</a>\n";
			echo "<a href=\"?page=audio&random=scream\" class=audioitem>Scream</a>\n";
			echo "</div>\n";
			echo "</div>\n";

		}

		?>
</div>
<div class="graduation"></div>
    <div class="slidecontainer">
        <div class="slider" id="flat-slider-vertical"></div>
    </div>
</div>
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

    $(".slider").slider().slider("pips");

    $.extend( $.ui.slider.prototype.options, {
        animate: 300
    });

    $("#flat-slider-vertical")
        .slider({
            max: 100,
            min: 0,
            range: "min",
            value: 30,
            orientation: "vertical"
        })
        .slider("pips", {
            first: "pip",
            last: "pip"
        })

        // Update the current slider value (each time you drag the slider handle)
    .on("slidechange", function(e,ui) {

        const request = new XMLHttpRequest();

	console.log("Setting volume to: " + this.value);
        request.open('GET', 'http://<?php echo $_SERVER['SERVER_NAME']; ?>/?page=audio&vol=' + this.value / 100, true);
        request.send();
    });
</script>
