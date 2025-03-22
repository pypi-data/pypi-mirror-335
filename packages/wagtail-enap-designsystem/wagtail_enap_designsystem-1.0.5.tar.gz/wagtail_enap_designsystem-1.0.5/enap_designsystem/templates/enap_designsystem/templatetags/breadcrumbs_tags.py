# enap_designsystem/templatetags/breadcrumbs_tags.py
from django import template
from wagtail.models import Page

register = template.Library()

@register.inclusion_tag('enap_designsystem/blocks/draft_breadcrumbs.html', takes_context=True)
def breadcrumbs(context, theme='light'):
    """
    Renderiza as breadcrumbs para a página atual.
    """
    page = context.get('page')
    if not page:
        return {'breadcrumbs': [], 'theme': theme}
    
    breadcrumbs = []
    # Adiciona a página inicial
    home_page = Page.objects.filter(depth=2).first()
    
    if home_page:
        breadcrumbs.append({
            'title': 'Home',
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
        'url': None,
        'is_current': True
    })
    
    return {'breadcrumbs': breadcrumbs, 'theme': theme}