window.onload = function(){
    // show pop modal on operation
    $('#myModal').modal('show');
    // Get the id of the state
    $('#state').on('change', function(){
        // let pop = this.value
        var state_id =  $("#state").find("option:selected").attr("title"); 
        console.log(state_id)   
        
        // Perform ajax call to send id to the backend to query database
        $.ajax({
            url : '/local-govts',
            type : 'POST',
            dataType : 'json',
            contentType : 'application/json',
            data : JSON.stringify({
                'state_id' : state_id,
            }),
            cache : false,
            success: function(){
                $.ajax({
                    url : "/api/local-govt",
                    success: function(data){        
                        $('#lga').html(data['html_string_selected'])
                    }
                })
            }
        })
       
    })
    $('.clickable').click(function(){

    })

    

}

