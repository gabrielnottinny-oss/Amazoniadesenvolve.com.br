from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class AuditMixin(models.Model):
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    class Meta:
        abstract = True

class Beneficiario(AuditMixin):
    nome = models.CharField(max_length=180)
    data_nascimento = models.DateField(null=True, blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    territorio = models.ForeignKey("Comunidade",null=True,blank=True,on_delete=models.PROTECT,related_name="beneficiarios")
    comunidade = models.CharField(max_length=160)
    municipio = models.CharField(max_length=100, default='Maués')
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    def __str__(self): return self.nome
    class Meta:
        ordering = ['nome']
        permissions = [('exportar_beneficiario','Pode exportar beneficiários')]

class ProjetoSocial(AuditMixin):
    class Status(models.TextChoices):
        PLANEJAMENTO='planejamento','Planejamento'
        EXECUCAO='execucao','Em execução'
        CONCLUIDO='concluido','Concluído'
        SUSPENSO='suspenso','Suspenso'
    territorios = models.ManyToManyField("Comunidade",blank=True,related_name="projetos_sociais")
    titulo = models.CharField(max_length=200)
    area = models.CharField(max_length=120)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=20,choices=Status.choices,default=Status.PLANEJAMENTO)
    inicio = models.DateField(null=True,blank=True)
    termino = models.DateField(null=True,blank=True)
    orcamento = models.DecimalField(max_digits=14,decimal_places=2,default=0,validators=[MinValueValidator(0)])
    beneficiarios = models.ManyToManyField(Beneficiario,blank=True,related_name='projetos')
    def __str__(self): return self.titulo
    class Meta: ordering=['-criado_em']

class AgenteComunitario(AuditMixin):
    class Vinculo(models.TextChoices):
        VOLUNTARIO='voluntario','Voluntário'
        CONTRATADO='contratado','Contratado'
        COORDENADOR='coordenador','Coordenador regional'
    territorios = models.ManyToManyField("Comunidade",blank=True,related_name="agentes_comunitarios")
    nome = models.CharField(max_length=180)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=30,blank=True)
    municipio = models.CharField(max_length=100,default='Maués')
    vinculo = models.CharField(max_length=20,choices=Vinculo.choices)
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL,related_name='agente')
    projetos = models.ManyToManyField(ProjetoSocial,blank=True,related_name='agentes')
    ativo = models.BooleanField(default=True)
    def __str__(self): return self.nome
    class Meta: ordering=['nome']


class Municipio(models.Model):
    nome = models.CharField(max_length=120)
    uf = models.CharField(max_length=2, default='AM')
    ativo = models.BooleanField(default=True)
    class Meta:
        ordering = ['nome']
        constraints = [models.UniqueConstraint(fields=['nome','uf'],name='municipio_nome_uf_unico')]
    def __str__(self): return f'{self.nome}/{self.uf}'

class Polo(models.Model):
    nome = models.CharField(max_length=160)
    municipio = models.ForeignKey(Municipio,on_delete=models.PROTECT,related_name='polos')
    ativo = models.BooleanField(default=True)
    class Meta: ordering = ['nome']
    def __str__(self): return f'{self.nome} — {self.municipio}'

class Comunidade(models.Model):
    nome = models.CharField(max_length=160)
    municipio = models.ForeignKey(Municipio,on_delete=models.PROTECT,related_name='comunidades')
    polo = models.ForeignKey(Polo,on_delete=models.PROTECT,related_name='comunidades')
    ativo = models.BooleanField(default=True)
    class Meta:
        ordering = ['nome']
        constraints = [models.UniqueConstraint(fields=['nome','municipio'],name='comunidade_nome_municipio_unico')]
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.polo_id and self.municipio_id and self.polo.municipio_id != self.municipio_id:
            raise ValidationError({'polo':'O polo deve pertencer ao município informado.'})
    def __str__(self): return f'{self.nome} — {self.municipio}'

class AcessoTerritorial(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='acessos_territoriais')
    municipio = models.ForeignKey(Municipio,on_delete=models.CASCADE,null=True,blank=True)
    polo = models.ForeignKey(Polo,on_delete=models.CASCADE,null=True,blank=True)
    comunidade = models.ForeignKey(Comunidade,on_delete=models.CASCADE,null=True,blank=True)
    class Meta: constraints = [models.CheckConstraint(condition=(models.Q(municipio__isnull=False)&models.Q(polo__isnull=True)&models.Q(comunidade__isnull=True))|(models.Q(municipio__isnull=True)&models.Q(polo__isnull=False)&models.Q(comunidade__isnull=True))|(models.Q(municipio__isnull=True)&models.Q(polo__isnull=True)&models.Q(comunidade__isnull=False)),name='acesso_uma_area')]
    def clean(self):
        from django.core.exceptions import ValidationError
        if sum(bool(v) for v in (self.municipio_id,self.polo_id,self.comunidade_id)) != 1:
            raise ValidationError('Escolha exatamente um território por concessão.')
    def __str__(self): return f'{self.usuario} — {self.comunidade or self.polo or self.municipio}'


class Familia(AuditMixin):
    codigo = models.CharField(max_length=30, unique=True)
    referencia = models.CharField(max_length=180, help_text='Nome de referência familiar; evite dados desnecessários')
    territorio = models.ForeignKey(Comunidade, on_delete=models.PROTECT, related_name='familias')
    endereco_referencia = models.CharField(max_length=240, blank=True)
    telefone = models.CharField(max_length=30, blank=True)
    membros = models.ManyToManyField(Beneficiario, blank=True, related_name='familias')
    observacoes = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    def __str__(self): return f'{self.codigo} — {self.referencia}'
    class Meta: ordering=['codigo']

class VisitaDomiciliar(AuditMixin):
    class Situacao(models.TextChoices):
        AGENDADA='agendada','Agendada'
        REALIZADA='realizada','Realizada'
        NAO_REALIZADA='nao_realizada','Não realizada'
    familia = models.ForeignKey(Familia,on_delete=models.PROTECT,related_name='visitas')
    agente = models.ForeignKey(AgenteComunitario,on_delete=models.PROTECT,related_name='visitas')
    data = models.DateField()
    situacao = models.CharField(max_length=20,choices=Situacao.choices,default=Situacao.AGENDADA)
    finalidade = models.CharField(max_length=200)
    relato = models.TextField(blank=True)
    proxima_visita = models.DateField(null=True,blank=True)
    def __str__(self): return f'{self.familia.codigo} — {self.data}'
    class Meta: ordering=['-data','-criado_em']

class AcompanhamentoSocial(AuditMixin):
    class Situacao(models.TextChoices):
        ABERTO='aberto','Aberto'
        ANDAMENTO='andamento','Em andamento'
        CONCLUIDO='concluido','Concluído'
    familia = models.ForeignKey(Familia,on_delete=models.PROTECT,related_name='acompanhamentos')
    projeto = models.ForeignKey(ProjetoSocial,on_delete=models.PROTECT,null=True,blank=True,related_name='acompanhamentos')
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    encaminhamento = models.TextField(blank=True)
    prazo = models.DateField(null=True,blank=True)
    situacao = models.CharField(max_length=20,choices=Situacao.choices,default=Situacao.ABERTO)
    def __str__(self): return self.titulo
    class Meta: ordering=['-criado_em']
