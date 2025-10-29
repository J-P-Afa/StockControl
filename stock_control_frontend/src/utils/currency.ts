// formatador de moeda
function formatCurrency(value: number, currency: 'BRL' | 'USD' = 'BRL'): string {
    const locale = currency === 'USD' ? 'en-US' : 'pt-BR';
    return new Intl.NumberFormat(locale, {
      style: 'currency',
      currency: currency
    }).format(value);
}

export default formatCurrency;