function enable(alarmid)
{
    $.ajax({
       type: "POST",
       url: "/alarms/enable",
       headers: { "X-CSRFToken": getCookie("csrftoken") },
       data: $("#enable_" + alarmid).serialize(),
       success: enable_callback,
       dataType: "json"
     });
}

function enable_callback(data)
{
    if(data.valid == true)
    {
        if(data.enabled == true)
        {
            $("#" + data.alarmid + "_enabled").attr("src", "/static/alarms/images/checkmark.png");
        }
        else
        {
            $("#" + data.alarmid + "_enabled").attr("src", "/static/shared/images/blank.png");
        }
    }
}
