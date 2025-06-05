/*!
* Start Bootstrap - Creative v7.0.5 (https://startbootstrap.com/theme/creative)
* Copyright 2013-2021 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-creative/blob/master/LICENSE)
*/
//
// Scripts
// 

window.addEventListener('DOMContentLoaded', event => {

    // Navbar shrink function
    var navbarShrink = function () {
        const navbarCollapsible = document.body.querySelector('#mainNav');
        if (!navbarCollapsible) {
            return;
        }
        if (window.scrollY === 0) {
            navbarCollapsible.classList.remove('navbar-shrink')
        } else {
            navbarCollapsible.classList.add('navbar-shrink')
        }

    };

    // Shrink the navbar 
    navbarShrink();

    // Shrink the navbar when page is scrolled
    document.addEventListener('scroll', navbarShrink);

    // Activate Bootstrap scrollspy on the main nav element
    const mainNav = document.body.querySelector('#mainNav');
    if (mainNav) {
        new bootstrap.ScrollSpy(document.body, {
            target: '#mainNav',
            offset: 74,
        });
    };

    // Collapse responsive navbar when toggler is visible
    const navbarToggler = document.body.querySelector('.navbar-toggler');
    const responsiveNavItems = [].slice.call(
        document.querySelectorAll('#navbarResponsive .nav-link')
    );
    responsiveNavItems.map(function (responsiveNavItem) {
        responsiveNavItem.addEventListener('click', () => {
            if (window.getComputedStyle(navbarToggler).display !== 'none') {
                navbarToggler.click();
            }
        });
    });

    // Activate SimpleLightbox plugin for portfolio items
    new SimpleLightbox({
        elements: '#portfolio a.portfolio-box'
    });

});

// LOOGOUT USER SUCCESSFULL
$(document).ready(function () {
    $("#logout").click(function () {
        // e.preventDefault();
        Swal.fire({
            title: "¿Cerrar sesión?",
            text: "Tu sesión se cerrará y tendrás que volver a iniciar sesión.",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Sí, cerrar sesión",
            cancelButtonText: "Cancelar"
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: "/cerrarsesion",
                    type: "POST",
                    success: function (response) {
                        if (response.success) {
                            Swal.fire("Sesión cerrada Exitosamente", response.message, "success")
                            .then(() => {
                                window.location.href = "/";
                            });
                        } else {
                            Swal.fire("Error", "No se pudo cerrar sesión.", "error");
                        }
                    },
                    error: function () {
                        Swal.fire("Error", "No se pudo conectar con el servidor.", "error");
                    }
                });
            }
        });
    });
});
//INICIO DE SESION PENDIENTE
$(document).ready(function () {
    $("#login-form").submit(function (event) {
        event.preventDefault(); // Evita que el formulario se envíe de manera tradicional

        var usuario = $("#usuario").val();
        var password = $("#password").val();

        $.ajax({
            url: "/validar_usuario",
            type: "POST",
            data: { usuario: usuario, password: password },  // Enviar como form-data
            success: function (response) {
                if (response.success) {
                    Swal.fire({
                        title: "¡Bienvenido!",
                        text: response.message,
                        icon: "success",
                        timer: 2000,
                        showConfirmButton: false
                    }).then(() => {
                        window.location.href = "/";
                    });
                } else {
                    Swal.fire("Error", response.message, "error");
                }
            },
            error: function (xhr, status, error) {
                console.log("Error en AJAX:", xhr.responseText); // Muestra el error exacto
                Swal.fire("Error", "No se pudo conectar con el servidor.", "error");
            }
        });
    });
});

// FUNCION ELIMINAR REGISTROS USUARIOS SUCCESSSFUL
$(document).ready(function () {
    $(".delete-btn").click(function () {
        var userId = $(this).data("id");
        var row = $("#row-" + userId);

        Swal.fire({
            title: "⚠️ ¿Estás seguro de Eliminar este Usuario?",
            text: "Esta acción no se puede deshacer",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: "#d33",
            cancelButtonColor: "#3085d6",
            confirmButtonText: "Sí, eliminar",
            cancelButtonText: "Cancelar"
        }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                    url: "/eliminar_usuarios/",
                    type: "POST",
                    contentType: "application/json",
                    data: JSON.stringify({ id: userId }),
                    success: function (response) {
                        if (response.success) {
                            Swal.fire("Eliminado", response.message, "success").then(() => {
                                row.fadeOut("slow", function () { $(this).remove(); });
                            });
                        } else {
                            Swal.fire("Error", response.message, "error");
                        }
                    },
                    error: function (xhr) {
                        if (xhr.status === 403) {
                            Swal.fire("Error", "Debe iniciar sesión nuevamente", "error")
                                .then(() => { window.location.href = "/login"; });
                        } else {
                            Swal.fire("Error", "No se pudo conectar con el servidor.", "error");
                        }
                    }
                });
            }
        });
    });
});
