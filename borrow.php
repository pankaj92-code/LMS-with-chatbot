<?php
// api/borrow.php
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

if ($action === 'issue') {
  // expects member_id (roll_number) and isbn
  $stmt = $pdo->prepare("SELECT id FROM students WHERE roll_number=?");
  $stmt->execute([$d['member_id']]); $stu = $stmt->fetch();
  if(!$stu){ echo json_encode(['ok'=>false,'message'=>'Student not found']); exit; }
  $stmt = $pdo->prepare("SELECT id,copies FROM books WHERE isbn=?");
  $stmt->execute([$d['isbn']]); $book = $stmt->fetch();
  if(!$book){ echo json_encode(['ok'=>false,'message'=>'Book not found']); exit; }
  // reduce copies if available
  if((int)$book['copies'] <= 0){ echo json_encode(['ok'=>false,'message'=>'No copies available']); exit; }

  $issue = new DateTime(); $due = (clone $issue)->modify('+30 days');
  $stmt = $pdo->prepare("INSERT INTO borrows (student_id,book_id,issue_date,due_date) VALUES (?,?,?,?)");
  $stmt->execute([$stu['id'],$book['id'],$issue->format('Y-m-d'),$due->format('Y-m-d')]);

  $pdo->prepare("UPDATE books SET copies=copies-1 WHERE id=?")->execute([$book['id']]);

  echo json_encode(['ok'=>true]); exit;
}

if ($action === 'return') {
  // expects borrow_id
  $ret = (new DateTime())->format('Y-m-d');
  $stmt = $pdo->prepare("UPDATE borrows SET return_date=? WHERE id=?");
  $stmt->execute([$ret,$d['borrow_id']]);
  // increase copies back
  $pdo->prepare("UPDATE books b JOIN borrows br ON b.id=br.book_id SET b.copies=b.copies+1 WHERE br.id=?")->execute([$d['borrow_id']]);
  echo json_encode(['ok'=>true]); exit;
}

if ($action === 'lookup') {
  $mid = $d['member_id'] ?? '';
  $stmt = $pdo->prepare("SELECT id,name,roll_number FROM students WHERE roll_number=?");
  $stmt->execute([$mid]); $m = $stmt->fetch();
  if(!$m){ echo json_encode(['ok'=>false,'message'=>'Member not found']); exit; }
  $sql = "SELECT br.id, b.title, br.issue_date, br.due_date, br.return_date
          FROM borrows br JOIN books b ON br.book_id=b.id WHERE br.student_id=? ORDER BY br.issue_date DESC";
  $stmt = $pdo->prepare($sql); $stmt->execute([$m['id']]);
  $rows = $stmt->fetchAll();
  foreach($rows as &$r){
    $r['fine'] = fine_for($r['due_date'], $r['return_date']);
  }
  echo json_encode(['ok'=>true,'data'=>$rows]); exit;
}

echo json_encode(['ok'=>false,'message'=>'Unknown action']);
?>
