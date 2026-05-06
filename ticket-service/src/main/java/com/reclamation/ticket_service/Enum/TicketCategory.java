package com.reclamation.ticket_service.Enum;

import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import lombok.AllArgsConstructor;
import lombok.Getter;

@AllArgsConstructor
public enum TicketCategory {
    BILLING ("BILLING"), TECHNICAL("TECHNICAL"), DELIVERY("DELIVERY"), OTHER("OTHER");
    private String value;
}
