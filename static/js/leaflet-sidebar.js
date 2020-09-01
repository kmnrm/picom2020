// Source code from leaflet-sidebar plugin https://github.com/Turbo87/leaflet-sidebar/

L.Control.Sidebar = L.Control.extend({

  includes: L.Mixin.Events,

  options: {
    swipeButton: true,
    closeButton: true,
    position: 'left',
    autoPan: true,
  },

  initialize: function (placeholder, options) {
    L.setOptions(this, options);

    // Find content container
    var content = this._contentContainer = L.DomUtil.get(placeholder);

    // Remove the content container from its original parent
    content.parentNode.removeChild(content);

    var l = 'leaflet-';

    // Create sidebar container
    var container = this._container = L.DomUtil.create('div', l + 'sidebar ' + this.options.position);
    
    // Style and attach content container
    L.DomUtil.addClass(content, l + 'control');
    container.appendChild(content);

    // Create swipe button and attach it if configured
    if (this.options.swipeButton) {
      var swipe = this._swipeButton = L.DomUtil.create('a', 'swipe', container);
      swipe.innerHTML = '';
    }
    
    // Create close button and attach it if configured
    if (this.options.closeButton) {
      var close = this._closeButton = L.DomUtil.create('a', 'close', container);
      close.innerHTML = '&times';
    }
  },

  addTo: function (map) {
    var container = this._container;
    var content = this._contentContainer;

    // Attach event to swipe button
    if (this.options.swipeButton) {
      var swipe = this._swipeButton;
      L.DomEvent.on(swipe, 'click', this.toggle, this);
    }
    // Attach event to close button
    if (this.options.closeButton) {
      var close = this._closeButton;
      L.DomEvent.on(close, 'click', this.hide, this);
    }

    L.DomEvent
        .on(container, 'transitionend',
            this._handleTransitionEvent, this)
        .on(container, 'webkitTransitionEnd',
            this._handleTransitionEvent, this);

    // Attach sidebar container to controls container
    var controlContainer = map._controlContainer;
    controlContainer.insertBefore(container, controlContainer.firstChild);

    this._map = map;

    // Make sure we don't drag the map when we interact with the content
    var stop = L.DomEvent.stopPropagation;
    var fakeStop = L.DomEvent._fakeStop || stop;
    L.DomEvent
        .on(content, 'contextmenu', stop)
        .on(content, 'click', fakeStop)
        .on(content, 'mousedown', stop)
        .on(content, 'touchstart', stop)
        .on(content, 'dblclick', fakeStop)
        .on(content, 'mousewheel', stop)
        .on(content, 'MozMousePixelScroll', stop);

    return this;
  },

  removeFrom: function (map) {
    //if the control is visible, hide it before removing it.
    this.hide();

    var container = this._container;
    var content = this._contentContainer;

    // Remove sidebar container from controls container
    var controlContainer = map._controlContainer;
    controlContainer.removeChild(container);

    //disassociate the map object
    this._map = null;

    // Unregister events to prevent memory leak
    var stop = L.DomEvent.stopPropagation;
    var fakeStop = L.DomEvent._fakeStop || stop;
    L.DomEvent
        .off(content, 'contextmenu', stop)
        .off(content, 'click', fakeStop)
        .off(content, 'mousedown', stop)
        .off(content, 'touchstart', stop)
        .off(content, 'dblclick', fakeStop)
        .off(content, 'mousewheel', stop)
        .off(content, 'MozMousePixelScroll', stop);

    L.DomEvent
        .off(container, 'transitionend',
            this._handleTransitionEvent, this)
        .off(container, 'webkitTransitionEnd',
            this._handleTransitionEvent, this);

    if (this._swipeButton && this._swipe) {
      var swipe = this._swipeButton;
      L.DomEvent.off(swipe, 'click', this.toggle, this);
    }

    if (this._closeButton && this._close) {
      var close = this._closeButton;
      L.DomEvent.off(close, 'click', this.hide, this);
    }

    return this;
  },

  isVisible: function () {
    return L.DomUtil.hasClass(this._container, 'visible');
  },

  show: function () {
    if (!this.isVisible()) {
      L.DomUtil.addClass(this._container, 'visible');
    //   if (this.options.autoPan) {
    //     this._map.panBy([-this.getOffset() / 2, 0], {
    //     this._map.panBy([0, 0], {
    //         duration: 0.5
    //     });
    //   }
    //   this.fire('show');
    }
  },

  hide: function (e) {
    if (this.isVisible()) {
      L.DomUtil.removeClass(this._container, 'visible');
      // if (this.options.autoPan) {
      //   this._map.panBy([this.getOffset() / 2, 0], {
      //   this._map.panBy([0, 0], {
      //       duration: 0.5
      //   });
      // }
      // this.fire('hide');
    }
    if(e) {
      L.DomEvent.stopPropagation(e);
    }
  },

  toggle: function (e) {
    if (this.isVisible()) {
      this.hide();
    } else {
      this.show();
    }
    if (e) {
      L.DomEvent.stopPropagation(e);
    }
  },

  getContainer: function () {
    return this._contentContainer;
  },

  getSwipeButton: function () {
    return this._swipeButton;
  },

  getCloseButton: function () {
    return this._closeButton;
  },

  setContent: function (content) {
    var container = this.getContainer();

    if (typeof content === 'string') {
      container.innerHTML = content;
    } else {
      // clean current content
      while (container.firstChild) {
        container.removeChild(container.firstChild);
      }

      container.appendChild(content);
    }

    return this;
  },

  getOffset: function () {
    if (this.options.position === 'right') {
      return -this._container.offsetWidth;
    } else {
      return this._container.offsetWidth;
    }
  },

  _handleTransitionEvent: function (e) {
    if (e.propertyName == 'left' || e.propertyName == 'right'){
      this.fire(this.isVisible() ? 'shown' : 'hidden');
    }
  }
});

L.control.sidebar = function (placeholder, options) {
  return new L.Control.Sidebar(placeholder, options);
};
