// نقشه
var map = L.map('map').setView([35.6892, 51.3890], 13);

L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/">OSM</a>',
    maxZoom: 19
}).addTo(map);

var marker = null;

// افزودن Marker ساده
function addMarker(latlng) {
    if (marker) {
        marker.setLatLng(latlng);
    } else {
        marker = L.marker(latlng, { draggable: true }).addTo(map);
        marker.on('dragend', function (event) {
            var pos = event.target.getLatLng();
            document.getElementById('id_latitude').value = pos.lat.toFixed(6);
            document.getElementById('id_longitude').value = pos.lng.toFixed(6);
        });
    }
    document.getElementById('id_latitude').value = latlng.lat.toFixed(6);
    document.getElementById('id_longitude').value = latlng.lng.toFixed(6);
}

// Marker پیش‌فرض وسط نقشه
addMarker(L.latLng(35.6892, 51.3890));

// کلیک روی نقشه
map.on('click', function (e) {
    addMarker(e.latlng);
});

// دکمه مکان من پایین سمت راست
var LocateControl = L.Control.extend({
    options: { position: 'bottomright' },
    onAdd: function (map) {
        var container = L.DomUtil.create('div', 'leaflet-bar');
        var button = L.DomUtil.create('button', 'locate-btn-map', container);
        button.innerHTML = '<i class="fa fa-location-dot"></i>';
        button.title = "مکان من";

        L.DomEvent.on(button, 'click', function (e) {
            e.preventDefault();
            e.stopPropagation();
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function (position) {
                    var latlng = L.latLng(position.coords.latitude, position.coords.longitude);
                    map.setView(latlng, 16);
                    addMarker(latlng);
                }, function () {
                    alert('لطفاً دسترسی موقعیت مکانی را فعال کنید.');
                });
            } else {
                alert('مرورگر شما از Geolocation پشتیبانی نمی‌کند.');
            }
        });

        return container;
    }
});
map.addControl(new LocateControl());

// افکت hover روی کارت فرم
const card = document.querySelector('.shop-form-card');
card.addEventListener('mouseenter', () => {
    card.style.transform = 'translateY(-8px)';
    card.style.boxShadow = '16px 16px 32px #d1d9e6, -16px -16px 32px #fff';
});
card.addEventListener('mouseleave', () => {
    card.style.transform = 'translateY(0)';
    card.style.boxShadow = '12px 12px 24px #d1d9e6, -12px -12px 24px #fff';
});

// پیش‌نمایش تصویر
const imageInput = document.getElementById('id_image');
imageInput.addEventListener('change', function () {
    const file = this.files[0];
    if (file) {
        let preview = document.querySelector('.input-group img.preview');
        if (!preview) {
            preview = document.createElement('img');
            preview.classList.add('preview');
            this.parentNode.appendChild(preview);
        }
        preview.src = URL.createObjectURL(file);
    }
});