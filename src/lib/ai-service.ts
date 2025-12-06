import { CompanyId } from '@/data/knowledge-base';
import { Article } from '@/data/documents/types';

import globalEstatuto from '@/data/documents/global-estatuto.json';
import companyAzul from '@/data/documents/company-azul.json';
import companyIberia from '@/data/documents/company-iberia.json';
import companyGroundforce from '@/data/documents/company-groundforce.json';

interface SearchResult {
    answer: string;
    sources: { category: string; topic: string; content: string }[];
}

// Mapa de documentos por empresa
const COMPANY_DOCS: Record<string, Article[]> = {
    azul: companyAzul,
    iberia: companyIberia,
    groundforce: companyGroundforce,
};

// Función helper para normalizar (quitar tildes y minúsculas)
function normalize(text: string): string {
    return text.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function calculateRelevance(text: string, queryTerms: string[]): number {
    const normalizedText = normalize(text);
    let score = 0;

    queryTerms.forEach(term => {
        // Puntos por coincidencia parcial (covers plurales simples)
        if (normalizedText.includes(term)) {
            score += 1;
            // Puntos extra si es coincidencia "perfecta" (palabra completa)
            // Para simplificar, si el término es largo y está incluido, damos más puntos
            if (term.length > 3) score += 1;
        }
    });

    return score;
}

export async function askAI(query: string, companyId?: CompanyId): Promise<SearchResult> {
    // Simulación de retraso de red
    await new Promise(resolve => setTimeout(resolve, 800));

    // 1. Preparar términos de búsqueda
    const stopWords = ['el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'a', 'ante', 'con', 'en', 'para', 'por', 'y', 'o', 'que', 'si', 'mi', 'tu', 'su', 'es', 'son', 'al'];

    let normalizedQuery = normalize(query)
        .replace(/[¿?¡!.,]/g, '')
        .trim();

    // Expansión de sinónimos
    if (includesAny(normalizedQuery, ['malo', 'enfermo', 'hospital', 'padre', 'madre'])) {
        normalizedQuery += ' enfermedad permiso familiar reposo alta';
    }
    if (includesAny(normalizedQuery, ['echan', 'botan', 'despedido'])) {
        normalizedQuery += ' despido improcedente finiquito';
    }
    if (includesAny(normalizedQuery, ['vacaciones', 'dias libres'])) {
        normalizedQuery += ' descanso anual natural';
    }

    // Permitimos palabras > 2 letras O números (para capturar "11", "333")
    const queryTerms = normalizedQuery.split(/\s+/).filter(w => !stopWords.includes(w) && (w.length > 2 || !isNaN(Number(w))));

    // 2. Recopilar todos los documentos válidos
    let allArticles: (Article & { sourceName: string })[] = [];

    // Agregar Estatuto (Global)
    allArticles = allArticles.concat(globalEstatuto.map(a => ({ ...a, sourceName: 'Estatuto de los Trabajadores / Jurisprudencia' })));

    // Agregar documento de empresa
    if (companyId && COMPANY_DOCS[companyId]) {
        const companyName = companyId.charAt(0).toUpperCase() + companyId.slice(1);
        allArticles = allArticles.concat(COMPANY_DOCS[companyId].map(a => ({ ...a, sourceName: `Convenio ${companyName}` })));
    }

    // 3. Ranking de artículos
    const scoredArticles = allArticles.map(article => {
        const contentScore = calculateRelevance(article.content, queryTerms);
        // Título normalizado para score
        let titleScore = calculateRelevance(article.title, queryTerms) * 2;
        const tagScore = article.tags
            ? calculateRelevance(article.tags.join(' '), queryTerms) * 1.5
            : 0;

        // BOOST: Prioridad a Jurisprudencia y alertas de Fraude
        if (normalize(article.title).includes('jurisprudencia') || article.tags?.some(tag => normalize(tag).includes('fraude'))) {
            titleScore *= 3;
        }

        // PENALIZACIÓN CONTEXTUAL:
        // Si preguntan por 'máximo' o 'más de', penalizamos garantías mínimas
        let penalty = 0;
        if (normalizedQuery.includes('maximo') || normalizedQuery.includes('mas de') || normalizedQuery.includes('limite')) {
            if (normalize(article.title).includes('garantia')) penalty = 5; // Penalización fuerte
        }

        return {
            article,
            score: contentScore + titleScore + tagScore - penalty
        };
    });

    // Ordenar por relevancia descendente
    scoredArticles.sort((a, b) => b.score - a.score);

    const bestMatch = scoredArticles[0];

    // Debug scoring (invisible en producción pero útil si persistiera el error)
    // console.log(scoredArticles.map(a => `${a.article.id}: ${a.score}`).slice(0,3));

    if (!bestMatch || bestMatch.score < 1) {
        return {
            answer: "Lo siento, he leído los documentos de tu empresa y el Estatuto, pero no encuentro ningún artículo que hable específicamente de eso.",
            sources: []
        };
    }

    return {
        answer: `He encontrado esto en la normativa:\n\n"${bestMatch.article.content}"`,
        sources: [{
            category: bestMatch.article.sourceName,
            topic: bestMatch.article.title,
            content: bestMatch.article.content
        }]
    };
}

function includesAny(text: string, terms: string[]): boolean {
    return terms.some(t => text.includes(t));
}
