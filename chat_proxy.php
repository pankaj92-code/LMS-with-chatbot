<?php
// api/chat_proxy.php
// This proxies the frontend chat to the Python chatbot microservice.
// Adjust $chatbot_url if your Python service runs elsewhere.
require_once 'config.php';
$d = json_input();
$q = $d['q'] ?? '';

$chatbot_url = 'http://127.0.0.1:5055/ask'; // Flask default from chatbot.py

$ch = curl_init($chatbot_url);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode(['q'=>$q]));
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$resp = curl_exec($ch);
if ($resp === false) {
  echo json_encode(['answer'=>'Chatbot service offline. Please start Python chatbot.']); exit;
}
curl_close($ch);
echo $resp;
?>
