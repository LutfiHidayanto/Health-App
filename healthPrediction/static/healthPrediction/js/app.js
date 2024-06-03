// Langkah 1: Dapatkan elemen DOM
let nextDom = document.getElementById('next');
let prevDom = document.getElementById('prev');
let carouselDom = document.querySelector('.carousel');
let SliderDom = carouselDom.querySelector('.carousel .list');
let thumbnailBorderDom = document.querySelector('.carousel .thumbnail');
let thumbnailItemsDom = thumbnailBorderDom.querySelectorAll('.item');

// Langkah 2: Sisipkan thumbnail pertama ke akhir untuk tampilan awal
thumbnailBorderDom.appendChild(thumbnailItemsDom[0]);

// Langkah 3: Tambahkan event listeners untuk Tombol Selanjutnya dan Sebelumnya
nextDom.onclick = function(){
    showSlider('next');    
}

prevDom.onclick = function(){
    showSlider('prev');    
}

// Langkah 4: Tambahkan event listener ke thumbnail
let currentIndex = 0; // Set indeks saat ini awal ke 1
let previousThumbnailIndex = 0; // Menyimpan nilai indeks thumbnail sebelumnya

// Fungsi untuk mengubah currentIndex menjadi 1 di awal
function setCurrentIndexToFirst() {
    if (currentIndex === 0) {
        currentIndex = 0;
        console.log("Indeks Saat Ini:", currentIndex);
    }
}

setCurrentIndexToFirst();

thumbnailItemsDom.forEach(function(thumbnail, index) {
    thumbnail.addEventListener('click', function() {
        let thumbnailIndex = Array.from(thumbnailItemsDom).indexOf(thumbnail);

        // Penanganan jika thumbnailIndex tidak ada atau tidak valid
        if (thumbnailIndex === -1 || isNaN(thumbnailIndex)) {
            currentIndex = 1;
            console.log("Indeks Thumbnail tidak valid. Indeks Saat Ini diatur ke 1.");
            return;
        }

        // Panggil fungsi untuk mengubah latar belakang carousel
        changeCarouselBackground(thumbnailIndex);

        // Update indeks saat ini agar sesuai dengan indeks thumbnail terakhir yang diklik
        currentIndex = previousThumbnailIndex + 1; // Update indeks saat ini dengan nilai indeks thumbnail sebelumnya + 1

        // Update nilai indeks thumbnail sebelumnya
        previousThumbnailIndex = thumbnailIndex;

        // Tampilkan indeks thumbnail dan indeks saat ini di konsol
        console.log("Indeks Thumbnail:", thumbnailIndex);
        console.log("Indeks Saat Ini:", currentIndex);

        // Tampilkan slide sesuai dengan thumbnail yang diklik
        if (thumbnailIndex === 3 && currentIndex === 2) {
            showSlider('next');
            showSlider('next');
        } else if (thumbnailIndex === 2 && currentIndex === 2) {
            showSlider('next');
        } else if (thumbnailIndex === 0 && currentIndex === 2) {
            showSlider('prev');
        } else if (thumbnailIndex === 1 && currentIndex === 1) {
            showSlider('next');
        } else if (thumbnailIndex === 2 && currentIndex === 1) {
            showSlider('next');
            showSlider('next');
        } else if (thumbnailIndex === 3 && currentIndex === 1) {
            showSlider('next');
            showSlider('next');
            showSlider('next');
        } else if (thumbnailIndex === 0 && currentIndex === 3) {
            showSlider('prev');
            showSlider('prev');
        } else if (thumbnailIndex === 1 && currentIndex === 3) {
            showSlider('prev');
        } else if (thumbnailIndex === 3 && currentIndex === 3) {
            showSlider('next');
        } else if (thumbnailIndex === 2 && currentIndex === 4) {
            showSlider('prev');
        } else if (thumbnailIndex === 1 && currentIndex === 4) {
            showSlider('prev');
            showSlider('prev');
        } else if (thumbnailIndex === 0 && currentIndex === 4) {
            showSlider('prev');
            showSlider('prev');
            showSlider('prev');
        }
    });
});

// Langkah 5: Fungsi untuk menampilkan slide dan menambahkan kelas 'active' untuk efek kilauan
function showSlider(type){
    let  SliderItemsDom = SliderDom.querySelectorAll('.carousel .list .item');
    let thumbnailItemsDom = document.querySelectorAll('.carousel .thumbnail .item');
    
    if(type === 'next'){
        SliderDom.appendChild(SliderItemsDom[0]);
        thumbnailBorderDom.appendChild(thumbnailItemsDom[0]);
        carouselDom.classList.add('next');
    } else {
        SliderDom.prepend(SliderItemsDom[SliderItemsDom.length - 1]);
        thumbnailBorderDom.prepend(thumbnailItemsDom[thumbnailItemsDom.length - 1]);
        carouselDom.classList.add('prev');
    }
    
    // Hapus kelas 'next' atau 'prev' setelah animasi
    carouselDom.addEventListener('transitionend', function(){
        let activeSlide = SliderDom.querySelector('.item.active');
        if (activeSlide) {
            activeSlide.classList.remove('active');
        }
        let newActiveSlide = SliderDom.querySelector('.item');
        newActiveSlide.classList.add('active');
        carouselDom.classList.remove('next');
        carouselDom.classList.remove('prev');
    }, { once: true });
}

// Langkah 6: Fungsi untuk mendapatkan indeks slide saat ini
function getCurrentSlideIndex() {
    let currentSlide = SliderDom.querySelector('.item');
    let currentIndex = Array.from(SliderDom.children).indexOf(currentSlide);
    
    // Set default currentIndex ke 1 jika tidak terdefinisi
    if (typeof currentIndex === 'undefined' || currentIndex === 0) {
        currentIndex = 1;
    }

    return currentIndex;
}

// Langkah 7: Secara awal, atur slide pertama sebagai aktif untuk efek kilauan
let firstSlide = SliderDom.querySelector('.item');
firstSlide.classList.add('active');

// Langkah 8: Fungsi untuk mengubah latar belakang carousel berdasarkan thumbnail
function changeCarouselBackground(thumbnailIndex) {
    let imageNames = ['img1.jpg', 'img2.jpg', 'img3.jpg', 'img4.jpg'];

    // Ganti latar belakang carousel dengan gambar yang sesuai
    let imageUrl = `image/${imageNames[thumbnailIndex]}`;
    carouselDom.style.backgroundImage = `url('${imageUrl}')`;
}

// Ambil elemen header
let header = document.querySelector('header');

// Fungsi untuk mengubah warna navbar sesuai dengan thumbnail yang diklik
function changeNavbarColor(thumbnailIndex) {
    // Temukan elemen nav dengan ID headernav
    var navbar = document.getElementById('headernav');

    // Ubah warna navbar berdasarkan thumbnailIndex
    switch(thumbnailIndex) {
        case 1:
            navbar.style.backgroundColor = "#f1683a"; // Warna merah muda
            break;
        case 2:
            navbar.style.backgroundColor = "#d2b48c"; // Warna coklat muda
            break;
        case 3:
            navbar.style.backgroundColor = "#808080"; // Warna abu-abu
            break;
        case 4:
            navbar.style.backgroundColor ="#800080"; // Warna ungu muda
            break;
        default:
            navbar.style.backgroundColor = "#f1683a"; // Warna default jika thumbnail tidak cocok
    }
}

document.addEventListener("DOMContentLoaded", function() {
    // Cari tombol "See More" di setiap daftar
    let seeMoreButtons = document.querySelectorAll('.carousel .item .buttons button');
    let previousContainerCard = null; // variabel untuk menyimpan containerCard sebelumnya

    seeMoreButtons.forEach(function(button, index) {
        button.addEventListener('click', function() {
            // Dapatkan nomor daftar dari indeks (dimulai dari 0)
            let listNumber = index + 1;

            // Dapatkan kontainer card sesuai dengan nomor daftar
            let containerCard = document.querySelector(`.containerCard${listNumber}`);

            // Tambahkan kelas "hidden" pada semua containerCard
            document.querySelectorAll('.containerCard').forEach(function(card) {
                card.classList.add('hidden');
            });

            // Hapus kelas "hidden" pada containerCard yang sesuai dengan nomor daftar
            containerCard.classList.remove('hidden');

                      // Dapatkan posisi offset dari containerCard yang sesuai
                      let containerCardOffset = containerCard.offsetTop;

                      // Jika ini adalah slide ke-2, scroll ke bawah sejauh 500px saja
                      if (listNumber === 2) {
                          window.scrollBy({
                              top: 610,
                              behavior: "smooth"
                          });
                      } else {
                          // Jika bukan slide ke-2, scroll ke posisi awal dari containerCard yang sesuai
                          window.scrollTo({
                              top: containerCardOffset,
                              behavior: "smooth"
                          });
                      }
          
            // Tampilkan nomor daftar yang dipilih di konsol
            console.log("Daftar yang dipilih:", listNumber);

            // Tambahkan kelas "hidden" pada .containerCard sebelumnya
            if (previousContainerCard && previousContainerCard !== containerCard) {
                previousContainerCard.classList.add('hidden');
            }

            // Simpan containerCard saat ini sebagai previousContainerCard
            previousContainerCard = containerCard;
        });
    });
});

document.addEventListener("DOMContentLoaded", function() {
    // Cari semua thumbnail
    let thumbnails = document.querySelectorAll('.thumbnail .item');

    thumbnails.forEach(function(thumbnail) {
        thumbnail.addEventListener('click', function() {
            // Atur animasi scroll ke bagian atas halaman
            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        });
    });
});

// Kemudian, pada bagian JavaScript Anda yang lain, panggil fungsi ini saat thumbnail diklik:
thumbnailItemsDom.forEach(function(thumbnail, index) {
    thumbnail.addEventListener('click', function() {
        let thumbnailIndex = Array.from(thumbnailItemsDom).indexOf(thumbnail);

        // Panggil fungsi untuk mengubah warna navbar
        changeNavbarColor(thumbnailIndex + 1); // Tambahkan +1 karena indeks dimulai dari 0
    });
});

