document.addEventListener("DOMContentLoaded", () => {

    const toggle = document.getElementById("togglePassword");

    const password = document.getElementById("password");

    if(toggle){

        toggle.addEventListener("click", () => {

            if(password.type==="password"){

                password.type="text";

                toggle.classList.remove("bi-eye");

                toggle.classList.add("bi-eye-slash");

            }else{

                password.type="password";

                toggle.classList.remove("bi-eye-slash");

                toggle.classList.add("bi-eye");

            }

        });

    }

});