package com.reclamation.ticket_service.Repository;

import com.reclamation.ticket_service.Entity.Ticket;
import com.reclamation.ticket_service.Enum.TicketCategory;
import com.reclamation.ticket_service.Enum.TicketPriority;
import com.reclamation.ticket_service.Enum.TicketStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface TicketRepository extends JpaRepository<Ticket, UUID>, JpaSpecificationExecutor<Ticket> {

        @Query("SELECT t FROM Ticket t WHERE " +
                "(:category IS NULL OR t.category = :category) AND " +
                "(:priority IS NULL OR t.priority = :priority) AND " +
                "(:status IS NULL OR t.status = :status) AND " +
                "(:clientId IS NULL OR t.clientId = :clientId) AND " +
                "(:agentId IS NULL OR t.agentId = :agentId)")
        List<Ticket> findByFilters(@Param("category") TicketCategory category,
                                   @Param("priority") TicketPriority priority,
                                   @Param("status") TicketStatus status,
                                   @Param("clientId") String clientId,
                                   @Param("agentId") String agentId);
}