document.getElementById('searchForm').addEventListener('submit', async function(e) {
    e.preventDefault(); 

    const train_no = document.getElementById('train_no').value;
    const date = document.getElementById('date').value;
    const station = document.getElementById('source_station').value;
    const dest_station = document.getElementById('dest_station').value;
    const class_pref = document.getElementById('class_pref').value;

    const btn = document.getElementById('submitBtn');
    const resultsArea = document.getElementById('resultsArea');
    const loading = document.getElementById('loading');
    const aiBox = document.getElementById('aiBox');
    const aiContent = document.getElementById('aiContent');
    const tableBody = document.querySelector('#resultsTable tbody');
    const viewMoreContainer = document.getElementById('viewMoreContainer');

    btn.disabled = true;
    btn.innerText = "Processing...";
    resultsArea.classList.remove('hidden');
    loading.classList.remove('hidden');
    aiBox.classList.add('hidden');
    tableBody.innerHTML = ""; 
    viewMoreContainer.innerHTML = ""; 

    try {
        const response = await fetch('/api/find_seats', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ train_no, date, station, dest_station, class_pref })
        });

        const result = await response.json();
        loading.classList.add('hidden');
        
        if (result.status === "success") {
            // 1. AI Output
            if (result.ai_advice) {
                aiBox.classList.remove('hidden');
                aiContent.innerHTML = result.ai_advice;
            }

            // 2. Raw Table Output with Toggle Logic
            if (result.raw_data && result.raw_data.length > 0) {
                
                let isExpanded = false;
                const initialLimit = 10;

                // Function to render table based on state
                const updateTable = () => {
                    tableBody.innerHTML = ""; // Clear current rows
                    
                    // Decide what data to show
                    const dataToShow = isExpanded ? result.raw_data : result.raw_data.slice(0, initialLimit);
                    
                    // Render Rows
                    dataToShow.forEach(seat => {
                        const row = `
                            <tr>
                                <td><strong>${seat.Coach}</strong></td>
                                <td>${seat.Seat}</td>
                                <td>${seat.From}</td>
                                <td>${seat.To}</td>
                                <td>${seat.Type}</td>
                            </tr>
                        `;
                        tableBody.innerHTML += row;
                    });

                    // Render Button
                    viewMoreContainer.innerHTML = ""; // Clear old button
                    if (result.raw_data.length > initialLimit) {
                        const toggleBtn = document.createElement('button');
                        toggleBtn.className = "view-more-btn";
                        toggleBtn.id = "toggleRowsBtn";
                        
                        if (isExpanded) {
                            toggleBtn.innerText = "Show Less 👆";
                        } else {
                            toggleBtn.innerText = `View ${result.raw_data.length - initialLimit} More Rows 👇`;
                        }

                        toggleBtn.onclick = function() {
                            isExpanded = !isExpanded; // Flip state
                            updateTable(); // Re-render
                            
                            // Optional: Scroll to table top when collapsing
                            if (!isExpanded) {
                                document.getElementById('resultsTable').scrollIntoView({behavior: 'smooth'});
                            }
                        };
                        
                        viewMoreContainer.appendChild(toggleBtn);
                    }
                };

                // Initial Render
                updateTable();

            } else {
                tableBody.innerHTML = "<tr><td colspan='5' style='text-align:center'>No vacant data found.</td></tr>";
            }
        } else {
            alert("Error: " + result.message);
        }

    } catch (error) {
        console.error("Error:", error);
        alert("Connection Error.");
    } finally {
        btn.disabled = false;
        btn.innerText = "Finding Vacant Seats";
    }
});