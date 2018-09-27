    $('.log-out').on('click', function(){
      var token = JSON.parse(localStorage.getItem('Token'));
        $.ajax({
          url: "{{url('user.token.remove')}}",
          type: 'GET',
          data: {'token': token},
        })
        .done(function(res) {
          console.log("success");
          localStorage.removeItem('Token');
          window.location.href = "{{url('inventory.signin')}}";
        })
        .fail(function() {
          console.log("error");
        })
        .always(function() {
          localStorage.removeItem('Token');
          window.location.href = "{{url('inventory.signin')}}";
          console.log("complete");
        });        
    });
