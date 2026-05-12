package com.iset.Agent.dto;

import com.iset.Agent.enums.AgentLevel;
import com.iset.Agent.enums.AgentSpecialty;
import com.iset.Agent.enums.AgentStatus;
import lombok.Data;
import java.time.LocalDateTime;

@Data
public class AgentResponseDTO {
    private String id;
    private String firstName;
    private String lastName;
    private String email;
    private String phone;
    private AgentSpecialty specialty;
    private AgentLevel level;
    private AgentStatus status;
    private String department;
    private int maxTickets;
    private int currentTicketCount;
    private LocalDateTime createdAt;
}