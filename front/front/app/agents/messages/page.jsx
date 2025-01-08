'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function AgentMessages() {
  const [messages, setMessages] = useState([
    { id: 1, from: 'Admin', to: 'Moi', content: 'Bonjour, n\'oubliez pas l\'événement de demain.', date: '2023-06-14 10:00' },
    { id: 2, from: 'Moi', to: 'Admin', content: 'Merci pour le rappel, je serai présent.', date: '2023-06-14 10:05' },
  ])
  const [newMessage, setNewMessage] = useState({ to: '', content: '' })

  const sendMessage = () => {
    if (newMessage.to && newMessage.content) {
      setMessages([...messages, { 
        id: messages.length + 1, 
        from: 'Moi', 
        to: newMessage.to, 
        content: newMessage.content, 
        date: new Date().toLocaleString() 
      }])
      setNewMessage({ to: '', content: '' })
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Mes Messages</h1>

      <div className="grid grid-cols-3 gap-4">
        <Input 
          placeholder="Destinataire" 
          value={newMessage.to} 
          onChange={(e) => setNewMessage({...newMessage, to: e.target.value})}
        />
        <Input 
          placeholder="Message" 
          value={newMessage.content} 
          onChange={(e) => setNewMessage({...newMessage, content: e.target.value})}
        />
        <Button onClick={sendMessage}>Envoyer</Button>
      </div>

      <Table>
        <TableCaption>Historique des messages</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>De</TableHead>
            <TableHead>À</TableHead>
            <TableHead>Message</TableHead>
            <TableHead>Date</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {messages.map((message) => (
            <TableRow key={message.id}>
              <TableCell>{message.from}</TableCell>
              <TableCell>{message.to}</TableCell>
              <TableCell>{message.content}</TableCell>
              <TableCell>{message.date}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

