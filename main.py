import asyncio
from supabase_client import supabase
from matching import haversine
import time
import firebase_messaging


CHECK_INTERVAL = 1

async def match_clients_and_maintenance():
    print("[INFO] Iniciando busca por novos tickets...")

    clients = supabase.table("client").select("*").eq("status", "ABERTO").execute().data
    technicians = supabase.table("maintenance").select("*").eq("status", "ATIVO").neq("status", "EM MANUTENÇÃO").execute().data

    for client in clients:
        best_tech = None
        best_score = float('inf')
        
        for tech in technicians:
            dist = haversine(client['longitude'], client['latitude'], tech['longitude'], tech['latitude'])
            specialty_match = client['problem'] == tech['specialty']
            score = dist * (0.5 if specialty_match else 1.5)
            
            if score < best_score:
                best_score = score
                best_tech = tech

        if best_tech:
            print(f"[MATCH] Cliente {client['nome']} -> Técnico {best_tech['nome']} ({best_score:.2f} pontos)")

            insert = supabase.table("service").insert({
                "fk_id_client": client["id_client"],
                "fk_id_maintenance": best_tech["id_maintenance"],
                "status": "EM AGUARDE",
                "specialty_match": client['problem'] == best_tech['specialty'],
                "score": str(best_score)
            }).execute()

            firebase_messaging.sendNotification(titleMessage='Você tem 5 minutos para aceitar', bodyMessage='Concerto de geladeira', tokenMessage='eMhCXt-SSjOogDC0ypowIW:APA91bE3RRGRQZJdWQO9ZN1UllYCf6WDNij_ORarIRSYo9qqIjKvViLO4RjOH3edyqAZYRFtR0fq1jeBhpreWM6yB-uschbaB87FiE7MFn3VlcqQ3539kLc')
            
            await wait_for_acceptance(client["id_client"], best_tech["id_maintenance"])

            supabase.table("maintenance").update({"status": "EM MANUTENÇÃO"}).eq("id_maintenance", best_tech["id_maintenance"]).execute()
            supabase.table("client").update({"status": "EM MANUTENÇÃO"}).eq("id_client", client["id_client"]).execute()

            technicians = supabase.table("maintenance").select("*").eq("status", "ATIVO").neq("status", "EM MANUTENÇÃO").execute().data

async def wait_for_acceptance(client_id, tech_id):
    
    print(f"[INFO] Aguardando aceitação de técnico {tech_id} para cliente {client_id}...")

    start_time = time.time()

    while time.time() - start_time < 300:

        service = supabase.table("service").select("*").match({
            "fk_id_client": client_id,
            "fk_id_maintenance": tech_id
        }).order("id_service", desc=True).limit(1).execute().data
        if service and service[0]["status"] == "CONCERTANDO":
            supabase.table("maintenance").update({"status": "EM MANUTENÇÃO"}).eq("id_maintenance", tech_id).execute().data
            supabase.table("client").update({"status": "EM MANUTENÇÃO"}).eq("id_client", client_id).execute().data
            print(f"[SUCESSO] Técnico aceitou o serviço!")
            return
        
        await asyncio.sleep(1)

    print(f"[TIMEOUT] Técnico {tech_id} não aceitou o serviço. Reatribuindo...")
    supabase.table("service").update({"status": "cancelado"}).match({
        "fk_id_client": client_id,
        "fk_id_maintenance": tech_id
    }).execute()

async def main_loop():
    
    while True:
        await match_clients_and_maintenance()
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main_loop())
