from django import forms

class TokenForm(forms.Form):
    token = forms.CharField(
      label=False,
      max_length=200,
      widget=forms.TextInput(
        attrs={
          'class': 'border-2 hover:bg-gradient-to-br focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800 font-medium rounded-lg text-sm px-5 py-2.5 text-center mr-2 mb-2 ease-in duration-100',
          'placeholder': 'One time use token'
        }
      )
  )