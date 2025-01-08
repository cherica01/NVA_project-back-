import '@/app/globals.css'
import { Inter } from 'next/font/google'
import Navigation from './components/Navigation'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'Gestion des Agents',
  description: 'Application de gestion des agents',
}

export default function RootLayout({ children }) {
  return (
    <html lang="fr">
      <body className={inter.className}>
        <Navigation />
        <main className="container mx-auto mt-4 p-4">
          {children}
        </main>
      </body>
    </html>
  )
}

