<?php
// api/books.php
require_once 'config.php';
$action = $_GET['action'] ?? '';
$d = json_input();

if ($action === 'add') {
  $sql = "INSERT INTO books (category,title,author,isbn,branch,date_of_purchase,price,source,rack_no,copies,remark)
          VALUES (?,?,?,?,?,?,?,?,?,?,?)";
  $stmt = $pdo->prepare($sql);
  $stmt->execute([
    $d['category'],$d['title'],$d['author'],$d['isbn'],$d['branch'],$d['dop'],$d['price'],$d['source'],$d['rack_no'],$d['copies'],$d['remark']??''
  ]);
  echo json_encode(['ok'=>true]); exit;
}

if ($action === 'delete') {
  $stmt = $pdo->prepare("DELETE FROM books WHERE isbn=?");
  $stmt->execute([$d['isbn']]);
  echo json_encode(['ok'=>true]); exit;
}

if ($action === 'search') {
  $q = '%'.($d['q'] ?? '').'%';
  $branch = $d['branch'] ?? '';
  if($branch){
    $stmt = $pdo->prepare("SELECT * FROM books WHERE (title LIKE ? OR isbn LIKE ?) AND branch=? ORDER BY title");
    $stmt->execute([$q,$q,$branch]);
  } else {
    $stmt = $pdo->prepare("SELECT * FROM books WHERE (title LIKE ? OR isbn LIKE ?) ORDER BY title");
    $stmt->execute([$q,$q]);
  }
  echo json_encode(['ok'=>true,'data'=>$stmt->fetchAll()]); exit;
}

if ($action === 'list') {
  $stmt = $pdo->query("SELECT title,author,isbn,category,branch,copies FROM books ORDER BY title LIMIT 200");
  echo json_encode(['ok'=>true,'data'=>$stmt->fetchAll()]); exit;
}

echo json_encode(['ok'=>false,'message'=>'Unknown action']);
?>
