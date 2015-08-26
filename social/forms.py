from django import forms

class PostForm(forms.Form):
	postName = forms.CharField(max_length = 100, widget = forms.TextInput(attrs={'class':'form-control','required':True}))
	imageUrl = forms.CharField(max_length = 255, required = False, widget = forms.TextInput(attrs={'class':'form-control'}))
	postCaption = forms.CharField(max_length = 255, widget = forms.TextInput(attrs={'class':'form-control','required':True}))
	postSource = forms.MultipleChoiceField(choices = (('fb','Facebook'),('li','LinkedIn')), widget = forms.CheckboxSelectMultiple(attrs={'class':'form-control'}))