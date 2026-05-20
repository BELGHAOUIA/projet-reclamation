package com.iset.Agent.notification;

import com.fasterxml.jackson.annotation.JsonInclude;
import lombok.Builder;
import lombok.Data;

@Data
@Builder
@JsonInclude(JsonInclude.Include.NON_NULL)
public class NotificationRequest {
    private String recipientId;
    private String recipientType;
    private String recipientEmail;
    private String recipientName;
    private String type;
    private String channel;
    private String ticketId;
}
