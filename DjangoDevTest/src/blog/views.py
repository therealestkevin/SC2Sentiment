from django.shortcuts import render, get_object_or_404
from .forms import ArticleForm
from .models import Article
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    ListView,
    DeleteView
)


# Create your views here.

'''
def article_create_view(request):
	form = ArticleForm(request.POST or None)

	if form.is_valid():
		form.save()
		form = ArticleForm()

	context = {
		'form' : form
	}

	return render(request, "articles/article_create.html", context)

def article_list_view(request):
	queryset = Article.objects.all()
	context = {
		"object_list": queryset
	}

	return render(request, "articles/article_list.html", context)

def article_detailed_view(request, id):
	obj = get_object_or_404(Article, id=id)

	context = {
		'object': obj
	}

	return render(request, "articles/article_detail.html", context)
'''

class ArticleListView(ListView):
	template_name = 'articles/article_list.html'
	queryset = Article.objects.all()

class ArticleDetailView(DetailView):
	template_name = 'articles/article_detail.html'

	def get_object(self):
		id_= self.kwargs.get("id")
		return get_object_or_404(Article, id=id_)

class ArticleCreateView(CreateView):
	template_name = 'articles/article_create.html'
	form_class = ArticleForm
	queryset = Article.objects.all()



	def form_valid(self, form):
		print(form.cleaned_data)
		return super().form_valid(form)

class ArticleUpdateView(UpdateView):
	template_name = 'articles/article_create.html'
	form_class = ArticleForm
	queryset = Article.objects.all()

	def get_object(self):
		id_= self.kwargs.get("id")
		return get_object_or_404(Article, id=id_)

	def form_valid(self, form):
		print(form.cleaned_data)
		return super().form_valid(form)

class ArticleDeleteView(DeleteView):
	template_name = 'articles/article_delete.html'

	def get_object(self):
		id_= self.kwargs.get("id")
		return get_object_or_404(Article, id=id_)

	def get_success_url(self):
		return reverse('articles:article-list')