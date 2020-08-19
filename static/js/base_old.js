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

var lc = L.control.locate({
    position: 'topleft',
    clickBehavior: {inView: 'setView'},
    setView: false,
    cacheLocation: false,
    strings: {
        title: "Show me where I am, yo!",
        popup: "Time to go somewhere, bro..."
    }
}).addTo(map);


var sidebar = L.control.sidebar('sidebar', {
  closeButton: true,
  position: 'left'
});
map.addControl(sidebar);


sidebar.show();

function createButton(label, container) {
  var btn = L.DomUtil.create('button', '', container);
  btn.setAttribute('type', 'button');
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

var control = L.Routing.control({
  position: 'topleft',
  routeWhileDragging: false,
  draggableWaypoints: false,
  reverseWaypoints: true,
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
})

map.on('click', function(){
  if(control){
    control.setWaypoints(null);
    map.removeControl(control);
  }
})


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
          startBtn = createButton('Start', container),
          fromMyLoc = createButton('Get here now', container),
          destBtn = createButton('Go', container);

        L.popup()
          .setContent(container)
          .setLatLng(event.latlng)
          .openOn(map);

        L.DomEvent.on(startBtn, 'click', function() {
            map.addControl(control);
            control.spliceWaypoints(0, 1, event.latlng);
            map.closePopup();
        });

        L.DomEvent.on(destBtn, 'click', function() {
            map.addControl(control);
            control.spliceWaypoints(control.getWaypoints().length - 1, 1, event.latlng);
            map.closePopup();
        });

        L.DomEvent.on(fromMyLoc, 'click', function(){
          map.addControl(control);
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
}).addTo(map);


var searchControl = new L.Control.Search({
  layer: locations,
  propertyName: 'title',
  position: 'topleft',
  marker: false
});

searchControl.on('search:locationfound', function(e) {
  sidebar.show();
  loadPlaceInfo(
    e.layer.feature.properties.placeId,
    e.layer.feature.properties.detailsUrl
  );
  e.layer.openPopup();
})

map.addControl(searchControl);


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
})

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
      similar_places: data.similar_places.sort(function(){
        return .5 - Math.random()
      }).slice(0, 4),

    };
  } finally {
    if (sidebarApp.loadingPlaceId == placeId){
      sidebarApp.loadingPlaceId = null;
    }
  }
}
