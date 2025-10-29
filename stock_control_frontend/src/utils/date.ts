/** Converte "DD/MM/YYYY" em número de milissegundos desde 1970 */
export function parseBrazilianDate(dateStr: string): number {
    const [day, month, year] = dateStr.split('/').map(Number);
    // mês no construtor Date é 0‑indexado
    return new Date(year, month - 1, day).getTime();
}

/** Formata uma data do formato ISO (YYYY-MM-DD) para o formato brasileiro (DD/MM/YYYY) */
export function formatDateToBrazilian(isoDate: string): string {
    // Se a data já estiver no formato brasileiro, retorna como está
    if (isoDate.includes('/')) return isoDate;
    
    try {
        const [year, month, day] = isoDate.split('-');
        return `${day}/${month}/${year}`;
    } catch (e) {
        console.error('Erro ao formatar data:', e);
        return isoDate; // Retorna a string original em caso de erro
    }
}

/** Converte uma data do formato brasileiro (DD/MM/YYYY) para o formato ISO (YYYY-MM-DD) */
export function formatBrazilianDateToISO(brazilianDate: string): string {
    // Se a data já estiver no formato ISO, retorna como está
    if (brazilianDate.includes('-')) return brazilianDate;
    
    try {
        const [day, month, year] = brazilianDate.split('/');
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')}`;
    } catch (e) {
        console.error('Erro ao converter data brasileira para ISO:', e);
        return brazilianDate; // Retorna a string original em caso de erro
    }
}

/** Obtém a data atual no formato brasileiro (DD/MM/YYYY) */
export function getCurrentBrazilianDate(): string {
    const today = new Date();
    const day = String(today.getDate()).padStart(2, '0');
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const year = today.getFullYear();
    return `${day}/${month}/${year}`;
}

/** Obtém a data atual no formato ISO (YYYY-MM-DD) usando data local */
export function getCurrentISODate(): string {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/** Valida se uma string é uma data válida no formato brasileiro (DD/MM/YYYY) */
export function isValidBrazilianDate(dateStr: string): boolean {
    if (!dateStr || typeof dateStr !== 'string') return false;
    
    // Verifica se tem o formato DD/MM/YYYY
    const dateRegex = /^\d{2}\/\d{2}\/\d{4}$/;
    if (!dateRegex.test(dateStr)) return false;
    
    try {
        const [day, month, year] = dateStr.split('/').map(Number);
        
        // Validações básicas
        if (day < 1 || day > 31) return false;
        if (month < 1 || month > 12) return false;
        if (year < 1900 || year > 2100) return false;
        
        // Cria a data e verifica se é válida
        const date = new Date(year, month - 1, day);
        return date.getDate() === day && 
               date.getMonth() === month - 1 && 
               date.getFullYear() === year;
    } catch {
        return false;
    }
}

/** Valida se uma string é uma data válida no formato ISO (YYYY-MM-DD) */
export function isValidISODate(dateStr: string): boolean {
    if (!dateStr || typeof dateStr !== 'string') return false;
    
    // Verifica se tem o formato YYYY-MM-DD
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(dateStr)) return false;
    
    try {
        const [year, month, day] = dateStr.split('-').map(Number);
        
        // Validações básicas
        if (day < 1 || day > 31) return false;
        if (month < 1 || month > 12) return false;
        if (year < 1900 || year > 2100) return false;
        
        // Cria a data e verifica se é válida
        const date = new Date(year, month - 1, day);
        return date.getDate() === day && 
               date.getMonth() === month - 1 && 
               date.getFullYear() === year;
    } catch {
        return false;
    }
}

/** Converte e valida uma data brasileira para ISO, retornando null se inválida */
export function safeFormatBrazilianDateToISO(brazilianDate: string): string | null {
    if (!brazilianDate || typeof brazilianDate !== 'string') return null;
    
    // Se já está no formato ISO e é válida, retorna como está
    if (brazilianDate.includes('-') && isValidISODate(brazilianDate)) {
        return brazilianDate;
    }
    
    // Se está no formato brasileiro e é válida, converte
    if (brazilianDate.includes('/') && isValidBrazilianDate(brazilianDate)) {
        return formatBrazilianDateToISO(brazilianDate);
    }
    
    return null;
}
  