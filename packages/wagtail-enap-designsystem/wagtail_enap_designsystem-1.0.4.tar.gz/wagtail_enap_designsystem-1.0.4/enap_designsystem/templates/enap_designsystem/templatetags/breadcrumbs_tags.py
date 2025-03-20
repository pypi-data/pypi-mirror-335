# enap_designsystem/templatetags/breadcrumbs_tags.py
from django import template
from wagtail.models import Page

register = template.Library()

@register.inclusion_tag('components/breadcrumbs.html', takes_context=True)
def breadcrumbs(context, theme='light'):
    """
    Renderiza as breadcrumbs para a página atual.
    
    Args:
        context: Contexto do template
        theme: 'light' ou 'dark' para controlar o esquema de cores
    """
    page = context.get('page')
    if not page:
        return {'breadcrumbs': [], 'theme': theme}
    
    breadcrumbs = []
    # Adiciona a página inicial
    home_page = Page.objects.filter(depth=2).first()
    
    if home_page:
        breadcrumbs.append({
            'title': 'Home',  # Usando "Home" em vez do título, já que usaremos o ícone
            'url': home_page.url,
            'is_home': True
        })
    
    # Adiciona as páginas ancestrais
    for ancestor in page.get_ancestors()[1:]:  # Ignora a raiz do site
        breadcrumbs.append({
            'title': ancestor.specific.title,
            'url': ancestor.specific.url,
            'is_home': False
        })
    
    # Adiciona a página atual
    breadcrumbs.append({
        'title': page.title,
        'url': None,  # Sem URL para a página atual
        'is_current': True
    })
    
    return {'breadcrumbs': breadcrumbs, 'theme': theme}