package com.reclamation.ticket_service.Controller;

import com.reclamation.ticket_service.Entity.TicketHistory;
import com.reclamation.ticket_service.Enum.TicketCategory;
import com.reclamation.ticket_service.Enum.TicketPriority;
import com.reclamation.ticket_service.Repository.TicketHistoryRepository;
import com.reclamation.ticket_service.Repository.TicketRepository;
import com.reclamation.ticket_service.Entity.Ticket;
import com.reclamation.ticket_service.Enum.TicketStatus;
import com.reclamation.ticket_service.Service.TicketService;
import jakarta.annotation.Priority;
import lombok.RequiredArgsConstructor;
import org.hibernate.query.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.awt.print.Pageable;
import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/ticket")
@RequiredArgsConstructor
public class TicketController {

    private final TicketRepository ticketRepository;
    private final TicketService ticketService;
    private final TicketHistoryRepository historyRepository;

    @PostMapping
    public ResponseEntity<Ticket> create(@RequestBody Ticket ticket) {
        ticket.setStatus(TicketStatus.OPEN);
        return ResponseEntity.ok(ticketRepository.save(ticket));
    }

    @GetMapping
    public ResponseEntity<List<Ticket>> getAll() {
        return ResponseEntity.ok(ticketRepository.findAll());
    }

    @GetMapping("/filter")
    public ResponseEntity<List<Ticket>> getFilteredTickets(
            @RequestParam(required = false) TicketCategory category,
            @RequestParam(required = false) TicketPriority priority,
            @RequestParam(required = false) TicketStatus status,
            @RequestParam String userId) {

        String queryClientId = null;
        String queryAgentId = null;

        if (!"ADMIN".equalsIgnoreCase(userId)) {
            if (userId != null && userId.endsWith("user")) {
                queryClientId = userId;
            } else if (userId != null && userId.endsWith("agent")) {
                queryAgentId = userId;
            }
        }
        List<Ticket> tickets = ticketRepository.findByFilters(
                category, priority, status, queryClientId, queryAgentId
        );

        return ResponseEntity.ok(tickets);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Ticket> getById(@PathVariable UUID id) {
        return ResponseEntity.of(ticketRepository.findById(id));
    }

    @PatchMapping("/{id}/status")
    public ResponseEntity<Ticket> changeStatus(@PathVariable UUID id, @RequestParam TicketStatus status) {
        return ResponseEntity.ok(ticketService.updateStatus(id, status, "SYSTEM_USER"));
    }

    @PutMapping("/{id}/assign/{agentId}")
    public ResponseEntity<Ticket> assignAgent(@PathVariable UUID id, @PathVariable String agentId) {
        Ticket ticket = ticketRepository.findById(id).orElseThrow();
        ticket.setAgentId(agentId);
        return ResponseEntity.ok(ticketRepository.save(ticket));
    }

    @PostMapping("/{id}/escalate")
    public ResponseEntity<Ticket> escalate(@PathVariable UUID id) {
        Ticket ticket = ticketRepository.findById(id).orElseThrow();
        ticket.setEscalationLevel(Math.min(ticket.getEscalationLevel() + 1, 3));
        ticket.setStatus(TicketStatus.ESCALATED);
        return ResponseEntity.ok(ticketRepository.save(ticket));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(@PathVariable UUID id) {
        ticketRepository.deleteById(id);
        return ResponseEntity.noContent().build();
    }

    @GetMapping("/{id}/history")
    public ResponseEntity<List<TicketHistory>> getTicketHistory(@PathVariable UUID id) {
        if (!ticketRepository.existsById(id)) {
            return ResponseEntity.notFound().build();
        }

        List<TicketHistory> history = historyRepository.findByTicketIdOrderByChangedAtDesc(id);
        return ResponseEntity.ok(history);
    }
}
