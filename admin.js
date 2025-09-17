
// Load books list
async function api(path, data={}, method='POST'){
  const opt = { method, headers: {'Content-Type':'application/json'} };
  if(method !== 'GET') opt.body = JSON.stringify(data);
  const res = await fetch(`api/${path}`, opt);
  return await res.json();
}

async function loadBooks(){
  const r = await api('books.php?action=list', {}, 'POST');
  const tbody = document.getElementById('adminBooksBody');
  tbody.innerHTML = (r.data||[]).map((b,i)=>`<tr>
    <td>${i+1}</td><td>${b.category}</td><td>${b.title}</td><td>${b.author}</td>
    <td>${b.isbn}</td><td>${b.branch}</td><td>${b.copies}</td>
    <td><button class="btn" onclick="delBook('${b.isbn}')">Delete</button></td>
  </tr>`).join('');
}
window.addEventListener('load', loadBooks);

document.getElementById('addBookForm').addEventListener('submit', async (e)=>{
  e.preventDefault();
  const data = Object.fromEntries(new FormData(e.target).entries());
  const r = await api('books.php?action=add', data);
  if(r.ok){ e.target.reset(); loadBooks(); }
  else alert(r.message||'Failed to add');
});

window.delBook = async function(isbn){
  if(!confirm('Delete this book?')) return;
  const r = await api('books.php?action=delete', { isbn });
  if(r.ok) loadBooks();
  else alert(r.message||'Failed');
};

document.getElementById('logoutAdmin').addEventListener('click', ()=>{
  alert('Logged out.');
  window.location.href = 'index.html';
});
