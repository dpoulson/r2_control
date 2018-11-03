<!DOCTYPE html>
<html>
<head>
<title>R2 Control</title>
<!--[if IE]><script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script><![endif]-->
<link rel="stylesheet" type="text/css" href="css/style.css" />
</head>
<body>
<?php $page = $_GET['page']; ?>
    <div id="wrapper">
        <div id="headerwrap">
        <div id="header">
            <p>R2 Control</p>
        </div>
        </div>
        <div id="contentliquid"><div id="contentwrap">
        <div id="content">
<?php include($page.".php"); ?>
        </div>
        </div></div>
        <div id="leftcolumnwrap">
        <div id="leftcolumn">
              <p>Menu</p>
              <ul>
               <li class=button><a href="?page=dome">Dome control</a></li>
               <li class=button><a href="?page=body">Body control</a></li>
               <li class=button><a href="?page=scripts">Scripting</a></li>
               <li class=button><a href="?page=audio">Audio</a></li>
               <li class=button><a href="?page=debug">Debug</a></li>
               <li class=button><a href="?page=controller">Controller</a></li>
               <li class=button><a href="?page=shutdown">Shutdown</a></li>
             </ul>
        </div>
        </div>
        <div id="footerwrap">
        <div id="footer">
            <p><center>R2 Control (c) Darren Poulson <darren.poulson@gmail.com> 2018</center></p>
        </div>
        </div>
    </div>
</body>
</html>


