from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('pdf-maker/', views.pdf_maker_tool, name='pdf-maker'),
    path('pdf-maker/process/', views.pdf_maker_process, name='pdf-maker-process'),
    path('merge/', views.merge_tool, name='merge'),
    path('split/', views.split_tool, name='split'),
    path('img-to-pdf/', views.img_to_pdf_tool, name='img-to-pdf'),
    path('word-to-pdf/', views.word_to_pdf_tool, name='word-to-pdf'),
    path('pdf-to-img/', views.pdf_to_img_tool, name='pdf-to-img'),
    path('pdf-to-word/', views.pdf_to_word_tool, name='pdf-to-word'),
    path('protect/', views.protect_tool, name='protect'),
]
