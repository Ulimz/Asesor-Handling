export interface Article {
    id: string;      // Identificador único del artículo, ej: 'art-37', 'cap-5'
    title: string;   // Título descriptivo, ej: 'Artículo 37. Descanso semanal, fiestas y permisos'
    content: string; // Texto completo del artículo
    tags?: string[]; // Etiquetas opcionales para ayudar a la búsqueda
}

export interface LegalDocument {
    id: string;               // ID del documento, ej: 'estatuto-trabajadores', 'conv-groundforce'
    title: string;            // Título oficial
    scope: 'global' | 'company';
    companyId?: string;       // ID de la empresa si el scope es 'company'
    articles: Article[];
}
