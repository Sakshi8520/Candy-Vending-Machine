console.log("signup.json loaded!")

const form = document.getElementById("signup-form");

form.addEventListener("submit", function(event) {
    event.preventDefault();
    
    console.log("signup form submitted!")

const username = document.getElementById("username").value;
const password = document.getElementById("password").value;

    fetch("/auth/users/sign_up", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        username: username,
        password: password
    })
})
    .then(response => response.json())
    .then(data => {console.log("Backend response:", data)})
    .catch(error => {console.error("Request failed:", error)})
});