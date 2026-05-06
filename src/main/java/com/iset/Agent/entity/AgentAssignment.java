package com.iset.Agent.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "agent_assignments")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AgentAssignment {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private String id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "agent_id", nullable = false)
    private Agent agent;

    @Column(nullable = false)
    private String ticketId;

    @Column(nullable = false)
    private String ticketPriority;

    private String ticketCategory;

    @Column(nullable = false)
    private LocalDateTime assignedAt;

    private LocalDateTime releasedAt;

    @Column(nullable = false)
    private boolean active = true;

    @PrePersist
    public void prePersist() {
        this.assignedAt = LocalDateTime.now();
    }
}