<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>R2 Control</title>
    <script src="js/jquery-3.6.0.min.js"></script>
    <script src="js/jquery-ui.min.js"></script>
    <script src="js/jquery-ui-slider-pips.js"></script>
    <link rel="stylesheet" type="text/css" href="js/jquery-ui.min.css"/>
    <link rel="stylesheet" type="text/css" href="js/jquery-ui-slider-pips.css"/>
    <link rel="stylesheet" type="text/css" href="css/style.css"/>
</head>
<body id="body" class="<?php echo file_get_contents('theme.txt'); ?>">

<?php $page = $_GET['page'];
$page = $page ?? 'configuration'; ?>

<div class="wrapper">
	<?php include("include/header.php"); ?>
    <div class="contentfluid">
        <aside id="leftaside" class="show">
	    <?php include("include/sidemenu.html"); ?>
        </aside>
        <div class="content">
			<?php include($page . ".php"); ?>
        </div>
        <aside id="rightaside">
	    <?php include("include/sidemenu.html"); ?>
        </aside>
    </div>
	<?php include("include/footer.html"); ?>
</div>
<script>
    const leftaside = document.getElementById('leftaside')
    const rightaside = document.getElementById('rightaside')
    function showleft(){
        rightaside.classList.remove('show')
        leftaside.classList.add('show');
    }
    function showright(){
        leftaside.classList.remove('show')
        rightaside.classList.add('show');
    }
    const mypanel = document.getElementsByClassName(".panel");
</script>
</body>
</html>


