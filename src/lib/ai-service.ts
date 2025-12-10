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

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export async function askAI(messages: Message[], companyId?: CompanyId): Promise<SearchResult> {
    try {
        // Extract current query and history
        const query = messages[messages.length - 1].content;
        const history = messages.slice(0, -1).map(m => ({
            role: m.role,
            content: m.content
        }));

        const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
        const res = await fetch(`${API_URL}/api/articulos/search/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query,
                history,
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
        if (process.env.NODE_ENV !== 'production') {
            console.error("Error en askAI:", error);
        }
        return {
            answer: "Lo siento, ha ocurrido un error al conectar con el servidor de inteligencia legal. Por favor inténtalo de nuevo.",
            sources: []
        };
    }
}
