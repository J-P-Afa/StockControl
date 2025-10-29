"""
Middleware para conversão automática de nomenclatura entre camelCase e snake_case.

Este módulo fornece um middleware Django que converte automaticamente:
- Requisições: camelCase (frontend) → snake_case (backend)
- Respostas: snake_case (backend) → camelCase (frontend)

Isso permite que o frontend use a convenção JavaScript (camelCase) enquanto
o backend mantém a convenção Python (snake_case), sem necessidade de conversão
manual em cada view ou serializer.
"""

import json
import logging
from typing import Callable
from django.http import HttpRequest, HttpResponse
from .utils import camelize_dict_keys, snakify_dict_keys

logger = logging.getLogger(__name__)


class CamelSnakeCaseMiddleware:
    """
    Middleware que transforma dados de requisição de camelCase para snake_case
    e dados de resposta de snake_case para camelCase.
    
    Fluxo de Processamento:
    ----------------------
    1. REQUISIÇÃO (Request):
       - Verifica se o content-type é 'application/json'
       - Converte todas as chaves do JSON de camelCase para snake_case
       - Exemplo: {"firstName": "João"} → {"first_name": "João"}
    
    2. RESPOSTA (Response):
       - Verifica se o content-type da resposta é 'application/json'
       - Converte todas as chaves do JSON de snake_case para camelCase
       - Exemplo: {"first_name": "João"} → {"firstName": "João"}
    
    Casos de Uso:
    ------------
    - API REST com frontend em JavaScript/TypeScript
    - Aplicações Vue.js, React, Angular consumindo API Django
    - Qualquer cenário onde há incompatibilidade de convenções de nomenclatura
    
    Limitações:
    ----------
    - Apenas processa requisições/respostas com content-type 'application/json'
    - Não processa dados binários ou multipart/form-data
    - Erros de parsing são capturados mas não interrompem a requisição
    
    Configuração:
    ------------
    Adicione ao MIDDLEWARE em settings.py:
    
    MIDDLEWARE = [
        'corsheaders.middleware.CorsMiddleware',
        'django.middleware.security.SecurityMiddleware',
        # ... outros middlewares ...
        'inventory.middleware.CamelSnakeCaseMiddleware',  # Adicione aqui
    ]
    
    Nota: A ordem importa! Coloque após middlewares de segurança e CORS.
    
    Exemplos:
    --------
    Request (Frontend):
    POST /api/users/
    {
        "firstName": "João",
        "lastName": "Silva",
        "emailAddress": "joao@example.com"
    }
    
    Recebido pelo Django (após middleware):
    {
        "first_name": "João",
        "last_name": "Silva",
        "email_address": "joao@example.com"
    }
    
    Response do Django:
    {
        "first_name": "João",
        "last_name": "Silva",
        "email_address": "joao@example.com",
        "created_at": "2025-10-01T10:30:00Z"
    }
    
    Recebido pelo Frontend (após middleware):
    {
        "firstName": "João",
        "lastName": "Silva",
        "emailAddress": "joao@example.com",
        "createdAt": "2025-10-01T10:30:00Z"
    }
    """
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """
        Inicializa o middleware.
        
        Args:
            get_response: Função que processa a requisição e retorna a resposta.
                         Fornecida automaticamente pelo Django.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Processa a requisição e resposta aplicando conversões de nomenclatura.
        
        Args:
            request: Objeto HttpRequest do Django
            
        Returns:
            HttpResponse com dados convertidos para camelCase
        """
        # Processa o corpo da requisição de camelCase para snake_case
        if request.body and self._is_json_request(request):
            self._process_request_body(request)
        
        # Obtém a resposta da view
        response = self.get_response(request)
        
        # Processa o corpo da resposta de snake_case para camelCase
        if self._is_json_response(response):
            self._process_response_body(response)
        
        return response
    
    def _is_json_request(self, request: HttpRequest) -> bool:
        """
        Verifica se a requisição tem content-type JSON.
        
        Args:
            request: Objeto HttpRequest do Django
            
        Returns:
            True se for JSON, False caso contrário
        """
        content_type = getattr(request, 'content_type', '')
        return 'application/json' in content_type
    
    def _is_json_response(self, response: HttpResponse) -> bool:
        """
        Verifica se a resposta tem content-type JSON.
        
        Args:
            response: Objeto HttpResponse do Django
            
        Returns:
            True se for JSON, False caso contrário
        """
        return (
            hasattr(response, 'content') and 
            response.get('Content-Type', '') == 'application/json'
        )
    
    def _process_request_body(self, request: HttpRequest) -> None:
        """
        Converte o corpo da requisição de camelCase para snake_case.
        
        Args:
            request: Objeto HttpRequest do Django (modificado in-place)
        """
        try:
            # Parse o corpo da requisição
            request_data = json.loads(request.body)
            
            # Converte chaves camelCase para snake_case
            snake_data = snakify_dict_keys(request_data)
            
            # Substitui o corpo da requisição pela versão em snake_case
            # type: ignore - _body é um atributo interno do Django que pode ser modificado
            request._body = json.dumps(snake_data).encode('utf-8')  # type: ignore
            
            # Loga conversão se request_data e snake_data forem dicionários
            if isinstance(request_data, dict) and isinstance(snake_data, dict):
                logger.debug(
                    f"Request body converted: {list(request_data.keys())} → "
                    f"{list(snake_data.keys())}"
                )
            
        except json.JSONDecodeError as e:
            # Erro de parsing JSON - loga mas não interrompe
            logger.warning(
                f"Failed to parse request body as JSON: {e}. "
                f"Body will be passed unchanged."
            )
        except Exception as e:
            # Qualquer outro erro - loga mas não interrompe
            logger.error(
                f"Unexpected error in CamelSnakeCaseMiddleware (request): {e}",
                exc_info=True
            )
    
    def _process_response_body(self, response: HttpResponse) -> None:
        """
        Converte o corpo da resposta de snake_case para camelCase.
        
        Args:
            response: Objeto HttpResponse do Django (modificado in-place)
        """
        try:
            # Parse o conteúdo da resposta
            content = json.loads(response.content.decode('utf-8'))
            
            # Converte chaves snake_case para camelCase
            camel_content = camelize_dict_keys(content)
            
            # Substitui o conteúdo da resposta pela versão em camelCase
            # type: ignore - content pode ser modificado em HttpResponse
            response.content = json.dumps(camel_content).encode('utf-8')  # type: ignore
            
            # Atualiza Content-Length se necessário
            if hasattr(response, '__getitem__') and 'Content-Length' in response:  # type: ignore
                response['Content-Length'] = len(response.content)  # type: ignore
            
            logger.debug(
                f"Response body converted to camelCase. "
                f"Size: {len(response.content)} bytes"
            )
            
        except json.JSONDecodeError as e:
            # Erro de parsing JSON - loga mas não interrompe
            logger.warning(
                f"Failed to parse response body as JSON: {e}. "
                f"Response will be passed unchanged."
            )
        except Exception as e:
            # Qualquer outro erro - loga mas não interrompe
            logger.error(
                f"Unexpected error in CamelSnakeCaseMiddleware (response): {e}",
                exc_info=True
            ) 