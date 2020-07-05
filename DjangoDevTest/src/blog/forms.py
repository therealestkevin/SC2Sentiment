from django import forms

from .models import Article

class ArticleForm(forms.ModelForm):
	title = forms.CharField(label='', widget=forms.TextInput(attrs={"placeholder":"your title"}))

	content = forms.CharField(
		required=True, 
		widget=forms.Textarea(
			attrs={
					"placeholder":"your content",
					"class": "new-class-name two",
					"id": "my-id-for-textarea",
					"rows": 20,
					"cols": 100
				}
			)

		)
	class Meta:
		model = Article
		fields = [
		'title',
		'content']
