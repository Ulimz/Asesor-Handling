import Image from 'next/image';

interface BrandLogoProps {
    className?: string;
    iconSize?: number;
    textSize?: 'xs' | 'sm' | 'md' | 'lg' | 'xl' | '2xl';
}

export default function BrandLogo({ className = '', iconSize = 64, textSize = 'xl' }: BrandLogoProps) {
    // Map textSize to font size classes and tracking
    const textClasses = {
        'xs': 'text-[10px] tracking-[0.1em]',
        'sm': 'text-sm tracking-[0.15em]',
        'md': 'text-base tracking-[0.15em]',
        'lg': 'text-lg tracking-[0.2em]',
        'xl': 'text-xl tracking-[0.2em]',
        '2xl': 'text-2xl tracking-[0.2em]',
    };

    return (
        <div className={`flex items-center gap-0 ${className}`}>
            <div className="relative flex-shrink-0" style={{ width: iconSize, height: iconSize * 0.75 }}>
                <Image
                    src="/Logo.png"
                    alt="Asistente Handling Logo"
                    fill
                    className="object-contain"
                />
            </div>
            <div className="flex flex-col leading-none">
                <span className={`${textClasses[textSize]} font-bold text-[var(--text-primary)] drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] dark:drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] drop-shadow-none`}>
                    AS<span className="text-cyan-400 drop-shadow-[0_0_5px_rgba(34,211,238,0.8)]">I</span>STENTE
                </span>
                <span className={`${textClasses[textSize]} font-bold text-[var(--text-primary)] drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] dark:drop-shadow-[0_0_5px_rgba(255,255,255,0.3)] drop-shadow-none`}>
                    H<span className="text-cyan-400 drop-shadow-[0_0_5px_rgba(34,211,238,0.8)]">A</span>NDLING
                </span>
            </div>
        </div>
    );
}
