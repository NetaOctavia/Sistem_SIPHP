from datetime import timedelta
import json
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg, Max, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import Pasar
from harga.models import HargaKomoditas
from .models import Komoditas

KATEGORI_EKSPOR = "Komoditi Ekspor"


def komoditas_ekspor(request):
    """Halaman publik daftar komoditi ekspor beserta harga terkininya."""
    latest_dates = (
        HargaKomoditas.objects.values("komoditas_id").annotate(max_date=Max("tanggal"))
    )
    latest_q = Q()
    for item in latest_dates:
        latest_q |= Q(komoditas_id=item["komoditas_id"], tanggal=item["max_date"])

    harga_map = {}
    if latest_q:
        harga_agg = (
            HargaKomoditas.objects.filter(latest_q)
            .values("komoditas_id")
            .annotate(avg_harga=Avg("harga"))
        )
        for row in harga_agg:
            harga_map[row["komoditas_id"]] = int(row["avg_harga"])

    daftar_ekspor = Komoditas.objects.filter(kategori=KATEGORI_EKSPOR).order_by("nama")
    daftar_komoditas_ekspor = [
        {
            "id": kom.id,
            "nama": kom.nama,
            "kategori": kom.kategori,
            "satuan": kom.satuan,
            "keterangan": kom.keterangan or "",
            "harga_terakhir": harga_map.get(kom.id),
        }
        for kom in daftar_ekspor
    ]

    context = {
        "daftar_komoditas_ekspor": daftar_komoditas_ekspor,
        "total_komoditas_ekspor": len(daftar_komoditas_ekspor),
    }
    return render(request, "dashboard/komoditas_ekspor.html", context)


def komoditas(request):
    daftar_komoditas_qs = Komoditas.objects.all().order_by("nama")
    daftar_pasar = Pasar.objects.all().order_by("nama_pasar")

    # Daftar Kategori dengan Icon & Label yang Rapi
    CATEGORY_ICONS = {
        "Beras & Padi": "🌾",
        "Cabai & Bumbu": "🌶️",
        "Peternakan & Daging": "🥩",
        "Perikanan": "🐟",
        "Sayuran": "🥬",
        "Minyak & Lemak": "🛢️",
        "Sembako & Olahan": "📦",
        "Kacang-kacangan": "🥜",
        "Umbi-umbian": "🥔",
        "Buah-buahan": "🍎",
        "Susu & Olahan": "🥛",
        "Palawija & Pakan": "🌽",
        "Komoditi Ekspor": "🚢",
    }

    # Ambil semua kategori yang ada di database
    kategori_db = list(
        Komoditas.objects.exclude(kategori__isnull=True)
        .exclude(kategori="")
        .values_list("kategori", flat=True)
        .distinct()
    )

    # Susun daftar tab kategori terurut
    kategori_priority = [
        "Beras & Padi", "Cabai & Bumbu", "Peternakan & Daging",
        "Perikanan", "Sayuran", "Minyak & Lemak", "Sembako & Olahan",
        "Kacang-kacangan", "Buah-buahan"
    ]
    daftar_tab_kategori = []
    for kat in kategori_priority:
        if kat in kategori_db:
            count = Komoditas.objects.filter(kategori=kat).count()
            daftar_tab_kategori.append({
                "key": kat,
                "label": kat,
                "icon": CATEGORY_ICONS.get(kat, "📦"),
                "count": count,
            })
    # Kategori lain yang belum masuk
    for kat in sorted(kategori_db):
        if kat not in kategori_priority:
            count = Komoditas.objects.filter(kategori=kat).count()
            daftar_tab_kategori.append({
                "key": kat,
                "label": kat,
                "icon": CATEGORY_ICONS.get(kat, "📦"),
                "count": count,
            })

    # Parameter URL
    selected_kategori = request.GET.get("kategori", "")
    if not selected_kategori and daftar_tab_kategori:
        selected_kategori = daftar_tab_kategori[0]["key"]  # Default ke 'Beras & Padi'

    selected_id = request.GET.get("komoditas_id", "")
    selected_pasar_id = request.GET.get("pasar_id", "")
    selected_periode = request.GET.get("periode", "7")

    today = timezone.now().date()
    
    # Menentukan rentang tanggal berdasarkan filter periode
    if selected_periode == "14":
        start_date = today - timedelta(days=13)
        periode_label = "14 Hari Terakhir"
    elif selected_periode == "30":
        start_date = today - timedelta(days=29)
        periode_label = "30 Hari Terakhir"
    elif selected_periode == "bulan_ini":
        start_date = today.replace(day=1)
        periode_label = f"Bulan Ini ({today.strftime('%B %Y')})"
    else:
        selected_periode = "7"
        start_date = today - timedelta(days=6)
        periode_label = "7 Hari Terakhir"

    delta_days = (today - start_date).days + 1
    dates_list = [(start_date + timedelta(days=i)) for i in range(delta_days)]
    dates_label = [d.strftime("%d %b") for d in dates_list]

    colors = [
        {"border": "#10B981", "bg": "rgba(16, 185, 129, 0.08)"},
        {"border": "#EF4444", "bg": "rgba(239, 68, 68, 0.08)"},
        {"border": "#3B82F6", "bg": "rgba(59, 130, 246, 0.08)"},
        {"border": "#F59E0B", "bg": "rgba(245, 158, 11, 0.08)"},
        {"border": "#8B5CF6", "bg": "rgba(139, 92, 246, 0.08)"},
        {"border": "#EC4899", "bg": "rgba(236, 72, 153, 0.08)"},
        {"border": "#14B8A6", "bg": "rgba(20, 184, 166, 0.08)"},
        {"border": "#6366F1", "bg": "rgba(99, 102, 241, 0.08)"},
    ]

    chart_datasets = []

    # 1. Logika Pembuatan Datasets Grafik Berdasarkan Kategori / Komoditas
    if selected_id:
        # Jika komoditas spesifik dipilih
        kom_terpilih = Komoditas.objects.filter(id=selected_id).first()
        if kom_terpilih:
            if selected_pasar_id:
                # 1 Komoditas di 1 Pasar spesifik
                pasar_obj = Pasar.objects.filter(id=selected_pasar_id).first()
                p_label = pasar_obj.nama_pasar if pasar_obj else "Pasar"
                h_qs = HargaKomoditas.objects.filter(
                    komoditas=kom_terpilih,
                    pasar_id=selected_pasar_id,
                    tanggal__range=(start_date, today)
                ).values("tanggal").annotate(avg_harga=Avg("harga"))
                h_map = {item["tanggal"]: int(item["avg_harga"]) for item in h_qs}
                
                chart_datasets.append({
                    "label": f"{kom_terpilih.nama} - {p_label}",
                    "data": [h_map.get(d, 0) for d in dates_list],
                    "borderColor": colors[0]["border"],
                    "backgroundColor": colors[0]["bg"],
                    "fill": True,
                    "tension": 0.35,
                    "pointRadius": 4,
                    "pointHoverRadius": 6,
                })
            else:
                # 1 Komoditas dibandingkan antar semua pasar
                for idx, p in enumerate(daftar_pasar):
                    h_qs = HargaKomoditas.objects.filter(
                        komoditas=kom_terpilih,
                        pasar=p,
                        tanggal__range=(start_date, today)
                    ).values("tanggal").annotate(avg_harga=Avg("harga"))
                    h_map = {item["tanggal"]: int(item["avg_harga"]) for item in h_qs}
                    series = [h_map.get(d, 0) for d in dates_list]
                    
                    col = colors[idx % len(colors)]
                    chart_datasets.append({
                        "label": f"{p.nama_pasar}",
                        "data": series,
                        "borderColor": col["border"],
                        "backgroundColor": col["bg"],
                        "fill": False,
                        "tension": 0.35,
                        "pointRadius": 4,
                        "pointHoverRadius": 6,
                    })
    else:
        # Menampilkan komoditas yang ada di dalam kategori terpilih (3 - 8 komoditas sekelompok)
        komoditas_plot = Komoditas.objects.filter(kategori=selected_kategori).order_by("nama")
        if not komoditas_plot.exists():
            komoditas_plot = daftar_komoditas_qs[:6]

        chart_qs = HargaKomoditas.objects.filter(
            komoditas__in=komoditas_plot,
            tanggal__range=(start_date, today)
        )
        if selected_pasar_id:
            chart_qs = chart_qs.filter(pasar_id=selected_pasar_id)
            
        chart_agg = chart_qs.values(
            "komoditas_id", "tanggal"
        ).annotate(avg_harga=Avg("harga"))
        
        chart_map = {
            (item["komoditas_id"], item["tanggal"]): int(item["avg_harga"])
            for item in chart_agg
        }

        for idx, kom in enumerate(komoditas_plot):
            series = [chart_map.get((kom.id, d), 0) for d in dates_list]
            col = colors[idx % len(colors)]
            chart_datasets.append({
                "label": kom.nama,
                "data": series,
                "borderColor": col["border"],
                "backgroundColor": col["bg"],
                "fill": False,
                "tension": 0.35,
                "pointRadius": 4,
                "pointHoverRadius": 6,
            })

    # Filter komoditas dropdown sesuai kategori aktif
    komoditas_dropdown = Komoditas.objects.filter(kategori=selected_kategori).order_by("nama")
    if not komoditas_dropdown.exists():
        komoditas_dropdown = daftar_komoditas_qs

    # Filter komoditas untuk tabel tabulasi
    komoditas_table_qs = daftar_komoditas_qs
    if selected_kategori:
        komoditas_table_qs = komoditas_table_qs.filter(kategori=selected_kategori)
    if selected_id:
        komoditas_table_qs = komoditas_table_qs.filter(id=selected_id)

    # 2. Batch fetch harga terakhir per komoditas untuk tabel
    latest_dates_qs = HargaKomoditas.objects.all()
    if selected_pasar_id:
        latest_dates_qs = latest_dates_qs.filter(pasar_id=selected_pasar_id)
    latest_dates = latest_dates_qs.values("komoditas_id").annotate(max_date=Max("tanggal"))
    latest_date_map = {item["komoditas_id"]: item["max_date"] for item in latest_dates}

    latest_q = Q()
    for kom_id, max_d in latest_date_map.items():
        if max_d:
            latest_q |= Q(komoditas_id=kom_id, tanggal=max_d)

    latest_prices_map = {}
    if latest_q:
        lp_qs = HargaKomoditas.objects.filter(latest_q)
        if selected_pasar_id:
            lp_qs = lp_qs.filter(pasar_id=selected_pasar_id)
        lp_agg = lp_qs.values("komoditas_id").annotate(avg_harga=Avg("harga"))
        for item in lp_agg:
            latest_prices_map[item["komoditas_id"]] = int(item["avg_harga"])

    daftar_komoditas_dengan_harga = []
    for kom in komoditas_table_qs:
        harga_terakhir_val = latest_prices_map.get(kom.id, 0)
        daftar_komoditas_dengan_harga.append({
            "id": kom.id,
            "nama": kom.nama,
            "kategori": kom.kategori or "",
            "satuan": kom.satuan,
            "harga_terakhir": f"{harga_terakhir_val:,}".replace(",", "."),
        })

    # Pagination: 10 items/page jika komoditas lebih dari 10
    paginator = Paginator(daftar_komoditas_dengan_harga, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "daftar_tab_kategori": daftar_tab_kategori,
        "selected_kategori": selected_kategori,
        "daftar_komoditas_dropdown": komoditas_dropdown,
        "daftar_komoditas": page_obj,
        "page_obj": page_obj,
        "daftar_pasar": daftar_pasar,
        "selected_id": selected_id,
        "selected_pasar_id": selected_pasar_id,
        "selected_periode": selected_periode,
        "periode_label": periode_label,
        "chart_labels": json.dumps(dates_label, cls=DjangoJSONEncoder),
        "chart_datasets": json.dumps(chart_datasets, cls=DjangoJSONEncoder),
    }
    return render(request, "dashboard/komoditas.html", context)


@staff_member_required(login_url='login')
def edit_komoditas(request, id):
    kom = get_object_or_404(Komoditas, id=id)

    if request.method == "POST":
        nama = request.POST.get("nama")
        satuan = request.POST.get("satuan")
        kategori = (request.POST.get("kategori") or "").strip()
        harga_input = request.POST.get("harga")
        pasar_id = request.POST.get("pasar_id")

        if nama and satuan:
            kom.nama = nama.strip()
            kom.satuan = satuan.strip()
            kom.kategori = kategori or None
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


@staff_member_required(login_url='login')
def hapus_komoditas(request, id):
    if request.method != "POST":
        return redirect("harga_komoditas")
    kom = get_object_or_404(Komoditas, id=id)
    kom.delete()
    messages.success(request, f'Komoditas "{kom.nama}" berhasil dihapus.')
    return redirect("harga_komoditas")


def api_daftar_komoditas(request):
    komoditas_qs = Komoditas.objects.all().order_by("nama")
    data = [
        {
            "id": k.id,
            "nama": k.nama,
            "kategori": k.kategori or "",
            "satuan": k.satuan,
            "keterangan": k.keterangan or "",
        }
        for k in komoditas_qs
    ]
    return JsonResponse({"status": "success", "count": len(data), "data": data}, safe=False)
