import csv
from datetime import timedelta
import json
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import Pasar
from berita.models import Berita
from komoditas.models import Komoditas
from .models import HargaKomoditas


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

    # Batch fetch semua harga kemarin (1 query)
    harga_yesterday_qs = HargaKomoditas.objects.filter(tanggal=yesterday).select_related(
        "komoditas", "pasar"
    )
    if selected_pasar_id:
        harga_yesterday_qs = harga_yesterday_qs.filter(pasar_id=selected_pasar_id)
    harga_yesterday_map = {}
    for hy in harga_yesterday_qs:
        harga_yesterday_map[(hy.komoditas_id, hy.pasar_id)] = hy.harga

    for h in harga_today:
        key = (h.komoditas_id, h.pasar_id)
        harga_kemarin_val = harga_yesterday_map.get(key, 0)
        has_yesterday = key in harga_yesterday_map
        perubahan = h.harga - harga_kemarin_val if has_yesterday else 0

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

    # Batch fetch semua harga 7 hari terakhir (1 query)
    chart_harga_qs = HargaKomoditas.objects.filter(
        tanggal__range=(start_date, today)
    )
    if selected_pasar_id:
        chart_harga_qs = chart_harga_qs.filter(pasar_id=selected_pasar_id)
    chart_agg = chart_harga_qs.values(
        'komoditas_id', 'tanggal'
    ).annotate(avg_harga=Avg('harga'))
    chart_harga_map = {}
    for item in chart_agg:
        chart_harga_map[(item['komoditas_id'], item['tanggal'])] = float(item['avg_harga'])

    chart_datasets = []
    for idx, kom in enumerate(daftar_komoditas):
        data_harga_per_hari = [
            chart_harga_map.get((kom.id, d), 0) for d in dates_list
        ]

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


@staff_member_required(login_url='login')
def dashboard_index(request):
    """
    Overview dashboard admin SIPHP ( /dashboard/ )
    """
    total_pasar = Pasar.objects.count()
    total_komoditas = Komoditas.objects.count()
    today = timezone.now().date()
    total_input_today = HargaKomoditas.objects.filter(tanggal=today).count()

    status_pasar_list = []
    for p in Pasar.objects.all().order_by("nama_pasar"):
        c = HargaKomoditas.objects.filter(pasar=p, tanggal=today).count()
        status_pasar_list.append({
            "pasar": p,
            "sudah_input": c > 0,
            "jumlah_input": c,
        })

    context = {
        "total_pasar": total_pasar,
        "total_komoditas": total_komoditas,
        "total_input_today": total_input_today,
        "status_pasar_list": status_pasar_list,
    }
    return render(request, "admin_dashboard/index.html", context)


@staff_member_required(login_url='login')
def harga_komoditas(request):
    user_pasar = None
    if hasattr(request.user, "profil_admin") and request.user.profil_admin and request.user.profil_admin.pasar:
        user_pasar = request.user.profil_admin.pasar

    if request.method == "POST":
        # 1. Form Tambah Pasar Baru (Khusus Admin Utama)
        if "tambah_pasar" in request.POST:
            if user_pasar:
                messages.error(request, "Anda tidak memiliki akses untuk menambah pasar.")
                return redirect("harga_komoditas")
            nama_pasar_baru = request.POST.get("nama_pasar_baru")
            if nama_pasar_baru:
                pasar_obj, _ = Pasar.objects.get_or_create(
                    nama_pasar=nama_pasar_baru.strip()
                )
                messages.success(
                    request, f'Pasar "{pasar_obj.nama_pasar}" berhasil ditambahkan!'
                )
                return redirect(f"/dashboard/harga/?pasar_id={pasar_obj.id}")
            return redirect("harga_komoditas")

        # 2. Form Tambah Komoditas Baru
        if "tambah_komoditas" in request.POST:
            if user_pasar:
                messages.error(request, "Hanya Admin Utama yang dapat menambah master komoditas.")
                return redirect("harga_komoditas")
            nama_komoditas_baru = request.POST.get("nama_komoditas_baru")
            satuan_baru = request.POST.get("satuan_baru", "kg")
            harga_awal = request.POST.get("harga_awal", "")

            if nama_komoditas_baru:
                kom_obj, created = Komoditas.objects.get_or_create(
                    nama=nama_komoditas_baru.strip(),
                    defaults={"satuan": satuan_baru.strip()},
                )

                if harga_awal:
                    val_clean = "".join(filter(str.isdigit, harga_awal))
                    if val_clean:
                        harga_val = int(val_clean)
                        pasar_target = user_pasar or Pasar.objects.first()
                        if pasar_target:
                            HargaKomoditas.objects.update_or_create(
                                komoditas=kom_obj,
                                pasar=pasar_target,
                                tanggal=timezone.now().date(),
                                defaults={
                                    "harga": harga_val,
                                    "diinput_oleh": request.user,
                                },
                            )
                messages.success(
                    request, f'Komoditas "{kom_obj.nama}" berhasil ditambahkan!'
                )
            return redirect("harga_komoditas")

        # 3. Form Batch Update Harga
        pasar_id = request.POST.get("pasar_id")
        tanggal_str = request.POST.get("tanggal")

        # Jika user terikat ke pasar tertentu, paksakan pasar tersebut
        if user_pasar:
            pasar_obj = user_pasar
        else:
            pasar_obj = get_object_or_404(Pasar, id=pasar_id)

        try:
            tanggal = (
                timezone.datetime.strptime(tanggal_str, "%Y-%m-%d").date()
                if tanggal_str
                else timezone.now().date()
            )
        except ValueError:
            tanggal = timezone.now().date()

        count_updated = 0

        for key, val in request.POST.items():
            if key.startswith("harga_") and val.strip():
                try:
                    komoditas_id = int(key.replace("harga_", ""))
                    val_clean = "".join(filter(str.isdigit, val))

                    if val_clean:
                        harga_val = int(val_clean)
                        komoditas_obj = Komoditas.objects.get(id=komoditas_id)

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

        return redirect(f"/dashboard/harga/?pasar_id={pasar_obj.id}&tanggal={tanggal}")

    # --- TAMPILAN GET REQUEST ---
    daftar_pasar = Pasar.objects.all().order_by("nama_pasar")
    selected_pasar_id = request.GET.get("pasar_id")
    selected_tanggal = request.GET.get(
        "tanggal", timezone.now().date().strftime("%Y-%m-%d")
    )

    pasar_aktif = None
    if user_pasar:
        pasar_aktif = user_pasar
    elif selected_pasar_id:
        pasar_aktif = Pasar.objects.filter(id=selected_pasar_id).first()
    elif daftar_pasar.exists():
        pasar_aktif = daftar_pasar.first()

    daftar_komoditas = Komoditas.objects.all().order_by("nama")
    list_komoditas_dengan_harga = []

    harga_existing_map = {}
    harga_terakhir_map = {}

    if pasar_aktif:
        for h in HargaKomoditas.objects.filter(
            pasar=pasar_aktif, tanggal=selected_tanggal
        ):
            harga_existing_map[h.komoditas_id] = int(h.harga)

        for h in HargaKomoditas.objects.filter(
            pasar=pasar_aktif
        ).order_by("tanggal", "id"):
            harga_terakhir_map[h.komoditas_id] = int(h.harga)

    for kom in daftar_komoditas:
        list_komoditas_dengan_harga.append({
            "id": kom.id,
            "nama": kom.nama,
            "satuan": kom.satuan or "kg",
            "harga_existing": harga_existing_map.get(kom.id),
            "harga_terakhir": harga_terakhir_map.get(kom.id, 0),
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


@staff_member_required(login_url='login')
def hapus_pasar(request, pasar_id):
    if request.method != "POST":
        return redirect("harga_komoditas")
    pasar = get_object_or_404(Pasar, id=pasar_id)
    nama_pasar = pasar.nama_pasar
    pasar.delete()
    messages.success(request, f'Pasar "{nama_pasar}" berhasil dihapus.')
    return redirect("harga_komoditas")


@staff_member_required(login_url='login')
def export_harga_csv(request):
    selected_pasar_id = request.GET.get("pasar_id")
    selected_tanggal = request.GET.get("tanggal")

    qs = HargaKomoditas.objects.select_related("komoditas", "pasar", "diinput_oleh").all()
    if selected_pasar_id:
        qs = qs.filter(pasar_id=selected_pasar_id)
    if selected_tanggal:
        qs = qs.filter(tanggal=selected_tanggal)

    qs = qs.order_by("-tanggal", "pasar__nama_pasar", "komoditas__nama")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    filename = f"rekap_harga_pangan_{selected_tanggal or timezone.now().date().strftime('%Y-%m-%d')}.csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    # Write BOM for Excel UTF-8 compatibility
    response.write("\ufeff".encode("utf8"))
    writer = csv.writer(response)
    writer.writerow(["No", "Tanggal", "Nama Pasar", "Komoditas", "Satuan", "Harga (Rp)", "Petugas Input"])

    for idx, item in enumerate(qs, start=1):
        writer.writerow([
            idx,
            item.tanggal.strftime("%Y-%m-%d"),
            item.pasar.nama_pasar if item.pasar else "-",
            item.komoditas.nama if item.komoditas else "-",
            item.komoditas.satuan if item.komoditas else "kg",
            int(item.harga),
            item.diinput_oleh.username if item.diinput_oleh else "-",
        ])

    return response


def api_harga_komoditas(request):
    selected_pasar_id = request.GET.get("pasar_id", "")
    selected_tanggal = request.GET.get("tanggal", "")

    qs = HargaKomoditas.objects.select_related("komoditas", "pasar").all()
    if selected_pasar_id:
        qs = qs.filter(pasar_id=selected_pasar_id)
    if selected_tanggal:
        qs = qs.filter(tanggal=selected_tanggal)

    data = []
    for item in qs.order_by("-tanggal", "komoditas__nama")[:100]:
        data.append({
            "id": item.id,
            "komoditas": item.komoditas.nama,
            "satuan": item.komoditas.satuan,
            "pasar": item.pasar.nama_pasar,
            "harga": int(item.harga),
            "tanggal": item.tanggal.strftime("%Y-%m-%d"),
        })

    return JsonResponse({"status": "success", "count": len(data), "data": data}, safe=False)
