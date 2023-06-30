import json
import os
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage, default_storage
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils import timezone

from ai.views import diary_views

# from ai.views.diary_views import create_diary
from pet.models import Personality, Pet

from ..forms import DiaryForm
from ..models import Diary, Keyword


@login_required(login_url="account:login")
def diary_create_before(request):
    if request.method == "POST":
        form = DiaryForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            # <- 보낼거 함수에 ->
            diary = form.save(commit=False)
            user_id = request.user.id
            pet_id = form.cleaned_data["pet"].id
            pet = Pet.objects.get(id=pet_id)
            personality = Personality.objects.get(pet=pet)
            content_list = request.POST.getlist("content[]")
            diary.registered_time = timezone.now()
            diary.updated_time = timezone.now()
            diary.user_id = user_id
            diary.save()

            input = {
                "pet": pet,
                "personality": personality,
                "add_content": content_list,
                "video": "static/" + diary.video.url,
            }

            result = diary_views.create_diary(input)
            # result = "일기 내용 일기 내용 일기 내용 일기 내용 "

            # content = create_diary(context)
            content_list = request.POST.getlist("content[]")
            context = {
                "form": form,
                "content": result,
                "title": content_list[0],
                "video": diary.video.url,
                "keywords": ["즐거움", "행복", "산책"],  # 생성된 keyword
            }

            return render(request, "diary/diary_result_form.html", context)
    else:
        form = DiaryForm(request.user)
    context = {"form": form}
    return render(request, "diary/diary_form.html", context)


@login_required(login_url="account:login")
def diary_create(request):
    if request.method == "POST":
        form = DiaryForm(request.user, request.POST, request.FILES)
        if form.is_valid():
            diary = form.save(commit=False)
            diary.user = request.user
            diary.registered_time = timezone.now()
            diary.updated_time = timezone.now()
            diary.content = request.POST.get("content")
            diary.title = request.POST.get("title")
            diary.video = request.POST.get("video").replace("media/", "")
            print("check", diary.video)

            checked_list_str = request.POST["keyword_list"]
            checked_list = json.loads(checked_list_str)
            keywords_list = []

            for keyword in checked_list:
                if keyword:
                    keyword_obj, created = Keyword.objects.get_or_create(word=keyword)
                    keywords_list.append(keyword_obj)

            diary.save()
            diary.keywords.set(keywords_list)

            return redirect("diary:index")
    else:
        form = DiaryForm(request.user)
    context = {"form": form}
    return render(request, "diary/diary_result_form.html", context)


@login_required(login_url="account:login")
def diary_modify(request, diary_id):
    diary = get_object_or_404(Diary, pk=diary_id)
    if request.user != diary.user:
        messages.error(request, "수정권한이 없습니다")
        return redirect("diary:detail", diary_id=diary.id)
    if request.method == "POST":
        form = DiaryForm(request.user, request.POST, request.FILES, instance=diary)
        if form.is_valid():
            diary = form.save(commit=False)
            diary.updated_time = timezone.now()  # 수정일시 저장
            added_list_str = request.POST["keyword_list"]
            added_list = json.loads(added_list_str)
            keywords_list = []

            for keyword in added_list:
                if keyword:
                    keyword_obj, created = Keyword.objects.get_or_create(word=keyword)
                    keywords_list.append(keyword_obj)
                    diary.keywords.add(keyword_obj)

            diary.save()

            return redirect("diary:detail", diary_id=diary.id)
    else:
        form = DiaryForm(user=request.user, instance=diary)
    context = {"form": form, "diary": diary}
    return render(request, "diary/diary_modify.html", context)


@login_required(login_url="account:login")
def diary_delete(request, diary_id):
    diary = get_object_or_404(Diary, pk=diary_id)
    if request.user != diary.user:
        messages.error(request, "삭제권한이 없습니다")
        return redirect("diary:detail", diary_id=diary.id)
    diary.delete()
    return redirect("diary:index")


@login_required(login_url="account:login")
def diary_bookmark(request, diary_id):
    diary = get_object_or_404(Diary, pk=diary_id)
    if request.user == diary.user:
        diary.bookmark = not diary.bookmark
        diary.save()
    query_params = {}
    page = request.POST.get("page")
    keyword = request.POST.get("keyword")
    pet_id = request.POST.get("pet_id")

    if page:
        query_params["page"] = page
    if keyword:
        query_params["keyword"] = keyword
    if pet_id:
        query_params["pet_id"] = pet_id

    query_string = urlencode(query_params)

    return HttpResponseRedirect(
        f"{resolve_url('diary:index_list')}?{query_string}#diary_{diary.id}"
    )
