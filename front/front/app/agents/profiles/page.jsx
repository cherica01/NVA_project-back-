'use client'

import { useState } from 'react'
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function AgentProfil() {
  const [profile, setProfile] = useState({
    nom: 'Dupont',
    prenom: 'Jean',
    age: 30,
    localisation: 'Paris',
    telephone: '0123456789',
    mensurations: '180cm/75kg',
    photos: ['/placeholder.jpg', '/placeholder.jpg', '/placeholder.jpg', '/placeholder.jpg']
  })

  const [newPhoto, setNewPhoto] = useState('')

  const updateProfile = (field, value) => {
    setProfile({...profile, [field]: value})
  }

  const addPhoto = () => {
    if (newPhoto && profile.photos.length < 4) {
      setProfile({...profile, photos: [...profile.photos, newPhoto]})
      setNewPhoto('')
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Mon Profil</h1>

      <div className="grid grid-cols-2 gap-4">
        <Input 
          placeholder="Nom" 
          value={profile.nom} 
          onChange={(e) => updateProfile('nom', e.target.value)}
        />
        <Input 
          placeholder="Prénom" 
          value={profile.prenom} 
          onChange={(e) => updateProfile('prenom', e.target.value)}
        />
        <Input 
          placeholder="Âge" 
          type="number"
          value={profile.age} 
          onChange={(e) => updateProfile('age', parseInt(e.target.value))}
        />
        <Input 
          placeholder="Localisation" 
          value={profile.localisation} 
          onChange={(e) => updateProfile('localisation', e.target.value)}
        />
        <Input 
          placeholder="Téléphone" 
          value={profile.telephone} 
          onChange={(e) => updateProfile('telephone', e.target.value)}
        />
        <Input 
          placeholder="Mensurations" 
          value={profile.mensurations} 
          onChange={(e) => updateProfile('mensurations', e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <h2 className="text-xl font-semibold">Mes photos</h2>
        <div className="grid grid-cols-4 gap-4">
          {profile.photos.map((photo, index) => (
            <img key={index} src={photo} alt={`Photo ${index + 1}`} className="w-full h-40 object-cover rounded" />
          ))}
        </div>
        <div className="flex gap-2">
          <Input 
            placeholder="URL de la nouvelle photo" 
            value={newPhoto} 
            onChange={(e) => setNewPhoto(e.target.value)}
          />
          <Button onClick={addPhoto} disabled={profile.photos.length >= 4}>Ajouter une photo</Button>
        </div>
      </div>

      <Button className="w-full">Sauvegarder les modifications</Button>
    </div>
  )
}

