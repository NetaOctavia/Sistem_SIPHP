from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import BeritaForm
from .models import Berita


def berita(request):
    berita_list = Berita.objects.all().order_by("-created_at")
    return render(
        request, "dashboard/berita.html", {"berita_list": berita_list}
    )


@staff_member_required
def kelola_berita(request):
    if request.method == "POST":
        form = BeritaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Berita berhasil ditambahkan!")
        else:
            for err in form.errors.values():
                messages.error(request, err.as_text())
        return redirect("kelola_berita")

    berita_qs = Berita.objects.all().order_by("-created_at")
    paginator = Paginator(berita_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "auth_custom/kelola_berita.html",
        {
            "daftar_berita": page_obj,
            "berita_list": page_obj,
            "page_obj": page_obj,
        },
    )


@staff_member_required
def edit_berita(request, id):
    berita_obj = get_object_or_404(Berita, id=id)
    if request.method == "POST":
        form = BeritaForm(request.POST, request.FILES, instance=berita_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Berita berhasil diperbarui!")
        else:
            for err in form.errors.values():
                messages.error(request, err.as_text())
    return redirect("kelola_berita")


@staff_member_required
def hapus_berita(request, id):
    if request.method != "POST":
        return redirect("kelola_berita")
    berita_obj = get_object_or_404(Berita, id=id)
    berita_obj.delete()
    messages.success(request, "Berita berhasil dihapus!")
    return redirect("kelola_berita")


def api_daftar_berita(request):
    berita_qs = Berita.objects.all().order_by("-created_at")[:20]
    data = [
        {
            "id": b.id,
            "judul": b.judul,
            "ringkasan": b.ringkasan or "",
            "url_sumber": b.url_sumber,
            "gambar": b.display_gambar,
            "created_at": b.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for b in berita_qs
    ]
    return JsonResponse({"status": "success", "count": len(data), "data": data}, safe=False)
