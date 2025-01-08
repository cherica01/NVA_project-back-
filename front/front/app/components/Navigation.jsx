'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const Navigation = () => {
  const pathname = usePathname()
  const isAdmin = pathname.startsWith('/admin')

  return (
    <nav className="bg-blue-600 p-4 text-white">
      <div className="container mx-auto flex justify-between items-center">
        <Link href="/" className="text-2xl font-bold">
          Gestion des Agents
        </Link>
        <div className="space-x-4">
          {isAdmin ? (
            <>
              <Link href="/admin/agents" className="hover:text-blue-200">Agents</Link>
              <Link href="/admin/paies" className="hover:text-blue-200">Paies</Link>
              <Link href="/admin/presences" className="hover:text-blue-200">Présences</Link>
              <Link href="/admin/evenements" className="hover:text-blue-200">Événements</Link>
            </>
          ) : (
            <>
              <Link href="/agent/agenda" className="hover:text-blue-200">Agenda</Link>
              <Link href="/agent/messages" className="hover:text-blue-200">Messages</Link>
              <Link href="/agent/notifications" className="hover:text-blue-200">Notifications</Link>
              <Link href="/agent/profil" className="hover:text-blue-200">Profil</Link>
              <Link href="/agent/wallet" className="hover:text-blue-200">Wallet</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navigation

