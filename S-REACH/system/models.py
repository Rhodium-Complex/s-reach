from django.db import models, connection
from django.db.models import Lookup, Func
from django import forms
from rdkit import Chem


###################################################
#PostgreSQL(データベース)への検索処理を拡張実装している
#https://github.com/rdkit/django-rdkit からパクった
#ここは黒魔術パート(なんで動くか良くわかってない)
#改変してもサポートできません
###################################################

class MolField(models.Field):
    
    description = ("Molecule")

    def db_type(self, connection):
        return 'mol'

    def get_placeholder(self, value, compiler, connection):
        if hasattr(value, 'as_sql'):
            return '%s'
        else:
            return 'mol_from_pkl(%s)'

    def select_format(self, compiler, sql, params):
        return 'mol_to_pkl(%s)' % sql, params

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return Chem.Mol(bytes(value))

    def to_python(self, value):
        if value is None or isinstance(value, Chem.Mol):
            return value
        if isinstance(value, str):
            return self.text_to_mol(value)
        elif isinstance(value, (bytes, bytearray, memoryview)):
            return Chem.Mol(bytes(value))
        else:
            raise ValidationError("Invalid input for a Mol instance")

    def get_prep_value(self, value):
        # convert the Molecule instance to the value used by the db driver
        if isinstance(value, str):
            value = self.text_to_mol(value)
        if isinstance(value, Chem.Mol):
            value = memoryview(value.ToBinary())
        if value is None:
            return value
        return Func(value, function='mol_from_pkl')

    @staticmethod
    def text_to_mol(value):
        value = str(value)
        mol = (Chem.MolFromSmiles(value)
            or Chem.MolFromMolBlock(value)
            or Chem.inchi.MolFromInchi(value))
        if mol is None:
            raise ValidationError("Invalid input for a Mol instance")
        return value

    def get_prep_lookup(self, lookup_type, value):
        "Perform preliminary non-db specific lookup checks and conversions"
        supported_lookup_types = (
            ['hassubstruct', 'issubstruct', 'exact', 'isnull',] +
            [T.lookup_name for T in MOL_DESCRIPTOR_TRANFORMS]
        )
        if lookup_type in supported_lookup_types:
            return value
        raise TypeError("Field has invalid lookup: %s" % lookup_type)

    def formfield(self, **kwargs):
        ## Use TextField as default input form to accommodate line breaks needed for molBlocks
        defaults = {'form_class': forms.CharField, 'strip': False, 'widget':forms.Textarea}
        defaults.update(kwargs)
        return None
        super().formfield(**defaults)

class HasSubstruct(Lookup):
    lookup_name = 'hassubstruct'
    prepare_rhs = False

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return "%s @> %s ::qmol" % (lhs, rhs), params

        return "%s @>mol_adjust_query_properties(%s, '{\"makeDummiesQueries \":false;\"adjustDegree\":false;}')" % (lhs, rhs), params

class NotEqual(Lookup):
    lookup_name = 'ne'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s <> %s ::qmol' % (lhs, rhs), params

class IsEqual(Lookup):
    lookup_name = 'isequal'
    prepare_rhs = False

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s @= %s' % (lhs, rhs), params

MolField.register_lookup(HasSubstruct)
MolField.register_lookup(NotEqual)
MolField.register_lookup(IsEqual)

###################################################
#黒魔術ここまで
###################################################

###################################################
#続いてデータベースの構造(列の名前とか)について
# <列の名前> = models.<データ型>(
#     <オプション>(下記参照)
# )
#データ型は
#   1行程度の文字列：CharField
#   複数行の文字列： TextField
#   数値：          FloatField
#   ファイル：       FileField
#から選択すればいいと思います。
#
#変更した場合、
#       manage.py makemigrations
#       manage.py migrate
#を実行してください。
#※列を削除した場合、列の名前を変更した場合はデータが消失します
###################################################

class Inventry(models.Model):
    smiles     = models.CharField( verbose_name='SMILES*', max_length=1000,)
    expdata    = models.TextField( verbose_name='コード*', max_length=1000,)

    #以下は任意で入力可能な項目
    name       = models.CharField( null=True, blank=True, verbose_name='製品名', max_length=1000)
    seller     = models.CharField( null=True, blank=True, verbose_name='卸業者', max_length=1000)
    properties = models.TextField( null=True, blank=True, verbose_name='性状',   max_length=1000)
    comments   = models.TextField( null=True, blank=True, verbose_name='その他', max_length=1000)
    HNMR       = models.FileField( null=True, blank=True, verbose_name='1H NMR', upload_to='',)
    CNMR       = models.FileField( null=True, blank=True, verbose_name='13C NMR',upload_to='',)
    IR         = models.FileField( null=True, blank=True, verbose_name='IR',     upload_to='',)
    UV_vis     = models.FileField( null=True, blank=True, verbose_name='UV_vis', upload_to='',)
    XRD        = models.FileField( null=True, blank=True, verbose_name='XRD',    upload_to='',)
    mol        = MolField(         null=True, blank=True,                        db_index=True)#分子構造を保持するための特別な列、上の方で定義している
    mw         = models.FloatField(null=True, blank=True,                        db_index=True)#分子量を保持する
    
    def save(self, *args, **kwargs):
        super(Inventry, self).save(*args, **kwargs)
        with connection.cursor() as cursor:

            #mol列(分子構造を持つ列)が空のときに、分子構造を注入する。
            #構造はSMILES列から取得する。
            cursor.execute("UPDATE system_inventry SET mol=mol_from_smiles(smiles::cstring) where mol is null")

            #分子量を計算し、検索を高速化するおまじないをかける。
            cursor.execute("UPDATE system_inventry SET mw=mol_amw(mol) where mw is null")
            #cursor.execute("create index on library_inventry using gist(mol);")

class Bottle(models.Model):
    compound = models.ForeignKey(  Inventry ,verbose_name='comBB',    on_delete=models.PROTECT,)
    lot_No   = models.CharField(             verbose_name='Lot No.',  max_length=1000, null=True, blank=True,  )
    ordered  = models.BooleanField(          verbose_name='注文済み', default=False,)
    delivered= models.BooleanField(          verbose_name='納品済み', default=False,)


