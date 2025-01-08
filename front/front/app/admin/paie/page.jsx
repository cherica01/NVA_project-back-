'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function AdminPaies() {
  const [paies, setPaies] = useState([
    { id: 1, agentId: 1, agentNom: 'Jean Dupont', joursTravailles: 20, montant: 2000 },
    { id: 2, agentId: 2, agentNom: 'Marie Martin', joursTravailles: 22, montant: 2200 },
  ])

  const exportToExcel = () => {
    // Logique d'exportation vers Excel à implémenter
    console.log('Exporting to Excel...')
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Gestion des Paies</h1>
      
      <Button onClick={exportToExcel}>Exporter vers Excel</Button>

      <Table>
        <TableCaption>Liste des paies</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Agent</TableHead>
            <TableHead>Jours travaillés</TableHead>
            <TableHead>Montant</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {paies.map((paie) => (
            <TableRow key={paie.id}>
              <TableCell>{paie.agentNom}</TableCell>
              <TableCell>{paie.joursTravailles}</TableCell>
              <TableCell>{paie.montant} €</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

