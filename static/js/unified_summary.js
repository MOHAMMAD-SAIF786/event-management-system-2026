/* ========================================================
   ROYAL EVENTS - UNIFIED CONTEXTUAL SUMMARY ACCORDION ENGINE
   ======================================================== */

function renderUnifiedSummaryCard(options = {}) {
    const summaryCard = document.querySelector('.summary-card');
    if (!summaryCard) return;

    // Detect current page context
    const path = window.location.pathname;
    if (path.includes('/booking/overview')) return;

    let page = options.currentPage || 'overview';
    if (path.includes('/room')) page = 'room';
    else if (path.includes('/halls/')) page = 'hall';
    else if (path.includes('/catering/')) page = 'catering';

    // Get latest cart state
    let cart = {};
    if (typeof RoyalCart !== 'undefined') {
        cart = RoyalCart.get();
    } else {
        try {
            cart = JSON.parse(sessionStorage.getItem('bookingData')) || {};
        } catch (e) {
            cart = {};
        }
    }

    // 1. Hall Booking
    let hallHtml = '';
    let hallPrice = 0;
    if (cart.hall) {
        hallPrice = parseFloat(cart.hall.price || 0);
        hallHtml = `
            <div class="summary-row">
                <div class="summary-left">
                    <h4>${cart.hall.name}</h4>
                    <small>Hall Reserved Successfully</small>
                </div>
                <div class="summary-price">₹${hallPrice.toLocaleString('en-IN')}</div>
            </div>
        `;
    } else {
        hallHtml = `
            <div class="summary-row">
                <div class="summary-left">
                    <small style="color: #94a3b8;">No hall selected</small>
                </div>
            </div>
        `;
    }

    // 2. Furniture & Seating
    let furnitureHtml = '';
    let furnitureTotal = 0;
    const furnitureItems = cart.furniture || [];
    if (furnitureItems.length > 0) {
        furnitureItems.forEach(item => {
            const itemTotal = (item.quantity || 1) * parseFloat(item.price || 0);
            furnitureTotal += itemTotal;
            furnitureHtml += `
                <div class="summary-row">
                    <div class="summary-left">
                        <h4>${item.name}</h4>
                        <small>${item.quantity || 1} × ₹${parseFloat(item.price || 0).toLocaleString('en-IN')}</small>
                    </div>
                    <div class="summary-price">₹${itemTotal.toLocaleString('en-IN')}</div>
                </div>
            `;
        });
    } else {
        furnitureHtml = `
            <div class="summary-row">
                <div class="summary-left">
                    <small style="color: #94a3b8;">No furniture selected</small>
                </div>
            </div>
        `;
    }

    // 3. Stage Decoration
    let stageHtml = '';
    let stagePrice = 0;
    if (cart.stage) {
        stagePrice = parseFloat(cart.stage.price || 0);
        stageHtml = `
            <div class="summary-row">
                <div class="summary-left">
                    <h4>${cart.stage.name}</h4>
                    <small>Stage Decoration Selected</small>
                </div>
                <div class="summary-price">₹${stagePrice.toLocaleString('en-IN')}</div>
            </div>
        `;
    } else {
        stageHtml = `
            <div class="summary-row">
                <div class="summary-left">
                    <small style="color: #94a3b8;">No stage selected</small>
                </div>
            </div>
        `;
    }

    // 4. Additional Services
    let servicesHtml = '';
    let servicesTotal = 0;
    const servicesList = cart.services || [];
    if (servicesList.length > 0) {
        servicesList.forEach(srv => {
            const srvPrice = parseFloat(srv.price || 0);
            servicesTotal += srvPrice;
            servicesHtml += `
                <div class="summary-row">
                    <div class="summary-left">
                        <h4>${srv.name}</h4>
                        <small>Service Added</small>
                    </div>
                    <div class="summary-price">₹${srvPrice.toLocaleString('en-IN')}</div>
                </div>
            `;
        });
    } else {
        servicesHtml = `
            <div class="summary-row">
                <div class="summary-left">
                    <small style="color: #94a3b8;">No additional services selected</small>
                </div>
            </div>
        `;
    }

    // 5. Room Booking
    let roomHtml = '';
    let roomTotal = 0;
    const roomItems = cart.rooms || [];
    if (roomItems.length > 0) {
        roomItems.forEach(rm => {
            const rmTotal = (rm.quantity || 1) * parseFloat(rm.price || 0);
            roomTotal += rmTotal;
            roomHtml += `
                <div class="summary-row">
                    <div class="summary-left">
                        <h4>${rm.name}</h4>
                        <small>${rm.quantity || 1} × ₹${parseFloat(rm.price || 0).toLocaleString('en-IN')}</small>
                    </div>
                    <div class="summary-price">₹${rmTotal.toLocaleString('en-IN')}</div>
                </div>
            `;
        });
    } else {
        roomHtml = `
            <div class="summary-row">
                <div class="summary-left">
                    <small style="color: #94a3b8;">No rooms selected</small>
                </div>
            </div>
        `;
    }

    // 6. Catering Package
    let cateringHtml = '';
    let cateringTotal = 0;
    const catering = cart.catering || null;
    if (catering && (catering.name || catering.total > 0 || (catering.selectedItems && catering.selectedItems.length > 0))) {
        cateringTotal = parseFloat(catering.total || 0);
        let itemsGrouped = {};
        if (catering.selectedItems && Array.isArray(catering.selectedItems)) {
            catering.selectedItems.forEach(it => {
                const sec = it.section || 'Menu Items';
                if (!itemsGrouped[sec]) itemsGrouped[sec] = [];
                itemsGrouped[sec].push(it.item);
            });
        }
        let menuListHtml = '';
        for (let s in itemsGrouped) {
            menuListHtml += `<div style="font-size:12px; color:#64748b; margin-top:4px;"><strong>${s}:</strong> ${itemsGrouped[s].join(', ')}</div>`;
        }

        cateringHtml = `
            <div class="summary-row">
                <div class="summary-left">
                    <h4>${catering.name || 'Selected Catering Package'}</h4>
                    <small>${catering.guestCount || 0} Guests × ₹${catering.pricePerPlate || 0}/Plate</small>
                    ${menuListHtml}
                </div>
                <div class="summary-price">₹${cateringTotal.toLocaleString('en-IN')}</div>
            </div>
        `;
    } else {
        cateringHtml = `
            <div class="summary-row">
                <div class="summary-left">
                    <small style="color: #94a3b8;">No catering selected</small>
                </div>
            </div>
        `;
    }

    // Calculate Grand Total
    const grandTotal = hallPrice + furnitureTotal + stagePrice + servicesTotal + roomTotal + cateringTotal;

    // Helper accordion generators
    const getHallAccordion = () => `
        <div class="summary-box ${cart.hall ? 'active' : ''}">
            <div class="summary-title accordion-title">
                <div><i class="fa-solid fa-building-columns"></i> Hall Booking</div>
                <div class="accordion-right">
                    <strong>₹${hallPrice.toLocaleString('en-IN')}</strong>
                    <i class="fa-solid fa-chevron-down accordion-icon"></i>
                </div>
            </div>
            <div class="summary-body" style="display: ${cart.hall ? 'block' : 'none'};">
                ${hallHtml}
            </div>
        </div>
    `;

    const getFurnitureAccordion = () => `
        <div class="summary-box ${furnitureTotal > 0 ? 'active' : ''}">
            <div class="summary-title accordion-title">
                <div><i class="fa-solid fa-chair"></i> Furniture & Seating</div>
                <div class="accordion-right">
                    <strong>₹${furnitureTotal.toLocaleString('en-IN')}</strong>
                    <i class="fa-solid fa-chevron-down accordion-icon"></i>
                </div>
            </div>
            <div class="summary-body" style="display: ${furnitureTotal > 0 ? 'block' : 'none'};">
                ${furnitureHtml}
            </div>
        </div>
    `;

    const getStageAccordion = () => `
        <div class="summary-box ${stagePrice > 0 ? 'active' : ''}">
            <div class="summary-title accordion-title">
                <div><i class="fa-solid fa-masks-theater"></i> Stage Decoration</div>
                <div class="accordion-right">
                    <strong>₹${stagePrice.toLocaleString('en-IN')}</strong>
                    <i class="fa-solid fa-chevron-down accordion-icon"></i>
                </div>
            </div>
            <div class="summary-body" style="display: ${stagePrice > 0 ? 'block' : 'none'};">
                ${stageHtml}
            </div>
        </div>
    `;

    const getServicesAccordion = () => `
        <div class="summary-box ${servicesTotal > 0 ? 'active' : ''}">
            <div class="summary-title accordion-title">
                <div><i class="fa-solid fa-bell-concierge"></i> Additional Services</div>
                <div class="accordion-right">
                    <strong>₹${servicesTotal.toLocaleString('en-IN')}</strong>
                    <i class="fa-solid fa-chevron-down accordion-icon"></i>
                </div>
            </div>
            <div class="summary-body" style="display: ${servicesTotal > 0 ? 'block' : 'none'};">
                ${servicesHtml}
            </div>
        </div>
    `;

    const getRoomAccordion = () => `
        <div class="summary-box ${roomTotal > 0 ? 'active' : ''}">
            <div class="summary-title accordion-title">
                <div><i class="fa-solid fa-bed"></i> Room Booking</div>
                <div class="accordion-right">
                    <strong>₹${roomTotal.toLocaleString('en-IN')}</strong>
                    <i class="fa-solid fa-chevron-down accordion-icon"></i>
                </div>
            </div>
            <div class="summary-body" style="display: ${roomTotal > 0 ? 'block' : 'none'};">
                ${roomHtml}
            </div>
        </div>
    `;

    const getCateringAccordion = () => `
        <div class="summary-box ${cateringTotal > 0 ? 'active' : ''}">
            <div class="summary-title accordion-title">
                <div><i class="fa-solid fa-utensils"></i> Catering Package</div>
                <div class="accordion-right">
                    <strong>₹${cateringTotal.toLocaleString('en-IN')}</strong>
                    <i class="fa-solid fa-chevron-down accordion-icon"></i>
                </div>
            </div>
            <div class="summary-body" style="display: ${cateringTotal > 0 ? 'block' : 'none'};">
                ${cateringHtml}
            </div>
        </div>
    `;

    // Compact Summary Builders
    let compactOtherHtml = '';

    if (page === 'room') {
        // Room Page: Primary = Room Accordion, Compact = Hall, Catering, Stage/Furniture/Services
        compactOtherHtml = `
            <div class="compact-summary-card">
                <div class="compact-summary-header"><i class="fa-solid fa-list-check"></i> Other Selections Summary</div>
                <div class="compact-summary-body">
                    <div class="compact-row">
                        <div class="compact-row-left">
                            <span class="compact-label"><i class="fa-solid fa-building-columns"></i> Hall</span>
                            <span class="compact-name">${cart.hall ? cart.hall.name : 'Not selected'}</span>
                        </div>
                        <span class="compact-price">₹${hallPrice.toLocaleString('en-IN')}</span>
                    </div>
                    ${stagePrice > 0 ? `
                    <div class="compact-row">
                        <div class="compact-row-left">
                            <span class="compact-label"><i class="fa-solid fa-masks-theater"></i> Stage</span>
                            <span class="compact-name">${cart.stage.name}</span>
                        </div>
                        <span class="compact-price">₹${stagePrice.toLocaleString('en-IN')}</span>
                    </div>` : ''}
                    ${furnitureTotal > 0 ? `
                    <div class="compact-row">
                        <div class="compact-row-left">
                            <span class="compact-label"><i class="fa-solid fa-chair"></i> Furniture</span>
                            <span class="compact-name">${furnitureItems.length} items</span>
                        </div>
                        <span class="compact-price">₹${furnitureTotal.toLocaleString('en-IN')}</span>
                    </div>` : ''}
                    ${servicesTotal > 0 ? `
                    <div class="compact-row">
                        <div class="compact-row-left">
                            <span class="compact-label"><i class="fa-solid fa-icons"></i> Services</span>
                            <span class="compact-name">${servicesList.length} items</span>
                        </div>
                        <span class="compact-price">₹${servicesTotal.toLocaleString('en-IN')}</span>
                    </div>` : ''}
                    <div class="compact-row">
                        <div class="compact-row-left">
                            <span class="compact-label"><i class="fa-solid fa-utensils"></i> Catering</span>
                            <span class="compact-name">${catering && catering.name ? catering.name : 'Not selected'}</span>
                        </div>
                        <span class="compact-price">₹${cateringTotal.toLocaleString('en-IN')}</span>
                    </div>
                </div>
            </div>
        `;
    } else if (page === 'catering') {
        // Catering Page: Primary = Catering Accordion, Compact = Hall, Rooms, Stage/Furniture/Services
        compactOtherHtml = `
            <div class="compact-summary-card">
                <div class="compact-summary-header"><i class="fa-solid fa-list-check"></i> Other Selections Summary</div>
                <div class="compact-summary-body">
                    <div class="compact-row">
                        <div class="compact-row-left">
                            <span class="compact-label"><i class="fa-solid fa-building-columns"></i> Hall</span>
                            <span class="compact-name">${cart.hall ? cart.hall.name : 'Not selected'}</span>
                        </div>
                        <span class="compact-price">₹${hallPrice.toLocaleString('en-IN')}</span>
                    </div>
                    <div class="compact-row">
                        <div class="compact-row-left">
                            <span class="compact-label"><i class="fa-solid fa-bed"></i> Rooms</span>
                            <span class="compact-name">${roomItems.length > 0 ? roomItems.length + ' types' : 'Not selected'}</span>
                        </div>
                        <span class="compact-price">₹${roomTotal.toLocaleString('en-IN')}</span>
                    </div>
                    ${stagePrice > 0 ? `
                    <div class="compact-row">
                        <div class="compact-row-left">
                            <span class="compact-label"><i class="fa-solid fa-masks-theater"></i> Stage</span>
                            <span class="compact-name">${cart.stage.name}</span>
                        </div>
                        <span class="compact-price">₹${stagePrice.toLocaleString('en-IN')}</span>
                    </div>` : ''}
                    ${furnitureTotal > 0 ? `
                    <div class="compact-row">
                        <div class="compact-row-left">
                            <span class="compact-label"><i class="fa-solid fa-chair"></i> Furniture</span>
                            <span class="compact-name">${furnitureItems.length} items</span>
                        </div>
                        <span class="compact-price">₹${furnitureTotal.toLocaleString('en-IN')}</span>
                    </div>` : ''}
                </div>
            </div>
        `;
    } else if (page === 'hall') {
        // Hall Page: Primary = Hall, Furniture, Stage, Services. Compact = Rooms, Catering
        compactOtherHtml = `
            <div class="compact-summary-card">
                <div class="compact-summary-header"><i class="fa-solid fa-list-check"></i> Stay & Dining Summary</div>
                <div class="compact-summary-body">
                    <div class="compact-row">
                        <div class="compact-row-left">
                            <span class="compact-label"><i class="fa-solid fa-bed"></i> Rooms</span>
                            <span class="compact-name">${roomItems.length > 0 ? roomItems.length + ' types' : 'Not selected'}</span>
                        </div>
                        <span class="compact-price">₹${roomTotal.toLocaleString('en-IN')}</span>
                    </div>
                    <div class="compact-row">
                        <div class="compact-row-left">
                            <span class="compact-label"><i class="fa-solid fa-utensils"></i> Catering</span>
                            <span class="compact-name">${catering && catering.name ? catering.name : 'Not selected'}</span>
                        </div>
                        <span class="compact-price">₹${cateringTotal.toLocaleString('en-IN')}</span>
                    </div>
                </div>
            </div>
        `;
    }

    // Build 2-column side-by-side layout content
    let contentHtml = '';
    if (page === 'room') {
        contentHtml = `
            <div class="summary-card-content">
                <div class="summary-primary-col">
                    ${getRoomAccordion()}
                </div>
                <div class="summary-side-col">
                    ${compactOtherHtml}
                </div>
            </div>
        `;
    } else if (page === 'catering') {
        contentHtml = `
            <div class="summary-card-content">
                <div class="summary-primary-col">
                    ${getCateringAccordion()}
                </div>
                <div class="summary-side-col">
                    ${compactOtherHtml}
                </div>
            </div>
        `;
    } else if (page === 'hall') {
        contentHtml = `
            <div class="summary-card-content">
                <div class="summary-primary-col">
                    ${getHallAccordion()}
                    ${getFurnitureAccordion()}
                    ${getStageAccordion()}
                    ${getServicesAccordion()}
                </div>
                <div class="summary-side-col">
                    ${compactOtherHtml}
                </div>
            </div>
        `;
    } else {
        contentHtml = `
            <div class="summary-card-content single-col">
                <div class="summary-primary-col">
                    ${getHallAccordion()}
                    ${getFurnitureAccordion()}
                    ${getStageAccordion()}
                    ${getServicesAccordion()}
                    ${getRoomAccordion()}
                    ${getCateringAccordion()}
                </div>
            </div>
        `;
    }

    // Render HTML into summaryCard
    summaryCard.innerHTML = `
        <div class="summary-header">
            <h2>Event Summary</h2>
            <p>Your complete booking details</p>
        </div>

        ${contentHtml}

        <!-- Grand Total -->
        <div class="grand-total">
            <span>Total Amount</span>
            <strong>₹${grandTotal.toLocaleString('en-IN')}</strong>
        </div>

        <!-- Buttons Footer -->
        <div class="summary-buttons">
            <a href="/halls/" class="summary-btn"><i class="fa-solid fa-building-columns"></i> Select Hall</a>
            <a href="/room/" class="summary-btn"><i class="fa-solid fa-bed"></i> Select Rooms</a>
            <a href="/catering/" class="summary-btn"><i class="fa-solid fa-utensils"></i> Select Catering</a>
            <button type="button" class="summary-btn final-btn" onclick="goToBookingOverview()"><i class="fa-solid fa-circle-check"></i> Confirm Booking</button>
        </div>
    `;

    // Attach Accordion Toggle Click Handlers
    summaryCard.querySelectorAll('.accordion-title').forEach(title => {
        title.addEventListener('click', function() {
            const box = this.closest('.summary-box');
            if (!box) return;
            box.classList.toggle('active');
            const body = box.querySelector('.summary-body');
            if (body) {
                body.style.display = box.classList.contains('active') ? 'block' : 'none';
            }
        });
    });
}

function goToBookingOverview() {
    let cart = {};
    if (typeof RoyalCart !== 'undefined') {
        cart = RoyalCart.get();
    } else {
        try {
            cart = JSON.parse(sessionStorage.getItem('bookingData')) || {};
        } catch (e) {
            cart = {};
        }
    }
    sessionStorage.setItem('bookingData', JSON.stringify(cart));
    window.location.href = '/booking/overview/';
}

document.addEventListener('DOMContentLoaded', function() {
    renderUnifiedSummaryCard();
});
