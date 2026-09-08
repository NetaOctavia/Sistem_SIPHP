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


def komoditas(request):
    daftar_komoditas_qs = Komoditas.objects.all().order_by("nama")
    daftar_pasar = Pasar.objects.all().order_by("nama_pasar")

    selected_id = request.GET.get("komoditas_id", "")
    selected_pasar_id = request.GET.get("pasar_id", "")

    today = timezone.now().date()
    start_date = today - timedelta(days=6)
    dates_list = [(start_date + timedelta(days=i)) for i in range(7)]
    dates_label = [d.strftime("%d %b") for d in dates_list]

    komoditas_filtered = daftar_komoditas_qs
    if selected_id:
        komoditas_filtered = komoditas_filtered.filter(id=selected_id)

    colors = [
        {"border": "#10B981", "bg": "rgba(16, 185, 129, 0.1)"},
        {"border": "#EF4444", "bg": "rgba(239, 68, 68, 0.1)"},
        {"border": "#3B82F6", "bg": "rgba(59, 130, 246, 0.1)"},
        {"border": "#F59E0B", "bg": "rgba(245, 158, 11, 0.1)"},
        {"border": "#8B5CF6", "bg": "rgba(139, 92, 246, 0.1)"},
    ]

    chart_datasets = []
    daftar_komoditas_dengan_harga = []

    # Batch fetch harga 7 hari terakhir (1 query)
    chart_qs = HargaKomoditas.objects.filter(
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

    # Batch fetch harga terakhir per komoditas (2 query total)
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

    for idx, kom in enumerate(komoditas_filtered):
        data_harga_per_hari = [
            chart_map.get((kom.id, d), 0) for d in dates_list
        ]
        harga_terakhir_val = latest_prices_map.get(kom.id, 0)

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

    # Pagination: 10 items/page jika memilih Semua Komoditas
    page_obj = None
    if not selected_id:
        paginator = Paginator(daftar_komoditas_dengan_harga, 10)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        table_komoditas = page_obj
    else:
        table_komoditas = daftar_komoditas_dengan_harga

    context = {
        "daftar_komoditas_dropdown": daftar_komoditas_qs,
        "daftar_komoditas": table_komoditas,
        "page_obj": page_obj,
        "daftar_pasar": daftar_pasar,
        "selected_id": selected_id,
        "selected_pasar_id": selected_pasar_id,
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
            "satuan": k.satuan,
            "keterangan": k.keterangan or "",
        }
        for k in komoditas_qs
    ]
    return JsonResponse({"status": "success", "count": len(data), "data": data}, safe=False)
