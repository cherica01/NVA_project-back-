'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function AdminAgents() {
  const [agents, setAgents] = useState([
    { id: 1, nom: 'Dupont', prenom: 'Jean', age: 30, localisation: 'Paris', telephone: '0123456789', mensurations: '180cm/75kg' },
    { id: 2, nom: 'Martin', prenom: 'Marie', age: 28, localisation: 'Lyon', telephone: '0987654321', mensurations: '165cm/60kg' },
  ])
  const [newAgent, setNewAgent] = useState({ nom: '', prenom: '', age: 0, localisation: '', telephone: '', mensurations: '' })

  const addAgent = () => {
    if (newAgent.nom && newAgent.prenom) {
      setAgents([...agents, { ...newAgent, id: agents.length + 1 }])
      setNewAgent({ nom: '', prenom: '', age: 0, localisation: '', telephone: '', mensurations: '' })
    }
  }

  const deleteAgent = (id) => {
    setAgents(agents.filter(agent => agent.id !== id))
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Gestion des Agents</h1>
      
      <div className="grid grid-cols-3 gap-4">
        <Input 
          placeholder="Nom" 
          value={newAgent.nom} 
          onChange={(e) => setNewAgent({...newAgent, nom: e.target.value})}
        />
        <Input 
          placeholder="Prénom" 
          value={newAgent.prenom} 
          onChange={(e) => setNewAgent({...newAgent, prenom: e.target.value})}
        />
        <Input 
          placeholder="Âge" 
          type="number"
          value={newAgent.age || ''} 
          onChange={(e) => setNewAgent({...newAgent, age: parseInt(e.target.value)})}
        />
        <Input 
          placeholder="Localisation" 
          value={newAgent.localisation} 
          onChange={(e) => setNewAgent({...newAgent, localisation: e.target.value})}
        />
        <Input 
          placeholder="Téléphone" 
          value={newAgent.telephone} 
          onChange={(e) => setNewAgent({...newAgent, telephone: e.target.value})}
        />
        <Input 
          placeholder="Mensurations" 
          value={newAgent.mensurations} 
          onChange={(e) => setNewAgent({...newAgent, mensurations: e.target.value})}
        />
      </div>
      <Button onClick={addAgent}>Ajouter un agent</Button>

      <Table>
        <TableCaption>Liste des agents</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Nom</TableHead>
            <TableHead>Prénom</TableHead>
            <TableHead>Âge</TableHead>
            <TableHead>Localisation</TableHead>
            <TableHead>Téléphone</TableHead>
            <TableHead>Mensurations</TableHead>
            <TableHead>Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {agents.map((agent) => (
            <TableRow key={agent.id}>
              <TableCell>{agent.nom}</TableCell>
              <TableCell>{agent.prenom}</TableCell>
              <TableCell>{agent.age}</TableCell>
              <TableCell>{agent.localisation}</TableCell>
              <TableCell>{agent.telephone}</TableCell>
              <TableCell>{agent.mensurations}</TableCell>
              <TableCell>
                <Button variant="destructive" onClick={() => deleteAgent(agent.id)}>Supprimer</Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

