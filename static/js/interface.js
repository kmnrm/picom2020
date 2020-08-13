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
