<?php
// api/auth.php
require_once 'config.php';
$action = $_GET['action'] ?? '';

if ($action === 'student_register') {
  $d = json_input();
  $sql = "INSERT INTO students (name,email,roll_number,course,branch,mobile,password_hash,dob,address)
          VALUES (?,?,?,?,?,?,?,?,?)";
  $stmt = $pdo->prepare($sql);
  $stmt->execute([
    $d['name'],$d['email'],$d['roll_number'],$d['course'],$d['branch'],$d['mobile'],
    password_hash($d['password'], PASSWORD_BCRYPT), $d['dob'],$d['address']
  ]);
  echo json_encode(['ok'=>true]); exit;
}

if ($action === 'student_login') {
  $d = json_input();
  $stmt = $pdo->prepare("SELECT id,password_hash FROM students WHERE roll_number=?");
  $stmt->execute([$d['roll_number']]);
  $u = $stmt->fetch();
  if($u && password_verify($d['password'], $u['password_hash'])) echo json_encode(['ok'=>true]);
  else echo json_encode(['ok'=>false,'message'=>'Invalid credentials']);
  exit;
}

if ($action === 'admin_register') {
  $d = json_input();
  $stmt = $pdo->prepare("INSERT INTO admins (name,user_id,email,password_hash) VALUES (?,?,?,?)");
  $stmt->execute([$d['name'],$d['user_id'],$d['email'],password_hash($d['password'], PASSWORD_BCRYPT)]);
  echo json_encode(['ok'=>true]); exit;
}

if ($action === 'admin_login') {
  $d = json_input();
  $stmt = $pdo->prepare("SELECT id,password_hash FROM admins WHERE user_id=?");
  $stmt->execute([$d['user_id']]);
  $u = $stmt->fetch();
  if($u && password_verify($d['password'], $u['password_hash'])) echo json_encode(['ok'=>true]);
  else echo json_encode(['ok'=>false,'message'=>'Invalid credentials']);
  exit;
}

echo json_encode(['ok'=>false,'message'=>'Unknown action']);
?>
