const mapsElement = document.getElementById("maps-list");
const mapsResponse = await fetch('./js/maps.json');
const maps = await mapsResponse.json();
for (const map of maps) {
    let mapElement = document.createElement("a");
    mapElement.classList.add("list-group-item");
    mapElement.classList.add("list-group-item-action");
    mapElement.innerHTML = map;
    mapElement.href = map;
    mapsElement.appendChild(mapElement);
}
