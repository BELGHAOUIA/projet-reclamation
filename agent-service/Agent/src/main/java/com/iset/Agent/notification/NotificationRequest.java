package com.iset.Agent.notification;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class NotificationRequest {
    private String recipientId;
    private String recipientType;
    private String recipientEmail;
    private String recipientName;
    private String type;
    private String channel;
    private String ticketId;
}
