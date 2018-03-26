function evaluate (e){


    var formData = new FormData();
    formData.append('file', $('#picture')[0].files[0]);
    formData.append('folder_name', $('input[name=model]:checked').val())

    msgbox = $('#message')
    msgbox.html('<h3>Please wait...</h3>')
    $.ajax({
           url : 'api/evaluate',
           type : 'POST',
           data : formData,
           processData: false,  // tell jQuery not to process the data
           contentType: false,  // tell jQuery not to set contentType
           success : function(data, statusText, xhr) {
               data = JSON.parse(data)
               console.log(data);
               result_table = $('<table class="table" id="result"><thead> <tr><th>Label</th><th>Confidence</th></tr></thead><tbody></tbody></table>')
               for(res of data[1]){
               result_table.find('tbody').append('<tr><td>'+res[0]+'</td><td>'+Number(res[1])*100+'%</td></tr>')
               }
               msgbox.html('<img height="500px" src="'+data[0]+'" />')
               msgbox.prepend(result_table)
           },
           error: function(xhr, statusText, err){
            alert("Error:" + xhr.status);
          }
    });

}

  $('#form').on('submit', function(e){
      e.preventDefault();
      evaluate(e)
  });