let rawBooking = sessionStorage.getItem("bookingData");
let bookingData = null;
if (rawBooking) {
    try { bookingData = JSON.parse(rawBooking); } catch(e) {}
}
if (!bookingData && typeof RoyalCart !== "undefined") {
    bookingData = RoyalCart.get();
}
console.log("Booking Data", bookingData);

function hideAllCards() {
    document.getElementById("hallCard").style.display = "none";
    document.getElementById("roomCard").style.display = "none";
    document.getElementById("furnitureCard").style.display = "none";
    document.getElementById("stageCard").style.display = "none";
    document.getElementById("serviceCard").style.display = "none";
    document.getElementById("cateringCard").style.display = "none";
}

if (!bookingData || RoyalCart.getTotalCount() === 0) {
    alert("No booking data found in cart.");
    window.location.href = "/";
}
// hideAllCards();

function loadHall() {

    if (!bookingData.hall) {

        return;

    }

    document.getElementById("hallCard").style.display = "block";

    document.getElementById("hallSection").innerHTML = `
        <div class="summary-row">

            <div class="summary-left">

                <h4>${bookingData.hall.name}</h4>

                <small>Hall Booking</small>

            </div>

            <div class="summary-price">

                ₹${bookingData.hall.price.toLocaleString("en-IN")}

            </div>

        </div>
    `;
}
function loadFurniture() {

    document.getElementById("furnitureCard").style.display = "block";

    let html = "";

    bookingData.furniture.forEach(item => {

        html += `

            <div class="summary-row">

                <div class="summary-left">

                    <h4>${item.name}</h4>

                    <small>

                        ${item.quantity} × ₹${item.price}

                    </small>

                </div>

                <div class="summary-price">

                    ₹${item.total.toLocaleString("en-IN")}

                </div>

            </div>

        `;

    });

    document.getElementById("furnitureSection").innerHTML = html;

}
function loadStage() {

    document.getElementById("stageCard").style.display = "block";

    if (!bookingData.stage) return;

    document.getElementById("stageSection").innerHTML = `

        <div class="summary-row">

            <div class="summary-left">

                <h4>${bookingData.stage.name}</h4>

            </div>

            <div class="summary-price">

                ₹${bookingData.stage.price.toLocaleString("en-IN")}

            </div>

        </div>

    `;

}
function loadRooms() {

    document.getElementById("roomCard").style.display = "block";

    console.log("loadRooms Called");
    console.log(bookingData.rooms);

    if (!bookingData.rooms || bookingData.rooms.length === 0) {

        document.getElementById("roomSection").innerHTML = `
            <p>No rooms selected.</p>
        `;

        document.getElementById("summaryRoomPrice").innerText = "₹0";

        return;
    }

    let html = "";
    let total = 0;

    bookingData.rooms.forEach(room => {

        total += room.total;

        html += `

        <div class="summary-row">

            <div class="summary-left">

                <h4>${room.name}</h4>

                <small>
                    ${room.quantity} × ₹${room.price.toLocaleString("en-IN")}
                </small>

            </div>

            <div class="summary-price">

                ₹${room.total.toLocaleString("en-IN")}

            </div>

        </div>

        `;

    });

    document.getElementById("roomSection").innerHTML = html;

    document.getElementById("summaryRoomPrice").innerText =
        "₹" + total.toLocaleString("en-IN");
}

function loadCatering() {
    const card = document.getElementById("cateringCard");
    const section = document.getElementById("cateringSection");
    if (!card || !section) return;

    if (!bookingData.catering) {
        card.style.display = "none";
        return;
    }

    card.style.display = "block";
    const c = bookingData.catering;
    const guestCount = parseInt(c.guestCount) || 100;
    const ppp = parseFloat(c.pricePerPlate) || parseFloat(c.price) || 0;
    const total = parseFloat(c.total) || (guestCount * ppp);

    let itemsHtml = "";
    if (Array.isArray(c.selectedItems) && c.selectedItems.length > 0) {
        itemsHtml = `<div style="margin-top: 10px; display: flex; flex-wrap: wrap; gap: 6px;">` +
            c.selectedItems.map(it => {
                let name = typeof it === 'object' ? (it.item || it.name || '') : it;
                return `<span style="display: inline-block; background: #f0f0f3; color: #171717; padding: 3px 8px; border-radius: 6px; font-size: 12px; font-weight: 500;">✓ ${name}</span>`;
            }).join('') +
            `</div>`;
    }

    section.innerHTML = `
        <div class="summary-row" style="align-items: flex-start;">
            <div class="summary-left" style="flex: 1;">
                <h4>${c.name}</h4>
                <div style="font-size: 13px; color: #60646c; margin-top: 4px;">
                    ₹${ppp.toLocaleString("en-IN")} / Plate
                </div>
                ${itemsHtml}
                <div style="margin-top: 14px; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 12px; font-weight: 600; text-transform: uppercase; color: #60646c;">Adjust Plates:</span>
                    <div style="display: inline-flex; align-items: center; gap: 4px; border: 1px solid #dcdee0; border-radius: 6px; padding: 2px 6px; background: #fff;">
                        <button type="button" onclick="adjustOverviewCateringPlates(-10)" style="border:none; background:none; cursor:pointer; font-size: 11px; font-weight:600; padding: 0 4px;" title="-10 plates">-10</button>
                        <button type="button" onclick="adjustOverviewCateringPlates(-1)" style="border:none; background:none; cursor:pointer; font-weight:bold; padding: 0 4px;">-</button>
                        <span id="overviewPlatesDisplay" style="font-family: 'JetBrains Mono', monospace; font-weight:600; min-width: 65px; text-align:center;">${guestCount} plates</span>
                        <button type="button" onclick="adjustOverviewCateringPlates(1)" style="border:none; background:none; cursor:pointer; font-weight:bold; padding: 0 4px;">+</button>
                        <button type="button" onclick="adjustOverviewCateringPlates(10)" style="border:none; background:none; cursor:pointer; font-size: 11px; font-weight:600; padding: 0 4px;" title="+10 plates">+10</button>
                    </div>
                </div>
            </div>
            <div class="summary-price" id="overviewCateringPrice">
                ₹${total.toLocaleString("en-IN")}
            </div>
        </div>
    `;
}

function adjustOverviewCateringPlates(delta) {
    if (!bookingData.catering) return;
    let current = parseInt(bookingData.catering.guestCount) || 100;
    let next = Math.max(1, current + delta);
    bookingData.catering.guestCount = next;
    let ppp = parseFloat(bookingData.catering.pricePerPlate) || parseFloat(bookingData.catering.price) || 0;
    bookingData.catering.pricePerPlate = ppp;
    bookingData.catering.total = next * ppp;
    
    if (typeof RoyalCart !== "undefined") {
        RoyalCart.setCatering(bookingData.catering, false);
    }
    sessionStorage.setItem("bookingData", JSON.stringify(bookingData));
    
    loadCatering();
    updateSummary();
}

function loadServices() {
    const card = document.getElementById("serviceCard");
    if (!card) return 0;

    let allServices = [];
    if (Array.isArray(bookingData.services) && bookingData.services.length > 0) {
        allServices = bookingData.services;
    } else {
        allServices = [
            ...(bookingData.entertainment || []),
            ...(bookingData.photography || []),
            ...(bookingData.guestServices || [])
        ];
    }

    if (allServices.length === 0) {
        card.style.display = "none";
        return 0;
    }

    card.style.display = "block";
    let html = "";
    let serviceTotal = 0;

    let grouped = {};
    allServices.forEach(service => {
        let cat = service.category || "Additional Services";
        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(service);
        serviceTotal += parseFloat(service.price || 0);
    });

    for (let cat in grouped) {
        html += `<div class="summary-category"><h3>${cat}</h3></div>`;
        grouped[cat].forEach(service => {
            html += `
                <div class="summary-row">
                    <div class="summary-left">
                        <h4>${service.name}</h4>
                    </div>
                    <div class="summary-price">
                        ₹${parseFloat(service.price || 0).toLocaleString("en-IN")}
                    </div>
                </div>
            `;
        });
    }

    document.getElementById("servicesSection").innerHTML = html;
    return serviceTotal;
}

function updateSummary() {
    let hallPrice = bookingData.hall ? parseFloat(bookingData.hall.price || 0) : 0;

    let roomPrice = 0;
    (bookingData.rooms || []).forEach(r => {
        roomPrice += parseFloat(r.total || (r.price * r.quantity) || 0);
    });

    let cateringTotal = bookingData.catering ? parseFloat(bookingData.catering.total || bookingData.catering.price || 0) : 0;

    let furniturePrice = 0;
    (bookingData.furniture || []).forEach(f => {
        furniturePrice += parseFloat(f.total || (f.price * f.quantity) || 0);
    });

    let stagePrice = bookingData.stage ? parseFloat(bookingData.stage.price || 0) : 0;

    let servicePrice = 0;
    let allServices = Array.isArray(bookingData.services) && bookingData.services.length > 0
        ? bookingData.services
        : [
            ...(bookingData.entertainment || []),
            ...(bookingData.photography || []),
            ...(bookingData.guestServices || [])
          ];
    allServices.forEach(item => {
        servicePrice += parseFloat(item.price || 0);
    });

    const setPriceText = (elemId, val) => {
        const el = document.getElementById(elemId);
        if (el) el.innerText = "₹" + val.toLocaleString("en-IN");
    };

    setPriceText("summaryHallPrice", hallPrice);
    setPriceText("summaryRoomPrice", roomPrice);
    setPriceText("summaryCateringPrice", cateringTotal);
    setPriceText("summaryFurniturePrice", furniturePrice);
    setPriceText("summaryStagePrice", stagePrice);
    setPriceText("summaryServicePrice", servicePrice);

    let grandTotal = hallPrice + roomPrice + cateringTotal + furniturePrice + stagePrice + servicePrice;
    setPriceText("grandTotal", grandTotal);
}
function getCookie(name) {

    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {

        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {

            cookie = cookie.trim();

            if (cookie.startsWith(name + "=")) {

                cookieValue =
                    decodeURIComponent(
                        cookie.substring(name.length + 1)
                    );

                break;

            }

        }

    }

    return cookieValue;

}
function modifyBooking() {

    window.history.back();

}
function confirmBooking() {

    const customer = {

        name:
            document.getElementById("customerName").value,

        phone:
            document.getElementById("customerPhone").value,

        email:
            document.getElementById("customerEmail").value,

        event_date:
            document.getElementById("eventDate").value,

        event_type:
            document.getElementById("eventType").value,

        special_request:
            document.getElementById("specialRequest").value

    };

    if (
        customer.name === "" ||
        customer.phone === "" ||
        customer.event_date === "" ||
        customer.event_type === ""

    ) {

        alert("Please fill all required fields.");

        return;

    }

    bookingData.customer = customer;

    console.log(bookingData);

    bookingData.customer = customer;

    fetch("/booking/create/", {

        method: "POST",

        headers: {

            "Content-Type": "application/json",

            "X-CSRFToken": getCookie("csrftoken")

        },

        body: JSON.stringify(bookingData)

    })

        .then(response => response.json())

        .then(data => {

            console.log(data);

            if (data.status === "success") {

                window.location.href =
                    `/booking/${data.booking_id}/quotation/`;

            }
            else {

                alert(data.message);

            }

        })

        .catch(error => {

            console.log(error);

        });

}


hideAllCards();

if (bookingData.hall) {
    loadHall();
}

if (bookingData.rooms && bookingData.rooms.length > 0) {
    loadRooms();
}

if (bookingData.furniture && bookingData.furniture.length > 0) {
    loadFurniture();
}

if (bookingData.stage) {
    loadStage();
}

if (
    (bookingData.entertainment && bookingData.entertainment.length > 0) ||
    (bookingData.photography && bookingData.photography.length > 0) ||
    (bookingData.guestServices && bookingData.guestServices.length > 0)
) {
    loadServices();
}

if (bookingData.catering) {
    loadCatering();
}

updateSummary();