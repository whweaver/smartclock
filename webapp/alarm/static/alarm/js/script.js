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

$(document).on("click", "#Save", function()
{
    $("#button").val("save");
    submit();
})

$(document).on("click", "#Delete", function()
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

function nothing()
{

}
