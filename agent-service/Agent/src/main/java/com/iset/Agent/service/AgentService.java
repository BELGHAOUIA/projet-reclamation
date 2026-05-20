package com.iset.Agent.service;

import com.iset.Agent.dto.*;
import com.iset.Agent.entity.Agent;
import com.iset.Agent.entity.AgentAssignment;
import com.iset.Agent.enums.AgentLevel;
import com.iset.Agent.enums.AgentSpecialty;
import com.iset.Agent.enums.AgentStatus;
import com.iset.Agent.notification.NotificationClient;
import com.iset.Agent.notification.TicketClient;
import com.iset.Agent.notification.TicketDTO;
import com.iset.Agent.repository.AgentAssignmentRepository;
import com.iset.Agent.repository.AgentRepository;
import jakarta.persistence.EntityNotFoundException;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AgentService {

    private final AgentRepository agentRepository;
    private final AgentAssignmentRepository assignmentRepository;
    private final NotificationClient notificationClient;
    private final TicketClient ticketClient;

    // ── CRUD ──────────────────────────────────────────────

    private void validateAgent(AgentRequestDTO dto) {
        boolean emailExists = agentRepository.findAll()
                .stream()
                .anyMatch(agent -> agent.getEmail().equalsIgnoreCase(dto.getEmail()));

        if (emailExists) {
            throw new IllegalArgumentException("L'adresse email est déjà utilisée.");
        }

        if (!dto.getPhone().matches("\\d+")) {
            throw new IllegalArgumentException("Le numéro de téléphone doit contenir uniquement des chiffres.");
        }

        if (dto.getPhone().length() < 8) {
            throw new IllegalArgumentException("Le numéro de téléphone doit contenir au moins 8 chiffres.");
        }

        if (dto.getMaxTickets() <= 0 || dto.getMaxTickets() > 20) {
            throw new IllegalArgumentException("Le nombre maximal de tickets doit être compris entre 1 et 20.");
        }

        List<String> departments = List.of("IT", "RH", "SUPPORT", "COMMERCIAL");
        if (!departments.contains(dto.getDepartment().toUpperCase())) {
            throw new IllegalArgumentException("Département invalide.");
        }
    }
    @Transactional
    public AgentResponseDTO createAgent(AgentRequestDTO dto) {

        validateAgent(dto);

        // 1. On nettoie l'email : on garde uniquement les lettres et les chiffres [^a-zA-Z0-9]
        // 2. On passe tout en minuscules pour éviter les surprises
        String cleanEmail = dto.getEmail().replaceAll("[^a-zA-Z0-9]", "").toLowerCase();

        // 3. On combine l'email propre et le mot "agent" (sans tiret)
        String customId = cleanEmail + "agent";

        Agent agent = Agent.builder()
                .id(customId)
                .firstName(dto.getFirstName())
                .lastName(dto.getLastName())
                .email(dto.getEmail()) // L'email stocké dans la table reste normal (ex: mohamed.benali@gmail.com)
                .phone(dto.getPhone())
                .specialty(dto.getSpecialty())
                .level(dto.getLevel())
                .department(dto.getDepartment())
                .maxTickets(dto.getMaxTickets())
                .currentTicketCount(0)
                .status(AgentStatus.AVAILABLE)
                .build();

        return toDTO(agentRepository.save(agent));
    }

    public List<AgentResponseDTO> getAllAgents() {
        return agentRepository.findAll().stream().map(this::toDTO).collect(Collectors.toList());
    }

    public AgentResponseDTO getAgentById(String id) {
        return toDTO(findAgent(id));
    }

    public AgentResponseDTO updateAgent(String id, AgentRequestDTO dto) {
        Agent agent = findAgent(id);
        agent.setFirstName(dto.getFirstName());
        agent.setLastName(dto.getLastName());
        agent.setEmail(dto.getEmail());
        agent.setPhone(dto.getPhone());
        agent.setSpecialty(dto.getSpecialty());
        agent.setLevel(dto.getLevel());
        agent.setDepartment(dto.getDepartment());
        agent.setMaxTickets(dto.getMaxTickets());
        return toDTO(agentRepository.save(agent));
    }

    public void deleteAgent(String id) {
        agentRepository.deleteById(id);
    }

    // ── DISPONIBILITÉ ─────────────────────────────────────

    public List<AgentResponseDTO> getAvailableAgents() {
        return agentRepository.findByStatus(AgentStatus.AVAILABLE)
                .stream().map(this::toDTO).collect(Collectors.toList());
    }

    public List<AgentResponseDTO> getAvailableByDepartment(String department) {
        return agentRepository.findByStatusAndDepartment(AgentStatus.AVAILABLE, department)
                .stream().map(this::toDTO).collect(Collectors.toList());
    }

    // ── AFFECTATION AUTOMATIQUE ───────────────────────────

    @Transactional
    public String assignAgent(String ticketId, String agentId) {

       Agent selected = agentRepository.findById(agentId).orElseThrow(EntityNotFoundException::new);
        selected.setCurrentTicketCount(selected.getCurrentTicketCount() + 1);
        if (selected.getCurrentTicketCount() >= selected.getMaxTickets()) {
            selected.setStatus(AgentStatus.BUSY);
        }
        agentRepository.save(selected);

        notificationClient.sendToAdmin("TICKET_ASSIGNED", ticketId);
        notificationClient.sendToAgent(selected.getId(), "TICKET_ASSIGNED", ticketId);
        return "ok";
    }

    @Transactional
    public void releaseAgent(String ticketId) {
        AgentAssignment assignment = assignmentRepository.findByTicketIdAndActiveTrue(ticketId)
                .orElseThrow(() -> new EntityNotFoundException("Aucune affectation active pour ce ticket."));

        assignment.setActive(false);
        assignment.setReleasedAt(LocalDateTime.now());
        assignmentRepository.save(assignment);

        Agent agent = assignment.getAgent();
        int newCount = Math.max(0, agent.getCurrentTicketCount() - 1);
        agent.setCurrentTicketCount(newCount);
        if (newCount < agent.getMaxTickets()) {
            agent.setStatus(AgentStatus.AVAILABLE);
        }
        agentRepository.save(agent);
    }

    public AssignmentResponseDTO getAssignmentByTicket(String ticketId) {
        AgentAssignment assignment = assignmentRepository.findByTicketIdAndActiveTrue(ticketId)
                .orElseThrow(() -> new EntityNotFoundException("Aucune affectation active pour ticket: " + ticketId));
        return toAssignmentDTO(assignment, assignment.getAgent());
    }

    // ── GESTION STATUT TICKET ─────────────────────────────

    @Transactional
    public void resolveTicket(String ticketId) {
        // Utilise getAssignmentByTicket (méthode existante) pour récupérer l'affectation et l'email agent
        AssignmentResponseDTO assignment = null;
        try { assignment = getAssignmentByTicket(ticketId); } catch (EntityNotFoundException ignored) {}

        ticketClient.updateStatus(ticketId, "RESOLVED");
        // Utilise releaseAgent (méthode existante) pour libérer l'agent
        if (assignment != null) {
            releaseAgent(ticketId);
        }

        notificationClient.sendToAdmin("TICKET_RESOLVED", ticketId);
        TicketDTO ticket = ticketClient.getTicket(ticketId);
        if (ticket != null) {
            notificationClient.sendToClient(ticket.getClientId(), "TICKET_RESOLVED", ticketId);
        }
        if (assignment != null) {
            notificationClient.sendToAgent(assignment.getAgentId(), "TICKET_RESOLVED", ticketId);
        }
    }

    @Transactional
    public void escalateTicket(String ticketId) {
        ticketClient.escalate(ticketId);

        notificationClient.sendToAdmin("TICKET_ESCALATED", ticketId);
        TicketDTO ticket = ticketClient.getTicket(ticketId);
        if (ticket != null) {
            notificationClient.sendToClient(ticket.getClientId(), "TICKET_ESCALATED", ticketId);
        }
    }

    public void updateTicket(String ticketId, String status) {
        if (status != null && !status.isBlank()) {
            ticketClient.updateStatus(ticketId, status);
        }
        notificationClient.sendToAdmin("TICKET_UPDATED", ticketId);
    }

    private Agent findAgent(String id) {
        return agentRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("Agent non trouvé: " + id));
    }

    private AgentSpecialty mapCategoryToSpecialty(String category) {
        if (category == null) return AgentSpecialty.GENERAL;
        return switch (category.toUpperCase()) {
            case "TECHNICAL" -> AgentSpecialty.TECHNICAL;
            case "BILLING" -> AgentSpecialty.BILLING;
            case "SHIPPING" -> AgentSpecialty.SHIPPING;
            case "RETURNS" -> AgentSpecialty.RETURNS;
            default -> AgentSpecialty.GENERAL;
        };
    }

    private AgentResponseDTO toDTO(Agent agent) {
        AgentResponseDTO dto = new AgentResponseDTO();
        dto.setId(agent.getId());
        dto.setFirstName(agent.getFirstName());
        dto.setLastName(agent.getLastName());
        dto.setEmail(agent.getEmail());
        dto.setPhone(agent.getPhone());
        dto.setSpecialty(agent.getSpecialty());
        dto.setLevel(agent.getLevel());
        dto.setStatus(agent.getStatus());
        dto.setDepartment(agent.getDepartment());
        dto.setMaxTickets(agent.getMaxTickets());
        dto.setCurrentTicketCount(agent.getCurrentTicketCount());
        dto.setCreatedAt(agent.getCreatedAt());
        return dto;
    }

    private AssignmentResponseDTO toAssignmentDTO(AgentAssignment a, Agent agent) {
        AssignmentResponseDTO dto = new AssignmentResponseDTO();
        dto.setAssignmentId(a.getId());
        dto.setAgentId(agent.getId());
        dto.setAgentName(agent.getFirstName() + " " + agent.getLastName());
        dto.setAgentEmail(agent.getEmail());
        dto.setTicketId(a.getTicketId());
        dto.setTicketPriority(a.getTicketPriority());
        dto.setAssignedAt(a.getAssignedAt());
        dto.setActive(a.isActive());
        return dto;
    }
}