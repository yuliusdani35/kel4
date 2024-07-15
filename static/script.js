// Ambil elemen ikon bantuan dan pop-up container
const helpIcon = document.getElementById('help-icon');
const popup = document.getElementById('popup');
const closePopup = document.getElementById('close-popup');

// Tambahkan event listener untuk ikon bantuan
helpIcon.addEventListener('click', function () {
    popup.classList.add('active'); // Tampilkan pop-up
});

closePopup.addEventListener('click', function () {
    popup.classList.remove('active');
});