<?php
// api/report.php
require_once 'config.php';
$action = $_GET['action'] ?? '';
$d = json_input();

function fine_for($due, $returnDate){
  $due_dt = new DateTime($due);
  $ret_dt = $returnDate ? new DateTime($returnDate) : new DateTime();
  $diff = $due_dt->diff($ret_dt)->days;
  if ($ret_dt <= $due_dt) return 0;
  return $diff * 5; // ₹5/day
}

if ($action === 'history') {
  $mid = $d['member_id'] ?? '';
  $stmt = $pdo->prepare("SELECT id,name,roll_number FROM students WHERE roll_number=?");
  $stmt->execute([$mid]); $m = $stmt->fetch();
  if(!$m){ echo json_encode(['ok'=>false,'message'=>'Member not found']); exit; }
  $sql = "SELECT b.title, br.issue_date, br.due_date, br.return_date
          FROM borrows br JOIN books b ON br.book_id=b.id WHERE br.student_id=? ORDER BY br.issue_date DESC";
  $stmt = $pdo->prepare($sql); $stmt->execute([$m['id']]);
  $rows = $stmt->fetchAll();
  foreach($rows as &$r){
    $r['fine'] = fine_for($r['due_date'], $r['return_date']);
  }
  echo json_encode(['ok'=>true,'member'=>$m,'data'=>$rows]); exit;
}

echo json_encode(['ok'=>false,'message'=>'Unknown action']);
?>
