from django import forms
from django.db.models import fields
from django.forms import ModelForm
from .models import Bottle, Inventry

class dossier_update(ModelForm):
    class Meta:
        model = Inventry
        fields = ['name', 'smiles', 'expdata', 'properties', 'HNMR', 'CNMR', 'IR', 'UV_vis','comments']
    
    seller = forms.fields.ChoiceField(
        choices = (
            ('ja', '日本'),
            ('us', 'アメリカ'),
            ('uk', 'イギリス'),
            ('ch', '中国'),
            ('kr', '韓国')
        ),
        widget=forms.widgets.Select
    )
    def __init__(self, *args, **kwargs):
        super(dossier_update, self).__init__(*args, **kwargs)
        self.fields['expdata'].widget.attrs.update({
            'placeholder': '実験番号なら000000 田中。Wako：000-00000。',
            'rows': '3'
        })
        self.fields['properties'].widget.attrs.update({
            'placeholder': '「白色粉体」「淡黄色液体」など',
            'rows': '3'
        })
        self.fields['comments'].widget.attrs.update({
            'placeholder': '「白色粉体」「淡黄色液体」など',
            'rows': '3'
        })

class dossier_create(dossier_update):
    class Meta:
        #moldel.pyで設定したcompoundsクラスと連携させる項目の指定
        model = Inventry
        fields = ['name', 'smiles', 'seller', 'expdata', 'properties', 'HNMR', 'CNMR', 'IR', 'UV_vis','comments']
    
    #特殊な入力項目の設定
    #今回は重複時の強制登録チェックボックスを作成
    duplicate_allow = forms.BooleanField(
        label='化合物が重複することを許可する。',
        required = False,
        widget=forms.CheckboxInput(
            attrs={'class': 'check'}
        ), 
    )
    #表示する項目の指定
    fields = ['name', 'smiles', 'expdata','seller', 'properties',  'HNMR', 'CNMR', 'IR', 'UV_vis','comments','duplicate_allow']

    def clean(self):
        #入力データのバリデーション
        cleaned_data = super().clean()
        if cleaned_data.get('smiles') is not None:
            result = Inventry.objects.filter(mol__isequal=cleaned_data.get('smiles'))
        else:
            result = Inventry.objects.none()

        if len(result) and not cleaned_data.get('duplicate_allow'):
            self.add_error('duplicate_allow', '同じ分子が登録されています。\n登録を継続する場合は「化合物が重複することを許可する」にチェックを入れてください。')
            self.result_smiles = result  
        return cleaned_data

class order(ModelForm):
    class Meta:
        model = Bottle
        fields = ["compound"]
    
    counter = forms.IntegerField(
        label='発注数',
        initial =1,
    )

class search_form(ModelForm):
    class Meta:
        model = Inventry
        fields = ['smiles', 'name', 'expdata',]
