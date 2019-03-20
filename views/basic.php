<!DOCTYPE html>
<html>
<head>
    <title><?php echo $title; ?> | GBooks</title>
    <meta http-equiv='Content-Type' content='text/html;charset=utf-8'/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    <link href="/css/style.css" rel="stylesheet"/>
    <script src="/js/chosen.jquery.min.js"></script>
    <link href="/css/chosen.min.css" rel="stylesheet"/>
    <?php echo $css; ?>


</head>
<body class="<?php echo $userStateClass; ?>">
<?php include SITE_ROOT . '/views/layouts/partials/header.tpl.php' ?>

<content class="col-lg-12">
    <div id="messages"><?php echo $messages; ?></div>
    <div><?php echo $content; ?></div>
</content>

<?php include SITE_ROOT . '/views/layouts/partials/footer.tpl.php' ?>
<?php echo $scriptElements; ?>
</body>
</html>