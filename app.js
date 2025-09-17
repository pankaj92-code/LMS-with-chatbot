// ======================
// UI Enhancements
// ======================

// Smooth scroll to features
document.getElementById('exploreBtn')?.addEventListener('click', () => {
  document.getElementById('features').scrollIntoView({behavior:'smooth'});
});

// Year in footer
document.getElementById('year').textContent = new Date().getFullYear();

// Auth modal handling
const authModal = document.getElementById('authModal');
document.getElementById('openAuth')?.addEventListener('click', () => authModal.showModal());
document.getElementById('closeAuth')?.addEventListener('click', () => authModal.close());
document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.pane').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.pane).classList.add('active');
  });
});

// ======================
// Particle Background
// ======================
const canvas = document.getElementById('bg-canvas');
if(canvas){
  const ctx = canvas.getContext('2d');
  let w, h, particles;
  function resize() {
    w = canvas.width = canvas.offsetWidth;
    h = canvas.height = canvas.offsetHeight;
    particles = Array.from({length: 80}, () => ({
      x: Math.random()*w, y: Math.random()*h, z: Math.random()*3+0.5,
      vx: (Math.random()-.5)*0.6, vy:(Math.random()-.5)*0.6
    }));
  }
  window.addEventListener('resize', resize); resize();
  function tick(){
    ctx.clearRect(0,0,w,h);
    for(const p of particles){
      p.x += p.vx * p.z; p.y += p.vy * p.z;
      if(p.x<0||p.x>w) p.vx*=-1;
      if(p.y<0||p.y>h) p.vy*=-1;
      const r = 1.2*p.z;
      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI*2);
      ctx.fillStyle = 'rgba(167,139,250,0.9)';
      ctx.fill();
    }
    requestAnimationFrame(tick);
  }
  tick();
}

// ======================
// API Helper
// ======================
const BASE_URL = "http://localhost:5000/api/";
async function api(path, data={}, method='POST'){
  const opt = { method, headers: {'Content-Type':'application/json'} };
  if(method !== 'GET') opt.body = JSON.stringify(data);
  const res = await fetch(BASE_URL + path, opt);
  return await res.json();
}

// ======================
// Books Search
// ======================
document.getElementById('searchBooks')?.addEventListener('click', async () => {
  const q = document.getElementById('bookQuery').value.trim();
  const branch = document.getElementById('bookBranch').value.trim();
  const r = await api('books.php?action=search', { q, branch });
  const box = document.getElementById('bookResult');
  box.innerHTML = r.data?.map(b => `<div><strong>${b.title}</strong> — ${b.author} | ISBN: ${b.isbn} | ${b.branch} | Copies: ${b.copies}</div>`).join('') || '<em>No results.</em>';
});

// ======================
// Member Lookup
// ======================
document.getElementById('searchMember')?.addEventListener('click', async () => {
  const id = document.getElementById('memberId').value.trim();
  const r = await api('members.php?action=status', { member_id: id });
  const box = document.getElementById('memberResult');
  if(!r.ok){ box.innerHTML = `<em>${r.message||'Not found'}</em>`; return; }
  box.innerHTML = `<div><strong>${r.data.name}</strong> (${r.data.roll_number})<br/>Current books: ${r.data.current_count} • Total issued: ${r.data.total_issued}</div>`;
});

// ======================
// Borrow Lookup
// ======================
document.getElementById('searchBorrow')?.addEventListener('click', async () => {
  const id = document.getElementById('borrowMemberId').value.trim();
  const r = await api('borrow.php?action=lookup', { member_id: id });
  const box = document.getElementById('borrowResult');
  if(!r.ok){ box.innerHTML = `<em>${r.message||'No records'}</em>`; return; }
  box.innerHTML = r.data.map(x => `<div>
    <strong>${x.title}</strong> — Issued: ${x.issue_date} • Due: ${x.due_date} • Returned: ${x.return_date||'-'} • Fine: ₹${x.fine}
  </div>`).join('');
});

// ======================
// Report
// ======================
document.getElementById('searchReport')?.addEventListener('click', async () => {
  const id = document.getElementById('reportMemberId').value.trim();
  const r = await api('report.php?action=history', { member_id: id });
  const box = document.getElementById('reportResult');
  if(!r.ok){ box.innerHTML = `<em>${r.message||'No history'}</em>`; return; }
  let html = `<h3>Issue History — ${r.member.name} (${r.member.roll_number})</h3>`;
  html += '<table><thead><tr><th>Title</th><th>Issue</th><th>Due</th><th>Return</th><th>Fine</th></tr></thead><tbody>';
  for(const x of r.data){
    html += `<tr><td>${x.title}</td><td>${x.issue_date}</td><td>${x.due_date}</td><td>${x.return_date||'-'}</td><td>₹${x.fine}</td></tr>`;
  }
  html += '</tbody></table>';
  box.innerHTML = html;
});
document.getElementById('printReport')?.addEventListener('click', () => window.print());

// ======================
// Catalogue Preview
// ======================
(async function loadCatalogue(){
  const tbody = document.getElementById('catalogueBody');
  if(!tbody) return;
  const r = await api('books.php?action=list', {}, 'POST');
  tbody.innerHTML = (r.data||[]).map(b => `<tr>
    <td>${b.title}</td><td>${b.author}</td><td>${b.isbn}</td><td>${b.category}</td><td>${b.branch}</td><td>${b.copies}</td>
  </tr>`).join('');
})();

// ======================
// Feedback
// ======================
document.getElementById('feedbackForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const fd = Object.fromEntries(new FormData(e.target).entries());
  const r = await api('feedback.php', fd);
  document.getElementById('feedbackMsg').textContent = r.ok ? 'Thank you for your feedback!' : (r.message||'Failed.');
  if(r.ok) e.target.reset();
});

// ======================
// Auth (Student/Admin)
// ======================
document.getElementById('studentRegisterForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  const r = await api('auth.php?action=student_register', data);
  document.getElementById('studentRegMsg').textContent = r.ok ? 'Registered successfully.' : (r.message||'Failed');
  if(r.ok) e.target.reset();
});
document.getElementById('studentLoginForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  const r = await api('auth.php?action=student_login', data);
  document.getElementById('studentLoginMsg').textContent = r.ok ? 'Login success.' : (r.message||'Invalid credentials');
  if(r.ok) window.location.href = 'student.php'; // Redirect to student dashboard or homepage
  });
// document.getElementById('studentLoginForm')?.addEventListener('submit', async (e) => {
//   e.preventDefault();
//   const data = Object.fromEntries(new FormData(e.target).entries());
//   const r = await api('auth.php?action=student_login', data);
//   const msg = document.getElementById('studentLoginMsg');
//   msg.textContent = r.ok ? 'Login success.' : (r.message||'Invalid credentials');

//   if(r.ok){
//     setTimeout(() => {
//       window.location.href = 'student_dashboard.html'; 
//     }, 1000); // 1 second delay
//   }
// });


document.getElementById('adminRegisterForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  const r = await api('auth.php?action=admin_register', data);
  document.getElementById('adminRegMsg').textContent = r.ok ? 'Admin registered.' : (r.message||'Failed');
  if(r.ok) e.target.reset();
});
document.getElementById('adminLoginForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  const r = await api('auth.php?action=admin_login', data);
  document.getElementById('adminLoginMsg').textContent = r.ok ? 'Login success. Opening panel...' : (r.message||'Invalid');
  if(r.ok) window.location.href = 'admin.html';
});

// ======================
// Chatbot Logic (Connected to Flask chat_proxy.php)
// ======================
const API_CHAT_URL = "http://127.0.0.1:5000/api/chat_proxy.php";
const API_GREETING_URL = "http://127.0.0.1:5000/greeting";

const chatbotLogo = document.getElementById("chatbot-logo");
const chatbotBox = document.getElementById("chatbot-box");
const closeBtn = document.getElementById("closeBtn");
const sendBtn = document.getElementById("sendBtn");
const voiceBtn = document.getElementById("voiceBtn");
const userInput = document.getElementById("userInput");
const chatBody = document.getElementById("chatbotMessages");

function addMessage(sender, text){
  let msg = document.createElement("div");
  msg.className = "msg " + sender;
  msg.textContent = text;
  chatBody.appendChild(msg);
  chatBody.scrollTop = chatBody.scrollHeight;
  if(sender === "bot") speakText(text);
}

function speakText(text){
  if('speechSynthesis' in window){
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = "en-IN";
    window.speechSynthesis.speak(utter);
  }
}

chatbotLogo?.addEventListener("click", async ()=>{
  chatbotBox.style.display="flex";
  chatbotLogo.style.display="none";
  try{
    const res = await fetch(API_GREETING_URL);
    const data = await res.json();
    addMessage("bot", data.reply);
  }catch{
    addMessage("bot","Hi! How may I help you?");
  }
});

closeBtn?.addEventListener("click",()=>{
  chatbotBox.style.display="none";
  chatbotLogo.style.display="flex";
  chatBody.innerHTML="";
});

async function sendMessage(message){
  addMessage("user", message);
  userInput.value = "";
  try{
    const res = await fetch(API_CHAT_URL,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body: JSON.stringify({ q: message })
    });
    const data = await res.json();
    addMessage("bot", data.answer);
  }catch{
    addMessage("bot","⚠️ Unable to connect to server.");
  }
}

sendBtn?.addEventListener("click",()=>{
  const msg = userInput.value.trim();
  if(msg) sendMessage(msg);
});

userInput?.addEventListener("keypress",(e)=>{
  if(e.key === "Enter"){
    const msg = userInput.value.trim();
    if(msg) sendMessage(msg);
  }
});

voiceBtn?.addEventListener("click",()=>{
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang="en-IN";
  recognition.start();
  recognition.onresult = (event)=>{
    const transcript = event.results[0][0].transcript;
    sendMessage(transcript);
  }
});
