'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function AdminPresences() {
  const [presences, setPresences] = useState([
    { id: 1, agentId: 1, agentNom: 'Jean Dupont', date: '2023-06-01', status: 'En attente' },
    { id: 2, agentId: 2, agentNom: 'Marie Martin', date: '2023-06-01', status: 'Validée' },
  ])

  const validatePresence = (id) => {
    setPresences(presences.map(presence => 
      presence.id === id ? {...presence, status: 'Validée'} : presence
    ))
  }

  const refusePresence = (id) => {
    setPresences(presences.map(presence => 
      presence.id === id ? {...presence, status: 'Refusée'} : presence
    ))
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Gestion des Présences</h1>

      <Table>
        <TableCaption>Liste des présences</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Agent</TableHead>
            <TableHead>Date</TableHead>
            <TableHead>Statut</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {presences.map((presence) => (
            <TableRow key={presence.id}>
              <TableCell>{presence.agentNom}</TableCell>
              <TableCell>{presence.date}</TableCell>
              <TableCell>{presence.status}</TableCell>
              <TableCell>
                {presence.status === 'En attente' && (
                  <>
                    <Button onClick={() => validatePresence(presence.id)} className="mr-2">Valider</Button>
                    <Button variant="destructive" onClick={() => refusePresence(presence.id)}>Refuser</Button>
                  </>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

