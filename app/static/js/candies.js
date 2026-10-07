console.log("candies.js loaded!");

fetch("/auth/users/me")
    .then(response => response.json())
    .then(data => {
        console.log("User data:", data);
    
    document.getElementById("balance").textContent = data.balance;
    })
    .catch(error => {
        console.error("Request failed:", error);
    });

fetch("/auth/candies")
    .then(response => response.json())
    .then(result => {
        console.log("Candies from backend:", result);

        const candyList = document.getElementById("candy-list");

        result.data.forEach(candy => {
            const card = document.createElement("div");

            card.classList.add("candy-card");

            card.innerHTML = `
                <h2>${candy.candy_name}</h2>
                <p>Price: ₹${candy.price}</p>
                <p>Stock: ${candy.stock}</p>
                <button>Buy</button>
            `;

            candyList.appendChild(card);
        });
    })
    .catch(error => {
        console.error("Failed to load candies:", error);
    });