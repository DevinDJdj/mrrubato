"undefined" === typeof Color && (Color = {});
"undefined" === typeof Color.Space && (Color.Space = {});
(function () {
    var b = {},
    a = {
        "HEX24>HSL": "HEX24>RGB>HSL",
        "HEX32>HSLA": "HEX32>RGBA>HSLA",
        "HEX24>CMYK": "HEX24>RGB>CMY>CMYK",
        "RGB>CMYK": "RGB>CMY>CMYK"
    },
    c = Color.Space = function (e, d) {
        a[d] && (d = a[d]);
        var k = d.split(">");
        if ("object" === typeof e && 0 <= e[0]) {
            for (var m = k[0], g = {}, f = 0; f < m.length; f++) {
                var l = m.substr(f, 1);
                g[l] = e[f]
            }
            e = g
        }
        if (b[d])
            return b[d](e);
        m = 1;
        for (g = k[0]; m < k.length; m++)
            1 < m && (g = g.substr(g.indexOf("_") + 1)), g += (0 === m ? "" : "_") + k[m], e = c[g](e);
        return e
    };
    c.RGB_W3 = function (a) {
        return "rgb(" + (a.R >> 0) + "," + (a.G >> 0) +
        "," + (a.B >> 0) + ")"
    };
    c.RGBA_W3 = function (a) {
        return "rgba(" + (a.R >> 0) + "," + (a.G >> 0) + "," + (a.B >> 0) + "," + ("number" === typeof a.A ? a.A / 255 : 1) + ")"
    };
    c.W3_RGB = function (a) {
        a = a.substr(4, a.length - 5).split(",");
        return {
            R: parseInt(a[0]),
            G: parseInt(a[1]),
            B: parseInt(a[2])
        }
    };
    c.W3_RGBA = function (a) {
        a = a.substr(5, a.length - 6).split(",");
        return {
            R: parseInt(a[0]),
            G: parseInt(a[1]),
            B: parseInt(a[2]),
            A: 255 * parseFloat(a[3])
        }
    };
    c.HSL_W3 = function (a) {
        return "hsl(" + (a.H + 0.5 >> 0) + "," + (a.S + 0.5 >> 0) + "%," + (a.L + 0.5 >> 0) + "%)"
    };
    c.HSLA_W3 = function (a) {
        return "hsla(" +
        (a.H + 0.5 >> 0) + "," + (a.S + 0.5 >> 0) + "%," + (a.L + 0.5 >> 0) + "%," + ("number" === typeof a.A ? a.A / 255 : 1) + ")"
    };
    c.W3_HSL = function (a) {
        a = a.substr(4, a.length - 5).split(",");
        return {
            H: parseInt(a[0]),
            S: parseInt(a[1]),
            L: parseInt(a[2])
        }
    };
    c.W3_HSLA = function (a) {
        a = a.substr(5, a.length - 6).split(",");
        return {
            H: parseInt(a[0]),
            S: parseInt(a[1]),
            L: parseInt(a[2]),
            A: 255 * parseFloat(a[3])
        }
    };
    c.W3_HEX = c.W3_HEX24 = function (a) {
        "#" === a.substr(0, 1) && (a = a.substr(1));
        3 === a.length && (a = a[0] + a[0] + a[1] + a[1] + a[2] + a[2]);
        return parseInt("0x" + a)
    };
    c.W3_HEX32 =
    function (a) {
        "#" === a.substr(0, 1) && (a = a.substr(1));
        return 6 === a.length ? parseInt("0xFF" + a) : parseInt("0x" + a)
    };
    c.HEX_W3 = c.HEX24_W3 = function (a, d) {
        d || (d = 6);
        a || (a = 0);
        for (var b = a.toString(16), c = b.length; c < d; )
            b = "0" + b, c++;
        for (c = b.length; c > d; )
            b = b.substr(1), c--;
        return "#" + b
    };
    c.HEX32_W3 = function (a) {
        return c.HEX_W3(a, 8)
    };
    c.HEX_RGB = c.HEX24_RGB = function (a) {
        return {
            R: a >> 16,
            G: a >> 8 & 255,
            B: a & 255
        }
    };
    c.HEX32_RGBA = function (a) {
        return {
            R: a >>> 16 & 255,
            G: a >>> 8 & 255,
            B: a & 255,
            A: a >>> 24
        }
    };
    c.RGBA_HEX32 = function (a) {
        return (a.A << 24 | a.R << 16 |
            a.G << 8 | a.B) >>> 0
    };
    c.RGB_HEX24 = c.RGB_HEX = function (a) {
        0 > a.R && (a.R = 0);
        0 > a.G && (a.G = 0);
        0 > a.B && (a.B = 0);
        255 < a.R && (a.R = 255);
        255 < a.G && (a.G = 255);
        255 < a.B && (a.B = 255);
        return a.R << 16 | a.G << 8 | a.B
    };
    c.RGB_CMY = function (a) {
        return {
            C: 1 - a.R / 255,
            M: 1 - a.G / 255,
            Y: 1 - a.B / 255
        }
    };
    c.RGBA_HSLA = c.RGB_HSL = function (a) {
        var d = a.R / 255,
        b = a.G / 255,
        c = a.B / 255,
        g = Math.min(d, b, c),
        f = Math.max(d, b, c),
        l = f - g,
        n,
        r = (f + g) / 2;
        if (0 === l)
            g = n = 0;
        else {
            var g = 0.5 > r ? l / (f + g) : l / (2 - f - g),
            q = ((f - d) / 6 + l / 2) / l,
            p = ((f - b) / 6 + l / 2) / l,
            l = ((f - c) / 6 + l / 2) / l;
            d === f ? n = l - p : b === f ? n = 1 / 3 + q - l :
                c === f && (n = 2 / 3 + p - q);
            0 > n && (n += 1);
            1 < n && (n -= 1)
        }
        return {
            H: 360 * n,
            S: 100 * g,
            L: 100 * r,
            A: a.A
        }
    };
    c.RGBA_HSVA = c.RGB_HSV = function (a) {
        var d = a.R / 255,
        b = a.G / 255,
        c = a.B / 255,
        g = Math.min(d, b, c),
        f = Math.max(d, b, c),
        l = f - g,
        n;
        if (0 === l)
            g = n = 0;
        else {
            var g = l / f,
            r = ((f - d) / 6 + l / 2) / l,
            q = ((f - b) / 6 + l / 2) / l,
            l = ((f - c) / 6 + l / 2) / l;
            d === f ? n = l - q : b === f ? n = 1 / 3 + r - l : c === f && (n = 2 / 3 + q - r);
            0 > n && (n += 1);
            1 < n && (n -= 1)
        }
        return {
            H: 360 * n,
            S: 100 * g,
            V: 100 * f,
            A: a.A
        }
    };
    c.CMY_RGB = function (a) {
        return {
            R: Math.max(0, 255 * (1 - a.C)),
            G: Math.max(0, 255 * (1 - a.M)),
            B: Math.max(0, 255 * (1 - a.Y))
        }
    };
    c.CMY_CMYK =
    function (a) {
        var d = a.C,
        b = a.M;
        a = a.Y;
        var c = Math.min(a, Math.min(b, Math.min(d, 1))),
        d = Math.round(100 * ((d - c) / (1 - c))),
        b = Math.round(100 * ((b - c) / (1 - c)));
        a = Math.round(100 * ((a - c) / (1 - c)));
        c = Math.round(100 * c);
        return {
            C: d,
            M: b,
            Y: a,
            K: c
        }
    };
    c.CMYK_CMY = function (a) {
        return {
            C: a.C * (1 - a.K) + a.K,
            M: a.M * (1 - a.K) + a.K,
            Y: a.Y * (1 - a.K) + a.K
        }
    };
    c.HSLA_RGBA = c.HSL_RGB = function (a) {
        var d = a.H / 360,
        b = a.S / 100,
        c = a.L / 100,
        g,
        f,
        l;
        0 === b ? c = b = d = c : (f = 0.5 > c ? c * (1 + b) : c + b - b * c, g = 2 * c - f, l = d + 1 / 3, 0 > l && (l += 1), 1 < l && (l -= 1), c = 1 > 6 * l ? g + 6 * (f - g) * l : 1 > 2 * l ? f : 2 > 3 * l ? g + 6 * (f - g) *
                    (2 / 3 - l) : g, l = d, 0 > l && (l += 1), 1 < l && (l -= 1), b = 1 > 6 * l ? g + 6 * (f - g) * l : 1 > 2 * l ? f : 2 > 3 * l ? g + 6 * (f - g) * (2 / 3 - l) : g, l = d - 1 / 3, 0 > l && (l += 1), 1 < l && (l -= 1), d = 1 > 6 * l ? g + 6 * (f - g) * l : 1 > 2 * l ? f : 2 > 3 * l ? g + 6 * (f - g) * (2 / 3 - l) : g);
        return {
            R: 255 * c,
            G: 255 * b,
            B: 255 * d,
            A: a.A
        }
    };
    c.HSVA_RGBA = c.HSV_RGB = function (a) {
        var d = a.H / 360,
        b = a.S / 100,
        c = a.V / 100,
        g,
        f,
        l;
        if (0 === b)
            g = f = l = Math.round(255 * c);
        else
            switch (1 <= d && (d = 0), d *= 6, D = d - Math.floor(d), A = Math.round(255 * c * (1 - b)), l = Math.round(255 * c * (1 - b * D)), C = Math.round(255 * c * (1 - b * (1 - D))), c = Math.round(255 * c), Math.floor(d)) {
            case 0:
                g =
                    c;
                f = C;
                l = A;
                break;
            case 1:
                g = l;
                f = c;
                l = A;
                break;
            case 2:
                g = A;
                f = c;
                l = C;
                break;
            case 3:
                g = A;
                f = l;
                l = c;
                break;
            case 4:
                g = C;
                f = A;
                l = c;
                break;
            case 5:
                g = c,
                f = A
            }
        return {
            R: g,
            G: f,
            B: l,
            A: a.A
        }
    }
})();
if ("undefined" === typeof MIDI)
    var MIDI = {};
(function () {
    var b = {},
    a = 0,
    c = function (c) {
        a++;
        var d = new Audio,
        k = c.split(";")[0];
        d.id = "audio";
        d.setAttribute("preload", "auto");
        d.setAttribute("audiobuffer", !0);
        d.addEventListener("error", function () {
            b[k] = !1;
            a--
        }, !1);
        d.addEventListener("canplaythrough", function () {
            b[k] = !0;
            a--
        }, !1);
        d.src = "data:" + c;
        document.body.appendChild(d)
    };
    MIDI.audioDetect = function (e) {
        if ("undefined" === typeof Audio)
            return e({});
        var d = new Audio;
        if ("undefined" === typeof d.canPlayType)
            return e(b);
        var k = d.canPlayType('audio/ogg; codecs="vorbis"'),
        k = "probably" === k || "maybe" === k,
        d = d.canPlayType("audio/mpeg"),
        d = "probably" === d || "maybe" === d;
        if (k || d) {
            k && c("audio/ogg;base64,T2dnUwACAAAAAAAAAADqnjMlAAAAAOyyzPIBHgF2b3JiaXMAAAAAAUAfAABAHwAAQB8AAEAfAACZAU9nZ1MAAAAAAAAAAAAA6p4zJQEAAAANJGeqCj3//////////5ADdm9yYmlzLQAAAFhpcGguT3JnIGxpYlZvcmJpcyBJIDIwMTAxMTAxIChTY2hhdWZlbnVnZ2V0KQAAAAABBXZvcmJpcw9CQ1YBAAABAAxSFCElGVNKYwiVUlIpBR1jUFtHHWPUOUYhZBBTiEkZpXtPKpVYSsgRUlgpRR1TTFNJlVKWKUUdYxRTSCFT1jFloXMUS4ZJCSVsTa50FkvomWOWMUYdY85aSp1j1jFFHWNSUkmhcxg6ZiVkFDpGxehifDA6laJCKL7H3lLpLYWKW4q91xpT6y2EGEtpwQhhc+211dxKasUYY4wxxsXiUyiC0JBVAAABAABABAFCQ1YBAAoAAMJQDEVRgNCQVQBABgCAABRFcRTHcRxHkiTLAkJDVgEAQAAAAgAAKI7hKJIjSZJkWZZlWZameZaouaov+64u667t6roOhIasBACAAAAYRqF1TCqDEEPKQ4QUY9AzoxBDDEzGHGNONKQMMogzxZAyiFssLqgQBKEhKwKAKAAAwBjEGGIMOeekZFIi55iUTkoDnaPUUcoolRRLjBmlEluJMYLOUeooZZRCjKXFjFKJscRUAABAgAMAQICFUGjIigAgCgCAMAYphZRCjCnmFHOIMeUcgwwxxiBkzinoGJNOSuWck85JiRhjzjEHlXNOSuekctBJyaQTAAAQ4AAAEGAhFBqyIgCIEwAwSJKmWZomipamiaJniqrqiaKqWp5nmp5pqqpnmqpqqqrrmqrqypbnmaZnmqrqmaaqiqbquqaquq6nqrZsuqoum65q267s+rZru77uqapsm6or66bqyrrqyrbuurbtS56nqqKquq5nqq6ruq5uq65r25pqyq6purJtuq4tu7Js664s67pmqq5suqotm64s667s2rYqy7ovuq5uq7Ks+6os+75s67ru2rrwi65r66os674qy74x27bwy7ouHJMnqqqnqq7rmarrqq5r26rr2rqmmq5suq4tm6or26os67Yry7aumaosm64r26bryrIqy77vyrJui67r66Ys67oqy8Lu6roxzLat+6Lr6roqy7qvyrKuu7ru+7JuC7umqrpuyrKvm7Ks+7auC8us27oxuq7vq7It/KosC7+u+8Iy6z5jdF1fV21ZGFbZ9n3d95Vj1nVhWW1b+V1bZ7y+bgy7bvzKrQvLstq2scy6rSyvrxvDLux8W/iVmqratum6um7Ksq/Lui60dd1XRtf1fdW2fV+VZd+3hV9pG8OwjK6r+6os68Jry8ov67qw7MIvLKttK7+r68ow27qw3L6wLL/uC8uq277v6rrStXVluX2fsSu38QsAABhwAAAIMKEMFBqyIgCIEwBAEHIOKQahYgpCCKGkEEIqFWNSMuakZM5JKaWUFEpJrWJMSuaclMwxKaGUlkopqYRSWiqlxBRKaS2l1mJKqcVQSmulpNZKSa2llGJMrcUYMSYlc05K5pyUklJrJZXWMucoZQ5K6iCklEoqraTUYuacpA46Kx2E1EoqMZWUYgupxFZKaq2kFGMrMdXUWo4hpRhLSrGVlFptMdXWWqs1YkxK5pyUzDkqJaXWSiqtZc5J6iC01DkoqaTUYiopxco5SR2ElDLIqJSUWiupxBJSia20FGMpqcXUYq4pxRZDSS2WlFosqcTWYoy1tVRTJ6XFklKMJZUYW6y5ttZqDKXEVkqLsaSUW2sx1xZjjqGkFksrsZWUWmy15dhayzW1VGNKrdYWY40x5ZRrrT2n1mJNMdXaWqy51ZZbzLXnTkprpZQWS0oxttZijTHmHEppraQUWykpxtZara3FXEMpsZXSWiypxNhirLXFVmNqrcYWW62ltVprrb3GVlsurdXcYqw9tZRrrLXmWFNtBQAADDgAAASYUAYKDVkJAEQBAADGMMYYhEYpx5yT0ijlnHNSKucghJBS5hyEEFLKnINQSkuZcxBKSSmUklJqrYVSUmqttQIAAAocAAACbNCUWByg0JCVAEAqAIDBcTRNFFXVdX1fsSxRVFXXlW3jVyxNFFVVdm1b+DVRVFXXtW3bFn5NFFVVdmXZtoWiqrqybduybgvDqKqua9uybeuorqvbuq3bui9UXVmWbVu3dR3XtnXd9nVd+Bmzbeu2buu+8CMMR9/4IeTj+3RCCAAAT3AAACqwYXWEk6KxwEJDVgIAGQAAgDFKGYUYM0gxphhjTDHGmAAAgAEHAIAAE8pAoSErAoAoAADAOeecc84555xzzjnnnHPOOeecc44xxhhjjDHGGGOMMcYYY4wxxhhjjDHGGGOMMcYYY0wAwE6EA8BOhIVQaMhKACAcAABACCEpKaWUUkoRU85BSSmllFKqFIOMSkoppZRSpBR1lFJKKaWUIqWgpJJSSimllElJKaWUUkoppYw6SimllFJKKaWUUkoppZRSSimllFJKKaWUUkoppZRSSimllFJKKaWUUkoppZRSSimllFJKKaWUUkoppZRSSimllFJKKaVUSimllFJKKaWUUkoppRQAYPLgAACVYOMMK0lnhaPBhYasBAByAwAAhRiDEEJpraRUUkolVc5BKCWUlEpKKZWUUqqYgxBKKqmlklJKKbXSQSihlFBKKSWUUkooJYQQSgmhlFRCK6mEUkoHoYQSQimhhFRKKSWUzkEoIYUOQkmllNRCSB10VFIpIZVSSiklpZQ6CKGUklJLLZVSWkqpdBJSKamV1FJqqbWSUgmhpFZKSSWl0lpJJbUSSkklpZRSSymFVFJJJYSSUioltZZaSqm11lJIqZWUUkqppdRSSiWlkEpKqZSSUmollZRSaiGVlEpJKaTUSimlpFRCSamlUlpKLbWUSkmptFRSSaWUlEpJKaVSSksppRJKSqmllFpJKYWSUkoplZJSSyW1VEoKJaWUUkmptJRSSymVklIBAEAHDgAAAUZUWoidZlx5BI4oZJiAAgAAQABAgAkgMEBQMApBgDACAQAAAADAAAAfAABHARAR0ZzBAUKCwgJDg8MDAAAAAAAAAAAAAACAT2dnUwAEAAAAAAAAAADqnjMlAgAAADzQPmcBAQA=");
            d && c("audio/mpeg;base64,/+MYxAAAAANIAUAAAASEEB/jwOFM/0MM/90b/+RhST//w4NFwOjf///PZu////9lns5GFDv//l9GlUIEEIAAAgIg8Ir/JGq3/+MYxDsLIj5QMYcoAP0dv9HIjUcH//yYSg+CIbkGP//8w0bLVjUP///3Z0x5QCAv/yLjwtGKTEFNRTMuOTeqqqqqqqqqqqqq/+MYxEkNmdJkUYc4AKqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq");
            var m = (new Date).getTime(),
            g = window.setInterval(function () {
                var d = 5E3 < (new Date).getTime() - m;
                if (!a || d)
                    window.clearInterval(g), e(b)
            }, 1)
        } else
            e(b)
    }
})();
"undefined" === typeof MIDI && (MIDI = {});
"undefined" === typeof MIDI.Soundfont && (MIDI.Soundfont = {});
(function () {
    MIDI.loadPlugin = function (d) {
        "function" === typeof d && (d = {
                callback: d
            });
        var c = d.instruments || d.instrument || "acoustic_grand_piano";
        "object" !== typeof c && (c = [c]);
        for (var e = 0; e < c.length; e++) {
            var f = c[e];
            "number" === typeof f && (c[e] = MIDI.GeneralMIDI.byId[f])
        }
        MIDI.soundfontUrl = d.soundfontUrl || MIDI.soundfontUrl || "./soundfont/";
        MIDI.audioDetect(function (e) {
            var f = "",
            f = a[d.api] ? d.api : a[window.location.hash.substr(1)] ? window.location.hash.substr(1) : window.webkitAudioContext || window.AudioContext ? "webaudio" :
                window.Audio ? "audiotag" : "flash";
            if (b[f]) {
                var r = d.targetFormat ? d.targetFormat : e["audio/ogg"] ? "ogg" : "mp3";
                MIDI.lang = f;
                MIDI.supports = e;
                b[f](r, c, d)
            }
        })
    };
    var b = {
        webmidi: function (a, d, c) {
            MIDI.loader && MIDI.loader.message("Web MIDI API...");
            MIDI.WebMIDI.connect(c)
        },
        flash: function (a, d, c) {
            MIDI.loader && MIDI.loader.message("Flash API...");
            DOMLoader.script.add({
                src: c.soundManagerUrl || "./inc/SoundManager2/script/soundmanager2.js",
                verify: "SoundManager",
                callback: function () {
                    MIDI.Flash.connect(d, c)
                }
            })
        },
        audiotag: function (a,
            b, g) {
            MIDI.loader && MIDI.loader.message("HTML5 Audio API...");
            var f = d({
                items: b,
                getNext: function (d) {
                    DOMLoader.sendRequest({
                        url: MIDI.soundfontUrl + d + "-" + a + ".js",
                        onprogress: e,
                        onload: function (a) {
                            c(a.responseText);
                            MIDI.loader && MIDI.loader.update(null, "Downloading", 100);
                            f.getNext()
                        }
                    })
                },
                onComplete: function () {
                    MIDI.AudioTag.connect(g)
                }
            })
        },
        webaudio: function (a, b, g) {
            MIDI.loader && MIDI.loader.message("Web Audio API...");
            var f = d({
                items: b,
                getNext: function (d) {
                    DOMLoader.sendRequest({
                        url: MIDI.soundfontUrl + d + "-" + a + ".js",
                        onprogress: e,
                        onload: function (a) {
                            c(a.responseText);
                            MIDI.loader && MIDI.loader.update(null, "Downloading...", 100);
                            f.getNext()
                        }
                    })
                },
                onComplete: function () {
                    MIDI.WebAudio.connect(g)
                }
            })
        }
    },
    a = {
        webmidi: !0,
        webaudio: !0,
        audiotag: !0,
        flash: !0
    },
    c = function (a) {
        var d = document.createElement("script");
        d.language = "javascript";
        d.type = "text/javascript";
        d.text = a;
        document.body.appendChild(d)
    },
    e = function (a) {
        this.totalSize || (this.getResponseHeader("Content-Length-Raw") ? this.totalSize = parseInt(this.getResponseHeader("Content-Length-Raw")) :
                this.totalSize = a.total);
        a = this.totalSize ? Math.round(100 * (a.loaded / this.totalSize)) : "";
        MIDI.loader && MIDI.loader.update(null, "Downloading...", a)
    },
    d = function (a) {
        var d = {
            queue: []
        },
        c;
        for (c in a.items)
            d.queue.push(a.items[c]);
        d.getNext = function () {
            if (!d.queue.length)
                return a.onComplete();
            a.getNext(d.queue.shift())
        };
        setTimeout(d.getNext, 1);
        return d
    }
})();
"undefined" === typeof MIDI && (MIDI = {});
"undefined" === typeof MIDI.Player && (MIDI.Player = {});
(function () {
    var b = MIDI.Player;
    b.callback = void 0;
    b.currentTime = 0;
    b.endTime = 0;
    b.restart = 0;
    b.playing = !1;
    b.timeWarp = 1;
    b.start = b.resume = function () {
        -1 > b.currentTime && (b.currentTime = -1);
        l(b.currentTime)
    };
    b.pause = function () {
        var a = b.restart;
        n();
        b.restart = a
    };
    b.stop = function () {
        n();
        b.restart = 0;
        b.currentTime = 0
    };
    b.addListener = function (a) {
        k = a
    };
    b.removeListener = function () {
        k = void 0
    };
    b.clearAnimation = function () {
        b.interval && window.clearInterval(b.interval)
    };
    b.setAnimation = function (a) {
        var c = "function" === typeof a ? a : a.callback;
        a = a.interval || 30;
        var e = 0,
        k = 0,
        f = 0;
        b.clearAnimation();
        b.interval = window.setInterval(function () {
            if (0 !== b.endTime) {
                b.playing ? (e = f === b.currentTime ? k - (new Date).getTime() : 0, e = 0 === b.currentTime ? 0 : b.currentTime - e, f !== b.currentTime && (k = (new Date).getTime(), f = b.currentTime)) : e = b.currentTime;
                var a = e / 1E3,
                l = a / 60,
                a = 60 * l + (a - 60 * l),
                l = b.endTime / 1E3;
                -1 > l - a || c({
                    now: a,
                    end: l,
                    events: d
                })
            }
        }, a)
    };
    b.loadMidiFile = function () {
        b.replayer = new Replayer(MidiFile(b.currentData), b.timeWarp);
        b.data = b.replayer.getData();
        b.endTime = f()
    };
    b.loadFile = function (a, d) {
        b.stop();
        if (-1 !== a.indexOf("base64,")) {
            var c = window.atob(a.split(",")[1]);
            b.currentData = c;
            b.loadMidiFile();
            d && d(c)
        } else
            c = new XMLHttpRequest, c.open("GET", a), c.overrideMimeType("text/plain; charset=x-user-defined"), c.onreadystatechange = function () {
                if (4 === this.readyState && 200 === this.status) {
                    for (var a = this.responseText || "", c = [], e = a.length, k = String.fromCharCode, f = 0; f < e; f++)
                        c[f] = k(a.charCodeAt(f) & 255);
                    a = c.join("");
                    b.currentData = a;
                    b.loadMidiFile();
                    d && d(a)
                }
            },
        c.send()
    };
    var a = [],
    c,
    e = 0,
    d = {},
    k = void 0,
    m = function (a, e, f, n, g, m) {
        return window.setTimeout(function () {
            var n = {
                channel: a,
                note: e,
                now: f,
                end: b.endTime,
                message: g,
                velocity: m
            };
            128 === g ? delete d[e] : d[e] = n;
            k && k(n);
            b.currentTime = f;
            b.currentTime === c && c < b.endTime && l(c, !0)
        }, f - n)
    },
    g = function () {
        if ("WebAudioAPI" === MIDI.lang)
            return MIDI.Player.ctx;
        b.ctx || (b.ctx = {
                currentTime: 0
            });
        return b.ctx
    },
    f = function () {
        for (var a = b.data, d = a.length, c = 0.5, e = 0; e < d; e++)
            c += a[e][1];
        return c
    },
    l = function (d, k) {
        if (b.replayer) {
            k || ("undefined" === typeof d && (d = b.restart),
                b.playing && n(), b.playing = !0, b.data = b.replayer.getData(), b.endTime = f());
            var l,
            s = 0,
            t = 0,
            v = b.data,
            w = g(),
            F = v.length;
            c = 0.5;
            e = w.currentTime;
            for (var B = 0; B < F; B++)
                if (l = v[B], l = l[1] || 1E-11, c + l <= d)
                    s = c += l;
                else
                    break;
            for (; B < F && 100 > t; B++) {
                l = v[B];
                c += l[1] || 1E-11;
                d = c - s;
                var x = l[0].event;
                if ("channel" === x.type) {
                    var u = x.channel;
                    switch (x.subtype) {
                    case "noteOn":
                        if (MIDI.channels[u].mute)
                            break;
                        l = x.noteNumber - (b.MIDIOffset || 0);
                        a.push({
                            event: x,
                            source: MIDI.noteOn(u, x.noteNumber, x.velocity, d / 1E3 + w.currentTime),
                            interval: m(u, l, c,
                                s, 144, x.velocity)
                        });
                        t++;
                        break;
                    case "noteOff":
                        if (MIDI.channels[u].mute)
                            break;
                        l = x.noteNumber - (b.MIDIOffset || 0);
                        a.push({
                            event: x,
                            source: MIDI.noteOff(u, x.noteNumber, d / 1E3 + w.currentTime),
                            interval: m(u, l, c, s, 128)
                        })
                    }
                }
            }
        }
    },
    n = function () {
        var c = g();
        b.playing = !1;
        for (b.restart += 1E3 * (c.currentTime - e); a.length; )
            c = a.pop(), window.clearInterval(c.interval), c.source && ("number" === typeof c.source ? window.clearTimeout(c.source) : c.source.disconnect(0));
        for (var f in d)
            c = d[f], 144 === d[f].message && k && k({
                channel: c.channel,
                note: c.note,
                now: c.now,
                end: c.end,
                message: 128,
                velocity: c.velocity
            });
        d = {}
    }
})();
"undefined" === typeof MIDI && (MIDI = {});
(function () {
    var b = function (a) {
        MIDI.api = a.api;
        MIDI.setVolume = a.setVolume;
        MIDI.programChange = a.programChange;
        MIDI.noteOn = a.noteOn;
        MIDI.noteOff = a.noteOff;
        MIDI.chordOn = a.chordOn;
        MIDI.chordOff = a.chordOff;
        MIDI.stopAllNotes = a.stopAllNotes;
        MIDI.getInput = a.getInput;
        MIDI.getOutputs = a.getOutputs
    };
    (function () {
        var a = null,
        c = null,
        e = MIDI.WebMIDI = {
            api: "webmidi"
        };
        e.setVolume = function (a, b) {
            c.send([176 + a, 7, b])
        };
        e.programChange = function (a, b) {
            c.send([192 + a, b])
        };
        e.noteOn = function (a, b, e, g) {
            c.send([144 + a, b, e], 1E3 * g)
        };
        e.noteOff =
        function (a, b, e) {
            c.send([128 + a, b, 0], 1E3 * e)
        };
        e.chordOn = function (a, b, e, g) {
            for (var f = 0; f < b.length; f++)
                c.send([144 + a, b[f], e], 1E3 * g)
        };
        e.chordOff = function (a, b, e) {
            for (var g = 0; g < b.length; g++)
                c.send([128 + a, b[g], 0], 1E3 * e)
        };
        e.stopAllNotes = function () {
            for (var a = 0; 16 > a; a++)
                c.send([176 + a, 123, 0])
        };
        e.getInput = function () {
            return a.getInputs()
        };
        e.getOutputs = function () {
            return a.getOutputs()
        };
        e.connect = function (d) {
            b(e);
            navigator.requestMIDIAccess().then(function (b) {
                a = b;
                c = a.outputs()[0];
                d.callback && d.callback()
            }, function (a) {
                d.api =
                    window.AudioContext || window.webkitAudioContext ? "webaudio" : window.Audio ? "audiotag" : "flash";
                MIDI.loadPlugin(d)
            })
        }
    })();
    (window.AudioContext || window.webkitAudioContext) && function () {
        var a = window.AudioContext || window.webkitAudioContext,
        c = MIDI.WebAudio = {
            api: "webaudio"
        },
        e,
        d = {},
        k = 127,
        m = {},
        g = function (a, d, c, b, k) {
            var g = MIDI.GeneralMIDI.byName[a],
            s = g.number,
            t = d[c];
            if (!MIDI.Soundfont[a][t])
                return k(a);
            var v = MIDI.Soundfont[a][t].split(",")[1],
            v = Base64Binary.decodeArrayBuffer(v);
            e.decodeAudioData(v, function (e) {
                for (var v =
                        t; 3 > v.length; )
                    v += "&nbsp;";
                "undefined" !== typeof MIDI.loader && MIDI.loader.update(null, g.instrument + "<br>Processing: " + (100 * (c / 87) >> 0) + "%<br>" + v);
                e.id = t;
                b[c] = e;
                if (b.length === d.length) {
                    for (; b.length; )
                        (e = b.pop()) && (m[s + "" + MIDI.keyToNote[e.id]] = e);
                    k(a)
                }
            })
        };
        c.setVolume = function (a, d) {
            k = d
        };
        c.programChange = function (a, d) {
            MIDI.channels[a].instrument = d
        };
        c.noteOn = function (a, c, b, g) {
            if (MIDI.channels[a]) {
                var q = MIDI.channels[a].instrument;
                if (m[q + "" + c]) {
                    g < e.currentTime && (g += e.currentTime);
                    var p = e.createBufferSource();
                    d[a + "" + c] = p;
                    p.buffer = m[q + "" + c];
                    p.connect(e.destination);
                    p.gainNode = e.createGain ? e.createGain() : e.createGainNode();
                    a = 2 * b / 127 * (k / 127) - 1;
                    p.gainNode.connect(e.destination);
                    p.gainNode.gain.value = Math.max(-1, a);
                    p.connect(p.gainNode);
                    p.noteOn ? p.noteOn(g || 0) : p.start(g || 0);
                    return p
                }
            }
        };
        c.noteOff = function (a, c, b) {
            b = b || 0;
            b < e.currentTime && (b += e.currentTime);
            var k = d[a + "" + c];
            if (k) {
                if (k.gainNode) {
                    var g = k.gainNode.gain;
                    g.linearRampToValueAtTime(g.value, b);
                    g.linearRampToValueAtTime(-1, b + 0.2)
                }
                k.noteOff ? k.noteOff(b + 0.3) :
                k.stop(b + 0.3);
                delete d[a + "" + c]
            }
        };
        c.chordOn = function (a, d, b, e) {
            for (var k = {}, g, m = 0, t = d.length; m < t; m++)
                k[g = d[m]] = c.noteOn(a, g, b, e);
            return k
        };
        c.chordOff = function (a, d, b) {
            for (var e = {}, k, g = 0, m = d.length; g < m; g++)
                e[k = d[g]] = c.noteOff(a, k, b);
            return e
        };
        c.stopAllNotes = function () {
            for (var a in d) {
                var c = 0;
                c < e.currentTime && (c += e.currentTime);
                d[a].gain.linearRampToValueAtTime(1, c);
                d[a].gain.linearRampToValueAtTime(0, c + 0.2);
                d[a].noteOff(c + 0.3);
                delete d[a]
            }
        };
        c.connect = function (d) {
            b(c);
            MIDI.Player.ctx = e = new a;
            var k = [],
            n = MIDI.keyToNote,
            r;
            for (r in n)
                k.push(r);
            var n = [],
            m = {};
            r = function (a) {
                delete m[a];
                for (var c in m)
                    break;
                c || d.callback()
            };
            for (var p in MIDI.Soundfont) {
                m[p] = !0;
                for (var s = 0; s < k.length; s++)
                    g(p, k, s, n, r)
            }
        }
    }
    ();
    window.Audio && function () {
        for (var a = MIDI.AudioTag = {
                api: "audiotag"
            }, c = {}, e = 127, d = -1, k = [], m = [], g = {}, f = 0; 12 > f; f++)
            k[f] = new Audio;
        var l = function (a, c) {
            if (MIDI.channels[a]) {
                var b = MIDI.GeneralMIDI.byId[MIDI.channels[a].instrument].id;
                if (c = g[c]) {
                    var f = (d + 1) % k.length,
                    l = k[f];
                    m[f] = b + "" + c.id;
                    l.src = MIDI.Soundfont[b][c.id];
                    l.volume = e / 127;
                    l.play();
                    d = f
                }
            }
        },
        n = function (a, c) {
            if (MIDI.channels[a]) {
                var b = MIDI.GeneralMIDI.byId[MIDI.channels[a].instrument].id;
                if (c = g[c])
                    for (var b = b + "" + c.id, e = 0; e < k.length; e++) {
                        var f = (e + d + 1) % k.length,
                        l = m[f];
                        if (l && l == b) {
                            k[f].pause();
                            m[f] = null;
                            break
                        }
                    }
            }
        };
        a.programChange = function (a, c) {
            MIDI.channels[a].instrument = c
        };
        a.setVolume = function (a, c) {
            e = c
        };
        a.noteOn = function (a, d, b, e) {
            var k = c[d];
            if (g[k]) {
                if (e)
                    return window.setTimeout(function () {
                        l(a, k)
                    }, 1E3 * e);
                l(a, k)
            }
        };
        a.noteOff = function (a, d, b) {
            var e = c[d];
            if (g[e]) {
                if (b)
                    return setTimeout(function () {
                        n(a,
                            e)
                    }, 1E3 * b);
                n(a, e)
            }
        };
        a.chordOn = function (a, d, b, e) {
            for (b = 0; b < d.length; b++) {
                var k = c[d[b]];
                if (g[k]) {
                    if (e)
                        return window.setTimeout(function () {
                            l(a, k)
                        }, 1E3 * e);
                    l(a, k)
                }
            }
        };
        a.chordOff = function (a, d, b) {
            for (var e = 0; e < d.length; e++) {
                var k = c[d[e]];
                if (g[k]) {
                    if (b)
                        return window.setTimeout(function () {
                            n(a, k)
                        }, 1E3 * b);
                    n(a, k)
                }
            }
        };
        a.stopAllNotes = function () {
            for (var a = 0, c = k.length; a < c; a++)
                k[a].pause()
        };
        a.connect = function (d) {
            for (var e in MIDI.keyToNote)
                c[MIDI.keyToNote[e]] = e, g[e] = {
                    id: e
                };
            b(a);
            d.callback && d.callback()
        }
    }
    ();
    (function () {
        var a =
            MIDI.Flash = {
            api: "flash"
        },
        c = {},
        e = {};
        a.programChange = function (a, c) {
            MIDI.channels[a].instrument = c
        };
        a.setVolume = function (a, c) {};
        a.noteOn = function (a, b, m, g) {
            if (MIDI.channels[a] && (b = MIDI.GeneralMIDI.byId[MIDI.channels[a].instrument].number + "" + c[b], e[b])) {
                if (g)
                    return window.setTimeout(function () {
                        e[b].play({
                            volume: 2 * m
                        })
                    }, 1E3 * g);
                e[b].play({
                    volume: 2 * m
                })
            }
        };
        a.noteOff = function (a, c, b) {};
        a.chordOn = function (a, b, m, g) {
            if (MIDI.channels[a]) {
                a = MIDI.GeneralMIDI.byId[MIDI.channels[a].instrument].number;
                for (var f in b)
                    g =
                        a + "" + c[b[f]], e[g] && e[g].play({
                        volume: 2 * m
                    })
            }
        };
        a.chordOff = function (a, c, b) {};
        a.stopAllNotes = function () {};
        a.connect = function (d, k) {
            soundManager.flashVersion = 9;
            soundManager.useHTML5Audio = !0;
            soundManager.url = k.soundManagerSwfUrl || "../inc/SoundManager2/swf/";
            soundManager.useHighPerformance = !0;
            soundManager.wmode = "transparent";
            soundManager.flashPollingInterval = 1;
            soundManager.debugMode = !1;
            soundManager.onload = function () {
                for (var g = function (a, c, d) {
                    e[MIDI.GeneralMIDI.byName[a].number + "" + c] = soundManager.createSound({
                        id: c,
                        url: MIDI.soundfontUrl + a + "-mp3/" + c + ".mp3",
                        multiShot: !0,
                        autoLoad: !0,
                        onload: d
                    })
                }, f = [], l = 88 * d.length, n = 0; n < d.length; n++)
                    for (var r = d[n], m = function () {
                        f.push(this.sID);
                        "undefined" !== typeof MIDI.loader && MIDI.loader.update(null, "Processing: " + this.sID)
                    }, p = 0; 88 > p; p++)
                        g(r, c[p + 21], m);
                b(a);
                var s = window.setInterval(function () {
                    f.length < l || (window.clearInterval(s), k.callback && k.callback())
                }, 25)
            };
            soundManager.onerror = function () {};
            for (var m in MIDI.keyToNote)
                c[MIDI.keyToNote[m]] = m
        }
    })();
    MIDI.GeneralMIDI = function (a) {
        var c =
        function (a) {
            return a.replace(/[^a-z0-9 ]/gi, "").replace(/[ ]/g, "_").toLowerCase()
        },
        b = {
            byName: {},
            byId: {},
            byCategory: {}
        },
        d;
        for (d in a)
            for (var k = a[d], m = 0, g = k.length; m < g; m++) {
                var f = k[m];
                if (f) {
                    var l = parseInt(f.substr(0, f.indexOf(" ")), 10),
                    f = f.replace(l + " ", "");
                    b.byId[--l] = b.byName[c(f)] = b.byCategory[c(d)] = {
                        id: c(f),
                        instrument: f,
                        number: l,
                        category: d
                    }
                }
            }
        return b
    }
    ({
        Piano: "1 Acoustic Grand Piano;2 Bright Acoustic Piano;3 Electric Grand Piano;4 Honky-tonk Piano;5 Electric Piano 1;6 Electric Piano 2;7 Harpsichord;8 Clavinet".split(";"),
        "Chromatic Percussion": "9 Celesta;10 Glockenspiel;11 Music Box;12 Vibraphone;13 Marimba;14 Xylophone;15 Tubular Bells;16 Dulcimer".split(";"),
        Organ: "17 Drawbar Organ;18 Percussive Organ;19 Rock Organ;20 Church Organ;21 Reed Organ;22 Accordion;23 Harmonica;24 Tango Accordion".split(";"),
        Guitar: "25 Acoustic Guitar (nylon);26 Acoustic Guitar (steel);27 Electric Guitar (jazz);28 Electric Guitar (clean);29 Electric Guitar (muted);30 Overdriven Guitar;31 Distortion Guitar;32 Guitar Harmonics".split(";"),
        Bass: "33 Acoustic Bass;34 Electric Bass (finger);35 Electric Bass (pick);36 Fretless Bass;37 Slap Bass 1;38 Slap Bass 2;39 Synth Bass 1;40 Synth Bass 2".split(";"),
        Strings: "41 Violin;42 Viola;43 Cello;44 Contrabass;45 Tremolo Strings;46 Pizzicato Strings;47 Orchestral Harp;48 Timpani".split(";"),
        Ensemble: "49 String Ensemble 1;50 String Ensemble 2;51 Synth Strings 1;52 Synth Strings 2;53 Choir Aahs;54 Voice Oohs;55 Synth Choir;56 Orchestra Hit".split(";"),
        Brass: "57 Trumpet;58 Trombone;59 Tuba;60 Muted Trumpet;61 French Horn;62 Brass Section;63 Synth Brass 1;64 Synth Brass 2".split(";"),
        Reed: "65 Soprano Sax;66 Alto Sax;67 Tenor Sax;68 Baritone Sax;69 Oboe;70 English Horn;71 Bassoon;72 Clarinet".split(";"),
        Pipe: "73 Piccolo;74 Flute;75 Recorder;76 Pan Flute;77 Blown Bottle;78 Shakuhachi;79 Whistle;80 Ocarina".split(";"),
        "Synth Lead": "81 Lead 1 (square);82 Lead 2 (sawtooth);83 Lead 3 (calliope);84 Lead 4 (chiff);85 Lead 5 (charang);86 Lead 6 (voice);87 Lead 7 (fifths);88 Lead 8 (bass + lead)".split(";"),
        "Synth Pad": "89 Pad 1 (new age);90 Pad 2 (warm);91 Pad 3 (polysynth);92 Pad 4 (choir);93 Pad 5 (bowed);94 Pad 6 (metallic);95 Pad 7 (halo);96 Pad 8 (sweep)".split(";"),
        "Synth Effects": "97 FX 1 (rain);98 FX 2 (soundtrack);99 FX 3 (crystal);100 FX 4 (atmosphere);101 FX 5 (brightness);102 FX 6 (goblins);103 FX 7 (echoes);104 FX 8 (sci-fi)".split(";"),
        Ethnic: "105 Sitar;106 Banjo;107 Shamisen;108 Koto;109 Kalimba;110 Bagpipe;111 Fiddle;112 Shanai".split(";"),
        Percussive: "113 Tinkle Bell;114 Agogo;115 Steel Drums;116 Woodblock;117 Taiko Drum;118 Melodic Tom;119 Synth Drum".split(";"),
        "Sound effects": "120 Reverse Cymbal;121 Guitar Fret Noise;122 Breath Noise;123 Seashore;124 Bird Tweet;125 Telephone Ring;126 Helicopter;127 Applause;128 Gunshot".split(";")
    });
    MIDI.channels = function () {
        for (var a = {}, c = 0; 16 > c; c++)
            a[c] = {
                instrument: 0,
                mute: !1,
                mono: !1,
                omni: !1,
                solo: !1
            };
        return a
    }
    ();
    MIDI.pianoKeyOffset = 21;
    MIDI.keyToNote = {};
    MIDI.noteToKey = {};
    (function () {
        for (var a = "C Db D Eb E F Gb G Ab A Bb B".split(" "), c = 21; 108 >= c; c++) {
            var b = a[c % 12] + ((c - 12) / 12 >> 0);
            MIDI.keyToNote[b] = c;
            MIDI.noteToKey[c] = b
        }
    })()
})();
var invertObject = function (b) {
    if (b.length)
        for (var a = {}, c = 0; c < b.length; c++)
            a[b[c]] = c;
    else
        for (c in a = {}, b)
            a[b[c]] = c;
    return a
};
"undefined" === typeof MusicTheory && (MusicTheory = {});
(function () {
    var b = MusicTheory;
    b.key2number = {
        A: 0,
        "A#": 1,
        Bb: 1,
        B: 2,
        C: 3,
        "C#": 4,
        Db: 4,
        D: 5,
        "D#": 6,
        Eb: 6,
        E: 7,
        F: 8,
        "F#": 9,
        Gb: 9,
        G: 10,
        "G#": 11,
        Ab: 11
    };
    b.number2float = {
        0: 0,
        1: 0.5,
        2: 1,
        3: 2,
        4: 2.5,
        5: 3,
        6: 3.5,
        7: 4,
        8: 5,
        9: 5.5,
        10: 6,
        11: 6.5,
        12: 7
    };
    b.number2key = invertObject(b.key2number);
    b.float2number = invertObject(b.number2float);
    b.getKeySignature = function (a) {
        var c = "A AB B C CD D DE E F FG G GA".split(" "),
        b = "FCGDAEB".split("");
        a = {
            Fb: -8,
            Cb: -7,
            Gb: -6,
            Db: -5,
            Ab: -4,
            Eb: -3,
            Bb: -2,
            F: -1,
            C: 0,
            G: 1,
            D: 2,
            A: 3,
            E: 4,
            B: 5,
            "F#": 6,
            "C#": 7,
            "G#": 8,
            "D#": 9,
            "A#": 10,
            "E#": 11,
            "B#": 12
        }
        [a];
        for (var b = 0 > a ? b.splice(7 + a, -a).reverse().join("") : b.splice(0, a).join(""), d = 0; d < c.length; d++)
            1 < c[d].length && (-1 != b.indexOf(c[d][0]) || -1 != b.indexOf(c[d][1]) ? c[d] = 0 < a ? c[d][0] + "#" : c[d][1] + "b" : c[d] = c[d][0] + "#");
        Piano.keySignature = c
    };
    b.tempoFromTap = function (a) {
        function c(a) {
            for (var c = {
                    200: "Prestissimo",
                    168: "Presto",
                    140: "Vivace",
                    120: "Allegro",
                    112: "Allegretto",
                    101: "Moderato",
                    76: "Andante",
                    66: "Adagio",
                    60: "Larghetto",
                    40: "Lento",
                    0: "Larghissimo"
                }, b = 0, d = ""; 250 > b; b++)
                if (c[b] && (d = c[b]),
                    a < b)
                    return d;
            return "Prestissimo"
        }
        if (a.tap) {
            var b = (new Date).getTime() - a.tap,
            d = 60 * (1 / (b / 1E3));
            Piano.tempo = d;
            console.log(c(d), d, b);
            document.getElementById("taptap").value = (d >> 0) + "bmp " + c(d)
        }
        a.tap = (new Date).getTime()
    };
    b.findChord = function (a) {
        a = {};
        var c = ["0", "3"],
        b = Piano.chords,
        d = {},
        k;
        for (k in b) {
            var m = {},
            g;
            for (g in b[k])
                m[b[k][g]] = 1;
            d[k] = m
        }
        for (var f in d)
            for (k = 0, g = c.length; k < g; k++)
                if (isNaN(d[f][c[k]])) {
                    a[f] = 1;
                    break
                }
        c = [];
        for (f in d)
            a[f] || c.push(f);
        return document.getElementById("find").value = c
    };
    b.scaleInfo =
    function (a) {
        var b = "r b2 2 b3 3 4 b5 5 &#X266F;5 6 b7 7 8 b9 9 &#X266F;9 10 11 b12 12 &#X266F;12 13".split(" "),
        e = "",
        d = "",
        k = "",
        m = "",
        g = "",
        f;
        for (f in a) {
            0 < a[f] && (k += "-" + (a[f] - l));
            var l = a[f],
            n = Piano.calculateNote(l) % 12,
            n = Piano.keySignature[n],
            m = m + (", " + MusicTheory.Solfege[n].syllable),
            g = g + (", " + l),
            e = e + (", " + n),
            d = d + (", " + b[l])
        }
        console.log("<b>notes:</b> " + e.substr(2) + "<br><b>solfege:</b> " + m.substr(2) + "<br><b>intervals:</b> " + d.substr(2) + "<br><b>keys:</b> " + g.substr(2) + "<br><b>gaps:</b> " + k.substr(1))
    }
})();
"undefined" === typeof MusicTheory && (MusicTheory = {});
MusicTheory.Chords = {
    Major: [0, 4, 7],
    Majb5: [0, 4, 6],
    minor: [0, 3, 7],
    minb5: [0, 3, 6],
    sus2: [0, 2, 7],
    sus4: [0, 5, 7],
    aug: [0, 4, 8],
    augsus4: [0, 5, 8],
    tri: [0, 3, 6, 9],
    "6th": null,
    "6 ": [0, 4, 7, 9],
    "6sus4": [0, 5, 7, 9],
    "6add9": [0, 4, 7, 9, 14],
    m6: [0, 3, 7, 9],
    m6add9: [0, 3, 7, 9, 14],
    "7th": null,
    "7 ": [0, 4, 7, 10],
    "7sus4": [0, 5, 7, 10],
    "7#5": [0, 4, 8, 10],
    "7b5": [0, 4, 6, 10],
    "7#9": [0, 4, 7, 10, 15],
    "7b9": [0, 4, 7, 10, 13],
    "7#5#9": [0, 4, 8, 12, 14, 19],
    "7#5b9": [0, 4, 8, 12, 14, 17],
    "7b5b9": [0, 4, 6, 10, 12, 15],
    "7add11": [0, 4, 7, 10, 17],
    "7add13": [0, 4, 7, 10, 21],
    "7#11": [0, 4, 7, 10, 18],
    Maj7: [0, 4, 7, 11],
    Maj7b5: [0, 4, 6, 11],
    "Maj7#5": [0, 4, 8, 11],
    "Maj7#11": [0, 4, 7, 11, 18],
    Maj7add13: [0, 4, 7, 11, 21],
    m7: [0, 3, 7, 10],
    m7b5: [0, 3, 6, 10],
    m7b9: [0, 3, 7, 10, 13],
    m7add11: [0, 3, 7, 10, 17],
    m7add13: [0, 3, 7, 10, 21],
    "m-Maj7": [0, 3, 7, 11],
    "m-Maj7add11": [0, 3, 7, 11, 17],
    "m-Maj7add13": [0, 3, 7, 11, 21],
    "9th": null,
    "9 ": [0, 4, 7, 10, 14],
    "9sus4": [0, 5, 7, 10, 14],
    add9: [0, 4, 7, 14],
    "9#5": [0, 4, 8, 10, 14],
    "9b5": [0, 4, 6, 10, 14],
    "9#11": [0, 4, 7, 10, 14, 18],
    "9b13": [0, 4, 7, 10, 14, 20],
    Maj9: [0, 4, 7, 11, 14],
    Maj9sus4: [0, 5, 7, 11, 15],
    "Maj9#5": [0, 4, 8, 11, 14],
    "Maj9#11": [0,
        4, 7, 11, 14, 18],
    m9: [0, 3, 7, 10, 14],
    madd9: [0, 3, 7, 14],
    m9b5: [0, 3, 6, 10, 14],
    "m9-Maj7": [0, 3, 7, 11, 14],
    "11th": null,
    "11 ": [0, 4, 7, 10, 14, 17],
    "11b9": [0, 4, 7, 10, 13, 17],
    Maj11: [0, 4, 7, 11, 14, 17],
    m11: [0, 3, 7, 10, 14, 17],
    "m-Maj11": [0, 3, 7, 11, 14, 17],
    "13th": null,
    "13 ": [0, 4, 7, 10, 14, 21],
    "13#9": [0, 4, 7, 10, 15, 21],
    "13b9": [0, 4, 7, 10, 13, 21],
    "13b5b9": [0, 4, 6, 10, 13, 21],
    Maj13: [0, 4, 7, 11, 14, 21],
    m13: [0, 3, 7, 10, 14, 21],
    "m-Maj13": [0, 3, 7, 11, 14, 21]
};
if ("undefined" === typeof MusicTheory)
    var MusicTheory = {};
"undefined" === typeof MusicTheory.Synesthesia && (MusicTheory.Synesthesia = {});
(function (b) {
    b.data = {
        "Isaac Newton (1704)": {
            format: "HSL",
            ref: "Gerstner, p.167",
            english: ["red", null, "orange", null, "yellow", "green", null, "blue", null, "indigo", null, "violet"],
            0: [0, 96, 51],
            1: [0, 0, 0],
            2: [29, 94, 52],
            3: [0, 0, 0],
            4: [60, 90, 60],
            5: [135, 76, 32],
            6: [0, 0, 0],
            7: [248, 82, 28],
            8: [0, 0, 0],
            9: [302, 88, 26],
            10: [0, 0, 0],
            11: [325, 84, 46]
        },
        "Louis Bertrand Castel (1734)": {
            format: "HSL",
            ref: "Peacock, p.400",
            english: "blue;blue-green;green;olive green;yellow;yellow-orange;orange;red;crimson;violet;agate;indigo".split(";"),
            0: [248,
                82, 28],
            1: [172, 68, 34],
            2: [135, 76, 32],
            3: [79, 59, 36],
            4: [60, 90, 60],
            5: [49, 90, 60],
            6: [29, 94, 52],
            7: [360, 96, 51],
            8: [1, 89, 33],
            9: [325, 84, 46],
            10: [273, 80, 27],
            11: [302, 88, 26]
        },
        "George Field (1816)": {
            format: "HSL",
            ref: "Klein, p.69",
            english: ["blue", null, "purple", null, "red", "orange", null, "yellow", null, "yellow green", null, "green"],
            0: [248, 82, 28],
            1: [0, 0, 0],
            2: [302, 88, 26],
            3: [0, 0, 0],
            4: [360, 96, 51],
            5: [29, 94, 52],
            6: [0, 0, 0],
            7: [60, 90, 60],
            8: [0, 0, 0],
            9: [79, 59, 36],
            10: [0, 0, 0],
            11: [135, 76, 32]
        },
        "D. D. Jameson (1844)": {
            format: "HSL",
            ref: "Jameson, p.12",
            english: "red red-orange orange orange-yellow yellow green green-blue blue blue-purple purple purple-violet violet".split(" "),
            0: [360, 96, 51],
            1: [14, 91, 51],
            2: [29, 94, 52],
            3: [49, 90, 60],
            4: [60, 90, 60],
            5: [135, 76, 32],
            6: [172, 68, 34],
            7: [248, 82, 28],
            8: [273, 80, 27],
            9: [302, 88, 26],
            10: [313, 78, 37],
            11: [325, 84, 46]
        },
        "Theodor Seemann (1881)": {
            format: "HSL",
            ref: "Klein, p.86",
            english: "carmine;scarlet;orange;yellow-orange;yellow;green;green blue;blue;indigo;violet;brown;black".split(";"),
            0: [0, 58, 26],
            1: [360, 96, 51],
            2: [29, 94, 52],
            3: [49, 90, 60],
            4: [60, 90, 60],
            5: [135, 76, 32],
            6: [172, 68, 34],
            7: [248, 82, 28],
            8: [302, 88, 26],
            9: [325, 84, 46],
            10: [0, 58, 26],
            11: [0, 0, 3]
        },
        "A. Wallace Rimington (1893)": {
            format: "HSL",
            ref: "Peacock, p.402",
            english: "deep red;crimson;orange-crimson;orange;yellow;yellow-green;green;blueish green;blue-green;indigo;deep blue;violet".split(";"),
            0: [360, 96, 51],
            1: [1, 89, 33],
            2: [14, 91, 51],
            3: [29, 94, 52],
            4: [60, 90, 60],
            5: [79, 59, 36],
            6: [135, 76, 32],
            7: [163, 62, 40],
            8: [172, 68, 34],
            9: [302, 88, 26],
            10: [248, 82, 28],
            11: [325, 84, 46]
        },
        "Bainbridge Bishop (1893)": {
            format: "HSL",
            ref: "Bishop, p.11",
            english: "red;orange-red or scarlet;orange;gold or yellow-orange;yellow or green-gold;yellow-green;green;greenish-blue or aquamarine;blue;indigo or violet-blue;violet;violet-red;red".split(";"),
            0: [360, 96, 51],
            1: [1, 89, 33],
            2: [29, 94, 52],
            3: [50, 93, 52],
            4: [60, 90, 60],
            5: [73, 73, 55],
            6: [135, 76, 32],
            7: [163, 62, 40],
            8: [302, 88, 26],
            9: [325, 84, 46],
            10: [343, 79, 47],
            11: [360, 96, 51]
        },
        "H. von Helmholtz (1910)": {
            format: "HSL",
            ref: "Helmholtz, p.22",
            english: "yellow;green;greenish blue;cayan-blue;indigo blue;violet;end of red;red;red;red;red orange;orange".split(";"),
            0: [60, 90, 60],
            1: [135, 76, 32],
            2: [172, 68, 34],
            3: [211, 70, 37],
            4: [302, 88, 26],
            5: [325, 84, 46],
            6: [330, 84, 34],
            7: [360, 96, 51],
            8: [10, 91, 43],
            9: [10, 91, 43],
            10: [8, 93, 51],
            11: [28, 89, 50]
        },
        "Alexander Scriabin (1911)": {
            format: "HSL",
            ref: "Jones, p.104",
            english: "red;violet;yellow;steely with the glint of metal;pearly blue the shimmer of moonshine;dark red;bright blue;rosy orange;purple;green;steely with a glint of metal;pearly blue the shimmer of moonshine".split(";"),
            0: [360, 96, 51],
            1: [325, 84, 46],
            2: [60, 90, 60],
            3: [245, 21, 43],
            4: [211,
                70, 37],
            5: [1, 89, 33],
            6: [248, 82, 28],
            7: [29, 94, 52],
            8: [302, 88, 26],
            9: [135, 76, 32],
            10: [245, 21, 43],
            11: [211, 70, 37]
        },
        "Adrian Bernard Klein (1930)": {
            format: "HSL",
            ref: "Klein, p.209",
            english: "dark red;red;red orange;orange;yellow;yellow green;green;blue-green;blue;blue violet;violet;dark violet".split(";"),
            0: [0, 91, 40],
            1: [360, 96, 51],
            2: [14, 91, 51],
            3: [29, 94, 52],
            4: [60, 90, 60],
            5: [73, 73, 55],
            6: [135, 76, 32],
            7: [172, 68, 34],
            8: [248, 82, 28],
            9: [292, 70, 31],
            10: [325, 84, 46],
            11: [330, 84, 34]
        },
        "August Aeppli (1940)": {
            format: "HSL",
            ref: "Gerstner, p.169",
            english: ["red", null, "orange", null, "yellow", null, "green", "blue-green", null, "ultramarine blue", "violet", "purple"],
            0: [0, 96, 51],
            1: [0, 0, 0],
            2: [29, 94, 52],
            3: [0, 0, 0],
            4: [60, 90, 60],
            5: [0, 0, 0],
            6: [135, 76, 32],
            7: [172, 68, 34],
            8: [0, 0, 0],
            9: [211, 70, 37],
            10: [273, 80, 27],
            11: [302, 88, 26]
        },
        "I. J. Belmont (1944)": {
            ref: "Belmont, p.226",
            english: "red red-orange orange yellow-orange yellow yellow-green green blue-green blue blue-violet violet red-violet".split(" "),
            0: [360, 96, 51],
            1: [14, 91, 51],
            2: [29, 94, 52],
            3: [50, 93, 52],
            4: [60, 90, 60],
            5: [73, 73, 55],
            6: [135, 76, 32],
            7: [172, 68, 34],
            8: [248, 82, 28],
            9: [313, 78, 37],
            10: [325, 84, 46],
            11: [338, 85, 37]
        },
        "Steve Zieverink (2004)": {
            format: "HSL",
            ref: "Cincinnati Contemporary Art Center",
            english: "yellow-green;green;blue-green;blue;indigo;violet;ultra violet;infra red;red;orange;yellow-white;yellow".split(";"),
            0: [73, 73, 55],
            1: [135, 76, 32],
            2: [172, 68, 34],
            3: [248, 82, 28],
            4: [302, 88, 26],
            5: [325, 84, 46],
            6: [326, 79, 24],
            7: [1, 89, 33],
            8: [360, 96, 51],
            9: [29, 94, 52],
            10: [62, 78, 74],
            11: [60, 90, 60]
        },
        "Circle of Fifths (Johnston 2003)": {
            format: "RGB",
            ref: "Joseph Johnston",
            english: "yellow;blue;orange;teal;red;green;purple;light orange;light blue;dark orange;dark green;violet".split(";"),
            0: [255, 255, 0],
            1: [50, 0, 255],
            2: [255, 150, 0],
            3: [0, 210, 180],
            4: [255, 0, 0],
            5: [130, 255, 0],
            6: [150, 0, 200],
            7: [255, 195, 0],
            8: [30, 130, 255],
            9: [255, 100, 0],
            10: [0, 200, 0],
            11: [225, 0, 225]
        },
        "Circle of Fifths (Wheatman 2002)": {
            format: "HEX",
            ref: "Stuart Wheatman",
            english: [],
            data: "#122400 #2E002E #002914 #470000 #002142 #2E2E00 #290052 #003D00 #520029 #003D3D #522900 #000080 #244700 #570057 #004D26 #7A0000 #003B75 #4C4D00 #47008F #006100 #850042 #005C5C #804000 #0000C7 #366B00 #80007F #00753B #B80000 #0057AD #6B6B00 #6600CC #008A00 #B8005C #007F80 #B35900 #2424FF #478F00 #AD00AD #00994D #F00000 #0073E6 #8F8F00 #8A14FF #00AD00 #EB0075 #00A3A3 #E07000 #6B6BFF #5CB800 #DB00DB #00C261 #FF5757 #3399FF #ADAD00 #B56BFF #00D600 #FF57AB #00C7C7 #FF9124 #9999FF #6EDB00 #FF29FF #00E070 #FF9999 #7ABDFF #D1D100 #D1A3FF #00FA00 #FFA3D1 #00E5E6 #FFC285 #C2C2FF #80FF00 #FFA8FF #00E070 #FFCCCC #C2E0FF #F0F000 #EBD6FF #ADFFAD #FFD6EB #8AFFFF #FFEBD6 #EBEBFF #E0FFC2 #FFEBFF #E5FFF2 #FFF5F5".split(" ")
        }
    };
    b.map = function (a) {
        var c = {},
        e = b.data;
        a = e[a] || e["D. D. Jameson (1844)"];
        for (e = 0; 88 >= e; e++)
            if (a.data)
                c[e] = {
                    hsl: a.data[e],
                    hex: a.data[e]
                };
            else {
                var d = a[(e + 9) % 12],
                k = "RGB" === a.format;
                k && (d = Color.Space(d, "RGB>HSL"));
                var m = Math.round(k ? d.H : d[0]),
                g = Math.round(k ? d.S : d[1]),
                k = Math.round(k ? d.L : d[2]);
                m == g && g == k && (d = [0.5 * f[0] + 0.5 * a[(e + 10) % 12][0] + 0.5 >> 0, 0.5 * f[1] + 0.5 * a[(e + 10) % 12][1] + 0.5 >> 0, 0.5 * f[2] + 0.5 * a[(e + 10) % 12][2] + 0.5 >> 0]);
                c[e] = {
                    hsl: "hsla(" + m + "," + g + "%," + k + "%, 1)",
                    hex: Color.Space({
                        H: m,
                        S: g,
                        L: k
                    }, "HSL>RGB>HEX>W3")
                };
                var f = d
            }
        return c
    }
})(MusicTheory.Synesthesia);
"undefined" === typeof MusicTheory && (MusicTheory = {});
MusicTheory.Scales = {
    Aeolian: [0, 2, 3, 5, 7, 8, 10],
    Altered: [0, 1, 3, 4, 6, 8, 10],
    "Altered b7": [0, 1, 3, 4, 6, 8, 9],
    Arabian: [0, 2, 4, 5, 6, 8, 10],
    Augmented: [0, 3, 4, 7, 8, 11],
    Balinese: [0, 1, 3, 7, 8],
    Blues: [0, 3, 5, 6, 7, 10],
    Byzantine: [0, 1, 4, 5, 7, 8, 11],
    Chinese: [0, 4, 6, 7, 11],
    "Chinese Mongolian": [0, 2, 4, 7, 9],
    Chromatic: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    "Diminished (H-W)": [0, 1, 3, 4, 6, 7, 9, 10],
    "Diminished (W-H)": [0, 2, 3, 5, 6, 8, 9, 11],
    Dorian: [0, 2, 3, 5, 7, 9, 10],
    "Dorian b2": [0, 1, 3, 5, 7, 9, 10],
    "Dorian #4": [0, 2, 3, 6, 7, 9, 10],
    "Double Harmonic": [0, 1, 4, 5, 7, 8, 11],
    Enigmatic: [0, 1, 4, 6, 8, 10, 11],
    Egyptian: [0, 2, 5, 7, 10],
    "Eight Tone Spanish": [0, 1, 4, 5, 6, 8, 10],
    "Harmonic Minor": [0, 2, 3, 5, 7, 8, 11],
    Hindu: [0, 2, 4, 5, 7, 8, 10],
    "Hirajoshi (Japanese)": [0, 2, 3, 7, 8],
    "Hungarian Major": [0, 3, 4, 6, 7, 9, 10],
    "Hungarian Minor": [0, 2, 3, 6, 7, 8, 11],
    Ichikosucho: [0, 2, 4, 5, 6, 7, 9, 11],
    Ionian: [0, 2, 4, 5, 7, 9, 11],
    "Ionian Aug": [0, 2, 4, 5, 8, 9, 11],
    "Iwato (Japanese)": [0, 1, 5, 6, 10],
    Kumoi: [0, 2, 3, 7, 9],
    "Leading Whole Tone": [0, 2, 4, 6, 8, 10, 11],
    Locrian: [0, 1, 3, 5, 6, 8, 10],
    "Locrian 2": [0, 2, 3, 5, 6, 8, 10],
    "Locrian 6": [0, 1, 3, 5, 6,
        9, 10],
    Lydian: [0, 2, 4, 6, 7, 9, 11],
    "Lydian Aug": [0, 2, 4, 6, 8, 9, 11],
    "Lydian b7": [0, 2, 4, 6, 7, 9, 10],
    "Lydian #9": [0, 3, 4, 6, 7, 9, 11],
    "Lydian Diminished": [0, 2, 3, 6, 7, 9, 11],
    "Lydian Minor": [0, 2, 4, 6, 7, 8, 10],
    "Marva (Indian)": [0, 1, 4, 6, 7, 9, 11],
    "Melodic Minor": [0, 2, 3, 5, 7, 9, 11],
    Mixolydian: [0, 2, 4, 5, 7, 9, 10],
    "Mixolydian b6": [0, 2, 4, 5, 7, 8, 10],
    Mohammedan: [0, 2, 3, 5, 7, 8, 11],
    "Neopolitan Major": [0, 1, 3, 5, 7, 9, 11],
    "Neopolitan Minor": [0, 1, 3, 5, 7, 8, 10],
    Oriental: [0, 1, 4, 5, 6, 9, 10],
    Overtone: [0, 2, 4, 6, 7, 9, 10],
    "Pelog (Balinese)": [0, 1, 3, 7, 10],
    "Pentatonic Major": [0,
        2, 4, 7, 9],
    "Pentatonic Minor": [0, 3, 5, 7, 10],
    Persian: [0, 1, 4, 5, 6, 8, 11],
    Phrygian: [0, 1, 3, 5, 7, 8, 10],
    Prometheus: [0, 2, 4, 6, 9, 10],
    "Prometheus Neopolitan": [0, 1, 4, 6, 9, 10],
    "Purvi Theta": [0, 1, 4, 6, 7, 8, 11],
    Romanian: [0, 2, 3, 6, 7, 9, 10],
    "Six Tone Symmetrical": [0, 1, 4, 5, 8, 9],
    "Todi (Indian)": [0, 1, 3, 6, 7, 8, 11],
    "Whole Tone": [0, 2, 4, 6, 8, 10]
};
MusicTheory.Solfege = {
    C: {
        poppins: "Doe \u2014 a deer, a female deer.",
        syllable: "Do",
        anglicized: "/do\u028a/"
    },
    "C#": {
        syllable: "Di",
        anglicized: "/di\u02d0/"
    },
    Db: {
        syllable: "Ra",
        anglicized: "/r\u0251\u02d0/"
    },
    D: {
        poppins: "Ray \u2014 a drop of golden sun.",
        syllable: "Re",
        anglicized: "/re\u026a/"
    },
    "D#": {
        syllable: "Ri",
        anglicized: "/ri\u02d0/"
    },
    Eb: {
        syllable: "Me",
        anglicized: "/me\u026a/"
    },
    E: {
        poppins: "Me \u2014 a name I call myself.",
        syllable: "Mi",
        anglicized: "/mi\u02d0/"
    },
    F: {
        poppins: "Far \u2014 a long long way to run.",
        syllable: "Fa",
        anglicized: "/f\u0251\u02d0/"
    },
    "F#": {
        syllable: "Fi",
        anglicized: "/fi\u02d0/"
    },
    Gb: {
        syllable: "Se",
        anglicized: "/se\u026a/"
    },
    G: {
        poppins: "Sew \u2014 a needle pulling thread.",
        syllable: "So",
        anglicized: "/so\u028a/"
    },
    "G#": {
        syllable: "Si",
        anglicized: "/si\u02d0/"
    },
    Ab: {
        syllable: "Le",
        anglicized: "/le\u026a/"
    },
    A: {
        poppins: "La \u2014 a note to follow so.",
        syllable: "La",
        anglicized: "/l\u0251\u02d0/"
    },
    "A#": {
        syllable: "Li",
        anglicized: "/li\u02d0/"
    },
    Bb: {
        syllable: "Te",
        anglicized: "/te\u026a/"
    },
    B: {
        poppins: "Tea \u2014 a drink with jam and bread.",
        syllable: "Ti",
        anglicized: "/ti\u02d0/"
    }
};
(function (b) {
    b.btoa || (b.btoa = function (a) {
        a = escape(a);
        var b = "",
        e,
        d,
        k = "",
        m,
        g,
        f = "",
        l = 0;
        do
            e = a.charCodeAt(l++), d = a.charCodeAt(l++), k = a.charCodeAt(l++), m = e >> 2, e = (e & 3) << 4 | d >> 4, g = (d & 15) << 2 | k >> 6, f = k & 63, isNaN(d) ? g = f = 64 : isNaN(k) && (f = 64), b = b + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".charAt(m) + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".charAt(e) + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".charAt(g) + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".charAt(f);
        while (l < a.length);
        return b
    });
    b.atob || (b.atob = function (a) {
        var b = "",
        e,
        d,
        k = "",
        m,
        g = "",
        f = 0;
        /[^A-Za-z0-9\+\/\=]/g.exec(a) && alert("There were invalid base64 characters in the input text.\nValid base64 characters are A-Z, a-z, 0-9, '+', '/',and '='\nExpect errors in decoding.");
        a = a.replace(/[^A-Za-z0-9\+\/\=]/g, "");
        do
            e = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".indexOf(a.charAt(f++)), d = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".indexOf(a.charAt(f++)), m = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".indexOf(a.charAt(f++)),
            g = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".indexOf(a.charAt(f++)), e = e << 2 | d >> 4, d = (d & 15) << 4 | m >> 2, k = (m & 3) << 6 | g, b += String.fromCharCode(e), 64 != m && (b += String.fromCharCode(d)), 64 != g && (b += String.fromCharCode(k));
        while (f < a.length);
        return unescape(b)
    })
})(this);
if ("undefined" === typeof DOM)
    var DOM = {};
(function () {
    DOM.dimensions = function () {
        document.body && (document.body.scrollHeight || (document.body.scrollHeight = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)), window.innerWidth && window.innerHeight || (document.body && document.body.offsetWidth ? (window.innerWidth = document.body.offsetWidth, window.innerHeight = document.body.offsetHeight) : "CSS1Compat" === document.compatMode && (document.documentElement && document.documentElement.offsetWidth) && (window.innerWidth = document.documentElement.offsetWidth,
                    window.innerHeight = document.documentElement.offsetHeight)))
    }
})();
if ("undefined" === typeof JSON)
    var JSON = {};
(function () {
    function b(a) {
        return 10 > a ? "0" + a : a
    }
    function a(a) {
        d.lastIndex = 0;
        return d.test(a) ? '"' + a.replace(d, function (a) {
            var b = g[a];
            return "string" === typeof b ? b : "\\u" + ("0000" + a.charCodeAt(0).toString(16)).slice(-4)
        }) + '"' : '"' + a + '"'
    }
    function c(b, d) {
        var e,
        g,
        p,
        s,
        t = k,
        v,
        w = d[b];
        w && ("object" === typeof w && "function" === typeof w.toJSON) && (w = w.toJSON(b));
        "function" === typeof f && (w = f.call(d, b, w));
        switch (typeof w) {
        case "string":
            return a(w);
        case "number":
            return isFinite(w) ? String(w) : "null";
        case "boolean":
        case "null":
            return String(w);
        case "object":
            if (!w)
                return "null";
            k += m;
            v = [];
            if ("[object Array]" === Object.prototype.toString.apply(w)) {
                s = w.length;
                for (e = 0; e < s; e += 1)
                    v[e] = c(e, w) || "null";
                p = 0 === v.length ? "[]" : k ? "[\n" + k + v.join(",\n" + k) + "\n" + t + "]" : "[" + v.join(",") + "]";
                k = t;
                return p
            }
            if (f && "object" === typeof f)
                for (s = f.length, e = 0; e < s; e += 1)
                    "string" === typeof f[e] && (g = f[e], (p = c(g, w)) && v.push(a(g) + (k ? ": " : ":") + p));
            else
                for (g in w)
                    Object.prototype.hasOwnProperty.call(w, g) && (p = c(g, w)) && v.push(a(g) + (k ? ": " : ":") + p);
            p = 0 === v.length ? "{}" : k ? "{\n" + k + v.join(",\n" +
                    k) + "\n" + t + "}" : "{" + v.join(",") + "}";
            k = t;
            return p
        }
    }
    "function" !== typeof Date.prototype.toJSON && (Date.prototype.toJSON = function (a) {
        return isFinite(this.valueOf()) ? this.getUTCFullYear() + "-" + b(this.getUTCMonth() + 1) + "-" + b(this.getUTCDate()) + "T" + b(this.getUTCHours()) + ":" + b(this.getUTCMinutes()) + ":" + b(this.getUTCSeconds()) + "Z" : null
    }, String.prototype.toJSON = Number.prototype.toJSON = Boolean.prototype.toJSON = function (a) {
        return this.valueOf()
    });
    var e = /[\u0000\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
    d = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g,
    k,
    m,
    g = {
        "\b": "\\b",
        "\t": "\\t",
        "\n": "\\n",
        "\f": "\\f",
        "\r": "\\r",
        '"': '\\"',
        "\\": "\\\\"
    },
    f;
    "function" !== typeof JSON.stringify && (JSON.stringify = function (a, b, d) {
        var e;
        m = k = "";
        if ("number" === typeof d)
            for (e = 0; e < d; e += 1)
                m += " ";
        else
            "string" === typeof d && (m = d);
        if ((f = b) && "function" !== typeof b && ("object" !== typeof b || "number" !== typeof b.length))
            throw Error("JSON.stringify");
        return c("", {
            "": a
        })
    });
    "function" !== typeof JSON.parse && (JSON.parse = function (a, b) {
        function d(a, c) {
            var e,
            k,
            f = a[c];
            if (f && "object" === typeof f)
                for (e in f)
                    Object.prototype.hasOwnProperty.call(f, e) && (k = d(f, e), void 0 !== k ? f[e] = k : delete f[e]);
            return b.call(a, c, f)
        }
        var c;
        a = String(a);
        e.lastIndex = 0;
        e.test(a) && (a = a.replace(e, function (a) {
                return "\\u" + ("0000" + a.charCodeAt(0).toString(16)).slice(-4)
            }));
        if (/^[\],:{}\s]*$/.test(a.replace(/\\(?:["\\\/bfnrt]|u[0-9a-fA-F]{4})/g, "@").replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g,
                    "]").replace(/(?:^|:|,)(?:\s*\[)+/g, "")))
            return c = eval("(" + a + ")"), "function" === typeof b ? d({
                "": c
            }, "") : c;
        throw new SyntaxError("JSON.parse");
    })
})();
window.requestAnimationFrame || (window.requestAnimationFrame = function () {
    return window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame || function (b, a) {
        window.setTimeout(b, 1E3 / 60)
    }
}
    ());
String.prototype.replaceAll = function (b, a) {
    if ("object" == typeof b) {
        for (var c = this, e = 0; e < b.length; e++)
            c = c.split(b[e]).join(a[e]);
        return c
    }
    return this.split(b).join(a)
};
String.prototype.trim = function (b) {
    return this.replace(/^\s+|\s+$/g, "")
};
String.prototype.ucfirst = function (b) {
    return this[0].toUpperCase() + this.substr(1)
};
String.prototype.ucwords = function (b) {
    return this.replace(/^(.)|\s(.)/g, function (a) {
        return a.toUpperCase()
    })
};
String.prototype.addslashes = function () {
    return this.replace(/([\\"'])/g, "\\$1").replace(/\0/g, "\\0")
};
String.prototype.stripslashes = function () {
    return this.replace(/\0/g, "0").replace(/\\([\\'"])/g, "$1")
};
String.format = function (b) {
    var a = Array.prototype.slice.call(arguments, 1, arguments.length);
    return b.replace(/\{(\d+)\}/g, function (b, e) {
        return a[e]
    })
};
String.prototype.basename = function () {
    return this.replace(/\\/g, "/").replace(/.*\//, "")
};
if ("undefined" === typeof widgets)
    var widgets = {};
(function () {
    var b = {
        "text/css": "string",
        "text/html": "string",
        "text/plain": "string"
    };
    widgets.FileSaver = function (a) {
        "undefined" === typeof a && (a = {});
        var c = a.jsDir || "./inc/",
        e = this;
        this.html5 = "function" === typeof ArrayBuffer;
        this.boot = function () {
            var b = window.BlobBuilder || window.WebKitBlobBuilder || window.MozBlobBuilder,
            d = window.btoa && window.atob,
            g = [];
            g.push({
                src: c + "File/jszip.js",
                verify: "JSZip"
            });
            d || g.push({
                src: c + "Polyfill/Base64.js",
                verify: ["atob", "btoa"]
            });
            b || g.push({
                src: c + "Polyfill/BlobBuilder.js",
                verify: "BlobBuilder"
            });
            e.html5 ? g.push({
                src: c + "File/FileSaver.js",
                verify: "saveAs"
            }) : g.push({
                src: c + "File/downloadify.js",
                verify: ["Downloadify", "swfobject"]
            });
            DOMLoader.script.add({
                srcs: g,
                callback: function () {
                    if (a.onready)
                        a.onready(e)
                }
            });
            return this
        };
        this.download = function (a) {
            if ("function" === typeof saveAs && "function" === typeof BlobBuilder && a.getData) {
                var c = a.getData(),
                e = a.name,
                f = a.mime,
                l = a.charset;
                a = a.extension;
                var n = "";
                if ("string" === typeof c) {
                    if ("data:" === c.substr(0, 5)) {
                        var r = c.substr(5).split(","),
                        c = r[1],
                        f = r[0].split(";")[0];
                        a || (a = f.split("/")[1]);
                        b[r[0]] || (n = "binary")
                    }
                } else
                    n = "binary", f = "application/zip", a = "zip", c = d(c);
                e || (e = "download");
                f || (f = "text/plain");
                a || (a = "txt");
                n || (n = b[f] || "binary");
                r = new BlobBuilder;
                if ("string" === n)
                    r.append(c), l && (f += ";charset=" + l);
                else {
                    for (var c = atob(c), l = new ArrayBuffer(c.length), n = new Uint8Array(l), q = 0; q < c.length; q++)
                        n[q] = c.charCodeAt(q);
                    r.append(l)
                }
                f = r.getBlob(f);
                saveAs(f, e + "." + a)
            }
        };
        this.button = function (a) {
            var b = a.parent || document.body,
            g = a.id,
            f = a.fileName,
            l = a.fileType,
            n = a.getData,
            r = "fake" ===
                a.format,
            q = document.createElement("span"),
            p = document.createElement("span");
            p.id = g;
            p.style.position = "absolute";
            q.style.cssText = "width: inherit; height: inherit;";
            q.className = "downloadify-container";
            q.appendChild(p);
            var s = document.createElement("span");
            s.style.cssText = "width: inherit; height: inherit;";
            s.className = "downloadify";
            a.src ? (p = new Image, p.src = a.src, s.appendChild(p)) : s.innerHTML = a.title ? a.title : f + "." + l;
            q.appendChild(s);
            b.appendChild(q);
            setTimeout(function () {
                var p = b.offsetWidth,
                v = b.offsetHeight;
                q.style.width = p + "px";
                q.style.height = v + "px";
                var w = document.getElementById(g);
                e.html5 || r ? Event.add(s, "click", function () {
                    if (r)
                        return n();
                    e.download({
                        name: f,
                        extension: l,
                        getData: n
                    })
                }) : (Event.add(w, "mousedown", Event.stop), Downloadify.create(g, {
                        filename: function () {
                            return f + "." + l
                        },
                        data: function () {
                            var a = n();
                            return "string" === typeof a ? a : d(a)
                        },
                        downloadImage: c + "File/downloadify.png",
                        swf: c + "File/downloadify.swf",
                        transparent: !0,
                        append: !1,
                        width: p,
                        height: v,
                        dataType: a.format
                    }))
            }, 1)
        };
        var d = function (a) {
            function c(a,
                d) {
                var e = a.data,
                f = {};
                -1 !== e.indexOf("base64") && (e = e.split(";"), b[e[0].substr(5)] && (f.binary = !1), f.base64 = !0, e = e[1].substr(7));
                d.add(a.name, e, f)
            }
            var d = new JSZip;
            if ("undefined" === typeof a.length)
                if (a.data && a.name)
                    a = [a];
                else {
                    for (var e in a)
                        for (var l = a[e], n = d.folder(e), r = 0, q = l.length; r < q; r++)
                            c(l[r], n);
                    return d.generate()
                }
            r = 0;
            for (q = a.length; r < q; r++)
                c(a[r], d);
            return d.generate()
        };
        return this.boot()
    }
})();
"undefined" === typeof widgets && (widgets = {});
(function () {
    var b = Math.PI,
    a = !document.createElement("canvas").getContext,
    c = {
        id: "loader",
        bars: 12,
        radius: 0,
        lineWidth: 20,
        lineHeight: 70,
        timeout: 0,
        display: !0
    };
    widgets.Loader = function (k) {
        if (!a) {
            var m = this;
            "string" === typeof k && (k = {
                    message: k
                });
            "boolean" === typeof k && (k = {
                    display: !1
                });
            "undefined" === typeof k && (k = {});
            k.container = k.container || document.body;
            if (k.container) {
                for (var g in c)
                    "undefined" === typeof k[g] && (k[g] = c[g]);
                var f = document.getElementById(k.id);
                if (f)
                    this.span = f.parentNode.getElementsByTagName("span")[0];
                else {
                    var l = document.createElement("div");
                    g = document.createElement("span");
                    g.className = "message";
                    l.appendChild(g);
                    l.className = c.id;
                    l.style.cssText = e("opacity", 400);
                    this.span = g;
                    this.div = l;
                    f = document.createElement("canvas");
                    document.body.appendChild(f);
                    f.id = k.id;
                    f.style.cssText = "opacity: 1; position: absolute; z-index: 10000;";
                    l.appendChild(f);
                    k.container.appendChild(l)
                }
                var n = k.bars,
                r = k.radius,
                q = 2 * (k.lineHeight + 20) + 2 * k.radius;
                d(k.container);
                var p = window.devicePixelRatio || 1;
                f.width = q * p;
                f.height = q * p;
                var s =
                    0,
                t = f.getContext("2d");
                t.globalCompositeOperation = "lighter";
                t.shadowOffsetX = 1;
                t.shadowOffsetY = 1;
                t.shadowBlur = 1;
                t.shadowColor = "rgba(0, 0, 0, 0.5)";
                this.messages = {};
                this.message = function (a, b) {
                    return this.interval ? this.add({
                        message: a,
                        onstart: b
                    }) : this.start(b, a)
                };
                this.update = function (a, b, c) {
                    if (!a)
                        for (a in this.messages);
                    if (!a)
                        return this.message(b);
                    a = this.messages[a];
                    a.message = b;
                    "number" === typeof c && (a.span.innerHTML = c + "%");
                    "..." === b.substr(-3) ? (a._message = b.substr(0, b.length - 3), a.messageAnimate = [".&nbsp;&nbsp;",
                            "..&nbsp;", "..."].reverse()) : (a._message = b, a.messageAnimate = !1);
                    a.element.innerHTML = b
                };
                this.add = function (a) {
                    "string" === typeof a && (a = {
                            message: a
                        });
                    this.span.style.cssText = "background: " + (k.background ? k.background : "rgba(0,0,0,0.65)") + ";";
                    this.div.style.cssText = e("opacity", 400);
                    this.div.style.cssText = this.stopPropagation ? this.div.style.cssText + "background: rgba(0,0,0,0.25);" : this.div.style.cssText + "pointer-events: none;";
                    f.parentNode.style.opacity = 1;
                    f.parentNode.style.display = "block";
                    k.background && (this.div.style.background =
                            k.backgrond);
                    var b = (new Date).getTime(),
                    c = Math.abs(b * Math.random() >> 0),
                    d = a.message,
                    g = document.createElement("div");
                    g.style.cssText = e("opacity", 500);
                    var l = document.createElement("span");
                    l.style.cssText = "float: right; width: 50px;";
                    var n = document.createElement("span");
                    n.innerHTML = d;
                    g.appendChild(n);
                    g.appendChild(l);
                    b = this.messages[c] = {
                        seed: c,
                        container: g,
                        element: n,
                        span: l,
                        message: d,
                        timeout: 1E3 * (a.timeout || k.timeout),
                        timestamp: b,
                        getProgress: a.getProgress
                    };
                    this.span.appendChild(g);
                    this.span.style.display =
                        "block";
                    this.update(b.seed, d);
                    a.onstart && window.setTimeout(a.onstart, 50);
                    this.center();
                    this.interval || (a.delay || w(), window.clearInterval(this.interval), this.interval = window.setInterval(w, 30));
                    return c
                };
                this.remove = function (a) {
                    s += 0.07;
                    (new Date).getTime();
                    "object" === typeof a && (a = a.join(":"));
                    a && (a = ":" + a + ":");
                    for (var b in this.messages) {
                        var c = this.messages[b];
                        a && -1 === a.indexOf(":" + c.seed + ":") || (delete this.messages[c.seed], c.container.style.color = "#99ff88", v(c), c.getProgress && (c.span.innerHTML = "100%"))
                    }
                };
                this.start = function (a, b) {
                    if (b || k.message)
                        return this.add({
                            message: b || k.message,
                            onstart: a
                        })
                };
                this.stop = function () {
                    this.remove();
                    window.clearInterval(this.interval);
                    delete this.interval;
                    if (k.oncomplete)
                        k.oncomplete();
                    f && f.style && (l.style.cssText += "pointer-events: none;", window.setTimeout(function () {
                            m.div.style.opacity = 0
                        }, 1), window.setTimeout(function () {
                            m.interval || (m.stopPropagation = !1, f.parentNode.style.display = "none", t.clearRect(0, 0, q, q))
                        }, 4E5))
                };
                this.center = function () {
                    var a = d(k.container),
                    b = a.height -
                        q;
                    f.style.left = (a.width - q) / 2 + "px";
                    f.style.top = b / 2 + "px";
                    f.style.width = q + "px";
                    f.style.height = q + "px";
                    m.span.style.top = b / 2 + q - 10 + "px"
                };
                g = document.createElement("style");
                g.innerHTML = ".loader { color: #fff; position: fixed; left: 0; top: 0; width: 100%; height: 100%; z-index: 100000; opacity: 0; display: none; }.loader span.message { font-family: monospace; font-size: 14px; margin: auto; opacity: 1; display: none; border-radius: 10px; padding: 0px; width: 300px; text-align: center; position: absolute; z-index: 10000; left: 0; right: 0; }.loader span.message div { border-bottom: 1px solid #222; padding: 5px 10px; clear: both; text-align: left; opacity: 1; }.loader span.message div:last-child { border-bottom: none; }";
                document.head.appendChild(g);
                var v = function (a) {
                    window.setTimeout(function () {
                        a.container.style.opacity = 0
                    }, 1);
                    window.setTimeout(function () {
                        a.container.parentNode.removeChild(a.container)
                    }, 250)
                },
                w = function () {
                    var a = (new Date).getTime(),
                    c;
                    for (c in m.messages) {
                        var d = m.messages[c],
                        e = s / 0.07 >> 0;
                        if (0 === e % 5 && d.getProgress) {
                            if (d.timeout && d.timestamp && a - d.timestamp > d.timeout) {
                                m.remove(d.seed);
                                continue
                            }
                            var f = d.getProgress();
                            if (100 <= f) {
                                m.remove(d.seed);
                                continue
                            }
                            d.span.innerHTML = (f >> 0) + "%"
                        }
                        0 === e % 10 && d.messageAnimate &&
                        (d.element.innerHTML = d._message + d.messageAnimate[e / 10 % d.messageAnimate.length])
                    }
                    c || m.stop();
                    t.save();
                    t.clearRect(0, 0, q * p, q * p);
                    t.scale(p, p);
                    t.translate(q / 2, q / 2);
                    a = 360 - 360 / n;
                    for (c = 0; c < n; c++) {
                        d = 2 * (c / n) * b + s;
                        t.save();
                        t.translate(r * Math.sin(-d), r * Math.cos(-d));
                        t.rotate(d);
                        var d = -k.lineWidth / 2,
                        e = k.lineWidth,
                        f = k.lineHeight,
                        g = e / 2;
                        t.beginPath();
                        t.moveTo(d + g, 0);
                        t.lineTo(d + e - g, 0);
                        t.quadraticCurveTo(d + e, 0, d + e, 0 + g);
                        t.lineTo(d + e, 0 + f - g);
                        t.quadraticCurveTo(d + e, 0 + f, d + e - g, 0 + f);
                        t.lineTo(d + g, 0 + f);
                        t.quadraticCurveTo(d,
                            0 + f, d, 0 + f - g);
                        t.lineTo(d, 0 + g);
                        t.quadraticCurveTo(d, 0, d + g, 0);
                        t.fillStyle = "hsla(" + c / (n - 1) * a + ", 100%, 50%, 0.85)";
                        t.fill();
                        t.restore()
                    }
                    t.restore();
                    s += 0.07
                };
                if (!1 === k.display)
                    return this;
                this.start();
                return this
            }
        }
    };
    var e = function (a, b) {
        return "\t\t-webkit-transition-property: " + a + ";\t\t-webkit-transition-duration: " + b + "ms;\t\t-moz-transition-property: " + a + ";\t\t-moz-transition-duration: " + b + "ms;\t\t-o-transition-property: " + a + ";\t\t-o-transition-duration: " + b + "ms;\t\t-ms-transition-property: " + a + ";\t\t-ms-transition-duration: " +
        b + "ms;"
    },
    d = function (a) {
        if (window.innerWidth && window.innerHeight)
            var b = window.innerWidth, d = window.innerHeight;
        else
            "CSS1Compat" === document.compatMode && document.documentElement && document.documentElement.offsetWidth ? (b = document.documentElement.offsetWidth, d = document.documentElement.offsetHeight) : document.body && document.body.offsetWidth && (b = document.body.offsetWidth, d = document.body.offsetHeight);
        a && (b = a.offsetWidth);
        return {
            width: b,
            height: d
        }
    }
})();
"undefined" === typeof widgets && (widgets = {});
widgets.Uploader = function (b) {
    b || (b = {});
    var a = this;
    this.uploadPath = "./gallery-upload.php";
    this.callback = b.callback;
    this.maxFiles = ((this.singleFile = b.singleFile || !1) ? 1 : b.max) || Infinity;
    this.fileCollection = {};
    this.hasFileReader = window.FileReader ? !0 : !1;
    this.acceptedFormats = b.formats || {
        "image/jpg": !0,
        "image/jpeg": !0,
        "image/gif": !0,
        "image/png": !0
    };
    this.uploadCollection = function (b) {
        var d = [],
        c = this.fileCollection,
        e;
        for (e in c)
            d.push(c[e]);
        a.handleFiles(d, {
            upload: !0,
            callback: b
        })
    };
    this.preview = function (b) {
        var d =
            b.name,
        e = function (b) {
            a.fileCollection[d].src = b.target.result;
            a.fileCollection[d].preview = !0;
            return c()
        },
        f = new FileReader;
        f.addEventListener ? f.addEventListener("loadend", e, !1) : f.onloadend = e;
        f.readAsDataURL(b)
    };
    this.upload = function (b) {
        var d = b.name;
        if (a.hasFileReader) {
            var e = function (b) {
                switch (b.target.error.code) {
                case b.target.error.NOT_FOUND_ERR:
                    a.status = "File not found.";
                    break;
                case b.target.error.NOT_READABLE_ERR:
                    a.status = "File not readable.";
                    break;
                case b.target.error.ABORT_ERR:
                    a.status = "Upload has been aborted.";
                    break;
                default:
                    a.status = "Read error."
                }
            },
            f = function (b) {
                b.lengthComputable && (a.status = Math.round(100 * b.loaded / b.total))
            },
            l = function (e) {
                var f = new XMLHttpRequest;
                f.onreadystatechange = function (b) {
                    if (4 === f.readyState && "success" === b.srcElement.responseText)
                        return a.fileCollection[d].uploaded = !0, c()
                };
                "undefined" !== typeof f.sendAsBinary ? (f.open("POST", a.uploadPath + "?upload=true", !0), e = "--xxxxxxxxx\r\n" + ("Content-Disposition: form-data; name='upload'; filename='" + b.name + "'\r\n"), e = e + "Content-Type: application/octet-stream\r\n\r\n" +
                        (n.result + "\r\n"), e += "--xxxxxxxxx\r\n", f.setRequestHeader("content-type", "multipart/form-data; boundary=xxxxxxxxx"), f.sendAsBinary(e)) : (f.open("POST", a.uploadPath + "?upload=true&base64=true", !0), f.setRequestHeader("X-FILENAME", b.name), f.setRequestHeader("X-FILESIZE", b.size), f.setRequestHeader("X-FILETYPE", b.type), f.send(window.btoa(n.result)))
            },
            n = new FileReader;
            "undefined" !== typeof n.addEventListener ? (n.addEventListener("loadend", l, !1), n.addEventListener("error", e, !1), n.addEventListener("progress",
                    f, !1)) : (n.onloadend = l, n.onerror = e, n.onprogress = f);
            n.readAsBinaryString(b)
        } else {
            var r = new XMLHttpRequest;
            r.onreadystatechange = function (b) {
                if (4 === r.readyState && "success" === b.srcElement.responseText)
                    return a.fileCollection[d].uploaded = !0, c()
            };
            r.open("POST", a.uploadPath + "?upload=true", !0);
            r.setRequestHeader("X-FILENAME", b.name);
            r.setRequestHeader("X-FILESIZE", b.size);
            r.setRequestHeader("X-FILETYPE", b.type);
            r.send(b)
        }
    };
    var c;
    this.handleFiles = function (b, d) {
        var e = 0,
        f = b.length;
        d || (d = {});
        0 < f && (a.singleFile &&
            !0 !== d.upload) && (a.fileCollection = {});
        (c = function () {
            var l = b[e],
            n = {
                status: a.status,
                current: e,
                length: f
            };
            if (++e > a.maxFiles || !l)
                a.callback(n, a.fileCollection, f - 1, d.event);
            else {
                a.callback(n);
                n = l.name;
                if (a.fileCollection[n])
                    if (d.upload) {
                        if (a.fileCollection[n].uploaded)
                            return c()
                    } else if (a.fileCollection[n].preview)
                        return c();
                a.fileCollection[n] = l;
                (n = l.type) || (n = "text/" + l.fileName.substr(l.fileName.lastIndexOf(".") + 1));
                if (!a.acceptedFormats[n])
                    return console.log(n + "is not an accepted format."), c();
                if (0 ===
                    (l.fileSize || l.size))
                    return console.log("file is empty."), c();
                if (d.upload)
                    a.upload(l);
                else if (d.preview && a.hasFileReader)
                    a.preview(l);
                else
                    return c()
            }
        })()
    };
    var e = document.createElement("form");
    e.action = "#";
    e.method = "post";
    e.enctype = "multipart/form-data";
    e.style.cssText = "z-index: 10000; position: absolute; left: 0; top: 0; display: none;";
    e.addEventListener("dragenter", function (a) {
        Event.prevent(a);
        Event.stop(a);
        e.style.background = "rgba(255,0,0,0.2)";
        return !1
    }, !1);
    e.addEventListener("dragover", function (a) {
        Event.prevent(a);
        Event.stop(a);
        return !1
    }, !1);
    e.addEventListener("drop", function (b) {
        Event.prevent(b);
        Event.stop(b);
        e.style.display = "none";
        e.style.background = "none";
        b.dataTransfer && b.dataTransfer.files && a.handleFiles(b.dataTransfer.files, {
            preview: !0,
            event: b
        })
    }, !1);
    e.addEventListener("dragleave", function (a) {
        Event.prevent(a);
        Event.stop(a);
        window.setTimeout(function () {
            e.style.display = "none";
            e.style.background = "none"
        }, 100)
    }, !1);
    var d = document.createElement("input");
    d.type = "file";
    d.name = "files[]";
    !this.singleFile && 1 < this.maxFiles &&
    (d.multiple = "multiple");
    d.style.cssText = "position: absolute; opacity: 0;";
    d.addEventListener("change", function (b) {
        d.files && d.files[0] ? a.handleFiles(d.files, {
            preview: !0,
            event: b
        }) : d.value && console.log(d.value)
    }, !1);
    d.addEventListener("click", function (a) {
        Event.prevent(a);
        Event.stop(a)
    }, !1);
    e.appendChild(d);
    b = function (a) {
        !window.innerWidth && (document.body && document.body.offsetWidth) && (window.innerWidth = document.body.offsetWidth, window.innerHeight = document.body.offsetHeight);
        window.innerWidth && window.innerHeight &&
        (e.style.width = window.innerWidth + "px", e.style.height = window.innerHeight + "px")
    };
    b();
    window.addEventListener("dragenter", function (a) {
        e.style.display = "block"
    }, !1);
    window.addEventListener("resize", b, !1);
    document.body.appendChild(e);
    return this
};
"undefined" === typeof DOMLoader && (DOMLoader = {});
DOMLoader.script = function () {
    this.loaded = {};
    this.loading = {};
    return this
};
DOMLoader.script.prototype.add = function (b) {
    var a = this;
    "string" === typeof b && (b = {
            src: b
        });
    var c = b.srcs;
    "undefined" === typeof c && (c = [{
                src: b.src,
                verify: b.verify
            }
        ]);
    var e = document.getElementsByTagName("head")[0],
    d = function (b, d) {
        if (!(a.loaded[b.src] || d && "undefined" === typeof window[d])) {
            a.loaded[b.src] = !0;
            if (a.loading[b.src])
                a.loading[b.src]();
            delete a.loading[b.src];
            b.callback && b.callback();
            "undefined" !== typeof l && l()
        }
    },
    k = [],
    m = function (c) {
        "string" === typeof c && (c = {
                src: c,
                verify: b.verify
            });
        if (/([\w\d.])$/.test(c.verify))
            if (c.test =
                    c.verify, "object" === typeof c.test)
                for (var f in c.test)
                    k.push(c.test[f]);
            else
                k.push(c.test);
        a.loaded[c.src] || (f = document.createElement("script"), f.onreadystatechange = function () {
            "loaded" !== this.readyState && "complete" !== this.readyState || d(c)
        }, f.onload = function () {
            d(c)
        }, f.onerror = function () {}, f.setAttribute("type", "text/javascript"), f.setAttribute("src", c.src), e.appendChild(f), a.loading[c.src] = function () {})
    },
    g = function (a) {
        if (a)
            d(a, a.test);
        else
            for (var e = 0; e < c.length; e++)
                d(c[e], c[e].test);
        for (var f = !0,
            e = 0; e < k.length; e++) {
            var l = k[e];
            if (l && -1 !== l.indexOf(".")) {
                var l = l.split("."),
                m = window[l[0]];
                "undefined" !== typeof m && (2 === l.length ? "undefined" === typeof m[l[1]] && (f = !1) : 3 === l.length && "undefined" === typeof m[l[1]][l[2]] && (f = !1))
            } else
                "undefined" === typeof window[l] && (f = !1)
        }
        !b.strictOrder && f ? b.callback && b.callback() : setTimeout(function () {
            g(a)
        }, 10)
    };
    if (b.strictOrder) {
        var f = -1,
        l = function () {
            f++;
            if (c[f]) {
                var d = c[f],
                e = d.src;
                a.loading[e] ? a.loading[e] = function () {
                    d.callback && d.callback();
                    l()
                }
                 : a.loaded[e] ? l() : (m(d),
                    g(d))
            } else
                b.callback && b.callback()
        };
        l()
    } else {
        for (f = 0; f < c.length; f++)
            m(c[f]);
        g()
    }
};
DOMLoader.script = new DOMLoader.script;
"undefined" === typeof DOMLoader && (DOMLoader = {});
if ("undefined" === typeof XMLHttpRequest) {
    var XMLHttpRequest;
    (function () {
        for (var b = [function () {
                    return new ActiveXObject("Msxml2.XMLHTTP")
                }, function () {
                    return new ActiveXObject("Msxml3.XMLHTTP")
                }, function () {
                    return new ActiveXObject("Microsoft.XMLHTTP")
                }
            ], a = 0; a < b.length; a++) {
            try {
                b[a]()
            } catch (c) {
                continue
            }
            break
        }
        XMLHttpRequest = b[a]
    })()
}
if ("undefined" === typeof(new XMLHttpRequest).responseText) {
    var IEBinaryToArray_ByteStr_Script = "\x3c!-- IEBinaryToArray_ByteStr --\x3e\r\n<script type='text/vbscript'>\r\nFunction IEBinaryToArray_ByteStr(Binary)\r\n   IEBinaryToArray_ByteStr = CStr(Binary)\r\nEnd Function\r\nFunction IEBinaryToArray_ByteStr_Last(Binary)\r\n   Dim lastIndex\r\n   lastIndex = LenB(Binary)\r\n   if lastIndex mod 2 Then\r\n       IEBinaryToArray_ByteStr_Last = Chr( AscB( MidB( Binary, lastIndex, 1 ) ) )\r\n   Else\r\n       IEBinaryToArray_ByteStr_Last = \"\"\r\n   End If\r\nEnd Function\r\n\x3c/script>\r\n";
    document.write(IEBinaryToArray_ByteStr_Script);
    DOMLoader.sendRequest = function (b) {
        function a(a) {
            for (var b = {}, c = 0; 256 > c; c++)
                for (var m = 0; 256 > m; m++)
                    b[String.fromCharCode(c + 256 * m)] = String.fromCharCode(c) + String.fromCharCode(m);
            c = IEBinaryToArray_ByteStr(a);
            a = IEBinaryToArray_ByteStr_Last(a);
            return c.replace(/[\s\S]/g, function (a) {
                return b[a]
            }) + a
        }
        var c = XMLHttpRequest();
        c.open("GET", b.url, !0);
        b.responseType && (c.responseType = b.responseType);
        b.onerror && (c.onerror = b.onerror);
        b.onprogress && (c.onprogress = b.onprogress);
        c.onreadystatechange = function (e) {
            if (4 === c.readyState && (200 === c.status ? c.responseText = a(c.responseBody) : c = !1, b.onload))
                b.onload(c)
        };
        c.setRequestHeader("Accept-Charset", "x-user-defined");
        c.send(null);
        return c
    }
} else
    DOMLoader.sendRequest = function (b) {
        var a = new XMLHttpRequest;
        a.open(b.data ? "POST" : "GET", b.url, !0);
        a.overrideMimeType && a.overrideMimeType("text/plain; charset=x-user-defined");
        b.data && a.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        b.responseType && (a.responseType = b.responseType);
        b.onerror && (a.onerror = b.onerror);
        b.onprogress && (a.onprogress = b.onprogress);
        a.onreadystatechange = function (c) {
            if (4 === a.readyState)
                if (200 !== a.status && 304 != a.status) {
                    if (b.onerror)
                        b.onerror(c, !1)
                } else if (b.onload)
                    b.onload(a)
        };
        a.send(b.data);
        return a
    };
if ("undefined" === typeof Event)
    var Event = {};
if ("undefined" === typeof eventjs)
    var eventjs = Event;
Event = function (b) {
    b.modifyEventListener = !0;
    b.modifySelectors = !0;
    b.add = function (a, b, d, e) {
        return c(a, b, d, e, "add")
    };
    b.remove = function (a, b, d, e) {
        return c(a, b, d, e, "remove")
    };
    b.stop = function (a) {
        a.stopPropagation && a.stopPropagation();
        a.cancelBubble = !0;
        a.bubble = 0
    };
    b.prevent = function (a) {
        a.preventDefault && a.preventDefault();
        a.returnValue = !1
    };
    b.cancel = function (a) {
        b.stop(a);
        b.prevent(a)
    };
    b.supports = function (a, b) {
        "string" === typeof a && (b = a, a = window);
        b = "on" + b;
        if (b in a)
            return !0;
        a.setAttribute || (a = document.createElement("div"));
        if (a.setAttribute && a.removeAttribute) {
            a.setAttribute(b, "");
            var d = "function" === typeof a[b];
            "undefined" !== typeof a[b] && (a[b] = null);
            a.removeAttribute(b);
            return d
        }
    };
    var a = function (b) {
        if (!b || "object" !== typeof b)
            return b;
        var d = new b.constructor,
        c;
        for (c in b)
            d[c] = b[c] && "object" === typeof b[c] ? a(b[c]) : b[c];
        return d
    },
    c = function (g, q, p, s, t, v) {
        s = s || {};
        if (g && q && p)
            if ("string" === typeof g && "ready" === q)
                var w = (new Date).getTime(), F = s.timeout, B = window.setInterval(function () {
                    (new Date).getTime() - w > F && window.clearInterval(B);
                    document.querySelector(g) && (window.clearInterval(B), setTimeout(p, 1))
                }, s.interval || 1E3 / 60);
            else {
                if ("string" === typeof g) {
                    g = document.querySelectorAll(g);
                    if (0 === g.length)
                        return d("Missing target on listener!");
                    1 === g.length && (g = g[0])
                }
                var x = {};
                if (0 < g.length && g !== window) {
                    for (var u = 0, y = g.length; u < y; u++)
                        (v = c(g[u], q, p, a(s), t)) && (x[u] = v);
                    return e(x)
                }
                q.indexOf && -1 !== q.indexOf(" ") && (q = q.split(" "));
                q.indexOf && -1 !== q.indexOf(",") && (q = q.split(","));
                if ("string" !== typeof q) {
                    if ("number" === typeof q.length)
                        for (u = 0,
                            y = q.length; u < y; u++)
                            (v = c(g, q[u], p, a(s), t)) && (x[q[u]] = v);
                    else
                        for (u in q)
                            (v = "function" === typeof q[u] ? c(g, u, q[u], a(s), t) : c(g, u, q[u].listener, a(q[u]), t)) && (x[u] = v);
                    return e(x)
                }
                if ("function" !== typeof p)
                    return d("Listener is not a function!");
                x = s.useCapture || !1;
                u = k(q) + f(g) + "." + f(p) + "." + (x ? 1 : 0);
                if (b.Gesture && b.Gesture._gestureHandlers[q])
                    if ("remove" === t) {
                        if (!m[u])
                            return;
                        m[u].remove();
                        delete m[u]
                    } else {
                        if ("add" === t) {
                            if (m[u])
                                return m[u];
                            if (s.useCall && !b.modifyEventListener) {
                                var z = p;
                                p = function (a, b) {
                                    for (var d in b)
                                        a[d] =
                                            b[d];
                                    return z.call(g, a)
                                }
                            }
                            s.gesture = q;
                            s.target = g;
                            s.listener = p;
                            s.fromOverwrite = v;
                            m[u] = b.proxy[q](s)
                        }
                    }
                else if (q = k(q), "remove" === t) {
                    if (!m[u])
                        return;
                    g[n](q, p, x);
                    delete m[u]
                } else if ("add" === t) {
                    if (m[u])
                        return m[u];
                    g[l](q, p, x);
                    m[u] = {
                        type: q,
                        target: g,
                        listener: p,
                        remove: function () {
                            b.remove(g, q, p, s)
                        }
                    }
                }
                return m[u]
            }
    },
    e = function (a) {
        return {
            remove: function () {
                for (var b in a)
                    a[b].remove()
            },
            add: function () {
                for (var b in a)
                    a[b].add()
            }
        }
    },
    d = function (a) {
        "undefined" !== typeof console && "undefined" !== typeof console.error && console.error(a)
    },
    k = function () {
        var a = {};
        return function (d) {
            b.pointerType || (window.navigator.msPointerEnabled ? (b.pointerType = "mspointer", a = {
                        mousedown: "MSPointerDown",
                        mousemove: "MSPointerMove",
                        mouseup: "MSPointerUp"
                    }) : b.supports("touchstart") ? (b.pointerType = "touch", a = {
                        mousedown: "touchstart",
                        mouseup: "touchend",
                        mousemove: "touchmove"
                    }) : b.pointerType = "mouse");
            a[d] && (d = a[d]);
            return document.addEventListener ? d : "on" + d
        }
    }
    (),
    m = {},
    g = 0,
    f = function (a) {
        if (a === window)
            return "#window";
        if (a === document)
            return "#document";
        if (!a)
            return d("Missing target on listener!");
        a.uniqueID || (a.uniqueID = "id" + g++);
        return a.uniqueID
    },
    l = document.addEventListener ? "addEventListener" : "attachEvent",
    n = document.removeEventListener ? "removeEventListener" : "detachEvent";
    b.createPointerEvent = function (a, d, c) {
        var e = d.gesture,
        f = d.target,
        g = a.changedTouches || b.proxy.getCoords(a);
        if (g.length) {
            var l = g[0];
            d.pointers = c ? [] : g;
            d.pageX = l.pageX;
            d.pageY = l.pageY;
            d.x = d.pageX;
            d.y = d.pageY
        }
        c = document.createEvent("Event");
        c.initEvent(e, !0, !0);
        c.originalEvent = a;
        for (var k in d)
            "target" !== k && (c[k] = d[k]);
        f.dispatchEvent(c)
    };
    b.modifyEventListener && window.HTMLElement && function () {
        var a = function (a) {
            var d = function (d) {
                var e = d + "EventListener",
                f = a[e];
                a[e] = function (a, e, g) {
                    if (b.Gesture && b.Gesture._gestureHandlers[a]) {
                        var l = g;
                        "object" === typeof g ? l.useCall = !0 : l = {
                            useCall: !0,
                            useCapture: g
                        };
                        c(this, a, e, l, d, !0);
                        f.call(this, a, e, g)
                    } else
                        f.call(this, k(a), e, g)
                }
            };
            d("add");
            d("remove")
        };
        navigator.userAgent.match(/Firefox/) ? (a(HTMLDivElement.prototype), a(HTMLCanvasElement.prototype)) : a(HTMLElement.prototype);
        a(document);
        a(window)
    }
    ();
    b.modifySelectors &&
    function () {
        var a = NodeList.prototype;
        a.removeEventListener = function (a, b, d) {
            for (var c = 0, e = this.length; c < e; c++)
                this[c].removeEventListener(a, b, d)
        };
        a.addEventListener = function (a, b, d) {
            for (var c = 0, e = this.length; c < e; c++)
                this[c].addEventListener(a, b, d)
        }
    }
    ();
    return b
}
(Event);
"undefined" === typeof Event && (Event = {});
"undefined" === typeof Event.proxy && (Event.proxy = {});
Event.proxy = function (b) {
    b.pointerSetup = function (a, b) {
        a.doc = a.target.ownerDocument || a.target;
        a.minFingers = a.minFingers || a.fingers || 1;
        a.maxFingers = a.maxFingers || a.fingers || Infinity;
        a.position = a.position || "relative";
        delete a.fingers;
        b = b || {};
        b.gesture = a.gesture;
        b.target = a.target;
        b.pointerType = Event.pointerType;
        Event.modifyEventListener && a.fromOverwrite && (a.listener = Event.createPointerEvent);
        var e = 0,
        d = 0 === b.gesture.indexOf("pointer") && Event.modifyEventListener ? "pointer" : "mouse";
        b.listener = a.listener;
        b.proxy =
        function (d) {
            b.defaultListener = a.listener;
            a.listener = d;
            d(a.event, b)
        };
        b.attach = function () {
            a.onPointerDown && Event.add(a.target, d + "down", a.onPointerDown);
            a.onPointerMove && Event.add(a.doc, d + "move", a.onPointerMove);
            a.onPointerUp && Event.add(a.doc, d + "up", a.onPointerUp)
        };
        b.remove = function () {
            a.onPointerDown && Event.remove(a.target, d + "down", a.onPointerDown);
            a.onPointerMove && Event.remove(a.doc, d + "move", a.onPointerMove);
            a.onPointerUp && Event.remove(a.doc, d + "up", a.onPointerUp);
            b.reset()
        };
        b.pause = function (b) {
            !a.onPointerMove ||
            b && !b.move || Event.remove(a.doc, d + "move", a.onPointerMove);
            !a.onPointerUp || b && !b.up || Event.remove(a.doc, d + "up", a.onPointerUp);
            e = a.fingers;
            a.fingers = 0
        };
        b.resume = function (b) {
            !a.onPointerMove || b && !b.move || Event.add(a.doc, d + "move", a.onPointerMove);
            !a.onPointerUp || b && !b.up || Event.add(a.doc, d + "up", a.onPointerUp);
            a.fingers = e
        };
        b.reset = function () {
            delete a.tracker;
            a.fingers = 0
        };
        return b
    };
    b.pointerStart = function (a, c, e) {
        var d = function (a, b) {
            var d = e.bbox,
            c = m[b] = {};
            switch (e.position) {
            case "absolute":
                c.offsetX = 0;
                c.offsetY =
                    0;
                break;
            case "difference":
                c.offsetX = a.pageX;
                c.offsetY = a.pageY;
                break;
            case "move":
                c.offsetX = a.pageX - d.x1;
                c.offsetY = a.pageY - d.y1;
                break;
            default:
                c.offsetX = d.x1,
                c.offsetY = d.y1
            }
            if ("relative" === e.position)
                var f = (a.pageX + d.scrollLeft - c.offsetX) * d.scaleX, d = (a.pageY + d.scrollTop - c.offsetY) * d.scaleY;
            else
                f = a.pageX - c.offsetX, d = a.pageY - c.offsetY;
            c.rotation = 0;
            c.scale = 1;
            c.startTime = c.moveTime = (new Date).getTime();
            c.move = {
                x: f,
                y: d
            };
            c.start = {
                x: f,
                y: d
            };
            e.fingers++
        };
        e.event = a;
        c.defaultListener && (e.listener = c.defaultListener,
            delete c.defaultListener);
        var k = !e.fingers,
        m = e.tracker;
        a = a.changedTouches || b.getCoords(a);
        for (var g = a.length, f = 0; f < g; f++) {
            var l = a[f],
            n = l.identifier || Infinity;
            if (e.fingers) {
                if (e.fingers >= e.maxFingers) {
                    d = [];
                    for (n in e.tracker)
                        d.push(n);
                    c.identifier = d.join(",");
                    return k
                }
                var r = 0,
                q;
                for (q in m) {
                    if (m[q].up) {
                        delete m[q];
                        d(l, n);
                        e.cancel = !0;
                        break
                    }
                    r++
                }
                m[n] || d(l, n)
            } else
                m = e.tracker = {},
            c.bbox = e.bbox = b.getBoundingBox(e.target),
            e.fingers = 0,
            e.cancel = !1,
            d(l, n)
        }
        d = [];
        for (n in e.tracker)
            d.push(n);
        c.identifier = d.join(",");
        return k
    };
    b.pointerEnd = function (a, b, e, d) {
        var k = a.touches || [],
        m = k.length;
        a = {};
        for (var g = 0; g < m; g++) {
            var f = k[g].identifier;
            a[f || Infinity] = !0
        }
        for (f in e.tracker)
            k = e.tracker[f], a[f] || k.up || (d && d({
                    pageX: k.pageX,
                    pageY: k.pageY,
                    changedTouches: [{
                            pageX: k.pageX,
                            pageY: k.pageY,
                            identifier: "Infinity" === f ? Infinity : f
                        }
                    ]
                }, "up"), k.up = !0, e.fingers--);
        if (0 !== e.fingers)
            return !1;
        d = [];
        e.gestureFingers = 0;
        for (f in e.tracker)
            e.gestureFingers++, d.push(f);
        b.identifier = d.join(",");
        return !0
    };
    b.getCoords = function (a) {
        b.getCoords = "undefined" !==
            typeof a.pageX ? function (a) {
            return Array({
                type: "mouse",
                x: a.pageX,
                y: a.pageY,
                pageX: a.pageX,
                pageY: a.pageY,
                identifier: Infinity
            })
        }
         : function (a) {
            a = a || window.event;
            return Array({
                type: "mouse",
                x: a.clientX + document.documentElement.scrollLeft,
                y: a.clientY + document.documentElement.scrollTop,
                pageX: a.clientX + document.documentElement.scrollLeft,
                pageY: a.clientY + document.documentElement.scrollTop,
                identifier: Infinity
            })
        };
        return b.getCoords(a)
    };
    b.getCoord = function (a) {
        if ("ontouchstart" in window) {
            var c = 0,
            e = 0;
            b.getCoord = function (a) {
                a =
                    a.changedTouches;
                return a.length ? {
                    x: c = a[0].pageX,
                    y: e = a[0].pageY
                }
                 : {
                    x: c,
                    y: e
                }
            }
        } else
            b.getCoord = "undefined" !== typeof a.pageX && "undefined" !== typeof a.pageY ? function (a) {
                return {
                    x: a.pageX,
                    y: a.pageY
                }
            }
         : function (a) {
            a = a || window.event;
            return {
                x: a.clientX + document.documentElement.scrollLeft,
                y: a.clientY + document.documentElement.scrollTop
            }
        };
        return b.getCoord(a)
    };
    b.getBoundingBox = function (a) {
        if (a === window || a === document)
            a = document.body;
        var b = {
            x1: 0,
            y1: 0,
            x2: 0,
            y2: 0,
            scrollLeft: 0,
            scrollTop: 0
        };
        a === document.body ? (b.height =
                window.innerHeight, b.width = window.innerWidth) : (b.height = a.offsetHeight, b.width = a.offsetWidth);
        b.scaleX = a.width / b.width || 1;
        b.scaleY = a.height / b.height || 1;
        for (var e = a; null !== e; )
            b.x1 += e.offsetLeft, b.y1 += e.offsetTop, e = e.offsetParent;
        for (e = a.parentNode; null !== e && e !== document.body && void 0 !== e.scrollTop; )
            b.scrollLeft += e.scrollLeft, b.scrollTop += e.scrollTop, e = e.parentNode;
        b.x2 = b.x1 + b.width;
        b.y2 = b.y1 + b.height;
        return b
    };
    (function () {
        var a = navigator.userAgent.toLowerCase(),
        c = -1 !== a.indexOf("macintosh"),
        e = c && -1 !==
            a.indexOf("khtml") ? {
            91: !0,
            93: !0
        }
         : c && -1 !== a.indexOf("firefox") ? {
            224: !0
        }
         : {
            17: !0
        };
        b.isMetaKey = function (a) {
            return !!e[a.keyCode]
        };
        b.metaTracker = function (a) {
            e[a.keyCode] && (b.metaKey = "keydown" === a.type)
        }
    })();
    return b
}
(Event.proxy);
"undefined" === typeof Event && (Event = {});
"undefined" === typeof Event.proxy && (Event.proxy = {});
Event.proxy = function (b) {
    b.click = function (a) {
        a.maxFingers = a.maxFingers || a.fingers || 1;
        var c;
        a.onPointerDown = function (d) {
            b.pointerStart(d, e, a) && (Event.add(a.doc, "mousemove", a.onPointerMove).listener(d), Event.add(a.doc, "mouseup", a.onPointerUp))
        };
        a.onPointerMove = function (a) {
            c = a
        };
        a.onPointerUp = function (d) {
            if (b.pointerEnd(d, e, a) && (Event.remove(a.doc, "mousemove", a.onPointerMove), Event.remove(a.doc, "mouseup", a.onPointerUp), !(c.cancelBubble && 1 < ++c.bubble))) {
                var k = (c.changedTouches || b.getCoords(c))[0];
                d = a.bbox;
                var m = b.getBoundingBox(a.target);
                if ("relative" === a.position)
                    var g = (k.pageX + d.scrollLeft - d.x1) * d.scaleX, k = (k.pageY + d.scrollTop - d.y1) * d.scaleY;
                else
                    g = k.pageX - d.x1, k = k.pageY - d.y1;
                0 < g && (g < d.width && 0 < k && k < d.height && d.scrollTop === m.scrollTop) && a.listener(c, e)
            }
        };
        var e = b.pointerSetup(a);
        e.state = "click";
        Event.add(a.target, "mousedown", a.onPointerDown);
        return e
    };
    Event.Gesture = Event.Gesture || {};
    Event.Gesture._gestureHandlers = Event.Gesture._gestureHandlers || {};
    Event.Gesture._gestureHandlers.click = b.click;
    return b
}
(Event.proxy);
"undefined" === typeof Event && (Event = {});
"undefined" === typeof Event.proxy && (Event.proxy = {});
Event.proxy = function (b) {
    b.dbltap = b.dblclick = function (a) {
        a.maxFingers = a.maxFingers || a.fingers || 1;
        var c,
        e,
        d,
        k,
        m;
        a.onPointerDown = function (f) {
            var l = f.changedTouches || b.getCoords(f);
            c && !e ? (m = l[0], e = (new Date).getTime() - c) : (k = l[0], c = (new Date).getTime(), e = 0, clearTimeout(d), d = setTimeout(function () {
                    c = 0
                }, 700));
            b.pointerStart(f, g, a) && (Event.add(a.doc, "mousemove", a.onPointerMove).listener(f), Event.add(a.doc, "mouseup", a.onPointerUp))
        };
        a.onPointerMove = function (f) {
            c && !e && (m = (f.changedTouches || b.getCoords(f))[0]);
            f = a.bbox;
            if ("relative" === a.position)
                var g = (m.pageX + f.scrollLeft - f.x1) * f.scaleX, n = (m.pageY + f.scrollTop - f.y1) * f.scaleY;
            else
                g = m.pageX - f.x1, n = m.pageY - f.y1;
            0 < g && g < f.width && 0 < n && n < f.height && 25 >= Math.abs(m.pageX - k.pageX) && 25 >= Math.abs(m.pageY - k.pageY) || (Event.remove(a.doc, "mousemove", a.onPointerMove), clearTimeout(d), c = e = 0)
        };
        a.onPointerUp = function (f) {
            b.pointerEnd(f, g, a) && (Event.remove(a.doc, "mousemove", a.onPointerMove), Event.remove(a.doc, "mouseup", a.onPointerUp));
            c && e && (700 >= e && !(f.cancelBubble && 1 < ++f.bubble) &&
                (g.state = a.gesture, a.listener(f, g)), clearTimeout(d), c = e = 0)
        };
        var g = b.pointerSetup(a);
        g.state = "dblclick";
        Event.add(a.target, "mousedown", a.onPointerDown);
        return g
    };
    Event.Gesture = Event.Gesture || {};
    Event.Gesture._gestureHandlers = Event.Gesture._gestureHandlers || {};
    Event.Gesture._gestureHandlers.dbltap = b.dbltap;
    Event.Gesture._gestureHandlers.dblclick = b.dblclick;
    return b
}
(Event.proxy);
"undefined" === typeof Event && (Event = {});
"undefined" === typeof Event.proxy && (Event.proxy = {});
Event.proxy = function (b) {
    b.dragElement = function (a, c) {
        b.drag({
            event: c,
            target: a,
            position: "move",
            listener: function (b, d) {
                a.style.left = d.x + "px";
                a.style.top = d.y + "px";
                Event.prevent(b)
            }
        })
    };
    b.drag = function (a) {
        a.gesture = "drag";
        a.onPointerDown = function (e) {
            b.pointerStart(e, c, a) && !a.monitor && (Event.add(a.doc, "mousemove", a.onPointerMove), Event.add(a.doc, "mouseup", a.onPointerUp));
            a.onPointerMove(e, "down")
        };
        a.onPointerMove = function (e, d) {
            if (!a.tracker)
                return a.onPointerDown(e);
            for (var k = a.bbox, m = e.changedTouches ||
                    b.getCoords(e), g = m.length, f = 0; f < g; f++) {
                var l = m[f],
                n = l.identifier || Infinity,
                r = a.tracker[n];
                r && (r.pageX = l.pageX, r.pageY = l.pageY, c.state = d || "move", c.identifier = n, c.start = r.start, c.fingers = a.fingers, "relative" === a.position ? (c.x = (r.pageX + k.scrollLeft - r.offsetX) * k.scaleX, c.y = (r.pageY + k.scrollTop - r.offsetY) * k.scaleY) : (c.x = r.pageX - r.offsetX, c.y = r.pageY - r.offsetY), a.listener(e, c))
            }
        };
        a.onPointerUp = function (e) {
            b.pointerEnd(e, c, a, a.onPointerMove) && !a.monitor && (Event.remove(a.doc, "mousemove", a.onPointerMove),
                Event.remove(a.doc, "mouseup", a.onPointerUp))
        };
        var c = b.pointerSetup(a);
        if (a.event)
            a.onPointerDown(a.event);
        else
            Event.add(a.target, "mousedown", a.onPointerDown), a.monitor && (Event.add(a.doc, "mousemove", a.onPointerMove), Event.add(a.doc, "mouseup", a.onPointerUp));
        return c
    };
    Event.Gesture = Event.Gesture || {};
    Event.Gesture._gestureHandlers = Event.Gesture._gestureHandlers || {};
    Event.Gesture._gestureHandlers.drag = b.drag;
    return b
}
(Event.proxy);
"undefined" === typeof Event && (Event = {});
"undefined" === typeof Event.proxy && (Event.proxy = {});
Event.proxy = function (b) {
    var a = Math.PI / 180;
    b.gesture = function (c) {
        c.minFingers = c.minFingers || c.fingers || 2;
        c.onPointerDown = function (a) {
            var k = c.fingers;
            b.pointerStart(a, e, c) && (Event.add(c.doc, "mousemove", c.onPointerMove), Event.add(c.doc, "mouseup", c.onPointerUp));
            if (c.fingers === c.minFingers && k !== c.fingers) {
                e.fingers = c.minFingers;
                e.scale = 1;
                e.rotation = 0;
                e.state = "start";
                var k = "",
                m;
                for (m in c.tracker)
                    k += m;
                e.identifier = parseInt(k);
                c.listener(a, e)
            }
        };
        c.onPointerMove = function (d, k) {
            for (var m = c.bbox, g = c.tracker,
                f = d.changedTouches || b.getCoords(d), l = f.length, n = 0; n < l; n++) {
                var r = f[n],
                q = r.identifier || Infinity,
                p = g[q];
                p && ("relative" === c.position ? (p.move.x = (r.pageX + m.scrollLeft - m.x1) * m.scaleX, p.move.y = (r.pageY + m.scrollTop - m.y1) * m.scaleY) : (p.move.x = r.pageX - m.x1, p.move.y = r.pageY - m.y1))
            }
            if (!(c.fingers < c.minFingers)) {
                var f = [],
                s = p = n = m = 0,
                l = 0;
                for (q in g)
                    r = g[q], r.up || (p += r.move.x, s += r.move.y, l++);
                p /= l;
                s /= l;
                for (q in g)
                    if (r = g[q], !r.up) {
                        l = r.start;
                        if (!l.distance) {
                            var t = l.x - p,
                            v = l.y - s;
                            l.distance = Math.sqrt(t * t + v * v);
                            l.angle = Math.atan2(t,
                                    v) / a
                        }
                        var t = r.move.x - p,
                        v = r.move.y - s,
                        w = Math.sqrt(t * t + v * v),
                        m = m + w / l.distance,
                        t = Math.atan2(t, v) / a,
                        l = (l.angle - t + 360) % 360 - 180;
                        r.DEG2 = r.DEG1;
                        r.DEG1 = 0 < l ? l : -l;
                        "undefined" !== typeof r.DEG2 && (r.rotation = 0 < l ? r.rotation + (r.DEG1 - r.DEG2) : r.rotation - (r.DEG1 - r.DEG2), n += r.rotation);
                        f.push(r.move)
                    }
                e.touches = f;
                e.fingers = c.fingers;
                e.scale = m / c.fingers;
                e.rotation = n / c.fingers;
                e.state = "change";
                c.listener(d, e)
            }
        };
        c.onPointerUp = function (a) {
            var k = c.fingers;
            b.pointerEnd(a, e, c) && (Event.remove(c.doc, "mousemove", c.onPointerMove), Event.remove(c.doc,
                    "mouseup", c.onPointerUp));
            k === c.minFingers && c.fingers < c.minFingers && (e.fingers = c.fingers, e.state = "end", c.listener(a, e))
        };
        var e = b.pointerSetup(c);
        Event.add(c.target, "mousedown", c.onPointerDown);
        return e
    };
    Event.Gesture = Event.Gesture || {};
    Event.Gesture._gestureHandlers = Event.Gesture._gestureHandlers || {};
    Event.Gesture._gestureHandlers.gesture = b.gesture;
    return b
}
(Event.proxy);
"undefined" === typeof Event && (Event = {});
"undefined" === typeof Event.proxy && (Event.proxy = {});
Event.proxy = function (b) {
    b.pointerdown = b.pointermove = b.pointerup = function (a) {
        if (!a.target.isPointerEmitter) {
            var c = !0;
            a.onPointerDown = function (b) {
                c = !1;
                e.gesture = "pointerdown";
                a.listener(b, e)
            };
            a.onPointerMove = function (b) {
                e.gesture = "pointermove";
                a.listener(b, e, c)
            };
            a.onPointerUp = function (b) {
                c = !0;
                e.gesture = "pointerup";
                a.listener(b, e, !0)
            };
            var e = b.pointerSetup(a);
            Event.add(a.target, "mousedown", a.onPointerDown);
            Event.add(a.target, "mousemove", a.onPointerMove);
            Event.add(a.doc, "mouseup", a.onPointerUp);
            a.target.isPointerEmitter =
                !0;
            return e
        }
    };
    Event.Gesture = Event.Gesture || {};
    Event.Gesture._gestureHandlers = Event.Gesture._gestureHandlers || {};
    Event.Gesture._gestureHandlers.pointerdown = b.pointerdown;
    Event.Gesture._gestureHandlers.pointermove = b.pointermove;
    Event.Gesture._gestureHandlers.pointerup = b.pointerup;
    return b
}
(Event.proxy);
"undefined" === typeof Event && (Event = {});
"undefined" === typeof Event.proxy && (Event.proxy = {});
Event.proxy = function (b) {
    b.shake = function (a) {
        var b = {
            gesture: "devicemotion",
            acceleration: {},
            accelerationIncludingGravity: {},
            target: a.target,
            listener: a.listener,
            remove: function () {
                window.removeEventListener("devicemotion", m, !1)
            }
        },
        e = (new Date).getTime(),
        d = {
            x: 0,
            y: 0,
            z: 0
        },
        k = {
            x: {
                count: 0,
                value: 0
            },
            y: {
                count: 0,
                value: 0
            },
            z: {
                count: 0,
                value: 0
            }
        },
        m = function (g) {
            var f = g.accelerationIncludingGravity;
            d.x = 0.8 * d.x + (1 - 0.8) * f.x;
            d.y = 0.8 * d.y + (1 - 0.8) * f.y;
            d.z = 0.8 * d.z + (1 - 0.8) * f.z;
            b.accelerationIncludingGravity = d;
            b.acceleration.x =
                f.x - d.x;
            b.acceleration.y = f.y - d.y;
            b.acceleration.z = f.z - d.z;
            if ("devicemotion" === a.gesture)
                a.listener(g, b);
            else
                for (var f = (new Date).getTime(), l = 0; 3 > l; l++) {
                    var n = "xyz"[l],
                    m = b.acceleration[n],
                    n = k[n],
                    q = Math.abs(m);
                    !(1E3 > f - e) && 4 < q && (m = f * m / q, q = Math.abs(m + n.value), n.value && 200 > q ? (n.value = m, n.count++, 3 === n.count && (a.listener(g, b), e = f, n.value = 0, n.count = 0)) : (n.value = m, n.count = 1))
                }
        };
        if (window.addEventListener)
            return window.addEventListener("devicemotion", m, !1), b
    };
    Event.Gesture = Event.Gesture || {};
    Event.Gesture._gestureHandlers =
        Event.Gesture._gestureHandlers || {};
    Event.Gesture._gestureHandlers.shake = b.shake;
    return b
}
(Event.proxy);
"undefined" === typeof Event && (Event = {});
"undefined" === typeof Event.proxy && (Event.proxy = {});
Event.proxy = function (b) {
    var a = Math.PI / 180;
    b.swipe = function (c) {
        c.snap = c.snap || 90;
        c.threshold = c.threshold || 1;
        c.onPointerDown = function (a) {
            b.pointerStart(a, e, c) && (Event.add(c.doc, "mousemove", c.onPointerMove).listener(a), Event.add(c.doc, "mouseup", c.onPointerUp))
        };
        c.onPointerMove = function (a) {
            a = a.changedTouches || b.getCoords(a);
            for (var e = a.length, m = 0; m < e; m++) {
                var g = a[m],
                f = c.tracker[g.identifier || Infinity];
                f && (f.move.x = g.pageX, f.move.y = g.pageY, f.moveTime = (new Date).getTime())
            }
        };
        c.onPointerUp = function (d) {
            if (b.pointerEnd(d,
                    e, c)) {
                Event.remove(c.doc, "mousemove", c.onPointerMove);
                Event.remove(c.doc, "mouseup", c.onPointerUp);
                var k,
                m,
                g,
                f,
                l = {
                    x: 0,
                    y: 0
                },
                n = 0,
                r = 0,
                q = 0,
                p;
                for (p in c.tracker) {
                    var s = c.tracker[p];
                    f = s.move.x - s.start.x;
                    var t = s.move.y - s.start.y,
                    n = n + s.move.x,
                    r = r + s.move.y;
                    l.x += s.start.x;
                    l.y += s.start.y;
                    q++;
                    m = Math.sqrt(f * f + t * t);
                    s = s.moveTime - s.startTime;
                    f = Math.atan2(f, t) / a + 180;
                    m = s ? m / s : 0;
                    if ("undefined" === typeof g)
                        g = f, k = m;
                    else if (20 >= Math.abs(f - g))
                        g = (g + f) / 2, k = (k + m) / 2;
                    else
                        return
                }
                k > c.threshold && (l.x /= q, l.y /= q, e.start = l, e.x = n / q,
                    e.y = r / q, e.angle =  - (((g / c.snap + 0.5 >> 0) * c.snap || 360) - 360), e.velocity = k, e.fingers = c.gestureFingers, e.state = "swipe", c.listener(d, e))
            }
        };
        var e = b.pointerSetup(c);
        Event.add(c.target, "mousedown", c.onPointerDown);
        return e
    };
    Event.Gesture = Event.Gesture || {};
    Event.Gesture._gestureHandlers = Event.Gesture._gestureHandlers || {};
    Event.Gesture._gestureHandlers.swipe = b.swipe;
    return b
}
(Event.proxy);
"undefined" === typeof Event && (Event = {});
"undefined" === typeof Event.proxy && (Event.proxy = {});
Event.proxy = function (b) {
    b.tap = b.longpress = function (a) {
        a.delay = a.delay || 500;
        a.timeout = a.timeout || 250;
        var c,
        e;
        a.onPointerDown = function (k) {
            b.pointerStart(k, d, a) && (c = (new Date).getTime(), Event.add(a.doc, "mousemove", a.onPointerMove).listener(k), Event.add(a.doc, "mouseup", a.onPointerUp), "longpress" === a.gesture && (e = setTimeout(function () {
                        if (!(k.cancelBubble && 1 < ++k.bubble)) {
                            var b = 0,
                            c;
                            for (c in a.tracker) {
                                if (!0 === a.tracker[c].end || a.cancel)
                                    return;
                                b++
                            }
                            d.state = "start";
                            d.fingers = b;
                            a.listener(k, d)
                        }
                    }, a.delay)))
        };
        a.onPointerMove = function (d) {
            var c = a.bbox;
            d = d.changedTouches || b.getCoords(d);
            for (var e = d.length, f = 0; f < e; f++) {
                var l = d[f],
                n = a.tracker[l.identifier || Infinity];
                if (n) {
                    if ("relative" === a.position)
                        var r = (l.pageX + c.scrollLeft - c.x1) * c.scaleX, l = (l.pageY + c.scrollTop - c.y1) * c.scaleY;
                    else
                        r = l.pageX - c.x1, l = l.pageY - c.y1;
                    if (!(0 < r && r < c.width && 0 < l && l < c.height && 25 >= Math.abs(r - n.start.x) && 25 >= Math.abs(l - n.start.y))) {
                        Event.remove(a.doc, "mousemove", a.onPointerMove);
                        a.cancel = !0;
                        break
                    }
                }
            }
        };
        a.onPointerUp = function (k) {
            b.pointerEnd(k,
                d, a) && (clearTimeout(e), Event.remove(a.doc, "mousemove", a.onPointerMove), Event.remove(a.doc, "mouseup", a.onPointerUp), k.cancelBubble && 1 < ++k.bubble || ("longpress" === a.gesture ? "start" === d.state && (d.state = "end", a.listener(k, d)) : a.cancel || (new Date).getTime() - c > a.timeout || (d.state = "tap", d.fingers = a.gestureFingers, a.listener(k, d))))
        };
        var d = b.pointerSetup(a);
        Event.add(a.target, "mousedown", a.onPointerDown);
        return d
    };
    Event.Gesture = Event.Gesture || {};
    Event.Gesture._gestureHandlers = Event.Gesture._gestureHandlers || {};
    Event.Gesture._gestureHandlers.tap = b.tap;
    Event.Gesture._gestureHandlers.longpress = b.longpress;
    return b
}
(Event.proxy);
"undefined" === typeof Event && (Event = {});
"undefined" === typeof Event.proxy && (Event.proxy = {});
Event.proxy = function (b) {
    b.wheel = function (a) {
        var b,
        e = a.timeout || 150,
        d = 0,
        k = {
            gesture: "wheel",
            state: "start",
            wheelDelta: 0,
            target: a.target,
            listener: a.listener,
            remove: function () {
                a.target[f](l, m, !1)
            }
        },
        m = function (f) {
            f = f || window.event;
            k.state = d++ ? "change" : "start";
            k.wheelDelta = f.detail ? -20 * f.detail : f.wheelDelta;
            a.listener(f, k);
            clearTimeout(b);
            b = setTimeout(function () {
                d = 0;
                k.state = "end";
                k.wheelDelta = 0;
                a.listener(f, k)
            }, e)
        },
        g = document.addEventListener ? "addEventListener" : "attachEvent",
        f = document.removeEventListener ?
            "removeEventListener" : "detachEvent",
        l = Event.supports("mousewheel") ? "mousewheel" : "DOMMouseScroll";
        a.target[g](l, m, !1);
        return k
    };
    Event.Gesture = Event.Gesture || {};
    Event.Gesture._gestureHandlers = Event.Gesture._gestureHandlers || {};
    Event.Gesture._gestureHandlers.wheel = b.wheel;
    return b
}
(Event.proxy);
function Stream(b) {
    function a() {
        var a = b.charCodeAt(c);
        c += 1;
        return a
    }
    var c = 0;
    return {
        eof: function () {
            return c >= b.length
        },
        read: function (a) {
            var d = b.substr(c, a);
            c += a;
            return d
        },
        readInt32: function () {
            var a = (b.charCodeAt(c) << 24) + (b.charCodeAt(c + 1) << 16) + (b.charCodeAt(c + 2) << 8) + b.charCodeAt(c + 3);
            c += 4;
            return a
        },
        readInt16: function () {
            var a = (b.charCodeAt(c) << 8) + b.charCodeAt(c + 1);
            c += 2;
            return a
        },
        readInt8: a,
        readVarInt: function () {
            for (var b = 0; ; ) {
                var d = a();
                if (d & 128)
                    b += d & 127, b <<= 7;
                else
                    return b + d
            }
        }
    }
}
function MidiFile(b) {
    function a(a) {
        var b = a.read(4),
        d = a.readInt32();
        return {
            id: b,
            length: d,
            data: a.read(d)
        }
    }
    function c(a) {
        var b = {};
        b.deltaTime = a.readVarInt();
        var d = a.readInt8();
        if (240 == (d & 240))
            if (255 == d) {
                b.type = "meta";
                var d = a.readInt8(),
                c = a.readVarInt();
                switch (d) {
                case 0:
                    b.subtype = "sequenceNumber";
                    if (2 != c)
                        throw "Expected length for sequenceNumber event is 2, got " + c;
                    b.number = a.readInt16();
                    return b;
                case 1:
                    return b.subtype = "text",
                    b.text = a.read(c),
                    b;
                case 2:
                    return b.subtype = "copyrightNotice",
                    b.text = a.read(c),
                    b;
                case 3:
                    return b.subtype = "trackName",
                    b.text = a.read(c),
                    b;
                case 4:
                    return b.subtype = "instrumentName",
                    b.text = a.read(c),
                    b;
                case 5:
                    return b.subtype = "lyrics",
                    b.text = a.read(c),
                    b;
                case 6:
                    return b.subtype = "marker",
                    b.text = a.read(c),
                    b;
                case 7:
                    return b.subtype = "cuePoint",
                    b.text = a.read(c),
                    b;
                case 32:
                    b.subtype = "midiChannelPrefix";
                    if (1 != c)
                        throw "Expected length for midiChannelPrefix event is 1, got " + c;
                    b.channel = a.readInt8();
                    return b;
                case 47:
                    b.subtype = "endOfTrack";
                    if (0 != c)
                        throw "Expected length for endOfTrack event is 0, got " +
                        c;
                    return b;
                case 81:
                    b.subtype = "setTempo";
                    if (3 != c)
                        throw "Expected length for setTempo event is 3, got " + c;
                    b.microsecondsPerBeat = (a.readInt8() << 16) + (a.readInt8() << 8) + a.readInt8();
                    return b;
                case 84:
                    b.subtype = "smpteOffset";
                    if (5 != c)
                        throw "Expected length for smpteOffset event is 5, got " + c;
                    d = a.readInt8();
                    b.frameRate = {
                        0: 24,
                        32: 25,
                        64: 29,
                        96: 30
                    }
                    [d & 96];
                    b.hour = d & 31;
                    b.min = a.readInt8();
                    b.sec = a.readInt8();
                    b.frame = a.readInt8();
                    b.subframe = a.readInt8();
                    return b;
                case 88:
                    b.subtype = "timeSignature";
                    if (4 != c)
                        throw "Expected length for timeSignature event is 4, got " +
                        c;
                    b.numerator = a.readInt8();
                    b.denominator = Math.pow(2, a.readInt8());
                    b.metronome = a.readInt8();
                    b.thirtyseconds = a.readInt8();
                    return b;
                case 89:
                    b.subtype = "keySignature";
                    if (2 != c)
                        throw "Expected length for keySignature event is 2, got " + c;
                    b.key = a.readInt8();
                    b.scale = a.readInt8();
                    return b;
                case 127:
                    return b.subtype = "sequencerSpecific",
                    b.data = a.read(c),
                    b;
                default:
                    return b.subtype = "unknown",
                    b.data = a.read(c),
                    b
                }
            } else {
                if (240 == d)
                    return b.type = "sysEx", c = a.readVarInt(), b.data = a.read(c), b;
                if (247 == d)
                    return b.type = "dividedSysEx",
                    c = a.readVarInt(), b.data = a.read(c), b;
                throw "Unrecognised MIDI event type byte: " + d;
            }
        else {
            0 == (d & 128) ? (c = d, d = e) : (c = a.readInt8(), e = d);
            var g = d >> 4;
            b.channel = d & 15;
            b.type = "channel";
            switch (g) {
            case 8:
                return b.subtype = "noteOff",
                b.noteNumber = c,
                b.velocity = a.readInt8(),
                b;
            case 9:
                return b.noteNumber = c,
                b.velocity = a.readInt8(),
                b.subtype = 0 == b.velocity ? "noteOff" : "noteOn",
                b;
            case 10:
                return b.subtype = "noteAftertouch",
                b.noteNumber = c,
                b.amount = a.readInt8(),
                b;
            case 11:
                return b.subtype = "controller",
                b.controllerType = c,
                b.value =
                    a.readInt8(),
                b;
            case 12:
                return b.subtype = "programChange",
                b.programNumber = c,
                b;
            case 13:
                return b.subtype = "channelAftertouch",
                b.amount = c,
                b;
            case 14:
                return b.subtype = "pitchBend",
                b.value = c + (a.readInt8() << 7),
                b;
            default:
                throw "Unrecognised MIDI event type: " + g;
            }
        }
    }
    var e;
    stream = Stream(b);
    b = a(stream);
    if ("MThd" != b.id || 6 != b.length)
        throw "Bad .mid file - header not found";
    var d = Stream(b.data);
    b = d.readInt16();
    var k = d.readInt16(),
    d = d.readInt16();
    if (d & 32768)
        throw "Expressing time division in SMTPE frames is not supported yet";
    ticksPerBeat = d;
    b = {
        formatType: b,
        trackCount: k,
        ticksPerBeat: ticksPerBeat
    };
    k = [];
    for (d = 0; d < b.trackCount; d++) {
        k[d] = [];
        var m = a(stream);
        if ("MTrk" != m.id)
            throw "Unexpected chunk - expected MTrk, got " + m.id;
        for (m = Stream(m.data); !m.eof(); ) {
            var g = c(m);
            k[d].push(g)
        }
    }
    return {
        header: b,
        tracks: k
    }
}
var clone = function (b) {
    if ("object" != typeof b || null == b)
        return b;
    var a = "number" == typeof b.length ? [] : {},
    c;
    for (c in b)
        a[c] = clone(b[c]);
    return a
};
function Replayer(b, a, c, e) {
    function d() {
        for (var a = null, d = null, c = null, e = 0; e < k.length; e++)
            null != k[e].ticksToNextEvent && (null == a || k[e].ticksToNextEvent < a) && (a = k[e].ticksToNextEvent, d = e, c = k[e].nextEventIndex);
        if (null != d) {
            var f = b.tracks[d][c];
            k[d].ticksToNextEvent = b.tracks[d][c + 1] ? k[d].ticksToNextEvent + b.tracks[d][c + 1].deltaTime : null;
            k[d].nextEventIndex += 1;
            for (e = 0; e < k.length; e++)
                null != k[e].ticksToNextEvent && (k[e].ticksToNextEvent -= a);
            return {
                ticksToEvent: a,
                event: f,
                track: d
            }
        }
        return null
    }
    var k = [],
    m = e ? e : 120,
    g = e ? !0 : !1,
    f = b.header.ticksPerBeat;
    for (c = 0; c < b.tracks.length; c++)
        k[c] = {
            nextEventIndex: 0,
            ticksToNextEvent: b.tracks[c].length ? b.tracks[c][0].deltaTime : null
        };
    var l,
    n = [];
    (function () {
        if (l = d())
            for (; l; ) {
                g || ("meta" != l.event.type || "setTempo" != l.event.subtype) || (m = 6E7 / l.event.microsecondsPerBeat);
                var b = 0,
                b = 0;
                0 < l.ticksToEvent && (b = l.ticksToEvent / f, b /= m / 60);
                n.push([l, 1E3 * b * a || 0]);
                l = d()
            }
    })();
    return {
        getData: function () {
            return clone(n)
        }
    }
}
(function (b) {
    function a(a) {
        return String.fromCharCode.apply(null, a)
    }
    function c(a, b) {
        if (b)
            for (; a.length / 2 < b; )
                a = "0" + a;
        for (var d = [], c = a.length - 1; 0 <= c; c -= 2)
            d.unshift(parseInt(0 === c ? a[c] : a[c - 1] + a[c], 16));
        return d
    }
    var e = Array.prototype;
    if (!b.console || !console.firebug) {
        var d = ["log", "debug", "info", "warn", "error"];
        b.console = {};
        for (var k = 0; k < d.length; ++k)
            b.console[d[k]] = function () {}
    }
    var m = {
        G9: 127,
        Gb9: 126,
        F9: 125,
        E9: 124,
        Eb9: 123,
        D9: 122,
        Db9: 121,
        C9: 120,
        B8: 119,
        Bb8: 118,
        A8: 117,
        Ab8: 116,
        G8: 115,
        Gb8: 114,
        F8: 113,
        E8: 112,
        Eb8: 111,
        D8: 110,
        Db8: 109,
        C8: 108,
        B7: 107,
        Bb7: 106,
        A7: 105,
        Ab7: 104,
        G7: 103,
        Gb7: 102,
        F7: 101,
        E7: 100,
        Eb7: 99,
        D7: 98,
        Db7: 97,
        C7: 96,
        B6: 95,
        Bb6: 94,
        A6: 93,
        Ab6: 92,
        G6: 91,
        Gb6: 90,
        F6: 89,
        E6: 88,
        Eb6: 87,
        D6: 86,
        Db6: 85,
        C6: 84,
        B5: 83,
        Bb5: 82,
        A5: 81,
        Ab5: 80,
        G5: 79,
        Gb5: 78,
        F5: 77,
        E5: 76,
        Eb5: 75,
        D5: 74,
        Db5: 73,
        C5: 72,
        B4: 71,
        Bb4: 70,
        A4: 69,
        Ab4: 68,
        G4: 67,
        Gb4: 66,
        F4: 65,
        E4: 64,
        Eb4: 63,
        D4: 62,
        Db4: 61,
        C4: 60,
        B3: 59,
        Bb3: 58,
        A3: 57,
        Ab3: 56,
        G3: 55,
        Gb3: 54,
        F3: 53,
        E3: 52,
        Eb3: 51,
        D3: 50,
        Db3: 49,
        C3: 48,
        B2: 47,
        Bb2: 46,
        A2: 45,
        Ab2: 44,
        G2: 43,
        Gb2: 42,
        F2: 41,
        E2: 40,
        Eb2: 39,
        D2: 38,
        Db2: 37,
        C2: 36,
        B1: 35,
        Bb1: 34,
        A1: 33,
        Ab1: 32,
        G1: 31,
        Gb1: 30,
        F1: 29,
        E1: 28,
        Eb1: 27,
        D1: 26,
        Db1: 25,
        C1: 24,
        B0: 23,
        Bb0: 22,
        A0: 21,
        Ab0: 20,
        G0: 19,
        Gb0: 18,
        F0: 17,
        E0: 16,
        Eb0: 15,
        D0: 14,
        Db0: 13,
        C0: 12
    },
    g = function (a) {
        if (!a || null === a.type && void 0 === a.type || null === a.channel && void 0 === a.channel || null === a.param1 && void 0 === a.param1)
            throw Error("Not enough parameters to create an event.");
        this.setTime(a.time);
        this.setType(a.type);
        this.setChannel(a.channel);
        this.setParam1(a.param1);
        this.setParam2(a.param2)
    };
    g.createNote = function (a, b) {
        if (!a)
            throw Error("Note not specified");
        if ("string" === typeof a)
            a = m[a];
        else if (!a.pitch)
            throw Error("The pitch is required in order to create a note.");
        var d = [];
        d.push(g.noteOn(a));
        b || d.push(g.noteOff(a, a.duration || 128));
        return d
    };
    g.noteOn = function (a, b) {
        return new g({
            time: a.duration || b || 0,
            type: 9,
            channel: a.channel || 0,
            param1: a.pitch || a,
            param2: a.volume || 90
        })
    };
    g.noteOff = function (a, b) {
        return new g({
            time: a.duration || b || 0,
            type: 8,
            channel: a.channel || 0,
            param1: a.pitch || a,
            param2: a.volume || 90
        })
    };
    g.prototype = {
        type: 0,
        channel: 0,
        time: 0,
        setTime: function (a) {
            var b =
                a || 0;
            for (a = b & 127; b >>= 7; )
                a <<= 8, a |= b & 127 | 128;
            for (b = []; ; )
                if (b.push(a & 255), a & 128)
                    a >>= 8;
                else
                    break;
            this.time = b
        },
        setType: function (a) {
            if (8 > a || 14 < a)
                throw Error("Trying to set an unknown event: " + a);
            this.type = a
        },
        setChannel: function (a) {
            if (0 > a || 15 < a)
                throw Error("Channel is out of bounds.");
            this.channel = a
        },
        setParam1: function (a) {
            this.param1 = a
        },
        setParam2: function (a) {
            this.param2 = a
        },
        toBytes: function () {
            var a = [],
            b = parseInt(this.type.toString(16) + this.channel.toString(16), 16);
            a.push.apply(a, this.time);
            a.push(b);
            a.push(this.param1);
            void 0 !== this.param2 && null !== this.param2 && a.push(this.param2);
            return a
        }
    };
    var f = function (a) {
        a && (this.setType(a.type), this.setData(a.data))
    };
    f.prototype = {
        setType: function (a) {
            this.type = a
        },
        setData: function (a) {
            this.data = a
        },
        toBytes: function () {
            if (!this.type || !this.data)
                throw Error("Type or data for meta-event not specified.");
            var a = [255, this.type];
            this.data && (this.data.concat && this.data.unshift && !this.data.callee) && e.push.apply(a, this.data);
            return a
        }
    };
    var l = function (a) {
        this.events = [];
        for (var b in a)
            if (a.hasOwnProperty(b))
                this["set" +
                    b.charAt(0).toUpperCase() + b.substring(1)](a[b])
    };
    l.TRACK_START = [77, 84, 114, 107];
    l.TRACK_END = [0, 255, 47, 0];
    l.prototype = {
        addEvent: function (a) {
            this.events.push(a);
            return this
        },
        setEvents: function (a) {
            e.push.apply(this.events, a);
            return this
        },
        setText: function (a, b) {
            b || (b = a = 1);
            return this.addEvent(new f({
                    type: a,
                    data: b
                }))
        },
        setCopyright: function (a) {
            return this.setText(2, a)
        },
        setTrackName: function (a) {
            return this.setText(3, a)
        },
        setInstrument: function (a) {
            return this.setText(4, a)
        },
        setLyric: function (a) {
            return this.setText(5,
                a)
        },
        setMarker: function (a) {
            return this.setText(6, a)
        },
        setCuePoint: function (a) {
            return this.setText(7, a)
        },
        setTempo: function (a) {
            this.addEvent(new f({
                    type: 81,
                    data: a
                }))
        },
        setTimeSig: function () {},
        setKeySig: function () {},
        toBytes: function () {
            var a = 0,
            b = [],
            d = l.TRACK_START,
            f = l.TRACK_END;
            this.events.forEach(function (d) {
                d = d.toBytes();
                a += d.length;
                e.push.apply(b, d)
            });
            var a = a + f.length,
            g = c(a.toString(16), 4);
            return d.concat(g, b, f)
        }
    };
    b.MidiWriter = function (d) {
        if (d) {
            d = d.tracks || [];
            var e = d.length.toString(16),
            f = "MThd\x00\x00\x00\u0006\x00\x00",
            f = f + a(c(e, 2)),
            f = f + "\u0001\u0090";
            d.forEach(function (b) {
                f += a(b.toBytes())
            });
            return {
                b64: btoa(f),
                play: function () {
                    if (document) {
                        var a = document.createElement("embed");
                        a.setAttribute("src", "data:audio/midi;base64," + this.b64);
                        a.setAttribute("type", "audio/midi");
                        document.body.appendChild(a)
                    }
                },
                save: function () {
                    b.open("data:audio/midi;base64," + this.b64, "JSMidi generated output", "resizable=yes,scrollbars=no,status=no")
                }
            }
        }
        throw Error("No parameters have been passed to MidiWriter.");
    };
    b.MidiEvent = g;
    b.MetaEvent =
        f;
    b.MidiTrack = l;
    b.noteTable = m
})(jsmidi = {});
(function (b) {
    b.btoa || (b.btoa = function (a) {
        a = escape(a);
        var b = "",
        e,
        d,
        k = "",
        m,
        g,
        f = "",
        l = 0;
        do
            e = a.charCodeAt(l++), d = a.charCodeAt(l++), k = a.charCodeAt(l++), m = e >> 2, e = (e & 3) << 4 | d >> 4, g = (d & 15) << 2 | k >> 6, f = k & 63, isNaN(d) ? g = f = 64 : isNaN(k) && (f = 64), b = b + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".charAt(m) + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".charAt(e) + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".charAt(g) + "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".charAt(f);
        while (l < a.length);
        return b
    });
    b.atob || (b.atob = function (a) {
        var b = "",
        e,
        d,
        k = "",
        m,
        g = "",
        f = 0;
        /[^A-Za-z0-9\+\/\=]/g.exec(a) && alert("There were invalid base64 characters in the input text.\nValid base64 characters are A-Z, a-z, 0-9, '+', '/',and '='\nExpect errors in decoding.");
        a = a.replace(/[^A-Za-z0-9\+\/\=]/g, "");
        do
            e = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".indexOf(a.charAt(f++)), d = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".indexOf(a.charAt(f++)), m = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".indexOf(a.charAt(f++)),
            g = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=".indexOf(a.charAt(f++)), e = e << 2 | d >> 4, d = (d & 15) << 4 | m >> 2, k = (m & 3) << 6 | g, b += String.fromCharCode(e), 64 != m && (b += String.fromCharCode(d)), 64 != g && (b += String.fromCharCode(k));
        while (f < a.length);
        return unescape(b)
    })
})(this);
String.prototype.replaceAll = function (b, a) {
    if ("object" === typeof b) {
        for (var c = this, e = 0; e < b.length; e++)
            c = c.split(b[e]).join(a[e]);
        return c
    }
    return this.split(b).join(a)
};
String.prototype.trim = function (b) {
    return this.replace(/^\s+|\s+$/g, "")
};
String.prototype.ucfirst = function (b) {
    return this[0].toUpperCase() + this.substr(1)
};
String.prototype.ucwords = function (b) {
    return this.replace(/^(.)|\s(.)/g, function (a) {
        return a.toUpperCase()
    })
};
String.prototype.addslashes = function () {
    return this.replace(/([\\"'])/g, "\\$1").replace(/\0/g, "\\0")
};
String.prototype.stripslashes = function () {
    return this.replace(/\0/g, "0").replace(/\\([\\'"])/g, "$1")
};
String.prototype.basename = function () {
    return this.replace(/\\/g, "/").replace(/.*\//, "")
};
String.prototype.lpad = function (b, a) {
    for (var c = this; c.length < a; )
        c = b + c;
    return c
};
String.prototype.rpad = function (b, a) {
    for (var c = this; c.length < a; )
        c += b;
    return c
};
window.STRING = String;
STRING.prototype.replaceAll = STRING.prototype.replaceAll;
STRING.prototype.trim = STRING.prototype.trim;
STRING.prototype.ucfirst = STRING.prototype.ucfirst;
STRING.prototype.ucwords = STRING.prototype.ucwords;
STRING.prototype.addslashes = STRING.prototype.addslashes;
STRING.prototype.stripslashes = STRING.prototype.stripslashes;
STRING.prototype.basename = STRING.prototype.basename;
STRING.prototype.lpad = STRING.prototype.lpad;
STRING.prototype.rpad = STRING.prototype.rpad;
window.localStorage || (window.localStorage = {
        getItem: function (b) {
            return b && this.hasOwnProperty(b) ? unescape(document.cookie.replace(RegExp("(?:^|.*;\\s*)" + escape(b).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=\\s*((?:[^;](?!;))*[^;]?).*"), "$1")) : null
        },
        key: function (b) {
            return unescape(document.cookie.replace(/\s*\=(?:.(?!;))*$/, "").split(/\s*\=(?:[^;](?!;))*[^;]?;\s*/)[b])
        },
        setItem: function (b, a) {
            b && (document.cookie = escape(b) + "=" + escape(a) + "; path=/", this.length = document.cookie.match(/\=/g).length)
        },
        length: document.cookie.match(/\=/g).length,
        removeItem: function (b) {
            if (b && this.hasOwnProperty(b)) {
                var a = new Date;
                a.setDate(a.getDate() - 1);
                document.cookie = escape(b) + "=; expires=" + a.toGMTString() + "; path=/";
                this.length--
            }
        },
        hasOwnProperty: function (b) {
            return RegExp("(?:^|;\\s*)" + escape(b).replace(/[\-\.\+\*]/g, "\\$&") + "\\s*\\=").test(document.cookie)
        }
    });
var Base64Binary = {
    _keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
    decodeArrayBuffer: function (b) {
        var a = Math.ceil(3 * b.length / 4),
        a = new ArrayBuffer(a);
        this.decode(b, a);
        return a
    },
    decode: function (b, a) {
        var c = this._keyStr.indexOf(b.charAt(b.length - 1)),
        e = this._keyStr.indexOf(b.charAt(b.length - 1)),
        d = Math.ceil(3 * b.length / 4);
        64 == c && d--;
        64 == e && d--;
        var k,
        m,
        g,
        f,
        l = 0,
        n = 0,
        c = a ? new Uint8Array(a) : new Uint8Array(d);
        b = b.replace(/[^A-Za-z0-9\+\/\=]/g, "");
        for (l = 0; l < d; l += 3)
            k = this._keyStr.indexOf(b.charAt(n++)),
            m = this._keyStr.indexOf(b.charAt(n++)), e = this._keyStr.indexOf(b.charAt(n++)), f = this._keyStr.indexOf(b.charAt(n++)), k = k << 2 | m >> 4, m = (m & 15) << 4 | e >> 2, g = (e & 3) << 6 | f, c[l] = k, 64 != e && (c[l + 1] = m), 64 != f && (c[l + 2] = g);
        return c
    }
};
"use strict";
var self = this;
self.URL = self.URL || self.webkitURL;
self.requestFileSystem = self.requestFileSystem || self.webkitRequestFileSystem;
self.resolveLocalFileSystemURL = self.resolveLocalFileSystemURL || self.webkitResolveLocalFileSystemURL;
navigator.temporaryStorage = navigator.temporaryStorage || navigator.webkitTemporaryStorage;
navigator.persistentStorage = navigator.persistentStorage || navigator.webkitPersistentStorage;
self.BlobBuilder = self.BlobBuilder || self.MozBlobBuilder || self.WebKitBlobBuilder;
if (void 0 === self.FileError) {
    var FileError = function () {};
    FileError.prototype.prototype = Error.prototype
}
var Util = {
    toArray: function (b) {
        return Array.prototype.slice.call(b || [], 0)
    },
    strToDataURL: function (b, a, c) {
        return (void 0 != c ? c : 1) ? "data:" + a + ";base64," + self.btoa(b) : "data:" + a + "," + b
    },
    strToObjectURL: function (b, a) {
        for (var c = new Uint8Array(b.length), e = 0; e < c.length; ++e)
            c[e] = b.charCodeAt(e);
        c = new Blob([c], a ? {
            type: a
        }
                 : {});
        return self.URL.createObjectURL(c)
    },
    fileToObjectURL: function (b) {
        return self.URL.createObjectURL(b)
    },
    fileToArrayBuffer: function (b, a, c) {
        var e = new FileReader;
        e.onload = function (b) {
            a(b.target.result)
        };
        e.onerror = function (a) {
            c && c(a)
        };
        e.readAsArrayBuffer(b)
    },
    dataURLToBlob: function (b) {
        if (-1 == b.indexOf(";base64,")) {
            var a = b.split(",");
            b = a[0].split(":")[1];
            a = decodeURIComponent(a[1]);
            return new Blob([a], {
                type: b
            })
        }
        a = b.split(";base64,");
        b = a[0].split(":")[1];
        for (var a = window.atob(a[1]), c = a.length, e = new Uint8Array(c), d = 0; d < c; ++d)
            e[d] = a.charCodeAt(d);
        return new Blob([e], {
            type: b
        })
    },
    arrayBufferToBlob: function (b, a) {
        var c = new Uint8Array(b);
        return new Blob([c], a ? {
            type: a
        }
             : {})
    },
    arrayBufferToBinaryString: function (b,
        a, c) {
        var e = new FileReader;
        e.onload = function (b) {
            a(b.target.result)
        };
        e.onerror = function (a) {
            c && c(a)
        };
        b = new Uint8Array(b);
        e.readAsBinaryString(new Blob([b]))
    },
    arrayToBinaryString: function (b) {
        if ("object" != typeof b)
            return null;
        for (var a = b.length, c = Array(a); a--; )
            c[a] = String.fromCharCode(b[a]);
        return c.join("")
    },
    getFileExtension: function (b) {
        var a = b.lastIndexOf(".");
        return -1 != a ? b.substring(a) : ""
    }
}, MyFileError = function (b) {
    this.prototype = FileError.prototype;
    this.code = b.code;
    this.name = b.name
};
FileError.BROWSER_NOT_SUPPORTED = 1E3;
FileError.prototype.__defineGetter__("name", function () {
    for (var b = Object.keys(FileError), a = 0, c; c = b[a]; ++a)
        if (FileError[c] == this.code)
            return c;
    return "Unknown Error"
});
var Filer = new function () {
    function b(b) {
        if (a = b || null)
            c = a.root, e = !0
    }
    var a = null,
    c = null,
    e = !1,
    d = function (b) {
        0 != b.indexOf("filesystem:") && (b = "/" == b[0] ? a.root.toURL() + b.substring(1) : 0 == b.indexOf("./") || 0 == b.indexOf("../") ? "../" == b && c != a.root ? c.toURL() + "/" + b : c.toURL() + b : c.toURL() + "/" + b);
        return b
    },
    k = function (a, b) {
        var c = arguments[1],
        e = arguments[2],
        k = function (a) {
            if (a.code == FileError.NOT_FOUND_ERR) {
                if (e)
                    throw Error('"' + c + '" or "' + e + '" does not exist.');
                throw Error('"' + c + '" does not exist.');
            }
            throw Error("Problem getting Entry for one or more paths.");
        },
        m = d(c);
        if (3 == arguments.length) {
            var p = d(e);
            self.resolveLocalFileSystemURL(m, function (b) {
                self.resolveLocalFileSystemURL(p, function (d) {
                    a(b, d)
                }, k)
            }, k)
        } else
            self.resolveLocalFileSystemURL(m, a, k)
    },
    m = function (b, d, c, e, m, q) {
        if (!a)
            throw Error("Filesystem has not been initialized.");
        if (typeof b != typeof d)
            throw Error("These method arguments are not supported.");
        var p = c || null,
        s = void 0 != q ? q : !1;
        (b.isFile || d.isDirectory) && d.isDirectory ? s ? b.moveTo(d, p, e, m) : b.copyTo(d, p, e, m) : k(function (a, b) {
            if (b.isDirectory)
                s ? a.moveTo(b,
                    p, e, m) : a.copyTo(b, p, e, m);
            else {
                var d = Error('Oops! "' + b.name + " is not a directory!");
                if (m)
                    m(d);
                else
                    throw d;
            }
        }, b, d)
    };
    b.DEFAULT_FS_SIZE = 1048576;
    b.version = "0.4.3";
    b.prototype = {
        get fs() {
            return a
        },
        get isOpen() {
            return e
        },
        get cwd() {
            return c
        }
    };
    b.prototype.pathToFilesystemURL = function (a) {
        return d(a)
    };
    b.prototype.init = function (b, d, k) {
        if (!self.requestFileSystem)
            throw new MyFileError({
                code: FileError.BROWSER_NOT_SUPPORTED,
                name: "BROWSER_NOT_SUPPORTED"
            });
        b = b ? b : {};
        var m = b.size || 1048576;
        this.type = self.TEMPORARY;
        "persistent" in
        b && b.persistent && (this.type = self.PERSISTENT);
        var r = function (b) {
            this.size = m;
            a = b;
            c = a.root;
            e = !0;
            d && d(b)
        };
        this.type == self.PERSISTENT && navigator.persistentStorage ? navigator.persistentStorage.requestQuota(m, function (a) {
            self.requestFileSystem(this.type, a, r.bind(this), k)
        }
            .bind(this), k) : self.requestFileSystem(this.type, m, r.bind(this), k)
    };
    b.prototype.ls = function (b, d, e) {
        if (!a)
            throw Error("Filesystem has not been initialized.");
        var m = function (a) {
            c = a;
            var b = [],
            g = c.createReader(),
            k = function () {
                g.readEntries(function (a) {
                    a.length ?
                    (b = b.concat(Util.toArray(a)), k()) : (b.sort(function (a, b) {
                            return a.name < b.name ? -1 : b.name < a.name ? 1 : 0
                        }), d(b))
                }, e)
            };
            k()
        };
        b.isDirectory ? m(b) : 0 == b.indexOf("filesystem:") ? k(m, b) : c.getDirectory(b, {}, m, e)
    };
    b.prototype.mkdir = function (b, d, e, k) {
        if (!a)
            throw Error("Filesystem has not been initialized.");
        var m = null != d ? d : !1,
        q = b.split("/"),
        p = function (a, d) {
            if ("." == d[0] || "" == d[0])
                d = d.slice(1);
            a.getDirectory(d[0], {
                create: !0,
                exclusive: m
            }, function (a) {
                if (a.isDirectory)
                    d.length && 1 != q.length ? p(a, d.slice(1)) : e && e(a);
                else if (a =
                        Error(b + " is not a directory"), k)
                    k(a);
                else
                    throw a;
            }, function (a) {
                if (a.code == FileError.INVALID_MODIFICATION_ERR)
                    if (a.message = "'" + b + "' already exists", k)
                        k(a);
                    else
                        throw a;
            })
        };
        p(c, q)
    };
    b.prototype.open = function (b, c, e) {
        if (!a)
            throw Error("Filesystem has not been initialized.");
        b.isFile ? b.file(c, e) : k(function (a) {
            a.file(c, e)
        }, d(b))
    };
    b.prototype.create = function (b, d, e, k) {
        if (!a)
            throw Error("Filesystem has not been initialized.");
        c.getFile(b, {
            create: !0,
            exclusive: null != d ? d : !0
        }, e, function (a) {
            a.code == FileError.INVALID_MODIFICATION_ERR &&
            (a.message = "'" + b + "' already exists");
            if (k)
                k(a);
            else
                throw a;
        })
    };
    b.prototype.mv = function (a, b, d, c, e) {
        m.bind(this, a, b, d, c, e, !0)()
    };
    b.prototype.rm = function (b, d, c) {
        if (!a)
            throw Error("Filesystem has not been initialized.");
        var e = function (a) {
            a.isFile ? a.remove(d, c) : a.isDirectory && a.removeRecursively(d, c)
        };
        b.isFile || b.isDirectory ? e(b) : k(e, b)
    };
    b.prototype.cd = function (b, e, l) {
        if (!a)
            throw Error("Filesystem has not been initialized.");
        b.isDirectory ? (c = b, e && e(c)) : (b = d(b), k(function (a) {
                if (a.isDirectory)
                    c = a, e && e(c);
                else if (a = Error("Path was not a directory."), l)
                    l(a);
                else
                    throw a;
            }, b))
    };
    b.prototype.cp = function (a, b, d, c, e) {
        m.bind(this, a, b, d, c, e)()
    };
    b.prototype.write = function (b, d, e, m) {
        if (!a)
            throw Error("Filesystem has not been initialized.");
        var r = function (a) {
            a.createWriter(function (b) {
                b.onerror = m;
                if (d.append)
                    b.onwriteend = function (b) {
                        e && e(a, this)
                    },
                b.seek(b.length);
                else {
                    var c = !1;
                    b.onwriteend = function (b) {
                        c ? e && e(a, this) : (c = !0, this.truncate(this.position))
                    }
                }
                d.data.__proto__ == ArrayBuffer.prototype && (d.data = new Uint8Array(d.data));
                var k = new Blob([d.data], d.type ? {
                    type: d.type
                }
                         : {});
                b.write(k)
            }, m)
        };
        b.isFile ? r(b) : 0 == b.indexOf("filesystem:") ? k(r, b) : c.getFile(b, {
            create: !0,
            exclusive: !1
        }, r, m)
    };
    b.prototype.df = function (a, b) {
        var d = function (b, d) {
            a(b, d - b, d)
        };
        if (!navigator.temporaryStorage.queryUsageAndQuota || !navigator.persistentStorage.queryUsageAndQuota)
            throw Error("Not implemented.");
        self.TEMPORARY == this.type ? navigator.temporaryStorage.queryUsageAndQuota(d, b) : self.PERSISTENT == this.type && navigator.persistentStorage.queryUsageAndQuota(d,
            b)
    };
    return b
};
"undefined" === typeof localStorage && (localStorage = {});
if ("undefined" === typeof Piano)
    var Piano = {};
"undefined" === typeof MIDI && (MIDI = {
        Player: {}
    });
var loader, canvas = {}, host = "chrome-extension:" === window.location.protocol ? "chrome-extension://" + window.location.host : "https://galactic.ink/piano";
(function (b) {
    Piano.width = 990;
    Piano.chordLock = !1;
    Piano.interval = 0;
    Piano.scaleObj = [];
    Piano.keySignature = [];
    Piano.notes = {};
    Piano.blackKeys = {
        1: !0,
        4: !0,
        6: !0,
        9: !0,
        11: !0
    };
    Piano.channel = 0;
    Piano.tempo = 250;
    Piano.inversion = 0;
    Piano.key = 3;
    Piano.octave = 3;
    Piano.HSL = localStorage.HSL || "D. D. Jameson (1844)";
    Piano.instrument = "Piano";
    Piano.chord = "Major";
    Piano.scale = "Aeolian";
    Piano.keys = [];
    Piano.offsetLeft = -14;
    Piano.timeWarp = parseFloat(localStorage.timeWarp || 1);
    Piano.labelKey = !0;
    Piano.visualize = localStorage.visualize ||
        "preview";
    Piano.labelType = "signature";
    Piano.setAnimation = function () {};
    Piano.MIDIPlayerPercentage = function () {
        function a(b) {
            var d = b / 60 >> 0;
            b = String(b - 60 * d >> 0);
            1 == b.length && (b = "0" + b);
            return d + ":" + b
        }
        var b = MIDI.Player,
        d = document.getElementById("capsule"),
        k = document.getElementById("cursor"),
        m = document.getElementById("time2");
        Event.add(d, "drag", function (a, d) {
            var c = MIDI.Player.endTime;
            b.currentTime = d.x / 220 * c;
            b.currentTime = Math.max(-Piano.width, b.currentTime);
            b.currentTime = Math.min(c, b.currentTime);
            b.restart =
                Math.max(0, Math.min(c, b.currentTime));
            "down" === d.state ? (isPlaying = b.playing, b.pause()) : "up" === d.state && isPlaying && Piano.resume();
            Piano.Animation.animate(!0);
            Piano.genTimeCursor()
        });
        Piano.genTimeCursor = function () {
            var b = MIDI.Player.endTime,
            d = MIDI.Player.currentTime,
            e = d / 1E3,
            n = e / 60;
            k.style.width = 100 * (d / b) + "%";
            m.innerHTML = "-" + a(b / 1E3 - (60 * n + (e - 60 * n)))
        };
        Piano.setAnimation = function () {
            b.clearAnimation();
            b.setAnimation(function (b, d) {
                var e = b.now >> 0,
                n = b.end >> 0;
                k.style.width = 100 * (b.now / b.end) + "%";
                m.innerHTML =
                    "-" + a(n - e);
                Piano.Animation.animate()
            })
        };
        Piano.genTimeCursor();
        MIDI.UI.enableView()
    };
    Piano.getNextSong = function (a) {
        var b = MIDI.Player;
        a = Math.abs((Piano.fileID += a) % Piano.filesArray.length);
        a = Piano.filesArray[a];
        var d = a.split("/").pop().replaceAll("%20", " "),
        k = MIDI.Player.playing;
        loader.update(null, "&lt;loading&gt;<br>" + d);
        Piano.loadFile(a, function (a) {
            Piano.Animation.scrollTop = 0;
            Piano.setAnimation();
            b.renderScreen();
            loader.stop();
            k && (MIDI.UI.togglePlayer(!0), b.resume())
        })
    };
    Piano.loadPlugin = function () {
        MIDI.loadPlugin(function () {
            var b =
                0,
            e = {},
            d;
            for (d in Piano.files)
                e[b] = d, b++;
            if ("#http" === window.location.hash.substr(0, 5))
                Piano.loadExternalMIDI(window.location.hash.substr(1));
            else {
                if ("#random" === window.location.hash)
                    Piano.midifile = e[Math.random() * b >> 0];
                else if (Piano.midifile = localStorage.midifile, !Piano.midifile || !Piano.files[Piano.midifile] && null !== Piano.files[Piano.midifile])
                    Piano.midifile = "Tchaikovsky - Dance of the Reed Flutes (Nutcracker).mid";
                Piano.loadFile(Piano.midifile, function () {
                    Piano.play();
                    Piano.MIDIPlayerPercentage(MIDI.Player);
                    a()
                })
            }
            "Java" == MIDI.lang && (MIDI.setVolume(Piano.channel, 100), Piano.drawInstruments());
            document.getElementById("control-play").onclick = MIDI.UI.togglePlayer;
            document.getElementById("control-backward").onclick = function () {
                Piano.getNextSong(-1)
            };
            document.getElementById("control-forward").onclick = function () {
                Piano.getNextSong(1)
            };
            MIDI.UI.drawTimeWarp();
            MIDI.UI.drawSynesthesia();
            Piano.filesArray = [];
            for (d in Piano.files)
                d === Piano.midifile && (Piano.fileID = Piano.filesArray.length), Piano.filesArray.push(d)
        })
    };
    Piano.loadFile = function (a, e) {
        b.clearNotes();
        if (a)
            b.midifile = a, Piano.loadExternalMIDI(b.midifile, e, host + "/audio/");
        else if (!MIDI.Player.replayer) {
            var d = Piano.files[b.midifile];
            MIDI.Player.loadFile(d, function (a) {
                var b = d.split(" - ")[1] || d;
                document.getElementById("playback-title").innerHTML = b.replace(".mid", "");
                e && e(a)
            });
            MIDI.Player.stop();
            b.clearNotes();
            b.Animation.callback(!0)
        }
    };
    Piano.loadExternalMIDI = function (c, e, d) {
        Piano.loadExternalMIDICallback = function (d) {
            Piano.files[m] = d;
            MIDI.Player.loadFile(d,
                function (d) {
                d = d.split(" - ")[1] || c;
                document.getElementById("playback-title").innerHTML = d.replace(".mid", "");
                localStorage.setItem("midifile", m);
                window.requestFileSystem && Piano.files[m] && filer.write("/audio/" + m.replace(".midi", "").replace(".mid", ""), {
                    data: Piano.files[m],
                    type: "txt"
                });
                if (d = document.getElementById("tools"))
                    d.parentNode.style.display = "none";
                loader && loader.stop();
                e && e();
                b.clearNotes();
                a()
            })
        };
        var k = function () {
            loader.update(null, "&lt;downloading&gt;<br>" + f);
            Piano.files[m] ? Piano.loadExternalMIDICallback(Piano.files[m]) :
            null === Piano.files[m] ? "chrome-extension:" === window.location.protocol ? Piano.loadExternalMIDICallback(host + "/audio/" + m) : DOMLoader.script.add({
                src: "https://galactic.ink/piano/midi-to-json.php?query=" + encodeURIComponent(m)
            }) : DOMLoader.script.add({
                src: "https://midi-to-json.appspot.com/" + g.split("//")[1]
            })
        };
        c || (c = document.getElementById("load-external-midi").value);
        e || (e = Piano.play);
        var m = c.basename(),
        g = decodeURIComponent(d + c),
        f = g.split(" - ")[1] || g;
        "http" !== g.substr(0, 4) && (g = "http://" + g);
        document.getElementById("playback-title").innerHTML =
            f.replace(".midi", "").replace(".mid", "");
        if (window.requestFileSystem)
            return filer.ls("/audio", function (a) {
                for (var b = m.replace(".midi", "").replace(".mid", ""), d = 0; d < a.length; d++)
                    if (a[d].name === b)
                        return filer.open("/audio/" + a[d].name, function (a) {
                            var b = new FileReader;
                            b.onload = function (b) {
                                b = b.target.result;
                                Piano.files[m] = b;
                                localStorage.setItem("midifile", m);
                                b = window.atob(b.split(",").pop());
                                var d = MIDI.Player.playing;
                                MIDI.Player.stop();
                                MIDI.Player.loadFile(b, function () {
                                    var b = a.name;
                                    document.getElementById("playback-title").innerHTML =
                                        b.replace(".mid", "");
                                    e && e();
                                    d && MIDI.Player.start();
                                    Piano.play();
                                    loader.stop()
                                })
                            };
                            b.readAsDataURL(a)
                        });
                k()
            });
        k()
    };
    var a = function () {
        DOM.dimensions();
        var a = window.innerHeight;
        Piano.height = a - 103 - 50;
        document.body.style.height = a + "px";
        "undefined" === typeof CanvasRender && (CanvasRender = {}, CanvasRender[0] = document.createElement("canvas"), CanvasRender[1] = document.createElement("canvas"), CanvasRender.overlay = document.createElement("canvas"), Piano.debug && (CanvasRender[0].style.background = "rgba(0,0,255,0.25)", CanvasRender[1].style.background =
                    "rgba(255,0,0,0.25)"));
        var a = Piano.height,
        b = Piano.width;
        CanvasRender.overlay.width = b;
        CanvasRender.overlay.height = a;
        CanvasRender[0].id = "render0";
        CanvasRender[0].width = b;
        CanvasRender[0].height = a;
        CanvasRender[1].width = b;
        CanvasRender[1].height = a;
        CanvasRender[1].id = "render1";
        "undefined" !== typeof MIDI.Player.replayer && Piano.Animation.boot();
        MIDI.Player.renderScreen();
        a = CanvasRender.overlay.getContext("2d");
        for (b = 0; 88 > b; b++)
            a.beginPath(), a.moveTo(88 * Piano.stretchX - b * Piano.stretchX + 0.5, 0), a.lineTo(88 * Piano.stretchX -
                b * Piano.stretchX + 0.5, CanvasRender[0].height), a.strokeStyle = 0 == (b + 5) % 7 ? "rgba(255,255,255,0.15)" : "rgba(255,255,255,0.1)", a.stroke();
        if (a = document.getElementById("file-browser"))
            a.style.height = window.innerHeight + "px", a.style.width = window.innerWidth + "px"
    };
    Event.add("body", "ready", function () {
        var b = document.createElement("script");
        b.type = "text/javascript";
        b.src = "https://chrome.google.com/webstore/widget/developer/scripts/widget.js";
        document.head.appendChild(b);
        Event.add(".tools", "mousedown", function (a) {
            MIDI.UI.enableConfigure(!1)
        });
        Event.add("#tools", "mousedown", function (a) {
            Event.stop(a)
        });
        Event.add("#tempo-from-tap", "mousedown", function (a) {
            MusicTheory.tempoFromTap(this)
        });
        Event.add("#playback-title", "click", Piano.fileBrowserToggle);
        Event.add("#theory img", "click", function (a) {
            Piano.func()
        });
        Event.add("#open", "click", Piano.fileBrowserToggle);
        Event.add("#view-song", "click", function (a) {
            Piano.songViewToggle(this)
        });
        Event.add("#configure", "click", function (a) {
            MIDI.UI.enableConfigure(!0)
        });
        Event.add("#find-chord", "click", function (a) {
            MusicTheory.findChord(Piano.chords.tri)
        });
        Event.add("#load-external-midi", "click", Piano.loadExternalMIDI);
        "undefined" !== typeof widgets.Loader && (MIDI.loader = loader = new widgets.Loader);
        a();
        MIDI.Player.timeWarp = Piano.timeWarp;
        b = document.createElement("link");
        b.href = "https://fonts.googleapis.com/css?family=Andada";
        b.rel = "stylesheet";
        b.type = "text/css";
        document.getElementsByTagName("head")[0].appendChild(b);
        b = document.getElementById("container");
        Event.add(b, "contextmenu", function (a) {
            Event.prevent(a)
        });
        canvas.animate = document.getElementById("animate");
        canvas.bg = document.getElementById("piano_bg");
        canvas.black = document.getElementById("black_keys").getContext("2d");
        canvas.white = document.getElementById("white_keys").getContext("2d");
        canvas.bg.height = Piano.Glyphs.whiteKey.canvas.height + 23;
        MusicTheory.getKeySignature("C");
        Piano.loadPlugin();
        Piano.colorMap = MusicTheory.Synesthesia.map(Piano.HSL);
        Piano.drawKeyboard();
        MIDI.UI.enableView(!0);
        MIDI.Player.addListener(function (a) {
            var b = a.note - Piano.MIDINoteOffset,
            c = 144 === a.message;
            Piano.trackNote(a.channel,
                b, c);
            Piano.drawKeyLabel(b, c);
            Piano.Animation.callback(b, c)
        });
        Piano.uploader = new widgets.Uploader({
            callback: function (a, b, c) {
                if (b) {
                    for (var m in b);
                    if (b[m]) {
                        a = MIDI.Player.playing;
                        var g = b[m].src;
                        MIDI.Player.stop();
                        MIDI.Player.loadFile(g, function (a) {
                            var b = g.split(" - ")[1] || g;
                            document.getElementById("playback-title").innerHTML = b.replace(".mid", "");
                            callback && callback(a)
                        });
                        a && window.setTimeout(MIDI.Player.start, 100)
                    }
                }
            },
            formats: {
                "audio/mid": !0,
                "audio/midi": !0
            }
        });
        Piano.fileBrowser();
        fileSaver = new widgets.FileSaver;
        filer = new Filer;
        window.requestFileSystem && filer.init({
            persistent: !1,
            size: 104857600
        }, function (a) {
            filer.pathToFilesystemURL("/");
            filer.mkdir("./soundfont");
            filer.mkdir("./audio")
        }, function (a) {
            window.requestFileSystem = !1
        })
    });
    Event.add(window, "resize", a);
    Event.add(window, "beforeunload", function () {
        MIDI.closePlugin && MIDI.closePlugin()
    });
    Event.add(window, "mousewheel", function (a) {
        Event.stop(a);
        Event.prevent(a)
    });
    Event.add(window, "keyup", function (a) {
        switch (a.keyCode) {
        case 32:
            if (!MIDI.Player.replayer)
                break;
            Event.prevent(a);
            MIDI.UI.togglePlayer();
            break;
        case 37:
            Event.prevent(a);
            Piano.getNextSong(-1);
            break;
        case 39:
            Event.prevent(a),
            Piano.getNextSong(1)
        }
    });
    b.MIDINoteOffset = 21
})(Piano);
"undefined" === typeof Piano && (Piano = {});
var root = Piano.Animation = function () {
    var b = {},
    a = 0,
    c = 0,
    e = this,
    d = MIDI.Player;
    this.tCurrent = this.animateInterval = this.scrollTop = 0;
    this.animate = function (b, m) {
        c++;
        Piano.notesPlaying && (c = 0);
        if (Piano.notesPlaying || !(150 < c) || b)
            if ("preview" === Piano.visualize && d.replayer) {
                if (d.playing || b)
                    this.scrollTop = 0, e.tCurrent === d.currentTime && 0 !== a && (this.scrollTop = a - (new Date).getTime()), this.scrollTop = d.currentTime - this.scrollTop, d.renderScreen(!0), e.tCurrent !== d.currentTime && (a = (new Date).getTime(), e.tCurrent = d.currentTime)
            } else {
                var g =
                    e.postview2d;
                if (b) {
                    var f = document.getElementById("note" + b);
                    f && (m ? -1 === f.className.indexOf("force") && (f.className += " force") : f.className = f.className.replace("force", "").trim())
                } else {
                    e.preview2d.drawImage(g.canvas, 0, 0);
                    var f = Piano.notes,
                    l;
                    for (l in f)
                        if (f[l].isOn) {
                            var n = l;
                            if (Piano.blackKeys[n % 12]) {
                                var r = 14;
                                e.preview2d.globalCompositeOperation = "source-over"
                            } else
                                r = Piano.width / 53, e.preview2d.globalCompositeOperation = "destination-over";
                            if (Piano.colorMap[n]) {
                                var q = Piano.colorMap[n].hsl;
                                q && (e.preview2d.fillStyle =
                                        q, e.preview2d.fillRect(Piano.keys[n] + 1 + Piano.offsetLeft - 1, 0, r, 2))
                            }
                        }
                    f = g.canvas;
                    g.clearRect(0, 0, f.width, f.height);
                    g.drawImage(e.preview2d.canvas, 0, 0, f.width, f.height, 0, 2, f.width, f.height);
                    e.preview2d.clearRect(0, 0, f.width, f.height)
                }
            }
    };
    this.boot = function () {
        var a = !1,
        c = 0;
        window.clearInterval(root.animateInterval);
        if (!b.preview) {
            Event.add(document.body, "mousewheel", function (b) {
                b = b ? b : window.event;
                var f = d.endTime;
                d.currentTime += 150 * (b.detail ? -1 * b.detail : b.wheelDelta / 40);
                d.currentTime = Math.max(-Piano.width,
                        d.currentTime);
                d.currentTime = Math.min(f, d.currentTime);
                d.restart = Math.max(0, Math.min(f, d.currentTime));
                c || (a = d.playing, d.pause(), Piano.clearNotes());
                window.clearInterval(c);
                c = window.setInterval(function () {
                    window.clearInterval(c);
                    c = 0;
                    a && Piano.resume()
                }, 150);
                e.animate(!0);
                Piano.genTimeCursor && Piano.genTimeCursor();
                Event.stop(b);
                Event.prevent(b)
            });
            var g = document.getElementById("container"),
            f = document.createElement("div");
            f.style.cssText = "position: absolute; background: #000; z-index: 1000; left: 0; top: 103px; overflow: hidden";
            f.appendChild(CanvasRender[0]);
            f.appendChild(CanvasRender[1]);
            f.appendChild(CanvasRender.overlay);
            g.appendChild(f);
            var l = CanvasRender.overlay.parentNode;
            Event.add(l, "mousedown", function (b) {
                var c = Event.proxy.getCoord(b).y;
                Event.proxy.drag({
                    target: l,
                    position: "absolute",
                    event: b,
                    listener: function (b, f) {
                        if ("up" === f.state && a)
                            return Piano.resume();
                        if ("down" === f.state)
                            return a = d.playing, d.pause();
                        var g = d.endTime;
                        d.currentTime -= 50 * (f.y - c);
                        d.currentTime = Math.max(-Piano.width, d.currentTime);
                        d.currentTime = Math.min(g,
                                d.currentTime);
                        d.restart = Math.max(0, Math.min(g, d.currentTime));
                        c = f.y;
                        e.animate(!0);
                        Piano.genTimeCursor()
                    }
                })
            });
            b.preview = f
        }
        b.postview || (f = document.createElement("div"), g = document.createElement("canvas"), g.setAttribute("style", "position: absolute; top: 98px"), g.width = canvas.bg.width, g.height = 300, f.appendChild(g), e.postview2d = g.getContext("2d"), g = canvas.animate, g.setAttribute("style", "position: absolute; top: 98px"), g.width = canvas.bg.width, g.height = 300, e.preview2d = canvas.animate.getContext("2d"), g.setAttribute("style",
                "border-radius: 10px; position: absolute; top: 98px; width: " + canvas.bg.width + "px; height: 300px"), g.className = "gradient", f.appendChild(g), document.getElementById("container").appendChild(f), b.postview = f);
        switch (Piano.visualize) {
        case "preview":
            b.postview && (b.postview.style.display = "none");
            b.musicbox && (musicbox.preview.style.display = "none");
            f = window.innerHeight - Event.proxy.getBoundingBox(b.preview).y1;
            b.preview.style.display = "block";
            b.preview.style.width = "990px";
            b.preview.style.height = f + "px";
            e.animate(!0);
            break;
        case "postview":
            b.preview && (b.preview.style.display = "none");
            b.musicbox && (musicbox.preview.style.display = "none");
            b.postview.style.display = "block";
            break;
        case "musicbox":
            b.postview && (b.postview.style.display = "none"),
            b.preview && (b.preview.style.display = "none"),
            b.musicbox || (MusicBox.init(), b.musicbox = {})
        }
    };
    this.callback = this.animate;
    return this
}
();
"undefined" === typeof MIDI && (MIDI = {});
(function (b) {
    var a = {
        9: 0,
        49: 1,
        81: 0,
        192: 0,
        50: 1,
        87: 2,
        51: 3,
        69: 4,
        52: 6,
        82: 5,
        53: 6,
        84: 7,
        54: 8,
        89: 9,
        55: 10,
        85: 11,
        56: 13,
        65: 13,
        73: 12,
        57: 13,
        79: 14,
        48: 15,
        80: 16,
        189: 18,
        219: 17,
        187: 18,
        221: 19,
        8: 20,
        220: 21,
        90: 12,
        83: 13,
        88: 14,
        68: 15,
        67: 16,
        70: 18,
        86: 17,
        71: 18,
        66: 19,
        72: 20,
        78: 21,
        74: 22,
        77: 23,
        75: 25,
        188: 24,
        76: 25,
        190: 26,
        186: 27,
        13: 30,
        222: 30,
        191: 28
    },
    c = function (b, c, e) {
        if (!isNaN(a[b])) {
            8 == b && c.preventDefault();
            var g = a[b] + 12;
            Piano.inversion = 0;
            16 != b && (c.shiftKey ? "down" == e ? Piano.chordOn(g) : Piano.chordOff(g) : "up" == e ? Piano.noteOff(g) : Piano.noteOn(g))
        }
    },
    e = {};
    Piano.keyDown = function (a) {
        var b = a.keyCode;
        e[b] || (e[b] = !0, c(b, a, "down"))
    };
    Piano.keyUp = function (a) {
        var b = a.keyCode;
        e[b] = !1;
        c(b, a, "up")
    };
    Event.add(window, "keydown", Piano.keyDown);
    Event.add(window, "keyup", Piano.keyUp);
    Event.add(window, "mouseup", function () {
        Piano.mouseIsActive = !1
    })
})(MIDI.Keyboard);
"undefined" == typeof Piano && (Piano = {});
(function (b) {
    b.notesPlaying = 0;
    b.trackNote = function (a, c, e) {
        b.notesPlaying += e ? 1 : -1;
        b.notes[c] = {
            isOn: e
        };
        "musicbox" === b.visualize && (e ? (a = MusicBox.scene.objects[c], a.scale.x = 1E3, MusicBox.render()) : (a = MusicBox.scene.objects[c], a.scale.x = 1, a.scale.y = 1))
    };
    b.calculateNote = function (a) {
        return b.key + 12 * b.octave + (a || 0)
    };
    b.noteOn = function (a) {
        "undefined" == typeof a && (a = b.key + 12 * b.octave);
        b.drawKeyLabel(a, !0);
        b.trackNote(b.channel, a, !0);
        MIDI.noteOn && MIDI.noteOn(b.channel, a + MIDI.pianoKeyOffset, 64)
    };
    b.noteOff = function (a) {
        b.drawKeyLabel(a,
            !1);
        b.trackNote(b.channel, a, !1);
        MIDI.noteOff && MIDI.noteOff(b.channel, a + MIDI.pianoKeyOffset)
    };
    b.chordOn = function (a) {
        "undefined" == typeof a && (a = b.key + 12 * b.octave);
        var c = clone(MusicTheory.Chords[b.chord]),
        e;
        for (e in c) {
            var d = a + c[e];
            b.trackNote(b.channel, d, !0);
            b.drawKeyLabel(d, !0);
            c[e] = d + MIDI.pianoKeyOffset
        }
        MIDI.chordOn && MIDI.chordOn(b.channel, c, 64)
    };
    b.chordOff = function (a) {
        var c = clone(MusicTheory.Chords[b.chord]),
        e = [],
        d;
        for (d in c)
            b.drawKeyLabel(a + c[d], !1), e.push(a + c[d] + MIDI.pianoKeyOffset);
        MIDI.chordOff &&
        MIDI.chordOff(b.channel, e);
        for (var k in e)
            b.notes[e[k] - MIDI.pianoKeyOffset] && b.trackNote(b.channel, e[k] - MIDI.pianoKeyOffset, !1)
    };
    b.playScale = function (a) {
        b.clearNotes();
        void 0 == a && (a = MusicTheory.Scales[b.scale]);
        a = clone(a);
        a.push(a[0] + 12);
        b.position = 0;
        b.scaleObj = a;
        window.clearInterval(b.interval);
        b.interval = window.setInterval(function () {
            if (b.position > b.scaleObj.length - 1)
                window.clearInterval(b.interval), b.interval = 0;
            else {
                var a = b.calculateNote(b.scaleObj[b.position]);
                b.noteOn(a);
                b.position++
            }
        }, 6E4 / b.tempo)
    };
    b.invert = function (a) {
        b.clearNotes();
        b.inversion += a;
        a = b.inversion;
        var c = clone(MusicTheory.Chords[b.chord]);
        0 > a && (c = c.reverse());
        for (var e = 0; e < Math.abs(a); e++)
            c[e % c.length] += 12 * (0 < a ? 1 : -1);
        for (var d in c)
            e = b.calculateNote(c[d]), c[d] = e, b.trackNote(b.channel, e, !0), b.drawKeyLabel(e, !0), b.noteOn(e)
    };
    b.clearNotes = function () {
        if (b.notes) {
            MIDI.chordOff && MIDI.chordOff(b.channel, b.notes);
            for (var a in b.notes)
                b.drawKeyLabel(a, !1), b.trackNote(b.channel, a, !1)
        }
    };
    b.func = b.playScale;
    b.play = function (a) {
        a && (MIDI.Player.currentData =
                a);
        MIDI.Player.loadMidiFile();
        MIDI.Player.renderScreen()
    };
    b.resume = function () {
        delete b.Animation.tCurrent;
        MIDI.Player.playing = !0;
        b.clearNotes();
        MIDI.Player.resume()
    }
})(Piano);
"undefined" === typeof MIDI && (MIDI = {});
"undefined" === typeof MIDI.Player && (MIDI.Player = {});
(function () {
    var b = MIDI.Player,
    a = [];
    b.cid = void 0;
    b.renderScreen = function (a) {
        var e = Piano.height,
        d = Piano.Animation.scrollTop / Piano.stretchY >> 0,
        k = Math.max(0, ((d + e) / e >> 0) - 1),
        m = k * e;
        0 === k % 2 ? (CanvasRender[0].style.top = -d + m + "px", CanvasRender[1].style.top = -d + e + m + "px") : (CanvasRender[1].style.top = -d + m + "px", CanvasRender[0].style.top = -d + e + m + "px");
        if (b.cid !== k + 1 || "undefined" === typeof a)
            d = (d / e >> 0) * e, MIDI.Player.renderGraphics(k % 2, d), MIDI.Player.renderGraphics((k + 1) % 2, d + e);
        b.cid = k + 1
    };
    b.renderGraphics = function (c, e) {
        if (b.replayer) {
            c ||
            (c = 0);
            e || (e = 0);
            var d = CanvasRender[c].getContext("2d"),
            k = b.data,
            m = Piano.colorMap,
            g = MIDI.pianoKeyOffset,
            f = Piano.blackKeys,
            l = Piano.stretchX,
            n = l / 2,
            r = n / 2,
            q = Piano.stretchY,
            p = MusicTheory.number2float,
            s = d.canvas.height,
            t = 0,
            v = !1;
            d.canvas.height = s;
            for (var w = 0, F = 0; w < k.length; w++) {
                var B = k[w][0].event,
                F = F + k[w][1] / q,
                x = F - e;
                switch (B.type) {
                case "channel":
                    switch (B.subtype) {
                    case "noteOn":
                        if (v)
                            break;
                        var u = B.noteNumber - g;
                        a[u] = [x, u * l];
                        t++;
                        break;
                    case "noteOff":
                        var u = B.noteNumber - g,
                        y = a[u];
                        if (!y)
                            break;
                        var t = Math.max(0, --t),
                        x = (x - y[0] >> 0) + 0.5,
                        y = (y[0] >> 0) + 0.5,
                        z = p[u % 12],
                        z = z + 7 * (u / 12 >> 0),
                        z = z * l;
                        if (y > s) {
                            if (!t)
                                return;
                            v = !0
                        }
                        delete a[u];
                        if (0 > y + x)
                            continue;
                        var E = "#000000" === m[u].hex;
                        d.beginPath();
                        d.fillStyle = m[u].hsl;
                        d.strokeStyle = E ? "rgba(255,255,255,0.3)" : "rgba(0,0,0,1)";
                        f[u % 12] ? (z += r, u = (z >> 0) + 0.5, z = n >> 0, d.fillRect(u, y, z, x), d.strokeRect(u, y, z, x)) : (u = (z >> 0) + 0.5, z = l >> 0, E = Math.min(x / 2, z / 2, 5), d.moveTo(u + E, y), d.lineTo(u + z - E, y), d.quadraticCurveTo(u + z, y, u + z, y + E), d.lineTo(u + z, y + x - E), d.quadraticCurveTo(u + z, y + x, u + z - E, y + x), d.lineTo(u + E, y +
                                x), d.quadraticCurveTo(u, y + x, u, y + x - E), d.lineTo(u, y + E), d.quadraticCurveTo(u, y, u + E, y), d.fill(), d.stroke());
                        break
                    }
                case "meta":
                    switch (B.subtype) {
                    case "setTempo":
                        MIDI.Player.tempo = 6E7 / B.microsecondsPerBeat
                    }
                }
            }
        }
    }
})();
"undefined" === typeof Piano && (Piano = {});
var scale = 0.36;
Piano.stretchX = 19;
Piano.stretchY = 10;
Piano.createKeyGlyphs = function () {
    function b(a) {
        var b = document.createElement("canvas"),
        c = b.getContext("2d"),
        e = a(c),
        f = e[0] * scale,
        l = e[1] * scale,
        n = e[3] * scale;
        b.width = e[2] * scale;
        b.height = n;
        c.scale(scale, scale);
        c.translate(-f / scale, -l / scale - 3);
        a(c);
        return {
            src: b.toDataURL(),
            canvas: b
        }
    }
    var a,
    c = b(function (b) {
        b.save();
        b.save();
        b.beginPath();
        b.moveTo(49.9, 34.1);
        b.lineTo(10, 34.1);
        b.bezierCurveTo(7.1, 34.1, 4.7, 36.5, 4.7, 39.4);
        b.lineTo(4.7, 240.7);
        b.bezierCurveTo(4.7, 243.6, 7.1, 245.9, 10, 245.9);
        b.lineTo(49.9, 245.9);
        b.bezierCurveTo(52.8,
            245.9, 55.1, 243.6, 55.1, 240.7);
        b.lineTo(55.1, 39.4);
        b.bezierCurveTo(55.1, 36.5, 52.8, 34.1, 49.9, 34.1);
        b.closePath();
        b.beginPath();
        b.moveTo(50.4, 235.4);
        b.bezierCurveTo(50.4, 238.3, 48, 240.7, 45.1, 240.7);
        b.lineTo(5.2, 240.7);
        b.bezierCurveTo(2.3, 240.7, 0, 238.3, 0, 235.4);
        b.lineTo(0, 34.1);
        b.bezierCurveTo(0, 31.2, 2.3, 28.9, 5.2, 28.9);
        b.lineTo(45.1, 28.9);
        b.bezierCurveTo(48, 28.9, 50.4, 31.2, 50.4, 34.1);
        b.lineTo(50.4, 235.4);
        b.closePath();
        a = b.createLinearGradient(25.2, 240.2, 25.2, 28.4);
        a.addColorStop(0, "rgb(255, 255, 255)");
        a.addColorStop(0.9, "rgb(226, 226, 226)");
        a.addColorStop(0.93, "rgb(143, 143, 143)");
        a.addColorStop(0.96, "rgb(60, 60, 60)");
        b.fillStyle = a;
        b.fill();
        b.restore();
        b.restore();
        return [0, 40, 51, 202]
    }),
    e = b(function (b) {
        b.save();
        b.save();
        b.beginPath();
        b.moveTo(67.2, 162.7);
        b.bezierCurveTo(67.2, 164.7, 65.7, 166.4, 63.7, 166.4);
        b.lineTo(39.7, 166.4);
        b.bezierCurveTo(37.7, 166.4, 36.1, 164.7, 36.1, 162.7);
        b.lineTo(36.1, 3.7);
        b.bezierCurveTo(36.1, 1.6, 37.7, 0, 39.7, 0);
        b.lineTo(63.7, 0);
        b.bezierCurveTo(65.7, 0, 67.2, 1.6, 67.2, 3.7);
        b.lineTo(67.2,
            162.7);
        b.closePath();
        b.fillStyle = "rgb(1, 1, 1)";
        b.fill();
        b.beginPath();
        b.moveTo(39, 36.5);
        b.lineTo(64.7, 36.5);
        b.lineTo(64.7, 163.5);
        b.lineTo(39, 163.5);
        b.lineTo(39, 36.5);
        b.closePath();
        a = b.createLinearGradient(51.8, 163.5, 51.8, 34.7);
        a.addColorStop(0.02, "rgb(30, 30, 30)");
        a.addColorStop(0.07, "rgb(75, 75, 75)");
        a.addColorStop(0.19, "rgb(119, 119, 119)");
        a.addColorStop(0.87, "rgb(75, 75, 75)");
        a.addColorStop(1, "rgb(30, 30, 30)");
        b.fillStyle = a;
        b.fill();
        b.beginPath();
        b.moveTo(62.7, 146.9);
        b.bezierCurveTo(62.7,
            148.3, 61.6, 149.4, 60.2, 149.4);
        b.lineTo(43.4, 149.4);
        b.bezierCurveTo(42, 149.4, 40.9, 148.3, 40.9, 146.9);
        b.lineTo(40.9, 38.8);
        b.bezierCurveTo(40.9, 37.5, 42, 36.3, 43.4, 36.3);
        b.lineTo(60.2, 36.3);
        b.bezierCurveTo(61.6, 36.3, 62.7, 37.5, 62.7, 38.8);
        b.lineTo(62.7, 146.9);
        b.closePath();
        a = b.createRadialGradient(19.6, 136.4, 0, 19.6, 136.4, 110.2);
        a.addColorStop(0.4, "rgb(5, 5, 5)");
        a.addColorStop(0.59, "rgb(60, 60, 60)");
        a.addColorStop(0.64, "rgb(119, 119, 119)");
        b.fillStyle = a;
        b.fill();
        b.beginPath();
        b.moveTo(62.7, 61.6);
        b.bezierCurveTo(62.7,
            61.9, 61.6, 62.2, 60.2, 62.2);
        b.lineTo(43.4, 62.2);
        b.bezierCurveTo(42, 62.2, 40.9, 61.9, 40.9, 61.6);
        b.lineTo(40.9, 34.9);
        b.bezierCurveTo(40.9, 34.5, 42, 34.2, 43.4, 34.2);
        b.lineTo(60.2, 34.2);
        b.bezierCurveTo(61.6, 34.2, 62.7, 34.5, 62.7, 34.9);
        b.lineTo(62.7, 61.6);
        b.closePath();
        a = b.createLinearGradient(51.8, 61.8, 51.8, 34.4);
        a.addColorStop(0, "rgb(119, 119, 119)");
        a.addColorStop(0.58, "rgb(80, 80, 80)");
        a.addColorStop(0.87, "rgb(40, 40, 40)");
        b.fillStyle = a;
        b.fill();
        b.beginPath();
        b.moveTo(59.6, 148.4);
        b.lineTo(44.2, 148.4);
        b.bezierCurveTo(43,
            148.4, 41.9, 147.3, 41.9, 146);
        b.lineTo(41.9, 37.9);
        b.bezierCurveTo(41.9, 37.4, 42.1, 36.9, 42.3, 36.5);
        b.bezierCurveTo(41.5, 36.9, 40.9, 37.8, 40.9, 38.8);
        b.lineTo(40.9, 146.9);
        b.bezierCurveTo(40.9, 148.3, 41.9, 149.4, 43.1, 149.4);
        b.lineTo(58.6, 149.4);
        b.bezierCurveTo(59.3, 149.4, 60, 148.9, 60.4, 148.3);
        b.bezierCurveTo(60.2, 148.4, 59.9, 148.4, 59.6, 148.4);
        b.closePath();
        b.save();
        b.transform(0.913, 0, 0, -1, 159.9, 643.1);
        a = b.createRadialGradient(-151.2, 506.6, 0, -151.2, 506.6, 108.2);
        a.addColorStop(0, "rgb(223, 223, 223)");
        a.addColorStop(0.81,
            "rgb(119, 119, 119)");
        a.addColorStop(1, "rgb(60, 60, 60)");
        b.fillStyle = a;
        b.fill();
        b.restore();
        b.beginPath();
        b.moveTo(43.1, 149.4);
        b.lineTo(41.1, 163.5);
        b.lineTo(39, 163.5);
        b.lineTo(39, 160.6);
        b.lineTo(41.8, 149.3);
        b.lineTo(43.1, 149.4);
        b.closePath();
        a = b.createLinearGradient(41, 163.3, 41, 101.3);
        a.addColorStop(0.02, "rgb(30, 30, 30)");
        a.addColorStop(0.07, "rgb(75, 75, 75)");
        a.addColorStop(0.19, "rgb(119, 119, 119)");
        a.addColorStop(0.87, "rgb(75, 75, 75)");
        a.addColorStop(1, "rgb(30, 30, 30)");
        b.fillStyle = a;
        b.fill();
        b.beginPath();
        b.moveTo(60.5, 149.4);
        b.lineTo(62.5, 163.5);
        b.lineTo(64.7, 163.5);
        b.lineTo(64.7, 160.6);
        b.lineTo(61.9, 149.3);
        b.lineTo(60.5, 149.4);
        b.closePath();
        b.save();
        b.transform(-1.005, 0, 0, -1, 5206.5, 643.1);
        a = b.createLinearGradient(5120.3, 479.8, 5120.3, 541.7);
        a.addColorStop(0.02, "rgb(30, 30, 30)");
        a.addColorStop(0.07, "rgb(63, 63, 63)");
        a.addColorStop(0.19, "rgb(95, 95, 95)");
        a.addColorStop(0.87, "rgb(63, 63, 63)");
        a.addColorStop(1, "rgb(30, 30, 30)");
        b.fillStyle = a;
        b.fill();
        b.restore();
        b.restore();
        b.restore();
        return [35, 40, 32, 127]
    });
    return {
        whiteKey: c,
        blackKey: e
    }
};
Piano.Glyphs = Piano.createKeyGlyphs();
Piano.drawKeyLabel = function (b, a) {
    if ((MIDI.Player.playing || "preview" !== Piano.visualize) && Piano.domKeys[b] && 0 <= b && 88 >= b)
        if (a) {
            var c = Piano.colorMap[b].hsl,
            e = document.getElementById("note" + b);
            e && -1 === e.className.indexOf("force") && (e.className += " force", e.style.color = "", e.style.textShadow = "", e.style.backgroundColor = c)
        } else (e = document.getElementById("note" + b)) && -1 !== e.className.indexOf("force") && (e.className = e.className.replace(" force", ""), e.style.background = "", e.style.color = "rgba(0,0,0,0)", e.style.textShadow =
                    "none")
};
Piano.domKeys = {};
Piano.drawKeyboard = function () {
    function b(b, k, m, g) {
        for (var f = {
                0: !0,
                2: !0,
                6: !0
            }, l = k.length, n = 0, r = 0; r < b; r++) {
            var q = r,
            p = document.createElement("div"),
            s = "black" === m,
            n = k[q % l] + 12 * Math.floor(q / l);
            Piano.keys[n] = g;
            var t = Piano.colorMap[n].hsl,
            v = g + Piano.offsetLeft;
            if (s)
                var s = canvas.black, w = a;
            else
                s = canvas.white, w = c;
            s.drawImage(w, v, 7);
            s.fillStyle = t;
            s.fillRect(v, 0, w.width, 7);
            p.style.width = w.width - 1 + "px";
            p.style.height = "21px";
            p.style.paddingTop = w.height - 26 + 3.5 + "px";
            t = Piano.keySignature[n % 12];
            t = "solfege" === Piano.labelType ?
                MusicTheory.Solfege[t].syllable : t;
            p.style.marginTop = "7px";
            p.style.left = g + Piano.offsetLeft + "px";
            p.style.color = "rgba(0,0,0,0)";
            p.style.textShadow = "none";
            p.className = m;
            p.name = n;
            p.innerHTML = t;
            p.id = "note" + n;
            Event.add(p, "mousedown", Piano.mouseDown);
            Event.add(p, "mouseup", Piano.mouseUp);
            Event.add(p, "mouseover", Piano.mouseOver);
            Event.add(p, "mouseout", Piano.mouseOut);
            Piano.domKeys[n] = p;
            document.getElementById("keys").appendChild(p);
            g = "white" !== m && f[q % l] ? g + 2 * e : g + e
        }
        Event.add(canvas.black.canvas, "mousedown", Piano.mouseDown);
        Event.add(canvas.black.canvas, "mouseup", Piano.mouseUp);
        Event.add(canvas.black.canvas, "mousemove", Piano.mouseOver)
    }
    document.getElementById("keys").innerHTML = "";
    var a = Piano.Glyphs.blackKey.canvas,
    c = Piano.Glyphs.whiteKey.canvas,
    e = c.width + 1;
    b(52, [0, 2, 3, 5, 7, 8, 10], "white", 14);
    b(36, [1, 4, 6, 9, 11], "black", 14 + c.width - a.width / 2)
};
Piano.mouseIsActive = !1;
Piano.mousePlay = function (b, a) {
    var c = parseInt(b);
    Piano.inversion = 0;
    Piano.mouseIsActive = !0;
    Piano.clearNotes();
    a.shiftKey ? Piano.chordOn(c) : Piano.noteOn(c)
};
Piano.mouseStop = function (b, a) {
    var c = parseInt(a);
    b.shiftKey ? (Piano.clearNotes(), Piano.chordOff(c)) : Piano.noteOff(c)
};
Piano.mouseUp = function (b) {
    var a = this.name || getNote(this, b);
    Piano.mouseIsActive = !1;
    Piano.mouseStop(b, a)
};
Piano.mouseDown = function (b) {
    var a = this.name || getNote(this, b);
    Piano.mousePlay(a, b)
};
Piano.mouseOver = function (b) {
    if (!1 != Piano.mouseIsActive)
        if ("undefined" == typeof this.name) {
            var a = getNote(this, b);
            this.currentNote !== a && (this.currentNote = a, Piano.mouseStop(b, this.currentNote), Piano.mousePlay(a, b))
        } else
            Piano.mousePlay(this.name, b)
};
Piano.mouseOut = function (b) {
    if (Piano.mouseIsActive) {
        var a = this.name || getNote(this, b);
        Piano.mouseStop(b, a)
    }
};
var getNote = function (b, a) {
    var c = Event.proxy.getCoord(a),
    e = Event.proxy.getBoundingBox(b),
    c = (c.x - e.x1) / (Piano.Glyphs.whiteKey.canvas.width + 1) >> 0,
    e = c % 7,
    d = 0;
    0 < e && (d += 1);
    2 < e && (d += 1);
    3 < e && (d += 1);
    5 < e && (d += 1);
    return c + (d + 5 * (c / 7 >> 0))
};
Piano.songViewToggle = function (b) {
    "postview" === Piano.visualize ? (b.id = "view-theory", b.title = "Music Theory Mode", MIDI.UI.enableSongView()) : (b.id = "view-song", b.title = "Piano Player Mode", MIDI.UI.enableTheoryView())
};
Piano.files = function () {
    for (var b = {}, a = "Albeniz - Espana (Spain) Op-165 Capricho Catalan.mid;Albeniz - Espana (Spain) Op-165 Malaguena.mid;Albeniz - Espana (Spain) Op-165 Prelude.mid;Albeniz - Espana (Spain) Op-165 Serenata.mid;Albeniz - Espana (Spain) Op-165 Tango.mid;Albeniz - Espana (Spain) Op-165 Zortcico.mid;Albeniz - Espana Op-165 Capricho Catalan.mid;Albeniz - Espana Op-165 Malaguena.mid;Albeniz - Espana Op-165 Prelude.mid;Albeniz - Espana Op-165 Serenata.mid;Albeniz - Espana Op-165 Tango.mid;Albeniz - Espana Op-165 Zortcico.mid;Albeniz - Evocation from Iberia Suite.mid;Albeniz - Suite Espagnole Aragon (Fantasia).mid;Albeniz - Suite Espagnole Aragon.mid;Albeniz - Suite Espagnole Asturias (Leyendas).mid;Albeniz - Suite Espagnole Asturias.mid;Albeniz - Suite Espagnole Cadiz.mid;Albeniz - Suite Espagnole Castilla (Seguidillas).mid;Albeniz - Suite Espagnole Castilla.mid;Albeniz - Suite Espagnole Cataluna-1.mid;Albeniz - Suite Espagnole Cataluna-2.mid;Albeniz - Suite Espagnole Cataluna.mid;Albeniz - Suite Espagnole Cuba (Notturno).mid;Albeniz - Suite Espagnole Cuba.mid;Albeniz - Suite Espagnole Granada.mid;Albeniz - Suite Espagnole Sevilla.mid;Albeniz - Tango (Arr Godowsky).mid;Albeniz - Tango.mid;Albeniz - Triana (From The Ibera Suite).mid;Alberto Ginastera - Sonata No-1 Op-22 1st & 4th Movs (Meek05).mid;Albinez - Tango arr. by Godowsky.mid;Albinez - Triana from Iberia Suite.mid;Alexander Scriabin - Entragete Op-63 (Sekino11).mid;Alexander Scriabin - Etude Op-42 No-4 Etude Op-65 No-3 (Meek02).mid;Alexander Scriabin - Fantasie in B-min Op-28 (Floril04).mid;Alexander Scriabin - Fragilite Op-51 (Sekino10).mid;Alexander Scriabin - Sonata No-5 Op-53 (Na03).mid;Alexander Scriabin - Sonata No-5 Op-53 (Na07).mid;Alexander Scriabin - Sonata No-5 Op-53 (Yeletskiy02).mid;Alexander Scriabin - Sonata No-5 Op-53 (Yeletskiy07).mid;Alexander Scriabin - Sonata No-9 Op-68 (Sekino12).mid;Alkan - Chemin De Fer.mid;Alkan - Festin Daesope.mid;Alkan - Op-35 No-05.mid;Alkan - Op-38a No-01.mid;Alkan - Op-39 No-01.mid;Alkan - Op-39 No-03.mid;Alkan - Op-39 No-10.mid;Alkan - Op-76 No-01.mid;Alkan - Op-76 No-02.mid;Alkan - Op-76 No-03.mid;Alkan - Saltarelo.mid;Bach, JS - Aria (Goldberg Variations).mid;Bach, JS - Ave Maria.mid;Bach, JS - BWV-0772 No-01 2-part invention.mid;Bach, JS - BWV-0773 No-02 2-part invention.mid;Bach, JS - BWV-0774 No-03 2-part invention.mid;Bach, JS - BWV-0775 No-04 2-part invention.mid;Bach, JS - BWV-0776 No-05 2-part invention.mid;Bach, JS - BWV-0777 No-06 2-part invention.mid;Bach, JS - BWV-0778 No-07 2-part invention.mid;Bach, JS - BWV-0779 No-08 2-part invention.mid;Bach, JS - BWV-0780 No-09 2-part invention.mid;Bach, JS - BWV-0781 No-10 2-part invention.mid;Bach, JS - BWV-0782 No-11 2-part invention.mid;Bach, JS - BWV-0783 No-12 2-part invention.mid;Bach, JS - BWV-0784 No-13 2-part invention.mid;Bach, JS - BWV-0785 No-14 2-part invention.mid;Bach, JS - BWV-0786 No-15 2-part invention.mid;Bach, JS - BWV-0787 No-01 3-part Sinfonia in C.mid;Bach, JS - BWV-0788 No-02 3-part Sinfonia in C.mid;Bach, JS - BWV-0789 No-03 3-part Sinfonia in D.mid;Bach, JS - BWV-0790 No-04 3-part Sinfonia in D.mid;Bach, JS - BWV-0791 No-05 3-part Sinfonia in E.mid;Bach, JS - BWV-0792 No-06 3-part Sinfonia in E.mid;Bach, JS - BWV-0793 No-07 3-part Sinfonia in E.mid;Bach, JS - BWV-0794 No-08 3-part Sinfonia in F.mid;Bach, JS - BWV-0795 No-09 3-part Sinfonia in F.mid;Bach, JS - BWV-0796 No-10 3-part Sinfonia in G.mid;Bach, JS - BWV-0797 No-11 3-part Sinfonia in G.mid;Bach, JS - BWV-0798 No-12 3-part Sinfonia in A.mid;Bach, JS - BWV-0799 No-13 3-part Sinfonia in A.mid;Bach, JS - BWV-0800 No-14 3-part Sinfonia in B.mid;Bach, JS - BWV-0801 No-15 3-part Sinfonia in B.mid;Bach, JS - BWV-0802 Duetto I in E-min.mid;Bach, JS - BWV-0803 Duetto II in F-Maj.mid;Bach, JS - BWV-0804 Duetto III in G-Maj.mid;Bach, JS - BWV-0805 Duetto IV in A-min.mid;Bach, JS - BWV-0806 English Suite No-1 in A-Maj.mid;Bach, JS - BWV-0807 English Suite No-2 in A-min.mid;Bach, JS - BWV-0808 English Suite No-3 in G-min.mid;Bach, JS - BWV-0808 Mov-01 Prelude English Suite.mid;Bach, JS - BWV-0808 Mov-02 Allemande English Suite.mid;Bach, JS - BWV-0808 Mov-03 Courante English Suite.mid;Bach, JS - BWV-0808 Mov-04 Sarabande English Suite.mid;Bach, JS - BWV-0808 Mov-05 Gavottes I & II English Suite.mid;Bach, JS - BWV-0808 Mov-06 Gigue English Suite.mid;Bach, JS - BWV-0809 English Suite No-4 in F-Maj.mid;Bach, JS - BWV-0810 English Suite No-5 in E-min.mid;Bach, JS - BWV-0811 English Suite No-6 in D-min.mid;Bach, JS - BWV-0812 French Suite in D-min.mid;Bach, JS - BWV-0813 French Suite in C-min.mid;Bach, JS - BWV-0814 French Suite in B-min.mid;Bach, JS - BWV-0815 French Suite in Eb.mid;Bach, JS - BWV-0816 French Suite in G.mid;Bach, JS - BWV-0817 French Suite in E.mid;Bach, JS - BWV-0818 Suite in A-min.mid;Bach, JS - BWV-0819 Suite in Eb-Maj.mid;Bach, JS - BWV-0825 Partita in Bb.mid;Bach, JS - BWV-0826 Partita in C.mid;Bach, JS - BWV-0827 Partita in A.mid;Bach, JS - BWV-0828 Partita in D.mid;Bach, JS - BWV-0829 Partita in G.mid;Bach, JS - BWV-0830 Partita in E.mid;Bach, JS - BWV-0833 Prelude & Partita in F.mid;Bach, JS - BWV-0846 No-1 Well Tempered Clavier.mid;Bach, JS - BWV-0847 No-2 Well Tempered Clavier.mid;Bach, JS - BWV-0848 No-3 Well Tempered Clavier.mid;Bach, JS - BWV-0849 No-4 Well Tempered Clavier.mid;Bach, JS - BWV-0850 No-5 Well Tempered Clavier.mid;Bach, JS - BWV-0851 No-6 Well Tempered Clavier.mid;Bach, JS - BWV-0852 No-7 Well Tempered Clavier.mid;Bach, JS - BWV-0853 No-8 Well Tempered Clavier.mid;Bach, JS - BWV-0854 No-9 Well Tempered Clavier.mid;Bach, JS - BWV-0855 No-10 Well Tempered Clavier.mid;Bach, JS - BWV-0856 No-11 Well Tempered Clavier.mid;Bach, JS - BWV-0857 No-12 Well Tempered Clavier.mid;Bach, JS - BWV-0858 No-13 Well Tempered Clavier.mid;Bach, JS - BWV-0859 No-14 Well Tempered Clavier.mid;Bach, JS - BWV-0860 No-15 Well Tempered Clavier.mid;Bach, JS - BWV-0861 No-16 Well Tempered Clavier.mid;Bach, JS - BWV-0862 No-17 Well Tempered Clavier.mid;Bach, JS - BWV-0863 No-18 Well Tempered Clavier.mid;Bach, JS - BWV-0864 No-19 Well Tempered Clavier.mid;Bach, JS - BWV-0865 No-20 Well Tempered Clavier.mid;Bach, JS - BWV-0866 No-21 Well Tempered Clavier.mid;Bach, JS - BWV-0867 No-22 Well Tempered Clavier.mid;Bach, JS - BWV-0868 No-23 Well Tempered Clavier.mid;Bach, JS - BWV-0869 No-24 Well Tempered Clavier.mid;Bach, JS - BWV-0870 No-1 Well Tempered Clavier.mid;Bach, JS - BWV-0871 No-2 Well Tempered Clavier.mid;Bach, JS - BWV-0872 No-3 Well Tempered Clavier.mid;Bach, JS - BWV-0873 No-4 Well Tempered Clavier.mid;Bach, JS - BWV-0874 No-5 Well Tempered Clavier.mid;Bach, JS - BWV-0875 No-6 Well Tempered Clavier.mid;Bach, JS - BWV-0876 No-7 Well Tempered Clavier.mid;Bach, JS - BWV-0877 No-8 Well Tempered Clavier.mid;Bach, JS - BWV-0878 No-9 Well Tempered Clavier.mid;Bach, JS - BWV-0879 No-10 Well Tempered Clavier.mid;Bach, JS - BWV-0880 No-11 Well Tempered Clavier.mid;Bach, JS - BWV-0881 No-12 Well Tempered Clavier.mid;Bach, JS - BWV-0882 No-13 Well Tempered Clavier.mid;Bach, JS - BWV-0883 No-14 Well Tempered Clavier.mid;Bach, JS - BWV-0884 No-15 Well Tempered Clavier.mid;Bach, JS - BWV-0885 No-16 Well Tempered Clavier.mid;Bach, JS - BWV-0886 No-17 Well Tempered Clavier.mid;Bach, JS - BWV-0887 No-18 Well Tempered Clavier.mid;Bach, JS - BWV-0888 No-19 Well Tempered Clavier.mid;Bach, JS - BWV-0889 No-20 Well Tempered Clavier.mid;Bach, JS - BWV-0890 No-21 Well Tempered Clavier.mid;Bach, JS - BWV-0891 No-22 Well Tempered Clavier.mid;Bach, JS - BWV-0892 No-23 Well Tempered Clavier.mid;Bach, JS - BWV-0893 No-24 Well Tempered Clavier.mid;Bach, JS - BWV-0902 Praeludium & Fughetta.mid;Bach, JS - BWV-0903 Chromatic Fantasy & Fugue.mid;Bach, JS - BWV-0906 Mov-01 Fantasia Fantasia & F.mid;Bach, JS - BWV-0906 Mov-02 Fuguee Fantasia & Fugue.mid;Bach, JS - BWV-0910 Toccata No-1 in F#-min.mid;Bach, JS - BWV-0911 Toccata No-2 in C-min.mid;Bach, JS - BWV-0912 Toccata No-3 in D-Major.mid;Bach, JS - BWV-0913 Toccata No-4 in D-min.mid;Bach, JS - BWV-0914 Toccata No-5 in E-min.mid;Bach, JS - BWV-0915 Toccata No-6 in G-min.mid;Bach, JS - BWV-0916 Toccata No-7 in G-Major.mid;Bach, JS - BWV-0948 Fugue in D-min.mid;Bach, JS - BWV-0953 Fugue in C.mid;Bach, JS - BWV-0963 sonata in D-Maj.mid;Bach, JS - BWV-0965 sonata in D-min.mid;Bach, JS - BWV-0966 sonata in C-Maj.mid;Bach, JS - BWV-0967 sonata in A-min.mid;Bach, JS - BWV-0988 Goldberg Variations.mid;Bach, JS - BWV-0992 Capriccio in Bb-Maj.mid;Bach, JS - BWV-0993 Capriccio in E-Maj.mid;Bach, JS - BWV-0Minuet in G-Maj.mid;Bach, JS - Christfreuden - Weihnachtsfantas.mid;Bach, JS - Concerto In The Italian Style.mid;Bach, JS - Das Wohltemperierte Klavier I - Prelude & Fuge in C Maj BWV-846.mid;Bach, JS - Das Wohltemperierte Klavier I - Prelude & Fuge in C min BWV-847.mid;Bach, JS - Das Wohltemperierte Klavier I - Prelude & Fuge in D Maj BWV-850.mid;Bach, JS - Das wohltemperierte Klavier I-1.mid;Bach, JS - Das wohltemperierte Klavier I-2.mid;Bach, JS - Duet in E-min BWV-802 (Jussow07).mid;Bach, JS - Duet in G-Maj BWV-804 (Jussow08).mid;Bach, JS - Fantasie uber Stille Nacht, hei.mid;Bach, JS - Fugue (WTC Bk-1 No-21).mid;Bach, JS - Fugue (WTC Bk-1 No-3).mid;Bach, JS - Fugue (WTC Bk-1 No-5).mid;Bach, JS - Fugue (WTC Bk-1 No-7).mid;Bach, JS - Gavotte (French Suite No-5).mid;Bach, JS - Intermezzo Op-118 No-2 in A-Maj (Shilyaev03).mid;Bach, JS - Italian Concerto Mvt-1.mid;Bach, JS - Italian Concerto Mvt-2.mid;Bach, JS - Italian Concerto Mvt-3.mid;Bach, JS - Jesu Joy of Man's Desiring.mid;Bach, JS - March in D.mid;Bach, JS - Minuet in G (2).mid;Bach, JS - Minuet in G.mid;Bach, JS - Musette in D.mid;Bach, JS - Ode to Joy (Jesu Joy).mid;Bach, JS - Op-116 Nos 1 2 & 3 (Atzinger02).mid;Bach, JS - Paganini Vars Op-35 Book I (Terenkova04).mid;Bach, JS - Paganini Vars Op-35 Book II (Golubeva03).mid;Bach, JS - Paganini Vars Op-35 Book II (Zhdanov03).mid;Bach, JS - Paganini Vars Op-35 Books I & II (Zhdanov10).mid;Bach, JS - Prelude (WTC Bk-1 No-21).mid;Bach, JS - Prelude (WTC Bk-1 No-3).mid;Bach, JS - Prelude (WTC Bk-1 No-5.mid;Bach, JS - Prelude (WTC Bk-1 No-7).mid;Bach, JS - Prelude in C (WTC) Bk.1).mid;Bach, JS - PrN\u0303ludium und Fuge in D-Dur, BWV.mid;Bach, JS - Sonata No-1 in C-Maj Op-1 (Na08).mid;Bach, JS - Sonata No-2 in F-sharp-min Op-2 (Tak06).mid;Bach, JS - Sonata No-3 in F-min Op-5 (Yang09).mid;Bach, JS - Sonata No-3 in F-min Op-5 1st Mov (Yang04).mid;Bach, JS - Three Part Inventions (G-min D-min & G-Maj) (Erice01).mid;Bach, JS - Toccata and Fugue in D.mid;Bach, JS - Vars on a theme by Paganini Op-35 Book II (ParkJ01).mid;Bach, JS - Weihnachts-Fantasie.mid;Bach, JS - Zu Weihnachten - Fantasie.mid;Bakairew Islamei - Orientalische Fantasie.mid;Balakirev - Islamei Orientalische Fa.mid;Balakirev - Islamey.mid;Bartok, Bela - Bagatelle Op-6 No-2.mid;Bartok, Bela - Milkrosmos No-153.mid;Bartok, Bela - Roumanian Dance.mid;Beethoven, Ludwig Van - Bagatelle Op-33 No-1.mid;Beethoven, Ludwig Van - Bagatelle Op-33 No-4.mid;Beethoven, Ludwig Van - Fuer Elise.mid;Beethoven, Ludwig Van - Fur Elise.mid;Beethoven, Ludwig Van - Mondscheinsonate (Moonlight Sonata) No.14 in C#-min Op-27-2 (1801) 1st Nov.mid;Beethoven, Ludwig Van - Mondscheinsonate (Moonlight Sonata) No.14 in C#-min Op-27-2 (1801) 2nd Nov.mid;Beethoven, Ludwig Van - Mondscheinsonate (Moonlight Sonata) No.14 in C#-min Op-27-2 (1801) 3rd Nov.mid;Beethoven, Ludwig Van - Moonlight Sonata 1st Mov.mid;Beethoven, Ludwig Van - Moonlight Sonata 2nd Mov .mid;Beethoven, Ludwig Van - Moonlight Sonata Op-27 No-2 Mvt-1.mid;Beethoven, Ludwig Van - Moonlight Sonata Op-27 No-2 Mvt-2.mid;Beethoven, Ludwig Van - Moonlight Sonata Op-27 No-2 Mvt-3.mid;Beethoven, Ludwig Van - Op-013 No-8 Mov-02 Adagio Cantabile.mid;Beethoven, Ludwig Van - Op-013 No-8 Mov-03 Rondo Allegro sonata.mid;Beethoven, Ludwig Van - Op-02 No-1 Mov-01 Allegro sonata No-1.mid;Beethoven, Ludwig Van - Op-027 Mov-01 Adagio Sostenuta sonata No-14 in C.mid;Beethoven, Ludwig Van - Op-027 Mov-02 Allegretto sonata No-14 in C.mid;Beethoven, Ludwig Van - Op-027 Mov-03 Presto sonata No-14 in C.mid;Beethoven, Ludwig Van - Op-031 Mov-04 Presto Con Fuoco sonata.mid;Beethoven, Ludwig Van - Op-033 No-1 Seven Bagatelles.mid;Beethoven, Ludwig Van - Op-033 No-2 Seven Bagatelles.mid;Beethoven, Ludwig Van - Op-033 No-3 Seven Bagatelles.mid;Beethoven, Ludwig Van - Op-033 No-4 Seven Bagatelles.mid;Beethoven, Ludwig Van - Op-033 No-5 Seven Bagatelles.mid;Beethoven, Ludwig Van - Op-033 No-6 Seven Bagatelles.mid;Beethoven, Ludwig Van - Op-033 No-7 Seven Bagatelles.mid;Beethoven, Ludwig Van - Op-049 Mov-01 Allegro Ma Non Troppo.mid;Beethoven, Ludwig Van - Op-053 Mov-01 Allegro Con Brio.mid;Beethoven, Ludwig Van - Op-053 Mov-02 Introduzione - Adagio.mid;Beethoven, Ludwig Van - Op-057 Mov-01 Allegro Assai.mid;Beethoven, Ludwig Van - Op-057 Mov-03 Allegro Ma Non Troppo.mid;Beethoven, Ludwig Van - Op-079 sonata No-25 in G.mid;Beethoven, Ludwig Van - Op-13 No-8 Mov-01 Grave - Allegro.mid;Beethoven, Ludwig Van - Pathetique Sonata No-08 Op-13 (1799) 1st Mov.mid;Beethoven, Ludwig Van - Pathetique Sonata No-08 Op-13 (1799) 2nd Mov.mid;Beethoven, Ludwig Van - Pathetique Sonata No-08 Op-13 (1799) 3rd Mov.mid;Beethoven, Ludwig Van - Pathetique Sonata Op-13 Mvt-1.mid;Beethoven, Ludwig Van - Pathetique Sonata Op-13 Mvt-2.mid;Beethoven, Ludwig Van - Pathetique Sonata Op-13 Mvt-3.mid;Beethoven, Ludwig Van - Sonata 1 Movement.mid;Beethoven, Ludwig Van - Sonata 2 Movement.mid;Beethoven, Ludwig Van - Sonata 3 Movement.mid;Beethoven, Ludwig Van - Sonata-1 Movement.mid;Beethoven, Ludwig Van - Sonata-2 Movement.mid;Beethoven, Ludwig Van - Sonata-3 Movement.mid;Beethoven, Ludwig Van - Sonate No-23 (Appassionata) F min Op-57 1st Mov.mid;Beethoven, Ludwig Van - Sonate No-23 (Appassionata) F min Op-57 2nd Mov.mid;Beethoven, Ludwig Van - Sonate No-23 (Appassionata) F min Op-57 3rd Mov.mid;Beethoven, Ludwig Van - Sonate No-23 Op Appassionata-1.mid;Beethoven, Ludwig Van - Sonate No-23 Op Appassionata-2.mid;Beethoven, Ludwig Van - Sonate No-23 Op Appassionata-3.mid;Beethoven, Ludwig Van - Sonate No-27 in E-min Op-90 1st Mov.mid;Beethoven, Ludwig Van - Sonate No-27 in E-min Op-90 2nd Mov.mid;Beethoven, Ludwig Van - Symphony No-5 Mvt-1.mid;Beethoven, Ludwig Van - Wadlheim Sonata-2 Movement.mid;Beethoven, Ludwig Van - Wadlheim Sonata-3 Movement.mid;Beethoven, Ludwig Van - Waldheim Sonata-1 Movement.mid;Beethoven, Ludwig von - Bagatellen Op-126 (Rozanski06).mid;Beethoven, Ludwig von - Fur Elize.mid;Beethoven, Ludwig von - Ich denke dein-01.mid;Beethoven, Ludwig von - Ich denke dein-02.mid;Beethoven, Ludwig von - Piano Sonata No-01.mid;Beethoven, Ludwig von - Piano Sonata No-02.mid;Beethoven, Ludwig von - Piano Sonata No-03.mid;Beethoven, Ludwig von - Piano Sonata No-04.mid;Beethoven, Ludwig von - Piano Sonata No-05.mid;Beethoven, Ludwig von - Piano Sonata No-06.mid;Beethoven, Ludwig von - Piano Sonata No-07.mid;Beethoven, Ludwig von - Piano Sonata No-09.mid;Beethoven, Ludwig von - Piano Sonata No-10.mid;Beethoven, Ludwig von - Piano Sonata No-11.mid;Beethoven, Ludwig von - Piano Sonata No-12.mid;Beethoven, Ludwig von - Piano Sonata No-13.mid;Beethoven, Ludwig von - Piano Sonata No-14.mid;Beethoven, Ludwig von - Piano Sonata No-15.mid;Beethoven, Ludwig von - Piano Sonata No-17.mid;Beethoven, Ludwig von - Piano Sonata No-18.mid;Beethoven, Ludwig von - Piano Sonata No-19.mid;Beethoven, Ludwig von - Piano Sonata No-20.mid;Beethoven, Ludwig von - Piano Sonata No-21.mid;Beethoven, Ludwig von - Piano Sonata No-22.mid;Beethoven, Ludwig von - Piano Sonata No-23.mid;Beethoven, Ludwig von - Piano Sonata No-24.mid;Beethoven, Ludwig von - Piano Sonata No-25.mid;Beethoven, Ludwig von - Piano Sonata No-27.mid;Beethoven, Ludwig von - Piano Sonata No-32.mid;Beethoven, Ludwig von - Piano Variation 3 March.mid;Beethoven, Ludwig von - Piano Variation No-14.mid;Beethoven, Ludwig von - Piano Variation No-16.mid;Beethoven, Ludwig von - Piano Variation No-17.mid;Beethoven, Ludwig von - Piano Variation No-18.mid;Beethoven, Ludwig von - Piano Variation No-19.mid;Beethoven, Ludwig von - Piano Variation No-20.mid;Beethoven, Ludwig von - Piano Variation No-21.mid;Beethoven, Ludwig von - Piano Variation Waldheim.mid;Beethoven, Ludwig von - Scherzo from Symph No-9 (Arr Liszt, Franz -).mid;Beethoven, Ludwig von - Sonata in A-flat-Maj Op-110 (Zuber04).mid;Beethoven, Ludwig von - Sonata in A-flat-Maj Op-110 1st Mov (Ahn01).mid;Beethoven, Ludwig von - Sonata in A-flat-Maj Op-110 1st Mov (Goh02).mid;Beethoven, Ludwig von - Sonata in A-flat-Maj Op-110 1st Mov (Huang01).mid;Beethoven, Ludwig von - Sonata in A-flat-Maj Op-110 1st Mov (Karpeyev01).mid;Beethoven, Ludwig von - Sonata in A-flat-Maj Op-110 1st Mov (Tang01).mid;Beethoven, Ludwig von - Sonata in A-flat-Maj Op-110 3rd Mov (ParkH01).mid;Beethoven, Ludwig von - Sonata in A-flat-Maj Op-110 4th Mov (Gokcin01).mid;Beethoven, Ludwig von - Sonata in A-flat-Maj Op-26 1st Mov (Garritson01).mid;Beethoven, Ludwig von - Sonata in A-flat-Maj Op-26 1st Mov (Zhao02).mid;Beethoven, Ludwig von - Sonata in A-Maj Op-101 1st Mov (Atzinger01).mid;Beethoven, Ludwig von - Sonata in A-Maj Op-101 1st Mov (Zhdanov01).mid;Beethoven, Ludwig von - Sonata in A-Maj Op-101 3rd Mov (Albright02).mid;Beethoven, Ludwig von - Sonata in C-Maj Op-53 ''Waldstein'' (Sekino05).mid;Beethoven, Ludwig von - Sonata in C-Maj Op-53 1st Mov (Lariviere01).mid;Beethoven, Ludwig von - Sonata in C-Maj Op-53 1st Mov (Shi02).mid;Beethoven, Ludwig von - Sonata in C-Maj Op-53 1st Mov (Sychev01).mid;Beethoven, Ludwig von - Sonata in C-Maj Op-53 1st Mov (Zuber01).mid;Beethoven, Ludwig von - Sonata in C-min Op-111 (Jussow06).mid;Beethoven, Ludwig von - Sonata in C-min Op-111 1st Mov (Jussow02).mid;Beethoven, Ludwig von - Sonata in C-min Op-13 ''Pathetique'' (Na06).mid;Beethoven, Ludwig von - Sonata in C-min Op-13 1st Mov (Erice04).mid;Beethoven, Ludwig von - Sonata in D-Maj Op-28 4th Mov (Floril01).mid;Beethoven, Ludwig von - Sonata in E-flat-Maj Op-27 Last Mov (Taverna01).mid;Beethoven, Ludwig von - Sonata in E-flat-Maj Op-81a ''Les Adieux'' (Zhdanov05).mid;Beethoven, Ludwig von - Sonata in E-Maj Op-109 1st Mov (Lajko01).mid;Beethoven, Ludwig von - Sonata in E-Maj Op-109 1st Mov (Shelest02).mid;Beethoven, Ludwig von - Sonata in E-Maj Op-109 3rd Mov (CaiC01).mid;Beethoven, Ludwig von - Sonata in E-Maj Op-14 No-1 (Tysman05).mid;Beethoven, Ludwig von - Sonata in E-min Op-90 1st Mov (Seredenko01).mid;Beethoven, Ludwig von - Sonata in F-Maj Op-54 1st Mov (WongDoe01).mid;Beethoven, Ludwig von - Sonata in F-min Op-57 1st Mov (Gintov01).mid;Beethoven, Ludwig von - Sonata in F-min Op-57 1st Mov (Na01).mid;Beethoven, Ludwig von - Sonata in F-min Op-57 1st Mov (Yeletskiy01).mid;Beethoven, Ludwig von - Sonata in F-Minor Op-2 No-1 1st Mov (KimG01).mid;Beethoven, Ludwig von - Sonata No-23 Op-57 Appassionata.mid;Beethoven, Ludwig von - Sonata No-29 No-01 (Hammerklavier).mid;Beethoven, Ludwig von - Sonata No-29 No-02 (Hammerklavier).mid;Beethoven, Ludwig von - Sonata No-29 No-03 (Hammerklavier).mid;Beethoven, Ludwig von - Sonata No-29 No-04 (Hammerklavier).mid;Beethoven, Ludwig von - Sonata No-6 (All 3 Mov In One file).mid;Beethoven, Ludwig von - Sonata No-7 (All 4 Mov In One file).mid;Beethoven, Ludwig von - Sonata Op-27 No-2 1st Mov (Meek03).mid;Beethoven, Ludwig von - Sonate Pathetique 01.mid;Beethoven, Ludwig von - Sonate Pathetique 02.mid;Beethoven, Ludwig von - Sonate Pathetique 03.mid;Beethoven, Ludwig von - Sonate Pathetique.mid;Beethoven, Ludwig von - The Moonlight Sonata.mid;Beethoven, Ludwig von - Vars & Fugue in E-flat-Maj ''Eroica'' Op-35 (KimG06).mid;Beethoven, Ludwig von - Vars & fugue in E-flat-Maj ''Eroica'' Op-35 (Taverna04).mid;Bela Bartok - Out Doors Suite Sz 81 (Yang05).mid;Bela Bartok - Out Doors Suite Sz 81 (Yang08).mid;Bela Bartok - Two Romanian Dances Op-8a BB56 (Gasanov05).mid;Boccherini - Minuet.mid;Borodin - Petite Suite 1 Im Kloster.mid;Borodin - Petite Suite 2 Intermezzo.mid;Borodin - Petite Suite 3 Mazurka.mid;Borodin - Petite Suite 4 Mazurka.mid;Borodin - Petite Suite 5 Reverei.mid;Borodin - Petite Suite 6 Serenade.mid;Borodin - Petite Suite 7 Nocturne.mid;Borodin - Petite Suite-1 Im Kloster.mid;Borodin - Petite Suite-2 Intermezzo.mid;Borodin - Petite Suite-3 Mazurka.mid;Borodin - Petite Suite-4 Mazurka.mid;Borodin - Petite Suite-5 Reverei.mid;Borodin - Petite Suite-6 Serenade.mid;Borodin - Petite Suite-7 Nocturne.mid;Brahms - 1st Intermezzo from Op-117.mid;Brahms - 3 Intermezzi Op-117.mid;Brahms - Ballade in D Op-10 No-1.mid;Brahms - Ballade in G Op-118 No-3.mid;Brahms - Capriccio in BOp-76 No-2.mid;Brahms - Fantasia Op-116 No-02 Intermezzo.mid;Brahms - Fantasia Op-116 No-05 Intermezzo.mid;Brahms - Fantasia Op-116 No-06 Intermezzo.mid;Brahms - Fantasie No-6, Intermezzo.mid;Brahms - Haydn, Franz Joseph - Variations (4 tracks GM file).mid;Brahms - Intermezzo In A Major from Op-118.mid;Brahms - Intermezzo in A Op-118 No-2.mid;Brahms - Intermezzo in B-flat Op-117 No-2.mid;Brahms - Intermezzo in C-sharp Op-117 No-3.mid;Brahms - Intermezzo in E-flat Op-117 No-1.mid;Brahms - Intermezzo in E-flat Op-118 No-6.mid;Brahms - Intermezzo No-5, Op-116.mid;Brahms - Intermezzo Op-117 No-3.mid;Brahms - Intermezzo Op-117.mid;Brahms - Intermezzo Op-118.mid;Brahms - Op-09 Piano Variations on Theme (Robert Schumann) F# min.mid;Brahms - Op-117 No-1 Intermezzo in Eb.mid;Brahms - Op-117 No-2 Intermezzo in Bb.mid;Brahms - Op-117 No-3 Intermezzo in D-min.mid;Brahms - Op-118 No-2 Intermezzo in A.mid;Brahms - Op-118 No-6 Intermezzo in Eb.mid;Brahms - Pan's auf StandaIntermezzo.mid;Brahms - Piano Sonata No-01.mid;Brahms - Piano Sonata No-02.mid;Brahms - Piano Sonata No-03.mid;Brahms - Piano Variations Op-9.mid;Brahms - Rhapsodie No-4 in Es-Dur, Op-1.mid;Brahms - Rhapsodie Nr 2 from Op-79.mid;Brahms - Rhapsody in G Op-79 No-2.mid;Brahms - Scherzo Op.4.mid;Brahms - Sonata in C-Maj Op-01 Mov-01.mid;Brahms - Sonata in C-Maj Op-01 Mov-02.mid;Brahms - Sonata in C-Maj Op-01 Mov-03.mid;Brahms - Sonata in C-Maj Op-01 Mov-04.mid;Brahms - The Haendel Variations Op-24.mid;Brahms - Waltz 01.mid;Brahms - Waltz 02.mid;Brahms - Waltz 03.mid;Brahms - Waltz 04.mid;Brahms - Waltz 05.mid;Brahms - Waltz 06.mid;Brahms - Waltz 07.mid;Brahms - Waltz 08.mid;Brahms - Waltz 09.mid;Brahms - Waltz 10.mid;Brahms - Waltz 11.mid;Brahms - Waltz 12.mid;Brahms - Waltz 13.mid;Brahms - Waltz 14.mid;Brahms - Waltz 15.mid;Brahms - Waltz 16.mid;Brahms - Waltz in A-flat Op-39 No-15.mid;Buegmueller - Etudes Op-109 Die Perlen (The Pearls).mid;Buegmueller - Etudes Op-109 Die Quelle (The Fountain).mid;Buegmueller - Etudes Op-109 Gewitter (Thunderstorm).mid;Buegmueller - Etueden Op-109 Die Perlen.mid;Buegmueller - Etueden Op-109 Die Quelle.mid;Buegmueller - Etueden Op-109 Gewitter.mid;Carl Vine - Sonata No-1 2nd Mov (Shi04).mid;Chaminade - Automne (Etude de Concert) Op-35 No-2.mid;Chopin, Frederic Francois - 01-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 01-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 01-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 01-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 02-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 02-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 02-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 02-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 03-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 03-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 03-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 03-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 04-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 04-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 04-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 04-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 05-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 05-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 05-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 05-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 06-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 06-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 06-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 06-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 07-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 07-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 07-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 07-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 08-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 08-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 08-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 08-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 09-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 09-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 09-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 09-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 10-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 10-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 10-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 10-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 11-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 11-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 11-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 11-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 12-of-12 Etudes Op-10.mid;Chopin, Frederic Francois - 12-of-12 Etudes Op-25.mid;Chopin, Frederic Francois - 12-of-12- Etudes Op-10.mid;Chopin, Frederic Francois - 12-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 13-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 14-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 15-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 16-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 17-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 18-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 19-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 20-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 21-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 22-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 23-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 24-of-24 Etudes Op-28.mid;Chopin, Frederic Francois - 2nd Ballade F Maj.mid;Chopin, Frederic Francois - 51 Mazurkas (1 of 4 files).mid;Chopin, Frederic Francois - 51 Mazurkas (1-of-4 files).mid;Chopin, Frederic Francois - 51 Mazurkas (2 of 4 files).mid;Chopin, Frederic Francois - 51 Mazurkas (2-of-4 files).mid;Chopin, Frederic Francois - 51 Mazurkas (3 of 4 files).mid;Chopin, Frederic Francois - 51 Mazurkas (3-of-4 files).mid;Chopin, Frederic Francois - 51 Mazurkas (4 of 4 files).mid;Chopin, Frederic Francois - 51 Mazurkas (4-of-4 files).mid;Chopin, Frederic Francois - Ballade in G minor Op-3.mid;Chopin, Frederic Francois - Ballade No-01 G minor Op-23.mid;Chopin, Frederic Francois - Ballade No-01 G Op-23.mid;Chopin, Frederic Francois - Ballade No-01.mid;Chopin, Frederic Francois - Ballade No-02 F Major Op-38.mid;Chopin, Frederic Francois - Ballade No-02.mid;Chopin, Frederic Francois - Ballade No-02a.mid;Chopin, Frederic Francois - Ballade No-03 A flat Major Op-47.mid;Chopin, Frederic Francois - Ballade No-03.mid;Chopin, Frederic Francois - Ballade No-04 F minor Op-52.mid;Chopin, Frederic Francois - Ballade No-04.mid;Chopin, Frederic Francois - Ballade No-1 in G Op-23.mid;Chopin, Frederic Francois - Ballade No1.mid;Chopin, Frederic Francois - Ballade No2.mid;Chopin, Frederic Francois - Ballade No3.mid;Chopin, Frederic Francois - Ballade No4.mid;Chopin, Frederic Francois - Barcarolle F sharp minor Op-60.mid;Chopin, Frederic Francois - Barcarolle Op-60.mid;Chopin, Frederic Francois - Barcarolle.mid;Chopin, Frederic Francois - Berceuse D flat Major Op-57.mid;Chopin, Frederic Francois - Bracarolle.mid;Chopin, Frederic Francois - Etude A flat Major Op-25 No-01.mid;Chopin, Frederic Francois - Etude A minor Op-25 No-11.mid;Chopin, Frederic Francois - Etude C minor Op-10 No-12 ''Revolutionary''.mid;Chopin, Frederic Francois - Etude C minor Op-25 No-12 (Vladimir Horowitz).mid;Chopin, Frederic Francois - Etude C Op-10 No-12 (Revolutionary).mid;Chopin, Frederic Francois - Etude C Sharp min Op-10.mid;Chopin, Frederic Francois - Etude C sharp minor Op-10 No-03.mid;Chopin, Frederic Francois - Etude C sharp minor Op-10 No-04.mid;Chopin, Frederic Francois - Etude C sharp minor Op-25 No-07.mid;Chopin, Frederic Francois - Etude E flat minor Op-10 No-06.mid;Chopin, Frederic Francois - Etude E Major Op-10 No-03 (Vladimir Horowitz).mid;Chopin, Frederic Francois - Etude E Op-10 No-3.mid;Chopin, Frederic Francois - Etude G flat Major Op-10 No-05.mid;Chopin, Frederic Francois - Etude G flat Major Op-25 No-09.mid;Chopin, Frederic Francois - Etude G sharp minor Op-25 No-06.mid;Chopin, Frederic Francois - Etude G-flat Op-10 No-5 (Black Key).mid;Chopin, Frederic Francois - Etude in A Op-25 No-11.mid;Chopin, Frederic Francois - Etude in A op.25 No-11.mid;Chopin, Frederic Francois - Etude in A-flat Op-25 No-1.mid;Chopin, Frederic Francois - Etude in C Op-10 No-12 (Revolutionary).mid;Chopin, Frederic Francois - Etude in C-sharp Op-25 No-7 (Cello).mid;Chopin, Frederic Francois - Etude in E Op-10 No-3.mid;Chopin, Frederic Francois - Etude in G-flat Op-10 No-5 (Black Key).mid;Chopin, Frederic Francois - Etude in G-sharp Op-25 No-6.mid;Chopin, Frederic Francois - Etude No-03.mid;Chopin, Frederic Francois - Etude No-1, Op-25.mid;Chopin, Frederic Francois - Etude No-11 (The Winter Wind).mid;Chopin, Frederic Francois - Etude No-12, Op-25.mid;Chopin, Frederic Francois - Etude No-2, Op-25.mid;Chopin, Frederic Francois - Etude No-3, Op-25.mid;Chopin, Frederic Francois - Etude No-3.mid;Chopin, Frederic Francois - Etude No-4, Op-25.mid;Chopin, Frederic Francois - Etude Op-10 No-01.mid;Chopin, Frederic Francois - Etude Op-10 No-05 Schwarze-Tasten.mid;Chopin, Frederic Francois - Etude Op-10 No-12.mid;Chopin, Frederic Francois - Etude Op-10 No-5.mid;Chopin, Frederic Francois - Etude Op-10 NoSchwarze-Tasten-.mid;Chopin, Frederic Francois - Etude Op-25 No-01.mid;Chopin, Frederic Francois - Etude Op-25 No-02.mid;Chopin, Frederic Francois - Etude Op-25 No-03.mid;Chopin, Frederic Francois - Etude Op-25 No-04.mid;Chopin, Frederic Francois - Etude Op-25 No-11.mid;Chopin, Frederic Francois - Etude Op-25 No-12.mid;Chopin, Frederic Francois - Etude Op-25, NSturmetA\u030ade.mid;Chopin, Frederic Francois - Fantaisie-Impromptu in C-sharp Op-66.mid;Chopin, Frederic Francois - Fantasie-Impromptu C sharp minor Op-66.mid;Chopin, Frederic Francois - Fantasie-Impromptu in C#.mid;Chopin, Frederic Francois - Fantesie Improptu.mid;Chopin, Frederic Francois - Fantesie-Improptu.mid;Chopin, Frederic Francois - Grand Valse Brillante in Es-Dur.mid;Chopin, Frederic Francois - Impromptu G Flat Maj.mid;Chopin, Frederic Francois - Mazurka A flat Major Op-07 No-04.mid;Chopin, Frederic Francois - Mazurka A flat Major Op-17 No-03.mid;Chopin, Frederic Francois - Mazurka A flat Major Op-24 No-03.mid;Chopin, Frederic Francois - Mazurka A flat Major Op-41 No-04.mid;Chopin, Frederic Francois - Mazurka A flat Major Op-50 No-02.mid;Chopin, Frederic Francois - Mazurka A flat Major Op-59 No-02.mid;Chopin, Frederic Francois - Mazurka A minor (posthum).mid;Chopin, Frederic Francois - Mazurka A minor Op-07 No-02.mid;Chopin, Frederic Francois - Mazurka A minor Op-17 No-04.mid;Chopin, Frederic Francois - Mazurka A minor Op-41 No-02.mid;Chopin, Frederic Francois - Mazurka A minor Op-59 No-01.mid;Chopin, Frederic Francois - Mazurka A minor Op-67 No-04.mid;Chopin, Frederic Francois - Mazurka A minor Op-68 No-04 (posthum).mid;Chopin, Frederic Francois - Mazurka A minor.mid;Chopin, Frederic Francois - Mazurka B flat Major Op-07 No-01.mid;Chopin, Frederic Francois - Mazurka B flat Major Op-17 No-01.mid;Chopin, Frederic Francois - Mazurka B flat minor Op-06 No-04.mid;Chopin, Frederic Francois - Mazurka B flat minor Op-24 No-04.mid;Chopin, Frederic Francois - Mazurka B Major Op-41 No-03.mid;Chopin, Frederic Francois - Mazurka B Major Op-63 No-01.mid;Chopin, Frederic Francois - Mazurka B minor Op-30 No-02.mid;Chopin, Frederic Francois - Mazurka B minor Op-33 No-04.mid;Chopin, Frederic Francois - Mazurka C Major Op-07 No-05.mid;Chopin, Frederic Francois - Mazurka C Major Op-24 No-02.mid;Chopin, Frederic Francois - Mazurka C Major Op-33 No-03.mid;Chopin, Frederic Francois - Mazurka C Major Op-56 No-02.mid;Chopin, Frederic Francois - Mazurka C Major Op-67 No-03.mid;Chopin, Frederic Francois - Mazurka C Major Op-68 No-02 (posthum).mid;Chopin, Frederic Francois - Mazurka C minor Op-30 No-01.mid;Chopin, Frederic Francois - Mazurka C minor Op-56 No-03.mid;Chopin, Frederic Francois - Mazurka C sharp minor Op-06 No-02.mid;Chopin, Frederic Francois - Mazurka C sharp minor Op-30 No-04.mid;Chopin, Frederic Francois - Mazurka C sharp minor Op-50 No-03.mid;Chopin, Frederic Francois - Mazurka C sharp minor Op-63 No-03.mid;Chopin, Frederic Francois - Mazurka C sharp Op-41 No-01.mid;Chopin, Frederic Francois - Mazurka D flat Major Op-30 No-03.mid;Chopin, Frederic Francois - Mazurka D Major Op-33 No-02.mid;Chopin, Frederic Francois - Mazurka E Major Op-06 No-03.mid;Chopin, Frederic Francois - Mazurka E Major Op-56 No-01.mid;Chopin, Frederic Francois - Mazurka E minor Op-17 No-02.mid;Chopin, Frederic Francois - Mazurka F minor Op-07 No-03.mid;Chopin, Frederic Francois - Mazurka F minor Op-63 No-02.mid;Chopin, Frederic Francois - Mazurka F sharp minor Op-06 No-01.mid;Chopin, Frederic Francois - Mazurka F sharp minor Op-59 No-03.mid;Chopin, Frederic Francois - Mazurka G Major Op-50 No-01.mid;Chopin, Frederic Francois - Mazurka G Major Op-67 No-01.mid;Chopin, Frederic Francois - Mazurka G Major Op-68 No-01 (posthum).mid;Chopin, Frederic Francois - Mazurka G minor Op-24 No-01.mid;Chopin, Frederic Francois - Mazurka G minor Op-67 No-02.mid;Chopin, Frederic Francois - Mazurka G minor Op-68 No-02 (posthum).mid;Chopin, Frederic Francois - Mazurka G sharp minor Op-33 No-01.mid;Chopin, Frederic Francois - Mazurka in B Op-33 No-4.mid;Chopin, Frederic Francois - Mazurka in B-flat Op-7 No-1.mid;Chopin, Frederic Francois - Mazurka in C-sharp Op-63 No-3.mid;Chopin, Frederic Francois - Mazurka in F-sharp Op-6 No-1.mid;Chopin, Frederic Francois - Mazurka Op-67 No 01.mid;Chopin, Frederic Francois - Mazurka Op-67 No 02.mid;Chopin, Frederic Francois - Mazurka Op-67 No 03.mid;Chopin, Frederic Francois - Mazurka Op-67 No 04.mid;Chopin, Frederic Francois - Mazurka Op-67 No-01.mid;Chopin, Frederic Francois - Mazurka Op-67 No-02.mid;Chopin, Frederic Francois - Mazurka Op-67 No-03.mid;Chopin, Frederic Francois - Mazurka Op-67 No-04.mid;Chopin, Frederic Francois - Mazurka Op-7 No-01.mid;Chopin, Frederic Francois - Mazurka Op-7 No-02.mid;Chopin, Frederic Francois - Mazurka Op-7 No-1.mid;Chopin, Frederic Francois - Mazurka Op-7 No-2.mid;Chopin, Frederic Francois - Mein Freuden transcribed by Liszt.mid;Chopin, Frederic Francois - Nocturne 01.mid;Chopin, Frederic Francois - Nocturne 02.mid;Chopin, Frederic Francois - Nocturne 03.mid;Chopin, Frederic Francois - Nocturne 04.mid;Chopin, Frederic Francois - Nocturne 05.mid;Chopin, Frederic Francois - Nocturne 06.mid;Chopin, Frederic Francois - Nocturne 07.mid;Chopin, Frederic Francois - Nocturne 08.mid;Chopin, Frederic Francois - Nocturne 09.mid;Chopin, Frederic Francois - Nocturne 10.mid;Chopin, Frederic Francois - Nocturne 11.mid;Chopin, Frederic Francois - Nocturne 12.mid;Chopin, Frederic Francois - Nocturne 13.mid;Chopin, Frederic Francois - Nocturne 14.mid;Chopin, Frederic Francois - Nocturne 15.mid;Chopin, Frederic Francois - Nocturne 16.mid;Chopin, Frederic Francois - Nocturne 17.mid;Chopin, Frederic Francois - Nocturne 18.mid;Chopin, Frederic Francois - Nocturne 19.mid;Chopin, Frederic Francois - Nocturne 20.mid;Chopin, Frederic Francois - Nocturne 21.mid;Chopin, Frederic Francois - Nocturne A flat Major Op-32 No-02.mid;Chopin, Frederic Francois - Nocturne B flat minor Op-09 No-01.mid;Chopin, Frederic Francois - Nocturne B Major Op-09 No-03.mid;Chopin, Frederic Francois - Nocturne B Major Op-32 No-01.mid;Chopin, Frederic Francois - Nocturne B Major Op-62 No-01.mid;Chopin, Frederic Francois - Nocturne C minor Op-48 No-01.mid;Chopin, Frederic Francois - Nocturne C minor.mid;Chopin, Frederic Francois - Nocturne C sharp minor Op-27 No-01.mid;Chopin, Frederic Francois - Nocturne C sharp minor.mid;Chopin, Frederic Francois - Nocturne D flat Major Op-27 No-02.mid;Chopin, Frederic Francois - Nocturne E flat Major Op-09 No-02.mid;Chopin, Frederic Francois - Nocturne E flat Major Op-55 No-02.mid;Chopin, Frederic Francois - Nocturne E Major Op-62 No-02.mid;Chopin, Frederic Francois - Nocturne E minor Op-72 No-01 (Posthum).mid;Chopin, Frederic Francois - Nocturne F Major Op-15 No-01.mid;Chopin, Frederic Francois - Nocturne F minor Op-55 No-01.mid;Chopin, Frederic Francois - Nocturne F sharp Major Op-15 No-02.mid;Chopin, Frederic Francois - Nocturne F sharp minor Op-48 No-02.mid;Chopin, Frederic Francois - Nocturne G Major Op-37 No-02.mid;Chopin, Frederic Francois - Nocturne G minor Op-15 No-03.mid;Chopin, Frederic Francois - Nocturne G minor Op-37 No-01.mid;Chopin, Frederic Francois - Nocturne in B Op-32 No-1.mid;Chopin, Frederic Francois - Nocturne in D-flat Op-27 No-2.mid;Chopin, Frederic Francois - Nocturne in E Op-62 No-2.mid;Chopin, Frederic Francois - Nocturne in E-flat Op-9 No-2.mid;Chopin, Frederic Francois - Nocturne in F-sharp Op-15 No-2.mid;Chopin, Frederic Francois - Nocturne in G Op-37 No-1.mid;Chopin, Frederic Francois - Nocturne No-01.mid;Chopin, Frederic Francois - Nocturne No-02.mid;Chopin, Frederic Francois - Nocturne No-03.mid;Chopin, Frederic Francois - Nocturne No-04.mid;Chopin, Frederic Francois - Nocturne No-05.mid;Chopin, Frederic Francois - Nocturne No-06.mid;Chopin, Frederic Francois - Nocturne No-07.mid;Chopin, Frederic Francois - Nocturne No-08.mid;Chopin, Frederic Francois - Nocturne No-09.mid;Chopin, Frederic Francois - Nocturne No-10.mid;Chopin, Frederic Francois - Nocturne No-11.mid;Chopin, Frederic Francois - Nocturne No-12.mid;Chopin, Frederic Francois - Nocturne No-13.mid;Chopin, Frederic Francois - Nocturne No-14.mid;Chopin, Frederic Francois - Nocturne No-15.mid;Chopin, Frederic Francois - Nocturne No-16.mid;Chopin, Frederic Francois - Nocturne No-17.mid;Chopin, Frederic Francois - Nocturne No-18.mid;Chopin, Frederic Francois - Nocturne No-19.mid;Chopin, Frederic Francois - Nocturne No-20.mid;Chopin, Frederic Francois - Nocturne No-21.mid;Chopin, Frederic Francois - Nocturne Op-15 No-01.mid;Chopin, Frederic Francois - Nocturne Op-15-No-01.mid;Chopin, Frederic Francois - Nocturne Op-27 No-01.mid;Chopin, Frederic Francois - Nocturne Op-27 No-02.mid;Chopin, Frederic Francois - Nocturne Op-27 No-1.mid;Chopin, Frederic Francois - Nocturne Op-27 No-2.mid;Chopin, Frederic Francois - Nocturne Op-33 No-02.mid;Chopin, Frederic Francois - Nocturne Op-33 No-04.mid;Chopin, Frederic Francois - Nocturne Op-33 No-2.mid;Chopin, Frederic Francois - Nocturne Op-33 No-4.mid;Chopin, Frederic Francois - Nocturne Op-61 No-1.mid;Chopin, Frederic Francois - Nocturne Op-61-no-1.mid;Chopin, Frederic Francois - Op-06 Mazurka No-1.mid;Chopin, Frederic Francois - Op-06 Mazurka No-2.mid;Chopin, Frederic Francois - Op-06 Mazurka No-3.mid;Chopin, Frederic Francois - Op-09 Nocturne No-1 In Bb Minor.mid;Chopin, Frederic Francois - Op-09 Nocturne No-1 in Bb-min.mid;Chopin, Frederic Francois - Op-09 Nocturne No-2 in Eb.mid;Chopin, Frederic Francois - Op-09 Nocturne No-3 B.mid;Chopin, Frederic Francois - Op-09 Nocturne No-3.mid;Chopin, Frederic Francois - Op-10 Etude No-01 in C.mid;Chopin, Frederic Francois - Op-10 Etude No-01C.mid;Chopin, Frederic Francois - Op-10 Etude No-02 in A-min.mid;Chopin, Frederic Francois - Op-10 Etude No-02A Minor.mid;Chopin, Frederic Francois - Op-10 Etude No-03 in E.mid;Chopin, Frederic Francois - Op-10 Etude No-03E.mid;Chopin, Frederic Francois - Op-10 Etude No-04 in C#-min.mid;Chopin, Frederic Francois - Op-10 Etude No-04C# Minor.mid;Chopin, Frederic Francois - Op-10 Etude No-05 in Gb.mid;Chopin, Frederic Francois - Op-10 Etude No-05Gb.mid;Chopin, Frederic Francois - Op-10 Etude No-06 in Eb-min.mid;Chopin, Frederic Francois - Op-10 Etude No-06Eb Minor.mid;Chopin, Frederic Francois - Op-10 Etude No-07 in C.mid;Chopin, Frederic Francois - Op-10 Etude No-07C.mid;Chopin, Frederic Francois - Op-10 Etude No-08 in F.mid;Chopin, Frederic Francois - Op-10 Etude No-08F.mid;Chopin, Frederic Francois - Op-10 Etude No-09 in F-min.mid;Chopin, Frederic Francois - Op-10 Etude No-09F Minor.mid;Chopin, Frederic Francois - Op-10 Etude No-10 in Ab.mid;Chopin, Frederic Francois - Op-10 Etude No-10Ab.mid;Chopin, Frederic Francois - Op-10 Etude No-11 in Eb.mid;Chopin, Frederic Francois - Op-10 Etude No-11Eb.mid;Chopin, Frederic Francois - Op-10 Etude No-12 in C-min A.mid;Chopin, Frederic Francois - Op-10 Etude No-12C Minor.mid;Chopin, Frederic Francois - Op-10 No-12 Etude No-12.mid;Chopin, Frederic Francois - Op-15 Nocturne No-1 in F.mid;Chopin, Frederic Francois - Op-15 Nocturne No-2 in F#.mid;Chopin, Frederic Francois - Op-15 Nocturne No-3 In G Minor.mid;Chopin, Frederic Francois - Op-15 Nocturne No-3 in G-min.mid;Chopin, Frederic Francois - Op-21 Mov.2 Larghetto 'piano Concer.mid;Chopin, Frederic Francois - Op-25 Etude No-01 (nick Carter).mid;Chopin, Frederic Francois - Op-25 Etude No-01.mid;Chopin, Frederic Francois - Op-25 Etude No-11 [winter Wind] (.mid;Chopin, Frederic Francois - Op-25 Etude No-11 [Winter Wind].mid;Chopin, Frederic Francois - Op-27 Nocturne No-1 In C# Minor.mid;Chopin, Frederic Francois - Op-27 Nocturne No-1 in C#-min.mid;Chopin, Frederic Francois - Op-27 Nocturne No-2 in Db.mid;Chopin, Frederic Francois - Op-28 Prelude in G-min No-04.mid;Chopin, Frederic Francois - Op-32 Nocturne No-1 in B.mid;Chopin, Frederic Francois - Op-32 Nocturne No-1 In Be.mid;Chopin, Frederic Francois - Op-32 Nocturne No-2 in Ab.mid;Chopin, Frederic Francois - Op-37 Nocturne No-1 In G Minor.mid;Chopin, Frederic Francois - Op-37 Nocturne No-1 in G-min.mid;Chopin, Frederic Francois - Op-37 Nocturne No-2 in G.mid;Chopin, Frederic Francois - Op-37 Nocturne No-2 In Ge.mid;Chopin, Frederic Francois - Op-48 Nocturne No-1 In C Minor.mid;Chopin, Frederic Francois - Op-48 Nocturne No-1 in C-min.mid;Chopin, Frederic Francois - Op-48 Nocturne No-2 In F# Minor.mid;Chopin, Frederic Francois - Op-48 Nocturne No-2 in F#-min.mid;Chopin, Frederic Francois - Op-53 Polonaise In Ab [Heroic].mid;Chopin, Frederic Francois - Op-53 Polonaise in Ab [heroic].mid;Chopin, Frederic Francois - Op-55 Nocturne No-1 In F Minor.mid;Chopin, Frederic Francois - Op-55 Nocturne No-1 in F-min.mid;Chopin, Frederic Francois - Op-55 Nocturne No-2 in Eb.mid;Chopin, Frederic Francois - Op-58 Mov-01 Allegro sonata No-3.mid;Chopin, Frederic Francois - Op-58 Mov-02 Scherzo sonata No-3.mid;Chopin, Frederic Francois - Op-58 Mov-03 Largo sonata No-3.mid;Chopin, Frederic Francois - Op-58 Mov-04 Presto sonata No-3.mid;Chopin, Frederic Francois - Op-58 Mov.1 Allegro Sonata No.3 In.mid;Chopin, Frederic Francois - Op-58 Mov.2 Scherzo Sonata No.3 In.mid;Chopin, Frederic Francois - Op-58 Mov.3 Largo Sonata No.3 In B.mid;Chopin, Frederic Francois - Op-58 Mov.4 Presto Sonata No.3 In .mid;Chopin, Frederic Francois - Op-62 Nocturne No-1 in B.mid;Chopin, Frederic Francois - Op-62 Nocturne No-2 in E.mid;Chopin, Frederic Francois - Op-62 Nocturne No-2 In Ee.mid;Chopin, Frederic Francois - Op-64 Waltz in C#-min No-2.mid;Chopin, Frederic Francois - Op-64 Waltz in Db No-1.mid;Chopin, Frederic Francois - Op-66 'fantaisie-impromptu In C# Mi.mid;Chopin, Frederic Francois - Op-66 Fantaisie-impromptu in C#.mid;Chopin, Frederic Francois - Op-70 Waltz No-2.mid;Chopin, Frederic Francois - Op-72 Nocturne No-1 In E Minor.mid;Chopin, Frederic Francois - Op-72 Nocturne No-1 in E-min.mid;Chopin, Frederic Francois - Op.64 Waltz In C# Minor No.2.mid;Chopin, Frederic Francois - Op.64 Waltz In Db No.1.mid;Chopin, Frederic Francois - Op.70 Waltz No.2.mid;Chopin, Frederic Francois - Piano-Concerto No-02 3rd Mov.mid;Chopin, Frederic Francois - Polonaise A Flat Maj ''Heroic''.mid;Chopin, Frederic Francois - Polonaise A flat Major Op-53 Eroic.mid;Chopin, Frederic Francois - Polonaise A Major Op-40 No-01 Military.mid;Chopin, Frederic Francois - Polonaise F sharp minor Op-44.mid;Chopin, Frederic Francois - Polonaise in A Op-40 No-1 (Military).mid;Chopin, Frederic Francois - Polonaise in A-flat Op-53.mid;Chopin, Frederic Francois - Polonaise in Ab major Op-.mid;Chopin, Frederic Francois - Polonaise No-06 (Heroique).mid;Chopin, Frederic Francois - Polonaise-Fantasie A flat Major Op-61.mid;Chopin, Frederic Francois - Prelude in A Op-28 No-7.mid;Chopin, Frederic Francois - Prelude in B Op-28 No-5.mid;Chopin, Frederic Francois - Prelude in D-flat Op-28 No-15 (Raindrop).mid;Chopin, Frederic Francois - Prelude in E Op-28 No-4.mid;Chopin, Frederic Francois - Prelude in F-sharp Op-28 No-8.mid;Chopin, Frederic Francois - Prelude No-1, Op-28.mid;Chopin, Frederic Francois - Prelude No-10.mid;Chopin, Frederic Francois - Prelude No-11.mid;Chopin, Frederic Francois - Prelude No-12, Op-28.mid;Chopin, Frederic Francois - Prelude No-13, Op-28.mid;Chopin, Frederic Francois - Prelude No-14, Op-28.mid;Chopin, Frederic Francois - Prelude No-15, Op-28.mid;Chopin, Frederic Francois - Prelude No-16, Op-28.mid;Chopin, Frederic Francois - Prelude No-17, Op-28.mid;Chopin, Frederic Francois - Prelude No-18, Op-28.mid;Chopin, Frederic Francois - Prelude No-19, Op-28.mid;Chopin, Frederic Francois - Prelude No-2, Op-28.mid;Chopin, Frederic Francois - Prelude No-20, Op-28.mid;Chopin, Frederic Francois - Prelude No-21, Op-28.mid;Chopin, Frederic Francois - Prelude No-22, Op-28.mid;Chopin, Frederic Francois - Prelude No-23, Op-28.mid;Chopin, Frederic Francois - Prelude No-24, Op-28.mid;Chopin, Frederic Francois - Prelude No-3, Op-28.mid;Chopin, Frederic Francois - Prelude No-4, Op-28.mid;Chopin, Frederic Francois - Prelude No-5, Op-28.mid;Chopin, Frederic Francois - Prelude No-6, Op-28.mid;Chopin, Frederic Francois - Prelude No-7.mid;Chopin, Frederic Francois - Prelude No-8.mid;Chopin, Frederic Francois - Prelude No-9.mid;Chopin, Frederic Francois - Prelude Op-28 No-01.mid;Chopin, Frederic Francois - Prelude Op-28 No-02.mid;Chopin, Frederic Francois - Prelude Op-28 No-03.mid;Chopin, Frederic Francois - Prelude Op-28 No-04.mid;Chopin, Frederic Francois - Prelude Op-28 No-05.mid;Chopin, Frederic Francois - Prelude Op-28 No-06.mid;Chopin, Frederic Francois - Prelude Op-28 No-07.mid;Chopin, Frederic Francois - Prelude Op-28 No-08.mid;Chopin, Frederic Francois - Prelude Op-28 No-09.mid;Chopin, Frederic Francois - Prelude Op-28 No-10.mid;Chopin, Frederic Francois - Prelude Op-28 No-11.mid;Chopin, Frederic Francois - Prelude Op-28 No-12.mid;Chopin, Frederic Francois - Prelude Op-28 No-13.mid;Chopin, Frederic Francois - Prelude Op-28 No-14.mid;Chopin, Frederic Francois - Prelude Op-28 No-15.mid;Chopin, Frederic Francois - Prelude Op-28 No-16.mid;Chopin, Frederic Francois - Prelude Op-28 No-17.mid;Chopin, Frederic Francois - Prelude Op-28 No-18.mid;Chopin, Frederic Francois - Prelude Op-28 No-19.mid;Chopin, Frederic Francois - Prelude Op-28 No-20.mid;Chopin, Frederic Francois - Prelude Op-28 No-21.mid;Chopin, Frederic Francois - Prelude Op-28 No-22.mid;Chopin, Frederic Francois - Prelude Op-28 No-23.mid;Chopin, Frederic Francois - Prelude Op-28 No-24.mid;Chopin, Frederic Francois - Raindrop Prelude.mid;Chopin, Frederic Francois - Scherzo in b-moll Op-31.mid;Chopin, Frederic Francois - Scherzo in C-sharp.mid;Chopin, Frederic Francois - Scherzo No-3.mid;Chopin, Frederic Francois - Sonata No-03 B min movement 1.mid;Chopin, Frederic Francois - Sonata No-03 B min movement 2.mid;Chopin, Frederic Francois - Sonata No-03 B min movement 3.mid;Chopin, Frederic Francois - Sonata No-03 B min movement 4.mid;Chopin, Frederic Francois - Sonata No-03.mid;Chopin, Frederic Francois - Sonate No-02 B-min Op-35 Mov-01.mid;Chopin, Frederic Francois - Sonate No-02 B-min Op-35 Mov-02 .mid;Chopin, Frederic Francois - Sonate No-02 B-min Op-35 Mov-03.mid;Chopin, Frederic Francois - Sonate No-02 B-min Op-35 Mov-04.mid;Chopin, Frederic Francois - Sonate No-03.mid;Chopin, Frederic Francois - Sonate Op-35, 1 Satz.mid;Chopin, Frederic Francois - Sonate Op-35, 2 Satz.mid;Chopin, Frederic Francois - Sonate Op-35, 4 Satz.mid;Chopin, Frederic Francois - Sonate Op-35, Trauermarsch.mid;Chopin, Frederic Francois - Waltz in C-sharp Op-64 No-2.mid;Chopin, Frederic Francois - Waltz in D-flat Op-64 No-1 (Minute).mid;Chopin, Frederic Francois - Waltz in E Op-Posth..mid;Chopin, Frederic Francois - Waltz in E Op-Posth.mid;Chopin, Frederic Francois - Waltz in E-flat Op-18.mid;Chopin, Frederic Francois - Waltz Op-Posthume.mid;Chopin, Frederic Francois - Waltz Opus Posthume.mid;Chopin, Frederic Francois - Winter Wind Etude Op-25 No-011.mid;Clementi - Sonatina Op-36 No-01 part-A.mid;Clementi - Sonatina Op-36 No-01 part-B.mid;Clementi - Sonatina Op-36 No-01 part-C.mid;Clementi - Sonatina Op-36 No-02 part-A.mid;Clementi - Sonatina Op-36 No-02 part-B.mid;Clementi - Sonatina Op-36 No-02 part-C.mid;Clementi - Sonatina Op-36 No-03 part-A.mid;Clementi - Sonatina Op-36 No-03 part-B.mid;Clementi - Sonatina Op-36 No-03 part-C.mid;Clementi - Sonatina Op-36 No-04 part-A.mid;Clementi - Sonatina Op-36 No-04 part-B.mid;Clementi - Sonatina Op-36 No-04 part-C.mid;Clementi - Sonatina Op-36 No-05 part-A.mid;Clementi - Sonatina Op-36 No-05 part-B.mid;Clementi - Sonatina Op-36 No-05 part-C.mid;Clementi - Sonatina Op-36 No-06 part-A.mid;Clementi - Sonatina Op-36 No-06 part-B.mid;Debussy, Claude - 2 Preludes Ondine & Les Tierces Alternees (kolessova).mid;Debussy, Claude - Afternoon of a Fawn 56027A.mid;Debussy, Claude - Arabesque No-01 in E (seq-01).mid;Debussy, Claude - Arabesque No-01 in E (seq-02).mid;Debussy, Claude - Arabesque No-01 in E (seq-03).mid;Debussy, Claude - Arabesque No-01.mid;Debussy, Claude - Arabesque No-1 in E.mid;Debussy, Claude - Arabesque No-2 in G.mid;Debussy, Claude - Childrens Corner.mid;Debussy, Claude - Clair de Lune (seq-01).mid;Debussy, Claude - Clair de Lune (seq-02).mid;Debussy, Claude - Clair de lune.mid;Debussy, Claude - Claire De Lune.mid;Debussy, Claude - Danse.mid;Debussy, Claude - Doctor Gradys ad Parnassum (Children's Corner).mid;Debussy, Claude - Doctor Gradys ad Parnassum (Children's Corner.mid;Debussy, Claude - En Bateau (from Petite Suite).mid;Debussy, Claude - Engulfed Cathedral (from Preludes Book I).mid;Debussy, Claude - Etude No-6, Book I, Pour les huits doigts (Lisiecki09).mid;Debussy, Claude - Feux d'artifice from Book II (Lin16).mid;Debussy, Claude - from 12 Etudes (DeTurck).mid;Debussy, Claude - from Preludes, Book I Les collines d'Anacapri (Ko15).mid;Debussy, Claude - from Preludes, Book I Voiles (Ko16).mid;Debussy, Claude - Girl With the Flaxen Hair.mid;Debussy, Claude - Golliwog's Cake Walk (Children's Corner) seq-01.mid;Debussy, Claude - Golliwog's Cake Walk (Children's Corner) seq-02.mid;Debussy, Claude - Golliwog's Cake Walk (Children's Corner).mid;Debussy, Claude - Hommage a Rameau.mid;Debussy, Claude - Images Book I (Tak07).mid;Debussy, Claude - Images, Book I, Reflets dans l'eau (Kleisen11).mid;Debussy, Claude - Images, Book II, Poissons d'or (Kleisen12).mid;Debussy, Claude - Jardins Sous La Pluie.mid;Debussy, Claude - Jimbo's Lullaby (Children's Corner).mid;Debussy, Claude - Les Collines d'Anacapri from Book I (Lin14).mid;Debussy, Claude - Ondine from Book II (Lin15).mid;Debussy, Claude - Pagodas from Estampes No-1 (Khmara06).mid;Debussy, Claude - Pour les arpeges composees from Douze Etudes (DeTurk).mid;Debussy, Claude - Prelude No-24 Fireworks (Huang08).mid;Debussy, Claude - Preludes Book I No 2 Voiles (Sails)-062BRD.mid;Debussy, Claude - Preludes Book I No. 10 La cathedrale engloutie (Engulfed)-041BRD.mid;Debussy, Claude - Reflections in the Water.mid;Debussy, Claude - Reflets dans l'eau (Reflections in the Water).mid;Debussy, Claude - Reverie.mid;Debussy, Claude - Sarabande.mid;Debussy, Claude - Serenade for the Doll (Children's Corner).mid;Debussy, Claude - Suite Bergamasque (1905) Clair de Lune.mid;Debussy, Claude - Suite Bergamasque (1905) Menuet.mid;Debussy, Claude - Suite Bergamasque (1905) Passe pied.mid;Debussy, Claude - Suite Bergamasque (1905) Prelude.mid;Debussy, Claude - Suite Bergamasque Clair de Lune.mid;Debussy, Claude - Suite Bergamasque Menuet.mid;Debussy, Claude - Suite Bergamasque Passepied.mid;Debussy, Claude - Suite Bergamasque Prelude.mid;Debussy, Claude - The Engulfed Cathedral.mid;Debussy, Claude - The Girl With The Flaxen Hair.mid;Debussy, Claude - The Little Shepherd (Children's Corner).mid;Debussy, Claude - The Snow is Dancing (Children's Corner).mid;Debussy, Claude - Valse - La plus que lente.mid;Debussy, Claude Achille - Arabesque No-1.mid;Debussy, Claude Achille - Clair De Lune.mid;Debussy, Claude Achille - Sarabande.mid;Domenico Scarlatti - Sonata in B-min K-197 (Staupe08).mid;Domenico Scarlatti - Sonata in B-min L-33 (Na05).mid;Domenico Scarlatti - Sonata in C-Maj K-179 (Staupe07).mid;Domenico Scarlatti - Sonata in D-Maj L-465 (Zhao01).mid;Domenico Scarlatti - Sonata in G-Maj K-146 (Staupe01).mid;Domenico Scarlatti - Sonata in G-Maj K-146 (Staupe09).mid;Domenico Scarlatti - Sonatas in B-min K-27 & in D-Maj K-119 (CaiC07).mid;Dvorak - American Suite.mid;Dvorak, Antonin - Op-098 American Suite.mid;Dvorak, Antonin - Op-101 No-1 Humoresque.mid;Dvorak, Antonin - Op-101 No-5 Humoresque in A-min.mid;Elgar - Enigma Variations (Complete).mid;Elgar - Enigma Variations.mid;Elgar - Imperial March (Church Organ).mid;Elgar - Imperial March.mid;Elgar - Nimrod (from The Enigma Variations).mid;Elgar - Pomp And Circumstance March No-04.mid;Elgar - Pomp and Circumstance No-1.mid;Faure - Claire de lune Op-46 No-2.mid;Faure - Dolly Suite 01-of-06.mid;Faure - Dolly Suite 02-of-06.mid;Faure - Dolly Suite 03-of-06.mid;Faure - Dolly Suite 04-of-06.mid;Faure - Dolly Suite 05-of-06.mid;Faure - Dolly Suite 06-of-06.mid;Faure - Impromptu in F minor Op-31 No-2.mid;Faure - Impromptu No-03.mid;Faure - Impromptu.mid;Faure - Nocturne No-04.mid;Faure - Romance No-03.MID;Faure - Romance Without Words.mid;Franz Joseph Haydn, Franz Joseph - Sonata Hob XVI-23 1st Mov (ParkJ03).mid;Franz Joseph Haydn, Franz Joseph - Sonata in A-flat-Maj Hob XVI-46 1st Mov (Shilyaev01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in A-Maj 1st Mov (Kunz01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in C-Maj Hob XVI-50 (Shi07).mid;Franz Joseph Haydn, Franz Joseph - Sonata in C-Maj Hob XVI-50 1st Mov (Tak01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in C-Maj Hob XVI-50 1st Mov (Toscano03).mid;Franz Joseph Haydn, Franz Joseph - Sonata in C-Maj XVI-50 1st Mov (Georgieva01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in C-min Hob XVI-20 1st Mov (ChenL01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in C-min Hob XVI-20 1st Mov (Terenkova01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in C-min Hob XVI-20 1st Mov (Uiasiuk01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in D-Maj Hob XVI-24 1st Mov (Sekino01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in D-Maj Hob XVI-42 1st Mov (Faliks01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in E-flat-Maj Hob XVI-28 1st Mov (Gryaznov01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in E-flat-Maj Hob XVI-49 1st Mov (Hou01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in E-flat-Maj Hob XVI-49 1st Mov (Soukhovetski01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in E-flat-Maj Hob XVI-52 1st Mov (Travinskyy0)1.mid;Franz Joseph Haydn, Franz Joseph - Sonata in E-Maj Hob XVI-31 1st Mov (Masycheva01).mid;Franz Joseph Haydn, Franz Joseph - Sonata in E-min Hob XVI-34 1st Mov (Yang02).mid;Franz Joseph Haydn, Franz Joseph - Sonata in F-Maj XVI-23 1st Mov (Golubeva01).mid;Franz Liszt, Franz - Sonata in B-min S-178 (Gasanov06).mid;Franz Liszt, Franz - Sonata in B-min S-178 (Yeletskiy05).mid;Franz Liszt, Franz - Sonata in B-min S-178 (Zuber07).mid;Franz Liszt, Franz - Tarantelle di bravura S386 (Taverna08).mid;Franz Schubert - Sonata in A-min D845 (Na10).mid;Franz Schubert - Sonata in B-flat-Maj D960 (Rozanski10).mid;Franz Schubert - Sonata in B-flat-Maj D960 (Zuber08).mid;Franz Schubert - Sonata in C-Maj D840 (Taverna10).mid;Franz Schubert - Sonata in C-min D958 (KimG10).mid;Franz Schubert - Sonata in C-min D958 (Shi10).mid;Franz Schubert - Sonata in C-min D958 (Tysman09).mid;Franz Schubert - Sonata in G-Maj D894 (Yeletskiy08).mid;Frederic Chopin, Frederic Francois - Andante Spianato & Grande Polonaise Brillante Op-22 (Soukhovetski04).mid;Frederic Chopin, Frederic Francois - Andante Spianato & Grande Polonaise Brillante Op-22 (Soukhovetski07).mid;Frederic Chopin, Frederic Francois - Andante Spianato & Grande Polonaise Brillante Op-22 (Zuber03).mid;Frederic Chopin, Frederic Francois - Andante Spianato & Grande Polonaise Brillante Op-22 (Zuber06).mid;Frederic Chopin, Frederic Francois - Ballade No-2 in F-Maj Op-38 (Gasanov04).mid;Frederic Chopin, Frederic Francois - Ballade No-2 in F-Maj Op-38 (Gasanov08).mid;Frederic Chopin, Frederic Francois - Barcarolle Op-60 (Rozanski07).mid;Frederic Chopin, Frederic Francois - Barcarolle Op-60 (Wilshire04).mid;Frederic Chopin, Frederic Francois - Etudes Op-10 Nos 1 2 3 & 4 (Zhao03).mid;Frederic Chopin, Frederic Francois - Fantasie in F-min Op-49 (Toscano01).mid;Frederic Chopin, Frederic Francois - Fantasy in F-min Op-49 (Jussow10).mid;Frederic Chopin, Frederic Francois - Nocturne in B-Maj Op-9 No-3 (Garritson06).mid;Frederic Chopin, Frederic Francois - Nocturne in E-Maj Op-62 No-2 (Jussow09).mid;Frederic Chopin, Frederic Francois - Polonaise-Fantasy in A-flat-Maj Op-61 (CaiC09).mid;Frederic Chopin, Frederic Francois - Polonaise-Fantasy in A-flat-Maj Op-61 (KimG07).mid;Frederic Chopin, Frederic Francois - Polonaise-Fantasy Op-61 (ChenL03).mid;Frederic Chopin, Frederic Francois - Preludes Op-28 Nos 1-12 (Tysman04).mid;Frederic Chopin, Frederic Francois - Scherzo No-2 in B-flat-min Op-31 (Jussow04).mid;Frederic Chopin, Frederic Francois - Scherzo No-2 in B-flat-min Op-31 (Jussow11).mid;Frederic Chopin, Frederic Francois - Scherzo No-4 in E-Maj Op-54 (Taverna05).mid;Frederic Chopin, Frederic Francois - Sonata in B-min Op-58 1st Mov (Gokcin02).mid;George Frederic Handel - Suite No-3 in D-min HWV428 (Prelude Allemande Courante Air) (Shi03).mid;George Frederic Handel - Suite No-3 in D-min HWV428 (Shi05).mid;Grainger - Country Gardens.mid;Grainger - Irish tune from County Derry.mid;Grainger - Shepherd's Hey.mid;Granados - Danza Espanola No-3.mid;Granados - Danza Espanola Oriental.mid;Granados - Danza Espanola Villanesca.mid;Granados - Danzas Espanolas (1900) N0-04 Villanesca.mid;Granados - Danzas Espanolas (1900) No-02 Oriental.mid;Granados - Danzas Espanolas (1900) No-3 Zarabanda.mid;Granados - El Pelele.mid;Granados - Oriental.mid;Greig - Air (Holberg).mid;Greig - Anitra's Dance (Peer Gynt).mid;Greig - Arietta Op-12 No-1.mid;Greig - Ase's Death (Peer Gynt).mid;Greig - Elfin Dance Op-12.mid;Greig - from Holbergs Time Suite.mid;Greig - Gavotte (Holberg).mid;Greig - Grieg Lyrische Stucke Op-43 Nr.mid;Greig - Hochzeitstag auf Troldhaugen Op.mid;Greig - I Love Thee.mid;Greig - In the Hall of the Mountain King (Peer Gynt).mid;Greig - Kobold Op-71, No-3.mid;Greig - Lyric Pieces Op-12 No-12 Valse.mid;Greig - Lyrische Norwegischer Tan.mid;Greig - Lyrische Stucke Buch-01 (1867) Op-12 No-02 Waltz.mid;Greig - Lyrische Stucke Buch-01 (1867) Op-12 No-03 Watchman's Song.mid;Greig - Lyrische Stucke Buch-01 (1867) Op-12 No-04 Fairy Dance.mid;Greig - Lyrische Stucke Buch-02 Op-38 No-04 (1883) Halling.mid;Greig - Lyrische Stucke Buch-03 (1886) Op-43 No-01 Butterfly.mid;Greig - Lyrische Stucke Buch-03 (1886) Op-43 No-02 Solitary Traveller.mid;Greig - Lyrische Stucke Buch-03 (1886) Op-43 No-04 Little Bird.mid;Greig - Lyrische Stucke Buch-05 (1891) Op-54 No-03 March of the Dwarfs.mid;Greig - Lyrische Stucke Buch-08 Op-65 No-06 Hochzeitstag auf (Wedding Day at) Troldhaugen.mid;Greig - Lyrische Stucke Buch-10 Op-71 No-03 (1901) Puck.mid;Greig - Lyrische Stucke Op-12 Nr.mid;Greig - Lyrische Stucke Op-43 No.mid;Greig - March of the Dwarfs Op-54 No-3.mid;Greig - Morning Mood (Peer Gynt).mid;Greig - Nocturne Op-54 No-4.mid;Greig - Op-12 No-01 (Poetic Tone Pictures).mid;Greig - Op-12 No-02 (Poetic Tone Pictures).mid;Greig - Op-12 No-03 (Poetic Tone Pictures).mid;Greig - Op-12 No-04 (Poetic Tone Pictures).mid;Greig - Op-12 No-05 (Poetic Tone Pictures).mid;Greig - Op-12 No-06 (Poetic Tone Pictures).mid;Greig - Op-12 No-07 (Poetic Tone Pictures).mid;Greig - Op-12 No-08 (Poetic Tone Pictures).mid;Greig - Peer Gynt Suite No-1 for Piano.mid;Greig - Preludium (Holberg).mid;Greig - Rigaudon (Holberg).mid;Greig - Sarabande (Holberg).mid;Greig - Solvejg's Song Op-52 No-4.mid;Greig - The Bird Op-43 No-4.mid;Greig - The Butterfly Op-43 No-1.mid;Greig - To Spring.mid;Greig - To the Spring Op-43 No-6.mid;Greig - To The Spring.mid;Greig - Vi\u0302glein Op-43, No-4.mid;Greig - Wachterlied Op12, No-3.mid;Greig - Wedding Day at Troldhaugen Op-65 No-6.mid;Greig - Wedding Day At Troldhaugen.mid;Greig - Zug der Zwerge Op-54, No-3.mid;Gyorgy Ligeti - Etude No-8 ''Fern'' (Taverna06).mid;Gyorgy Ligeti - Two Etudes ''Fanfare'' & ''Autumn in Warsaw'' (WongDoe03).mid;Haydn, Franz Joseph - Klaviersonate in G-Maj Hoboken XVI-40 (1784) 1st Mov.mid;Haydn, Franz Joseph - Klaviersonate in G-Maj Hoboken XVI-40 (1784) 2nd Mov.mid;Haydn, Franz Joseph - Klaviersonate in1 Satz.mid;Haydn, Franz Joseph - Klaviersonate in2 Satz.mid;Haydn, Franz Joseph - Op-Minuet in Eb.mid;Haydn, Franz Joseph - Op-Mov-01 piano sonata No-37 in D.mid;Haydn, Franz Joseph - Op-Mov-01 piano sonata No-52 in Eb.mid;Haydn, Franz Joseph - Op-Mov-03 Presto piano sonata No-52.mid;Haydn, Franz Joseph - Op-No-1 in D German Dance.mid;Haydn, Franz Joseph - Op-No-5 in D German Dance.mid;Haydn, Franz Joseph - Op-No-6 in E German Dance.mid;Haydn, Franz Joseph - Op-Scherzo in F sonatina No-4.mid;Haydn, Franz Joseph - Sonata in E-flat Mvt-1 (Hob.XVI-52).mid;Haydn, Franz Joseph - Sonata in E-flat Mvt-2 (Hob.XVI-52).mid;Haydn, Franz Joseph - Sonata in E-flat Mvt-3 (Hob.XVI-52).mid;Haydn, Franz Joseph - Sonate No-52.mid;Joplin - The Entertainer.mid;Karol Szymanowski - Mazurkas Op-50 Nos 1 2 & 3 (Zuber05).mid;Ketelbey - in A Monastery Garden.mid;Liszt, Franz - ''Standchen'' ''Auf dem Wasser zu singen'' (Travinskyy02).mid;Liszt, Franz - 1st Concerto (version for 2 pianos).mid;Liszt, Franz - Ave Maria.mid;Liszt, Franz - Benediction To God In Solitude.mid;Liszt, Franz - Canzone from Venezia e Napoli.mid;Liszt, Franz - Canzone Venezia.mid;Liszt, Franz - Concert Etude No-3 in D-flat (Un Sospiro).mid;Liszt, Franz - Eroica (transcendental Etude).mid;Liszt, Franz - Eroica Etude Transcendentale.mid;Liszt, Franz - Etude No-1 aus Grandes Etudes d.mid;Liszt, Franz - Etude No-2 aus Grandes Etudes d.mid;Liszt, Franz - Etude No-3 ausLa Campanella.mid;Liszt, Franz - Etude No-4 aus Grandes Etudes d.mid;Liszt, Franz - Etude No-5 aus Grandes Etudes d.mid;Liszt, Franz - Etude No-6 aus Grandes Etudes d.mid;Liszt, Franz - Etudes d'execution Mazeppa.mid;Liszt, Franz - Etudes d'executon Wilde Jagd.mid;Liszt, Franz - Feux Follet (transcendental Etude).mid;Liszt, Franz - Feux Follets Etude Transcendentale.mid;Liszt, Franz - Franz Liszt Etudes Feux Follets (Ir.mid;Liszt, Franz - Gondoliera from Venezia e Napoli.mid;Liszt, Franz - Gondoliera Venezia.mid;Liszt, Franz - Hungarian Rhapsody No-012.mid;Liszt, Franz - Hungarian Rhapsody No-015.mid;Liszt, Franz - Hungarian Rhapsody No-12.mid;Liszt, Franz - Hungarian Rhapsody No-15 (Rakoczy March).mid;Liszt, Franz - Hungarian Rhapsody No-2.mid;Liszt, Franz - Impromptu Venezia.mid;Liszt, Franz - La Campanella (from Paganinis 2nd Conc).mid;Liszt, Franz - Les Cloches De Geneve.mid;Liszt, Franz - Liebestraum No-3 (vers a).mid;Liszt, Franz - Liebestraum No-3 (vers b).mid;Liszt, Franz - Liebestraum No-3.mid;Liszt, Franz - Liebestraume No-1.mid;Liszt, Franz - Liebestraume No-3.mid;Liszt, Franz - Mazeppa (transcendental Etude).mid;Liszt, Franz - Mazeppa Etude Transcendentale.mid;Liszt, Franz - Mephisto Valse No1.mid;Liszt, Franz - Mephisto Waltz No-01.mid;Liszt, Franz - Mephisto Waltz.mid;Liszt, Franz - Mov-01 & 2 Concerto in Eb.mid;Liszt, Franz - Mov-03 Concerto in Eb.mid;Liszt, Franz - Mov-04 Concerto in Eb.mid;Liszt, Franz - No-1 Mephisto Waltz.mid;Liszt, Franz - No-1 Valse Oubliee.mid;Liszt, Franz - No-13 Hungarian Raphsody.mid;Liszt, Franz - No-2 Hungarian Raphsody.mid;Liszt, Franz - No-2 Valse Oubliee.mid;Liszt, Franz - No-3 Mephisto Waltz.mid;Liszt, Franz - Obermanns Valley (from The Swiss Book of Annees De Pelerinage).mid;Liszt, Franz - On the Edge Of a Spring.mid;Liszt, Franz - Paganini Etude No-3 (La Campanella).mid;Liszt, Franz - Petrarch Sonnet No 104 (from The Italian Book of Annees De Pelerinage).mid;Liszt, Franz - Petrarch Sonnet No-0104.mid;Liszt, Franz - Petrarch Sonnet No-0123.mid;Liszt, Franz - Petrarch Sonnet.mid;Liszt, Franz - Polonaise in E No-2.mid;Liszt, Franz - Reminiscnenes do Don Juan.mid;Liszt, Franz - Rhapsodie No-10.mid;Liszt, Franz - Rhapsodie No-12.mid;Liszt, Franz - Rhapsodie No-15.mid;Liszt, Franz - Rhapsodie No-9 - Pesther Karnev.mid;Liszt, Franz - sonata in B-min.mid;Liszt, Franz - Sonate B Minor.mid;Liszt, Franz - Tarantella from Venezia e Napoli.mid;Liszt, Franz - Transcendental Etude ''Eroica''.mid;Liszt, Franz - Transcendental Etude ''Mazeppa''.mid;Liszt, Franz - Transcendental Etude ''Paysage''.mid;Liszt, Franz - Un Sospiro.mid;Liszt, Franz - Ungarische Rhapsodie No-2.mid;Liszt, Franz - Vallee d'Obermann.mid;Liszt, Franz - Valse Oubliee.mid;Liszt, Franz - Valse-Impromptu.mid;Liszt, Franz - Venezia E Napoli Canzone.mid;Liszt, Franz - Venezia E Napoli Gondola.mid;Liszt, Franz - Venezia E Napoli Tarantel.mid;Lizst, Franz - Etude No-1 aus Grandes Etudes.mid;Lizst, Franz - Etude No-2 aus Grandes Etudes.mid;Lizst, Franz - Etude No-3 aus La Campanella.mid;Lizst, Franz - Etude No-4 aus Grandes Etudes.mid;Lizst, Franz - Etude No-5 aus Grandes Etudes.mid;Lizst, Franz - Etude No-6 aus Grandes Etudes.mid;Lizst, Franz - Etudes Feux Follets.mid;Lizst, Franz - Etudes Mazeppa.mid;Lizst, Franz - Etudes Wilde Jagd.mid;Lizst, Franz - Liebestraum No-3.mid;Lizst, Franz - Reminiscnenes do Don Juan.mid;Lizst, Franz - Rhapsodie No-10.mid;Lizst, Franz - Rhapsodie No-12.mid;Lizst, Franz - Rhapsodie No-15.mid;Lizst, Franz - Rhapsodie No-9 - Pesther Karnev.mid;Lizst, Franz - Ungarische Rhapsodie No-2.mid;Lowell Liebermann - Gargoyles Op-29 3rd Mov (Atzinger04).mid;MacDowell E - To a Wild Rose Op-51.mid;Mendelssohn - Andante and Rondo Capriciosso Op-14.mid;Mendelssohn - Lieder ohne Wort Venetianisches G.mid;Mendelssohn - Lieder ohne Worte Morgenlied.mid;Mendelssohn - Lieder ohne Worte Op-30 No-1.mid;Mendelssohn - Lieder ohne Worte Trauermarsch.mid;Mendelssohn - Lieder ohne Worte Volkslied.mid;Mendelssohn - Piano Concerto In G Minor (1st Mov).mid;Mendelssohn - Song of Spring Op-62 No-6.mid;Mendelssohn - Song Without Words C Maj.mid;Mendelssohn - Song Without Words Op-19 No-01.mid;Mendelssohn - Song without Words Op-19 No-1.mid;Mendelssohn - Song Without Words Op-38 No-02.mid;Mendelssohn - Song without Words Op-38 No-2.mid;Mendelssohn - Song Without Words Op-53 No-01.mid;Mendelssohn - Song without Words Op-85 No-1.mid;Mendelssohn - Spinner's Song Op-67 No-4.mid;Mendelssohn - Spring Song.mid;Mendelssohn - Wedding March transcr for Piano.mid;Mendelssohn - Wedding March.mid;Moszkowski - Etincelles Op-36, No-6.mid;Moszkowski - Sonata No-14 in Mondscheinsonate-1.mid;Moszkowski - Sonata No-14 in Mondscheinsonate-2.mid;Moszkowski - Sonata No-14 in Mondscheinsonate-3.mid;Moszkowsky - Etincelles.mid;Moszkowsky - Op-36 No-06 Etincelles (Sparks).mid;Mozart, Wolfgang Amadeus - (piano for 4 hands) K19d.mid;Mozart, Wolfgang Amadeus - (piano for 4 hands) K357.mid;Mozart, Wolfgang Amadeus - (piano for 4 hands) K358.mid;Mozart, Wolfgang Amadeus - (piano for 4 hands) K381.mid;Mozart, Wolfgang Amadeus - (piano for 4 hands) K401.mid;Mozart, Wolfgang Amadeus - (piano for 4 hands) K497.mid;Mozart, Wolfgang Amadeus - (piano for 4 hands) K501.mid;Mozart, Wolfgang Amadeus - (piano for 4 hands) K521.mid;Mozart, Wolfgang Amadeus - (piano for 4 hands) K594.mid;Mozart, Wolfgang Amadeus - (piano for 4 hands) K608.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate B 1st Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate B 2nd Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate B 3rd Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate C 1st Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate C 2nd Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate C 3rd Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate No-11 KV331 1st Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate No-11 KV331 2nd Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate No-11 KV331 3rd Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate No-12 KV 331 1st Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate No-12 KV 331 2nd Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate No-12 KV 331 3rd Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate No-12 KV332 1st Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate No-12 KV332 2nd Mov.mid;Mozart, Wolfgang Amadeus - 3 Klaviersonate No-12 KV332 3rd Mov.mid;Mozart, Wolfgang Amadeus - 5 Klaviersonate KV545 2nd Mov.mid;Mozart, Wolfgang Amadeus - 5 Klaviersonate KV545 3rd Mov.mid;Mozart, Wolfgang Amadeus - 5 Klaviersonate KV570 1st Mov.mid;Mozart, Wolfgang Amadeus - 5 Klaviersonate KV570 2nd Mov.mid;Mozart, Wolfgang Amadeus - 5 Klaviersonate KV570 3rd Mov.mid;Mozart, Wolfgang Amadeus - 5 Sonate KV545 1st Mov.mid;Mozart, Wolfgang Amadeus - Ah Vous Dirai Je Maman Variations.mid;Mozart, Wolfgang Amadeus - Alla Turca Rondo.mid;Mozart, Wolfgang Amadeus - Fantasie C Moll.mid;Mozart, Wolfgang Amadeus - Fantasie D Moll.mid;Mozart, Wolfgang Amadeus - Fantasy in C K-475.mid;Mozart, Wolfgang Amadeus - Fantasy in D K-397.mid;Mozart, Wolfgang Amadeus - K003 Allegro in Bb.mid;Mozart, Wolfgang Amadeus - K004-Minuet in F.mid;Mozart, Wolfgang Amadeus - K175 Mov-01 Allegro piano concerto.mid;Mozart, Wolfgang Amadeus - K175 Mov-02 Andante Ma Un Poco Adagio piano concerto.mid;Mozart, Wolfgang Amadeus - K175 Mov-03 Allegro piano concerto.mid;Mozart, Wolfgang Amadeus - K246 Mov-01 Allegro Aperto piano concerto.mid;Mozart, Wolfgang Amadeus - K246 Mov-02 Andante piano concerto.mid;Mozart, Wolfgang Amadeus - K246 Mov-03 Rondo piano concerto.mid;Mozart, Wolfgang Amadeus - K279 Mov-01 Allegro piano sonata.mid;Mozart, Wolfgang Amadeus - K279 Mov-02 Andante piano sonata.mid;Mozart, Wolfgang Amadeus - K279 Mov-03 Allegro piano sonata.mid;Mozart, Wolfgang Amadeus - K280 Piano sonata No-2 in F.mid;Mozart, Wolfgang Amadeus - K281 Mov-01 Allegro piano sonata.mid;Mozart, Wolfgang Amadeus - K281 Mov-02 Andante piano sonata.mid;Mozart, Wolfgang Amadeus - K281 Mov-03 Rondo piano sonata.mid;Mozart, Wolfgang Amadeus - K282 Piano sonata No-4 in E.mid;Mozart, Wolfgang Amadeus - K283 Piano sonata No-5 in G.mid;Mozart, Wolfgang Amadeus - K284 Piano sonata No-6 in D.mid;Mozart, Wolfgang Amadeus - K309 Mov-01 Allegro piano sonata.mid;Mozart, Wolfgang Amadeus - K309 Mov-02 Andante piano sonata.mid;Mozart, Wolfgang Amadeus - K309 Mov-03 Presto piano sonata.mid;Mozart, Wolfgang Amadeus - K311 Mov-01 Allegro Con Spirito.mid;Mozart, Wolfgang Amadeus - K311 Mov-02 Adagio Non Troppo piano sonata.mid;Mozart, Wolfgang Amadeus - K311 Mov-03 Rondo piano sonata.mid;Mozart, Wolfgang Amadeus - K330 piano sonata No-10 in C.mid;Mozart, Wolfgang Amadeus - K331 Mov-01 Andante Grazioso piano.mid;Mozart, Wolfgang Amadeus - K331 Mov-02 Minueto & trio piano.mid;Mozart, Wolfgang Amadeus - K331 Mov-03 Allegretto piano sonata.mid;Mozart, Wolfgang Amadeus - K332 Mov-01 Allegro piano sonata.mid;Mozart, Wolfgang Amadeus - K332 Mov-02 Adagio piano sonata.mid;Mozart, Wolfgang Amadeus - K332 Mov-03 Allegro Assai piano sonata.mid;Mozart, Wolfgang Amadeus - K333 Mov-01 Allegro piano sonata.mid;Mozart, Wolfgang Amadeus - K333 Mov-02 Andante Cantabile piano sonata.mid;Mozart, Wolfgang Amadeus - K333 Mov-03 Allegro Grazioso piano sonata.mid;Mozart, Wolfgang Amadeus - K357 Piano sonata in G.mid;Mozart, Wolfgang Amadeus - K358 Piano sonata in Bb.mid;Mozart, Wolfgang Amadeus - K381 Piano sonata in D.mid;Mozart, Wolfgang Amadeus - K401 Piano sonata in G.mid;Mozart, Wolfgang Amadeus - K450 Mov-01 Allegro piano concerto.mid;Mozart, Wolfgang Amadeus - K450 Mov-02 Andante piano concerto.mid;Mozart, Wolfgang Amadeus - K450 Mov-03 Allegro piano concerto.mid;Mozart, Wolfgang Amadeus - K453 Mov-01 Allegro piano concerto.mid;Mozart, Wolfgang Amadeus - K453 Mov-02 Andante piano concerto.mid;Mozart, Wolfgang Amadeus - K453 Mov-03 Allegretto piano concerto.mid;Mozart, Wolfgang Amadeus - K457 Mov-01 Molto Allegro piano sonata.mid;Mozart, Wolfgang Amadeus - K457 Mov-02 Adagio piano sonata.mid;Mozart, Wolfgang Amadeus - K457 Mov-03 Allegro Assai piano sonata.mid;Mozart, Wolfgang Amadeus - K466 Mov-01 piano concerto No-20.mid;Mozart, Wolfgang Amadeus - K466 Mov-02 piano concerto No-20.mid;Mozart, Wolfgang Amadeus - K466 Mov-03 piano concert No-20.mid;Mozart, Wolfgang Amadeus - K467 Mov-01 piano concerto No-21.mid;Mozart, Wolfgang Amadeus - K467 Mov-02 piano concerto No-21.mid;Mozart, Wolfgang Amadeus - K467 Mov-03 piano concerto No-21.mid;Mozart, Wolfgang Amadeus - K488 Mov-01 Allegro Con Spirito.mid;Mozart, Wolfgang Amadeus - K488 Mov-02 Andante Un Poco Adagio.mid;Mozart, Wolfgang Amadeus - K488 Mov-03 Rondo Allegretto Grazio.mid;Mozart, Wolfgang Amadeus - K497 piano sonata in F.mid;Mozart, Wolfgang Amadeus - K521 piano sonata in C.mid;Mozart, Wolfgang Amadeus - K545 Mov-01 Allegro piano sonata.mid;Mozart, Wolfgang Amadeus - K545 Mov-02 Andante piano sonata.mid;Mozart, Wolfgang Amadeus - K545 Mov-03 Rondo piano sonata.mid;Mozart, Wolfgang Amadeus - K570 Mov-01 Allegro piano sonata.mid;Mozart, Wolfgang Amadeus - K570 Mov-02 Adagio piano sonata.mid;Mozart, Wolfgang Amadeus - K570 Mov-03 Allegretto piano sonata.mid;Mozart, Wolfgang Amadeus - K576 piano sonata No-17 in D.mid;Mozart, Wolfgang Amadeus - Klaviersonate B-1 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate B-2 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate B-3 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate C-1 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate C-2 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate C-3 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate KV 545 2 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate KV 545 3 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate KV 570 1 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate KV 570 2 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate No-11 KV 331 2 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate No-11 KV 331 3 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate No-11 KV 331.mid;Mozart, Wolfgang Amadeus - Klaviersonate No-12 KV 331 1 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate No-12 KV 331 2 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate No-12 KV 331 3 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate No-12 KV 332 1 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate No-12 KV 332 2 Satz.mid;Mozart, Wolfgang Amadeus - Klaviersonate No-12 KV 332 No.mid;Mozart, Wolfgang Amadeus - KMinuet in F.mid;Mozart, Wolfgang Amadeus - Nine Vars in C-Maj K-264 (Gryaznov05).mid;Mozart, Wolfgang Amadeus - Sonata in A 1st Mvt. K-331.mid;Mozart, Wolfgang Amadeus - Sonata in A 2nd Mvt. K-331.mid;Mozart, Wolfgang Amadeus - Sonata in A 3rd Mvt-(Alla Turca) K-331.mid;Mozart, Wolfgang Amadeus - Sonata in A-min K-310 1st Mov (Jia01).mid;Mozart, Wolfgang Amadeus - Sonata in A-min K-310 1st Mov (Rozanski02).mid;Mozart, Wolfgang Amadeus - Sonata in B-flat-Maj K-281 (Lee04).mid;Mozart, Wolfgang Amadeus - Sonata in B-flat-Maj K-281 1st Mov (Lee01).mid;Mozart, Wolfgang Amadeus - Sonata in B-flat-Maj K-333 (Zukiewicz01).mid;Mozart, Wolfgang Amadeus - Sonata in C Allegro K.545.mid;Mozart, Wolfgang Amadeus - Sonata in C Andante K.545.mid;Mozart, Wolfgang Amadeus - Sonata in C Rondo K.545.mid;Mozart, Wolfgang Amadeus - Sonata in C-min K-457 (Gasanov01).mid;Mozart, Wolfgang Amadeus - Sonata in C-min K-457 1st Mov (Falzone01).mid;Mozart, Wolfgang Amadeus - Sonata in C-min K-457 1st Mov (Tysman01).mid;Mozart, Wolfgang Amadeus - Sonata in D-Maj K-311 (Jia04).mid;Mozart, Wolfgang Amadeus - Sonata in D-Maj K-311 (Staupe10).mid;Mozart, Wolfgang Amadeus - Sonata in D-Maj K-311 3rd Mov (Staupe03).mid;Mozart, Wolfgang Amadeus - Sonata in F-Maj K-533 1st Mov (Wilshire01).mid;Mozart, Wolfgang Amadeus - Sonate Kv 284.mid;Mozart, Wolfgang Amadeus - Sonate Kv 332.mid;Mozart, Wolfgang Amadeus - Sonate KV 545 1 Satz.mid;Mozart, Wolfgang Amadeus - Sonate Kv 545.mid;Mozart, Wolfgang Amadeus - Sonate KV 570 3 Satz.mid;Mozart, Wolfgang Amadeus - Sonate Kv331 (01-of-03 files).mid;Mozart, Wolfgang Amadeus - Sonate Kv331 (02-of-03 files).mid;Mozart, Wolfgang Amadeus - Sonate Kv331 (03-of-03 files).mid;Mozart, Wolfgang Amadeus - Sonate No-10 (With The Alla Turca Rondo).mid;Mozart, Wolfgang Amadeus - Variations on Ah vous dirais-je maman.mid;Mussorgsky - Ballet of the Unhatched Chickens (Pictures).mid;Mussorgsky - Bilder einer Aus Baba-Yaga - Das.mid;Mussorgsky - Bilder einer Aus Bydlo.mid;Mussorgsky - Bilder einer Aus Promenade - Ball.mid;Mussorgsky - Bilder einer Aus Samuel Goldenber.mid;Mussorgsky - Bilder einer AusP romenade - Der.mid;Mussorgsky - Bilder einer AusPromenade - Baba-Yaga (The Great Gate of Kiev).mid;Mussorgsky - Bilder einer AusPromenade - Ballet of the Unhatched Chickens.mid;Mussorgsky - Bilder einer AusPromenade - Bydlo.mid;Mussorgsky - Bilder einer AusPromenade - Die Tulieries.mid;Mussorgsky - Bilder einer AusPromenade - Die.mid;Mussorgsky - Bilder einer AusPromenade - Gnom.mid;Mussorgsky - Bilder einer AusPromenade - Gnomus.mid;Mussorgsky - Bilder einer AusPromenade - Il v.mid;Mussorgsky - Bilder einer AusPromenade - Il vechio Castello.mid;Mussorgsky - Bilder einer AusPromenade - Marketplace of Limoges (Catacombes).mid;Mussorgsky - Bilder einer AusPromenade - Samuel Goldenberg und Schmuyle.mid;Mussorgsky - Bydlo (Pictures).mid;Mussorgsky - Pictures At An Exhibition - No-01 The Gnome (Sempre vivo).mid;Mussorgsky - Pictures At An Exhibition - No-02 The Old Castle (Andantino molto).mid;Mussorgsky - Pictures At An Exhibition - No-03 The Tuileries (Allegretto non troppo).mid;Mussorgsky - Pictures At An Exhibition - No-04 Bydlo.mid;Mussorgsky - Pictures At An Exhibition - No-05 Ballet of the Chickens in their Shells.mid;Mussorgsky - Pictures At An Exhibition - No-07 Limoges No-08 Catacombs - Skulls.mid;Mussorgsky - Pictures At An Exhibition - No-09 Hut on Cock's Legs (Baba-Yaga) No-10 The Great Gate of Kiev.mid;Mussorgsky - Pictures At An Exhibition.mid;Mussorgsky - Promenade (Pictures).mid;Mussorgsky - The Old Castle (Pictures).mid;Mussorgsky - Tuileries (Pictures).mid;Muzio Clementi - Sonata in B-flat-Maj Op-24 No-2 (Tak05).mid;Muzio Clementi - Sonata in B-flat-Maj Op-24 No-2 (Yang07).mid;Poulenc - Mouvement perpetuels.mid;Prokofiev - Prelude Op-12 No-7.mid;Prokofiev - Sonata No-3.mid;Prokofiev - Suggestion Diabolique.mid;Prokofiev - The Famous Toccata.mid;Prokofiev, Sergei - Pieces Op-12 Nos 1 7 & 9 (Shilyaev04).mid;Prokofiev, Sergei - Sonata No-2 in D-min Op-14 1 & 3 Movs (Seredenko03).mid;Prokofiev, Sergei - Sonata No-4 in C-min Op-29 (Soukhovetski06).mid;Prokofiev, Sergei - Sonata No-7 in B flat Op-83 (Garritson09).mid;Prokofiev, Sergei - Sonata No-7 in B-flat Op-83 1st & 3rd Movs (Garritson03).mid;Prokofiev, Sergei - Sonata No-7 in B-flat Op-83 2nd & 3rd Movs (Masycheva04).mid;Prokofiev, Sergei - Sonata No-8 Op-84 3rd Mov (Gintov03).mid;Rachmaninov, Sergei Vasilyevich - Flight of the Bumblebee.mid;Rachmaninov, Sergei Vasilyevich - Prelude in C-sharp Op-3 No-2.mid;Rachmaninov, Sergei Vasilyevich - Prelude in G Op-23 No-5.mid;Rachmaninov, Sergei Vasilyevich - 1st Concerto (version for 2 pianos).mid;Rachmaninov, Sergei Vasilyevich - 2nd Suite for 2 pianos Op-17 (Complete).mid;Rachmaninov, Sergei Vasilyevich - 2nd Suite for 2 pianos Op-17 Introduction.mid;Rachmaninov, Sergei Vasilyevich - 2nd Suite for 2 pianos Op-17 Romance.mid;Rachmaninov, Sergei Vasilyevich - 2nd Suite for 2 pianos Op-17 Tarantelle.mid;Rachmaninov, Sergei Vasilyevich - 2nd Suite for 2 pianos Op-17 Valse.mid;Rachmaninov, Sergei Vasilyevich - 3rd Movement of the 2nd Sonata.mid;Rachmaninov, Sergei Vasilyevich - 4 Improvisations (1896).mid;Rachmaninov, Sergei Vasilyevich - Barcarolle Op-10 No-03.mid;Rachmaninov, Sergei Vasilyevich - Barcarolle Op-11 No-01.mid;Rachmaninov, Sergei Vasilyevich - Bumblebee cb Rimsky-Korsakoff pb Rachmaninoff.mid;Rachmaninov, Sergei Vasilyevich - Caprice Bohemien Op-12 (1894).mid;Rachmaninov, Sergei Vasilyevich - Cello Sonata 3rd Mov Volodos.mid;Rachmaninov, Sergei Vasilyevich - Cello Sonata 4.mid;Rachmaninov, Sergei Vasilyevich - Cello Sonata Op-19 Mov-01 (reduced to piano only).mid;Rachmaninov, Sergei Vasilyevich - Cello Sonata Op-19 Mov-02 (reduced to piano only).mid;Rachmaninov, Sergei Vasilyevich - Cello Sonata Op-19 Mov-03 (reduced to piano only).mid;Rachmaninov, Sergei Vasilyevich - Concerto No-01 F sharp min.mid;Rachmaninov, Sergei Vasilyevich - Daisies Op-38 No-03 (1924).mid;Rachmaninov, Sergei Vasilyevich - Elegiac Trio in G-min (reduced to piano only) 1892.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-33 No-1 in F-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-33 No-2 in C-Maj.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-33 No-3 in C-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-33 No-5 in D-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-33 No-6 in E-flat-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-33 No-7 in Eb-Maj.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-33 No-8 in G-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-33 No-9 in C-sharp-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-39 No-1 in C-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-39 No-2 in A-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-39 No-3 in F-sharp-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-39 No-4 in B-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-39 No-5 in E-flat-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-39 No-6 in A-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-39 No-7 in C-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-39 No-8 in D-min.mid;Rachmaninov, Sergei Vasilyevich - Etude Tableau Op-39 No-9 in D-Maj.mid;Rachmaninov, Sergei Vasilyevich - Floods of Spring Op-14 No-11.mid;Rachmaninov, Sergei Vasilyevich - Fragments (1917).mid;Rachmaninov, Sergei Vasilyevich - Isle of the Dead Op-29 (1909).mid;Rachmaninov, Sergei Vasilyevich - Italian Polka - Volodos (1909).mid;Rachmaninov, Sergei Vasilyevich - Korsakovs Bumble Bee (transcr for Piano).mid;Rachmaninov, Sergei Vasilyevich - Liebesfreud cb Kreisler-Rachmaninoff pb Rachmaninoff.mid;Rachmaninov, Sergei Vasilyevich - Liebesleid (1921).mid;Rachmaninov, Sergei Vasilyevich - Lilacs Op-21 No-05 (1913).mid;Rachmaninov, Sergei Vasilyevich - Lullaby Op-16 No-01 cb Tchaikovsky-Rachmaninoff.mid;Rachmaninov, Sergei Vasilyevich - Melodiya Op-21 No-09 (Volodos).mid;Rachmaninov, Sergei Vasilyevich - Minuet from L'Arlesienne Suite No-01 cb Bizet-Rachmaninoff pb Rachmaninoff.mid;Rachmaninov, Sergei Vasilyevich - Moments Musicaux No-01 in Bb-min - Andantino Op-16 No-01 (1896).mid;Rachmaninov, Sergei Vasilyevich - Moments Musicaux No-02 in Eb-min - Allegretto Op-16 No-02 (1896).mid;Rachmaninov, Sergei Vasilyevich - Moments Musicaux No-03 in B-min - Andante contabile Op-16 No-03 (1896).mid;Rachmaninov, Sergei Vasilyevich - Moments Musicaux No-04 in E-min - Presto Op-16 No-04 (1896).mid;Rachmaninov, Sergei Vasilyevich - Moments Musicaux No-05 in Db-Maj - Adagio sostenuto Op-16 No-05 (1896).mid;Rachmaninov, Sergei Vasilyevich - Moments Musicaux No-06 in C-Maj - Maestoso Op-16 No-06 (1896).mid;Rachmaninov, Sergei Vasilyevich - Morceau de Fantasie in G-min (1899).mid;Rachmaninov, Sergei Vasilyevich - Morceau de Fantasie Op-03 No-01 Elegie in Eb-min - cb Rach pb Rach (1892).mid;Rachmaninov, Sergei Vasilyevich - Morceau de Fantasie Op-03 No-02 Prelude in C#-min (1892).mid;Rachmaninov, Sergei Vasilyevich - Morceau de Fantasie Op-03 No-03 Melodie (1892).mid;Rachmaninov, Sergei Vasilyevich - Morceau de Fantasie Op-03 No-04 Polichinelle (1892).mid;Rachmaninov, Sergei Vasilyevich - Morceau de Fantasie Op-03 No-05 Serenade (1892).mid;Rachmaninov, Sergei Vasilyevich - No-06.MID;Rachmaninov, Sergei Vasilyevich - Nocturne No-01 in F# min (11888).mid;Rachmaninov, Sergei Vasilyevich - Nocturne No-02 in F-Maj (11888).mid;Rachmaninov, Sergei Vasilyevich - Nocturne No-03 in C-min (11888).mid;Rachmaninov, Sergei Vasilyevich - Op-01 Mov-01 Vivace piano concerto.mid;Rachmaninov, Sergei Vasilyevich - Op-01 Mov-02 Andante piano concerto.mid;Rachmaninov, Sergei Vasilyevich - Op-01 Mov-03 Allegro Vivace.mid;Rachmaninov, Sergei Vasilyevich - Op-03 No-02 Prelude in C#-min.mid;Rachmaninov, Sergei Vasilyevich - Op-16 No-2 in B-flat-min.mid;Rachmaninov, Sergei Vasilyevich - Op-16 No-4 in E-min.mid;Rachmaninov, Sergei Vasilyevich - Op-16 No-6 in C.mid;Rachmaninov, Sergei Vasilyevich - Op-23 No-02 Prelude in B.mid;Rachmaninov, Sergei Vasilyevich - Op-23 No-04 Prelude in D.mid;Rachmaninov, Sergei Vasilyevich - Op-23 No-05 Prelude in G-min.mid;Rachmaninov, Sergei Vasilyevich - Op-32 No-12 Prelude in G#.mid;Rachmaninov, Sergei Vasilyevich - Op-34 No-14 Vocalise.mid;Rachmaninov, Sergei Vasilyevich - Oriental Dance for Cello & Piano Op-02 No-01 (1892) reduced for piano only.mid;Rachmaninov, Sergei Vasilyevich - Oriental Sketch (1917).mid;Rachmaninov, Sergei Vasilyevich - Piano Sonata No-01 Op-28 Mov-01 (1907).mid;Rachmaninov, Sergei Vasilyevich - Piano Sonata No-01 Op-28 Mov-02 (1907).mid;Rachmaninov, Sergei Vasilyevich - Piano Sonata No-01 Op-28 Mov-03 (1907).mid;Rachmaninov, Sergei Vasilyevich - Polka de WR (1911).mid;Rachmaninov, Sergei Vasilyevich - Prelude for Cello and Piano Op-02 No-01 (reduced to piano only).mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-03 No-02 in C#-min.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-01 in F#-min.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-02 in C#-min.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-03 in D-min.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-04 in D.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-04.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-05 in G-min.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-05.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-06 in Eb.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-07 in C-min.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-08 in G-min.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-09 in Eb-min.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-23 No-10 in Gb.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-32 No-01 in C.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-32 No-05 in G.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-32 No-06 in G#.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-32 No-08 in A-min.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-32 No-11 in B.mid;Rachmaninov, Sergei Vasilyevich - Prelude Op-32 No-12 in G#-min.mid;Rachmaninov, Sergei Vasilyevich - Romance Op-08 No-02.mid;Rachmaninov, Sergei Vasilyevich - Russian Rhapsody - for 2 pianos (1891) vers-1.mid;Rachmaninov, Sergei Vasilyevich - Russian Rhapsody - for 2 pianos (1891) vers-2.mid;Rachmaninov, Sergei Vasilyevich - Scherzo from a Mid-Summer Night's Dream (1933).mid;Rachmaninov, Sergei Vasilyevich - Serenade Op.3 No.5 (1940).mid;Rachmaninov, Sergei Vasilyevich - Sleeping Beauty Suite - No-01 Introduction ''La fee des lilas'' (1891).mid;Rachmaninov, Sergei Vasilyevich - Sleeping Beauty Suite - No-02 Adagio ''Pas d'action'' (1891).mid;Rachmaninov, Sergei Vasilyevich - Sleeping Beauty Suite - No-03 Pas de caractere ''Le Chat botte et la Chatte blanche'' (1891).mid;Rachmaninov, Sergei Vasilyevich - Sleeping Beauty Suite - No-04 ''Panorama'' (1891).mid;Rachmaninov, Sergei Vasilyevich - Sleeping Beauty Suite - No-05 ''Valse'' (1891).mid;Rachmaninov, Sergei Vasilyevich - Sonata No-01 2nd Mov.mid;Rachmaninov, Sergei Vasilyevich - Sonata No-01 3rd Mov.mid;Rachmaninov, Sergei Vasilyevich - Sonata No-01 Op-28- 1st Mov.mid;Rachmaninov, Sergei Vasilyevich - Sonata No-02 Op-36 (1913, revised 1931).mid;Rachmaninov, Sergei Vasilyevich - Symphonic Dances No-01.mid;Rachmaninov, Sergei Vasilyevich - Symphonic Dances No-02.mid;Rachmaninov, Sergei Vasilyevich - Symphonic Dances No-03.mid;Rachmaninov, Sergei Vasilyevich - Symphony No-01 D-min Op-13 Mov-01.mid;Rachmaninov, Sergei Vasilyevich - Symphony No-01 D-min Op-13 Mov-02.mid;Rachmaninov, Sergei Vasilyevich - Symphony No-01 D-min Op-13 Mov-03.mid;Rachmaninov, Sergei Vasilyevich - Symphony No-01 D-min Op-13 Mov-04.mid;Rachmaninov, Sergei Vasilyevich - Symphony-02 Mov-01.mid;Rachmaninov, Sergei Vasilyevich - Symphony-02 Mov-02.mid;Rachmaninov, Sergei Vasilyevich - Symphony-02 Mov-03.mid;Rachmaninov, Sergei Vasilyevich - Symphony-02 Mov-04.mid;Rachmaninov, Sergei Vasilyevich - Symphony-03 A-min Op-44 Mov-01.mid;Rachmaninov, Sergei Vasilyevich - Symphony-03 A-min Op-44 Mov-02.mid;Rachmaninov, Sergei Vasilyevich - Symphony-03 A-min Op-44 Mov-03.mid;Rachmaninov, Sergei Vasilyevich - Tarantelle.mid;Rachmaninov, Sergei Vasilyevich - The Bells Op-35 No-01 Allegro ma non tanto ''The Silver Sleigh Bells'' (1913).mid;Rachmaninov, Sergei Vasilyevich - The Bells Op-35 No-02 Lento ''The Mellow Wedding Bells'' (1913).mid;Rachmaninov, Sergei Vasilyevich - The Bells Op-35 No-03 Presto ''The Loud Alarm Bells'' (1913).mid;Rachmaninov, Sergei Vasilyevich - The Bells Op-35 No-04 Lento lugubre ''The Mournful Iron Bells'' (1913).mid;Rachmaninov, Sergei Vasilyevich - The Famous C Sharp Minor Prelude.mid;Rachmaninov, Sergei Vasilyevich - The Other Most Famous Prelude.mid;Rachmaninov, Sergei Vasilyevich - The Rock (the Crag) Op-07 (1893).mid;Rachmaninov, Sergei Vasilyevich - Three Russian Songs Op-41 No-01 ''Over the little River'' (1926).mid;Rachmaninov, Sergei Vasilyevich - Three Russian Songs Op-41 No-02 ''Oh Vanka you Bold Fellow'' (1926).mid;Rachmaninov, Sergei Vasilyevich - Three Russian Songs Op-41 No-03 ''Quickly Quickly from my Cheeks'' (1926).mid;Rachmaninov, Sergei Vasilyevich - Variations on a Theme of Corelli,Op-42 (1931).mid;Rachmaninov, Sergei Vasilyevich - Vocalise Op-34 No-14 (vers-1).mid;Rachmaninov, Sergei Vasilyevich - Vocalise Op-34 No-14 (vers-2).mid;Rachmaninov, Sergei Vasilyevich - Vocalise.mid;Rachmaninov, Sergei Vasilyevich - What Wealth of Rapture Op-34 No-12.mid;Ravel - Gaspard de la Nuit (1908) Le Gibet.mid;Ravel - Gaspard de la Nuit (1908) Ondine.mid;Ravel - Gaspard de la Nuit (1908) Scarbo.mid;Ravel - Jeux d'eau (1901).mid;Ravel - Jeux d'eau (Fountains).mid;Ravel - Menuet Antique.mid;Ravel - Menuet on the Name of Haydn, Franz Joseph - (Sonatina).mid;Ravel - Miroirs (1905) Noctuelles.mid;Ravel - Ondine (from Gaspard De La Nuit).mid;Ravel - Ondine from Gaspard de la Nuit.mid;Ravel - Pavane For A Dead Princess.mid;Ravel - Pavane Pour Une Infante Defunde.mid;Robert Schumann - Kreisleriana Op-16 (Jia06).mid;Robert Schumann - Sonata No-1 in F-sharp-min Op-11 (Soukhovetski08).mid;Robert Schumann - Toccata in C-Maj Op-7 (Zhdanov06).mid;Sait-Saens - Beethoven, Ludwig von - Variations.mid;Samuel Barber - Sonata Op-26 4th Mov (Fugue) (Atzinger05).mid;Satie - The 3 Gymnopedies.mid;Satie Eric - Gymnopedie No-1.mid;Satie Eric - Gymnopedie No-2.mid;Satie Eric - Gymnopedie No-3.mid;Scarlatti - Sonata in C L.104 K.159.mid;Scarlatti - Sonata in D.mid;Scarlatti - Sonata in F.mid;Schubert - 4 Improptus Op 90.mid;Schubert - Fantasie in C-Maj Op-15 D-760 1st Mov ''Wanderer'' (1822).mid;Schubert - Fantasie in C-Maj Op-15 D-760 2nd Mov ''Wanderer'' (1822).mid;Schubert - Fantasie in C-Maj Op-15 D-760 3rd Mov ''Wanderer'' (1822).mid;Schubert - Fantasie in C-Maj Op-15 D-760 4th Mov ''Wanderer'' (1822).mid;Schubert - Impromptu in A-flat minor Op-90 No-4.mid;Schubert - Impromptu in E-flat Op-90 No-2.mid;Schubert - Impromptu in G-flat Op-90 No-3.mid;Schubert - Improptu Op.90 No-4.mid;Schubert - Klaviersonate (1823) in A-min D-784 Op-143 1st Mov.mid;Schubert - Klaviersonate (1823) in A-min D-784 Op-143 2nd Mov.mid;Schubert - Klaviersonate (1823) in A-min D-784 Op-143 3rd Mov.mid;Schubert - Klaviersonate a-Moll, Op-143 1.mid;Schubert - Klaviersonate a-Moll, Op-143 2.mid;Schubert - Klaviersonate a-Moll, Op-143 3.mid;Schubert - MomentAllegretto.mid;Schubert - Musical Moment No-6.mid;Schubert - Round - Franz Schubert - Sonata in G-Maj D894 (Lee10).mid;Schubert - Sechs Moments Musicaux D-780 Op-94 (1828) No-01.mid;Schubert - Sechs Moments Musicaux D-780 Op-94 (1828) No-02.mid;Schubert - Sechs Moments Musicaux D-780 Op-94 (1828) No-03.mid;Schubert - Sechs Moments Musicaux D-780 Op-94 (1828) No-04.mid;Schubert - Sechs Moments Musicaux D-780 Op-94 (1828) No-05.mid;Schubert - Sechs Moments Musicaux D-780 Op-94 (1828) No-06.mid;Schubert - Sonata in Bb-Maj D-960 1st Mov (1828).mid;Schubert - Sonata in Bb-Maj D-960 2nd Mov (1828).mid;Schubert - Sonata in Bb-Maj D-960 3rd Mov (1828).mid;Schubert - Sonata in Bb-Maj D-960 4th Mov (1828).mid;Schubert - Sonate D960, 1 Satz.mid;Schubert - Sonate D960, 2 Satz.mid;Schubert - Sonate D960, 3 Satz.mid;Schubert - Sonate D960, 4 Satz.mid;Schubert - The Wanderer Fantasy.mid;Schubert - Vier Impromptus D-899 Op-90 (1827) No-01.mid;Schubert - Vier Impromptus D-899 Op-90 (1827) No-02.mid;Schubert - Vier Impromptus D-899 Op-90 (1827) No-03.mid;Schubert - Vier Impromptus D-899 Op-90 (1827) No-04.mid;Schubert - Vier Impromptus D-935 Op-142 (Posthume) No-1.mid;Schubert - Vier Impromptus D-935 Op-142 (Posthume) No-2.mid;Schubert - Vier Impromptus Impromptu No-1.mid;Schubert - Vier Impromptus Impromptu No-2.mid;Schubert - Vier Impromptus Impromptu No-3.mid;Schubert - Vier Impromptus Impromptu No-4.mid;Schubert - Wandererfantasie D760, 1 Satz.mid;Schubert - Wandererfantasie D760, 2 Satz.mid;Schubert - Wandererfantasie D760, 3 Satz.mid;Schubert - Wandererfantasie D760, 4 Satz.mid;Schumann - A-minor Concerto (Ver for 2 Pianos).mid;Schumann - Abegg-Variationen Op-01 (1830).mid;Schumann - Abegg-Variationen.mid;Schumann - About Foreign Lands and People Op-15 No-1.mid;Schumann - Almost Too Serious Op-15 No-10.mid;Schumann - Arabeske Op-18.mid;Schumann - Blumenstuck (Flower Piece).mid;Schumann - By the Fireside Op-15 No-8.mid;Schumann - Carnaval.mid;Schumann - Catch Me! Op-15 No-3.mid;Schumann - Child Falling Asleep Op-15 No-12.mid;Schumann - Curious Story Op-15 No-2.mid;Schumann - Fantasie C-dur 01-of-03.mid;Schumann - Fantasie C-dur 02-of-03.mid;Schumann - Fantasie C-dur 03-of-03.mid;Schumann - Fantasiestuecken.mid;Schumann - Frightening Op-15 No-11.mid;Schumann - Important Event Op-15 No-6.mid;Schumann - In the Evening Op-12 No-1.mid;Schumann - In the Night Op-12 No-5.mid;Schumann - Kinderszenen (Includes The Traumerei).mid;Schumann - Kinderszenen Opus 15.mid;Schumann - Kinderszenen Opus Am Kamin.mid;Schumann - Kinderszenen Opus Der Dichter spri.mid;Schumann - Kinderszenen Opus Fast zu ernst.mid;Schumann - Kinderszenen Opus Furchtenmachen.mid;Schumann - Kinderszenen Opus Gluckes genug.mid;Schumann - Kinderszenen Opus Hasche-Mann.mid;Schumann - Kinderszenen Opus Kind im Einschlu.mid;Schumann - Kinderszenen Opus Kuriose Geschich.mid;Schumann - Kinderszenen Opus Ritter vom Steck.mid;Schumann - Kinderszenen Opus TrN\u0303umerei.mid;Schumann - Kinderszenen Opus Von fremden LN\u0303nd.mid;Schumann - Kinderszenen Opus Wichtige Begeben.mid;Schumann - Kinderszenen Opus-15 (1838) A Tale of Distant Lands.mid;Schumann - Kinderszenen Opus-15 (1838) Almost too Serious.mid;Schumann - Kinderszenen Opus-15 (1838) Blind Man's Bluff.mid;Schumann - Kinderszenen Opus-15 (1838) By the Fireside.mid;Schumann - Kinderszenen Opus-15 (1838) Curious Story.mid;Schumann - Kinderszenen Opus-15 (1838) Great Adventure.mid;Schumann - Kinderszenen Opus-15 (1838) Hobgoblin.mid;Schumann - Kinderszenen Opus-15 (1838) In Slumberland.mid;Schumann - Kinderszenen Opus-15 (1838) On the Rocking Horse.mid;Schumann - Kinderszenen Opus-15 (1838) Perfect Happiness.mid;Schumann - Kinderszenen Opus-15 (1838) Pleading Child.mid;Schumann - Kinderszenen Opus-15 (1838) Reverie.mid;Schumann - Kinderszenen Opus-15 (1838) The Poet Speaks.mid;Schumann - King of the Rocking-Horse Op-15 No-9.mid;Schumann - Kreisleriana 3.mid;Schumann - Kreisleriana No-4.mid;Schumann - Kreisleriana No-7.mid;Schumann - Kreisleriana No-Fantasien-1.mid;Schumann - Kreisleriana No-Fantasien-2.mid;Schumann - Kreisleriana Op-16 (1838) No-01.mid;Schumann - Kreisleriana Op-16 (1838) No-02.mid;Schumann - Kreisleriana Op-16 (1838) No-03.mid;Schumann - Kreisleriana Op-16 (1838) No-04.mid;Schumann - Kreisleriana Op-16 (1838) No-05.mid;Schumann - Kreisleriana Op-16 (1838) No-06.mid;Schumann - Kreisleriana Op-16 (1838) No-07.mid;Schumann - Kreisleriana Op-16 (1838) No-08.mid;Schumann - Kreisleriana Sehr langsam.mid;Schumann - Kreisleriana Teil 5.mid;Schumann - Kreisleriana Teil 8.mid;Schumann - Liebeslied (transcribed by Liszt, Franz -).mid;Schumann - Liebeslied arr. by Liszt.mid;Schumann - Perfect Happiness Op-15 No-5.mid;Schumann - Piano Concerto A min 1st. mov.mid;Schumann - Piano Concerto A min 2nd & 3rd movements.mid;Schumann - Pleading Child Op-15 No-4.mid;Schumann - Restless Dreams Op-12 No-7.mid;Schumann - Reverie Op-15 No-7.mid;Schumann - Romanze in F-sharp Op-28 No-2.mid;Schumann - Sechs Moments MuNo-1 in C-Dur.mid;Schumann - Sechs Moments MuNo-2 in As-Dur.mid;Schumann - Sechs Moments MuNo-3 f-moll.mid;Schumann - Sechs Moments MuNo-4 cis-moll.mid;Schumann - Sechs Moments MuNo-5 in f-moll.mid;Schumann - Soaring Op-12 No-2.mid;Schumann - Symphonic Etude in C#-min Op-13.mid;Schumann - Symphonic Etudes.mid;Schumann - The Happy Farmer.mid;Schumann - The Poet Speaks Op-15 No-13.mid;Schumann - The Song's End Op-12 No-8.mid;Schumann - Traumerei (from The Kinderszenen).mid;Schumann - Traumerei.mid;Schumann - Traumeri.mid;Schumann - Whims Op-12 No-4.mid;Schumann - Why Op-12 No-3.mid;Scriabin - 01 (Piano).mid;Scriabin - 02 (Piano).mid;Scriabin - 03 (Piano).mid;Scriabin - 04 (Piano).mid;Scriabin - Etude in C#-min Op-02 No-01 (1887).mid;Scriabin - Etude in C-sharpop.2no 11.mid;Scriabin - Etude Op-08 (1894) No-02 in F#.mid;Scriabin - Etude Op-08 (1894) No-12 in E# min.mid;Scriabin - Nocturne For The Left Hand.mid;Serge Rachmaninov, Sergei Vasilyevich - Corelli Vars Op-42 (Zukiewicz03).mid;Serge Rachmaninov, Sergei Vasilyevich - Prelude in B-min Op-32 No-10 (Floril03).mid;Serge Rachmaninov, Sergei Vasilyevich - Sonata in B-flat-min 1st & 2nd Movs (KimG03).mid;Serge Rachmaninov, Sergei Vasilyevich - Sonata in B-flat-min Op-36 1st & 2nd Movs (Georgieva02).mid;Serge Rachmaninov, Sergei Vasilyevich - Sonata No-2 in B-flat-Maj Op-36 (Lee03).mid;Serge Rachmaninov, Sergei Vasilyevich - Sonata No-2 in B-flat-min Op-36 (1913) (Staupe12).mid;Serge Rachmaninov, Sergei Vasilyevich - Sonata No-2 in B-flat-min Op-36 (1913) 1st Mov (Staupe04).mid;Serge Rachmaninov, Sergei Vasilyevich - Sonata No-2 in B-flat-min Op-36 (KimG09).mid;Serge Rachmaninov, Sergei Vasilyevich - Sonata No-2 in B-flat-min Op-36 (Lee09).mid;Serge Rachmaninov, Sergei Vasilyevich - Sonata No-2 Op-36 (Revised Edition) 1st Mov (ParkH03).mid;Shostakovich - Op-87 Fugue-01.mid;Shostakovich - Op-87 Fugue-02.mid;Shostakovich - Op-87 Fugue-03.mid;Shostakovich - Op-87 Fugue-04.mid;Shostakovich - Op-87 Fugue-05.mid;Shostakovich - Op-87 Fugue-06.mid;Shostakovich - Op-87 Fugue-07.mid;Shostakovich - Op-87 Fugue-08.mid;Shostakovich - Op-87 Fugue-09.mid;Shostakovich - Op-87 Fugue-10.mid;Shostakovich - Op-87 Fugue-11.mid;Shostakovich - Op-87 Fugue-12.mid;Shostakovich - Op-87 Fugue-13.mid;Shostakovich - Op-87 Fugue-14.mid;Shostakovich - Op-87 Fugue-15.mid;Shostakovich - Op-87 Fugue-16.mid;Shostakovich - Op-87 Fugue-17.mid;Shostakovich - Op-87 Fugue-18.mid;Shostakovich - Op-87 Fugue-19.mid;Shostakovich - Op-87 Fugue-20.mid;Shostakovich - Op-87 Fugue-21.mid;Shostakovich - Op-87 Fugue-22.mid;Shostakovich - Op-87 Fugue-23.mid;Shostakovich - Op-87 Fugue-24.mid;Shostakovich - Op-87 Prelude 01.mid;Shostakovich - Op-87 Prelude 02.mid;Shostakovich - Op-87 Prelude 03.mid;Shostakovich - Op-87 Prelude 04.mid;Shostakovich - Op-87 Prelude 05.mid;Shostakovich - Op-87 Prelude 06.mid;Shostakovich - Op-87 Prelude 07.mid;Shostakovich - Op-87 Prelude 08.mid;Shostakovich - Op-87 Prelude 09.mid;Shostakovich - Op-87 Prelude 10.mid;Shostakovich - Op-87 Prelude 11.mid;Shostakovich - Op-87 Prelude 12.mid;Shostakovich - Op-87 Prelude 13.mid;Shostakovich - Op-87 Prelude 14.mid;Shostakovich - Op-87 Prelude 15.mid;Shostakovich - Op-87 Prelude 16.mid;Shostakovich - Op-87 Prelude 17.mid;Shostakovich - Op-87 Prelude 18.mid;Shostakovich - Op-87 Prelude 19.mid;Shostakovich - Op-87 Prelude 20.mid;Shostakovich - Op-87 Prelude 21.mid;Shostakovich - Op-87 Prelude 22.mid;Shostakovich - Op-87 Prelude 23.mid;Shostakovich - Op-87 Prelude 24.mid;Sibelius - Romance in D-flat.mid;Sibelius - Valse Triste.mid;Sinding - Rustles of Spring Op-32 No-3.mid;Sinding - The Rustle-of-Spring.mid;Stravinsky - 3 Movements from Petruska.mid;Stravinsky - Le Sacre Du Printemps (transcribed for Piano).mid;Tchaikovsky - 01-Die Jahreszeiten Januar.mid;Tchaikovsky - 02-Die Jahreszeiten Februar.mid;Tchaikovsky - 03-Die Jahreszeiten Maerz.mid;Tchaikovsky - 04-Die Jahreszeiten April.mid;Tchaikovsky - 05-Die Jahreszeiten Mai.mid;Tchaikovsky - 06-Die Jahreszeiten Juni.mid;Tchaikovsky - 07-Die Jahreszeiten Juli.mid;Tchaikovsky - 08-Die Jahreszeiten August.mid;Tchaikovsky - 09-Die Jahreszeiten September.mid;Tchaikovsky - 10-Die Jahreszeiten Oktober.mid;Tchaikovsky - 11-Die Jahreszeiten November.mid;Tchaikovsky - 12-Die Jahreszeiten Dezember.mid;Tchaikovsky - Arabian Dance (Nutcracker).mid;Tchaikovsky - Chant Sans Paroles Op-40 No-6.mid;Tchaikovsky - Chinese Dance (Nutcracker).mid;Tchaikovsky - Dance of the Reed Flutes (Nutcracker).mid;Tchaikovsky - Dance of the Sugar-Plum Fairy (Nutcracker).mid;Tchaikovsky - Die Jahreszeiten April.mid;Tchaikovsky - Die Jahreszeiten August.mid;Tchaikovsky - Die Jahreszeiten Dezember.mid;Tchaikovsky - Die Jahreszeiten Februar.mid;Tchaikovsky - Die Jahreszeiten Januar.mid;Tchaikovsky - Die Jahreszeiten Juli.mid;Tchaikovsky - Die Jahreszeiten Juni.mid;Tchaikovsky - Die Jahreszeiten Maerz.mid;Tchaikovsky - Die Jahreszeiten Mai.mid;Tchaikovsky - Die Jahreszeiten November.mid;Tchaikovsky - Die Jahreszeiten Oktober.mid;Tchaikovsky - Die Jahreszeiten September.mid;Tchaikovsky - Dumka Op-59 (Soukhovetski03).mid;Tchaikovsky - Dumka Op-59 (Soukhovetski05).mid;Tchaikovsky - from Nutcracker Suite March Intermezzo Trepak & Andante Maestoso (Sychev02).mid;Tchaikovsky - June (Barcarolle) Op-37 No-6.mid;Tchaikovsky - March (Nutcracker).mid;Tchaikovsky - Mazurka Op-39 No-10.mid;Tchaikovsky - Neapolitan Song Op-39 No-18.mid;Tchaikovsky - Nutcracker Suite Op-71a.mid;Tchaikovsky - Old French Song Op-39 No-16.mid;Tchaikovsky - Overture (Nutcracker).mid;Tchaikovsky - Reverie.mid;Tchaikovsky - Romance .mid;Tchaikovsky - Romance Op-51.mid;Tchaikovsky - Russian Dance (Nutcracker).mid;Tchaikovsky - Song of the Lark Op-39 No-22.mid;Tchaikovsky - Sweet Dream Op-39 No-21.mid;Tchaikovsky - The Nutcracker for Solo Piano.mid;Tchaikovsky - Waltz of the Flowers (Nutcracker).mid;Tchaikovsky - Waltz Of The Flowers From The Nutcracker.mid;Tchaikovsky - Waltz Op-39 No-8.mid;Villa-Lobos - Punch (Le Polichinelle).mid;Von Weber - Rondo Brilliant in E-flat Op-62.mid;Wagner, Richard - Liebestod from Tristan and Isolde arr. by Liszt.mid;Wagner, Richard - Overture Tannhauser [Liszt, Franz - transcription].mid;Wagner, Richard - Tannhauser Ouverture (transcribed by Liszt, Franz -).mid;Wagner, Richard - Tannhauser Overture arr. by Liszt.mid;Wagner, Richard - Traume.mid;Weber - Rondo Brillande.mid".split(";"), c =
            0; c < a.length; c++)
        b[a[c]] = null;
    return b
}
();
Piano.fileBrowserKeyboard = function (b) {
    27 === b.keyCode && Piano.fileBrowserToggle()
};
Piano.fileBrowserToggle = function () {
    var b = document.getElementById("file-browser");
    0 !== parseInt(b.style.opacity) ? (b.style.opacity = 0, setTimeout(function () {
            b.style.display = "none"
        }, 500), Event.remove(document, "keydown", Piano.fileBrowserKeyboard)) : (b.style.display = "block", setTimeout(function () {
            b.style.opacity = 1
        }, 1), Event.add(document, "keydown", Piano.fileBrowserKeyboard), b.getElementsByTagName("input")[0].focus(), Piano.fileBrowserUpdate())
};
Piano.fileBrowser = function () {
    function b(a, b) {
        var c = a.parentNode.getElementsByClassName("selected");
        if (c)
            for (var d = 0; d < c.length; d++)
                c[d].className = "";
        a.className = "selected";
        c = a.getAttribute("data-src");
        if (-1 !== c.indexOf(".mid")) {
            d = c.split("/").pop().replaceAll("%20", " ");
            loader.message("loading: " + d);
            var e = MIDI.Player.playing;
            e && MIDI.UI.togglePlayer();
            Piano.midifile = c;
            Piano.loadFile(Piano.midifile, function () {
                e && MIDI.UI.togglePlayer();
                Piano.Animation.scrollTop = 0;
                Piano.fileBrowserToggle();
                MIDI.Player.renderScreen();
                b && b(Piano.midifile);
                loader.stop()
            })
        }
    }
    Piano.fileBrowserUpdate = function (a) {
        a = (a || "").toLowerCase().trim();
        var c = k.getElementsByTagName("div"),
        d = -1,
        e = !!c.length,
        n = 0,
        r;
        for (r in Piano.files) {
            d++;
            var q = r.replace(".mid", ""),
            p = a && 0 > r.toLowerCase().indexOf(a);
            e && (p ? c[d].style.display = "none" : (c[d].style.display = "block", n++, p = !0));
            Piano.midifile && (q === Piano.midifile.replace(".mid", "") && c[d]) && (c[d].className = "selected");
            p || (n++, p = document.createElement("div"), k.appendChild(p), p.onclick = function (a) {
                Event.cancel(a);
                b(this)
            }, p.setAttribute("data-src", r), p.innerHTML = q.replace(" - ", "&mdash;"), q = document.createElement("a"), q.onclick = function (a) {
                Event.cancel(a);
                b(this.parentNode, function (a) {
                    fileSaver.html5 && fileSaver.download({
                        name: a.replace(".mid", ""),
                        extension: "midi",
                        getData: function () {
                            var b = Piano.files[a].split(",").pop();
                            return window.atob(b)
                        }
                    })
                })
            }, q.innerHTML = "download", p.appendChild(q))
        }
        c[c.length - 1].style.display = n ? "none" : "block";
        e || (p = document.createElement("div"), p.style.height = window.innerHeight - 40 + "px",
            p.style.background = "#eee", p.style.color = "#000", p.style.cursor = "default", p.style.display = "none", p.innerHTML = "No results...", k.appendChild(p))
    };
    var a = document.body,
    c = document.createElement("div");
    c.id = "file-browser";
    c.style.cssText = "display: none; opacity: 0";
    c.style.width = window.innerWidth + "px";
    c.style.height = window.innerHeight + "px";
    var e = document.createElement("img");
    e.onclick = Piano.fileBrowserToggle;
    e.style.cssText = "position: fixed; top: 8px; right: 7px; z-index: 2; cursor: pointer";
    e.src = "./media/close.png";
    c.appendChild(e);
    e = document.createElement("input");
    e.placeholder = "Enter your search here...";
    var d = 0;
    e.onkeyup = e.onkeypress = e.onkeydown = function (a) {
        var b = this;
        Event.stop(a);
        27 === a.keyCode && this.blur();
        "keyup" === a.type && (window.clearTimeout(d), d = window.setTimeout(function () {
                Piano.fileBrowserUpdate(b.value)
            }, 150))
    };
    c.appendChild(e);
    var k = document.createElement("div");
    k.style.cssText = "position: relative; top: 65px";
    c.appendChild(k);
    a.appendChild(c);
    Event.add(c, "mousewheel", Event.stop);
    Piano.fileBrowserUpdate()
};
var MusicBox = {};
(function () {
    function b(b) {
        a.aspect = window.innerWidth / window.innerHeight;
        a.updateProjectionMatrix();
        e.setSize(window.innerWidth, window.innerHeight)
    }
    var a,
    c,
    e,
    d,
    k = [],
    m = "#interactive" == window.location.hash,
    g;
    MusicBox.init = function () {
        d = document.createElement("div");
        d.id = "musicbox";
        d.style.cssText = "position: absolute; top: 0; left: 0; z-index: 0";
        d.onmousemove = MusicBox.render;
        document.body.appendChild(d);
        a = new THREE.TrackballCamera({
            fov: 200,
            aspect: window.innerWidth / window.innerHeight,
            near: 0,
            far: 1E3,
            rotateSpeed: 1,
            zoomSpeed: 1.2,
            panSpeed: 0.8,
            noZoom: !1,
            noPan: !1,
            staticMoving: !1,
            dynamicDampingFactor: 0.3
        });
        a.position.x = 900;
        a.position.y = -100;
        a.position.z = -100;
        MusicBox.scene = new THREE.Scene;
        MusicBox.scene.fog = new THREE.FogExp2(0, 0.0025);
        var f = new THREE.DirectionalLight(13421772, 4);
        f.position.x = 1;
        f.position.y = 1;
        f.position.z = 1;
        f.position.normalize();
        MusicBox.scene.addLight(f);
        f = new THREE.DirectionalLight(16777215, 4);
        f.position.x = -1;
        f.position.y = -1;
        f.position.z = -1;
        f.position.normalize();
        MusicBox.scene.addLight(f);
        for (var f =
                0, k = new THREE.CubeGeometry(100, 40, 40), g = 1; 9 > g; g++)
            for (var m = 0; 12 > m; m++) {
                var q = new THREE.Mesh(k, new THREE.MeshLambertMaterial({
                            color: parseInt("0x" + Piano.colorMap[f++].hex),
                            transparent: !0,
                            blending: THREE.AdditiveBlending
                        }));
                q.position.x = 1E3 * (m / 36) - 50;
                q.position.y = 1E3 * (g / 10) - 500;
                q.position.z = 1E3 * (m / 10) - 400;
                q.sticky = !0;
                MusicBox.scene.addObject(q)
            }
        k = new THREE.Geometry;
        for (i = 0; 4E3 > i; i++)
            vector = new THREE.Vector3(2E3 * Math.random() - 1E3, 2E3 * Math.random() - 1E3, 2E3 * Math.random() - 1E3), k.vertices.push(new THREE.Vertex(vector));
        parameters = [[[1, 1, 1], 5], [[0.95, 1, 1], 4], [[0.9, 1, 1], 3], [[0.85, 1, 1], 2], [[0.8, 1, 1], 1]];
        c = new THREE.Projector;
        e = new THREE.WebGLRenderer;
        e.sortObjects = !1;
        e.setSize(window.innerWidth, window.innerHeight);
        d.appendChild(e.domElement);
        window.addEventListener("resize", b, !1)
    };
    MusicBox.render = function () {
        a.update();
        if (m) {
            var b = new THREE.Vector3(0, 0, 0.5);
            c.unprojectVector(b, a);
            b = (new THREE.Ray(a.position, b.subSelf(a.position).normalize())).intersectScene(MusicBox.scene);
            0 < b.length ? g != b[0].object && (g && (g.scale.x =
                        1), g = b[0].object, g.currentHex = g.materials[0].color.hex, MIDI.noteOn && (b = Color.Space(g.currentHex, "HEX>RGB>HSL"), b = (12 * (b.H / 360) >> 0) + 12 * (b.L / 10 >> 0), g.scale.x = 100, MIDI.noteOn(1, b))) : (g && (g.scale.x = 1), g = null)
        }
        b = 1E-4 * (new Date).getTime();
        for (i = 0; i < MusicBox.scene.objects.length; i++) {
            var d = MusicBox.scene.objects[i];
            d.sticky || (d.rotation.y = b * (4 > i ? i / 70 : -i / 70))
        }
        for (i = 0; i < k.length; i++)
            color = parameters[i][0], h = 360 * (color[0] + b) % 360 / 360, k[i].color.setHSV(h, color[1], color[2]);
        e.render(MusicBox.scene, a)
    }
})();
var change = function () {
    return {
        css: function (b, a) {
            "string" === typeof b && (b = document.getElementById(b));
            if (b) {
                a = a.split(";");
                for (var c = 0, e = a.length; c < e; c++) {
                    var d = a[c].split(":");
                    b.style[d[0]] = d[1]
                }
            }
        },
        className: function (b, a) {
            "string" === typeof b && (b = document.getElementById(b));
            if (b) {
                if (b.parentNode) {
                    var c = b.parentNode.getElementsByClassName(a);
                    if (c.length)
                        for (var e = 0; e < c.length; e++)
                            c[e].className = (" " + c[e].className + " ").replace(" " + a + " ", " ").trim()
                }
                b.className = (b.className + " " + a).trim()
            }
        }
    }
}
();
"undefined" === typeof MIDI && (MIDI = {});
"undefined" === typeof MIDI.UI && (MIDI.UI = {});
(function (b) {
    b.enableConfigure = function (a) {
        var b = document.getElementById("tools").parentNode.style;
        a ? (Event.remove(window, "keydown", Piano.keyDown), Event.remove(window, "keyup", Piano.keyUp), b.display = "block") : (Event.add(window, "keydown", Piano.keyDown), Event.add(window, "keyup", Piano.keyUp), b.display = "none")
    };
    b.enableView = function (a) {
        "postview" === Piano.visualize ? (MIDI.UI.enableTheoryView(), a || Piano.func()) : MIDI.UI.enableSongView()
    };
    b.enableTheoryView = function () {
        Piano.setAnimation();
        change.className("view-theory",
            "selected");
        document.querySelector("#view-song").className = "selected theorymode";
        var a = document.getElementById("playback");
        "none" !== a.style.display && (a.style.display = "none", a = document.getElementById("theory"), a.style.display = "inline-block", a.loaded || (a.loaded = !0, b.drawKeySignatures(a), b.drawOctaves(a), b.drawChords(a), b.drawInversions(a), b.drawScales(a)), Piano.visualize = "postview", localStorage.setItem("visualize", Piano.visualize), Piano.Animation.boot())
    };
    b.enableSongView = function () {
        Piano.clearNotes();
        change.className("view-song", "selected");
        document.querySelector("#view-song").className = "selected songmode";
        var a = document.getElementById("playback");
        "inline-block" !== a.style.display && (a.style.display = "inline-block", document.getElementById("theory").style.display = "none", Piano.visualize = "preview", localStorage.setItem("visualize", Piano.visualize), Piano.Animation.boot())
    };
    b.drawKeySignatures = function (a) {
        var b = MIDI.noteToKey[Piano.key + 21].replace(/[^a-zA-Z]+/g, "");
        a.appendChild(e({
                arr: MusicTheory.key2number,
                header: {
                    Signature: null
                },
                id: "key",
                title: "Key Signature",
                callback: function (a) {
                    a = a.options[a.selectedIndex].value;
                    Piano.key = MusicTheory.key2number[a];
                    Piano.inversion = 0;
                    MusicTheory.getKeySignature(a);
                    Piano.drawKeyboard();
                    Piano.func()
                },
                selected: b
            }))
    };
    b.drawOctaves = function (a) {
        for (var b = {}, c = 0; 7 > c; c++)
            b[c + " "] = c;
        a.appendChild(e({
                arr: b,
                header: {
                    Octave: null
                },
                id: "octave",
                callback: function (a) {
                    Piano.octave = parseInt(a.options[a.selectedIndex].value);
                    Piano.inversion = 0;
                    Piano.clearNotes();
                    Piano.func()
                },
                selected: Piano.octave,
                title: "Octaves"
            }))
    };
    b.drawChords = function (a) {
        a.appendChild(e({
                arr: MusicTheory.Chords,
                id: "chord",
                header: {
                    Chords: null
                },
                callback: function (a) {
                    Piano.chord = a.options[a.selectedIndex].value;
                    Piano.func = function () {
                        Piano.clearNotes();
                        Piano.chordOn()
                    };
                    Piano.func();
                    Piano.inversion = 0
                },
                selected: Piano.chord,
                title: "Chords"
            }))
    };
    b.drawScales = function (a) {
        var b = 0,
        c = [],
        g;
        for (g in MusicTheory.Scales)
            c[b++] = g;
        Piano.scale = c[Math.round(Math.random() * b)];
        a.appendChild(e({
                arr: MusicTheory.Scales,
                id: "scale",
                header: {
                    Scales: null
                },
                callback: function (a) {
                    Piano.scale = a.options[a.selectedIndex].value;
                    Piano.func = Piano.playScale;
                    Piano.clearNotes();
                    Piano.func();
                    Piano.inversion = 0
                },
                selected: Piano.scale,
                title: "Scales"
            }))
    };
    b.drawInversions = function (a) {
        var b = document.createElement("input");
        b.type = "button";
        b.title = "Inversion -1";
        b.value = "-";
        b.onclick = function () {
            Piano.clearNotes();
            Piano.invert(-1)
        };
        a.appendChild(b);
        b = document.createElement("input");
        b.type = "button";
        b.title = "Inversion +1";
        b.value = "+";
        b.onclick = function () {
            Piano.clearNotes();
            Piano.invert(1)
        };
        a.appendChild(b)
    };
    b.togglePlayer = function (a) {
        var b = document.getElementById("control-play"),
        c = "boolean" !== typeof a;
        c || b.setAttribute("toggled", a);
        a = b.getAttribute("toggled");
        "true" === a ? (b.setAttribute("toggled", !1), b.src = "./media/pause.png", Piano.clearNotes(), c && (Piano.resume(), Piano.setAnimation())) : (b.setAttribute("toggled", !0), b.src = "./media/play.png", c && MIDI.Player.pause())
    };
    b.drawTimeWarp = function () {
        var b = document.createElement("div");
        b.style.cssText = "display: inline-block;";
        var c,
        e,
        g = document.createElement("input");
        g.style.cssText = "display: inline-block; width: 190px; position: relative; top: 4px;";
        g.setAttribute("type", "range");
        g.max = 400;
        g.min = 100;
        g.value = 100 * Piano.timeWarp;
        g.onmousedown = function (a) {
            e = MIDI.Player.currentTime;
            c = MIDI.Player.endTime;
            Event.stop(a);
            MIDI.Player.playing && MIDI.UI.togglePlayer()
        };
        g.onchange = function (a) {
            var b = g.value / 100;
            a = (b < Piano.timeWarp ? "Increasing" : "Decreasing") + " speed...";
            Piano.timeWarp = b;
            localStorage.setItem("timeWarp", b);
            loader.message(a);
            window.setTimeout(function () {
                MIDI.Player.timeWarp = b;
                MIDI.Player.loadMidiFile();
                MIDI.Player.currentTime = Piano.Animation.scrollTop = e / c * MIDI.Player.endTime;
                MIDI.Player.renderScreen();
                loader.stop()
            }, 10);
            f.innerHTML = Math.round(1E4 * (1.25 - g.value / 400)) / 100 + "%"
        };
        b.appendChild(g);
        var f = document.createElement("span");
        f.style.cssText = "display: inline-block; color: #333; width: 30px; padding-left: 10px";
        f.innerHTML = g.value + "%";
        b.appendChild(f);
        a("Playback Speed:", b)
    };
    b.drawSynesthesia = function () {
        var b = e({
            arr: MusicTheory.Synesthesia.data,
            id: "rgb",
            callback: function (a) {
                Piano.HSL = a.options[a.selectedIndex].value;
                localStorage.setItem("HSL", Piano.HSL);
                Piano.colorMap = MusicTheory.Synesthesia.map(Piano.HSL);
                Piano.drawKeyboard();
                MIDI.Player.renderScreen();
                MIDI.Player.playing || (Piano.clearNotes(), Piano.func(), Piano.inversion = 0)
            },
            selected: Piano.HSL,
            title: "Synesthesia"
        });
        a("Synesthesia:", b, !0)
    };
    b.drawInstruments = function () {
        String(MIDI.getInstruments()).split("|").splice(0, 128);
        var c = {},
        k = "",
        m;
        for (m in MIDI.instruments) {
            var g = MIDI.instruments[m];
            g.instrument && (k != g.category && (k = g.category, c[k] = null), c[g.instrument] = m)
        }
        a("Instrument", e({
                arr: c,
                id: "voice",
                title: "Instruments",
                callback: function (a) {
                    Piano.clearNotes();
                    b.instrument = a.options[a.selectedIndex].value;
                    MIDI.Plugin && MIDI.programChange(b.channel, c[b.instrument]);
                    MIDI.Player.playing || Piano.func()
                },
                selected: b.instrument
            }))
    };
    b.drawChannels = function () {
        for (var d = {}, k = 0; 16 > k; k++)
            d[k + " "] = k;
        k = document.createElement("div");
        k.style.cssText = "display: inline-block;";
        k.appendChild(e({
                arr: d,
                header: {
                    Channels: null
                },
                id: "channel",
                callback: function (a) {
                    b.channel = parseInt(a.options[a.selectedIndex].value);
                    a = MIDI.channels[b.channel];
                    document.getElementById("mute").checked = a.mute ? "checked" : "";
                    document.getElementById("voice").selectedIndex = a.instrument
                },
                selected: 0,
                title: "Channels"
            }));
        k.appendChild(c({
                title: "Mute channel",
                id: "mute",
                checked: !1,
                value: "Mute channel",
                callback: function () {
                    Piano.clearNotes();
                    MIDI.channels[b.channel].mute = this.checked;
                    MIDI.setMute(b.channel, this.checked)
                }
            }));
        a("Channels", k)
    };
    var a = function (a,
        b, c) {
        var e = document.getElementById("tools"),
        f = document.createElement("span");
        f.innerHTML = a;
        !1 !== c && e.appendChild(document.createElement("hr"));
        e.appendChild(f);
        e.appendChild(b)
    },
    c = function (a) {
        a || (a = {});
        var b = document.createElement("input");
        b.title = a.title;
        b.id = a.id;
        b.type = "checkbox";
        b.value = a.value;
        b.checked = a.checked ? a.checked : "";
        b.onmousedown = function (a) {
            Event.stop(a)
        };
        b.onclick = a.callback;
        return b
    },
    e = function (a) {
        var b = document.createElement("select");
        b.id = a.id;
        b.title = a.title;
        b.onmousedown = function (a) {
            Event.stop(a)
        };
        b.onchange = function (b) {
            a.callback(this, b);
            this.blur()
        };
        if (a.header) {
            var c = a.header,
            e;
            for (e in a.arr)
                c[e] = a.arr[e];
            a.arr = c
        }
        for (e in a.arr)
            null === a.arr[e] ? (c = document.createElement("optgroup"), c.label = "-" + e.toUpperCase() + "-") : (c = document.createElement("option"), a.selected == e && (c.selected = !0), c.value = e, c.text = e), b.appendChild(c);
        return b
    }
})(MIDI.UI);
