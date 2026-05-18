package com.reclamation.ticket_service.notification;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

/**
 * Client HTTP pour récupérer les données d'un agent depuis AGENT-SERVICE.
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AgentClient {

    private final RestTemplate restTemplate;

    @SuppressWarnings("unchecked")
    public String getAgentEmail(String agentId) {
        try {
            Map<String, Object> agent = restTemplate.getForObject(
                    "http://AGENT-SERVICE/agent/" + agentId, Map.class);
            return agent != null ? (String) agent.get("email") : null;
        } catch (Exception ex) {
            log.warn("[agent-client] Impossible de recuperer l'email de l'agent {}: {}",
                    agentId, ex.getMessage());
            return null;
        }
    }
}
