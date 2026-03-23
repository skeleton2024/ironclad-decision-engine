import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Ironclad Decision Engine',
  description: '对抗式理性决策引擎',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh">
      <body>{children}</body>
    </html>
  );
}
