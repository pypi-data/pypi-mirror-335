from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page
from wagtail.blocks import RichTextBlock
from wagtail import blocks
from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.snippets.models import register_snippet
from wagtail.images.blocks import ImageChooserBlock
from wagtail.fields import StreamField
from coderedcms.models import CoderedWebPage
from modelcluster.models import ClusterableModel


from wagtail.blocks import StreamBlock, StructBlock, CharBlock, ChoiceBlock, RichTextBlock, ChooserBlock

from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import MultiFieldPanel, FieldPanel, InlinePanel
from wagtail.documents.models import Document
from wagtail.fields import StreamField
from .blocks import ButtonBlock
from .blocks import ImageBlock
from modelcluster.fields import ParentalKey
from wagtail.models import Orderable


from enap_designsystem.blocks import EnapFooterGridBlock
from enap_designsystem.blocks import EnapFooterSocialGridBlock 
from enap_designsystem.blocks import EnapAccordionPanelBlock
from enap_designsystem.blocks import EnapNavbarLinkBlock



from enap_designsystem.blocks import PageListBlock
from enap_designsystem.blocks import NewsCarouselBlock
from enap_designsystem.blocks import DropdownBlock
from enap_designsystem.blocks import CoursesCarouselBlock
from enap_designsystem.blocks import EventsCarouselBlock
from enap_designsystem.blocks import EnapBannerBlock
from enap_designsystem.blocks import FeatureImageTextBlock
from enap_designsystem.blocks import EnapAccordionBlock
from enap_designsystem.blocks.base_blocks import ButtonGroupBlock
from enap_designsystem.blocks.base_blocks import CarouselBlock
from wagtail.snippets.blocks import SnippetChooserBlock

from enap_designsystem.blocks import LAYOUT_STREAMBLOCKS
from enap_designsystem.blocks import DYNAMIC_CARD_STREAMBLOCKS
from enap_designsystem.blocks import CARD_CARDS_STREAMBLOCKS


# class MainLayout(Page):
#     template = "enap_designsystem/main_layout.html"
#     content_panels = Page.content_panels + [
#         FieldPanel("title"),
#     ]

# class MidLayout(Page):
#     template = "enap_designsystem/mid_layout.html"
#     content_panels = Page.content_panels + [
#         FieldPanel("title"),
#     ]

# class ComponentLayout(models.Model):
#     name = models.CharField(max_length=255)
#     content = models.TextField()

#     panels = [
#         FieldPanel("name"),
#         FieldPanel("content"),
#     ]

#     class Meta:
#         abstract = True

class ENAPLayout(CoderedWebPage):
    """Página personalizada herdando todas as características de CoderedWebPage."""
    
    admin_notes = models.TextField(
        verbose_name="Anotações Internas",
        blank=True,
        help_text="Escreva observações importantes. Este campo é visível apenas para administradores."
    )

    template = "enap_designsystem/pages/enap_layout.html"

    settings_panels = CoderedWebPage.settings_panels + [
        FieldPanel('admin_notes'),
    ]

    body = StreamField(
        LAYOUT_STREAMBLOCKS,
        null=True,
        blank=True,
        use_json_field=True,
    )

    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    footer = models.ForeignKey(
        "EnapFooterSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = CoderedWebPage.content_panels + [
		FieldPanel("navbar"),
		FieldPanel("footer"),
	]
    class Meta:
        verbose_name = "ENAP Layout"
        verbose_name_plural = "ENAP Layouts"





class ENAPFormacao(CoderedWebPage):
    """Página personalizada herdando todas as características de CoderedWebPage."""
    
    admin_notes = models.TextField(
        verbose_name="Anotações Internas",
        blank=True,
        help_text="Escreva observações importantes."
    )

    template = "enap_designsystem/pages/template-cursos.html"
    miniview_template = "coderedcms/pages/article_page.mini.html"
    search_template = "coderedcms/pages/article_page.search.html"

    content = StreamField(
        [
            ("banner", EnapBannerBlock()), 
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    feature = StreamField(
        [
            ("enap_herofeature", FeatureImageTextBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    accordion_cursos = StreamField(
        [
            ("enap_accordion", EnapAccordionBlock()),
            ('button_group', ButtonGroupBlock()),
            ('carousel', CarouselBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    body = StreamField(
        CARD_CARDS_STREAMBLOCKS,
        null=True,
        blank=True,
        use_json_field=True,
    )


    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    footer = models.ForeignKey(
        "EnapFooterSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    modal = models.ForeignKey(
    "Modal",  
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name="+",
    )

    wizard = models.ForeignKey(
    "Wizard",  
    null=True,
    blank=True,
    on_delete=models.SET_NULL,
    related_name="+",
    )

    # Painéis no admin do Wagtail
    content_panels = CoderedWebPage.content_panels + [
        FieldPanel('navbar'),
        FieldPanel('modal'), 
        FieldPanel('wizard'),
        FieldPanel('footer'),
        FieldPanel('content'),
        FieldPanel('feature'),
        FieldPanel('accordion_cursos'),
    ]

    class Meta:
        verbose_name = "Template ENAP Curso"
        verbose_name_plural = "Template ENAP Cursos"






class ENAPTemplatev1(CoderedWebPage):
    """Página personalizada herdando todas as características de CoderedWebPage."""
    
    admin_notes = models.TextField(
        verbose_name="Anotações Internas",
        blank=True,
        help_text="Escreva observações importantes."
    )

    template = "enap_designsystem/pages/draft_template-teste.html"
    miniview_template = "coderedcms/pages/article_page.mini.html"
    search_template = "coderedcms/pages/article_page.search.html"

    page_title = models.CharField(
        max_length=255, 
        default="Título Padrão", 
        verbose_name="Título da Página"
    )


    body = StreamField(
        DYNAMIC_CARD_STREAMBLOCKS,
        null=True,
        blank=True,
        use_json_field=True,
    )


    teste_courses = StreamField(
        [("courses_carousel", CoursesCarouselBlock())], 
        null=True,
        blank=True,
        use_json_field=True,
    )

    noticias = StreamField(
        [("eventos_carousel", EventsCarouselBlock())], 
        null=True,
        blank=True,
        use_json_field=True,
    )

    teste_noticia = StreamField(
        [("noticias_carousel", NewsCarouselBlock())], 
        null=True,
        blank=True,
        use_json_field=True,
    )

    teste_preview = StreamField(
        [("page_preview_teste", PageListBlock())],
        null=True,
        blank=True,
        use_json_field=True,
    )

    dropdown_content = StreamField(
        [("dropdown", DropdownBlock())],
        null=True,
        blank=True,
        use_json_field=True,
    )
    
    paragrafo = RichTextField(
        blank=True, 
        help_text="Adicione o texto do parágrafo aqui.", 
        verbose_name="Parágrafo sessao dinamica"
    )
    
    video_background = models.FileField(
        upload_to='media/videos', 
        null=True, 
        blank=True, 
        verbose_name="Vídeo de Fundo"
    )

    background_image = StreamField(
        [
            ("image", ImageBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    linkcta = RichTextField(blank=True)
    button_link = models.URLField(
        "Link do Botão",
        blank=True,
        help_text="URL do link do botão"
    )
    

    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    footer = models.ForeignKey(
        "EnapFooterSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Painéis no admin do Wagtail
    content_panels = CoderedWebPage.content_panels + [
        FieldPanel('navbar'),
        FieldPanel('video_background'),
        MultiFieldPanel(
            [
                FieldPanel('page_title'),
                FieldPanel('paragrafo'),
                FieldPanel('background_image'),
                FieldPanel('button_link'),
            ],
            heading="Título e Parágrafo CTA Dinamico"
        ),
        FieldPanel('teste_courses'),
        FieldPanel('noticias'),
        FieldPanel('dropdown_content'),
        FieldPanel('teste_preview'),
        FieldPanel('teste_noticia'),  
        FieldPanel('footer'),
    ]

    class Meta:
        verbose_name = "Enap home v1"
        verbose_name_plural = "Enap Home v1"





class ENAPTeste(CoderedWebPage):
    """Página personalizada herdando todas as características de CoderedWebPage."""
    
    admin_notes = models.TextField(
        verbose_name="Anotações Internas",
        blank=True,
        help_text="Escreva observações importantes."
    )

    template = "enap_designsystem/pages/template_homeII.html"
    miniview_template = "coderedcms/pages/article_page.mini.html"
    search_template = "coderedcms/pages/article_page.search.html"

    page_title = models.CharField(
        max_length=255, 
        default="Título Padrão", 
        verbose_name="Título da Página"
    )


    body = StreamField(
        DYNAMIC_CARD_STREAMBLOCKS,
        null=True,
        blank=True,
        use_json_field=True,
    )


    teste_courses = StreamField(
        [("courses_carousel", CoursesCarouselBlock())], 
        null=True,
        blank=True,
        use_json_field=True,
    )

    noticias = StreamField(
        [("eventos_carousel", EventsCarouselBlock())], 
        null=True,
        blank=True,
        use_json_field=True,
    )

    teste_noticia = StreamField(
        [("noticias_carousel", NewsCarouselBlock())], 
        null=True,
        blank=True,
        use_json_field=True,
    )

    teste_preview = StreamField(
        [("page_preview_teste", PageListBlock())],
        null=True,
        blank=True,
        use_json_field=True,
    )

    dropdown_content = StreamField(
        [("dropdown", DropdownBlock())],
        null=True,
        blank=True,
        use_json_field=True,
    )
    
    paragrafo = RichTextField(
        blank=True, 
        help_text="Adicione o texto do parágrafo aqui.", 
        verbose_name="Parágrafo sessao dinamica"
    )
    
    video_background = models.FileField(
        upload_to='media/videos', 
        null=True, 
        blank=True, 
        verbose_name="Vídeo de Fundo"
    )

    background_image = StreamField(
        [
            ("image", ImageBlock()),
        ],
        null=True,
        blank=True,
        use_json_field=True,
    )

    linkcta = RichTextField(blank=True)
    button_link = models.URLField(
        "Link do Botão",
        blank=True,
        help_text="URL do link do botão"
    )
    

    navbar = models.ForeignKey(
        "EnapNavbarSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    footer = models.ForeignKey(
        "EnapFooterSnippet",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Painéis no admin do Wagtail
    content_panels = CoderedWebPage.content_panels + [
        FieldPanel('navbar'),
        FieldPanel('video_background'),
        MultiFieldPanel(
            [
                FieldPanel('page_title'),
                FieldPanel('paragrafo'),
                FieldPanel('background_image'),
                FieldPanel('button_link'),
            ],
            heading="Título e Parágrafo CTA Dinamico"
        ),
        FieldPanel('teste_courses'),
        FieldPanel('noticias'),
        FieldPanel('dropdown_content'),
        FieldPanel('teste_preview'),
        FieldPanel('teste_noticia'),  
        FieldPanel('footer'),
    ]

    class Meta:
        verbose_name = "Enap Home v2"
        verbose_name_plural = "Home V2"




@register_snippet
class EnapFooterSnippet(ClusterableModel):
    """
    Custom footer for bottom of pages on the site.
    """

    class Meta:
        verbose_name = "ENAP Footer"
        verbose_name_plural = "ENAP Footers"

    image = StreamField([
		("logo", ImageChooserBlock()),
	], blank=True, use_json_field=True)

    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text="Título do snippet"
    )

    links = StreamField([
		("enap_footergrid", EnapFooterGridBlock()),
	], blank=True, use_json_field=True)

    social = StreamField([
		("enap_footersocialgrid", EnapFooterSocialGridBlock()),
	], blank=True, use_json_field=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("image"),
        FieldPanel("social"),
        FieldPanel("links"),
    ]

    def __str__(self) -> str:
        return self.name
    

@register_snippet
class EnapAccordionSnippet(ClusterableModel):
    """
	Snippet de Accordion estilo FAQ.
    """
    class Meta:
        verbose_name = "ENAP Accordion"
        verbose_name_plural = "ENAP Accordions"

    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        help_text="Nome do snippet para facilitar a identificação no admin."
    )

    panels_content = StreamField([
        ("accordion_item", EnapAccordionPanelBlock()),
    ], blank=True, use_json_field=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("panels_content"),
    ]

    def __str__(self):
        return self.name


@register_snippet
class EnapNavbarSnippet(ClusterableModel):
	"""
	Snippet para a Navbar do ENAP, permitindo logo, busca, idioma e botão de contraste.
	"""

	name = models.CharField(
		max_length=255,
		blank=False,
		null=False,
		help_text="Nome do snippet para facilitar a identificação no admin."
	)

	logo = StreamField([
		("image", ImageChooserBlock())
	], blank=True, use_json_field=True, verbose_name="Logo da Navbar")

	links = StreamField([
		("navbar_link", EnapNavbarLinkBlock()),
	], blank=True, use_json_field=True)

	panels = [
		FieldPanel("name"),
		FieldPanel("logo"),
		FieldPanel("links"),
	]

	class Meta:
		verbose_name = " ENAP Navbar"
		verbose_name_plural = "ENAP Navbars"

	def __str__(self):
		return self.name



@register_snippet
class Alert(models.Model):
    """
    Snippet para criar alertas reutilizáveis.
    Cada tipo de alerta já vem com seu próprio ícone e esquema de cores.
    """
    ALERT_TYPES = [
        ('success', 'Sucesso'),  # Verde com ícone de check
        ('error', 'Erro'),       # Vermelho com ícone de erro
        ('warning', 'Aviso'),    # Amarelo com ícone de aviso
        ('info', 'Informação'),  # Azul com ícone de informação
    ]
    
    title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Título")
    message = models.TextField(verbose_name="Mensagem")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='success', verbose_name="Tipo de Alerta")
    button_text = models.CharField(max_length=50, blank=True, default="Fechar", verbose_name="Texto do Botão")
    show_automatically = models.BooleanField(default=True, verbose_name="Mostrar automaticamente")
    
    panels = [
        FieldPanel('title'),
        FieldPanel('message'),
        FieldPanel('alert_type'),
        FieldPanel('button_text'),
        FieldPanel('show_automatically'),
    ]
    
    def __str__(self):
        return self.title or f"Alerta ({self.get_alert_type_display()})"
    
    class Meta:
        verbose_name = "ENAP Alerta"
        verbose_name_plural = "ENAP Alertas"





# Opções para os tipos de alerta
ALERT_TYPES = [
    ('success', 'Sucesso'),
    ('error', 'Erro'),
    ('warning', 'Aviso'),
    ('info', 'Informação'),
]

# Os ícones, cores de fundo e cores dos ícones serão aplicados automaticamente
# com base no tipo de alerta selecionado

class AlertBlock(StructBlock):
    """
    Bloco de alerta que pode ser adicionado a um StreamField
    """
    title = CharBlock(required=False, help_text="Título do alerta (opcional)")
    message = RichTextBlock(required=True, help_text="Mensagem do alerta")
    alert_type = ChoiceBlock(choices=ALERT_TYPES, default='success', help_text="Tipo do alerta")
    button_text = CharBlock(required=False, default="Fechar", help_text="Texto do botão (deixe em branco para não mostrar botão)")
    
    class Meta:
        template = "enap_designsystem/blocks/draft_alerts.html"
        icon = 'warning'
        label = 'ENAP Alerta'


# Exemplo de uso em uma página
class FlexibleContentPage(Page):
    body = StreamField([
        ('alert', AlertBlock()),
        # Outros blocos de conteúdo...
    ], use_json_field=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]





class WizardChooserBlock(ChooserBlock):
    @property
    def target_model(self):
        from enap_designsystem.models import Wizard  # Importação local para evitar referência circular
        return Wizard

    def get_form_state(self, value):
        return {
            'id': value.id if value else None,
            'title': str(value) if value else '',
        }

@register_snippet
class Wizard(ClusterableModel):
    """
    Snippet para criar wizards reutilizáveis
    """
    title = models.CharField(max_length=255, verbose_name="Título")
    
    panels = [
        FieldPanel('title'),
        InlinePanel('steps', label="Etapas do Wizard"),
    ]
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "ENAP Wizard"
        verbose_name_plural = "ENAP Wizard"


class WizardStep(Orderable):
    """
    Uma etapa dentro de um wizard
    """
    wizard = ParentalKey(Wizard, on_delete=models.CASCADE, related_name='steps')
    title = models.CharField(max_length=255, verbose_name="Título da Etapa")
    content = models.TextField(blank=True, verbose_name="Conteúdo")
    
    panels = [
        FieldPanel('title'),
        FieldPanel('content'),
    ]
    
    def __str__(self):
        return f"{self.title} - Etapa {self.sort_order + 1}"


class WizardBlock(StructBlock):
    """
    Bloco para adicionar um wizard a uma página
    """
    wizard = WizardChooserBlock(required=True)
    current_step = ChoiceBlock(
        choices=[(1, 'Etapa 1'), (2, 'Etapa 2'), (3, 'Etapa 3'), (4, 'Etapa 4'), (5, 'Etapa 5')],
        default=1,
        required=True,
        help_text="Qual etapa deve ser exibida como ativa",
    )
    
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        wizard = value['wizard']
        
        # Adiciona as etapas do wizard ao contexto
        steps = wizard.steps.all().order_by('sort_order')
        
        # Adapta o seletor de etapa atual para corresponder ao número real de etapas
        current_step = min(int(value['current_step']), steps.count())
        
        context.update({
            'wizard': wizard,
            'steps': steps,
            'current_step': current_step,
        })
        return context
    
    class Meta:
        template = 'enap_designsystem/blocks/draft_wizard.html'
        icon = 'list-ol'
        label = 'ENAP Wizard'




@register_snippet
class Modal(models.Model):
    """
    Snippet para criar modais reutilizáveis
    """
    title = models.CharField(max_length=255, verbose_name="Título do Modal")
    content = RichTextField(verbose_name="Conteúdo do Modal")
    button_text = models.CharField(max_length=100, verbose_name="Texto do Botão", default="Abrir Modal")
    button_action_text = models.CharField(max_length=100, verbose_name="Texto do Botão de Ação", blank=True, 
                                         help_text="Deixe em branco para não exibir um botão de ação")
    
    panels = [
        FieldPanel('title'),
        FieldPanel('content'),
        FieldPanel('button_text'),
        FieldPanel('button_action_text'),
    ]
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "ENAP Modal"
        verbose_name_plural = "ENAP Modais"



class ModalBlock(StructBlock):
    """
    Bloco para incluir um modal dentro de um StreamField.
    Permite escolher entre um modal existente ou criar um novo na hora.
    """
    use_existing = SnippetChooserBlock('enap_designsystem.Modal', required=False, help_text="Selecione um modal existente ou deixe em branco para criar um novo")
    
    # Campos para criar um novo modal inline
    title = CharBlock(required=False, help_text="Título do modal (se não usar um existente)")
    content = RichTextBlock(required=False, help_text="Conteúdo do modal (se não usar um existente)")
    button_text = CharBlock(required=False, default="Abrir Modal", help_text="Texto do botão que abre o modal")
    button_action_text = CharBlock(required=False, help_text="Texto do botão de ação dentro do modal (opcional)")
    
    class Meta:
        template = 'enap_designsystem/blocks/draft_modal.html'
        icon = 'placeholder'
        label = 'ENAP Modal'