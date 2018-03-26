function addLabel(){
var element = $('#label_input')
var id = generateID(4);
$('#label_table tr:last').after('<tr id='+id+' ><td><input type="hidden" name="labels[]" value = "'+element.val()+'"/> '+element.val()+'</td><td><input name = files[] type="file"/></td><td><button onclick=removeRowById('+id+')>Remove</button></td></tr>');
}

function removeRowById(id){
var element = $(id)
element.remove()
}

function generateID(length) {
    let text = ""
    const possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    for(let i = 0; i < length; i++)  {
        text += possible.charAt(Math.floor(Math.random() * possible.length))
    }

    return text
}

function startLearning(){
    console.log('Submiting Learning data')
    var formdata = new FormData($('#form')[0]);
    msg = $('#message');
    msg.html('<p>Starting.... </p>')
    url_post = 'api/retrain'
    $.ajax(
            {
                 url:url_post,
                 type:'POST',
                 data: formdata,
                 processData:false,
                 contentType:false,
                 success: function( data, statusCode, xhr ) {
                  msg.html( data.msg );
                },
                error: function(xhr, statusCode, err){
                alert('Error', err)
                msg.html('<p>Failure.... </p>')
                }
            }
        )
}

$('#form').on('submit', function(e){
e.preventDefault();
startLearning();
})