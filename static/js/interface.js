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

function paginator() {
  let elements = document.getElementsByClassName('review-card');
  let pages = [];
  for (let i = 0; i < elements.length / 3; i++) {
    pages[i] = []
  }
  console.log(pages);

  let pageNumber = 0;
  for (let i = 0; i < elements.length; i++) {
    if (i % 3 == 0) {
      pageNumber += 1;
      pages[pageNumber] = [];
      pages[pageNumber].push(elements[i]);
    } else {
      pages[pageNumber].push(elements[i])
    }
  }
  //   return pages;
}

paginator();