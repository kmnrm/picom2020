var map = L.map('map', {zoomControl: false});
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


L.control.layers(null, overlays).addTo(map);
L.control.zoom({
    position: 'bottomright'
}).addTo(map);


var sidebar = L.control.sidebar('sidebar', {
  closeButton: true,
  position: 'left'
});
map.addControl(sidebar);


sidebar.show();

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

let places = loadJSON('places-geojson');

/*
var ZZGo = L.Class.extend({
  geocode: function(query, cb, context) {
    var params = {
        title: query
      };

    getJSON(
      window.location.href + 'api/places.json',
      L.extend(params, this.options.geocodingQueryParams),
      function(data) {
        var results = [],
          loc,
          latLng,
          latLngBounds;}


    )
  }
});
*/



/* ======--Routing Machine--======*/
var control = L.Routing.control({
  position: 'topleft',
  autoRoute: false,
  routeWhileDragging: false,
  draggableWaypoints: false,
  reverseWaypoints: false,
  // geocoder: ZZGo,
  geocoder: L.Control.Geocoder.nominatim(),
  lineOptions : {
    addWaypoints: false,
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
      control.route()
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
        color: 'rgb(92, 92, 255)',
        fillColor: '#000',
        fillOpacity: 0.5,
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



var addPopUpRoutingBtns = function(locationLatLng, locationTitle) {
  var container = L.DomUtil.create('div'),
    placeTitle = L.DomUtil.create('p', '', container),
    startBtn = createButton('Start', container, 'leaflet-route-start'),
    fromMyLoc = createButton('Get here now', container, 'leaflet-route-get-here'),
    destBtn = createButton('Go', container, 'leaflet-route-go');
    placeTitle.textContent = locationTitle;

    L.popup()
      .setContent(container)
      .setLatLng(locationLatLng)
      .openOn(map);

    L.DomEvent.on(startBtn, 'click', function() {
      control.show();
      showGeocoderBtn.style.display = "none";
      control.spliceWaypoints(0, 1, locationLatLng);
      map.closePopup();
    });

    L.DomEvent.on(destBtn, 'click', function() {
      control.show();
      showGeocoderBtn.style.display = "none";
      control.spliceWaypoints(control.getWaypoints().length - 1, 1, locationLatLng);
      map.closePopup();
    });

    L.DomEvent.on(fromMyLoc, 'click', function(){
      control.show();
      map.addControl(lc);
      showGeocoderBtn.style.display = "none";
      lc.stop();
      lc.start();
      map.on('locationfound', function(e){
        control.spliceWaypoints(0, 1, e.latlng);
        control.spliceWaypoints(control.getWaypoints().length - 1, 1, locationLatLng);
      });
    });
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
  addPopUpRoutingBtns(e.latlng, e.layer.feature.properties.title);
  loadPlaceInfo(
    e.layer.feature.properties.placeId,
    e.layer.feature.properties.detailsUrl
  );
})
/* ================================*/

/* ======--Location--======*/
var lc = L.control.locate({
  position: 'topleft',
  clickBehavior: { inView: 'setView' },
  setView: 'always',
  strings: {
    title: "Show me where I am, yo!",
    popup: "Time to go somewhere, bro..."
  }
});


var clearWaypoints = function(){
  if(control){
    control.setWaypoints(null);
    control.hide();
  }};


var controlContainer = control.getContainer(),
  showGeocoderBtn = document.createElement("button");

var setGeocoderBtn = function() {

  showGeocoderBtn.classList.add('leaflet-geocoders-toggler');
  controlContainer.appendChild(showGeocoderBtn);
  showGeocoderBtnHTML = document.getElementsByClassName('leaflet-geocoders-toggler')[0];
  showGeocoderBtn.style.display = "block";
  showGeocoderBtnHTML.innerHTML = `
    <svg width="83" height="39" viewBox="0 0 83 39" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M2 26.9487V21.5046C2 14.5985 7.59851 9 14.5046 9V9C21.4107 9 27.0093 14.5985 27.0093 21.5046V23.9815C27.0093 31.1714 32.8378 37 40.0278 37V37C47.2177 37 53.0463 31.1714 53.0463 23.9815V23C53.0463 15.268 59.3143 9 67.0463 9H76" stroke="black" stroke-width="4"/>
    <path d="M68 2L79 10L68 18" stroke="black" stroke-width="4"/>
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

var closeRoutingControl = function () {
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

var sidebarApp = new Vue({
  el: '#sidebar-app',
  data: {
    loadingPlaceId: null,
    selectedPlace: null,
  },
  computed: {
    promptVisible: function () {
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

map.on('click', function () {
  sidebarApp.selectedPlace = null;
  sidebarApp.loadingPlaceId = null;

  if (!searchControl._map) {
    map.addControl(searchControl);
  }
})

if (!Array.prototype.last){
    Array.prototype.last = function(){
        return this[this.length - 1];
    };
};

var getSimilarPlaces = function (parentPlaceId, placeCategory, placesGeoJson, setSize) {
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


async function loadPlaceInfo(placeId, detailsUrl){
  sidebarApp.selectedPlace = null;
  sidebarApp.loadingPlaceId = placeId;


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
      pinyin_address: data.pinyin_address,
      average_price: data.average_price,
      rating: data.rating || 0,
      rating_rounded: Math.round(data.rating),
      police_rating: data.police_rating,
      police_rating_value: parseInt(data.police_rating.charAt(0)),
      events: data.events,
      reviews: data.reviews,
      opening_hours: data.opening_hours,
      closing_hours: data.closing_hours,
      logo: data.logo,
      phone_number: data.phone_number,
      similar_places: getSimilarPlaces(data.id, data.category, places, 4),
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

  addPopUpRoutingBtns(placeLatLng, place.title);
  loadPlaceInfo(place.id, place.detailsUrl);
};
