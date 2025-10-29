from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Transacao(models.Model):
    """
    Modelo para representar transações de estoque (entradas e saídas).
    
    Uma transação pode estar associada a uma entrada ou saída através
    dos relacionamentos reversos 'entradas' e 'saidas'.
    """
    id_transacao = models.AutoField(primary_key=True)
    cod_nf = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        db_index=True,
        verbose_name="Código da Nota Fiscal"
    )
    cod_sku = models.ForeignKey(
        'Item',
        db_column='cod_sku',
        on_delete=models.DO_NOTHING,
        verbose_name="Item"
    )
    quantidade = models.DecimalField(
        max_digits=20, 
        decimal_places=2,
        verbose_name="Quantidade"
    )
    valor_unit = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Valor Unitário"
    )
    cod_fornecedor = models.ForeignKey(
        'Fornecedor',
        db_column='cod_fornecedor',
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        verbose_name="Fornecedor"
    )

    class Meta:
        db_table = 'transacoes'
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        indexes = [
            models.Index(fields=['cod_nf']),
            models.Index(fields=['cod_sku']),
            models.Index(fields=['cod_fornecedor']),
        ]

    def __str__(self):
        return f"Transação {self.id_transacao} - {self.cod_sku}"

    @property
    def valor_total(self):
        """Calcula o valor total da transação."""
        return self.quantidade * self.valor_unit

    @property
    def is_entrada(self):
        """Verifica se esta transação é uma entrada."""
        return hasattr(self, 'entradas') and getattr(self, 'entradas').exists()

    @property
    def is_saida(self):
        """Verifica se esta transação é uma saída."""
        return hasattr(self, 'saidas') and getattr(self, 'saidas').exists()


class Item(models.Model):
    """
    Modelo para representar itens do estoque.
    
    Cada item possui um código SKU único, descrição, unidade de medida
    e status ativo/inativo.
    """
    cod_sku = models.CharField(
        primary_key=True, 
        max_length=50,
        verbose_name="Código SKU"
    )
    descricao_item = models.TextField(
        db_index=True,
        verbose_name="Descrição do Item"
    )
    unid_medida = models.CharField(
        max_length=50,
        verbose_name="Unidade de Medida"
    )
    active = models.BooleanField(
        default=True, 
        db_index=True,
        verbose_name="Ativo"
    )

    class Meta:
        db_table = 'itens'
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'
        indexes = [
            models.Index(fields=['descricao_item']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return f"{self.cod_sku} - {self.descricao_item}"


class Usuario(models.Model):
    """
    Modelo para representar usuários do sistema de inventário.
    
    Estende o modelo User do Django com informações específicas
    do sistema de inventário.
    """
    mat_usuario = models.BigIntegerField(
        primary_key=True,
        verbose_name="Matrícula do Usuário"
    )
    nome_usuario = models.TextField(
        verbose_name="Nome do Usuário"
    )
    auth_user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='inventory_user',
        verbose_name="Usuário de Autenticação"
    )
    permissions = models.JSONField(
        default=list, 
        blank=True, 
        null=True,
        verbose_name="Permissões"
    )

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.nome_usuario

    @property
    def is_active(self):
        """Verifica se o usuário está ativo."""
        return self.auth_user.is_active if self.auth_user else False

    @property
    def email(self):
        """Retorna o email do usuário."""
        return self.auth_user.email if self.auth_user else None


# Signal to create a Usuario when a User is created
@receiver(post_save, sender=User)
def create_usuario(sender, instance, created, **kwargs):
    """
    Create a Usuario instance for newly created User instances
    """
    if created:
        # Get the last usuario ID to generate a unique mat_usuario
        last_usuario = Usuario.objects.order_by('-mat_usuario').first()
        new_mat_usuario = 1 if not last_usuario else last_usuario.mat_usuario + 1
        
        Usuario.objects.create(
            mat_usuario=new_mat_usuario,
            nome_usuario=instance.get_full_name() or instance.username,
            auth_user=instance
        )


class Fornecedor(models.Model):
    """
    Modelo para representar fornecedores de produtos.
    """
    cod_fornecedor = models.AutoField(
        primary_key=True,
        verbose_name="Código do Fornecedor"
    )
    nome_fornecedor = models.TextField(
        db_index=True,
        verbose_name="Nome do Fornecedor"
    )
    active = models.BooleanField(
        default=True, 
        db_index=True,
        verbose_name="Ativo"
    )

    class Meta:
        db_table = 'fornecedores'
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        indexes = [
            models.Index(fields=['nome_fornecedor']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return self.nome_fornecedor


class Entrada(models.Model):
    """
    Modelo para representar entradas de produtos no estoque.
    
    Cada entrada está associada a uma transação e registra
    quando e por quem o produto foi adicionado ao estoque.
    """
    cod_entrada = models.AutoField(
        primary_key=True,
        verbose_name="Código da Entrada"
    )
    transacao = models.ForeignKey(
        Transacao,
        related_name='entradas',
        on_delete=models.CASCADE,
        verbose_name="Transação"
    )
    mat_usuario = models.ForeignKey(
        Usuario,
        db_column='mat_usuario',
        on_delete=models.DO_NOTHING,
        verbose_name="Usuário"
    )
    data_entrada = models.DateField(
        db_index=True,
        verbose_name="Data da Entrada"
    )
    hora_entrada = models.TimeField(
        verbose_name="Hora da Entrada"
    )

    class Meta:
        db_table = 'entradas'
        verbose_name = 'Entrada'
        verbose_name_plural = 'Entradas'
        indexes = [
            models.Index(fields=['data_entrada']),
            models.Index(fields=['transacao']),
            models.Index(fields=['mat_usuario']),
        ]

    def __str__(self):
        return f"Entrada {self.cod_entrada} - {self.transacao.cod_sku}"

    @property
    def item(self):
        """Retorna o item da transação."""
        return self.transacao.cod_sku

    @property
    def quantidade(self):
        """Retorna a quantidade da transação."""
        return self.transacao.quantidade


class Saida(models.Model):
    """
    Modelo para representar saídas de produtos do estoque.
    
    Cada saída está associada a uma transação e registra
    quando e por quem o produto foi retirado do estoque.
    """
    cod_pedido = models.AutoField(
        primary_key=True,
        verbose_name="Código do Pedido"
    )
    transacao = models.ForeignKey(
        Transacao,
        related_name='saidas',
        on_delete=models.CASCADE,
        verbose_name="Transação"
    )
    mat_usuario = models.ForeignKey(
        Usuario,
        db_column='mat_usuario',
        on_delete=models.DO_NOTHING,
        verbose_name="Usuário"
    )
    data_saida = models.DateField(
        db_index=True,
        verbose_name="Data da Saída"
    )
    hora_saida = models.TimeField(
        verbose_name="Hora da Saída"
    )

    class Meta:
        db_table = 'saidas'
        verbose_name = 'Saída'
        verbose_name_plural = 'Saídas'
        indexes = [
            models.Index(fields=['data_saida']),
            models.Index(fields=['transacao']),
            models.Index(fields=['mat_usuario']),
        ]

    def __str__(self):
        return f"Pedido {self.cod_pedido} - {self.transacao.cod_sku}"

    @property
    def item(self):
        """Retorna o item da transação."""
        return self.transacao.cod_sku

    @property
    def quantidade(self):
        """Retorna a quantidade da transação."""
        return self.transacao.quantidade
