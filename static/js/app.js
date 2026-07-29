// Local Business CRM Frontend Interactivity Script

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
            subtotal: price * quantity
        });
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
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted);">No items added to current sale.</td></tr>`;
    } else {
        posItems.forEach((item, index) => {
            rawSubtotal += item.subtotal;
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><b>${item.product_name}</b></td>
                <td>₹${item.unit_price.toFixed(2)}</td>
                <td>${item.quantity}</td>
                <td>₹${item.subtotal.toFixed(2)}</td>
                <td>
                    <button type="button" class="btn btn-danger btn-sm" onclick="removePosItem(${index})">Remove</button>
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

// Copy AI Message to Clipboard
window.copyToClipboard = function(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    navigator.clipboard.writeText(el.innerText || el.textContent).then(() => {
        alert("AI message copied to clipboard!");
    }).catch(err => {
        console.error("Copy failed", err);
    });
};
