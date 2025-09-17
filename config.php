<?php
// api/config.php
header('Content-Type: application/json');
$host = 'localhost';
$db   = 'library_db';
$user = 'root';
$pass = '';
$charset = 'utf8mb4';

$options = [
  PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
  PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
  PDO::ATTR_EMULATE_PREPARES   => false,
];

try {
  $pdo = new PDO("mysql:host=$host;dbname=$db;charset=$charset", $user, $pass, $options);
} catch (PDOException $e) {
  http_response_code(500);
  echo json_encode(['ok'=>false,'message'=>'DB connection failed: '.$e->getMessage()]);
  exit;
}

function json_input(){
  $raw = file_get_contents('php://input');
  return $raw ? json_decode($raw, true) : [];
}
?>
