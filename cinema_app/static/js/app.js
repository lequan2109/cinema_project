document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.seat-select').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const seat = this.dataset.seat;
      const input = document.getElementById('seat_input');
      if (input) input.value = seat;
      document.querySelectorAll('.seat-select').forEach(b => b.classList.remove('btn-secondary'));
      this.classList.add('btn-secondary');
    });
  });
});
