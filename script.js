// PD made changes in the first part, and MP made the rest of the changes.

document.addEventListener("DOMContentLoaded", () => {


// Cases + folders
    let currentCase = "main";

        const caseFolders = {
            main: "",
            high: "",
            low: ""
        };


// Forecast hours

    const hours = [
        "000","006","012","018","024","030","036","042",
        "048","054","060","066","072","078","084","090","096"
    ];

    let currentIndex = 0;


// Elements

    const hourSelect = document.getElementById("hourSelect");
    const hourSlider = document.getElementById("hourSlider");
    const plotImage = document.getElementById("plotImage");
    const caseSelect = document.getElementById("caseSelect");


// Populate dropdown

    hours.forEach(hour => {
        const option = document.createElement("option");
        option.value = hour;
        option.textContent = `Hour ${hour}`;
        hourSelect.appendChild(option);
    });


// Main update function


function showHour(index) {
    currentIndex = (index + hours.length) % hours.length;
    const hour = hours[currentIndex];

    let fileName;

    if (currentCase === "main") {
        fileName = `winter_threat_${hour}.png`;
    } 
    else if (currentCase === "high") {
        fileName = `winter_threat_high_end.png`;
    } 
    else if (currentCase === "low") {
        fileName = `winter_threat_low_end.png`;
    }

    plotImage.src = fileName;

    hourSelect.value = hour;
    hourSlider.value = currentIndex;
}

 
// Case selector

caseSelect.addEventListener("change", () => {
    currentCase = caseSelect.value;

    const isMain = currentCase === "main";

    hourSelect.disabled = !isMain;
    hourSlider.disabled = !isMain;

    showHour(currentIndex);
});


// Dropdown hour control

    hourSelect.addEventListener("change", () => {
        const index = hours.indexOf(hourSelect.value);
        showHour(index);
    });


// Slider

    hourSlider.addEventListener("input", () => {
        showHour(parseInt(hourSlider.value));
    });


// Buttons

    document.getElementById("prevBtn").addEventListener("click", () => {
        showHour(currentIndex - 1);
    });

    document.getElementById("nextBtn").addEventListener("click", () => {
        showHour(currentIndex + 1);
    });


// Initial load

    showHour(0);

});