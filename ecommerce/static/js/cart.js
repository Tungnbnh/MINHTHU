// document.querySelector(".search-button").addEventListener("click", function() {
//     this.parentNode.classList.toggle("open");
// });
var updateBtns = document.getElementsByClassName("update-cart");

for (i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener("click", function() {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log("productId:", productId, "action:", action);

        console.log("USER:", user);
        if (user === "AnonymousUser") {
            console.log("Not logged in");
        } else {
            updateUserOrder(productId, action);
        }
    });
}

function updateUserOrder(productId, action) {
    console.log("User is logged in, sending data..");

    var url = "/update_item/";

    fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({ productId: productId, action: action }),
        })
        .then((response) => {
            return response.json();
        })

    .then((data) => {
        console.log("data:", data);
        location.reload();
    });
}
var updateBtns = document.getElementsByClassName("update-cart");

// Nut tim kiem

var form = document.getElementById("search-form");
var input = document.getElementById("search-input");

input.addEventListener("keypress", function(event) {
    if (event.keyCode === 13) {
        event.preventDefault(); // Ngăn không cho form submit mặc định
        // form.submit(); // Submit form để tìm kiếm
    }
});