package com.iset.Agent.notification;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
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

    private static final String NOTIFICATION_URL =
            "http://localhost:8888/api/v1/notifications/send/";

    private static final String ADMIN_ID = "ADMIN";

    public void sendToAdmin(String type, String ticketId) {
        send(NotificationRequest.builder()
                .recipientId(ADMIN_ID)
                .recipientType("ADMIN")
                .type(type)
                .channel("IN_APP")
                .ticketId(ticketId)
                .build());
    }

    public void sendToClient(String clientId, String type, String ticketId) {
        if (clientId == null || clientId.isBlank()) return;
        send(NotificationRequest.builder()
                .recipientId(clientId)
                .recipientType("CLIENT")
                .type(type)
                .channel("IN_APP")
                .ticketId(ticketId)
                .build());
    }

    public void sendToAgent(String agentId, String type, String ticketId) {
        if (agentId == null || agentId.isBlank()) return;
        send(NotificationRequest.builder()
                .recipientId(agentId)
                .recipientType("AGENT")
                .type(type)
                .channel("IN_APP")
                .ticketId(ticketId)
                .build());
    }

    private void send(NotificationRequest req) {
        try {
            restTemplate.postForObject(NOTIFICATION_URL, req, Object.class);
            log.info("[notification] Envoyee: type={} -> {}", req.getType(), req.getRecipientId());
        } catch (Exception ex) {
            log.warn("[notification] Echec envoi type={} -> {}: {}",
                    req.getType(), req.getRecipientId(), ex.getMessage());
        }
    }

    private UUID toUUID(String id) {
            return UUID.fromString(id);
    }
}
