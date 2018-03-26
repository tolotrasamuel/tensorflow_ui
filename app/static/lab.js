function removeModel(id){
console.log("Removing model: "+id)
$.ajax({
type:'POST',
data:{id:id},
url:'api/deletebyid',
 success: function( data, statusCode, xhr ) {
                  location.reload();
                },
                error:function(xhr, statusCode, err){
                alert('Failed')
                console.log(xhr, statusCode)
            }
})
}