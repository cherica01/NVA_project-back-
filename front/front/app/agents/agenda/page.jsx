'use client'

import { useState } from 'react'
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function AgentAgenda() {
  const [evenements, setEvenements] = useState([
    { id: 1, date: '2023-06-15', lieu: 'Paris', societe: 'Société A', codeNom: 'Alpha' },
    { id: 2, date: '2023-06-20', lieu: 'Lyon', societe: 'Société B', codeNom: 'Beta' },
  ])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Mon Agenda</h1>

      <Table>
        <TableCaption>Mes événements à venir</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Date</TableHead>
            <TableHead>Lieu</TableHead>
            <TableHead>Société</TableHead>
            <TableHead>Code nom</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {evenements.map((evenement) => (
            <TableRow key={evenement.id}>
              <TableCell>{evenement.date}</TableCell>
              <TableCell>{evenement.lieu}</TableCell>
              <TableCell>{evenement.societe}</TableCell>
              <TableCell>{evenement.codeNom}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

