package com.reclamation.ticket_service.Entity;

import com.reclamation.ticket_service.Enum.TicketCategory;
import com.reclamation.ticket_service.Enum.TicketPriority;
import com.reclamation.ticket_service.Enum.TicketStatus;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.Date;
import java.util.List;
import java.util.UUID;
@Entity
@Table(name = "tickets")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Ticket {
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private UUID id;

    @Column(nullable = false)
    private String title;

    @Column(columnDefinition = "TEXT")
    private String description;

    @Enumerated(EnumType.STRING)
    private TicketPriority priority;

    @Enumerated(EnumType.STRING)
    private TicketStatus status;

    @Enumerated(EnumType.STRING)
    private TicketCategory category;

    private String clientId;
    private String agentId;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;

    private LocalDateTime resolvedAt;

    @Column(columnDefinition = "int default 0")
    private Integer escalationLevel = 0;

    @OneToMany(mappedBy = "ticket", cascade = CascadeType.ALL)
    private List<TicketHistory> history;
}