package com.iset.Agent.notification;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

/**
 * Client HTTP pour interagir avec TICKET-SERVICE via Eureka.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class TicketClient {

    private final RestTemplate restTemplate;

    public TicketDTO getTicket(String ticketId) {
        try {
            return restTemplate.getForObject(
                    "http://TICKET-SERVICE/ticket/" + ticketId, TicketDTO.class);
        } catch (Exception ex) {
            log.warn("[ticket-client] Impossible de recuperer le ticket {}: {}", ticketId, ex.getMessage());
            return null;
        }
    }

    public void updateStatus(String ticketId, String status) {
        try {
            restTemplate.patchForObject(
                    "http://TICKET-SERVICE/ticket/" + ticketId + "/status?status=" + status,
                    null, Object.class);
        } catch (Exception ex) {
            log.warn("[ticket-client] Impossible de mettre a jour le statut du ticket {}: {}",
                    ticketId, ex.getMessage());
        }
    }

    public void escalate(String ticketId) {
        try {
            restTemplate.postForObject(
                    "http://TICKET-SERVICE/ticket/" + ticketId + "/escalate",
                    null, Object.class);
        } catch (Exception ex) {
            log.warn("[ticket-client] Impossible d'escalader le ticket {}: {}", ticketId, ex.getMessage());
        }
    }
}
