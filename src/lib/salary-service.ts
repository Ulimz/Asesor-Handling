import { API_URL as BASE_URL } from '@/config/api';

const API_URL = `${BASE_URL}/api`;

export interface ConceptSchema {
    name: string;
    code: string;
    description?: string;
    input_type: string;
    default_price: number;
}

export const SalaryService = {
    async getCompanies(): Promise<string[]> {
        const res = await fetch(`${API_URL}/calculadoras/metadata/companies`);
        if (!res.ok) return [];
        return res.json();
    },

    async getGroups(companyId: string): Promise<string[]> {
        const res = await fetch(`${API_URL}/calculadoras/metadata/${companyId}/groups`);
        if (!res.ok) return [];
        return res.json();
    },

    async getLevels(companyId: string, groupId: string): Promise<string[]> {
        const res = await fetch(`${API_URL}/calculadoras/metadata/${companyId}/${groupId}/levels`);
        if (!res.ok) return [];
        return res.json();
    },

    async getConcepts(companySlug: string): Promise<ConceptSchema[]> {
        const res = await fetch(`${API_URL}/calculadoras/concepts/${companySlug}`);
        if (!res.ok) return [];
        return res.json();
    }
};
