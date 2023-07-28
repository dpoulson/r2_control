<?php

include("include/config.php");

$style = file_get_contents('theme.txt');
if ($style === "galactic") {
	$domeimage = "galactic-dome";
} else {
	$domeimage = "dome";
}

$panels = ["PP1" => "Pie Panel 1",
            "PP2" => "Pie Panel 2",
            "PERI" => "Periscope Pie Panel",
            "PP5" => "Pie Panel 5",
            "PP6" => "Pie Panel 6",
            "DT" => "Dome Topper",
            "MP1" => "Medium Panel 1",
            "MP2" => "Medium Panel 2",
            "MP3" => "Medium Panel 3",
            "LP1" => "Large Panel 1",
            "LP2" => "Large Panel 2",
            "LP3" => "Large Panel 3",
            "SP" => "Small Panel",
            "VSP" => "Very Small Panel"];

$servo_list = file_get_contents("http://localhost:5000/dome/list");
$convert = explode("\n", $servo_list);

for ($i = 0; $i < count($convert); $i++) {
	$data = str_getcsv($convert[$i]);
	$list[$i] = $data[0];
}

$servo_name = $_GET["servo_name"];
$value = $_GET["value"];

if (isset($servo_name)) {
	$url = "http://localhost:5000/dome/" . $servo_name . "/" . $value . "/0";
	$handle = fopen($url, "r");
}
?>
<div class="servowrapper">
    <div class="diagram">
        <img src="images/<?php echo $domeimage ?>.png" srcset="images/<?php echo $domeimage ?>@2x.png 2x,images/<?php echo $domeimage ?>@3x.png 3x" width="367" height="378" alt="Dome Diagram">
    </div>
    <div class="table">
        <table>
            <thead>
            <tr>
                <th>Panel</th>
                <th colspan=2>Control</th>
            </tr>
            </thead>
            <tbody>
<?php

$i = 0;
foreach ($panels as $key => $panel) {
    $i++;
    if (in_array($key, $list)) {
        echo "<tr>
                <td class='panel'>$i $panel</td>
                <td><a href=\"?page=dome&servo_name=$key&value=0.9\" class='open'>Open</a></td>
                <td><a href=\"?page=dome&servo_name=$key&value=0\" class='close'>Close</a></td>
            </tr>\n";
                } else {
                    echo "<tr>
                <td class='panel'><i>$i $panel</i></td>
                <td colspan='2'>Unavailable</td>
            </tr>\n";
    }
}
?>
            </tbody>
        </table>
    </div>
</div>
