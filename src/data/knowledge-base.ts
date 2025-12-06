export type CompanyId = 'azul' | 'iberia' | 'groundforce' | 'swissport' | 'menzies' | 'wfs' | 'clece' | 'acciona' | 'aviapartner';

export interface Company {
    id: CompanyId;
    name: string;
    color: string; // Hex color for branding
}

export const companies: Company[] = [
    { id: 'azul', name: 'Azul Handling', color: '#004481' },
    { id: 'iberia', name: 'Iberia', color: '#D7192D' },
    { id: 'groundforce', name: 'Groundforce', color: '#0033A0' },
    { id: 'swissport', name: 'Swissport', color: '#FF6600' },
    { id: 'menzies', name: 'Menzies', color: '#2B3E50' },
    { id: 'wfs', name: 'WFS', color: '#E31837' },
];

export interface KnowledgeItem {
    id: string;
    category: string; // e.g. 'Convenio Azul Handling', 'Estatuto Trabajadores'
    topic: string;
    content: string;
    keywords: string[];
    scope: 'global' | 'company';
    companyId?: CompanyId; // Optional, only if scope is 'company'
}

export const knowledgeBase: KnowledgeItem[] = [
    // --- GLOBAL (Estatuto & Sectorial) ---
    {
        id: 'et-despido',
        category: 'Estatuto Trabajadores',
        topic: 'Despido Improcedente',
        content: 'En caso de despido improcedente, la indemnización será de 33 días de salario por año de servicio, prorrateándose por meses los periodos de tiempo inferiores a un año, hasta un máximo de 24 mensualidades.',
        keywords: ['despido', 'echado', 'fin contrato', 'indemnización'],
        scope: 'global'
    },
    {
        id: 'et-permiso-familiar',
        category: 'Estatuto Trabajadores',
        topic: 'Permiso por Enfermedad Familiar',
        content: 'Tendrás derecho a 5 días laborables de permiso retribuido por accidente o enfermedad graves, hospitalización o intervención quirúrgica sin hospitalización que precise reposo domiciliario del cónyuge, pareja de hecho o parientes hasta el segundo grado (padres, hijos, abuelos, hermanos, nietos).',
        keywords: ['permiso', 'enfermedad', 'malo', 'hospital', 'operación', 'padre', 'madre', 'hijo', 'familiar', 'ingresado'],
        scope: 'global'
    },
    {
        id: 'et-permiso-alta',
        category: 'Estatuto Trabajadores',
        topic: 'Fin del Permiso por Alta Médica',
        content: 'El permiso retribuido está vinculado al hecho causante (la enfermedad o hospitalización). Si dan el alta médica al familiar y no requiere reposo domiciliario, el permiso finaliza, aunque no hayas gastado los 5 días. El permiso es para el cuidado efectivo, no son días libres fijos si ya no hay necesidad.',
        keywords: ['alta', 'curado', 'casa', 'segundo día', 'recuperado', 'vuelve', 'hospital', 'y si'],
        scope: 'global'
    },
    {
        id: 'common-prl',
        category: 'Ley Prevención Riesgos (PRL)',
        topic: 'Derecho a la Protección',
        content: 'Los trabajadores tienen derecho a una protección eficaz en materia de seguridad y salud en el trabajo. El empresario tiene el deber de proteger a los trabajadores frente a los riesgos laborales.',
        keywords: ['seguridad', 'riesgos', 'protección', 'salud', 'prl', 'epi', 'epis'],
        scope: 'global'
    },

    // --- AZUL HANDLING ---
    {
        id: 'azul-vacaciones',
        category: 'Convenio Azul Handling',
        topic: 'Vacaciones (Azul)',
        content: 'En Azul Handling, el personal tendrá derecho a 30 días naturales de vacaciones anuales retribuidas.',
        keywords: ['vacaciones', 'días libres', 'descanso'],
        scope: 'company',
        companyId: 'azul'
    },
    {
        id: 'azul-jornada',
        category: 'Convenio Azul Handling',
        topic: 'Jornada Laboral (Azul)',
        content: 'La jornada laboral ordinaria en Azul Handling será de 1712 horas anuales de trabajo efectivo.',
        keywords: ['jornada', 'horas', 'horario', 'trabajo'],
        scope: 'company',
        companyId: 'azul'
    },
    {
        id: 'azul-tablas',
        category: 'Convenio Azul Handling',
        topic: 'Tablas Salariales (Azul)',
        content: 'Las tablas salariales de Azul Handling para 2025 establecen un incremento del 2.5% sobre el salario base.',
        keywords: ['sueldo', 'salario', 'cobrar', 'dinero', 'aumento'],
        scope: 'company',
        companyId: 'azul'
    },


    // --- IBERIA (Datos Simulados / Ejemplo) ---
    {
        id: 'iberia-vacaciones',
        category: 'Convenio Iberia',
        topic: 'Vacaciones (Iberia)',
        content: 'En Iberia Tierra, las vacaciones pueden fraccionarse hasta en tres periodos, garantizando siempre 15 días en periodo estival (junio-septiembre).',
        keywords: ['vacaciones', 'días libres', 'verano'],
        scope: 'company',
        companyId: 'iberia'
    },
    {
        id: 'iberia-billetes',
        category: 'Convenio Iberia',
        topic: 'Billetes con Descuento',
        content: 'El personal de Iberia con más de 6 meses de antigüedad tiene acceso a billetes con descuento (ID90/ID50) en vuelos del grupo.',
        keywords: ['vuelo', 'viajar', 'gratis', 'descuento', 'billete', 'avion'],
        scope: 'company',
        companyId: 'iberia'
    },

    // --- GROUNDFORCE (Datos Simulados / Ejemplo) ---
    {
        id: 'gf-jornada',
        category: 'Convenio Groundforce',
        topic: 'Jornada Laboral (Groundforce)',
        content: 'La jornada anual en Groundforce se establece en 1720 horas, con especial atención a la distribución irregular en temporada alta.',
        keywords: ['jornada', 'horas', 'horario'],
        scope: 'company',
        companyId: 'groundforce'
    }
];
