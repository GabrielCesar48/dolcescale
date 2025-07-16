# forms.py
from django import forms
from django.core.validators import RegexValidator
from .models import Codigo


class CodigoForm(forms.Form):
    """
    Formulário para envio de códigos.
    O campo aceita entrada com ou sem espaços, mas valida apenas o código limpo.
    """
    codigo = forms.CharField(
        max_length=14,  # 12 caracteres + 2 espaços
        min_length=12,
        widget=forms.TextInput(attrs={
            'class': 'form-control codigo-input',
            'placeholder': 'XXXX XXXX XXXX',
            'autocomplete': 'off',
            'data-mask': 'codigo',
            'style': 'text-transform: uppercase; letter-spacing: 2px; font-size: 1.2rem; text-align: center;'
        }),
        label='Código',
        help_text='Digite o código de 12 caracteres'
    )
    
    def clean_codigo(self):
        """
        Limpa e valida o código.
        Remove espaços e converte para maiúsculas.
        """
        codigo = self.cleaned_data['codigo']
        # Remove espaços e converte para maiúsculas
        codigo_limpo = codigo.replace(' ', '').upper()
        
        # Validar formato do código
        if len(codigo_limpo) != 12:
            raise forms.ValidationError(
                'O código deve conter exatamente 12 caracteres.'
            )
        
        # Validar se contém apenas letras e números
        if not codigo_limpo.isalnum():
            raise forms.ValidationError(
                'O código deve conter apenas letras e números.'
            )
        
        return codigo_limpo


class ResgatePontosForm(forms.Form):
    """
    Formulário para resgate de pontos de um usuário.
    """
    pontos = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Quantidade de pontos'
        }),
        label='Pontos a resgatar'
    )
    
    descricao = forms.CharField(
        max_length=200,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Descrição do resgate (ex: Troca por prêmio X)'
        }),
        label='Descrição'
    )
    
    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        if self.usuario:
            saldo = self.usuario.saldo_pontos
            self.fields['pontos'].max_value = saldo
            self.fields['pontos'].help_text = f'Saldo disponível: {saldo} pontos'
            
    def clean_pontos(self):
        """
        Valida se o usuário tem pontos suficientes.
        """
        pontos = self.cleaned_data['pontos']
        
        if self.usuario:
            saldo = self.usuario.saldo_pontos
            if pontos > saldo:
                raise forms.ValidationError(
                    f'O usuário possui apenas {saldo} pontos disponíveis.'
                )
        
        return pontos