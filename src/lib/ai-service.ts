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
        const res = await fetch(`/api/articulos/search/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query,
                company_slug: companyId
            })
        });

        if (!res.ok) {
            throw new Error(`Error del servidor: ${res.statusText}`);
        }

        const data = await res.json();

        return {
            answer: data.answer,
            sources: data.sources.map((hit: any) => ({
                category: hit.document_id || 'Documentación General',
                topic: hit.article_ref || 'Referencia',
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
