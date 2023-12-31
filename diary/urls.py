from django.urls import path

from .views import ajax_views, base_views, diary_views

app_name = "diary"

urlpatterns = [
    path("", base_views.index, name="index"),
    path("list/", base_views.index_list, name="index_list"),
    path("<int:diary_id>/", base_views.detail, name="detail"),
    path("get_diarys/", ajax_views.get_diarys, name="get_diarys"),
    path(
        "get_diary_info/<int:diary_id>/",
        ajax_views.get_diary_info,
        name="get_diary_info",
    ),
    path("create/", diary_views.diary_create_before, name="diary_create_before"),
    path("create/result/", diary_views.diary_create, name="diary_create"),
    path("modify/<int:diary_id>/", diary_views.diary_modify, name="diary_modify"),
    path("delete/<int:diary_id>/", diary_views.diary_delete, name="diary_delete"),
    path("bookmark/", diary_views.diary_bookmark, name="diary_bookmark_base"),
    path("bookmark/<int:diary_id>/", diary_views.diary_bookmark, name="diary_bookmark"),
]
