<?php
// api/members.php
require_once 'config.php';
$action = $_GET['action'] ?? '';
$d = json_input();

if ($action === 'status') {
  $mid = $d['member_id'] ?? '';
  $stmt = $pdo->prepare("SELECT id,name,roll_number FROM students WHERE roll_number=?");
  $stmt->execute([$mid]);
  $m = $stmt->fetch();
  if(!$m){ echo json_encode(['ok'=>false,'message'=>'Member not found']); exit; }
  $stmt = $pdo->prepare("SELECT COUNT(*) AS c FROM borrows WHERE student_id=? AND return_date IS NULL");
  $stmt->execute([$m['id']]); $current = $stmt->fetch()['c'];
  $stmt = $pdo->prepare("SELECT COUNT(*) AS c FROM borrows WHERE student_id=?");
  $stmt->execute([$m['id']]); $total = $stmt->fetch()['c'];
  echo json_encode(['ok'=>true,'data'=>['name'=>$m['name'],'roll_number'=>$m['roll_number'],'current_count'=>$current,'total_issued'=>$total]]); exit;
}

echo json_encode(['ok'=>false,'message'=>'Unknown action']);
?>
