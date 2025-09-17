<?php
// api/feedback.php
require_once 'config.php';
$d = json_input();
$stmt = $pdo->prepare("INSERT INTO feedback (name,email,branch,feedback) VALUES (?,?,?,?)");
$stmt->execute([$d['name']??'', $d['email']??'', $d['branch']??'', $d['feedback']??'']);
echo json_encode(['ok'=>true]);
?>
