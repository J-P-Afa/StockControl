/**
 * Serviço centralizado de logging com níveis de log configuráveis.
 * Em produção, apenas logs de erro são exibidos.
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  NONE = 4
}

class Logger {
  private level: LogLevel
  private isProduction: boolean

  constructor() {
    this.isProduction = import.meta.env.PROD
    // Em produção, mostrar apenas erros; em desenvolvimento, mostrar tudo
    this.level = this.isProduction ? LogLevel.ERROR : LogLevel.DEBUG
  }

  /**
   * Define o nível mínimo de log a ser exibido
   */
  setLevel(level: LogLevel): void {
    this.level = level
  }

  /**
   * Log de debug - apenas em desenvolvimento
   */
  debug(message: string, ...args: any[]): void {
    if (this.level <= LogLevel.DEBUG) {
      console.log(`[DEBUG] ${message}`, ...args)
    }
  }

  /**
   * Log de informação
   */
  info(message: string, ...args: any[]): void {
    if (this.level <= LogLevel.INFO) {
      console.info(`[INFO] ${message}`, ...args)
    }
  }

  /**
   * Log de aviso
   */
  warn(message: string, ...args: any[]): void {
    if (this.level <= LogLevel.WARN) {
      console.warn(`[WARN] ${message}`, ...args)
    }
  }

  /**
   * Log de erro - sempre mostrado
   */
  error(message: string, ...args: any[]): void {
    if (this.level <= LogLevel.ERROR) {
      console.error(`[ERROR] ${message}`, ...args)
    }
  }

  /**
   * Agrupa logs relacionados
   */
  group(label: string): void {
    if (!this.isProduction) {
      console.group(label)
    }
  }

  /**
   * Finaliza grupo de logs
   */
  groupEnd(): void {
    if (!this.isProduction) {
      console.groupEnd()
    }
  }

  /**
   * Cria uma instância de logger com contexto específico
   */
  createContextLogger(context: string) {
    return {
      debug: (message: string, ...args: any[]) => this.debug(`[${context}] ${message}`, ...args),
      info: (message: string, ...args: any[]) => this.info(`[${context}] ${message}`, ...args),
      warn: (message: string, ...args: any[]) => this.warn(`[${context}] ${message}`, ...args),
      error: (message: string, ...args: any[]) => this.error(`[${context}] ${message}`, ...args),
      group: (label: string) => this.group(`[${context}] ${label}`),
      groupEnd: () => this.groupEnd()
    }
  }
}

// Instância singleton do logger
export const logger = new Logger()

// Função helper para criar loggers com contexto
export const createLogger = (context: string) => logger.createContextLogger(context)










