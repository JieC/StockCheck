<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <title>MSSC</title>

    <!-- Bootstrap core CSS -->
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">

    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
      <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
      <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>

  <body>
    <nav class="navbar navbar-inverse">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="#">Stock Check</a>
        </div>
        <div id="navbar" class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li class="active"><a href="#">Home</a></li>
            <li><a href="#">About</a></li>
          </ul>
		  <form class="navbar-form navbar-right" role="add" action='/add' method="post"> 
			<div class="form-group">
			  <input type="text" class="form-control" name="pid" placeholder="ID">
			  <input type="text" class="form-control" name="pname" placeholder="Name">
			</div>
			<button type="submit" class="btn btn-primary">Add</button>
		  </form>
        </div><!--/.nav-collapse -->
      </div>
    </nav>

    <div class="container">
		<table class="table table-striped">
		  <tr>
			<th>Product ID</th>
			<th>Product Name</th>
			<th>In Stock?</th>
			<th>Last Check Date</th>
      <th>Delete</th>
		  </tr>
    	% for p in q:
        <tr>
        <td><a href="http://www.microsoftstore.com/store/msusa/en_US/pdp/productID.{{p.key.id()}}">{{p.key.id()}}</a></td>
        <td>{{p.pname}}</td>
        <td>{{p.instock}}</td>
        <td>{{p.rdate.replace(microsecond=0).isoformat()}}</td>
        <td><button class='btn btn-primary btn-xs'>X</button></td>
        </tr>
      % end
		</table>
    </div><!-- /.container -->


    <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.3/jquery.min.js"></script>
    <!-- Include all compiled plugins (below), or include individual files as needed -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>
    <script src="static/sc.js"></script>  

  </body>
</html>
