package com.iset.Agent.notification;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.nio.charset.StandardCharsets;
import java.util.UUID;

/**
 * Client HTTP pour l'envoi de notifications via NOTIFICATION-SERVICE.
 * Les erreurs d'envoi sont loguées sans impacter l'opération principale.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class NotificationClient {

    private final RestTemplate restTemplate;

    @Value("${admin.email:admin@reclamation.com}")
    private String adminEmail;

    private static final String NOTIFICATION_URL =
            "http://NOTIFICATION-SERVICE/api/v1/notifications/send/";

    private static final UUID ADMIN_ID =
            UUID.fromString("00000000-0000-0000-0000-000000000001");

    public void sendToAdmin(String type, String ticketId) {
        send(NotificationRequest.builder()
                .recipientId(ADMIN_ID.toString())
                .recipientType("ADMIN")
                .recipientEmail(adminEmail)
                .recipientName("Administrateur")
                .type(type)
                .channel("EMAIL")
                .ticketId(ticketId)
                .build());
    }

    public void sendToClient(String clientId, String clientEmail, String clientName,
                             String type, String ticketId) {
        if (clientEmail == null || clientEmail.isBlank()) return;
        send(NotificationRequest.builder()
                .recipientId(toUUID(clientId, "client:").toString())
                .recipientType("CLIENT")
                .recipientEmail(clientEmail)
                .recipientName(clientName != null ? clientName : clientId)
                .type(type)
                .channel("EMAIL")
                .ticketId(ticketId)
                .build());
    }

    public void sendToAgent(String agentId, String agentEmail, String agentName,
                            String type, String ticketId) {
        if (agentEmail == null || agentEmail.isBlank()) return;
        send(NotificationRequest.builder()
                .recipientId(toUUID(agentId, "agent:").toString())
                .recipientType("AGENT")
                .recipientEmail(agentEmail)
                .recipientName(agentName != null ? agentName : agentId)
                .type(type)
                .channel("EMAIL")
                .ticketId(ticketId)
                .build());
    }

    private void send(NotificationRequest req) {
        try {
            restTemplate.postForObject(NOTIFICATION_URL, req, Object.class);
            log.info("[notification] Envoyee: type={} -> {}", req.getType(), req.getRecipientEmail());
        } catch (Exception ex) {
            log.warn("[notification] Echec envoi type={} -> {}: {}",
                    req.getType(), req.getRecipientEmail(), ex.getMessage());
        }
    }

    private UUID toUUID(String id, String prefix) {
        try {
            return UUID.fromString(id);
        } catch (IllegalArgumentException e) {
            return UUID.nameUUIDFromBytes((prefix + id).getBytes(StandardCharsets.UTF_8));
        }
    }
}
