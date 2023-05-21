<?php

include("include/config.php");

$style = file_get_contents('theme.txt');
if ($style === "galactic") {
	$bodyimage = "galactic-body";
} else {
	$bodyimage = "body";
}

$panels = ["LLD" => "Left Bread Pan Door",
            "DATA" => "Data Panel Door",
            "CBD" => "Changing Bay Door",
            "AUX" => "Auxiliary Door",
            "RLD" => "Right Bread Pan Door",
            "GripArm" => "Gripper Arm",
            "TopArm" => "Top Utility Arm",
            "BotArm" => "Bottom Utility Arm",
            "SArm" => "SCOMP Computer Interface Arm",
            "ENABLE_DRIVE"];

$servo_list = file_get_contents("http://localhost:5000/servo/body/list");
$convert = explode("\n", $servo_list);

for ($i = 0; $i < count($convert); $i++) {
	$data = str_getcsv($convert[$i]);
	$list[$i] = $data[0];
}

$servo_name = $_GET["servo_name"];
$value = $_GET["value"];

if (isset($servo_name)) {
	$url = "http://localhost:5000/servo/body/" . $servo_name . "/" . $value . "/0";
	$handle = fopen($url, "r");
}
?>
<div class="servowrapper">
    <div class="diagram">
        <img src="images/<?php echo $bodyimage ?>.png" srcset="images/<?php echo $bodyimage ?>@2x.png 2x,images/<?php echo $bodyimage ?>@3x.png 3x" width="382" height="375" alt="Body Diagram">
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
    if (in_array($panel, $list)) {
        echo "<tr>
                <td class='panel'>$i $panel</td>
                <td><a href=\"?page=body&servo_name=$key&value=0.9\" class='open'>Open</a></td>
                <td><a href=\"?page=body&servo_name=$key&value=0\" class='close'>Close</a></td>
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
