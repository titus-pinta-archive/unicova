<nav class="navbar navbar-inverse">
    <div class="container-fluid">
        <div class="navbar-header">
            <a href="/">
                <img class="navbar-brand" src=""/>
            </a>
        </div>
        <ul class="nav navbar-nav">
            <li><a href="/"> Home</a></li>
            <li><a href="/admin"> Admin</a></li>
            <li class="logged-in"><a href="/admin/settings"> Settings</a></li>
        </ul>
        <ul class="nav navbar-nav navbar-right">
            <li class="logged-out">
                <a href="/login">
                    <span class="glyphicon glyphicon-log-in">
                    </span> Login
                </a>
            </li>
            <li class="logged-in">
                <a href="/logout">
                    <span class="glyphicon glyphicon-log-out">
                    </span> Logout
                </a>
            </li>
        </ul>
    </div>
</nav>
