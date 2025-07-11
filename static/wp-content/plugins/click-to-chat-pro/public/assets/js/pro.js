! function(e) {
    e((function() {
        var t = "",
            c = window.location.href,
            n = void 0 !== document.title ? document.title : "",
            o = {};

        function _() {
            localStorage.getItem("ht_ctc_storage") && (o = localStorage.getItem("ht_ctc_storage"), o = JSON.parse(o))
        }

        function a(e) {
            return !!o[e] && o[e]
        }

        function r(e, t) {
            _(), o[e] = t;
            var c = JSON.stringify(o);
            localStorage.setItem("ht_ctc_storage", c)
        }
        _();
        var i = "";
        ! function() {
            if ("undefined" != typeof ht_ctc_chat_var) i = ht_ctc_chat_var;
            else try {
                if (document.querySelector(".ht_ctc_chat_data")) {
                    var t = e(".ht_ctc_chat_data").attr("data-settings");
                    i = JSON.parse(t)
                }
            } catch (e) {
                i = {}
            }
        }();
        var s, d, l, u = {};

        function g(t) {
            var c = "",
                n = t + "_data";
            if (void 0 !== window[t]) c = window[t];
            else try {
                if (document.querySelector("." + n)) {
                    var o = e("." + n).attr("data-settings");
                    c = JSON.parse(o)
                }
            } catch (e) {
                c = {}
            }
            return e("." + n).remove(), c
        }
        "undefined" != typeof ht_ctc_variables ? u = ht_ctc_variables : (u = {}, setTimeout((() => {
            u = "undefined" != typeof ht_ctc_variables ? ht_ctc_variables : {}
        }), 2e3)), s = e(".ht_ctc_multi_agent"), d = g("ht_ctc_multi_agent_main"), l = "yes", s.each((function(t, c) {
            var n = g(e(c).attr("data-key")),
                o = m().getDay();
            "0" == o && (o = 7);
            var _ = [];
            for (t = o; t <= 7; t++) _.push(t);
            if (7 !== _.length) {
                var a = 7 - _.length;
                for (t = 1; t <= a; t++) _.push(t)
            }
            var r = "yes";
            if (n.timings && "always" == n.timings) r = "yes";
            else if (n.timings && "set" == n.timings)
                if (n.time_sets) {
                    r = "no";
                    var i = n.time_sets,
                        s = v(),
                        u = 1;
                    i.forEach((e => {
                        e.stm <= s && s <= e.etm && 1 == u && (r = "yes", u++)
                    }))
                } else r = "no", l = "no";

            function f(t) {
                var o = e(c);
                e(c).css({
                    order: "1"
                }), o.find(".g_multi_box").css({
                    opacity: "0.5"
                }), o.find(".ctc_g_agent_tags").css({
                    color: "unset"
                }), "nochat" == t && e(c).css({
                    "pointer-events": "none"
                });
                var _ = function() {
                    var e = "";
                    if (n.time_sets) {
                        var t = v(),
                            c = n.time_sets,
                            o = "",
                            _ = 1;
                        if (c.forEach((e => {
                                t <= e.stm && 1 == _ && (o = e.stm, _++)
                            })), "" == o) {
                            var a = 10080 - t;
                            next_week_start_minute = c[0].stm, r = a + next_week_start_minute
                        } else var r = o - t;
                        (e = r) < 60 ? e = (e = Math.round(e)) + " " + (e < 2 ? d.ctc_minute : d.ctc_minutes) : 24 > (e /= 60) ? e = (e = Math.round(e)) + " " + (e < 2 ? d.ctc_hour : d.ctc_hours) : (e /= 24, e = (e = Math.round(e)) + " " + (e < 2 ? d.ctc_day : d.ctc_days))
                    }
                    return e
                }();
                "no" !== l && (o.find(".ctc_g_agent_tags .ctc_agent_next_time").append(_), o.find(".ctc_g_agent_tags .ctc_agent_next_time").css({
                    display: "flex"
                }))
            }
            "no" == r && d.agent_offline && ("chat" == d.agent_offline ? f("chat") : "nochat" == d.agent_offline ? f("nochat") : c.remove())
        })), g_hook_v = i.hook_v ? i.hook_v : "", g_hook_url = i.hook_url ? i.hook_url : "", document.addEventListener("ht_ctc_event_number", (function(e) {
            if ((i = e.detail.ctc).r_nums && i.r_nums[0]) {
                var t = i.r_nums;
                i.number = t[Math.floor(Math.random() * t.length)]
            }
        })), e(document).on("click", ".ht_ctc_chat_greetings_for_forum_link", (function(t) {
            e(".ht_ctc_chat_greetings_forum_link").trigger("click");
            var c = document.getElementById("ctc_pro_greetings_form");
            c && !1 === c.checkValidity() && e("#ctc_pro_greetings_form [type=checkbox][required]:not(:checked)").closest("div").fadeOut("1").fadeIn("1")
        })), i.form_no_duplicates && e(document).on("input", ".ctc_pro_greetings_form", (function(e) {
            r("form_data_change", (new Date).getTime())
        })), document.querySelector("#ctc_opt_g_form") && (e("#ctc_opt_g_form").on("change", (function(t) {
            e("#ctc_opt_g_form").is(":checked") && (e(".ctc_opt_g_form").hide(500), r("g_optin", "y"))
        })), a("g_optin") ? (e("#ctc_opt_g_form").prop("checked", !0), e(".ctc_opt_g_form").hide()) : e("#ctc_opt_g_form").prop("required", !0)), e(document).on("click", ".ht_ctc_chat_greetings_box_link_multi", (function(t) {
            function c() {
                var t = e(".ctc_g_content").attr("data-agentstyle");
                if ("card-1" == t ? e(".ctc_g_content").css({
                        padding: "4px 0px",
                        "background-color": "#f8f8f8"
                    }) : "7_1" == t && e(".ctc_g_content").css({
                        padding: "4px 0px 8px 0px"
                    }), e(".ctc_g_sentbutton").hide(), "card-1" == t) {
                    var c = e(".ctc_g_message_box");
                    e(c).removeClass("ctc_g_message_box"), e(c).css({
                        "background-color": "",
                        "text-align": "inherit",
                        padding: "4px 0px"
                    }), e(".ctc_g_heading_for_main_content").append(c)
                } else "7_1" == t && e(".ctc_g_message_box").css({
                    "background-color": "",
                    "text-align": "center",
                    padding: "4px 0px"
                });
                e(".ctc_g_agents").slideToggle("slow", (function() {}))
            }
            t.preventDefault(), document.querySelector("#ctc_opt_multi") ? e("#ctc_opt_multi").is(":checked") || a("g_optin") ? c() : e(".ctc_opt_in").show(400).fadeOut("1").fadeIn("1") : c(), document.querySelector("#ctc_opt_multi") && e("#ctc_opt_multi").on("change", (function(t) {
                e("#ctc_opt_multi").is(":checked") && (e(".ctc_opt_in").hide(100), r("g_optin", "y"), setTimeout((() => {
                    c()
                }), 500))
            }))
        })), document.querySelector(".add_ctc_chat") && ((e("#ctc_opt_multi").is(":checked") || a("g_optin")) && e(".add_ctc_chat").addClass("ctc_chat").removeClass("add_ctc_chat"), e(document).on("click", ".add_ctc_chat", (function(t) {
            e(".ctc_opt_in").show(400).fadeOut("1").fadeIn("1")
        })), e("#ctc_opt_multi").on("change", (function(t) {
            e("#ctc_opt_multi").is(":checked") && (e(".ctc_opt_in").hide(100), r("g_optin", "y"), e(".add_ctc_chat").addClass("ctc_chat").removeClass("add_ctc_chat"))
        })));
        var f = "no";

        function h(e, t) {
            try {
                e = (e = (e = e.replace("{number}", t)).replace("{title}", n)).replace("{url}", c)
            } catch (e) {}
            return e
        }

        function m() {
            var e = new Date,
                t = e.getTime() + 6e4 * e.getTimezoneOffset(),
                c = parseFloat(i.tz);
            return new Date(t + 36e5 * c)
        }
        e(document).on("submit", ".ctc_pro_greetings_form", (function(t) {
            t.preventDefault();
            try {
                e(".ctc_g_its_checkbox").each((function() {
                    e(this).is(":checked") && e(this).siblings(['type="hidden"']).prop("disabled", !0)
                }))
            } catch (t) {}
            var n = e(".ctc_pro_greetings_form").find(".ht_ctc_g_form_field").serializeArray();
            if (document.querySelector(".ctc_g_field_add_to_prefilled")) {
                var o = i.pre_filled,
                    _ = i.pre_filled,
                    s = e(".ctc_pro_greetings_form").find(".ctc_g_field_add_to_prefilled").serializeArray(),
                    d = "\n";
                for (var l of s.values()) {
                    var u = ".ctc_pro_greetings_form [name='" + (E = l.name) + "']",
                        g = E;
                    e(u)[0].hasAttribute("data-name") && (g = e(u).attr("data-name")), "" !== (I = l.value) && (d += g + ": " + I + "\n")
                }
                _ += d, i.pre_filled = _
            }
            e(".ht_ctc_chat_greetings_forum_link").addClass("ht_ctc_chat_greetings_box_link"), setTimeout((() => {
                e(".ht_ctc_chat_greetings_box_link").trigger("click")
            }), 20), setTimeout((() => {
                e(".ht_ctc_chat_greetings_forum_link").removeClass("ht_ctc_chat_greetings_box_link"), i.pre_filled && o && (i.pre_filled = o)
            }), 500);
            var h = e(".ctc_g_form_keys #ht_ctc_pro_greetings_nonce").val(),
                p = "no";
            try {
                if (i.form_no_duplicates) {
                    var v = (new Date).getTime(),
                        b = a("form_data_sent"),
                        k = Number.isInteger(b) ? Math.abs(v - b) : 60001,
                        w = a("form_data_change");
                    k < 6e4 ? Number.isInteger(w) && b >= w && (p = "y") : Number.isInteger(w) || r("form_data_change", v)
                }
            } catch (t) {}
            if ("y" == p || "y" == f);
            else if (f = "y", setTimeout((() => {
                    f = "n"
                }), 1e3), i.ajaxurl && i.g1_form_email && e.ajax({
                    url: i.ajaxurl,
                    type: "POST",
                    data: {
                        action: "ctc_pro_greetings_form",
                        form_data: n,
                        nonce: h
                    },
                    success: function(e) {
                        r("form_data_sent", (new Date).getTime())
                    },
                    error: function(e) {}
                }), i.g1_form_webhook) {
                var x = i.g1_form_webhook,
                    S = {};
                for (var l of n.values()) {
                    var E = l.name,
                        I = l.value;
                    S[E] = I
                }
                decoded_url = y(c), S.ctc_page_url = decoded_url;
                var T = m();
                if (S.ctc_wp_date = T.toDateString(), S.ctc_wp_time = T.getHours() + ":" + T.getMinutes() + ":" + T.getSeconds(), i.webhook_format && "json" == i.webhook_format) var q = S;
                else q = JSON.stringify(S);
                e.ajax({
                    url: x,
                    type: "POST",
                    mode: "no-cors",
                    data: q,
                    success: function(e) {
                        r("form_data_sent", (new Date).getTime())
                    },
                    error: function(e) {}
                })
            }
            try {
                e(".ctc_g_hidden_for_checkbox").each((function() {
                    e(this).prop("disabled", !1)
                }))
            } catch (t) {}
            0
        })), document.addEventListener("ht_ctc_event_hook", (function(e) {
            i = e.detail.ctc, number = i.chat_number && "" !== i.chat_number ? i.chat_number : e.detail.number;
            var t = m(),
                n = t.toDateString() + ", " + t.getHours() + ":" + t.getMinutes() + ":" + t.getSeconds();
            if (i.hook_url) {
                var o = i.hook_url ? i.hook_url : "";
                if (decoded_url = y(c), o = (o = (o = o.replace(/\{url}/gi, decoded_url)).replace(/\{number}/gi, number)).replace(/\{time}/gi, n), i.hook_v) {
                    hook_values = g_hook_v;
                    var _ = {},
                        a = 1;
                    hook_values.forEach((e => {
                        e = (e = (e = e.replace(/\{url}/gi, decoded_url)).replace(/\{number}/gi, number)).replace(/\{time}/gi, n), _["value" + a] = e, a++
                    })), i.hook_url = o, i.hook_v = _
                }
            }
        })), document.addEventListener("ht_ctc_event_display", (function(c) {
            if (i = c.detail.ctc, online_content = c.detail.online_content, i.display_user_base && (t = function(c) {
                    t = "no";
                    var n = (i = c.detail.ctc).display_user_base ? i.display_user_base : "",
                        o = "logged_out";
                    return document.querySelector("body").classList.contains("logged-in") && (o = "logged_in"), "logged_in" == n ? "logged_in" == o ? t = "yes" : i.ajaxurl && e.ajax({
                        url: i.ajaxurl,
                        data: {
                            action: "ctc_pro_is_user_logged_in"
                        },
                        success: function(e) {
                            "yes" == e.data && (t = "yes")
                        }
                    }) : "logged_out" == n && "logged_out" == o && (t = "yes"), t
                }(c)), "no" !== t)
                if (u.display_countries_list && u.display_countries_list.length > 0) {
                    document.dispatchEvent(new CustomEvent("ht_ctc_event_display_country_base", {
                        detail: {
                            ctc: i,
                            ctc_setItem: r,
                            ctc_getItem: a
                        }
                    }));
                    var n = 0,
                        o = setInterval((() => {
                            n++, u.country_code && (u.country_code.length > 0 && (t = u.display_countries_list.includes(u.country_code) ? "yes" : "no"), clearInterval(o), _()), n > 40 && (clearInterval(o), _())
                        }), 200)
                } else _();

            function _() {
                "no" !== t && function(t) {
                    i = t.detail.ctc, display_chat = t.detail.display_chat, ht_ctc_chat = t.detail.ht_ctc_chat;
                    var c = "",
                        n = i.bh,
                        o = (p.getDay(), p.getHours()),
                        _ = p.getMinutes();
                    if ("always" == n) c = "yes";
                    else if ("timebase" == n) {
                        var a = p.getDay();
                        "0" == a && (a = 7);
                        var r = "d" + a;
                        if (i[r]) {
                            var s = r + "_et";
                            if (i[d = r + "_st"] && i[s]) {
                                var d = i[d],
                                    l = (s = i[s], d.split(":")),
                                    u = s.split(":"),
                                    g = l[0],
                                    f = l[1],
                                    h = u[0],
                                    m = u[1];
                                g <= o && o <= h ? (c = "yes", g == o ? f > _ && (c = "no") : o == h && _ > m && (c = "no")) : c = "no"
                            } else c = "yes"
                        } else c = "no"
                    }

                    function v() {
                        "" !== i.timedelay || "" !== i.scroll ? ("" !== i.timedelay && setTimeout((() => {
                            display_chat(ht_ctc_chat)
                        }), 1e3 * i.timedelay), "" !== i.scroll && window.addEventListener("scroll", (function e() {
                            var t = document.documentElement,
                                c = document.body,
                                n = "scrollTop",
                                o = "scrollHeight";
                            (t[n] || c[n]) / ((t[o] || c[o]) - t.clientHeight) * 100 >= i.scroll && (display_chat(ht_ctc_chat), window.removeEventListener("scroll", e))
                        }), !1)) : display_chat(ht_ctc_chat)
                    }

                    function y() {
                        if (document.querySelector(".ctc_woo_schedule")) {
                            var t = e(".ctc_woo_schedule").attr("data-dt");
                            e(".ctc_woo_schedule").css("display", t)
                        }
                    }
                    "yes" == c ? (v(), y(), "undefined" != typeof online_content && online_content()) : "no" == c && (i.off_cta && (e(".ht-ctc-chat .ctc_cta").text(i.off_cta), e(".ctc_chat.ctc_woo_schedule .ctc_cta").text(i.off_cta)), i.off_num && (i.number = i.off_num, i.r_nums = ""), i.off_hide || (v(), y()), e(".for_greetings_header_image_badge").length && (i.offline_badge_color && (e(".for_greetings_header_image_badge").addClass("g_header_badge_online"), e(".g_header_badge_online").css("background-color", i.offline_badge_color)), e(".for_greetings_header_image_badge").show()))
                }(c)
            }
        })), document.addEventListener("ht_ctc_event_after_chat_displayed", (function(e) {
            if (i = e.detail.ctc, greetings_open = e.detail.greetings_open, greetings_close = e.detail.greetings_close, i.g_no_reopen && "user_closed" == a("g_user_action"));
            else if (i.g_time_action && setTimeout((() => {
                    greetings_open("time_action")
                }), 1e3 * i.g_time_action), i.g_scroll_action) {
                window.addEventListener("scroll", (function e() {
                    var t = document.documentElement,
                        c = document.body,
                        n = "scrollTop",
                        o = "scrollHeight";
                    (t[n] || c[n]) / ((t[o] || c[o]) - t.clientHeight) * 100 >= i.g_scroll_action && (greetings_open("scroll_action"), window.removeEventListener("scroll", e))
                }), !1)
            }
            if (document.querySelector(".ctc_greetings_now") && "IntersectionObserver" in window) {
                var t = window.innerHeight / 4 * -1;
                t = parseInt(t), rm = t + "px", rm = String(rm);
                var c = new IntersectionObserver((function(e) {
                    e.forEach((e => {
                        e.isIntersecting && (greetings_open("now"), c.unobserve(e.target))
                    }))
                }), {
                    rootMargin: rm
                });
                document.querySelectorAll(".ctc_greetings_now").forEach((e => {
                    c.observe(e, {
                        subtree: !0,
                        childList: !0
                    })
                }))
            }
        })), document.addEventListener("ht_ctc_event_analytics", (function(t) {
            var o = i.chat_number && "" !== i.chat_number ? i.chat_number : i.number;
            if (i.gads_conversation && "undefined" != typeof gtag) {
                var _ = i.gads_conversation,
                    a = {};
                a.send_to = _, u.g_ads_params && u.g_ads_params.forEach((e => {
                    if (u[e]) {
                        var t = u[e],
                            c = t.key,
                            n = t.value;
                        c = h(c, o), n = h(n, o), a[c] = n
                    }
                })), gtag("event", "conversion", a)
            }
            var r = i.nonce ? i.nonce : "";
            i.fb_conversion && e.ajax({
                url: i.ajaxurl,
                data: {
                    action: "ctc_pro_capi",
                    url: c,
                    title: n,
                    number: o,
                    nonce: r
                },
                type: "POST",
                success: function(e) {},
                error: function(e) {}
            })
        })), document.querySelector(".ht_ctc_chat_greetings_box_layout") && e(".ht_ctc_chat_greetings_box_layout").css("background-color", "unset");
        var p = m();

        function v() {
            var e = m(),
                t = e.getDay();
            return "0" == t && (t = 7), 60 * (24 * (t - 1) + e.getHours()) + e.getMinutes()
        }

        function y(e) {
            new_value = e;
            try {
                new_value = decodeURI(e)
            } catch (e) {}
            return new_value
        }
        v()
    }))
}(jQuery);