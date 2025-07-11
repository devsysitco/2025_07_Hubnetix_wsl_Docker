jQuery(function($) {

    jQuery(document).on("click", ".continue_login", function(e) {
        e.preventDefault();
        jQuery(".login_error").empty();
        var coutrycode = jQuery("#c_code").val();
        var mobile_number = jQuery("input[name=mobile_number]").val();
        if (mobile_number == "" || coutrycode == "") {
            showclErrorMessage("Invalid phoneNumber.", 'errormsg_cls');
            return;
        }
        if (!jQuery.isNumeric(mobile_number)) {
            showclErrorMessage("Invalid phoneNumber.", 'errormsg_cls');
            return;
        }

        var data = {
            'action': 'send_otp',
            'coutrycode': coutrycode,
            'mobile_number': mobile_number,
        };

        jQuery.post(my_ajax_object.ajax_url, data, function(response) {
            console.log(response);
            if (response == 0) {
                jQuery("#login_otp").remove();
                jQuery(".continue_login").addClass("verify_otp").removeClass('continue_login');
                jQuery(".verify_otp").attr("disabled", "disabled");
                jQuery('.verify_otp').html(jQuery('.login-inner .popup-header').attr('continue-text'));
                jQuery(".input_login_field").hide();
                jQuery(".login-inner .popup-header h2").html(jQuery('.login-inner .popup-header').attr('data-verify-text'));
                //timer
                var timer2 = "1:01";
                var interval = setInterval(function() {


                    var timer = timer2.split(':');
                    //by parsing integer, I avoid all extra string processing
                    var minutes = parseInt(timer[0], 10);
                    var seconds = parseInt(timer[1], 10);
                    --seconds;
                    minutes = (seconds < 0) ? --minutes : minutes;
                    if (minutes < 0) clearInterval(interval);
                    seconds = (seconds < 0) ? 59 : seconds;
                    seconds = (seconds < 10) ? '0' + seconds : seconds;
                    //minutes = (minutes < 10) ?  minutes : minutes;
                    jQuery('.countdown').html(jQuery('.login-inner .popup-header').attr('resend-code') + " : " + minutes + ':' + seconds);
                    if (minutes == 0 && seconds == 00) {
                        jQuery('.countdown').remove();
                        jQuery('.continue_login').remove();
                        jQuery('.otp_section').append('<button class="continue_login">' + jQuery('.login-inner .popup-header').attr('resend-code') + '</button>');
                    }
                    timer2 = minutes + ':' + seconds;
                }, 1000);

                jQuery(".otp_section").html("<p class='verify_text'>" + jQuery('.login-inner .popup-header').attr('code-text') + "</p><b>+" + coutrycode + " " + mobile_number + "</b><input type='number' name='otp' id='login_otp' placeholder='0 0 0 0 0 0'><div class='countdown'></div>");

            } else {
                // /showclErrorMessage(response);
                jQuery(".login_error").html(response);
                jQuery('.continue_login').html(jQuery('.login-inner .popup-header').attr('continue-text'));
                jQuery(".continue_login").attr("disabled", "disabled");
            }
        });
    });
    jQuery(document).on("click", ".verify_otp", function(e) {
        e.preventDefault();
        jQuery("#login_otp").focus();
        var coutrycode = jQuery("#c_code").val();
        var mobile_number = jQuery("input[name=mobile_number]").val();
        var otp = jQuery("input[name=otp]").val();
        var data = {
            'action': 'verify_otp',
            'coutrycode': coutrycode,
            'mobile_number': mobile_number,
            'otp': otp,
        };
        jQuery.post(my_ajax_object.ajax_url, data, function(response) {
            //console.log(response);
            if (response == 0) {
                var data = {
                    'action': 'verify_login',
                    'mobile_number': mobile_number,
                };
                jQuery.post(my_ajax_object.ajax_url, data, function(response) {
                    console.log(response);
                    if (response.data.code == 0) {

                        document.cookie = temp_user_id = response.data.user_id;

                        jQuery(".user_name").text(response.data.user_name);
                        jQuery("#login_btn").remove();
                        jQuery(".header_btn").addClass("user_data");
                        jQuery(".header_btn").removeClass("login_btn");
                        jQuery(".mobilemenu-inner h2").text(response.data.user_name);
                        jQuery(".mobilemenu-inner p").text(response.data.number);
                        jQuery(".login-popup").removeClass("is-active");
                        location.reload();
                        //showclErrorMessage("Login Successfully.",'successmsg_cls');

                    }
                    if (response.data.code == 1) {
                        jQuery("#login_form").hide();
                        jQuery(".login-inner .popup-header h2").html(jQuery('.login-inner .popup-header').attr('signup-text'));
                        jQuery(".register_user").show();
                        jQuery("#user_regis_btn").append('<input type="hidden" name="mobile_number" value="' + mobile_number + '">');
                        jQuery("#user_regis_btn").append('<input type="hidden" name="coutrycode" value="' + coutrycode + '">');
                    }
                });
            } else {
                jQuery(".login_error").html(response);
                //showclErrorMessage(response);
            }
        });
    });
    jQuery(document).on("click", "#user_regis_btn", function(e) {
        e.preventDefault();
        var user_email = jQuery("#user_email").val();
        var first_name = jQuery("#first_name").val();
        var last_name = jQuery("#last_name").val();
        var user_gender = jQuery("#user_gender").val();
        var birth_date = jQuery("#datepicker").val();
        var coutrycode = jQuery("#c_code").val();
        var mobile_number = jQuery("input[name=mobile_number]").val();
        if (user_email == '') {
            showclErrorMessage("Enter Email Address", 'errormsg_cls');
            return;
        }
        if (first_name == '') {
            showclErrorMessage("Enter first name", 'errormsg_cls');
            return;
        }
        if (last_name == '') {
            showclErrorMessage("Enter last name", 'errormsg_cls');
            return;
        }
        var data = {
            'action': 'register_user',
            'first_name': first_name,
            'last_name': last_name,
            'user_email': user_email,
            'user_gender': user_gender,
            'birth_date': birth_date,
            'coutrycode': coutrycode,
            'mobile_number': mobile_number,
        };
        jQuery.post(my_ajax_object.ajax_url, data, function(response) {
            console.log();
            if (response.data.code == 0) {
                document.cookie = temp_user_id = response.data.user_id;
                //initFreshChat(user_email,first_name,mobile_number,coutrycode);
                //initialize();
                jQuery(".user_name").text(response.data.user_name);
                jQuery("#login_btn").remove();
                jQuery(".header_btn").addClass("user_data");
                jQuery(".header_btn").removeClass("login_btn");
                jQuery(".mobilemenu-inner h2").text(response.data.user_name);
                jQuery(".mobilemenu-inner p").text(response.data.number);
                jQuery(".login-popup").removeClass("is-active");
                location.reload();
                //showclErrorMessage("Registeration Successfully.",'successmsg_cls');
            } else {
                showclErrorMessage(response.data.msg, 'errormsg_cls');
            }
        });
    });

    jQuery(document).on("click", "#login_btn,.login_btn", function() {
        jQuery(this).addClass('hide');
        jQuery('.login-popup').addClass('is-active');
    });
    jQuery(document).on("click", "button.header_btn.user_menu", function() {
        jQuery('.menu-inner .header_right ul.user-menu').toggleClass('is-active');
    });
    jQuery(document).on('click', '.login-popup .login-inner .popup-header svg', function() {
        jQuery('.login-popup').removeClass('is-active');
        jQuery('.chat-icon').removeClass('hide');
    });
    jQuery(document).on("keyup keypress change", "input[name=mobile_number]", function() {

        var mobile_number = jQuery(this).val();
        var c_code = jQuery("#c_code").val();
        jQuery(this).attr('data-number', mobile_number);

    });

    var numbercheck = setInterval(function() {
        var mobile_number = jQuery('input[name="mobile_number"]').attr('data-number');
        if (mobile_number) {
            var mob_length = mobile_number.length;
            var c_code = jQuery("#c_code").val();
            // console.log(mob_length);

            if (c_code == '91' && mob_length == 10) {
                jQuery('.continue_login').trigger('click');
                jQuery('.continue_login').html("<div class='small_loader'></div>");
                clearInterval(numbercheck);
            }
            if (c_code == '974' && mob_length == 9) {
                jQuery('.continue_login').trigger('click');
                jQuery('.continue_login').html("<div class='small_loader'></div>");
                clearInterval(numbercheck);
            }
        }
    }, 500);

    jQuery(document).on("keyup change", ".phone_field input[name=mobile_number]", function() {
        var phone = jQuery(this).val();
        if (phone != '') {
            jQuery(".continue_login").removeAttr("disabled");
        } else {
            jQuery(".continue_login").attr("disabled", "disabled");
            jQuery('.continue_login').html(jQuery('.login-inner .popup-header').attr('continue-text'));
        }
    });
    jQuery(document).on("keyup change", "input[name=otp]", function() {
        var phone = jQuery(this).val();
        //var a = jQuery("input[name=mobile_number]").val();
        var otp_length = phone.length;
        if (otp_length == 6) {
            jQuery(".verify_otp").removeAttr("disabled");
            jQuery('.verify_otp').trigger('click');
            jQuery('.verify_otp').html("<div class='small_loader'></div>");
        } else {
            jQuery(".verify_otp").attr("disabled", "disabled");
            jQuery('.verify_otp').html(jQuery('.login-inner .popup-header').attr('continue-text'));
        }
    });

    function showclErrorMessage(message, msgclass) {
        jQuery(".cl_popmessage").remove();
        jQuery("body").append("<div class='cl_popmessage " + msgclass + "'><div class='cl_popmessage_contents'>" + message + "</div></div>");
    }
});