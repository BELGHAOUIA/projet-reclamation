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

    public AgentResponseDTO createAgent(AgentRequestDTO dto) {
        Agent agent = Agent.builder()
                .firstName(dto.getFirstName())
                .lastName(dto.getLastName())
                .email(dto.getEmail())
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
    public AssignmentResponseDTO assignAgent(String ticketId, String priority, String category) {
        // Étape 1 : trouver specialty selon catégorie
        AgentSpecialty specialty = mapCategoryToSpecialty(category);

        // Étape 2 : selon priorité, chercher senior/expert si HIGH ou CRITICAL
        List<Agent> candidates;
        if (priority.equals("HIGH") || priority.equals("CRITICAL")) {
            candidates = agentRepository.findByStatusAndSpecialtyAndLevel(
                    AgentStatus.AVAILABLE, specialty, AgentLevel.SENIOR);
            if (candidates.isEmpty()) {
                candidates = agentRepository.findByStatusAndSpecialtyAndLevel(
                        AgentStatus.AVAILABLE, specialty, AgentLevel.EXPERT);
            }
        } else {
            candidates = agentRepository.findByStatusAndSpecialty(AgentStatus.AVAILABLE, specialty);
        }

        // Étape 3 : fallback — n'importe quel agent disponible
        if (candidates.isEmpty()) {
            candidates = agentRepository.findByStatus(AgentStatus.AVAILABLE);
        }
        if (candidates.isEmpty()) {
            throw new RuntimeException("Aucun agent disponible actuellement.");
        }

        // Étape 4 : choisir le moins chargé
        Agent selected = candidates.stream()
                .filter(a -> a.getCurrentTicketCount() < a.getMaxTickets())
                .min((a, b) -> Integer.compare(a.getCurrentTicketCount(), b.getCurrentTicketCount()))
                .orElseThrow(() -> new RuntimeException("Tous les agents sont à capacité maximale."));

        // Mise à jour agent
        selected.setCurrentTicketCount(selected.getCurrentTicketCount() + 1);
        if (selected.getCurrentTicketCount() >= selected.getMaxTickets()) {
            selected.setStatus(AgentStatus.BUSY);
        }
        agentRepository.save(selected);

        // Créer assignment
        AgentAssignment assignment = AgentAssignment.builder()
                .agent(selected)
                .ticketId(ticketId)
                .ticketPriority(priority)
                .ticketCategory(category)
                .active(true)
                .build();
        AgentAssignment saved = assignmentRepository.save(assignment);

        AssignmentResponseDTO response = toAssignmentDTO(saved, selected);
        notificationClient.sendToAdmin("TICKET_ASSIGNED", ticketId);
        notificationClient.sendToAgent(selected.getId(), "TICKET_ASSIGNED", ticketId);
        return response;
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