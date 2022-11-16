
(function() {
  "use strict";

  /**
   * Easy selector helper function
   */
  const select = (el, all = false) => {
    el = el.trim()
    if (all) {
      return [...document.querySelectorAll(el)]
    } else {
      return document.querySelector(el)
    }
  }

  /**
   * Easy event listener function
   */
  const on = (type, el, listener, all = false) => {
    if (all) {
      select(el, all).forEach(e => e.addEventListener(type, listener))
    } else {
      select(el, all).addEventListener(type, listener)
    }
  }

  /**
   * Easy on scroll event listener 
   */
  const onscroll = (el, listener) => {
    el.addEventListener('scroll', listener)
  }

  /**
   * Sidebar toggle
   */
  if (select('.toggle-sidebar-btn')) {
    on('click', '.toggle-sidebar-btn', function(e) {
      select('body').classList.toggle('toggle-sidebar')
    })
  }

  /**
   * Search bar toggle
   */
  if (select('.search-bar-toggle')) {
    on('click', '.search-bar-toggle', function(e) {
      select('.search-bar').classList.toggle('search-bar-show')
    })
  }

  /**
   * Navbar links active state on scroll
   */
  let navbarlinks = select('#navbar .scrollto', true)
  const navbarlinksActive = () => {
    let position = window.scrollY + 200
    navbarlinks.forEach(navbarlink => {
      if (!navbarlink.hash) return
      let section = select(navbarlink.hash)
      if (!section) return
      if (position >= section.offsetTop && position <= (section.offsetTop + section.offsetHeight)) {
        navbarlink.classList.add('active')
      } else {
        navbarlink.classList.remove('active')
      }
    })
  }
  window.addEventListener('load', navbarlinksActive)
  onscroll(document, navbarlinksActive)

  /**
   * Toggle .header-scrolled class to #header when page is scrolled
   */
  let selectHeader = select('#header')
  if (selectHeader) {
    const headerScrolled = () => {
      if (window.scrollY > 100) {
        selectHeader.classList.add('header-scrolled')
      } else {
        selectHeader.classList.remove('header-scrolled')
      }
    }
    window.addEventListener('load', headerScrolled)
    onscroll(document, headerScrolled)
  }

  /**
   * Back to top button
   */
  let backtotop = select('.back-to-top')
  if (backtotop) {
    const toggleBacktotop = () => {
      if (window.scrollY > 100) {
        backtotop.classList.add('active')
      } else {
        backtotop.classList.remove('active')
      }
    }
    window.addEventListener('load', toggleBacktotop)
    onscroll(document, toggleBacktotop)
  }

  /**
   * Initiate tooltips
   */
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
  var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
  })

  /**
   * Initiate quill editors
   */
  if (select('.quill-editor-default')) {
    new Quill('.quill-editor-default', {
      theme: 'snow'
    });
  }

  if (select('.quill-editor-bubble')) {
    new Quill('.quill-editor-bubble', {
      theme: 'bubble'
    });
  }

  if (select('.quill-editor-full')) {
    new Quill(".quill-editor-full", {
      modules: {
        toolbar: [
          [{
            font: []
          }, {
            size: []
          }],
          ["bold", "italic", "underline", "strike"],
          [{
              color: []
            },
            {
              background: []
            }
          ],
          [{
              script: "super"
            },
            {
              script: "sub"
            }
          ],
          [{
              list: "ordered"
            },
            {
              list: "bullet"
            },
            {
              indent: "-1"
            },
            {
              indent: "+1"
            }
          ],
          ["direction", {
            align: []
          }],
          ["link", "image", "video"],
          ["clean"]
        ]
      },
      theme: "snow"
    });
  }


  /**
   * Initiate Bootstrap validation check
   */
  var needsValidation = document.querySelectorAll('.needs-validation')

  Array.prototype.slice.call(needsValidation)
    .forEach(function(form) {
      form.addEventListener('submit', function(event) {
        if (!form.checkValidity()) {
          event.preventDefault()
          event.stopPropagation()
        }

        form.classList.add('was-validated')
      }, false)
    })

})();


//SignUp Validation

// const form = document.getElementById('form');
// const email = document.getElementById('email');
// const password = document.getElementById('password');

// form.addEventListener('submit', e => {
// 	e.preventDefault();
	
// 	checkInputs();
// });

// function checkInputs() {
// 	// trim to remove the whitespaces
// 	const emailValue = email.value.trim();
// 	const passwordValue = password.value.trim();
	
	
	
// 	if(emailValue === '') {
// 		setErrorFor(email, 'Email cannot be blank');
// 	} else if (!isEmail(emailValue)) {
// 		setErrorFor(email, 'Not a valid email');
// 	} else {
// 		setSuccessFor(email);
// 	}
	
// 	if(passwordValue === '') {
// 		setErrorFor(password, 'Password cannot be blank');
// 	} else {
// 		setSuccessFor(password);
// 	}
	
	
// }

// function setErrorFor(input, message) {
// 	const formControl = input.parentElement;
// 	const small = formControl.querySelector('small');
// 	formControl.className = 'form-control error';
// 	small.innerText = message;
// }

// function setSuccessFor(input) {
// 	const formControl = input.parentElement;
// 	formControl.className = 'form-control success';
// }
	
// function isEmail(email) {
// 	return /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/.test(email);
// }



var nameError=document.getElementById('name-error');
var emailError=document.getElementById('email-error');
var passError=document.getElementById('pass-error');
var passError1=document.getElementById('pass1-error');
var passError2=document.getElementById('pass2-error');
var phoneError=document.getElementById('phone-error');
var expenseNameError=document.getElementById('expensename-error');
var expenseAmountError=document.getElementById('amount-error');

function validateName(){
  var name=document.getElementById('name').value;

  if(name.length==0){
    nameError.innerHTML='Name is required';
    return false;
  }
  else{
    nameError.innerHTML="Proper Name is Required"
  }
  nameError.innerHTML='<i class="fa-solid fa-circle-check"></i><span>&nbsp;&nbsp;&nbsp;Name is Valid</span>';
  return true;
}

function validateEmail(){
  var email=document.getElementById('email').value;
  if(email.length==0){
    emailError.innerHTML="Email is Required";
    return false;
  }
  if(!email.match(/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/)){
    emailError.innerHTML="Email Invalid";
    return false;
  }

  emailError.innerHTML='<i class="fa-solid fa-circle-check"></i><span>&nbsp;&nbsp;&nbsp;Email is Valid</span>';
  return true;
}


function validatePass(){
  var pass=document.getElementById('pass').value;
  if(pass.length==0){
    passError.innerHTML="Password is Required";
    return false;
  }
  if(pass.length<8){
    passError.innerHTML="Password must contain atleast 8 characters";
    return false;
  }
  if(pass.length>20){
    passError.innerHTML="Password must be below 20 characters";
    return false;
  }

  passError.innerHTML='<i class="fa-solid fa-circle-check"></i><span>&nbsp;&nbsp;&nbsp;Password is Valid</span>';
  return true;
}



function validatePass1(){
  var pass1=document.getElementById('pass1').value;
  if(pass1.length==0){
    passError1.innerHTML="Password is Required";
    return false;
  }
  if(pass1.length<8){
    passError1.innerHTML="Password must contain atleast 8 characters";
    return false;
  }
  if(pass1.length>20){
    passError1.innerHTML="Password must be below 20 characters";
    return false;
  }

  passError1.innerHTML='<i class="fa-solid fa-circle-check"></i><span>&nbsp;&nbsp;&nbsp;Password is Valid</span>';
  return true;
}


function validatePass2(){
  var pass2=document.getElementById('pass2').value;
  if(pass2.length==0){
    passError2.innerHTML="Password is Required";
    return false;
  }
  if(pass2.length<8){
    passError2.innerHTML="Password must contain atleast 8 characters";
    return false;
  }
  if(pass2.length>20){
    passError2.innerHTML="Password must be below 20 characters";
    return false;
  }

  passError2.innerHTML='<i class="fa-solid fa-circle-check"></i><span>&nbsp;&nbsp;&nbsp;Password is Valid</span>';
  return true;
}


function validatePhone(){
  var phone=document.getElementById('phone').value;

  if(phone.length==0){
    phoneError.innerHTML='Phone is required';
    return false;
  }
  if(phone.length!==10){
    phoneError.innerHTML="PhoneNo should be 10 digits";
    return false;
  }
  
  phoneError.innerHTML='<i class="fa-solid fa-circle-check"></i><span>&nbsp;&nbsp;&nbsp;Phone Number is Valid</span>';
  return true;
}

function validateExpName(){
  var expenseName=document.getElementById('expensename').value;

  if(expenseName.length==0){
    expenseNameError.innerHTML='Name is required';
    return false;
  }
  expenseNameError.innerHTML='';
  return true;
}


function validateAmount(){
  var expenseAmount=document.getElementById('expensename').value;
  if(expenseAmount.length==0){
    expenseAmountError.innerHTML='Please Enter Amount';
    return false;
  }
  return true;
}


function validateSavingType(){
  var savingtype=document.getElementById('savings').value;

  if(savingtype.length==0){
    savingtype.innerHTML='Savings Type is required';
    return false;
  }
  savings.innerHTML='<i class="fa-solid fa-circle-check"></i><span>&nbsp;&nbsp;&nbsp;</span>';
  return true;
}

function ValidateForm(){
  if(!validateName() || !validateEmail() || !validatePass() || !validatePhone()){
    return false;
  }
  return true;
}
function ValidatePassword(){
  if(!validatePass() || !validatePass1() || !validatePass2()){
    return false;
  }
  return true;
}

function ValidateProfile(){
  if(!validateName()|| !validatePhone()){
    return false;
  }
  return true;
}

function ValidateSignIn(){
  if( !validateEmail() || !validatePass() ){
    return false;
  }
  return true;
}

function ValidateExpenseForm(){
  if( !validateExpName() || !validateSavingType() ){
    return false;
  }
  return true;
}