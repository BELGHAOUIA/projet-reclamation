package com.iset.Agent.dto;

import com.iset.Agent.enums.AgentLevel;
import com.iset.Agent.enums.AgentSpecialty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;

@Data
public class AgentRequestDTO {

    @NotBlank(message = "Le prénom est obligatoire")
    private String firstName;

    @NotBlank(message = "Le nom est obligatoire")
    private String lastName;

    @NotBlank @Email
    private String email;

    private String phone;

    @NotNull
    private AgentSpecialty specialty;

    @NotNull
    private AgentLevel level;

    @NotBlank
    private String department;

    private int maxTickets = 5;
}