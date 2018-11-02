<!DOCTYPE html>
<html>
<head>
<title>R2 Control</title>
<!--[if IE]><script src="http://html5shiv.googlecode.com/svn/trunk/html5.js"></script><![endif]-->
<link rel="stylesheet" type="text/css" href="css/style.css" />
<script src="https://code.jquery.com/jquery-2.1.4.min.js"></script>
<script>
       var page = "<?php echo $_GET['page'] ?>.php";
       function load_contents(page)
       {
           var xmlHttp = new XMLHttpRequest();

           xmlHttp.onreadystatechange = function() {
                if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
                {
                   content.innerHTML = xmlHttp.responseText;
                   //alert(new Date().getTime() - start);
                }
            };

            start = new Date().getTime();

            xmlHttp.open("GET", page, true); // true for asynchronous
            xmlHttp.send(null);

            // 1039
        }
</script>
</head>
<body>
<? echo test; ?>
    <div id="wrapper">
        <div id="headerwrap">
        <div id="header">
            <p>R2 Control</p>
        </div>
        </div>
        <div id="contentliquid"><div id="contentwrap">
        <div id="content">

        </div>
        </div></div>
        <div id="leftcolumnwrap">
        <div id="leftcolumn">
              <p>Menu</p>
              <ul>
               <li><a href="?page=dome">Dome control</a></li>
               <li><a href="?page=body">Body control</a></li>
               <li><a href="?page=scripts">Scripting</a></li>
               <li><a href="?page=audio">Audio</a></li>
               <li><a href="?page=debug">Debug</a></li>
               <li><a href="?page=controller">Controller</a></li>
               <li><a href="?page=shutdown">Shutdown</a></li>
             </ul>
        </div>
        </div>
        <div id="footerwrap">
        <div id="footer">
            <p><center>R2 Control (c) Darren Poulson <darren.poulson@gmail.com> 2018</center></p>
        </div>
        </div>
    </div>
<script>load_contents(page);</script>
</body>
</html>


