# EndPoint
## GESTION AGENT 
* (POST) login

`/api/accounts/login/`

* forme de donnée 
    {
    * "username":"riantsoa",
    * "password":"cherica"
}
 *(POST) add Agent(mbola tsisy sary )

 `/api/accounts/add-agent/`
 
 * forme de donnee
 {
    "username":"test1",
    "password":"cherica",
    "age":"10",
    "gender":"male",
    "location":"tsimbazaza",
    "phone_number":"0344445677",
    "measurements":"1m67"
}

*(PATCH) PATCH agent 
`/api/accounts/<int:pk>/update/`

*(DELETE) DELETE agent 
`/api/accounts/<int:pk>/update/`
*(GET) VISITER PROFILS
`/api/accounts/profile/`

## GESTION NOTIF 

*(POST) send notification

`/api/management/send-notification/`

* forme de donnee 
{
  "message": "Reminder: Your shift starts at 9 AM tomorrow.",
  "date": "2024-12-20",  
  "recipient_id": 1  
}
* (DELETE) delete notif 
`/api/management/delete-notification/<int:pk>/`

*(GET) recuperation des notif de l agent 

`/api/management/agent-notifications/<int:id>/`

*(GET) VOIR les historique de notification 

`/api/management/notifications/history/`
## GESTION DE PAYMENT 
* (POST) contribution de payment pOUR l agent 
`/api/management/admin/payment/`

* (GET)recuperation de ces soldes total 
`/api/management/agent/total-payment/`

* (GET) MIJERY HISTORIQUE DE PAYMENT 
`/api/management/agent/payments/history/`

## GESTION EVENT 
*(POST) CREER EVENT 
`/api/management/create-event/`
*forme de donnnee
{
    "location": "Antananarivo",
    "company_name": "Tech Corp",
    "event_code": "EVT2025",
    "start_date": "2025-01-15",
    "end_date": "2025-01-20",
    "agents": [1, 2, 3]
}
*(PATCH) MIS A JOUR EVENT
`/api/management/events/<int:pk>/update/`

*(DELETE) SUP EVENT
`/api/management/events/<int:pk>/delete/`
