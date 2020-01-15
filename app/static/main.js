$(function() {
  $('button.switch').click(function() {
    $.ajax({
      url: '/switch',
      contentType: 'application/json',
      data: JSON.stringify({
        'switch': $(this).data('switch') == 'on' ? true : false,
        'id': $(this).data('device-id').toString()
      }),
      type: 'POST'
    })
  })
})