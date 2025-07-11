$(document).ready(function() {
    // Enable hover for dropdown on desktop screens
    if ($(window).width() > 768) {
        $('.navbar-nav .nav-item.dropdown').hover(function() {
            $(this).find('.dropdown-menu').first().stop(true, true).delay(250).slideDown();
        }, function() {
            $(this).find('.dropdown-menu').first().stop(true, true).delay(100).slideUp();
        });
    }
});


 var mainSwiper = new Swiper('.main-swiper', {
            // Your main swiper configuration here
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
            autoplay: {
    delay: 3000,
  },
        });

          var thumbnailSwiper = new Swiper('.thumbnail-swiper', {
            // Your thumbnail swiper configuration here
            slidesPerView: 3, // Number of thumbnail slides to display
            spaceBetween: 10, // Space between thumbnail slides
            navigation: {
                nextEl: '.swiper-button-next',
                prevEl: '.swiper-button-prev',
            },
        });

        // Add a click event listener to thumbnail slides
        thumbnailSwiper.on('click', function () {
            // Get the clicked thumbnail index
            var clickedIndex = thumbnailSwiper.clickedIndex;
            
            // Set the main swiper to the clicked index
            mainSwiper.slideTo(clickedIndex);
        });

function animateCounter() {
        const counters = document.querySelectorAll(".count");
        counters.forEach(function (counter) {
            const target = parseInt(counter.textContent, 10);
            let current = 0;

            const increment = target / 100; // Adjust the increment as needed
            const duration = 1000; // Adjust the duration (in milliseconds) as needed

            const updateCounter = () => {
                current += increment;
                counter.textContent = Math.round(current);

                if (current < target) {
                    requestAnimationFrame(updateCounter);
                } else {
                    counter.textContent = target;
                }
            };

            updateCounter();
        });
    }

    // Call the animateCounter function when the page is loaded
    window.addEventListener("load", animateCounter);


 var owl = $('.home-info-list');
        owl.owlCarousel({
            margin: 0,
            loop: true,
            autoplay:true,
            autoplayTimeout: 4000,
            autoplayHoverPause: true,
            center: false,
            nav: true,
            dots:true,
            responsive: {
                0: {
                    items: 3,
                    margin: 10,
                 
                },
                600: {
                    items: 4,
                   
                },
                1000: {
                    items: 4
                }
            },
            navText: ["<i class='lni lni-chevron-left'></i>", "<i class='lni lni-chevron-right'></i>"]
        })



 var owl = $('.home-service-list');
        owl.owlCarousel({
            margin: 0,
            loop: true,
            autoplay:true,
            autoplayTimeout: 4000,
            autoplayHoverPause: true,
            center: false,
            nav: true,
            dots:true,
            responsive: {
                0: {
                    items: 3,
                    margin: 10,
                 
                },
                600: {
                    items: 4,
                   
                },
                1000: {
                    items: 5
                }
            },
            navText: ["<i class='lni lni-chevron-left'></i>", "<i class='lni lni-chevron-right'></i>"]
        })


 var owl = $('.home-location-list');
        owl.owlCarousel({
            margin: 0,
            loop: true,
            autoplay:true,
            autoplayTimeout: 4000,
            autoplayHoverPause: true,
            center: false,
            nav: false,
            dots:false,
            responsive: {
                0: {
                    items: 3,
                    margin: 10,
                 
                },
                600: {
                    items: 2,
                   
                },
                1000: {
                    items: 4
                }
            },
            navText: ["<i class='lni lni-chevron-left'></i>", "<i class='lni lni-chevron-right'></i>"]
        })


$(document).ready(function() {
    $('#home-sectors .card .btn').click(function() {
        // Toggle the background color of the parent card based on aria-expanded
        var card = $(this).closest('.card');
        if (card.find('.btn').attr('aria-expanded') === "true") {
            card.addClass('active-card');
        } else {
            card.removeClass('active-card');
        }
    });
});



