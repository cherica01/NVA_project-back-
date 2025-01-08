'use client'

import { useState } from 'react'
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function AgentWallet() {
  const [solde, setSolde] = useState(1500)
  const [payments, setPayments] = useState([
    { id: 1, date: '2023-06-01', montant: 1000, description: 'Paiement pour mai 2023' },
    { id: 2, date: '2023-06-15', montant: 500, description: 'Bonus événement spécial' },
  ])

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Mon Wallet</h1>

      <div className="bg-blue-100 p-4 rounded">
        <h2 className="text-xl font-semibold">Solde actuel</h2>
        <p className="text-3xl font-bold">{solde} €</p>
      </div>

      <Table>
        <TableCaption>Historique des paiements</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Date</TableHead>
            <TableHead>Montant</TableHead>
            <TableHead>Description</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {payments.map((payment) => (
            <TableRow key={payment.id}>
              <TableCell>{payment.date}</TableCell>
              <TableCell>{payment.montant} €</TableCell>
              <TableCell>{payment.description}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

