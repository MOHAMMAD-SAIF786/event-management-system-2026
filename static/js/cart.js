/* =========================================
   EXPO DESIGN SYSTEM - PERSISTENT CART ENGINE
   ========================================= */

const CART_STORAGE_KEY = "royalEventCart";

const RoyalCart = {
    getDefaultCart() {
        return {
            hall: null,
            rooms: [],
            catering: null,
            stage: null,
            furniture: [],
            services: []
        };
    },

    get() {
        try {
            const raw = localStorage.getItem(CART_STORAGE_KEY);
            if (!raw) return this.getDefaultCart();
            const parsed = JSON.parse(raw);
            return {
                hall: parsed.hall || null,
                rooms: Array.isArray(parsed.rooms) ? parsed.rooms : [],
                catering: parsed.catering || null,
                stage: parsed.stage || null,
                furniture: Array.isArray(parsed.furniture) ? parsed.furniture : [],
                services: Array.isArray(parsed.services) ? parsed.services : []
            };
        } catch (e) {
            console.error("Error reading cart:", e);
            return this.getDefaultCart();
        }
    },

    save(cartData) {
        try {
            localStorage.setItem(CART_STORAGE_KEY, JSON.stringify(cartData));
            sessionStorage.setItem("bookingData", JSON.stringify(cartData));
            this.updateHeaderBadge();
            this.renderSidebar();
            if (typeof renderFullCartPage === "function") {
                renderFullCartPage();
            }
        } catch (e) {
            console.error("Error saving cart:", e);
        }
    },

    clear() {
        localStorage.removeItem(CART_STORAGE_KEY);
        sessionStorage.removeItem("bookingData");
        this.updateHeaderBadge();
        this.renderSidebar();
        if (typeof renderFullCartPage === "function") {
            renderFullCartPage();
        }
    },

    // Hall
    setHall(hallObj, autoOpen = true) {
        const cart = this.get();
        cart.hall = hallObj;
        this.save(cart);
        if (autoOpen) openCartSidebar();
    },
    removeHall() {
        const cart = this.get();
        cart.hall = null;
        this.save(cart);
    },

    // Rooms
    addRoom(roomObj, autoOpen = true) {
        const cart = this.get();
        const idx = cart.rooms.findIndex(r => String(r.id) === String(roomObj.id));
        if (idx > -1) {
            cart.rooms[idx].quantity = (cart.rooms[idx].quantity || 1) + 1;
            cart.rooms[idx].total = cart.rooms[idx].quantity * parseFloat(cart.rooms[idx].price);
        } else {
            cart.rooms.push({
                id: roomObj.id,
                name: roomObj.name,
                price: parseFloat(roomObj.price),
                quantity: roomObj.quantity || 1,
                total: (roomObj.quantity || 1) * parseFloat(roomObj.price)
            });
        }
        this.save(cart);
        if (autoOpen) openCartSidebar();
    },
    updateRoomQty(roomId, delta) {
        const cart = this.get();
        const idx = cart.rooms.findIndex(r => String(r.id) === String(roomId));
        if (idx > -1) {
            cart.rooms[idx].quantity = (cart.rooms[idx].quantity || 1) + delta;
            if (cart.rooms[idx].quantity <= 0) {
                cart.rooms.splice(idx, 1);
            } else {
                cart.rooms[idx].total = cart.rooms[idx].quantity * parseFloat(cart.rooms[idx].price);
            }
            this.save(cart);
        }
    },
    removeRoom(roomId) {
        const cart = this.get();
        cart.rooms = cart.rooms.filter(r => String(r.id) !== String(roomId));
        this.save(cart);
    },

    // Catering
    setCatering(cateringObj, autoOpen = true) {
        const cart = this.get();
        cart.catering = cateringObj;
        this.save(cart);
        if (autoOpen) openCartSidebar();
    },
    updateCateringGuests(delta) {
        const cart = this.get();
        if (!cart.catering) return;
        let current = parseInt(cart.catering.guestCount) || 100;
        let next = Math.max(1, current + delta);
        cart.catering.guestCount = next;
        let ppp = parseFloat(cart.catering.pricePerPlate) || parseFloat(cart.catering.price) || 0;
        cart.catering.pricePerPlate = ppp;
        cart.catering.total = next * ppp;
        this.save(cart);
    },
    setCateringGuests(count) {
        const cart = this.get();
        if (!cart.catering) return;
        let next = Math.max(1, parseInt(count) || 1);
        cart.catering.guestCount = next;
        let ppp = parseFloat(cart.catering.pricePerPlate) || parseFloat(cart.catering.price) || 0;
        cart.catering.pricePerPlate = ppp;
        cart.catering.total = next * ppp;
        this.save(cart);
    },
    removeCatering() {
        const cart = this.get();
        cart.catering = null;
        this.save(cart);
    },

    // Stage
    setStage(stageObj, autoOpen = true) {
        const cart = this.get();
        cart.stage = stageObj;
        this.save(cart);
        if (autoOpen) openCartSidebar();
    },
    removeStage() {
        const cart = this.get();
        cart.stage = null;
        this.save(cart);
    },

    // Furniture
    addFurniture(itemObj, autoOpen = true) {
        const cart = this.get();
        const idx = cart.furniture.findIndex(f => String(f.id) === String(itemObj.id));
        if (itemObj.quantity <= 0) {
            if (idx > -1) cart.furniture.splice(idx, 1);
        } else {
            if (idx > -1) {
                cart.furniture[idx] = itemObj;
            } else {
                cart.furniture.push(itemObj);
            }
        }
        this.save(cart);
        if (autoOpen) openCartSidebar();
    },
    updateFurnitureQty(itemId, delta) {
        const cart = this.get();
        const idx = cart.furniture.findIndex(f => String(f.id) === String(itemId));
        if (idx > -1) {
            cart.furniture[idx].quantity = (cart.furniture[idx].quantity || 1) + delta;
            if (cart.furniture[idx].quantity <= 0) {
                cart.furniture.splice(idx, 1);
            } else {
                cart.furniture[idx].total = cart.furniture[idx].quantity * parseFloat(cart.furniture[idx].price);
            }
            this.save(cart);
        }
    },
    removeFurniture(itemId) {
        const cart = this.get();
        cart.furniture = cart.furniture.filter(f => String(f.id) !== String(itemId));
        this.save(cart);
    },

    // Services
    addService(serviceObj, autoOpen = true) {
        const cart = this.get();
        const idx = cart.services.findIndex(s => String(s.id) === String(serviceObj.id));
        if (idx === -1) {
            cart.services.push(serviceObj);
        }
        this.save(cart);
        if (autoOpen) openCartSidebar();
    },
    removeService(serviceId) {
        const cart = this.get();
        cart.services = cart.services.filter(s => String(s.id) !== String(serviceId));
        this.save(cart);
    },

    getTotalCount() {
        const cart = this.get();
        let count = 0;
        if (cart.hall) count += 1;
        if (cart.catering) count += 1;
        if (cart.stage) count += 1;
        count += cart.rooms.reduce((acc, r) => acc + (r.quantity || 1), 0);
        count += cart.furniture.reduce((acc, f) => acc + (f.quantity || 1), 0);
        count += cart.services.length;
        return count;
    },

    getGrandTotal() {
        const cart = this.get();
        let total = 0;
        if (cart.hall) total += parseFloat(cart.hall.price || 0);
        if (cart.catering) total += parseFloat(cart.catering.total || cart.catering.price || 0);
        if (cart.stage) total += parseFloat(cart.stage.price || 0);
        cart.rooms.forEach(r => { total += parseFloat(r.total || (r.price * r.quantity) || 0); });
        cart.furniture.forEach(f => { total += parseFloat(f.total || (f.price * f.quantity) || 0); });
        cart.services.forEach(s => { total += parseFloat(s.price || 0); });
        return total;
    },

    updateHeaderBadge() {
        const count = this.getTotalCount();
        const badgeElems = document.querySelectorAll(".cart-badge-count, #headerCartCount");
        badgeElems.forEach(el => {
            el.textContent = count;
            el.style.display = "inline";
        });
    },

    renderSidebar() {
        const bodyElem = document.getElementById("cartSidebarBody");
        const grandTotalElem = document.getElementById("cartSidebarGrandTotal");
        const footerElem = document.getElementById("cartSidebarFooter");

        if (!bodyElem) return;

        const cart = this.get();
        const grandTotal = this.getGrandTotal();

        if (grandTotalElem) {
            grandTotalElem.textContent = "₹" + grandTotal.toLocaleString("en-IN");
        }

        const count = this.getTotalCount();

        if (count === 0) {
            bodyElem.innerHTML = `
                <div class="cart-empty-state">
                    <i class="fa-solid fa-cart-shopping"></i>
                    <p>Your cart is empty</p>
                    <small>Browse halls, rooms, and catering packages to build your event.</small>
                </div>
            `;
            if (footerElem) footerElem.style.display = "none";
            return;
        }

        if (footerElem) footerElem.style.display = "block";

        let html = "";

        // 1. Hall
        if (cart.hall) {
            html += `
                <div class="sidebar-item-card">
                    <button class="sidebar-item-remove" onclick="RoyalCart.removeHall()" title="Remove Hall"><i class="fa-solid fa-xmark"></i></button>
                    <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #60646c; margin-bottom: 2px;"><i class="fa-solid fa-building-columns"></i> Hall</div>
                    <div class="sidebar-item-title">${cart.hall.name}</div>
                    <div style="font-size: 13px; color: #60646c; margin-bottom: 6px;">Capacity: ${cart.hall.capacity || 'N/A'} Guests</div>
                    <div class="sidebar-item-price">₹${parseFloat(cart.hall.price).toLocaleString("en-IN")}</div>
                </div>
            `;
        }

        // 2. Rooms
        if (cart.rooms.length > 0) {
            cart.rooms.forEach(r => {
                const rTotal = parseFloat(r.total || (r.price * r.quantity));
                html += `
                    <div class="sidebar-item-card">
                        <button class="sidebar-item-remove" onclick="RoyalCart.removeRoom('${r.id}')" title="Remove Room"><i class="fa-solid fa-xmark"></i></button>
                        <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #60646c; margin-bottom: 2px;"><i class="fa-solid fa-bed"></i> Room</div>
                        <div class="sidebar-item-title">${r.name}</div>
                        <div class="sidebar-qty-row">
                            <div class="qty-controls">
                                <button class="qty-btn" onclick="RoyalCart.updateRoomQty('${r.id}', -1)">-</button>
                                <span class="qty-num">${r.quantity}</span>
                                <button class="qty-btn" onclick="RoyalCart.updateRoomQty('${r.id}', 1)">+</button>
                            </div>
                            <div class="sidebar-item-price">₹${rTotal.toLocaleString("en-IN")}</div>
                        </div>
                    </div>
                `;
            });
        }

        // 3. Catering
        if (cart.catering) {
            const cTotal = parseFloat(cart.catering.total || cart.catering.price);
            const ppp = parseFloat(cart.catering.pricePerPlate || cart.catering.price || 0);
            html += `
                <div class="sidebar-item-card">
                    <button class="sidebar-item-remove" onclick="RoyalCart.removeCatering()" title="Remove Catering"><i class="fa-solid fa-xmark"></i></button>
                    <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #60646c; margin-bottom: 2px;"><i class="fa-solid fa-utensils"></i> Catering</div>
                    <div class="sidebar-item-title">${cart.catering.name}</div>
                    <div style="font-size: 12px; color: #60646c; margin-bottom: 6px;">₹${ppp.toLocaleString("en-IN")} / Plate</div>
                    <div class="sidebar-qty-row">
                        <div class="qty-controls">
                            <button class="qty-btn" onclick="RoyalCart.updateCateringGuests(-10)" title="-10 plates" style="font-size: 10px; padding: 0 4px;">-10</button>
                            <button class="qty-btn" onclick="RoyalCart.updateCateringGuests(-1)">-</button>
                            <span class="qty-num" style="min-width: 60px;">${cart.catering.guestCount || 100} p</span>
                            <button class="qty-btn" onclick="RoyalCart.updateCateringGuests(1)">+</button>
                            <button class="qty-btn" onclick="RoyalCart.updateCateringGuests(10)" title="+10 plates" style="font-size: 10px; padding: 0 4px;">+10</button>
                        </div>
                        <div class="sidebar-item-price">₹${cTotal.toLocaleString("en-IN")}</div>
                    </div>
                </div>
            `;
        }

        // 4. Stage
        if (cart.stage) {
            html += `
                <div class="sidebar-item-card">
                    <button class="sidebar-item-remove" onclick="RoyalCart.removeStage()" title="Remove Stage"><i class="fa-solid fa-xmark"></i></button>
                    <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #60646c; margin-bottom: 2px;"><i class="fa-solid fa-masks-theater"></i> Stage Design</div>
                    <div class="sidebar-item-title">${cart.stage.name}</div>
                    <div class="sidebar-item-price">₹${parseFloat(cart.stage.price).toLocaleString("en-IN")}</div>
                </div>
            `;
        }

        // 5. Furniture
        if (cart.furniture.length > 0) {
            cart.furniture.forEach(f => {
                const fTotal = parseFloat(f.total || (f.price * f.quantity));
                html += `
                    <div class="sidebar-item-card">
                        <button class="sidebar-item-remove" onclick="RoyalCart.removeFurniture('${f.id}')" title="Remove Furniture"><i class="fa-solid fa-xmark"></i></button>
                        <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #60646c; margin-bottom: 2px;"><i class="fa-solid fa-chair"></i> Furniture</div>
                        <div class="sidebar-item-title">${f.name}</div>
                        <div class="sidebar-qty-row">
                            <div class="qty-controls">
                                <button class="qty-btn" onclick="RoyalCart.updateFurnitureQty('${f.id}', -1)">-</button>
                                <span class="qty-num">${f.quantity}</span>
                                <button class="qty-btn" onclick="RoyalCart.updateFurnitureQty('${f.id}', 1)">+</button>
                            </div>
                            <div class="sidebar-item-price">₹${fTotal.toLocaleString("en-IN")}</div>
                        </div>
                    </div>
                `;
            });
        }

        // 6. Services
        if (cart.services.length > 0) {
            cart.services.forEach(s => {
                html += `
                    <div class="sidebar-item-card">
                        <button class="sidebar-item-remove" onclick="RoyalCart.removeService('${s.id}')" title="Remove Service"><i class="fa-solid fa-xmark"></i></button>
                        <div style="font-size: 11px; font-weight: 600; text-transform: uppercase; color: #60646c; margin-bottom: 2px;"><i class="fa-solid fa-concierge-bell"></i> Service</div>
                        <div class="sidebar-item-title">${s.name}</div>
                        <div class="sidebar-item-price">₹${parseFloat(s.price).toLocaleString("en-IN")}</div>
                    </div>
                `;
            });
        }

        bodyElem.innerHTML = html;
    }
};

// Global Helpers for easy HTML button onclick binding
function addHallToCart(id, name, price, capacity) {
    RoyalCart.setHall({ id, name, price, capacity });
}

function addRoomToCart(id, name, price) {
    RoyalCart.addRoom({ id, name, price, quantity: 1 });
}

function addCateringToCart(id, name, price) {
    RoyalCart.setCatering({ id, name, price, total: parseFloat(price) });
}

// Global UI controls for sidebar
function openCartSidebar() {
    const sidebar = document.getElementById("cartSidebar");
    const backdrop = document.getElementById("cartBackdrop");
    RoyalCart.renderSidebar();
    if (sidebar) {
        sidebar.classList.add("active");
        sidebar.classList.add("open");
    }
    if (backdrop) {
        backdrop.classList.add("active");
        backdrop.classList.add("open");
    }
}

function closeCartSidebar() {
    const sidebar = document.getElementById("cartSidebar");
    const backdrop = document.getElementById("cartBackdrop");
    if (sidebar) {
        sidebar.classList.remove("active");
        sidebar.classList.remove("open");
    }
    if (backdrop) {
        backdrop.classList.remove("active");
        backdrop.classList.remove("open");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    RoyalCart.updateHeaderBadge();
});
