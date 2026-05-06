package com.reclamation.ticket_service.Enum;

import lombok.AllArgsConstructor;

@AllArgsConstructor
public enum TicketPriority {
    LOW("LOW"), MEDIUM("MEDIUM"), HIGH("HIGH"), CRITICAL("CRITICAL");

    private String value;
}
