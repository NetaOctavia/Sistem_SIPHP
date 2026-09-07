from datetime import timedelta
import json
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Berita, HargaKomoditas, Komoditas, Pasar, PesanKontak


def beranda(request):
    selected_pasar_id = request.GET.get("pasar_id", "")
    daftar_pasar = Pasar.objects.all().order_by("nama_pasar")

    # Ambil entri harga terbaru
    harga_qs = HargaKomoditas.objects.all()
    if selected_pasar_id:
        harga_qs = harga_qs.filter(pasar_id=selected_pasar_id)

    latest_entry = harga_qs.order_by("-tanggal").first()
    today = latest_entry.tanggal if latest_entry else timezone.now().date()
    yesterday = today - timedelta(days=1)

    avg_harga_query = HargaKomoditas.objects.filter(tanggal=today)
    if selected_pasar_id:
        avg_harga_query = avg_harga_query.filter(pasar_id=selected_pasar_id)

    avg_harga = avg_harga_query.aggregate(Avg("harga"))["harga__avg"] or 0
    berita_list = Berita.objects.all().order_by("-created_at")[:3]

    harga_today = HargaKomoditas.objects.filter(tanggal=today).select_related(
        "komoditas", "pasar"
    )
    if selected_pasar_id:
        harga_today = harga_today.filter(pasar_id=selected_pasar_id)

    data_harga_formatted = []

    for h in harga_today:
        h_kemarin = (
            HargaKomoditas.objects.filter(
                komoditas=h.komoditas, pasar=h.pasar, tanggal=yesterday
            ).first()
            if h.pasar
            else None
        )

        harga_kemarin_val = h_kemarin.harga if h_kemarin else 0
        perubahan = h.harga - harga_kemarin_val if h_kemarin else 0

        data_harga_formatted.append({
            "nama_item": (
                f"{h.komoditas.nama} ({h.pasar.nama_pasar})"
                if h.pasar
                else h.komoditas.nama
            ),
            "satuan": h.komoditas.satuan,
            "harga_kemarin": harga_kemarin_val,
            "harga_hari_ini": h.harga,
            "perubahan": perubahan,
            "perubahan_abs": abs(perubahan),
        })

    # LOGIKA GRAFIK TREN HARGA 7 HARI TERAKHIR
    start_date = today - timedelta(days=6)
    dates_list = [(start_date + timedelta(days=i)) for i in range(7)]
    dates_label = [d.strftime("%d %b") for d in dates_list]

    daftar_komoditas = Komoditas.objects.all()

    colors = [
        {"border": "#10B981", "bg": "rgba(16, 185, 129, 0.1)"},
        {"border": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)"},
        {"border": "#3B82F6", "bg": "rgba(59, 130, 246, 0.1)"},
        {"border": "#F59E0B", "bg": "rgba(245, 158, 11, 0.1)"},
        {"border": "#8B5CF6", "bg": "rgba(139, 92, 246, 0.1)"},
    ]

    chart_datasets = []
    for idx, kom in enumerate(daftar_komoditas):
        data_harga_per_hari = []
        for d in dates_list:
            entries = HargaKomoditas.objects.filter(komoditas=kom, tanggal=d)
            if selected_pasar_id:
                entries = entries.filter(pasar_id=selected_pasar_id)

            if entries.exists():
                avg_val = entries.aggregate(Avg("harga"))["harga__avg"]
                nilai_harga = float(avg_val) if avg_val else 0
            else:
                nilai_harga = 0
            data_harga_per_hari.append(nilai_harga)

        color_scheme = colors[idx % len(colors)]
        chart_datasets.append({
            "label": kom.nama,
            "data": data_harga_per_hari,
            "borderColor": color_scheme["border"],
            "backgroundColor": color_scheme["bg"],
            "fill": True,
            "tension": 0.3,
        })

    context = {
        "avg_harga": round(avg_harga),
        "tanggal_terbaru": today,
        "tanggal_kemarin": yesterday,
        "data_harga": data_harga_formatted,
        "berita_list": berita_list,
        "daftar_pasar": daftar_pasar,
        "selected_pasar_id": selected_pasar_id,
        "komoditas_naik": sum(
            1 for item in data_harga_formatted if item["perubahan"] > 0
        ),
        "komoditas_turun": sum(
            1 for item in data_harga_formatted if item["perubahan"] < 0
        ),
        "chart_labels": json.dumps(dates_label, cls=DjangoJSONEncoder),
        "chart_datasets": json.dumps(chart_datasets, cls=DjangoJSONEncoder),
    }
    return render(request, "dashboard/beranda.html", context)


def user_login(request):
    if request.user.is_authenticated:
        return redirect("harga_komoditas")

    if request.method == "POST":
        username_req = request.POST.get("username")
        password_req = request.POST.get("password")

        user = authenticate(
            request, username=username_req, password=password_req
        )

        if user is not None:
            login(request, user)
            messages.success(
                request, f"Selamat datang kembali, {user.username}!"
            )
            return redirect("harga_komoditas")
        else:
            messages.error(request, "Username atau password salah!")

    return render(request, "auth_custom/login.html")


def user_logout(request):
    logout(request)
    messages.info(request, "Anda telah berhasil keluar.")
    return redirect("beranda")


def register(request):
    if request.user.is_authenticated:
        return redirect("harga_komoditas")

    if request.method == "POST":
        username_req = request.POST.get("username")
        email_req = request.POST.get("email")
        password_req = request.POST.get("password")
        password_confirm = request.POST.get("password_confirm")

        if password_req != password_confirm:
            messages.error(request, "Konfirmasi password tidak cocok!")
            return render(request, "auth_custom/register.html")

        if User.objects.filter(username=username_req).exists():
            messages.error(request, "Username sudah terdaftar!")
            return render(request, "auth_custom/register.html")

        user = User.objects.create_user(
            username=username_req, email=email_req, password=password_req
        )
        user.save()
        messages.success(request, "Pendaftaran berhasil! Silakan login.")
        return redirect("login")

    return render(request, "auth_custom/register.html")


def berita(request):
    berita_list = Berita.objects.all().order_by("-created_at")
    return render(
        request, "dashboard/berita.html", {"berita_list": berita_list}
    )


def komoditas(request):
    daftar_komoditas_qs = Komoditas.objects.all().order_by("nama")
    daftar_pasar = Pasar.objects.all().order_by("nama_pasar")

    selected_id = request.GET.get("komoditas_id", "")
    selected_pasar_id = request.GET.get("pasar_id", "")
    keyword = request.GET.get("q", "")

    today = timezone.now().date()
    start_date = today - timedelta(days=6)
    dates_list = [(start_date + timedelta(days=i)) for i in range(7)]
    dates_label = [d.strftime("%d %b") for d in dates_list]

    komoditas_filtered = daftar_komoditas_qs
    if selected_id:
        komoditas_filtered = komoditas_filtered.filter(id=selected_id)
    if keyword:
        komoditas_filtered = komoditas_filtered.filter(nama__icontains=keyword)

    colors = [
        {"border": "#10B981", "bg": "rgba(16, 185, 129, 0.1)"},
        {"border": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)"},
        {"border": "#3B82F6", "bg": "rgba(59, 130, 246, 0.1)"},
        {"border": "#F59E0B", "bg": "rgba(245, 158, 11, 0.1)"},
        {"border": "#8B5CF6", "bg": "rgba(139, 92, 246, 0.1)"},
    ]

    chart_datasets = []
    daftar_komoditas_dengan_harga = []

    for idx, kom in enumerate(komoditas_filtered):
        data_harga_per_hari = []
        for d in dates_list:
            entries = HargaKomoditas.objects.filter(komoditas=kom, tanggal=d)
            if selected_pasar_id:
                entries = entries.filter(pasar_id=selected_pasar_id)

            if entries.exists():
                avg_val = entries.aggregate(Avg("harga"))["harga__avg"]
                nilai_harga = int(avg_val) if avg_val else 0
            else:
                nilai_harga = 0
            data_harga_per_hari.append(nilai_harga)

        # Ambil rata-rata harga terakhir untuk tabel
        last_entries = HargaKomoditas.objects.filter(komoditas=kom)
        if selected_pasar_id:
            last_entries = last_entries.filter(pasar_id=selected_pasar_id)

        last_entries = last_entries.order_by("-tanggal")

        if last_entries.exists():
            latest_date = last_entries.first().tanggal
            query_latest = HargaKomoditas.objects.filter(
                komoditas=kom, tanggal=latest_date
            )
            if selected_pasar_id:
                query_latest = query_latest.filter(pasar_id=selected_pasar_id)

            avg_last = query_latest.aggregate(Avg("harga"))["harga__avg"]
            harga_terakhir_val = int(avg_last) if avg_last else 0
        else:
            harga_terakhir_val = 0

        daftar_komoditas_dengan_harga.append({
            "id": kom.id,
            "nama": kom.nama,
            "satuan": kom.satuan,
            "harga_terakhir": f"{harga_terakhir_val:,}".replace(",", "."),
        })

        color_scheme = colors[idx % len(colors)]
        chart_datasets.append({
            "label": kom.nama,
            "data": data_harga_per_hari,
            "borderColor": color_scheme["border"],
            "backgroundColor": color_scheme["bg"],
            "fill": True,
            "tension": 0.3,
        })

    context = {
        "daftar_komoditas": daftar_komoditas_dengan_harga,
        "daftar_pasar": daftar_pasar,
        "selected_id": selected_id,
        "selected_pasar_id": selected_pasar_id,
        "keyword": keyword,
        "chart_labels": json.dumps(dates_label, cls=DjangoJSONEncoder),
        "chart_datasets": json.dumps(chart_datasets, cls=DjangoJSONEncoder),
    }
    return render(request, "dashboard/komoditas.html", context)


def kontak(request):
    if request.method == "POST":
        nama = request.POST.get("nama", "").strip()
        email = request.POST.get("email", "").strip()
        telepon = request.POST.get("telepon", "").strip()
        subjek = request.POST.get("subjek", "").strip()
        pesan = request.POST.get("pesan", "").strip()

        if nama and email and subjek and pesan:
            PesanKontak.objects.create(
                nama=nama,
                email=email,
                telepon=telepon,
                subjek=subjek,
                pesan=pesan,
                is_read=False,
            )
            messages.success(
                request, "Pesan Anda berhasil dikirim! Terima kasih atas masukannya."
            )
            return redirect("kontak")
        else:
            messages.error(
                request, "Harap isi semua kolom wajib (Nama, Email, Subjek, Pesan)!"
            )

    return render(request, "dashboard/kontak.html")


def profil(request):
    return render(request, "dashboard/profil.html")


def layanan_teknis(request):
    return render(request, "dashboard/layanan_teknis.html")


# ADMIN MANAGEMENT VIEWS - KELOLA HARGA & KOMODITAS
@login_required
def harga_komoditas(request):
    if request.method == "POST":
        # 1. Form Tambah Pasar Baru
        if "tambah_pasar" in request.POST:
            nama_pasar_baru = request.POST.get("nama_pasar_baru")
            if nama_pasar_baru:
                pasar_obj, _ = Pasar.objects.get_or_create(
                    nama_pasar=nama_pasar_baru.strip()
                )
                messages.success(
                    request, f'Pasar "{pasar_obj.nama_pasar}" berhasil ditambahkan!'
                )
                return redirect(f"/kelola-harga/?pasar_id={pasar_obj.id}")
            return redirect("harga_komoditas")

        # 2. Form Tambah Komoditas Baru
        if "tambah_komoditas" in request.POST:
            nama_komoditas = request.POST.get("nama_komoditas")
            satuan = request.POST.get("satuan", "kg")
            if nama_komoditas:
                Komoditas.objects.get_or_create(
                    nama=nama_komoditas.strip(), defaults={"satuan": satuan}
                )
                messages.success(
                    request,
                    f'Komoditas "{nama_komoditas}" berhasil ditambahkan ke sistem!',
                )
            return redirect("harga_komoditas")

        # 3. Form Simpan Perubahan Harga Komoditas
        pasar_id = request.POST.get("pasar_id")
        tanggal_input = request.POST.get("tanggal")
        tanggal = tanggal_input if tanggal_input else timezone.now().date()

        if not pasar_id:
            messages.error(request, "Silakan pilih pasar terlebih dahulu.")
            return redirect("harga_komoditas")

        pasar_obj = get_object_or_404(Pasar, id=pasar_id)

        count_updated = 0
        for key, val in request.POST.items():
            if key.startswith("harga_") and val.strip() != "":
                try:
                    komoditas_id = int(key.replace("harga_", ""))
                    val_clean = "".join(filter(str.isdigit, val))

                    if val_clean:
                        harga_val = int(val_clean)
                        komoditas_obj = Komoditas.objects.get(id=komoditas_id)

                        # Menyimpan unik berdasarkan kombinasi (komoditas, pasar, tanggal)
                        HargaKomoditas.objects.update_or_create(
                            komoditas=komoditas_obj,
                            pasar=pasar_obj,
                            tanggal=tanggal,
                            defaults={
                                "harga": harga_val,
                                "diinput_oleh": request.user,
                            },
                        )
                        count_updated += 1
                except (ValueError, Komoditas.DoesNotExist):
                    continue

        if count_updated > 0:
            messages.success(
                request,
                f"Berhasil memperbarui harga {count_updated} komoditas di {pasar_obj.nama_pasar}!",
            )
        else:
            messages.warning(
                request, "Tidak ada harga komoditas yang dimasukkan atau diubah."
            )

        return redirect(f"/kelola-harga/?pasar_id={pasar_obj.id}&tanggal={tanggal}")

    # --- TAMPILAN GET REQUEST ---
    daftar_pasar = Pasar.objects.all().order_by("nama_pasar")
    selected_pasar_id = request.GET.get("pasar_id")
    selected_tanggal = request.GET.get(
        "tanggal", timezone.now().date().strftime("%Y-%m-%d")
    )

    pasar_aktif = None
    if selected_pasar_id:
        pasar_aktif = Pasar.objects.filter(id=selected_pasar_id).first()
    elif daftar_pasar.exists():
        pasar_aktif = daftar_pasar.first()

    daftar_komoditas = Komoditas.objects.all().order_by("nama")
    list_komoditas_dengan_harga = []

    for kom in daftar_komoditas:
        harga_existing = None
        harga_terakhir_val = 0

        if pasar_aktif:
            harga_existing_obj = HargaKomoditas.objects.filter(
                komoditas=kom, pasar=pasar_aktif, tanggal=selected_tanggal
            ).first()
            if harga_existing_obj:
                harga_existing = int(harga_existing_obj.harga)

            harga_terakhir_obj = (
                HargaKomoditas.objects.filter(komoditas=kom, pasar=pasar_aktif)
                .order_by("-tanggal", "-id")
                .first()
            )
            if harga_terakhir_obj:
                harga_terakhir_val = int(harga_terakhir_obj.harga)

        list_komoditas_dengan_harga.append({
            "id": kom.id,
            "nama": kom.nama,
            "satuan": kom.satuan or "kg",
            "harga_existing": harga_existing,
            "harga_terakhir": harga_terakhir_val,
        })

    return render(
        request,
        "auth_custom/kelola_harga.html",
        {
            "komoditas_list": list_komoditas_dengan_harga,
            "daftar_pasar": daftar_pasar,
            "pasar_aktif": pasar_aktif,
            "tanggal_input": selected_tanggal,
            "today_date": timezone.now().date().strftime("%Y-%m-%d"),
        },
    )


@login_required
def hapus_pasar(request, pasar_id):
    pasar = get_object_or_404(Pasar, id=pasar_id)
    nama_pasar = pasar.nama_pasar
    pasar.delete()
    messages.success(request, f'Pasar "{nama_pasar}" berhasil dihapus.')
    return redirect("harga_komoditas")


@login_required
def edit_komoditas(request, id):
    kom = get_object_or_404(Komoditas, id=id)

    if request.method == "POST":
        nama = request.POST.get("nama")
        satuan = request.POST.get("satuan")
        harga_input = request.POST.get("harga")
        pasar_id = request.POST.get("pasar_id")

        if nama and satuan:
            kom.nama = nama.strip()
            kom.satuan = satuan.strip()
            kom.save()

            if harga_input:
                val_clean = "".join(filter(str.isdigit, harga_input))
                if val_clean:
                    harga_val = int(val_clean)
                    today = timezone.now().date()

                    pasar_target = None
                    if pasar_id:
                        pasar_target = Pasar.objects.filter(id=pasar_id).first()
                    if not pasar_target:
                        pasar_target = Pasar.objects.first()

                    if pasar_target:
                        HargaKomoditas.objects.update_or_create(
                            komoditas=kom,
                            pasar=pasar_target,
                            tanggal=today,
                            defaults={
                                "harga": harga_val,
                                "diinput_oleh": request.user,
                            },
                        )

            messages.success(
                request, f'Data komoditas "{kom.nama}" berhasil diperbarui!'
            )
        else:
            messages.error(request, "Nama dan satuan komoditas wajib diisi!")

    return redirect("harga_komoditas")


@login_required
def hapus_komoditas(request, id):
    kom = get_object_or_404(Komoditas, id=id)
    kom.delete()
    messages.success(request, f'Komoditas "{kom.nama}" berhasil dihapus.')
    return redirect("harga_komoditas")


# ADMIN MANAGEMENT VIEWS - BERITA & KONTAK
@login_required
def kelola_berita(request):
    if request.method == "POST":
        judul = request.POST.get("judul")
        link_input = request.POST.get("url_sumber", "")

        if link_input and not link_input.startswith(("http://", "https://")):
            link_input = "https://" + link_input

        gambar_url = request.POST.get("gambar_url", "")
        ringkasan = request.POST.get("ringkasan", "")

        Berita.objects.create(
            judul=judul,
            url_sumber=link_input,
            gambar_url=gambar_url,
            ringkasan=ringkasan,
        )
        messages.success(request, "Berita berhasil ditambahkan!")
        return redirect("kelola_berita")

    berita_qs = Berita.objects.all().order_by("-created_at")
    return render(
        request,
        "auth_custom/kelola_berita.html",
        {
            "daftar_berita": berita_qs,
            "berita_list": berita_qs,
        },
    )


@login_required
def edit_berita(request, id):
    berita_obj = get_object_or_404(Berita, id=id)
    if request.method == "POST":
        berita_obj.judul = request.POST.get("judul")

        link_input = request.POST.get("url_sumber", "")
        if link_input and not link_input.startswith(("http://", "https://")):
            link_input = "https://" + link_input

        berita_obj.url_sumber = link_input
        berita_obj.gambar_url = request.POST.get("gambar_url", "")
        berita_obj.ringkasan = request.POST.get("ringkasan", "")

        berita_obj.save()
        messages.success(request, "Berita berhasil diperbarui!")
    return redirect("kelola_berita")


@login_required
def hapus_berita(request, id):
    berita_obj = get_object_or_404(Berita, id=id)
    berita_obj.delete()
    messages.success(request, "Berita berhasil dihapus!")
    return redirect("kelola_berita")


@login_required
def kelola_kontak(request):
    pesan_list = PesanKontak.objects.all().order_by("-created_at")
    return render(
        request,
        "auth_custom/kelola_kontak.html",
        {"pesan_list": pesan_list},
    )


@login_required
def hapus_kontak(request, id):
    pesan_obj = get_object_or_404(PesanKontak, id=id)
    pesan_obj.delete()
    messages.success(request, "Pesan kontak berhasil dihapus!")
    return redirect("kelola_kontak")