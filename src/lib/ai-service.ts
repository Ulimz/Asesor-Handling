import { CompanyId } from '@/data/knowledge-base';
import { Article } from '@/data/documents/types';

interface SearchResult {
    answer: string;
    sources: { category: string; topic: string; content: string }[];
}

interface ApiHit {
    id: string;
    title: string;
    content: string;
    tags: string[];
    score: number;
    company_slug: string | null;
}

export async function askAI(query: string, companyId?: CompanyId): Promise<SearchResult> {
    try {
        // Construir URL con parámetros
        const params = new URLSearchParams({ q: query });
        if (companyId) {
            params.append('company_slug', companyId);
        }

        // Llamada al Backend
        const res = await fetch(`/api/articulos/search?${params.toString()}`);

        if (!res.ok) {
            throw new Error(`Error del servidor: ${res.statusText}`);
        }

        const data = await res.json();
        const hits: ApiHit[] = data.results || [];

        if (hits.length === 0) {
            return {
                answer: "Lo siento, he consultado la base de datos de normas y convenios, pero no encuentro información relevante para tu consulta.",
                sources: []
            };
        }

        // Tomar el mejor resultado (Top 1)
        const bestMatch = hits[0];

        // Construir respuesta
        // (En el futuro, esto se pasaría a un LLM para generar texto natural)
        return {
            answer: `He encontrado información relevante en el ${bestMatch.company_slug ? 'Convenio de ' + bestMatch.company_slug.toUpperCase() : 'Estatuto'}:\n\n"${bestMatch.content}"`,
            sources: hits.slice(0, 3).map(hit => ({
                category: hit.company_slug ? `Convenio ${hit.company_slug}` : 'Normativa General',
                topic: hit.title,
                content: hit.content
            }))
        };

    } catch (error) {
        console.error("Error en askAI:", error);
        return {
            answer: "Lo siento, ha ocurrido un error al conectar con el servidor de inteligencia legal. Por favor inténtalo de nuevo.",
            sources: []
        };
    }
}
