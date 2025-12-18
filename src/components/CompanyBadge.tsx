import { companies, CompanyId } from '@/data/knowledge-base';
import { Building2 } from 'lucide-react';

interface CompanyBadgeProps {
    companyId: CompanyId | null;
    showName?: boolean;
    className?: string;
}

export default function CompanyBadge({ companyId, showName = true, className = '' }: CompanyBadgeProps) {
    const company = companies.find(c => c.id === companyId);

    return (
        <div className={`flex items-center gap-3 ${className}`}>
            <div
                className="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm shadow-[0_0_10px_rgba(0,0,0,0.2)] border border-white/10 shrink-0"
                style={{ backgroundColor: company ? company.color : '#334155' }}
            >
                {company ? company.name.charAt(0) : <Building2 size={16} />}
            </div>
            {showName && (
                <div className="flex flex-col">
                    <span className="text-sm font-semibold text-slate-200">
                        {company ? company.name : 'Sin Empresa'}
                    </span>
                    <span className="text-[10px] text-slate-400 uppercase tracking-wide">
                        {company ? (company.agreementLabel || 'Convenio Activo') : 'Requerido'}
                    </span>
                </div>
            )}
        </div>
    );
}
