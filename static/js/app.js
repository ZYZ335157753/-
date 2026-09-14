const state = { menu: [], cart: [] };
const money = value => `¥${value}`;
const byId = id => document.getElementById(id);

async function loadMenu() {
  const response = await fetch('/api/v1/menu');
  const data = await response.json(); state.menu = data.products;
  byId('products').innerHTML = state.menu.map(product => `<article class="product"><div class="product-top"><div><h3>${product.name}</h3><p>${product.description}</p></div><span class="badge">${product.badge}</span></div><div class="product-bottom"><strong class="price">${money(product.price)}</strong><button class="add" aria-label="加入${product.name}" data-add="${product.id}">+</button></div></article>`).join('');
}
function changeItem(id, delta) {
  const item = state.cart.find(entry => entry.product_id === id);
  if (!item && delta > 0) state.cart.push({ product_id: id, quantity: 1 });
  else if (item) { item.quantity += delta; if (item.quantity <= 0) state.cart = state.cart.filter(entry => entry !== item); }
  renderCart();
}
function renderCart() {
  const cartItems = byId('cart-items'); const cartCount = state.cart.reduce((sum, item) => sum + item.quantity, 0);
  const total = state.cart.reduce((sum, item) => sum + state.menu.find(product => product.id === item.product_id).price * item.quantity, 0);
  byId('cart-count').textContent = `${cartCount} 杯`; byId('cart-total').textContent = money(total); byId('modal-total').textContent = total;
  byId('checkout').disabled = cartCount === 0;
  cartItems.innerHTML = cartCount ? state.cart.map(item => { const product = state.menu.find(p => p.id === item.product_id); return `<div class="cart-row"><div><strong>${product.name}</strong><div class="quantity"><button data-change="${product.id}" data-delta="-1">−</button><span>${item.quantity} 杯</span><button data-change="${product.id}" data-delta="1">+</button></div></div><strong>${money(product.price * item.quantity)}</strong></div>`; }).join('') : '<p class="empty">还没有选择饮品</p>';
}
document.addEventListener('click', event => { const add = event.target.dataset.add; const change = event.target.dataset.change; if (add) changeItem(add, 1); if (change) changeItem(change, Number(event.target.dataset.delta)); if (event.target.id === 'checkout') byId('checkout-modal').hidden = false; if (event.target.dataset.close !== undefined) byId('checkout-modal').hidden = true; });
byId('order-form').addEventListener('submit', async event => { event.preventDefault(); const form = new FormData(event.target); const response = await fetch('/api/v1/orders', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({ customer_name:form.get('customer_name'), phone:form.get('phone'), items:state.cart }) }); const data = await response.json(); if (!response.ok) return alert(data.error || '下单失败'); state.cart = []; renderCart(); byId('checkout-modal').hidden = true; event.target.reset(); byId('lookup-result').innerHTML = `<div class="lookup-card">支付成功，订单号：<strong>${data.order.order_no}</strong>。饮品正在制作，祝你品茶愉快。</div>`; document.location.hash = 'lookup'; });
byId('lookup-form').addEventListener('submit', async event => { event.preventDefault(); const orderNo = byId('order-no').value.trim(); const response = await fetch(`/api/v1/orders/${encodeURIComponent(orderNo)}`); const data = await response.json(); byId('lookup-result').innerHTML = response.ok ? `<div class="lookup-card"><strong>${data.order.order_no}</strong> · ${data.order.status === 'preparing' ? '正在制作' : data.order.status}<br>${data.order.items.map(item => `${item.name} × ${item.quantity}`).join('、')} · 共 ${money(data.order.total)}</div>` : `<p class="error">${data.error || '查询失败'}</p>`; });
loadMenu().catch(() => { byId('products').innerHTML = '<p class="error">茶单加载失败，请刷新页面重试。</p>'; });

