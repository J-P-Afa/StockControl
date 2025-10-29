import requests
from decimal import Decimal
from datetime import date
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class CurrencyService:
    """
    Serviço para conversão de moedas usando a API do Banco Central do Brasil.
    """
    
    BASE_URL = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata"
    
    @classmethod
    def get_usd_rate(cls, target_date: Optional[date] = None) -> Optional[Decimal]:
        """
        Obtém a cotação do dólar para uma data específica.
        
        Args:
            target_date: Data para a cotação (padrão: hoje)
            
        Returns:
            Taxa de conversão USD/BRL ou None se não conseguir obter
        """
        if target_date is None:
            target_date = date.today()
        
        try:
            # Formatar data no padrão MM-DD-YYYY
            formatted_date = target_date.strftime('%m-%d-%Y')
            
            # URL para cotação do dólar em uma data específica
            url = f"{cls.BASE_URL}/CotacaoDolarDia(dataCotacao=@dataCotacao)"
            params = {
                '@dataCotacao': f"'{formatted_date}'",
                '$format': 'json'
            }
            
            logger.info(f"Buscando cotação USD para data: {formatted_date}")
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'value' in data and len(data['value']) > 0:
                # Usar a cotação de venda (cotacaoVenda)
                usd_rate = Decimal(str(data['value'][0]['cotacaoVenda']))
                logger.info(f"Cotação USD obtida: {usd_rate}")
                return usd_rate
            else:
                logger.warning(f"Nenhuma cotação encontrada para a data: {formatted_date}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para API do Banco Central: {e}")
            return None
        except (KeyError, IndexError, ValueError) as e:
            logger.error(f"Erro ao processar resposta da API: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao obter cotação USD: {e}")
            return None
    
    @classmethod
    def convert_brl_to_usd(cls, brl_amount: Decimal, target_date: Optional[date] = None) -> Optional[Decimal]:
        """
        Converte um valor em BRL para USD.
        
        Args:
            brl_amount: Valor em BRL
            target_date: Data para a cotação (padrão: hoje)
            
        Returns:
            Valor convertido em USD ou None se não conseguir obter a cotação
        """
        usd_rate = cls.get_usd_rate(target_date)
        
        if usd_rate is None:
            return None
        
        try:
            # Converter BRL para USD dividindo pela cotação
            usd_amount = brl_amount / usd_rate
            # Arredondar para 2 casas decimais
            return usd_amount.quantize(Decimal('0.01'))
        except Exception as e:
            logger.error(f"Erro ao converter BRL para USD: {e}")
            return None
    
    @classmethod
    def get_cached_rate(cls, target_date: Optional[date] = None) -> Optional[Decimal]:
        """
        Obtém a cotação com cache simples (para evitar muitas requisições).
        Em produção, seria melhor usar Redis ou similar.
        """
        if target_date is None:
            target_date = date.today()
        
        # Por simplicidade, sempre busca nova cotação
        # Em produção, implementar cache com TTL
        return cls.get_usd_rate(target_date)
