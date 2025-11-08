console.log("Looking for the login panel...");

window.addEventListener("DOMContentLoaded", () => {
    // Find the target container
    const loginPanel = document.querySelector(
        'div.grid.gap-6'
    );

    if (!loginPanel) {
        console.warn("Login panel not found!");
    } else {
        console.log("Login panel found:", loginPanel);
    }

    // Create logo wrapper
    const logoRow = document.createElement("div");
    logoRow.style.display = "flex";
    logoRow.style.justifyContent = "center";
    logoRow.style.gap = "1rem";
    logoRow.style.marginTop = "2rem";

    // Add logos
    const logos = [
        { src: "imperial_logo.png", alt: "Imperial" },
        { src: "microsoft_logo.png", alt: "Microsoft" },
    ];

    logos.forEach(({ src, alt }) => {
        const img = document.createElement("img");
        img.src = src;
        img.alt = alt;
        img.style.height = "32px";
        img.style.objectFit = "contain";
        logoRow.appendChild(img);
    });

    // Append after the form
    loginPanel.appendChild(logoRow);
});