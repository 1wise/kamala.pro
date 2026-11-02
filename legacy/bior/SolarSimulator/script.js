// Timestamp: 2026-10-30 | Version: 2.0.1 | Author and Credits: https://www.alawise.es/1-s
// Drive reference; not installed by the V2 overlay.
const G = 6.67430e-11;
const masses = {
    "Sun": 1.989e30,
    "Mercury": 3.3011e23,
    "Venus": 4.8675e24,
    "Earth": 5.97237e24,
    "Moon": 7.342e22,
    "Mars": 6.4171e23,
    "Jupiter": 1.8982e27
};

const canvas    = document.getElementById('canvas');
const ctx       = canvas.getContext('2d');
const manualDate = document.getElementById('manualDate');
const speedSlider = document.getElementById('speed');
const pauseBtn  = document.getElementById('pause');
const slowerBtn = document.getElementById('slower');
const fasterBtn = document.getElementById('faster');
const gravityInfo = document.getElementById('gravityInfo');

let isPaused = false;
let currentTime = new Date();
let speed = 1;

// Initialize the manual date input to current time (UTC, trimmed to minutes)
manualDate.value = currentTime.toISOString().slice(0, 16);

// When the manual date is changed, update the simulation time, redraw, and update the gravity info
manualDate.onchange = () => { 
    currentTime = new Date(manualDate.value);
    draw();
    updateChartAndGravityInfo();
};

// Toggle pause/resume on Pause button click
pauseBtn.onclick = () => {
    isPaused = !isPaused;
    pauseBtn.innerHTML = isPaused ? "Resume ►" : "Pause ❚❚";
};

// Slow down time speed (clamped to slider min)
slowerBtn.onclick = () => {
    if (speed > parseInt(speedSlider.min)) {
        speed -= 1;
        speedSlider.value = speed;
    }
};

// Speed up time (clamped to slider max)
fasterBtn.onclick = () => {
    if (speed < parseInt(speedSlider.max)) {
        speed += 1;
        speedSlider.value = speed;
    }
};

// Sync speed variable with slider on manual adjustment
speedSlider.oninput = () => {
    speed = parseInt(speedSlider.value);
};

// Get heliocentric position of a body (using Astronomy Engine library)
function getPosition(body, date) {
    return Astronomy.HelioVector(body, date);
}

// Draw the solar system bodies on the canvas at the current time
function draw() {
    ctx.clearRect(0, 0, 360, 500);

    const bodies = ["Mercury", "Venus", "Earth", "Mars", "Jupiter"];
    const positions = {};
    // Sun at center
    positions["Sun"] = { x: 0, y: 0, z: 0 };
    // Get positions for each planet relative to Sun
    bodies.forEach(body => {
        positions[body] = getPosition(body, currentTime);
    });
    // Scale down Jupiter's position for better visibility (because Jupiter is far)
    positions["Jupiter"].x /= 2;
    positions["Jupiter"].y /= 2;
    positions["Jupiter"].z /= 2;

    // Compute Moon's position relative to Earth (geocentric vector scaled and added to Earth's position)
    const earthPos = positions["Earth"];
    const moonGeo = Astronomy.GeoVector("Moon", currentTime, true);
    positions["Moon"] = {
        x: earthPos.x + (moonGeo.x / 1.496e8) * 80,
        y: earthPos.y + (moonGeo.y / 1.496e8) * 80,
        z: earthPos.z + (moonGeo.z / 1.496e8) * 80
    };

    // Draw each body on the canvas
    ctx.save();
    ctx.translate(200, 300);  // translate to roughly center the view
    Object.entries(positions).forEach(([name, pos]) => {
        // Color coding for bodies
        ctx.fillStyle = ({
            "Sun": "yellow",
            "Earth": "cyan",
            "Moon": "gray",
            "Venus": "red",
            "Mercury": "blue",
            "Mars": "pink",
            "Jupiter": "brown"
        })[name] || "white";
        // Set size (Sun larger, Moon smaller)
        const size = (name === "Sun" ? 8 : (name === "Moon" ? 3 : 5));
        ctx.beginPath();
        ctx.arc(pos.x * 70, pos.y * 70, size, 0, 2 * Math.PI);
        ctx.fill();
        // Label the point with the body's name
        ctx.font = "12px Arial";
        ctx.fillText(name, pos.x * 70 + 6, pos.y * 70);
    });
    ctx.restore();
}

// Advance time and redraw at a fixed interval, if not paused
setInterval(() => {
    if (!isPaused) {
        // Advance current time by speed*60 seconds (speed steps in minutes per tick)
        currentTime.setSeconds(currentTime.getSeconds() + speed * 60);
        // Update the manual date input to reflect the new time
        manualDate.value = currentTime.toISOString().slice(0, 16);
        // Redraw the simulation
        draw();
        // (Optional) You could also update the gravity info here periodically if desired
        // document.getElementById('gravityValue').textContent = calculateGravityDelta(currentTime).toFixed(6);
    }
}, 100);

// Initial draw of the simulation canvas
draw();

