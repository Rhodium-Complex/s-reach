from django.db.models.expressions import F
from django.db.models import Q, Count
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from .form import dossier_create, dossier_update, search_form, order
from .models import Bottle, Inventry
import re

class searchClass(TemplateView):
    template_name = 'search.html'

class createClass(CreateView):
    template_name = 'create.html'
    model         = Inventry
    form_class    = dossier_create
    success_url   = "/search/"

class updateClass(UpdateView):
    template_name = 'update.html'
    model         = Inventry
    form_class    = dossier_update
    success_url   = "/result/"


class sellerOrderClass(ListView):
    template_name = 'sellerOrder.html'
    model         = Bottle
    def get_queryset(self):
        rst = Bottle.objects.all().select_related().filter(ordered=False).values('compound_id','compound__smiles').annotate(total=Count('ordered'))
        print(rst.query)
        return rst

class sellerOrderedClass(ListView):
    template_name = 'sellerOrder.html'
    model         = Bottle
    def get_queryset(self):
        rst = Bottle.objects.all().select_related().filter(ordered=True).filter(delivered=False).values('compound_id','compound__smiles').annotate(total=Count('ordered'))
        print(rst.query)
        return rst

class orderClass(CreateView):
    template_name = 'order.html'
    model         = Bottle
    form_class    = order 
    success_url   = "/result/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["Inventry"] = Inventry.objects.filter(id = self.kwargs.get('pk'))[0]
        context["id"] = self.kwargs.get('pk')
        print(context["Inventry"])
        return context
    
    def form_valid(self, form):
        for _ in range(form.cleaned_data['counter']-1):
            Bottle.objects.create(
                compound = form.cleaned_data['compound']
            )
        return super().form_valid(form)

class resultClass(ListView):
    template_name = 'result.html'
    model = search_form   
    def post(self, request, *args, **kwargs):
        for i in ['smiles','name', 'expdata', ]:
            request.session[i] = self.request.POST.get(i)
        return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        default_data = {}
        for i in ['smiles','name', 'expdata', ]:
            default_data[i] = self.request.session[i] if i in self.request.session else "" 

        context['test_form'] = search_form(initial=default_data) # 検索フォーム

        return context

    def get_queryset(self):
        if 'smiles' not in self.request.session: return Inventry.objects.none()
        if 'name'   not in self.request.session: return Inventry.objects.none()
        if 'expdata'not in self.request.session: return Inventry.objects.none()
        smarts = self.request.session['smiles']
        name   = self.request.session['name']
        expdata= self.request.session['expdata']


        rst = Inventry.objects
        if len(smarts) > 0: rst = rst.filter(Qstack(smarts))
        if len(name)   > 0: rst = rst.filter(name__icontains = name)
        if len(expdata)> 0: rst = rst.filter(expdata__icontains = expdata)
        return rst.order_by('mw')

def aroma_searchable(fragments):
    if len(fragments)==1:
        yield fragments[0]
    else:
        tmp = fragments.copy()
        tmp[-2] = tmp[-2]+"="+tmp[-1]
        tmp.pop()
        yield from aroma_searchable(tmp)
        
        tmp = fragments.copy()
        tmp[-2] = tmp[-2]+":"+tmp[-1]
        tmp.pop()
        yield from aroma_searchable(tmp)

def Qstack(smarts):
    # 検索時にSiとするとSMILESが[SiH4]となり
    # シラン化合物が検索できないことの対応策
    smarts = re.sub('H\d*]',']', smarts)
    # 非芳香族で検索した際に、二重結合部位がベンゾ環の場合
    # 検索結果に出ないことの対応策。
    # SMARTS表記([#6]など)にすることで解決を図る。
    smarts = re.sub( r'\[#6\]([a-z])',r'C\1',smarts.replace('C','[#6]'))
    smarts = re.sub( r'\[#7\]([a-z])',r'N\1',smarts.replace('N','[#7]'))
    smarts = re.sub( r'\[#8\]([a-z])',r'O\1',smarts.replace('O','[#8]'))
    smarts = re.sub(r'\[#15\]([a-z])',r'P\1',smarts.replace('P','[#15]'))
    smarts = re.sub(r'\[#16\]([a-z])',r'S\1',smarts.replace('S','[#16]'))

    # 2重結合、1.5結合のSMARTSを強制的にリストアップする。
    # その結果をOR検索で順次結合している。
    smartsSPL = smarts.split("=")
    rst = Q(mol__hassubstruct = smarts)
    for i in aroma_searchable(smartsSPL):
        rst = rst|Q(mol__hassubstruct = i)
    return rst


    