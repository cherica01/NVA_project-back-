'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function AdminEvenements() {
  const [evenements, setEvenements] = useState([
    { id: 1, lieu: 'Paris', societe: 'Société A', agents: ['Jean Dupont', 'Marie Martin'], codeNom: 'Alpha' },
    { id: 2, lieu: 'Lyon', societe: 'Société B', agents: ['Pierre Durand'], codeNom: 'Beta' },
  ])
  const [newEvenement, setNewEvenement] = useState({ lieu: '', societe: '', agents: [], codeNom: '' })

  const addEvenement = () => {
    if (newEvenement.lieu && newEvenement.societe && newEvenement.codeNom) {
      setEvenements([...evenements, { ...newEvenement, id: evenements.length + 1 }])
      setNewEvenement({ lieu: '', societe: '', agents: [], codeNom: '' })
    }
  }

  const deleteEvenement = (id) => {
    setEvenements(evenements.filter(evenement => evenement.id !== id))
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Gestion des Événements</h1>
      
      <div className="grid grid-cols-4 gap-4">
        <Input 
          placeholder="Lieu" 
          value={newEvenement.lieu} 
          onChange={(e) => setNewEvenement({...newEvenement, lieu: e.target.value})}
        />
        <Input 
          placeholder="Société" 
          value={newEvenement.societe} 
          onChange={(e) => setNewEvenement({...newEvenement, societe: e.target.value})}
        />
        <Input 
          placeholder="Agents (séparés par des virgules)" 
          value={newEvenement.agents.join(', ')} 
          onChange={(e) => setNewEvenement({...newEvenement, agents: e.target.value.split(', ')})}
        />
        <Input 
          placeholder="Code nom" 
          value={newEvenement.codeNom} 
          onChange={(e) => setNewEvenement({...newEvenement, codeNom: e.target.value})}
        />
      </div>
      <Button onClick={addEvenement}>Ajouter un événement</Button>

      <Table>
        <TableCaption>Liste des événements</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Lieu</TableHead>
            <TableHead>Société</TableHead>
            <TableHead>Agents</TableHead>
            <TableHead>Code nom</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {evenements.map((evenement) => (
            <TableRow key={evenement.id}>
              <TableCell>{evenement.lieu}</TableCell>
              <TableCell>{evenement.societe}</TableCell>
              <TableCell>{evenement.agents.join(', ')}</TableCell>
              <TableCell>{evenement.codeNom}</TableCell>
              <TableCell>
                <Button variant="destructive" onClick={() => deleteEvenement(evenement.id)}>Supprimer</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

