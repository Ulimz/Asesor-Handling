import React from 'react';

export default function NeonLogo({ className = "w-48 h-24" }: { className?: string }) {
    return (
        <div className={`relative flex items-center justify-center ${className}`}>
            <svg
                viewBox="0 0 300 180"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
                className="w-full h-full drop-shadow-[0_0_15px_rgba(34,211,238,0.5)]"
            >
                <defs>
                    <linearGradient id="neonGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stopColor="#22d3ee" />   {/* Cyan-400 */}
                        <stop offset="50%" stopColor="#3b82f6" />   {/* Blue-500 */}
                        <stop offset="100%" stopColor="#22d3ee" /> {/* Cyan-400 */}
                    </linearGradient>

                    <filter id="glow">
                        <feGaussianBlur stdDeviation="2.5" result="coloredBlur" />
                        <feMerge>
                            <feMergeNode in="coloredBlur" />
                            <feMergeNode in="SourceGraphic" />
                        </feMerge>
                    </filter>
                </defs>

                {/* --- TAIL FIN SHAPE (Vertical Stabilizer) --- */}
                {/* Trapezoidal swept-back shape typical of commercial airliners */}
                <path
                    d="M 90 145 L 145 25 L 205 25 L 185 145 Z"
                    stroke="url(#neonGradient)"
                    strokeWidth="3"
                    fill="rgba(34, 211, 238, 0.05)"
                    strokeLinejoin="round"
                />

                {/* --- INNER DOCUMENT LINES (stylized) --- */}
                {/* Adapted to fit the swept-back fin shape */}
                <line x1="120" y1="55" x2="180" y2="55" stroke="#3b82f6" strokeWidth="1" strokeOpacity="0.5" />
                <line x1="115" y1="75" x2="185" y2="75" stroke="#3b82f6" strokeWidth="1" strokeOpacity="0.5" />
                <line x1="110" y1="95" x2="190" y2="95" stroke="#3b82f6" strokeWidth="1" strokeOpacity="0.5" />
                <line x1="105" y1="115" x2="185" y2="115" stroke="#3b82f6" strokeWidth="1" strokeOpacity="0.5" />

                {/* --- MAIN TEXT "AH" --- */}
                <text
                    x="148"
                    y="110"
                    textAnchor="middle"
                    fontFamily="sans-serif"
                    fontWeight="bold"
                    fontSize="55"
                    fill="transparent"
                    stroke="#e0f2fe"
                    strokeWidth="2"
                    style={{ letterSpacing: '2px', filter: 'drop-shadow(0 0 5px #22d3ee)' }}
                >
                    AH
                </text>

                {/* --- MAGNIFYING GLASS ICON (Search Loop) --- */}
                <circle cx="175" cy="65" r="12" stroke="#22d3ee" strokeWidth="2" fill="none" />
                <line x1="184" y1="74" x2="194" y2="84" stroke="#22d3ee" strokeWidth="3" strokeLinecap="round" />

                {/* --- BOTTOM TEXT "Asistente Handling IA" --- */}
                <text
                    x="140"
                    y="165"
                    textAnchor="middle"
                    fontFamily="sans-serif"
                    fontWeight="600"
                    fontSize="14"
                    fill="#e0f2fe"
                    style={{ letterSpacing: '1px', textTransform: 'uppercase' }}
                >
                    Asistente Handling IA
                </text>

            </svg>
        </div>
    );
}
