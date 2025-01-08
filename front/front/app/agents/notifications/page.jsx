'use client'

import { useState } from 'react'
import { Table, TableBody, TableCaption, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

export default function AgentNotifications() {
  const [notifications, setNotifications] = useState([
    { id: 1, content: 'Nouvel événement ajouté à votre agenda', date: '2023-06-14 09:00', read: false },
    { id: 2, content: 'Rappel : événement demain à 10h', date: '2023-06-14 15:00', read: true },
  ])

  const markAsRead = (id) => {
    setNotifications(notifications.map(notif => 
      notif.id === id ? {...notif, read: true} : notif
    ))
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Mes Notifications</h1>

      <Table>
        <TableCaption>Liste des notifications</TableCaption>
        <TableHeader>
          <TableRow>
            <TableHead>Contenu</TableHead>
            <TableHead>Date</TableHead>
            <TableHead>Statut</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {notifications.map((notif) => (
            <TableRow key={notif.id} className={notif.read ? 'opacity-50' : ''}>
              <TableCell>{notif.content}</TableCell>
              <TableCell>{notif.date}</TableCell>
              <TableCell>
                {notif.read ? 'Lu' : (
                  <button onClick={() => markAsRead(notif.id)} className="text-blue-500 hover:underline">
                    Marquer comme lu
                  </button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

