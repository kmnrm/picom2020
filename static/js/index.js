var scripts = document.getElementsByTagName('script'),
    path = scripts[scripts.length-1].src.split('?')[0],
    thisDir = path.split('/').slice(0, -1).join('/')+'/';

var map = L.map('map', {zoomControl: false, minZoom: 2});
map.setView([34.76, 113.71], 12);

/*L.tileLayer.provider('OpenStreetMap.Mapnik').addTo(map);*/
var night = L.tileLayer.provider('Jawg.Dark', {
        variant: 'c603bda4-6780-4f3a-b06f-b5de44f2ed88',
        accessToken: 'Ej2LIAfNJgZZ1TprVGdK16SXWDk9sWDrFbI8YMNYfIPYJMLwsN43j0dqVXovhUQE'
        })
    daytime = L.tileLayer.provider('Jawg.Light', {
        variant: '356d4034-9a74-4ce1-b906-515215d2d48d',
        accessToken: 'Ej2LIAfNJgZZ1TprVGdK16SXWDk9sWDrFbI8YMNYfIPYJMLwsN43j0dqVXovhUQE'
        })

map.addLayer(night)
var overlays = {
    "Light Theme": daytime
};

function sidebarToggle() {
  var sidebar = document.getElementsByClassName('leaflet-sidebar')[0];
  sidebar.classList.toggle('visible');
}

var locLatLng;
map.on('locationfound', function(e) { locLatLng = e.latlng } );

function showGeocodersPopUp(event) {
  let element = event.target.nextElementSibling;
  element.style.display = 'block';
  setTimeout(() => element.style.display = "none", 3000);
}

function setMyLocation(event) {
  let element = event.target.parentElement.parentElement.children[1];
  if (!lc._active) {
    lc.start();
  }
  setTimeout(() => {
    if (element.placeholder === 'Start') {
      if (control.getWaypoints()[1].name === 'My location') {
      control.setWaypoints(null)
      };
      control.spliceWaypoints(0, 1, locLatLng);
    } else {
      if (control.getWaypoints()[0].name === 'My location') {
        control.setWaypoints(null)
      };
      control.spliceWaypoints(control.getWaypoints().length - 1, 1, locLatLng);
    }
  }, 100);
}

L.control.layers(null, overlays).addTo(map);
L.control.zoom({
    position: 'bottomright'
}).addTo(map);


var sidebar = L.control.sidebar('sidebar', {
  closeButton: true,
  position: 'left'
});
map.addControl(sidebar);

if (document.documentElement.clientWidth > 450) sidebar.show();

function createButton(label, container, elemClass) {
  var btn = L.DomUtil.create('button', '', container);
  btn.setAttribute('class', elemClass);
  btn.innerHTML = label;
  return btn;
}

function loadJSON(elementId){
  let element = document.getElementById(elementId);

  if (!element){
    return null;
  }

  return JSON.parse(element.textContent);
}

function getTopPlaces(placesGeoJson, n) {
  var topSlice = placesGeoJson.features.slice(0, n);
  for (i = 0; i < topSlice.length; i++) {
    topSlice[i].properties.ratingRounded = Math.round(topSlice[i].properties.rating);
    topSlice[i].properties.coordinates = topSlice[i].geometry.coordinates
  }
  var topPlaces = topSlice.map(
    function(feature) {
      return feature.properties
    }
  )
  return topPlaces
}

let places = loadJSON('places-geojson');

let topPlaces = getTopPlaces(places, 3);


/* ======--Routing Machine--======*/
var control = L.Routing.control({
  router: L.Routing.mapbox(config.MAPBOX_KEY),
  position: 'topleft',
  autoRoute: false,
  routeWhileDragging: false,
  draggableWaypoints: false,
  reverseWaypoints: true,
  geocoder: L.Control.Geocoder.zzgo(),
  lineOptions : {
    addWaypoints: false,
    styles: [{ color: '#0053b5', opacity: 1, weight: 5 }]
  },

  createMarker: function (i, start, n){
    var marker = L.marker (start.latLng, {
      icon: L.divIcon({
        html: '<div><div class="map-label-arrow"></div><p class="map-label-content">' + start.name + '</p></div>'
      })
    });
    return marker
  },
  waypointNameFallback: function(latLng) {
    var featureIndex,
      waypointLngLat = [latLng.lng, latLng.lat],
      locs = places.features;
    for (featureIndex = 0; featureIndex <locs.length; featureIndex++) {
      if (waypointLngLat.every(
        function(value, index){
          return value === locs[featureIndex].geometry.coordinates[index]
        })
      ){
        return locs[featureIndex].properties.title;
      }
    }
    return 'My location'
  }
});
control.addTo(map);
control.hide();

/* ======--Set A Route Button--======*/
var setRouteBtn = control.getPlan()._geocoderContainer.querySelector('.btnSetRoute');
var closeRoutingControlBtn = control.getPlan()._geocoderContainer.querySelector('.btnClose');

setRouteBtn.addEventListener('click', function() {
  control.getWaypoints().every(function(wp, wpIndex) {
    if(wp.latLng) {
      control.route();
      control.hide();
      // lc.getContainer().style.display = 'none';
      setGeocoderBtn();
    }
  })
});
/* ========================*/

var locations = L.geoJSON(places, {
    pointToLayer: function(geoJsonPoint, latlng) {
      if (geoJsonPoint.geometry.type != "Point"){
        return
      }

      let color = geoJsonPoint.properties.color || 'red';

      let marker = L.circleMarker(latlng, {
        color: '#fff',
        fillColor: '#0859F5',
        fillOpacity: 1,
        radius: 6,
        clickable: true,
        riseOnHover: true
      });

      marker.bindTooltip(geoJsonPoint.properties.title);
      marker.bindPopup(function (layer) {
        return geoJsonPoint.properties.title;
      })

      marker.on('click', function(event){
        sidebar.show();
        loadPlaceInfo(geoJsonPoint.properties.placeId, geoJsonPoint.properties.detailsUrl);
        addPopUpRoutingBtns(event.latlng, geoJsonPoint.properties.title);
      });
      return marker;
    }
});
map.addLayer(locations);
/* ================================*/



function addPopUpRoutingBtns(locationLatLng, locationTitle) {
  var plan = control._plan,
    container = L.DomUtil.create('div'),
    placeTitle = L.DomUtil.create('p', '', container),
    destBtn = createButton('Set a route', container, 'leaflet-route-go');
    placeTitle.textContent = locationTitle;

    L.popup()
      .setContent(container)
      .setLatLng(locationLatLng)
      .openOn(map);

    L.DomEvent.on(destBtn, 'click', function() {
      control.show();
      showGeocoderBtn.style.display = "none";
      control.spliceWaypoints(control.getWaypoints().length - 1, 1, locationLatLng);
      map.closePopup();
      plan._markers[1]._icon.children[0].children[1].textContent = plan._waypoints[1].name;
    })
}



/* ======--Search--======*/
var searchControl = new L.Control.Search({
  container: 'search',
  layer: locations,
  propertyName: 'title',
  position: 'topleft',
  marker: false,
  collapsed: false,
  textPlaceholder: 'Where to go?',
  firstTipSubmit: true,
});

searchControl.on('search:locationfound', function (e) {
  sidebar.show();
  // addPopUpRoutingBtns(e.latlng, e.layer.feature.properties.title);
  e.layer.openPopup();
  loadPlaceInfo(
    e.layer.feature.properties.placeId,
    e.layer.feature.properties.detailsUrl
  );
})
/* ================================*/

/* ======--Location--======*/
var lc = L.control.locate({
  position: 'bottomright',
  clickBehavior: { inView: 'setView' },
  setView: 'once',
  initialZoomLevel: 17,
  strings: {
    title: "Show me where I am, yo!",
    popup: "Time to go somewhere, bro..."
  }
});


function clearWaypoints(){
  if(control){
    // control.setWaypoints(null);
    control.hide();
  }};


var controlContainer = control.getContainer(),
  showGeocoderBtn = document.createElement("button");

function setGeocoderBtn() {

  showGeocoderBtn.classList.add('leaflet-geocoders-toggler');
  controlContainer.appendChild(showGeocoderBtn);
  showGeocoderBtnHTML = document.getElementsByClassName('leaflet-geocoders-toggler')[0];
  showGeocoderBtn.style.display = "block";
  showGeocoderBtnHTML.innerHTML = `
    <svg width="75" height="59" viewBox="0 0 75 59" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M13 30H26.7128C30.6101 30 33.7696 33.1594 33.7696 37.0568V37.0568C33.7696 40.9542 30.6101 44.1136 26.7128 44.1136H19.4432C15.8847 44.1136 13 46.9983 13 50.5568V50.5568C13 54.1153 15.8847 57 19.4432 57H56" stroke="#0859F5" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
<path d="M56.8191 10C47.0524 10 39.125 17.8774 39.125 27.5823C39.125 34.5144 42.0423 41.5095 47.5598 47.8324C51.6821 52.5588 55.7621 55.2267 55.9312 55.3527C56.1849 55.5207 56.502 55.6048 56.7979 55.6048C57.0939 55.6048 57.411 55.5207 57.6646 55.3527C57.8338 55.2477 61.9138 52.5588 66.036 47.8324C71.5535 41.5095 74.4708 34.4934 74.4708 27.5823C74.492 17.8774 66.5645 10 56.8191 10Z" fill="#0859F5"/>
<path d="M56.8192 20.5871C52.9506 20.5871 49.8008 23.7171 49.8008 27.5612C49.8008 31.4054 52.9506 34.5353 56.8192 34.5353C60.6878 34.5353 63.8376 31.4054 63.8376 27.5612C63.8376 23.7171 60.6878 20.5871 56.8192 20.5871ZM56.8192 31.4054C54.7052 31.4054 52.9718 29.6829 52.9718 27.5822C52.9718 25.4816 54.7052 23.7591 56.8192 23.7591C58.9332 23.7591 60.6667 25.4816 60.6667 27.5822C60.6667 29.6829 58.9332 31.4054 56.8192 31.4054Z" fill="white"/>
<path d="M11.6859 0C5.7741 0 0.975586 4.76821 0.975586 10.6426C0.975586 14.8387 2.74144 19.0728 6.08121 22.9001C8.57644 25.7611 11.0461 27.3759 11.1484 27.4522C11.302 27.5539 11.4939 27.6048 11.6731 27.6048C11.8522 27.6048 12.0442 27.5539 12.1977 27.4522C12.3001 27.3886 14.7697 25.7611 17.2649 22.9001C20.6047 19.0728 22.3706 14.826 22.3706 10.6426C22.3834 4.76821 17.5849 0 11.6859 0Z" fill="#0859F5"/>
<path d="M11.6858 6.40829C9.34411 6.40829 7.4375 8.30286 7.4375 10.6298C7.4375 12.9566 9.34411 14.8512 11.6858 14.8512C14.0275 14.8512 15.9341 12.9566 15.9341 10.6298C15.9341 8.30286 14.0275 6.40829 11.6858 6.40829Z" fill="white"/>
</svg>
  `;
};

setGeocoderBtn();

showGeocoderBtn.onclick = function () {
  control.show();
  lc.addTo(map);
  lc.stop();
  controlContainer.removeChild(showGeocoderBtn);
};

function closeRoutingControl() {
  if (lc._map){
    lc.stop();
    map.removeControl(lc);
  }

  clearWaypoints();
  setGeocoderBtn();
}

closeRoutingControlBtn.onclick = function () {
  closeRoutingControl()
}


function checkIfPlaceOpen(placeOpeningHours, placeClosingHours) {
  var now = new Date(),
      nowDate = now.toISOString().split('T')[0],
      openTime = new Date(nowDate + 'T' + placeOpeningHours + '.000+08:00');
      closeTime = new Date(nowDate + 'T' + placeClosingHours + '.000+08:00');

  if (placeOpeningHours > placeClosingHours) {
    if (now >= closeTime && now < openTime) { return false }
    closeTime.setDate(closeTime.getDate() + 1);
  }
  return now >= openTime && now < closeTime || openTime === closeTime
}

var sidebarApp = new Vue({
  el: '#sidebar-app',
  data: {
    loadingPlaceId: null,
    selectedPlace: null,
  },
  computed: {
    promptVisible: function () {
      // document.getElementsByClassName('search-title')[0].style.display = 'block';
      return !this.loading && !this.selectedPlace;
    },
    loading: function () {
      return this.loadingPlaceId !== null;
    },

    carouselImages: function () {
      if (!this.selectedPlace || !this.selectedPlace.images.length){
        return [];
      }
      return this.selectedPlace.images;
    },

    placeIsOpen: function () {
      if (!this.selectedPlace){
        return false
      }
      return checkIfPlaceOpen(
        this.selectedPlace.openingHours,
        this.selectedPlace.closingHours
      )
    }
  },
  updated: function () {
    this.$nextTick(function () {
      // Код, будет запущен только после обновления всех представлений
      $('#place-photos').carousel();
    })
  },
  methods: {
    handlePhotosClick: function(slideId='next') {
      // default event handlers of Bootstrap Carousel conflict with Leaflet
      // so custom handler will mimic expected carousel behaviour
      $('#place-photos').carousel(slideId);
    }
  },
});

map.addControl(searchControl);
var backButton = document.getElementById('back-button');

function getBackToMain() {
  sidebarApp.selectedPlace = null;
  sidebarApp.loadingPlaceId = null;
  backButton.style.display = 'none';
  map.closePopup();
}

backButton.onclick = function () {
  getBackToMain();
}

map.on('click', function () {
  getBackToMain();
  document.querySelector('.search-title').style.display = 'block';
})

if (!Array.prototype.last){
    Array.prototype.last = function(){
        return this[this.length - 1];
    };
};

function getSimilarPlaces(parentPlaceId, placeCategory, placesGeoJson, setSize) {
  var similarPlaces = [],
    places = placesGeoJson.features;
  for (i = 0; i < places.length; i++){
    if (places[i].properties.category === placeCategory && places[i].properties.placeId !== parentPlaceId) {
      similarPlaces.push(places[i].properties);
      similarPlaces.last().coordinates = places[i].geometry.coordinates
    }
  }
  return (similarPlaces.sort(() => 0.5 - Math.random())).slice(0, setSize)
}

function getBusinessHours(openHours, closeHours) {
  if (openHours !== null && closeHours !== null) {
    if (openHours === closeHours) {
      return '24/7'
    }
    return openHours.slice(0, -3) + ' - ' + closeHours.slice(0, -3)
  }
  return '-'
}

async function loadPlaceInfo(placeId, detailsUrl){
  sidebarApp.selectedPlace = null;
  sidebarApp.loadingPlaceId = placeId;
  backButton.style.display = 'block';
  document.querySelector('.search-title').style.display = 'none';

  try {
    let response = await fetch(detailsUrl);
    if (!response.ok){
      return;
    }

    let data = await response.json();

    if (sidebarApp.loadingPlaceId != placeId){
      // Place loading was cancelled by user
      return
    }

    sidebarApp.selectedPlace = {
      title: data.title,
      placeId: placeId,
      images: data.images || [],
      category: data.category,
      description: data.description,
      address: data.address,
      averagePrice: data.average_price,
      rating: data.rating || 0,
      ratingRounded: Math.round(data.rating),
      ratingStatus: data.rating_status,
      policeRating: data.police_rating.slice(3, ),
      policeRatingValue: parseInt(data.police_rating.charAt(0)),
      events: data.events,
      reviews: data.reviews,
      businessHours: getBusinessHours(data.opening_hours, data.closing_hours),
      openingHours: data.opening_hours,
      closingHours: data.closing_hours,
      logo: data.logo,
      phoneNumber: data.phone_number,
      similarPlaces: getSimilarPlaces(data.id, data.category, places, 4),
    };
  } finally {
    if (sidebarApp.loadingPlaceId == placeId){
      sidebarApp.loadingPlaceId = null;
    }
  }
}

function loadClickedPlace(place){
  var placeLatLng = L.latLng(
    place.coordinates.latitude || place.coordinates[1],
    place.coordinates.longitude || place.coordinates[0]
  )
  L.popup()
    .setLatLng(placeLatLng)
    .setContent(place.title)
    .openOn(map);
  addPopUpRoutingBtns(placeLatLng, place.title);
  loadPlaceInfo(place.id, place.detailsUrl);
};
