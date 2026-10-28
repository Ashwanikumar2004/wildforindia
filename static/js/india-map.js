import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

const canvasHost = document.querySelector("#india-map-canvas");
const dataElement = document.querySelector("#wildlife-map-locations");

if (canvasHost && dataElement) {
    startWildlifeMap().catch((error) => {
        console.error("Could not start the India wildlife map:", error);
        showMapError("The 3D map could not load. Check your internet connection and refresh the page.");
    });
}

async function startWildlifeMap() {
    const locations = JSON.parse(dataElement.textContent);
    const response = await fetch(canvasHost.dataset.boundaryUrl);
    if (!response.ok) throw new Error(`India boundary request failed with ${response.status}`);
    const boundary = await response.json();
    const stateFeatures = (boundary.features || []).filter((feature) => feature.geometry);
    const getStateName = (feature) => feature.properties.name || feature.properties.NAME_1 || "Region";
    if (!stateFeatures.length) throw new Error("The India state boundary file is empty.");

    const featurePolygons = stateFeatures.map((feature) => ({
        feature,
        polygons: feature.geometry.type === "Polygon" ? [feature.geometry.coordinates] : feature.geometry.coordinates,
    }));
    const coordinatePairs = featurePolygons.flatMap(({ polygons }) => polygons.flatMap((polygon) => polygon.flat()));
    const longitudes = coordinatePairs.map(([longitude]) => longitude);
    const latitudes = coordinatePairs.map(([, latitude]) => latitude);
    const minLongitude = Math.min(...longitudes);
    const maxLongitude = Math.max(...longitudes);
    const minLatitude = Math.min(...latitudes);
    const maxLatitude = Math.max(...latitudes);
    const centerLatitude = (minLatitude + maxLatitude) / 2;
    const centerLongitude = (minLongitude + maxLongitude) / 2;
    const longitudeScale = Math.cos(THREE.MathUtils.degToRad(centerLatitude));
    const projectionScale = 11 / Math.max((maxLongitude - minLongitude) * longitudeScale, maxLatitude - minLatitude);

    function project(longitude, latitude) {
        return new THREE.Vector2(
            (longitude - centerLongitude) * longitudeScale * projectionScale,
            (latitude - centerLatitude) * projectionScale,
        );
    }

    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#e8f1e8");
    const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100);
    const initialCameraPosition = new THREE.Vector3(0, -7.5, 15.5);
    camera.position.copy(initialCameraPosition);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(canvasHost.clientWidth, canvasHost.clientHeight, false);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    renderer.domElement.setAttribute("aria-label", "Interactive 3D map of India's states and wildlife regions");
    renderer.domElement.setAttribute("role", "img");
    canvasHost.prepend(renderer.domElement);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 0, 0.35);
    controls.enableDamping = true;
    controls.dampingFactor = 0.07;
    controls.minDistance = 10;
    controls.maxDistance = 26;
    controls.minPolarAngle = 0.2;
    controls.maxPolarAngle = 1.42;
    controls.update();

    scene.add(new THREE.HemisphereLight(0xe8f4ff, 0x31563f, 2.1));
    const keyLight = new THREE.DirectionalLight(0xfff2d6, 3.5);
    keyLight.position.set(-5, 7, 12);
    scene.add(keyLight);
    const fillLight = new THREE.DirectionalLight(0x9cc5a5, 1.8);
    fillLight.position.set(7, -5, 8);
    scene.add(fillLight);

    const mapGroup = new THREE.Group();
    scene.add(mapGroup);
    const borderMaterial = new THREE.LineBasicMaterial({ color: 0xf5f8e9, transparent: true, opacity: 0.96 });
    const stateMeshes = [];

    function makeShape(polygon) {
        const outer = polygon[0];
        if (!outer || outer.length < 4) return null;
        const shape = new THREE.Shape();
        outer.forEach(([longitude, latitude], index) => {
            const point = project(longitude, latitude);
            if (index === 0) shape.moveTo(point.x, point.y);
            else shape.lineTo(point.x, point.y);
        });
        shape.closePath();
        for (const hole of polygon.slice(1)) {
            if (!hole.length) continue;
            const holePath = new THREE.Path();
            hole.forEach(([longitude, latitude], index) => {
                const point = project(longitude, latitude);
                if (index === 0) holePath.moveTo(point.x, point.y);
                else holePath.lineTo(point.x, point.y);
            });
            holePath.closePath();
            shape.holes.push(holePath);
        }
        return shape;
    }

    featurePolygons.forEach(({ feature, polygons }, featureIndex) => {
        const stateName = getStateName(feature);
        const topMaterial = new THREE.MeshStandardMaterial({
            color: new THREE.Color().setHSL(0.34 + (featureIndex % 6) * 0.018, 0.35, 0.48 + (featureIndex % 3) * 0.035),
            roughness: 0.76,
            metalness: 0.02,
            flatShading: true,
        });
        const sideMaterial = new THREE.MeshStandardMaterial({ color: 0x315d43, roughness: 0.88, flatShading: true });

        polygons.forEach((polygon) => {
            const shape = makeShape(polygon);
            if (!shape) return;
            const geometry = new THREE.ExtrudeGeometry(shape, {
                depth: 0.3,
                bevelEnabled: true,
                bevelSegments: 1,
                steps: 1,
                bevelSize: 0.025,
                bevelThickness: 0.045,
                curveSegments: 2,
            });
            geometry.computeVertexNormals();
            const mesh = new THREE.Mesh(geometry, [topMaterial, sideMaterial]);
            mesh.position.z = -0.24;
            mesh.userData.stateName = stateName;
            mesh.castShadow = true;
            mesh.receiveShadow = true;
            mapGroup.add(mesh);
            stateMeshes.push(mesh);

            polygon.forEach((ring) => {
                const points = ring.map(([longitude, latitude]) => {
                    const point = project(longitude, latitude);
                    return new THREE.Vector3(point.x, point.y, 0.08);
                });
                mapGroup.add(new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(points), borderMaterial));
            });
        });
    });

    const markerMaterial = new THREE.MeshStandardMaterial({ color: 0xf0b84e, emissive: 0x965614, emissiveIntensity: 0.5, roughness: 0.4 });
    const selectedMarkerMaterial = new THREE.MeshStandardMaterial({ color: 0xffe08b, emissive: 0xe99b27, emissiveIntensity: 1, roughness: 0.3 });
    const markerGeometry = new THREE.SphereGeometry(0.16, 20, 16);
    const haloGeometry = new THREE.TorusGeometry(0.25, 0.025, 8, 28);
    const haloMaterial = new THREE.MeshBasicMaterial({ color: 0xffd37b, transparent: true, opacity: 0.78 });
    const markerObjects = locations.map((location) => {
        const point = project(location.longitude, location.latitude);
        const marker = new THREE.Mesh(markerGeometry, markerMaterial);
        marker.position.set(point.x, point.y, 0.46);
        marker.userData.locationId = location.id;
        marker.castShadow = true;
        const halo = new THREE.Mesh(haloGeometry, haloMaterial.clone());
        halo.position.copy(marker.position);
        mapGroup.add(halo, marker);
        return { location, marker, halo };
    });

    const locationsById = new Map(locations.map((location) => [location.id, location]));
    const locationButtons = [...document.querySelectorAll("[data-location-id]")];
    const filterButtons = [...document.querySelectorAll("[data-map-filter]")];
    const stateFilter = document.querySelector("#map-state-filter");
    let activeSpecies = "all";
    let activeState = "all";
    let selectedId = null;

    if (stateFilter) {
        [...new Set(stateFeatures.map(getStateName).filter(Boolean))]
            .sort((a, b) => a.localeCompare(b))
            .forEach((state) => stateFilter.add(new Option(state, state)));
    }

    function locationMatches(location) {
        const speciesMatches = activeSpecies === "all" || location.species.some((species) => species.id === activeSpecies);
        const stateMatches = activeState === "all" || location.state.toLowerCase() === activeState.toLowerCase();
        return speciesMatches && stateMatches;
    }

    function selectLocation(locationId) {
        const location = locationsById.get(locationId);
        if (!location) return;
        selectedId = locationId;
        document.querySelector("#map-selected-title").textContent = location.name;
        document.querySelector("#map-selected-state").textContent = `${location.state}${location.demo ? " · illustrative example" : ""}`;
        document.querySelector("#map-selected-summary").textContent = location.summary || "Wildlife information for this park will appear here.";
        const speciesContainer = document.querySelector("#map-selected-species");
        speciesContainer.replaceChildren();
        if (location.species.length) {
            for (const species of location.species) {
                const card = document.createElement("article");
                card.className = "map-species-card";
                const name = document.createElement(species.url ? "a" : "h3");
                name.className = "map-species-name";
                name.textContent = species.name;
                if (species.url) name.href = species.url;
                const scientificName = document.createElement("p");
                scientificName.className = "map-species-scientific";
                scientificName.textContent = species.scientificName;
                const details = document.createElement("p");
                details.className = "map-species-details";
                details.textContent = `${species.category} · ${species.status}`;
                const summary = document.createElement("p");
                summary.className = "map-species-summary";
                summary.textContent = species.summary;
                card.append(name, scientificName, details, summary);
                speciesContainer.append(card);
            }
        } else {
            const noSpecies = document.createElement("span");
            noSpecies.className = "map-species-summary";
            noSpecies.textContent = "No verified species are linked yet";
            speciesContainer.append(noSpecies);
        }
        const detailsLink = document.querySelector("#map-selected-link");
        detailsLink.hidden = !location.url;
        if (location.url) detailsLink.href = location.url;
        locationButtons.forEach((button) => {
            const selected = button.dataset.locationId === locationId;
            button.classList.toggle("is-selected", selected);
            button.setAttribute("aria-pressed", String(selected));
        });
        markerObjects.forEach(({ location: markerLocation, marker }) => {
            marker.material = markerLocation.id === locationId ? selectedMarkerMaterial : markerMaterial;
        });
    }

    function applyFilters() {
        let visibleCount = 0;
        markerObjects.forEach(({ location, marker, halo }) => {
            const matches = locationMatches(location);
            marker.visible = matches;
            halo.visible = matches;
            if (matches) visibleCount += 1;
        });
        locationButtons.forEach((button) => {
            const location = locationsById.get(button.dataset.locationId);
            button.hidden = !location || !locationMatches(location);
        });
        document.querySelector("#map-location-count").textContent = `${visibleCount} wildlife ${visibleCount === 1 ? "region" : "regions"}`;
        if (selectedId && !locationMatches(locationsById.get(selectedId))) {
            const firstVisible = locations.find(locationMatches);
            if (firstVisible) {
                selectLocation(firstVisible.id);
            } else {
                selectedId = null;
                document.querySelector("#map-selected-title").textContent = "No matching regions";
                document.querySelector("#map-selected-state").textContent = activeState === "all" ? "No regions match this species filter." : `${activeState} · no regions match the current filters`;
                document.querySelector("#map-selected-summary").textContent = "Try another state or choose All wildlife to see the available protected areas.";
                document.querySelector("#map-selected-species").replaceChildren();
                document.querySelector("#map-selected-link").hidden = true;
                locationButtons.forEach((button) => {
                    button.classList.remove("is-selected");
                    button.setAttribute("aria-pressed", "false");
                });
                markerObjects.forEach(({ marker }) => { marker.material = markerMaterial; });
            }
        }
    }

    locationButtons.forEach((button) => button.addEventListener("click", () => selectLocation(button.dataset.locationId)));
    filterButtons.forEach((button) => button.addEventListener("click", () => {
        activeSpecies = button.dataset.mapFilter;
        filterButtons.forEach((item) => {
            const active = item.dataset.mapFilter === activeSpecies;
            item.classList.toggle("is-active", active);
            item.setAttribute("aria-pressed", String(active));
        });
        applyFilters();
    }));
    stateFilter?.addEventListener("change", () => {
        activeState = stateFilter.value;
        applyFilters();
    });

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    let pointerStart = null;
    renderer.domElement.addEventListener("pointerdown", (event) => { pointerStart = { x: event.clientX, y: event.clientY }; });
    renderer.domElement.addEventListener("pointerup", (event) => {
        if (!pointerStart) return;
        const moved = Math.hypot(event.clientX - pointerStart.x, event.clientY - pointerStart.y);
        pointerStart = null;
        if (moved > 6) return;
        const rect = renderer.domElement.getBoundingClientRect();
        pointer.set(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1);
        raycaster.setFromCamera(pointer, camera);
        const markerHit = raycaster.intersectObjects(markerObjects.map(({ marker }) => marker), false)[0];
        if (markerHit?.object.userData.locationId) {
            selectLocation(markerHit.object.userData.locationId);
            return;
        }
        const stateHit = raycaster.intersectObjects(stateMeshes, false)[0];
        if (stateHit?.object.userData.stateName && stateFilter) {
            stateFilter.value = stateHit.object.userData.stateName;
            activeState = stateFilter.value;
            applyFilters();
        }
    });

    document.querySelector("#map-reset").addEventListener("click", () => {
        camera.position.copy(initialCameraPosition);
        controls.target.set(0, 0, 0.35);
        controls.update();
    });
    document.querySelector("#map-zoom-in").addEventListener("click", () => { camera.position.multiplyScalar(0.86); controls.update(); });
    document.querySelector("#map-zoom-out").addEventListener("click", () => { camera.position.multiplyScalar(1.14); controls.update(); });

    document.querySelector("#map-loading")?.remove();
    const resize = () => {
        const width = canvasHost.clientWidth;
        const height = canvasHost.clientHeight;
        if (!width || !height) return;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height, false);
    };
    new ResizeObserver(resize).observe(canvasHost);
    resize();

    function animate() {
        requestAnimationFrame(animate);
        const time = performance.now() * 0.001;
        markerObjects.forEach(({ marker, halo }) => {
            if (marker.visible) halo.scale.setScalar(1 + Math.sin(time * 2.4 + marker.position.x) * 0.1);
        });
        controls.update();
        renderer.render(scene, camera);
    }
    animate();
    if (locations.length) selectLocation((locations.find((location) => location.species.length) || locations[0]).id);
    applyFilters();
}

function showMapError(message) {
    const loading = document.querySelector("#map-loading");
    const error = document.querySelector("#map-render-error");
    if (loading) loading.hidden = true;
    if (error) {
        error.textContent = message;
        error.hidden = false;
    }
}
