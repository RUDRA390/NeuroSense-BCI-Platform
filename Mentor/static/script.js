document.getElementById("predictBtn").addEventListener("click", async () => {

    const fileInput = document.getElementById("trialFile");
    const model = document.getElementById("model").value;
    const resultDiv = document.getElementById("result");

    if (fileInput.files.length === 0) {
        alert("Please select a .npy EEG file.");
        return;
    }

    const formData = new FormData();
    formData.append("trial_file", fileInput.files[0]);
    formData.append("model_name", model);

    resultDiv.innerHTML = "<p>Predicting...</p>";

    try {

        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML =
                `<h3 style="color:red;">${data.error}</h3>`;
            return;
        }

        let html = "";

        html += `<h2>Prediction</h2>`;

        html += `<h3>${data.predicted_class}</h3>`;

        html += `<p><b>Model:</b> ${data.model_used}</p>`;

        html += "<hr>";

        for (const cls in data.probabilities) {

            const p = data.probabilities[cls];

            html += `
                <p>${cls} : ${(p*100).toFixed(2)}%</p>

                <div class="bar"
                     style="width:${p*100}%">
                </div>
            `;
        }

        resultDiv.innerHTML = html;

    }

    catch(err){

        resultDiv.innerHTML =
        `<h3 style="color:red;">${err}</h3>`;

    }

});