package com.iset.Agent.controller;

import com.iset.Agent.dto.*;
import com.iset.Agent.service.AgentService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;

@RestController
@RequestMapping("/agent")
@RequiredArgsConstructor
@CrossOrigin(origins = "*")
public class AgentController {

    private final AgentService agentService;

    // ── CRUD ──────────────────────────────────────────────

    @PostMapping
    public ResponseEntity<AgentResponseDTO> createAgent(@Valid @RequestBody AgentRequestDTO dto) {
        return ResponseEntity.status(HttpStatus.CREATED).body(agentService.createAgent(dto));
    }

    @GetMapping
    public ResponseEntity<List<AgentResponseDTO>> getAllAgents() {
        return ResponseEntity.ok(agentService.getAllAgents());
    }

    @GetMapping("/{id}")
    public ResponseEntity<AgentResponseDTO> getAgent(@PathVariable String id) {
        return ResponseEntity.ok(agentService.getAgentById(id));
    }

    @PutMapping("/{id}")
    public ResponseEntity<AgentResponseDTO> updateAgent(@PathVariable String id,
                                                         @Valid @RequestBody AgentRequestDTO dto) {
        return ResponseEntity.ok(agentService.updateAgent(id, dto));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteAgent(@PathVariable String id) {
        agentService.deleteAgent(id);
        return ResponseEntity.noContent().build();
    }

    // ── DISPONIBILITÉ ─────────────────────────────────────

    @GetMapping("/available")
    public ResponseEntity<List<AgentResponseDTO>> getAvailableAgents() {
        return ResponseEntity.ok(agentService.getAvailableAgents());
    }

    @GetMapping("/available/department/{dept}")
    public ResponseEntity<List<AgentResponseDTO>> getAvailableByDept(@PathVariable String dept) {
        return ResponseEntity.ok(agentService.getAvailableByDepartment(dept));
    }

    // ── AFFECTATION ───────────────────────────────────────

    @PostMapping("/assign")
    public ResponseEntity<AssignmentResponseDTO> assignAgent(
            @RequestParam String ticketId,
            @RequestParam String priority,
            @RequestParam(required = false, defaultValue = "GENERAL") String category) {
        return ResponseEntity.ok(agentService.assignAgent(ticketId, priority, category));
    }

    @PostMapping("/release/{ticketId}")
    public ResponseEntity<Void> releaseAgent(@PathVariable String ticketId) {
        agentService.releaseAgent(ticketId);
        return ResponseEntity.ok().build();
    }

    @GetMapping("/assignment/ticket/{ticketId}")
    public ResponseEntity<AssignmentResponseDTO> getAssignment(@PathVariable String ticketId) {
        return ResponseEntity.ok(agentService.getAssignmentByTicket(ticketId));
    }

    // ── GESTION STATUT TICKET ─────────────────────────────

    @PostMapping("/ticket/{ticketId}/resolve")
    public ResponseEntity<Void> resolveTicket(@PathVariable String ticketId) {
        agentService.resolveTicket(ticketId);
        return ResponseEntity.ok().build();
    }

    @PostMapping("/ticket/{ticketId}/escalate")
    public ResponseEntity<Void> escalateTicket(@PathVariable String ticketId) {
        agentService.escalateTicket(ticketId);
        return ResponseEntity.ok().build();
    }

    @PatchMapping("/ticket/{ticketId}")
    public ResponseEntity<Void> updateTicket(@PathVariable String ticketId,
                                              @RequestParam(required = false) String status) {
        agentService.updateTicket(ticketId, status);
        return ResponseEntity.ok().build();
    }
}