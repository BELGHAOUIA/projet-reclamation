package com.reclamation.ticket_service.Enum;

import lombok.AllArgsConstructor;

@AllArgsConstructor
public enum TicketStatus {
    OPEN("OPEN"), IN_PROGRESS("IN_PROGRESS"), RESOLVED("RESOLVED"), ESCALATED("ESCALATED"), CLOSED("CLOSED");
    private String value;
}
