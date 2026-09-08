from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PesanKontakForm
from .models import PesanKontak


def kontak(request):
    if request.method == "POST":
        form = PesanKontakForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Pesan Anda berhasil dikirim! Terima kasih atas masukannya."
            )
            return redirect("kontak")
        else:
            for err in form.errors.values():
                messages.error(request, err.as_text())

    return render(request, "dashboard/kontak.html")


def profil(request):
    return render(request, "dashboard/profil.html")


def layanan_teknis(request):
    return render(request, "dashboard/layanan_teknis.html")


@staff_member_required
def kelola_kontak(request):
    pesan_qs = PesanKontak.objects.all().order_by("-created_at")
    paginator = Paginator(pesan_qs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "auth_custom/kelola_kontak.html",
        {
            "pesan_list": page_obj,
            "page_obj": page_obj,
        },
    )


@staff_member_required
def hapus_kontak(request, id):
    if request.method != "POST":
        return redirect("kelola_kontak")
    pesan_obj = get_object_or_404(PesanKontak, id=id)
    pesan_obj.delete()
    messages.success(request, "Pesan kontak berhasil dihapus!")
    return redirect("kelola_kontak")
