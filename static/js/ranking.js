

function user_rating(id){
    $.ajax({
        url: "usuario/ranking/",
        method: 'GET',
        data : {
            'title':document.getElementById('title-'+id).value,
        'rating': document.getElementById('ra-'+id).value}
    });
    document.getElementById('exit-'+id).click()
}