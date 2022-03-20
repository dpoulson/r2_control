<?php
$style = file_get_contents('theme.txt');
if ($style === "galactic") {
$menuicon = "galacticmenuicon";
} else {
$menuicon = "menuicon";
}
?>
<header>
    <div class="leftheader">
        <a onclick="showleft();">
            <img src="images/<?php echo $menuicon ?>.png" srcset="images/<?php echo $menuicon ?>@2x.png 2x,images/<?php echo $menuicon ?>@3x.png 3x" width="44" height="44" alt="Open Menu this side">
        </a>
    </div>
    <div class="header">
        <h1>R2 Control <?php echo $page ?></h1>
    </div>
    <div class="rightheader">
        <a onclick="showright();">
            <img src="images/<?php echo $menuicon ?>.png" srcset="images/<?php echo $menuicon ?>@2x.png 2x,images/<?php echo $menuicon ?>@3x.png 3x" width="44" height="44" alt="Open Menu this side">
        </a>
    </div>
</header>
