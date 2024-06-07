// Get the modal
var modal = document.getElementById("addToCartModal");

// Get the button that opens the modal
var buttons = document.getElementsByClassName("add-to-cart-button");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];


// When the user clicks on the button, open the modal
for (var i = 0; i < buttons.length; i++) {
    buttons[i].onclick = function() {
        modal.style.display = "block";
        var medicineId = this.getAttribute("data-medicine-id");
        document.getElementById("add-to-cart-confirm").setAttribute("data-medicine-id", medicineId);
    }

}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

// Increment and decrement quantity
document.getElementById('increment').addEventListener('click', function() {
    var quantityInput = document.getElementById('quantity');
    quantityInput.value = parseInt(quantityInput.value) + 1;
});

document.getElementById('decrement').addEventListener('click', function() {
    var quantityInput = document.getElementById('quantity');
    if (parseInt(quantityInput.value) > 1) {
        quantityInput.value = parseInt(quantityInput.value) - 1;
    }
});

// Add to cart
document.getElementById('add-to-cart-confirm').addEventListener('click', function() {
    var quantity = document.getElementById('quantity').value;
    var medicineId = this.getAttribute("data-medicine-id");
    var url = "/medicines/" + medicineId + "/add_to_cart/?quantity=" + quantity;
    window.location.href = url;
});

