// BizFlow AI - Professional Frontend & POS Checkout Logic

document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons if available
    if (window.lucide) {
        lucide.createIcons();
    }

    // Modal Handlers
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.add('active');
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('active');
    };

    // Close modal on click outside
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.remove('active');
            }
        });
    });

    // Table Search Filter
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(input => {
        input.addEventListener('keyup', function() {
            const query = this.value.toLowerCase();
            const targetTableId = this.getAttribute('data-table');
            const table = document.getElementById(targetTableId);
            if (!table) return;

            const rows = table.querySelectorAll('tbody tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    });

    // Payment Method Chip Selection Handler
    window.selectPayMethod = function(chipEl) {
        document.querySelectorAll('.pay-method-chip').forEach(c => c.classList.remove('active'));
        chipEl.classList.add('active');
        const radio = chipEl.querySelector('input[type="radio"]');
        if (radio) radio.checked = true;
    };

    document.querySelectorAll('.pay-method-chip').forEach(chip => {
        chip.addEventListener('click', function() {
            window.selectPayMethod(this);
        });
    });
});

// POS Checkout Calculation Logic
let posItems = [];

window.addPosItem = function() {
    const productSelect = document.getElementById('pos_product_select');
    const quantityInput = document.getElementById('pos_quantity_input');
    
    if (!productSelect || !productSelect.value) {
        alert("Please select a product.");
        return;
    }

    const selectedOption = productSelect.options[productSelect.selectedIndex];
    const productId = parseInt(productSelect.value);
    const productName = selectedOption.getAttribute('data-name');
    const price = parseFloat(selectedOption.getAttribute('data-price'));
    const stock = parseInt(selectedOption.getAttribute('data-stock'));
    const quantity = parseInt(quantityInput.value) || 1;

    if (quantity <= 0) {
        alert("Quantity must be at least 1.");
        return;
    }

    if (quantity > stock) {
        alert(`Insufficient stock! Only ${stock} units available.`);
        return;
    }

    // Check if item already exists in posItems
    const existingIndex = posItems.findIndex(i => i.product_id === productId);
    if (existingIndex > -1) {
        if (posItems[existingIndex].quantity + quantity > stock) {
            alert(`Cannot add more than total stock (${stock} units).`);
            return;
        }
        posItems[existingIndex].quantity += quantity;
        posItems[existingIndex].subtotal = posItems[existingIndex].quantity * price;
    } else {
        posItems.push({
            product_id: productId,
            product_name: productName,
            unit_price: price,
            quantity: quantity,
            stock: stock,
            subtotal: price * quantity
        });
    }

    renderPosTable();
};

window.quickAddProduct = function(productId, productName, price, stock) {
    if (stock <= 0) {
        alert("Product is out of stock!");
        return;
    }

    const existingIndex = posItems.findIndex(i => i.product_id === productId);
    if (existingIndex > -1) {
        if (posItems[existingIndex].quantity + 1 > stock) {
            alert(`Cannot add more than total stock (${stock} units).`);
            return;
        }
        posItems[existingIndex].quantity += 1;
        posItems[existingIndex].subtotal = posItems[existingIndex].quantity * price;
    } else {
        posItems.push({
            product_id: productId,
            product_name: productName,
            unit_price: price,
            quantity: 1,
            stock: stock,
            subtotal: price
        });
    }

    renderPosTable();
};

window.updateQty = function(index, delta) {
    if (!posItems[index]) return;
    const newQty = posItems[index].quantity + delta;
    if (newQty <= 0) {
        posItems.splice(index, 1);
    } else if (newQty > posItems[index].stock) {
        alert(`Cannot exceed total available stock (${posItems[index].stock} units).`);
    } else {
        posItems[index].quantity = newQty;
        posItems[index].subtotal = posItems[index].quantity * posItems[index].unit_price;
    }
    renderPosTable();
};

window.removePosItem = function(index) {
    posItems.splice(index, 1);
    renderPosTable();
};

window.renderPosTable = function() {
    const tbody = document.getElementById('pos_items_tbody');
    const subtotalEl = document.getElementById('pos_subtotal');
    const discountEl = document.getElementById('pos_discount_input');
    const grandTotalEl = document.getElementById('pos_grand_total');
    const itemsJsonInput = document.getElementById('pos_items_json');

    if (!tbody) return;

    tbody.innerHTML = '';
    let rawSubtotal = 0.0;

    if (posItems.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted); padding: 24px 0;">No items added to current sale yet. Select a product or click quick cards above.</td></tr>`;
    } else {
        posItems.forEach((item, index) => {
            rawSubtotal += item.subtotal;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b style="color:white;">${item.product_name}</b></td>
                <td>₹${item.unit_price.toFixed(2)}</td>
                <td>
                    <div style="display:inline-flex; align-items:center; gap:6px; background:rgba(255,255,255,0.06); padding:4px 8px; border-radius:8px;">
                        <button type="button" class="qty-btn" onclick="updateQty(${index}, -1)">-</button>
                        <span style="font-weight:700; color:white; min-width:20px; text-align:center;">${item.quantity}</span>
                        <button type="button" class="qty-btn" onclick="updateQty(${index}, 1)">+</button>
                    </div>
                </td>
                <td><strong style="color:#34D399;">₹${item.subtotal.toFixed(2)}</strong></td>
                <td>
                    <button type="button" class="btn btn-rose btn-sm" onclick="removePosItem(${index})" title="Remove item">
                        Remove
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    const discount = parseFloat(discountEl ? discountEl.value : 0) || 0;
    const grandTotal = Math.max(0, rawSubtotal - discount);

    if (subtotalEl) subtotalEl.textContent = `₹${rawSubtotal.toFixed(2)}`;
    if (grandTotalEl) grandTotalEl.textContent = `₹${grandTotal.toFixed(2)}`;
    if (itemsJsonInput) itemsJsonInput.value = JSON.stringify(posItems);
};

// Open Quick Digital Receipt Modal
window.openReceiptModal = function(saleId, customerName, totalAmount, dateStr, pdfUrl) {
    const modal = document.getElementById('receiptModal');
    if (!modal) return;

    document.getElementById('receipt_sale_id').textContent = `#SALE-${saleId}`;
    document.getElementById('receipt_customer').textContent = customerName;
    document.getElementById('receipt_total').textContent = `₹${parseFloat(totalAmount).toFixed(2)}`;
    document.getElementById('receipt_date').textContent = dateStr;
    
    const pdfBtn = document.getElementById('receipt_pdf_btn');
    if (pdfBtn) pdfBtn.href = pdfUrl;

    modal.classList.add('active');
};
