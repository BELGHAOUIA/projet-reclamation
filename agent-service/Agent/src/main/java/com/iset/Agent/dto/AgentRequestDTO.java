package com.iset.Agent.dto;

import com.iset.Agent.enums.AgentLevel;
import com.iset.Agent.enums.AgentSpecialty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import lombok.Data;

@Data
public class AgentRequestDTO {

    @NotBlank(message = "Le prénom est obligatoire")
    private String firstName;

    @NotBlank(message = "Le nom est obligatoire")
    private String lastName;

    @NotBlank(message = "L'adresse e-mail est obligatoire")
    @Email(message = "L'adresse e-mail saisie est invalide")
    private String email;

    @NotBlank(message = "Le numéro de téléphone est obligatoire")
    @Pattern(regexp = "^[0-9]{8}$", message = "Le numéro de téléphone doit contenir exactement 8 chiffres")
    private String phone;

    @NotNull(message = "La spécialité est obligatoire")
    private AgentSpecialty specialty;

    @NotNull(message = "Le niveau est obligatoire")
    private AgentLevel level;

    @NotBlank(message = "Le département est obligatoire")
    private String department;

    private int maxTickets = 5;
}