$(document).ready(function() {
  $('td:nth-child(4)').each(function() {
    var $this = $(this);
    $this.text(new Date($this.text() + 'Z').toLocaleString());
  });

  $('td:nth-child(3)').each(function() {
    var $this = $(this);
    switch ($this.text()) {
      case 'Yes':
        $this.addClass('success');
        break;
      case 'Pending':
        $this.addClass('warning');
        break;
      case 'Invalid ID':
        $this.addClass('danger');
        break;
    }
  });

  $('td button').click(function() {
    var $this = $(this),
      pid = $this.parent().siblings().first().text();
    $.post("/del", {
        pid: pid
      })
      .done(function(data) {
        $this.parent().parent().remove()
      });
  });
});

