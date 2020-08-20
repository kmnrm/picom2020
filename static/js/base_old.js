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

/* ======--Routing Machine--======*/
var control = L.Routing.control({
  position: 'topleft',
  routeWhileDragging: false,
  draggableWaypoints: false,
  reverseWaypoints: false,
  geocoder: L.Control.Geocoder.nominatim({
    reverseQueryParams: {
      zoom: 0
    }
  }),
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
control.htmlAddress = document.getElementsByClassName("leaflet-routing-geocoders")[0];

control.hide();

var clearWaypoints = function(){
  if(control){
    control.setWaypoints(null);
    control.hide();
  }};

map.on('click', clearWaypoints);

var itineraryShown = false,
    controlContainer = control.getContainer(),
    showGeocoderBtn = document.createElement("button");

showGeocoderBtn.classList.add('123');
showGeocoderBtn.textContent = 'VLAD HELP ME!!!';
controlContainer.appendChild(showGeocoderBtn);

showGeocoderBtn.onclick = function() {
 if (itineraryShown) {
   clearWaypoints();
   control.hide();
   itineraryShown = !itineraryShown;
 } else {
   control.show();
   itineraryShown = !itineraryShown;
}};



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

        var container = L.DomUtil.create('div'),
          placeTitle = L.DomUtil.create('p', '', container),
          startBtn = createButton('Start', container, 'leaflet-route-start'),
          fromMyLoc = createButton('Get here now', container, 'leaflet-route-get-here'),
          destBtn = createButton('Go', container, 'leaflet-route-go');
          
          placeTitle.textContent = geoJsonPoint.properties.title;

        L.popup()
          .setContent(container)
          .setLatLng(event.latlng)
          .openOn(map);

        L.DomEvent.on(startBtn, 'click', function() {
            control.show();
            control.spliceWaypoints(0, 1, event.latlng);
            map.closePopup();
        });

        L.DomEvent.on(destBtn, 'click', function() {
            control.show();
            control.spliceWaypoints(control.getWaypoints().length - 1, 1, event.latlng);
            map.closePopup();
        });

        L.DomEvent.on(fromMyLoc, 'click', function(){
          control.show();
          lc.stop();
          lc.start();
          map.on('locationfound', function(e){
            control.spliceWaypoints(0, 1, e.latlng);
            control.spliceWaypoints(control.getWaypoints().length - 1, 1, event.latlng);

          });
        });

      });
      return marker;
    }
});
/* ================================*/


/* ======--Search--======*/
var searchControl = new L.Control.Search({
  layer: locations,
  propertyName: 'title',
  position: 'topleft',
  marker: false
});
searchControl.addTo(map);
searchControl.htmlAddress = document.getElementsByClassName("leaflet-control-search")[0];

searchControl.on('search:locationfound', function (e) {
  sidebar.show();
  loadPlaceInfo(
    e.layer.feature.properties.placeId,
    e.layer.feature.properties.detailsUrl
  );
  e.layer.openPopup();
})
/* ================================*/

/* ======--Location--======*/
var lc = L.control.locate({
  position: 'topleft',
  clickBehavior: { inView: 'setView' },
  setView: false,
  cacheLocation: false,
  strings: {
    title: "Show me where I am, yo!",
    popup: "Time to go somewhere, bro..."
  }
});
lc.addTo(map);
lc.htmlAddress = document.getElementsByClassName("leaflet-control-locate")[0];
/* ================================*/

var controlsHtml = [control.htmlAddress, searchControl.htmlAddress, lc.htmlAddress];
controlsHtml.forEach(item => { item.classList.add('disabled') });

/* ======--Button--======*/
var navigateButton = new L.Control.Button("", {
  position: "topleft",
  className: "navigate-button",
});
navigateButton.addTo(map);
navigateButton.htmlAddress = document.getElementsByClassName('navigate-button')[0];

navigateButton.on('click', function() {
  controlsHtml.forEach(item => {
    item.classList.toggle('disabled');
    navigateButton.htmlAddress.classList.toggle('disabled');
    }
  );
  // return controlsHtml;
});
/* ================================*/

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

map.on('click', function () {
  sidebarApp.selectedPlace = null;
  sidebarApp.loadingPlaceId = null;
  // if (navigateButton.htmlAddress.classList.contains('disabled')) {
  //   [navigateButton, ...controlsHtml].forEach(item => {
  //     console.log(item);
  //     item.classList.toggle('disabled')
  //     }
  //   );
  // }
})

var nullToZeros = function (arr) {
  for (const obj of arr) {
    if (obj.rating === null) {
      obj.rating = 0;
    }
  }
  return arr
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
      similar_places: nullToZeros(data.similar_places.sort(function(){
        return .5 - Math.random()
      }).slice(0, 4)),

    };
  } finally {
    if (sidebarApp.loadingPlaceId == placeId){
      sidebarApp.loadingPlaceId = null;
    }
  }
}
