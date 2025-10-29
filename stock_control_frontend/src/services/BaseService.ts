// services/BaseService.ts - Classe base para serviços
import api from './api';
import type { Paginated } from '@/types/api';
import type { BaseFilter } from '@/types/common';

/**
 * Classe base para serviços com funcionalidades comuns de CRUD
 * 
 * @template T - Tipo da entidade
 * @template CreateData - Tipo dos dados para criação
 * @template UpdateData - Tipo dos dados para atualização
 * @template Filters - Tipo dos filtros (deve estender BaseFilter)
 * 
 * @example
 * class UserService extends BaseService<User, CreateUserData, UpdateUserData, UserFilters> {
 *   constructor() {
 *     super('/api/users');
 *   }
 * }
 */
export abstract class BaseService<
  T, 
  CreateData = Partial<T>, 
  UpdateData = Partial<T>, 
  Filters extends BaseFilter = BaseFilter
> {
  protected baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * Lista todos os itens com paginação e filtros
   * 
   * @param page - Número da página (começa em 1)
   * @param filters - Filtros a serem aplicados (opcional)
   * @returns Promise com dados paginados
   * 
   * @throws {Error} Se houver erro na requisição
   */
  async getAll(page = 1, filters: Partial<Filters> = {}): Promise<Paginated<T>> {
    try {
      const params = new URLSearchParams();
      
      // Adiciona o parâmetro de página
      params.append('page', page.toString());
      
      // Adiciona filtros aos parâmetros
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          params.append(key, String(value));
        }
      });

      const url = `${this.baseUrl}/?${params.toString()}`;
      const response = await api.get<Paginated<T>>(url);
      return response.data;
    } catch (error) {
      console.error(`Erro ao buscar ${this.baseUrl}:`, error);
      throw error;
    }
  }

  /**
   * Busca um item por ID
   * 
   * @param id - ID do item a ser buscado
   * @returns Promise com o item encontrado
   * 
   * @throws {Error} Se o item não for encontrado ou houver erro na requisição
   */
  async getById(id: string | number): Promise<T> {
    try {
      const response = await api.get<T>(`${this.baseUrl}/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Erro ao buscar item ${id}:`, error);
      throw error;
    }
  }

  /**
   * Cria um novo item
   * 
   * @param data - Dados para criação do item
   * @returns Promise com o item criado
   * 
   * @throws {Error} Se houver erro de validação ou na requisição
   */
  async create(data: CreateData): Promise<T> {
    try {
      const response = await api.post<T>(`${this.baseUrl}/`, data);
      return response.data;
    } catch (error) {
      console.error(`Erro ao criar item:`, error);
      throw error;
    }
  }

  /**
   * Atualiza um item existente (PUT - substitui todos os campos)
   * 
   * @param id - ID do item a ser atualizado
   * @param data - Dados completos para atualização
   * @returns Promise com o item atualizado
   * 
   * @throws {Error} Se o item não for encontrado ou houver erro na requisição
   */
  async update(id: string | number, data: UpdateData): Promise<T> {
    try {
      const response = await api.put<T>(`${this.baseUrl}/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error(`Erro ao atualizar item ${id}:`, error);
      throw error;
    }
  }

  /**
   * Atualiza parcialmente um item (PATCH - atualiza apenas campos fornecidos)
   * 
   * @param id - ID do item a ser atualizado
   * @param data - Dados parciais para atualização
   * @returns Promise com o item atualizado
   * 
   * @throws {Error} Se o item não for encontrado ou houver erro na requisição
   */
  async patch(id: string | number, data: Partial<UpdateData>): Promise<T> {
    try {
      const response = await api.patch<T>(`${this.baseUrl}/${id}/`, data);
      return response.data;
    } catch (error) {
      console.error(`Erro ao atualizar parcialmente item ${id}:`, error);
      throw error;
    }
  }

  /**
   * Remove um item
   * 
   * @param id - ID do item a ser removido
   * @returns Promise vazia (void)
   * 
   * @throws {Error} Se o item não for encontrado ou houver erro na requisição
   */
  async delete(id: string | number): Promise<void> {
    try {
      await api.delete(`${this.baseUrl}/${id}/`);
    } catch (error) {
      console.error(`Erro ao deletar item ${id}:`, error);
      throw error;
    }
  }

  /**
   * Busca itens usando termo de pesquisa
   * 
   * @param term - Termo de pesquisa
   * @returns Promise com lista de itens encontrados
   * 
   * @throws {Error} Se houver erro na requisição
   */
  async search(term: string): Promise<T[]> {
    try {
      const response = await api.get<Paginated<T> | T[]>(`${this.baseUrl}/?search=${encodeURIComponent(term)}`);
      // Verifica se a resposta é paginada ou uma lista direta
      return 'results' in response.data ? response.data.results : response.data as T[];
    } catch (error) {
      console.error(`Erro ao buscar ${this.baseUrl}:`, error);
      throw error;
    }
  }
}
