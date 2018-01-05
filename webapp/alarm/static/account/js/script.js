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
       url: "/account/change",
       headers: { "X-CSRFToken": getCookie("csrftoken") },
       data: $("#accountForm").serialize(),
       success: callback,
       dataType: "json"
     });
}

function callback(data)
{
    if(data.valid == true)
    {
        window.location.href = "/accounts";
    }
    else
    {
        if(data.action == "save")
        {
            alert("Invalid username/password!");
        }
        else
        {
            alert("Account does not exist!");
        }
    }
}

function nothing()
{

}
