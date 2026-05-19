package com.iset.Agent.notification;

import lombok.Data;

/**
 * DTO léger pour lire les données d'un ticket depuis TICKET-SERVICE.
 */
@Data
public class TicketDTO {
    private String id;
    private String title;
    private String clientId;
    private String clientEmail;
    private String agentId;
    private String status;
}
