'use client';

import { ProfileProvider } from '@/context/ProfileContext';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <ProfileProvider>
            {children}
        </ProfileProvider>
    );
}
