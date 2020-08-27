function formShow() {
  let formSection = document.getElementById('form-section');
  formSection.classList.remove('disabled');
}

function formHide() {
  let formSection = document.getElementById('form-section');
  formSection.classList.add('disabled');
}

function formChange() {
  let signInForm = document.getElementById('autorization-form');
  let signUpForm = document.getElementById('registration-form');
  signInForm.classList.toggle('disabled');
  signUpForm.classList.toggle('disabled');
}

function descriptionRating() {
  let rating = Math.round(document.getElementById('description-rating-value').innerHTML);
  let stars = document.getElementsByClassName('description-rating-stars');
  for (let i = 0; i < rating; i++) {
    stars[i].classList.add('active');
  }
}

function descriptionPoliceRate() {
  let policeRate = parseInt(document.getElementById('description-police-rate-value').innerHTML);
  let warnings = document.getElementsByClassName('description-rating-warnings');
  for (let i = 0; i < policeRate; i++) {
    warnings[i].classList.add('active');
  }
}


function choosePage() {}
function paginator() {
  let createPageButton = function (num) {
    let buttons = document.getElementById('reviews-pages');
    let button = document.createElement('a');
    if (isFinite(num)) {
      let text = document.createTextNode(num + 1);
      button.appendChild(text);
      button.href = '#';
      button.setAttribute('onclick', 'choosePage(num + 1)');
      buttons.appendChild(button);
    }
  }

  let elements = document.getElementsByClassName('review-card');
  let pages = [];
  for (let i = 0; i < elements.length / 3; i++) {
    pages[i] = [];
    createPageButton(i);
  }
  console.log(pages);

  let pageNumber = 0;
  for (let i = 0; i < elements.length; i++) {
    if (i % 3 == 0 && i != 0) {
      pageNumber += 1;
      pages[pageNumber] = [];
      pages[pageNumber].push(elements[i]);
    } else {
      pages[pageNumber].push(elements[i])
    }
  }

  for (let page of pages) {
    for (let element of page) {
      element.style.display = 'none';
    }
  }
  createPageButton();
}

function addScroll(event) {
  event.target.onwheel = function (event) {
    if (event.deltaMode == event.DOM_DELTA_PIXEL) {
      var modifier = 0.5;
      // иные режимы возможны в Firefox
    } else if (event.deltaMode == event.DOM_DELTA_LINE) {
      var modifier = parseInt(getComputedStyle(this).lineHeight) / 2;
    } else if (event.deltaMode == event.DOM_DELTA_PAGE) {
      var modifier = this.clientHeight / 2;
    }
    if (event.deltaY != 0) {
      // замена вертикальной прокрутки горизонтальной
      this.scrollLeft += modifier * event.deltaY;
      event.preventDefault();
    }
  }
};