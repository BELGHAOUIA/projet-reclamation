package com.reclamation.ticket_service.Service;

import com.reclamation.ticket_service.Repository.TicketHistoryRepository;
import com.reclamation.ticket_service.Repository.TicketRepository;
import com.reclamation.ticket_service.Entity.Ticket;
import com.reclamation.ticket_service.Entity.TicketHistory;
import com.reclamation.ticket_service.Enum.TicketStatus;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class TicketService {
    private final TicketRepository ticketRepository;
    private final TicketHistoryRepository historyRepository;

    @Transactional
    public Ticket updateStatus(UUID id, TicketStatus newStatus, String user) {
        Ticket ticket = ticketRepository.findById(id).orElseThrow();

        TicketHistory history = TicketHistory.builder()
                .ticket(ticket)
                .oldStatus(ticket.getStatus())
                .newStatus(newStatus)
                .changedBy(user)
                .build();

        ticket.setStatus(newStatus);
        if (newStatus == TicketStatus.RESOLVED) ticket.setResolvedAt(LocalDateTime.now());

        historyRepository.save(history);
        return ticketRepository.save(ticket);
    }
}
