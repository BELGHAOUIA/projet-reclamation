package com.iset.Agent.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class AssignmentResponseDTO {
    private String assignmentId;
    private String agentId;
    private String agentName;
    private String agentEmail;
    private String ticketId;
    private String ticketPriority;
    private LocalDateTime assignedAt;
    private boolean active;
}