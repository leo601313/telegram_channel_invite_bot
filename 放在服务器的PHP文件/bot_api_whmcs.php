<?php
if (!isset ($_SESSION)) {
	ob_start();
	session_start();
}
header("Content-type: text/html;charset=utf-8");
try{
    $dbh = new PDO("mysql:host=localhost;port=3301;dbname=数据库名", "数据库用户名", "数据库密码");
    $dbh->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    global  $dbh;
    //  由于国外的名在前，姓氏在后，为了防止输入歧义，所以只审核名字（firstname）
    foreach($dbh->query("select  *  from  tblclients  where  `email`='".$_GET['email']."'")  as  $email) {
    	$id = $email['id'];
    	$firstname = $email['firstname'];}
    foreach($dbh->query("select  *  from  tblhosting  where  `userid`='".$id."' AND `domainstatus`='Active' LIMIT 1")as  $activelist)
    $id;
    if ($id == null) {
        echo "该用户没有注册！";
    } else {
        if ($firstname != $_GET['firstname']) {
            echo "邮箱和用户名不匹配！";
        } elseif ($firstname == $_GET['firstname'] && $activelist == null) {
            echo "该用户没有活跃的产品！";
        } elseif ($firstname == $_GET['firstname'] && $activelist != null) {
            echo "认证成功！";
        }
    }
    $dbh = null;
} catch (PDOException $e) {
    print "Error!: " . $e->getMessage() . "<br/>";
    die();
}
?>