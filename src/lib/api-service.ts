import { API_URL } from '@/config/api';

export interface User {
    id: number;
    email: string;
    full_name: string;
    preferred_name?: string;
    company_slug?: string;
    job_group?: string;
    salary_level?: string;
    contract_type?: string;
    seniority_date?: string;
    is_active: boolean;
}

export interface UserContext {
    job_group?: string;
    salary_level?: string;
    contract_type?: string;
    preferred_name?: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
}

// Assuming Message and SearchResult are defined elsewhere or need to be added.
// For the purpose of this edit, I'll add minimal definitions to make the code syntactically valid.
interface Message {
    role: string;
    content: string;
}

type CompanyId = string | number; // Assuming CompanyId can be string or number

interface SearchResult {
    // Define properties of SearchResult based on API response
    // e.g., results: any[];
}

export async function askAI(messages: Message[], companyId?: CompanyId, userContext?: UserContext): Promise<SearchResult> {
    try {
        // Extract current query and history
        const query = messages[messages.length - 1].content;
        const history = messages.slice(0, -1).map(m => ({
            role: m.role,
            content: m.content
        }));

        const res = await fetch(`${API_URL}/api/articulos/search/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query,
                history,
                company_slug: companyId,
                user_context: userContext
            })
        });

        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || 'Error en la consulta a la IA');
        }
        return res.json();
    } catch (error) {
        console.error("Error calling askAI:", error);
        throw error;
    }
}


export const apiService = {
    async login(username: string, password: string): Promise<LoginResponse> {
        const response = await fetch(`${API_URL}/api/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ username, password }),
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || 'Error en inicio de sesión');
        }
        return response.json();
    },

    async getMe(token: string): Promise<User> {
        const response = await fetch(`${API_URL}/api/users/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Error obteniendo perfil');
        return response.json();
    },

    async getCompanies(): Promise<any[]> {
        const response = await fetch(`${API_URL}/api/companies`);
        if (!response.ok) throw new Error('Error obteniendo empresas');
        return response.json();
    },

    async updateProfile(token: string, data: Partial<User>): Promise<User> {
        const response = await fetch(`${API_URL}/api/users/profile`, {
            method: 'PUT',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) throw new Error('Error actualizando perfil');
        return response.json();
    },

    async deleteAccount(token: string): Promise<void> {
        const response = await fetch(`${API_URL}/api/users/me`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) throw new Error('Error eliminando cuenta');
    },

    profiles: {
        async getAll(token: string) {
            const res = await fetch(`${API_URL}/api/users/me/profiles`, {
                headers: { 'Authorization': `Bearer ${token}` },
                cache: 'no-store'
            });
            if (!res.ok) throw new Error('Failed to fetch profiles');
            return res.json();
        },
        async create(token: string, data: any) {
            const res = await fetch(`${API_URL}/api/users/me/profiles`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
                cache: 'no-store'
            });
            if (!res.ok) throw new Error('Failed to create profile');
            return res.json();
        },
        async update(token: string, id: number, data: any) {
            const res = await fetch(`${API_URL}/api/users/me/profiles/${id}`, {
                method: 'PUT',
                headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
                cache: 'no-store'
            });
            if (!res.ok) throw new Error('Failed to update profile');
            return res.json();
        },
        async delete(token: string, id: number) {
            const res = await fetch(`${API_URL}/api/users/me/profiles/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` },
                cache: 'no-store'
            });
            if (!res.ok) throw new Error('Failed to delete profile');
        },
        async activate(token: string, id: number) {
            const res = await fetch(`${API_URL}/api/users/me/profiles/${id}/activate`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` },
                cache: 'no-store'
            });
            if (!res.ok) throw new Error('Failed to activate profile');
            return res.json();
        }
    }
};
