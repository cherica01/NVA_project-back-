import Link from 'next/link'
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen py-2">
      <main className="flex flex-col items-center justify-center w-full flex-1 px-20 text-center">
        <h1 className="text-6xl font-bold">
          Bienvenue sur l'application de Gestion des Agents
        </h1>
        <p className="mt-3 text-2xl">
          Connectez-vous pour commencer
        </p>
        <div className="mt-6">
          <Link href="/login">
            <Button>Se connecter</Button>
          </Link>
        </div>
      </main>
    </div>
  )
}

