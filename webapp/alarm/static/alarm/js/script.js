$(document).on("click", ".ampm", function()
{
    var id = $(this).attr("id");
    if((id == "am"))
    {
        $("#am").removeClass("unselected");
        $("#am").addClass("selected");
        $("#pm").removeClass("selected");
        $("#pm").addClass("unselected");
        $("#id_ampm").val("am");
    }
    else if((id == "pm"))
    {
        $("#am").removeClass("selected");
        $("#am").addClass("unselected");
        $("#pm").removeClass("unselected");
        $("#pm").addClass("selected");
        $("#id_ampm").val("pm");
    }
});

$(document).on("click", ".day", function()
{
    var id = $(this).attr("id");
    $("#" + id).toggleClass("selected");
    $("#" + id).toggleClass("unselected");
    if($("#id_" + id).val().toLowerCase() == "true")
    {
        $("#id_" + id).val(false);
    }
    else
    {
        $("#id_" + id).val(true);
    }
});

$(document).on("change", "#id_music_account", function()
{
    $("#id_music_playlist").html("<option>Getting playlists...</option>");
    $.ajax({
       type: "POST",
       url: "/alarm/get_playlists",
       headers: { "X-CSRFToken": getCookie("csrftoken") },
       data: $("#alarmForm").serialize(),
       success: playlist_callback,
       dataType: "html"
     });
})

function playlist_callback(data)
{
    $("#id_music_playlist").html(data);
}

$(document).on("change mousemove", "#id_music_vol", function()
{
    update_slider_value($(this), function(slider_value)
    {
        return parseFloat(slider_value * 100).toFixed();
    });
});

$(document).on("change mousemove", "#id_music_fade_seconds", function()
{
    update_slider_value($(this), function(slider_value)
    {
        return parseFloat(slider_value).toFixed();
    });
});

$(document).on("change mousemove", "#id_sunrise_brightness", update_sunrise_brightness);

$(document).on("change mousemove", "#id_sunrise_fade_minutes", function()
{
    update_slider_value($(this), function(slider_value)
    {
        return parseFloat(slider_value).toFixed();
    });
});

$(document).on("change mousemove", "#id_sunrise_color", function()
{
    var id = $(this).attr("id");
    var field = id.replace("id_", "");
    var value_id = field + "_value";
    var value = "#" + range_to_rgb(parseFloat($(this).val()));
    $("#" + value_id).css("background-color", value);
    update_sunrise_brightness();
});

$(document).on("click", "#save", function()
{
    $("#button").val("save");
    submit();
})

$(document).on("click", "#delete", function()
{
    $("#button").val("delete");
    submit();
})

function submit()
{
    $.ajax({
       type: "POST",
       url: "/alarm/change",
       headers: { "X-CSRFToken": getCookie("csrftoken") },
       data: $("#alarmForm").serialize(),
       success: form_callback,
       dataType: "json"
     });
}

function form_callback(data)
{
    if(data.valid == true)
    {
        window.location.href = "/alarms";
    }
    else
    {
        if(data.action == "save")
        {
            alert("Saving Failed!");
        }
        else
        {
            alert("Deleting Failed!");
        }
    }
}

function update_sunrise_brightness()
{
    update_slider_value($("#id_sunrise_brightness"), function(slider_value)
    {
        color = parseFloat($("#id_sunrise_color").val());
        color_adj = (1 - Math.abs(color)) * 0.5 + 0.5;
        return parseFloat(slider_value * color_adj * 100).toFixed();
    });
}

function update_slider_value(cur_slider, converter)
{
    var id = cur_slider.attr("id");
    var field = id.replace("id_", "");
    var value_id = field + "_value";
    var value = converter(cur_slider.val());
    $("#" + value_id).html(value);
}

function range_to_rgb(range)
{
    var temp = range_to_temp(range);
    var rgb = temp_to_rgb(temp);
    return rgb;
}

function range_to_temp(range)
{
    var neg_range = -range;
    var warm = 2200;
    var cool = 5700;

    var warm_weight = 1;
    var cool_weight = 1;

    if(neg_range < 0)
    {
        warm_weight = 1;
        cool_weight = 1 + neg_range;
    }
    else
    {
        warm_weight = 1 - neg_range;
        cool_weight = 1;
    }

    var temp = (warm * warm_weight + cool * cool_weight) / (warm_weight + cool_weight);
    return temp;
}

// Algorithm from here: http://www.tannerhelland.com/4435/convert-temperature-rgb-algorithm-code/
function temp_to_rgb(temp)
{
    var red = 255;
    var green = 255;
    var blue = 255;
    var adj_temp = temp / 100;

    if(adj_temp <= 66)
    {
        red = 255;
    }
    else
    {
        red = limit_rgb(329.698727446 * Math.pow(adj_temp - 60, -0.1332047592));
    }

    if(adj_temp <= 66)
    {
        green = limit_rgb(99.4708025861 * Math.log(adj_temp) - 161.1195681661);
    }

    if(adj_temp >= 66)
    {
        blue = 255;
    }
    else
    {
        if(adj_temp <= 19)
        {
            blue = 0;
        }
        else
        {
            blue = limit_rgb(138.5177312231 * Math.log(adj_temp - 10) - 305.0447927307);
        }
    }

    var rgb = number_to_hex(red) + number_to_hex(green) + number_to_hex(blue);
    return rgb;
}

function number_to_hex(number)
{
    return ("00" + parseInt(number.toFixed()).toString(16)).substr(-2);
}

function limit_rgb(value)
{
    var limited_value = value;
    if(value < 0)
    {
        limited_value = 0;
    }
    else if(value > 255)
    {
        limited_value = 255;
    }
    else
    {
        limited_value = value;
    }

    return limited_value;
}
